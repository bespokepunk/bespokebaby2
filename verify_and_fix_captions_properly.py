#!/usr/bin/env python3
"""
Properly verify and fix captions by analyzing ACTUAL pixel colors.
Compare caption claims vs real RGB/hex values in the images.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    """Convert RGB to hex."""
    return f"#{r:02x}{g:02x}{b:02x}"

def get_eye_pixels(image_path):
    """Extract actual eye region pixels from 24x24 image."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Eye region in 24x24 portrait: approximately rows 8-13, cols 6-18
    eye_region = arr[8:14, 6:19]

    # Get all pixels in eye region
    pixels = eye_region.reshape(-1, 3)

    # Count color frequencies
    color_counts = Counter(tuple(p) for p in pixels)

    return color_counts

def analyze_eye_color(color_counts):
    """
    Analyze eye color based on actual pixel RGB values.
    Returns the dominant eye color and evidence.
    """

    # Get top 10 most common colors
    top_colors = color_counts.most_common(10)

    # Track scores for each color category
    evidence = {
        'brown': [],
        'dark_brown': [],
        'cyan': [],
        'blue': [],
        'green': [],
        'red': [],
        'gray': [],
        'black': [],
        'purple': [],
        'orange': []
    }

    for (r, g, b), count in top_colors:
        r, g, b = int(r), int(g), int(b)
        hex_color = rgb_to_hex(r, g, b)

        # Skip very light colors (likely skin/highlights)
        if r > 220 and g > 220 and b > 220:
            continue

        # Categorize by RGB values

        # Brown tones (orange-brown, tan-brown)
        if 60 < r < 200 and 40 < g < 150 and 20 < b < 120:
            if r > g and g >= b and r - b > 30:
                evidence['brown'].append((hex_color, count, (r, g, b)))

        # Dark brown / very dark
        if 30 < r < 90 and 20 < g < 70 and 10 < b < 60:
            if r >= g >= b:
                evidence['dark_brown'].append((hex_color, count, (r, g, b)))

        # Cyan (bright blue-green)
        if b > 100 and g > 80 and (b - r) > 40:
            if abs(b - g) < 60:
                evidence['cyan'].append((hex_color, count, (r, g, b)))

        # Blue
        if b > 60 and (b - r) > 20 and (b - g) > 15:
            if b > g:
                evidence['blue'].append((hex_color, count, (r, g, b)))

        # Green
        if g > 60 and (g - r) > 20 and (g - b) > 20:
            evidence['green'].append((hex_color, count, (r, g, b)))

        # Red/Orange
        if r > 100 and (r - g) > 30 and (r - b) > 30:
            evidence['red'].append((hex_color, count, (r, g, b)))

        # Gray (balanced RGB)
        if 60 < r < 180 and abs(r - g) < 30 and abs(g - b) < 30:
            evidence['gray'].append((hex_color, count, (r, g, b)))

        # Black/very dark
        if r < 50 and g < 50 and b < 50:
            evidence['black'].append((hex_color, count, (r, g, b)))

        # Purple
        if b > 100 and r > 80 and b > g and r > g:
            evidence['purple'].append((hex_color, count, (r, g, b)))

    # Determine dominant color based on evidence
    color_scores = {k: sum(count for _, count, _ in v) for k, v in evidence.items()}

    if not any(color_scores.values()):
        return None, evidence

    dominant = max(color_scores.items(), key=lambda x: x[1])

    if dominant[1] == 0:
        return None, evidence

    return dominant[0], evidence

def get_caption_eye_color(caption_text):
    """Extract eye color claim from caption."""
    match = re.search(r'\b(dark brown|brown|cyan|blue|green|red|gray|grey|black|purple|orange|pink) eyes\b',
                     caption_text, re.IGNORECASE)
    if match:
        color = match.group(1).lower()
        if color == 'grey':
            color = 'gray'
        return color
    return None

def suggest_fix(caption_color, actual_color, evidence):
    """Suggest caption fix based on evidence."""

    if caption_color == actual_color:
        return None  # Already correct

    if actual_color == 'dark_brown':
        actual_color = 'brown'  # Simplify for captions

    # Get evidence for the actual color
    actual_evidence = evidence.get(actual_color, [])
    caption_evidence = evidence.get(caption_color.replace(' ', '_'), []) if caption_color else []

    if not actual_evidence and not caption_evidence:
        return None  # Can't determine

    # If caption color has more evidence, maybe keep it
    caption_total = sum(c for _, c, _ in caption_evidence)
    actual_total = sum(c for _, c, _ in actual_evidence)

    if caption_total > actual_total * 1.5:
        return None  # Caption might be right

    return actual_color

print("="*100)
print("CAPTION VERIFICATION - Comparing Caption Claims vs Actual Pixel Colors")
print("="*100)
print()

mismatches = []
correct = []
uncertain = []

# Process all images
for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        continue

    # Read caption
    with open(txt_path, 'r') as f:
        caption = f.read().strip()

    caption_color = get_caption_eye_color(caption)

    if not caption_color:
        continue  # No eye color in caption (sunglasses, etc.)

    # Analyze actual pixels
    color_counts = get_eye_pixels(png_path)
    actual_color, evidence = analyze_eye_color(color_counts)

    if not actual_color:
        uncertain.append({
            'file': png_file,
            'caption_color': caption_color,
            'reason': 'Could not determine actual color'
        })
        continue

    # Compare
    caption_normalized = caption_color.replace(' ', '_').replace('dark_brown', 'brown')
    actual_normalized = actual_color.replace('dark_', '')

    if caption_normalized == actual_normalized:
        correct.append({
            'file': png_file,
            'color': caption_color,
            'evidence': evidence[actual_color][:3]
        })
    else:
        # Check if we should suggest a fix
        suggested = suggest_fix(caption_color, actual_color, evidence)

        mismatches.append({
            'file': png_file,
            'caption_says': caption_color,
            'actual_pixels': actual_color,
            'caption_evidence': evidence.get(caption_color.replace(' ', '_'), [])[:3],
            'actual_evidence': evidence.get(actual_color, [])[:3],
            'suggested_fix': suggested
        })

# Print Results
print(f"\n{'='*100}")
print(f"SUMMARY")
print(f"{'='*100}")
print(f"✓ Correct: {len(correct)}")
print(f"✗ Mismatches: {len(mismatches)}")
print(f"? Uncertain: {len(uncertain)}")
print()

if mismatches:
    print(f"\n{'='*100}")
    print(f"MISMATCHES FOUND (Caption vs Actual Pixels)")
    print(f"{'='*100}\n")

    for m in mismatches[:30]:  # Show first 30
        print(f"File: {m['file']}")
        print(f"  Caption says: {m['caption_says']} eyes")
        print(f"  Actual pixels: {m['actual_pixels']} eyes")

        if m['actual_evidence']:
            print(f"  Actual color evidence:")
            for hex_c, count, rgb in m['actual_evidence']:
                print(f"    {hex_c} (RGB{rgb}) - {count} pixels")

        if m['caption_evidence']:
            print(f"  Caption color evidence:")
            for hex_c, count, rgb in m['caption_evidence']:
                print(f"    {hex_c} (RGB{rgb}) - {count} pixels")

        if m['suggested_fix']:
            print(f"  → SUGGESTED FIX: Change to '{m['suggested_fix']} eyes'")
        else:
            print(f"  → UNCLEAR - Need manual review")

        print()

print(f"\n{'='*100}")
print("RECOMMENDATION")
print(f"{'='*100}")
print(f"Files needing review: {len([m for m in mismatches if m['suggested_fix']])}")
print(f"Files needing manual check: {len([m for m in mismatches if not m['suggested_fix']])} + {len(uncertain)}")
print()
print("Next step: Review the mismatches and decide whether to:")
print("  1. Fix captions to match actual pixels")
print("  2. Fix pixel art to match captions")
print("  3. Accept current state")
