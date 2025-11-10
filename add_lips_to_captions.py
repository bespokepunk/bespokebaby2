#!/usr/bin/env python3
"""
Add lips (with hex color) and facial expression to caption files missing them.
"""

import os
import re
from PIL import Image
from collections import Counter

def rgb_to_hex(r, g, b):
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"

def get_dominant_lip_color(image_path):
    """
    Extract the dominant lip color from a 24x24 pixel art image.
    Lips are typically in the lower-middle face area.
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Focus on lower face area where lips typically are
    # For 24x24 pixel art, lips are usually around rows 14-17, cols 8-16
    lip_colors = []

    for y in range(14, 18):  # Lower face area
        for x in range(8, 17):  # Center horizontal area
            if x < width and y < height:
                color = pixels[x, y]
                lip_colors.append(color)

    if not lip_colors:
        # Fallback: sample center-bottom area
        for y in range(height//2, height):
            for x in range(width//3, 2*width//3):
                lip_colors.append(pixels[x, y])

    # Find most common color (excluding pure black which is often outline)
    color_counts = Counter(lip_colors)
    # Remove black outlines
    color_counts = {k: v for k, v in color_counts.items() if k != (0, 0, 0)}

    if not color_counts:
        return None

    dominant_color = max(color_counts.items(), key=lambda x: x[1])[0]
    return rgb_to_hex(*dominant_color)

def detect_expression(image_path):
    """
    Detect if the character has a smile or neutral expression.
    For 24x24 pixel art, this is challenging - we'll check for mouth curve.
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Look for mouth pixels in lower face (rows 15-18)
    # A smile curves upward, neutral is straight/minimal
    mouth_pixels = []

    for y in range(15, 19):
        for x in range(9, 16):
            if x < width and y < height:
                color = pixels[x, y]
                if color != (0, 0, 0):  # Not black outline
                    mouth_pixels.append((x, y, color))

    # Simple heuristic: if mouth pixels span multiple rows with variation, likely smile
    if len(mouth_pixels) > 3:
        y_coords = [p[1] for p in mouth_pixels]
        if max(y_coords) - min(y_coords) >= 2:
            return "slight smile"

    return "neutral expression"

def update_caption_with_lips(caption_path, image_path):
    """
    Update a caption file to include lips with hex color and expression.
    """
    # Read current caption
    with open(caption_path, 'r') as f:
        caption = f.read().strip()

    # Extract lip color from image
    lip_color = get_dominant_lip_color(image_path)
    if not lip_color:
        print(f"⚠️  Could not detect lip color for {os.path.basename(caption_path)}")
        return False

    # Detect expression
    expression = detect_expression(image_path)

    # Find where to insert lips in caption
    # Lips should go after "eyes" and before "skin tone"
    # Pattern: "eyes (#hexcode), " -> insert after this

    # Look for eye color pattern
    eye_pattern = r'(eyes \(#[0-9a-f]{6}\)),\s*'
    match = re.search(eye_pattern, caption)

    if match:
        # Insert lips after eyes
        insert_pos = match.end()
        lips_text = f"lips ({lip_color}), {expression}, "
        updated_caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
    else:
        # Fallback: insert before "skin tone"
        skin_pattern = r'(medium|light|dark|pale).*?skin tone'
        match = re.search(skin_pattern, caption)
        if match:
            insert_pos = match.start()
            lips_text = f"lips ({lip_color}), {expression}, "
            updated_caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
        else:
            print(f"⚠️  Could not find insertion point for {os.path.basename(caption_path)}")
            return False

    # Write updated caption
    with open(caption_path, 'w') as f:
        f.write(updated_caption)

    print(f"✓ Updated {os.path.basename(caption_path)}: lips {lip_color}, {expression}")
    return True

def main():
    """Process all caption files missing lips."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

    # Read list of files missing lips
    with open('/tmp/missing_lips.txt', 'r') as f:
        missing_files = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(missing_files)} caption files missing lips...\n")

    success_count = 0
    failed_count = 0

    for txt_file in missing_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found: {image_path}")
            failed_count += 1
            continue

        if update_caption_with_lips(caption_path, image_path):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*60}")
    print(f"✓ Successfully updated: {success_count} files")
    print(f"✗ Failed: {failed_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
