#!/usr/bin/env python3
"""Check which images claim to have brown eyes and analyze their actual pixel colors."""

import os
from PIL import Image
import numpy as np
from collections import Counter

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def get_eye_region_colors(image_path):
    """Get the dominant colors in the approximate eye region (top-middle of 24x24)."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Eye region is roughly rows 8-12, cols 8-16 in a 24x24 portrait
    eye_region = arr[8:13, 8:17]

    # Flatten and get unique colors
    pixels = eye_region.reshape(-1, 3)
    colors = [tuple(p) for p in pixels]

    return Counter(colors).most_common(5)  # Top 5 colors in eye region

def rgb_to_name(rgb):
    """Rough color naming."""
    r, g, b = rgb

    # Cyan/blue range
    if b > 150 and g > 100 and b > r + 30:
        return "CYAN/BLUE"
    # Blue
    if b > r + 30 and b > g + 20:
        return "BLUE"
    # Brown range
    if r > 80 and g > 50 and b < 80 and r > g and r > b:
        return "BROWN"
    # Dark brown/black
    if r < 50 and g < 50 and b < 50:
        return "BLACK/DARK_BROWN"
    # Gray
    if abs(r - g) < 30 and abs(g - b) < 30 and 100 < r < 180:
        return "GRAY"
    # Green
    if g > r and g > b:
        return "GREEN"
    # Red
    if r > 150 and r > g + 30 and r > b + 30:
        return "RED"
    # Light/white
    if r > 200 and g > 200 and b > 200:
        return "WHITE/LIGHT"
    # Skin tone
    if r > 150 and g > 100 and b > 80 and r > b:
        return "SKIN_TONE"

    return f"OTHER({r},{g},{b})"

print("="*80)
print("BROWN EYES CAPTION VERIFICATION")
print("="*80)

# Find all files with "brown eyes" in caption
brown_eye_files = []
for txt_file in os.listdir(TRAINING_DIR):
    if not txt_file.endswith('.txt'):
        continue

    txt_path = os.path.join(TRAINING_DIR, txt_file)
    with open(txt_path, 'r') as f:
        caption = f.read().lower()

    if 'brown eyes' in caption or 'dark brown eyes' in caption:
        png_file = txt_file.replace('.txt', '.png')
        png_path = os.path.join(TRAINING_DIR, png_file)

        if os.path.exists(png_path):
            brown_eye_files.append((txt_file, png_file, caption))

print(f"\nFound {len(brown_eye_files)} files with 'brown eyes' in caption\n")

# Analyze each one
mismatches = []
correct = []

for txt_file, png_file, caption in brown_eye_files:
    png_path = os.path.join(TRAINING_DIR, png_file)

    # Get eye region colors
    colors = get_eye_region_colors(png_path)

    # Analyze top colors
    top_color_names = [rgb_to_name(rgb) for rgb, count in colors[:3]]

    # Check if any top colors are actually brown
    has_brown = any('BROWN' in name for name in top_color_names)
    has_cyan_blue = any('CYAN' in name or 'BLUE' in name for name in top_color_names)

    status = "✓ CORRECT" if has_brown else "✗ MISMATCH"

    result = {
        'file': png_file,
        'status': status,
        'top_colors': top_color_names,
        'has_brown': has_brown,
        'has_cyan_blue': has_cyan_blue
    }

    if has_brown:
        correct.append(result)
    else:
        mismatches.append(result)

    if not has_brown:  # Show mismatches immediately
        print(f"{status}: {png_file}")
        print(f"  Caption says: brown eyes")
        print(f"  Actual eye colors: {', '.join(top_color_names[:3])}")
        print(f"  Top 3 RGB: {[rgb for rgb, _ in colors[:3]]}")
        print()

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total 'brown eyes' captions: {len(brown_eye_files)}")
print(f"Correct (actually have brown): {len(correct)}")
print(f"Mismatches (don't have brown): {len(mismatches)}")
print(f"Accuracy: {len(correct)/len(brown_eye_files)*100:.1f}%")

if mismatches:
    print(f"\n⚠️  PROBLEM: {len(mismatches)} images labeled 'brown eyes' have wrong pixel colors!")
    print("These need to be fixed for training to work correctly.")
    print("\nMismatch files:")
    for m in mismatches[:20]:  # Show first 20
        print(f"  - {m['file']}: {', '.join(m['top_colors'][:2])}")
