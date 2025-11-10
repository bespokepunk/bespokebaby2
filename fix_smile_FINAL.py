#!/usr/bin/env python3
"""
FINAL smile detection - downsample 512x512 to 24x24 first, then analyze original pixel art.
This removes the noise from upscaling and gives us the true pixel art mouth shape.
"""

import os
import re
from PIL import Image

def detect_expression_from_original_art(image_path):
    """
    Downsample to 24x24 to get original pixel art, then analyze mouth shape.
    """
    img = Image.open(image_path).convert('RGB')

    # Downsample to 24x24 if needed
    if img.size != (24, 24):
        img = img.resize((24, 24), Image.NEAREST)  # Use NEAREST to preserve pixel art

    pixels = img.load()

    # Mouth area in 24x24 pixel art: rows 16-18, cols 9-15
    mouth_pixels = []
    for y in range(16, 19):
        for x in range(9, 16):
            color = pixels[x, y]
            if color != (0, 0, 0):  # Non-black
                mouth_pixels.append((x, y, color))

    if len(mouth_pixels) < 3:
        return "neutral expression"

    # Analyze mouth shape row by row
    rows = {}
    for x, y, c in mouth_pixels:
        if y not in rows:
            rows[y] = []
        rows[y].append(x)

    # Check if mouth spans multiple rows (indicates curve/smile)
    num_rows = len(rows)

    if num_rows >= 3:
        # Multi-row mouth suggests smile/curve
        return "slight smile"
    elif num_rows == 2:
        # Two rows - check the width and pattern
        row_keys = sorted(rows.keys())
        width_row1 = len(rows[row_keys[0]])
        width_row2 = len(rows[row_keys[1]])

        # If both rows are substantial, it's likely a smile
        if width_row1 >= 4 and width_row2 >= 4:
            return "slight smile"
        else:
            return "neutral expression"
    else:
        # Single row = straight line = neutral
        return "neutral expression"

def update_expression(caption_path, image_path):
    """Update expression in caption."""
    with open(caption_path, 'r') as f:
        caption = f.read().strip()

    new_expression = detect_expression_from_original_art(image_path)

    if 'slight smile' in caption:
        old_expression = 'slight smile'
    elif 'neutral expression' in caption:
        old_expression = 'neutral expression'
    else:
        return False, None, None

    if old_expression == new_expression:
        return False, old_expression, new_expression

    updated_caption = caption.replace(old_expression, new_expression)
    with open(caption_path, 'w') as f:
        f.write(updated_caption)

    return True, old_expression, new_expression

def main():
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"
    txt_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.txt')])

    print(f"Processing {len(txt_files)} files with downsampled pixel art analysis...\\n")
    print("=" * 80)

    changes = []
    unchanged = 0

    for txt_file in txt_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            continue

        changed, old, new = update_expression(caption_path, image_path)

        if changed:
            changes.append((txt_file, old, new))
            print(f"✓ {txt_file}: {old} → {new}")
        else:
            unchanged += 1

    print(f"\\n" + "=" * 80)
    print(f"Updated: {len(changes)} files")
    print(f"Unchanged: {unchanged} files")

    neutral_to_smile = sum(1 for _, old, new in changes if old == 'neutral expression' and new == 'slight smile')
    smile_to_neutral = sum(1 for _, old, new in changes if old == 'slight smile' and new == 'neutral expression')

    print(f"\\nChanges:")
    print(f"  Neutral → Smile: {neutral_to_smile}")
    print(f"  Smile → Neutral: {smile_to_neutral}")

    # Final count
    final_smiles = 0
    final_neutrals = 0
    for txt_file in txt_files:
        caption_path = os.path.join(base_dir, txt_file)
        with open(caption_path, 'r') as f:
            caption = f.read()
            if 'slight smile' in caption:
                final_smiles += 1
            elif 'neutral expression' in caption:
                final_neutrals += 1

    print(f"\\nFinal distribution:")
    print(f"  Slight smile: {final_smiles} ({100*final_smiles/len(txt_files):.1f}%)")
    print(f"  Neutral: {final_neutrals} ({100*final_neutrals/len(txt_files):.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
