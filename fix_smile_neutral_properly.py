#!/usr/bin/env python3
"""
Fix smile vs neutral classifications using stricter, more accurate criteria.
The previous algorithm was too lenient - everything was marked as "slight smile".

This version uses much stricter rules:
- Neutral: Straight horizontal mouth, minimal vertical range
- Slight smile: Clear upward curve, significant vertical range
"""

import os
import re
from PIL import Image

def detect_expression_strict(image_path):
    """
    Strict smile detection that won't over-classify smiles.

    Rules for SMILE:
    - Vertical range >= 3 pixels (significant curve)
    - Width >= 6 pixels (wide enough)
    - Pixel count >= 8 (substantial mouth)
    - Curved shape (center different from edges)

    Otherwise: NEUTRAL
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Handle both 24x24 and upscaled 512x512 images
    if width == 512:
        scale = 21.3
        mouth_rows = range(int(15*scale), int(19*scale))
        mouth_cols = range(int(8*scale), int(17*scale))
        smile_threshold_y_range = int(3 * scale)  # Scaled threshold
        smile_threshold_width = int(6 * scale)
        smile_threshold_pixels = int(8 * scale * scale)
    else:
        mouth_rows = range(15, 19)
        mouth_cols = range(8, 17)
        smile_threshold_y_range = 3
        smile_threshold_width = 6
        smile_threshold_pixels = 8

    # Collect non-black pixels in mouth area
    mouth_pixels = []
    for y in mouth_rows:
        if y >= height:
            break
        for x in mouth_cols:
            if x >= width:
                break
            color = pixels[x, y]
            if color != (0, 0, 0):
                mouth_pixels.append((x, y, color))

    if len(mouth_pixels) < 4:
        # Very small mouth, default to neutral
        return "neutral expression"

    y_coords = [p[1] for p in mouth_pixels]
    x_coords = [p[0] for p in mouth_pixels]

    y_range = max(y_coords) - min(y_coords)
    x_range = max(x_coords) - min(x_coords)

    # Check for curve (left/right edges vs center)
    if width == 512:
        left_threshold = int(11 * scale)
        right_threshold = int(14 * scale)
    else:
        left_threshold = 11
        right_threshold = 14

    left_y = [y for x, y, c in mouth_pixels if x <= left_threshold]
    center_y = [y for x, y, c in mouth_pixels if left_threshold < x < right_threshold]
    right_y = [y for x, y, c in mouth_pixels if x >= right_threshold]

    # Calculate smile score with STRICT criteria
    smile_score = 0

    # Criterion 1: Significant vertical range (most important!)
    if y_range >= smile_threshold_y_range:
        smile_score += 3
    elif y_range >= smile_threshold_y_range * 0.7:
        smile_score += 1

    # Criterion 2: Wide mouth
    if x_range >= smile_threshold_width:
        smile_score += 1

    # Criterion 3: Many pixels (indicates visible mouth)
    if len(mouth_pixels) >= smile_threshold_pixels:
        smile_score += 1

    # Criterion 4: Curved shape (center lower than edges)
    if center_y and (left_y or right_y):
        avg_center = sum(center_y) / len(center_y)
        edge_ys = (left_y if left_y else []) + (right_y if right_y else [])
        if edge_ys:
            avg_edge = sum(edge_ys) / len(edge_ys)
            diff = abs(avg_center - avg_edge)
            if diff >= (2 * scale if width == 512 else 2):
                smile_score += 2
            elif diff >= (1.5 * scale if width == 512 else 1.5):
                smile_score += 1

    # STRICT threshold: Need score >= 5 for smile (out of 7 possible)
    # This means we need strong evidence of a smile
    if smile_score >= 5:
        return "slight smile"
    else:
        return "neutral expression"

def update_expression_in_caption(caption_path, image_path):
    """Update the expression in a caption file."""
    with open(caption_path, 'r') as f:
        caption = f.read().strip()

    # Detect the correct expression
    new_expression = detect_expression_strict(image_path)

    # Check current expression
    if 'slight smile' in caption:
        current_expression = 'slight smile'
    elif 'neutral expression' in caption:
        current_expression = 'neutral expression'
    else:
        return False, None

    # Update if different
    if current_expression != new_expression:
        updated_caption = caption.replace(current_expression, new_expression)
        with open(caption_path, 'w') as f:
            f.write(updated_caption)
        return True, f"{current_expression} → {new_expression}"

    return False, None

def main():
    """Process all files and update expressions."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

    txt_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.txt')])

    print(f"Processing {len(txt_files)} files with STRICT smile detection...\n")
    print("=" * 80)

    changes = []
    no_change = 0

    for txt_file in txt_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            continue

        changed, change_desc = update_expression_in_caption(caption_path, image_path)

        if changed:
            changes.append((txt_file, change_desc))
            print(f"✓ {txt_file}: {change_desc}")
        else:
            no_change += 1

    print(f"\n" + "=" * 80)
    print(f"Updated: {len(changes)} files")
    print(f"No change: {no_change} files")

    # Show summary of changes
    smile_to_neutral = sum(1 for _, desc in changes if 'slight smile → neutral' in desc)
    neutral_to_smile = sum(1 for _, desc in changes if 'neutral → slight smile' in desc)

    print(f"\nChanges breakdown:")
    print(f"  Smile → Neutral: {smile_to_neutral}")
    print(f"  Neutral → Smile: {neutral_to_smile}")
    print("=" * 80)

if __name__ == "__main__":
    main()
