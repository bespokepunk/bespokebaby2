#!/usr/bin/env python3
"""
Verify that HEX colors mentioned in captions actually exist in the images.
This is the most accurate way - check the explicit color codes you provided.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def hex_to_rgb(hex_str):
    """Convert hex string to RGB tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """Convert RGB to hex."""
    return f"#{r:02x}{g:02x}{b:02x}"

def get_all_colors_in_image(image_path):
    """Get all unique colors in the image with their counts."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    color_counts = Counter(tuple(p) for p in pixels)
    return color_counts

def find_hex_colors_in_caption(caption):
    """Extract all hex color codes from caption."""
    hex_pattern = r'#([0-9a-fA-F]{6})'
    matches = re.findall(hex_pattern, caption)
    return [f"#{m.lower()}" for m in matches]

def color_distance(rgb1, rgb2):
    """Calculate color distance between two RGB colors."""
    return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5

print("="*100)
print("HEX COLOR VERIFICATION - Checking explicit color codes in captions")
print("="*100)
print()

mismatches = []
perfect = []
no_hex = []

for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        continue

    with open(txt_path, 'r') as f:
        caption = f.read().strip()

    # Find hex colors in caption
    caption_hexes = find_hex_colors_in_caption(caption)

    if not caption_hexes:
        no_hex.append(png_file)
        continue

    # Get all colors in image
    image_colors = get_all_colors_in_image(png_path)
    image_hexes = {rgb_to_hex(r, g, b): count for (r, g, b), count in image_colors.items()}

    # Verify each hex color
    file_issues = []
    for hex_color in caption_hexes:
        if hex_color in image_hexes:
            # Exact match
            continue
        else:
            # Check for close matches (in case of slight variations)
            claimed_rgb = hex_to_rgb(hex_color)
            closest_color = None
            min_distance = float('inf')

            for (r, g, b), count in image_colors.most_common(20):
                dist = color_distance(claimed_rgb, (r, g, b))
                if dist < min_distance:
                    min_distance = dist
                    closest_color = ((r, g, b), count, rgb_to_hex(r, g, b))

            file_issues.append({
                'claimed_hex': hex_color,
                'claimed_rgb': claimed_rgb,
                'closest_actual': closest_color,
                'distance': min_distance
            })

    if file_issues:
        mismatches.append({
            'file': png_file,
            'issues': file_issues,
            'caption': caption
        })
    else:
        perfect.append(png_file)

print(f"{'='*100}")
print(f"SUMMARY")
print(f"{'='*100}")
print(f"✓ Perfect hex matches: {len(perfect)}")
print(f"⚠️  Hex color mismatches: {len(mismatches)}")
print(f"ℹ️  No hex colors in caption: {len(no_hex)}")
print()

if mismatches:
    print(f"{'='*100}")
    print(f"HEX COLOR MISMATCHES (First 30)")
    print(f"{'='*100}\n")

    for item in mismatches[:30]:
        print(f"File: {item['file']}")
        for issue in item['issues']:
            print(f"  Caption claims: {issue['claimed_hex']} (RGB{issue['claimed_rgb']})")
            if issue['closest_actual']:
                rgb, count, hex_str = issue['closest_actual']
                print(f"  Closest actual: {hex_str} (RGB{rgb}) - {count} pixels")
                print(f"  Color distance: {issue['distance']:.1f}")

                # Suggest if it's close enough (might be rounding)
                if issue['distance'] < 10:
                    print(f"  → VERY CLOSE - might be rounding, suggest update caption to {hex_str}")
                elif issue['distance'] < 30:
                    print(f"  → CLOSE - suggest update caption to {hex_str}")
                else:
                    print(f"  → DIFFERENT - caption hex doesn't match image!")
        print()

print(f"\n{'='*100}")
print(f"Next: Review mismatches and update hex codes in captions to match actual image colors")
print(f"{'='*100}")
