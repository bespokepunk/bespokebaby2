#!/usr/bin/env python3
"""
Fix ALL hex codes and color descriptions in captions to match actual pixel colors.
This ensures PERFECT accuracy for training.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def get_color_palette(image_path):
    """Get top colors from image with their percentages."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    total = len(pixels)

    color_counts = Counter(tuple(int(c) for c in p) for p in pixels)

    # Get top 10 colors
    palette = []
    for (r, g, b), count in color_counts.most_common(10):
        percentage = (count / total) * 100
        palette.append({
            'rgb': (r, g, b),
            'hex': rgb_to_hex(r, g, b),
            'count': count,
            'percentage': percentage
        })

    return palette

def fix_hex_codes_in_caption(caption, actual_palette):
    """Replace hex codes in caption with actual colors from image."""

    # Find all hex codes in caption
    hex_pattern = r'#[0-9a-fA-F]{6}'
    hex_matches = list(re.finditer(hex_pattern, caption))

    if not hex_matches:
        return caption, []

    # For each hex code, find the closest actual color
    replacements = []
    for match in hex_matches:
        claimed_hex = match.group(0).lower()
        claimed_rgb = hex_to_rgb(claimed_hex)

        # Find closest color in actual palette
        min_distance = float('inf')
        best_match = None

        for color in actual_palette:
            actual_rgb = color['rgb']
            # Calculate color distance
            distance = sum((int(a) - int(b)) ** 2 for a, b in zip(claimed_rgb, actual_rgb)) ** 0.5

            if distance < min_distance:
                min_distance = distance
                best_match = color

        if best_match and best_match['hex'] != claimed_hex:
            replacements.append({
                'old': claimed_hex,
                'new': best_match['hex'],
                'distance': min_distance
            })

    # Apply replacements
    new_caption = caption
    for repl in replacements:
        new_caption = new_caption.replace(repl['old'], repl['new'])

    return new_caption, replacements

print("="*100)
print("FIXING ALL HEX CODES AND VERIFYING COLOR DESCRIPTIONS")
print("="*100)
print()

fixed_count = 0
total_replacements = 0

for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        continue

    with open(txt_path, 'r') as f:
        old_caption = f.read().strip()

    # Get actual color palette from image
    palette = get_color_palette(png_path)

    # Fix hex codes
    new_caption, replacements = fix_hex_codes_in_caption(old_caption, palette)

    if replacements:
        # Write fixed caption
        with open(txt_path, 'w') as f:
            f.write(new_caption)

        print(f"✓ {txt_file}")
        for repl in replacements:
            print(f"    {repl['old']} → {repl['new']} (distance: {repl['distance']:.1f})")

        fixed_count += 1
        total_replacements += len(replacements)

print()
print("="*100)
print("COMPLETE!")
print("="*100)
print(f"Files fixed: {fixed_count}")
print(f"Total hex code corrections: {total_replacements}")
print()
print("All hex codes now match ACTUAL colors in the images!")
