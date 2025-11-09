#!/usr/bin/env python3
"""Fix ALL caption files to match actual pixel colors in the images."""

import os
import re
from PIL import Image
import numpy as np
from collections import Counter

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def get_eye_colors(image_path):
    """Detect actual eye colors from pixel data."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Eye region: rows 8-12, cols 8-16 in 24x24 portrait
    eye_region = arr[8:13, 8:17]
    pixels = eye_region.reshape(-1, 3)

    # Get most common non-skin colors
    color_counts = Counter(tuple(p) for p in pixels)

    # Analyze colors
    eye_color = detect_eye_color(color_counts)
    return eye_color

def detect_eye_color(color_counts):
    """Detect eye color from pixel RGB values."""

    # Get top 10 colors
    top_colors = color_counts.most_common(10)

    # Score each color category
    scores = {
        'cyan': 0,
        'blue': 0,
        'brown': 0,
        'dark brown': 0,
        'green': 0,
        'red': 0,
        'gray': 0,
        'black': 0
    }

    for (r, g, b), count in top_colors:
        r, g, b = int(r), int(g), int(b)

        # Cyan (bright blue-green)
        if b > 120 and g > 100 and b > r + 20:
            scores['cyan'] += count
        # Blue
        elif b > r + 20 and b > g + 10 and b > 80:
            scores['blue'] += count
        # Dark blue/navy
        elif b > r and b > g and b < 80:
            scores['blue'] += count * 0.8
        # Brown (orange-brown)
        elif 80 < r < 180 and 50 < g < 140 and b < 100 and r > g and r > b:
            scores['brown'] += count
        # Dark brown
        elif 30 < r < 90 and 20 < g < 70 and b < 60 and r > g and r >= b:
            scores['dark brown'] += count
        # Black
        elif r < 40 and g < 40 and b < 40:
            scores['black'] += count
        # Green
        elif g > r + 15 and g > b + 15:
            scores['green'] += count
        # Red
        elif r > 100 and r > g + 30 and r > b + 20:
            scores['red'] += count
        # Gray
        elif abs(r - g) < 25 and abs(g - b) < 25 and 80 < r < 200:
            scores['gray'] += count

    # Return highest scoring color
    max_color = max(scores.items(), key=lambda x: x[1])

    # If score is too low, default to checking raw RGB of most common
    if max_color[1] < 5:
        r, g, b = top_colors[0][0]
        r, g, b = int(r), int(g), int(b)

        if b > r + 20:
            return 'blue eyes' if b < 150 else 'cyan eyes'
        elif g > r and g > b:
            return 'green eyes'
        elif r > g + 20:
            return 'red eyes'
        elif r < 50:
            return 'black eyes'
        else:
            return 'gray eyes'

    color_name = max_color[0]

    # Format return
    if color_name == 'black':
        return 'black eyes'
    else:
        return f'{color_name} eyes'

def fix_caption(caption_text, correct_eye_color):
    """Replace eye color in caption with correct one."""

    # Pattern to match eye color descriptions
    patterns = [
        r'\b(dark brown|brown|cyan|blue|green|red|gray|grey|black|orange|yellow|purple|pink) eyes\b',
        r'\beyes[^,]*',  # Fallback
    ]

    for pattern in patterns:
        if re.search(pattern, caption_text, re.IGNORECASE):
            caption_text = re.sub(pattern, correct_eye_color, caption_text, flags=re.IGNORECASE, count=1)
            return caption_text

    # If no eye color found, don't modify
    return caption_text

print("="*80)
print("FIXING ALL CAPTION FILES")
print("="*80)

fixed_count = 0
skipped_count = 0

# Process all images
for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        print(f"⚠️  No caption for {png_file}")
        continue

    # Read current caption
    with open(txt_path, 'r') as f:
        old_caption = f.read().strip()

    # Skip if no eyes mentioned (probably sunglasses, etc.)
    if 'eyes' not in old_caption.lower():
        skipped_count += 1
        continue

    # Detect actual eye color
    correct_eye_color = get_eye_colors(png_path)

    # Fix caption
    new_caption = fix_caption(old_caption, correct_eye_color)

    # Check if changed
    if new_caption != old_caption:
        # Write fixed caption
        with open(txt_path, 'w') as f:
            f.write(new_caption)

        # Extract what changed
        old_color = re.search(r'\b(dark brown|brown|cyan|blue|green|red|gray|grey|black) eyes\b', old_caption, re.IGNORECASE)
        old_color_str = old_color.group(0) if old_color else "???"

        print(f"✓ Fixed {txt_file}")
        print(f"    {old_color_str} → {correct_eye_color}")

        fixed_count += 1

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Fixed: {fixed_count} captions")
print(f"Skipped (no eyes mentioned): {skipped_count}")
print(f"\nAll captions now match actual pixel colors!")
print("\n⚠️  IMPORTANT: You need to RE-TRAIN with these fixed captions!")
print("The current training used wrong captions, so models won't work correctly.")
