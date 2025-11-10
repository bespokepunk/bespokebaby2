#!/usr/bin/env python3
"""
Comprehensive fix for all lip and smoking classification issues:
1. Fix pipe -> cigarette vs joint (based on color)
2. Improve smile vs neutral detection
3. Add lips to files missing them
4. Fix files with lips but no expression
"""

import os
import re
from PIL import Image
from collections import Counter

def rgb_to_hex(r, g, b):
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"

def get_dominant_lip_color(image_path):
    """Extract the dominant lip color from a 24x24 pixel art image."""
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Focus on lower face area where lips typically are (rows 14-18)
    lip_colors = []

    for y in range(14, 18):
        for x in range(8, 17):
            if x < width and y < height:
                color = pixels[x, y]
                lip_colors.append(color)

    if not lip_colors:
        # Fallback to lower half of face
        for y in range(height//2, height):
            for x in range(width//3, 2*width//3):
                lip_colors.append(pixels[x, y])

    color_counts = Counter(lip_colors)
    # Filter out black
    color_counts = {k: v for k, v in color_counts.items() if k != (0, 0, 0)}

    if not color_counts:
        return None

    dominant_color = max(color_counts.items(), key=lambda x: x[1])[0]
    return rgb_to_hex(*dominant_color)

def detect_smoking_accessory(image_path):
    """
    Detect if character is smoking and classify as cigarette or joint.
    Returns: None, 'cigarette', or 'joint'
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Look for smoking accessories around mouth area (right side typically)
    # Pixels around rows 15-18, columns 16-22
    brown_pixels = []
    white_light_pixels = []
    orange_pixels = []

    for y in range(14, 19):
        for x in range(16, min(23, width)):
            if x < width and y < height:
                color = pixels[x, y]
                r, g, b = color

                # Detect orange tip (high red, medium green, low blue)
                if r > 200 and g > 50 and g < 150 and b < 100:
                    orange_pixels.append((x, y, color))

                # Detect brown (balanced RGB, low values)
                elif 50 < r < 150 and 30 < g < 120 and 20 < b < 100 and abs(r - g) < 40:
                    brown_pixels.append((x, y, color))

                # Detect white/light cigarette color
                elif r > 180 and g > 180 and b > 180:
                    white_light_pixels.append((x, y, color))

    # If we found orange tip and either brown or white pixels, classify it
    if len(orange_pixels) >= 1:
        if len(brown_pixels) >= 3:
            return 'joint'
        elif len(white_light_pixels) >= 3:
            return 'cigarette'

    return None

def improved_smile_detection(image_path):
    """
    Improved smile detection algorithm.
    Looks for:
    - Curved mouth shape
    - Wider mouth area
    - Upward angles at corners
    - More sophisticated pixel analysis
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Scan mouth area (rows 15-19, cols 8-16)
    mouth_pixels = []
    for y in range(15, 20):
        for x in range(8, 17):
            if x < width and y < height:
                color = pixels[x, y]
                # Non-black pixels in mouth area
                if color != (0, 0, 0):
                    mouth_pixels.append((x, y, color))

    if len(mouth_pixels) < 3:
        return "neutral expression"

    # Get y-coordinates to analyze mouth shape
    y_coords = [p[1] for p in mouth_pixels]
    x_coords = [p[0] for p in mouth_pixels]

    # Check for vertical spread (smile has more vertical pixels)
    y_range = max(y_coords) - min(y_coords)
    x_range = max(x_coords) - min(x_coords)

    # Check for curved shape - analyze left, center, right
    left_y = [y for x, y, c in mouth_pixels if x <= 10]
    center_y = [y for x, y, c in mouth_pixels if 11 <= x <= 13]
    right_y = [y for x, y, c in mouth_pixels if x >= 14]

    # Smile indicators:
    # 1. Vertical range >= 2 pixels
    # 2. Wider mouth (x_range >= 5)
    # 3. Curved shape (center lower than edges)
    # 4. Large number of mouth pixels (>= 6)

    smile_score = 0

    if y_range >= 2:
        smile_score += 2

    if x_range >= 6:
        smile_score += 1

    if len(mouth_pixels) >= 6:
        smile_score += 1

    # Check for curve (center y should be higher/lower than edges)
    if center_y and (left_y or right_y):
        avg_center = sum(center_y) / len(center_y)
        edge_ys = (left_y if left_y else []) + (right_y if right_y else [])
        if edge_ys:
            avg_edge = sum(edge_ys) / len(edge_ys)
            if abs(avg_center - avg_edge) >= 1:
                smile_score += 2

    # Threshold: score >= 3 = smile
    if smile_score >= 3:
        return "slight smile"
    else:
        return "neutral expression"

def fix_caption_file(caption_path, image_path, dry_run=False):
    """
    Fix a single caption file:
    1. Check for smoking accessories and fix pipe->cigarette/joint
    2. Add or fix lips + expression
    """
    with open(caption_path, 'r') as f:
        caption = f.read().strip()

    original_caption = caption
    changes_made = []

    # Step 1: Fix smoking accessories
    smoking = detect_smoking_accessory(image_path)
    if smoking:
        # Check if caption mentions pipe/smoking
        if 'pipe' in caption.lower():
            if smoking == 'joint':
                caption = re.sub(
                    r'pipe',
                    'brown joint with an orange tip',
                    caption,
                    flags=re.IGNORECASE
                )
                changes_made.append("Fixed pipe -> joint")
            elif smoking == 'cigarette':
                caption = re.sub(
                    r'pipe',
                    'cigarette with an orange tip',
                    caption,
                    flags=re.IGNORECASE
                )
                changes_made.append("Fixed pipe -> cigarette")

        # Fix typo "join" -> "joint"
        if 'brown join with' in caption:
            caption = caption.replace('brown join with', 'brown joint with')
            changes_made.append("Fixed typo: join -> joint")

    # Step 2: Check lips situation
    has_lips = 'lips (' in caption
    has_expression = 'slight smile' in caption or 'neutral expression' in caption

    if not has_lips:
        # Case A: Missing lips entirely
        lip_color = get_dominant_lip_color(image_path)
        if lip_color:
            expression = improved_smile_detection(image_path)
            lips_text = f"lips ({lip_color}), {expression}, "

            # Insert before skin tone
            skin_patterns = [
                r'(medium|light|dark|pale|olive)\s+.*?skin',
                r'skin\s+\(#[0-9a-f]{6}\)',
            ]

            inserted = False
            for pattern in skin_patterns:
                match = re.search(pattern, caption, re.IGNORECASE)
                if match:
                    insert_pos = match.start()
                    caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
                    changes_made.append(f"Added lips + {expression}")
                    inserted = True
                    break

            if not inserted:
                # Try inserting after eyes
                eye_match = re.search(r'eyes\s+\(#[0-9a-f]{6}\),\s*', caption, re.IGNORECASE)
                if eye_match:
                    insert_pos = eye_match.end()
                    caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
                    changes_made.append(f"Added lips + {expression}")

    elif has_lips and not has_expression:
        # Case B: Has lips but missing expression
        expression = improved_smile_detection(image_path)

        # Find lips color and add expression after it
        lips_match = re.search(r'lips\s+\(#[0-9a-f]{6}\),?\s*', caption)
        if lips_match:
            # Replace lips section to include expression
            old_lips = lips_match.group(0)
            # Extract just the color
            color_match = re.search(r'\(#[0-9a-f]{6}\)', old_lips)
            if color_match:
                color = color_match.group(0)
                new_lips = f"lips {color}, {expression}, "
                caption = caption.replace(old_lips, new_lips)
                changes_made.append(f"Added {expression} to existing lips")

    elif has_lips and has_expression:
        # Case C: Has both, but expression might be wrong
        expression = improved_smile_detection(image_path)

        # Check current expression
        if 'slight smile' in caption and expression == 'neutral expression':
            caption = caption.replace('slight smile', 'neutral expression')
            changes_made.append("Fixed smile -> neutral")
        elif 'neutral expression' in caption and expression == 'slight smile':
            caption = caption.replace('neutral expression', 'slight smile')
            changes_made.append("Fixed neutral -> smile")

    # Write changes if any were made
    if caption != original_caption:
        if not dry_run:
            with open(caption_path, 'w') as f:
                f.write(caption)
        return True, changes_made

    return False, []

def main():
    """Process all training files."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

    # Get all txt files
    txt_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.txt')])

    print(f"Processing {len(txt_files)} caption files...\n")
    print("=" * 70)

    # First do a dry run on the specific problem files
    problem_files = [
        "lad_087_HEEM.txt",
        "lad_103_merheb.txt",
        "lad_103_merheb2.txt",
        "lad_103_merheb3.txt",
        "lady_001_hazelnut.txt",
        "lady_054_hazelnutabstract-3.txt",
    ]

    print("DRY RUN on problem files:\n")
    for txt_file in problem_files:
        if txt_file not in txt_files:
            continue

        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            continue

        changed, changes = fix_caption_file(caption_path, image_path, dry_run=True)
        if changed:
            print(f"✓ {txt_file}:")
            for change in changes:
                print(f"    - {change}")
        else:
            print(f"  {txt_file}: No changes needed")

    print("\n" + "=" * 70)
    print("\nProceeding with full run...\n")

    success_count = 0
    no_change_count = 0
    error_count = 0

    for txt_file in txt_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found: {image_path}")
            error_count += 1
            continue

        try:
            changed, changes = fix_caption_file(caption_path, image_path, dry_run=False)
            if changed:
                print(f"✓ {txt_file}")
                for change in changes:
                    print(f"    - {change}")
                success_count += 1
            else:
                no_change_count += 1
        except Exception as e:
            print(f"✗ {txt_file}: ERROR - {e}")
            error_count += 1

    print(f"\n{'='*70}")
    print(f"✓ Modified: {success_count} files")
    print(f"  No change needed: {no_change_count} files")
    print(f"✗ Errors: {error_count} files")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
