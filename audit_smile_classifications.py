#!/usr/bin/env python3
"""
Audit smile vs neutral classifications by showing images with their current classification.
This helps visually verify if the automatic detection was correct.
"""

import os
import re
from PIL import Image

def extract_expression(caption_path):
    """Extract the current expression from caption."""
    with open(caption_path, 'r') as f:
        caption = f.read()

    if 'slight smile' in caption:
        return 'slight smile'
    elif 'neutral expression' in caption:
        return 'neutral expression'
    else:
        return 'UNKNOWN'

def analyze_mouth_pixels(image_path):
    """Analyze mouth area and return statistics."""
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # For 512x512 upscaled images (24x -> 512x means ~21.3x scale)
    # Mouth area would be roughly rows 320-400, cols 170-340
    # For 24x24 original, mouth is rows 15-19, cols 8-16

    # Detect if this is upscaled or original
    if width == 512:
        # Upscaled image
        scale = 21.3
        mouth_rows = range(int(15*scale), int(19*scale))
        mouth_cols = range(int(8*scale), int(17*scale))
    else:
        # Original 24x24
        mouth_rows = range(15, 19)
        mouth_cols = range(8, 17)

    mouth_pixels = []
    for y in mouth_rows:
        if y >= height:
            break
        for x in mouth_cols:
            if x >= width:
                break
            color = pixels[x, y]
            if color != (0, 0, 0):  # Non-black
                mouth_pixels.append((x, y, color))

    if not mouth_pixels:
        return None

    y_coords = [p[1] for p in mouth_pixels]
    x_coords = [p[0] for p in mouth_pixels]

    y_range = max(y_coords) - min(y_coords) if y_coords else 0
    x_range = max(x_coords) - min(x_coords) if x_coords else 0

    return {
        'pixel_count': len(mouth_pixels),
        'y_range': y_range,
        'x_range': x_range,
        'y_min': min(y_coords) if y_coords else 0,
        'y_max': max(y_coords) if y_coords else 0,
    }

def main():
    """Audit all files and report statistics."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

    txt_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.txt')])

    print(f"Auditing {len(txt_files)} files...\n")
    print("=" * 80)

    smile_stats = []
    neutral_stats = []

    for txt_file in txt_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            continue

        expression = extract_expression(caption_path)
        stats = analyze_mouth_pixels(image_path)

        if stats and expression == 'slight smile':
            smile_stats.append(stats)
        elif stats and expression == 'neutral expression':
            neutral_stats.append(stats)

    print(f"\nClassification Statistics:\n")
    print(f"Slight Smile: {len(smile_stats)} files")
    if smile_stats:
        avg_y_range = sum(s['y_range'] for s in smile_stats) / len(smile_stats)
        avg_pixel_count = sum(s['pixel_count'] for s in smile_stats) / len(smile_stats)
        print(f"  Average Y range: {avg_y_range:.1f} pixels")
        print(f"  Average pixel count: {avg_pixel_count:.1f} pixels")

    print(f"\nNeutral Expression: {len(neutral_stats)} files")
    if neutral_stats:
        avg_y_range = sum(s['y_range'] for s in neutral_stats) / len(neutral_stats)
        avg_pixel_count = sum(s['pixel_count'] for s in neutral_stats) / len(neutral_stats)
        print(f"  Average Y range: {avg_y_range:.1f} pixels")
        print(f"  Average pixel count: {avg_pixel_count:.1f} pixels")

    print(f"\n" + "=" * 80)
    print(f"Total files classified: {len(smile_stats) + len(neutral_stats)}")
    print(f"Smiles: {len(smile_stats)} ({100*len(smile_stats)/(len(smile_stats)+len(neutral_stats)):.1f}%)")
    print(f"Neutral: {len(neutral_stats)} ({100*len(neutral_stats)/(len(smile_stats)+len(neutral_stats)):.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
