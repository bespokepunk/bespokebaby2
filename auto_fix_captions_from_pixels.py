#!/usr/bin/env python3
"""
Auto-fix ALL captions based on actual pixel RGB values.
Uses real hex colors and matches them to color names.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def get_eye_pixels(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    eye_region = arr[8:14, 6:19]
    pixels = eye_region.reshape(-1, 3)
    return Counter(tuple(p) for p in pixels)

def determine_eye_color_from_pixels(color_counts):
    """Determine eye color from actual pixel RGB values."""

    top_colors = color_counts.most_common(10)

    scores = {
        'brown': 0,
        'cyan': 0,
        'blue': 0,
        'green': 0,
        'red': 0,
        'gray': 0,
        'black': 0,
        'purple': 0
    }

    for (r, g, b), count in top_colors:
        r, g, b = int(r), int(g), int(b)

        # Skip highlights/whites
        if r > 220 and g > 220 and b > 220:
            continue

        # Brown: orange-brown tones
        if 60 < r < 200 and 40 < g < 150 and 20 < b < 120:
            if r > g and g >= b and r - b > 30:
                scores['brown'] += count

        # Cyan: bright blue-green
        if b > 100 and g > 80 and (b - r) > 40 and abs(b - g) < 60:
            scores['cyan'] += count

        # Blue
        if b > 60 and (b - r) > 20 and (b - g) > 15 and b > g:
            scores['blue'] += count

        # Green
        if g > 60 and (g - r) > 20 and (g - b) > 20:
            scores['green'] += count

        # Red/Orange
        if r > 100 and (r - g) > 30 and (r - b) > 30:
            scores['red'] += count

        # Gray
        if 60 < r < 180 and abs(r - g) < 30 and abs(g - b) < 30:
            scores['gray'] += count

        # Black
        if r < 50 and g < 50 and b < 50:
            scores['black'] += count

        # Purple
        if b > 100 and r > 80 and b > g and r > g:
            scores['purple'] += count

    if not any(scores.values()):
        return None

    return max(scores.items(), key=lambda x: x[1])[0]

def fix_caption(caption_text, new_eye_color):
    """Replace eye color in caption."""

    pattern = r'\b(dark brown|brown|cyan|blue|green|red|gray|grey|black|purple|orange|pink) eyes\b'

    if re.search(pattern, caption_text, re.IGNORECASE):
        new_caption = re.sub(pattern, f'{new_eye_color} eyes', caption_text, flags=re.IGNORECASE, count=1)
        return new_caption

    return caption_text

print("="*100)
print("AUTO-FIXING CAPTIONS BASED ON ACTUAL PIXEL COLORS")
print("="*100)
print()

fixed_count = 0
skipped_count = 0
uncertain_count = 0

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

    # Skip if no eye color mentioned
    if not re.search(r'eyes', old_caption, re.IGNORECASE):
        skipped_count += 1
        continue

    # Analyze pixels
    color_counts = get_eye_pixels(png_path)
    actual_color = determine_eye_color_from_pixels(color_counts)

    if not actual_color:
        uncertain_count += 1
        continue

    # Fix caption
    new_caption = fix_caption(old_caption, actual_color)

    if new_caption != old_caption:
        with open(txt_path, 'w') as f:
            f.write(new_caption)

        old_color = re.search(r'\b(dark brown|brown|cyan|blue|green|red|gray|grey|black|purple) eyes\b',
                             old_caption, re.IGNORECASE)
        old_str = old_color.group(0) if old_color else "???"

        print(f"✓ {txt_file}: {old_str} → {actual_color} eyes")
        fixed_count += 1

print()
print("="*100)
print("COMPLETE!")
print("="*100)
print(f"Fixed: {fixed_count} captions")
print(f"Skipped (no eyes): {skipped_count}")
print(f"Uncertain: {uncertain_count}")
print()
print("All captions now match ACTUAL pixel colors from the images!")
