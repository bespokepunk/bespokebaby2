#!/usr/bin/env python3
"""
CORRECT smile vs neutral detection.
The key insight: We need to look at the SHAPE of the mouth, not just its size.

NEUTRAL: Straight horizontal line, all y-coordinates very similar
SMILE: Clear curve, y-coordinates vary significantly with center lower/higher than edges
"""

import os
import re
from PIL import Image
from collections import Counter

def detect_expression_correct(image_path):
    """
    Correct detection based on mouth SHAPE analysis.

    The key is analyzing the Y-coordinate pattern across the mouth:
    - NEUTRAL: Y-coords are mostly uniform (straight line)
    - SMILE: Y-coords show a curve pattern
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Detect scale
    if width == 512:
        scale = 21.3
        # Mouth area for 512x512 upscaled image
        mouth_y_start = int(15 * scale)
        mouth_y_end = int(19 * scale)
        mouth_x_start = int(8 * scale)
        mouth_x_end = int(17 * scale)
    else:
        scale = 1
        mouth_y_start = 15
        mouth_y_end = 19
        mouth_x_start = 8
        mouth_x_end = 17

    # Collect mouth pixels with their positions
    mouth_pixels = []
    for y in range(mouth_y_start, mouth_y_end):
        if y >= height:
            break
        for x in range(mouth_x_start, mouth_x_end):
            if x >= width:
                break
            color = pixels[x, y]
            # Exclude black (background) and skin tones (similar to surrounding)
            if color != (0, 0, 0):
                mouth_pixels.append((x, y, color))

    if len(mouth_pixels) < 10:  # Too few pixels to analyze
        return "neutral expression"

    # Group pixels by X coordinate to analyze the shape
    x_to_y = {}
    for x, y, c in mouth_pixels:
        if x not in x_to_y:
            x_to_y[x] = []
        x_to_y[x].append(y)

    if len(x_to_y) < 3:  # Need at least 3 x-positions to detect curve
        return "neutral expression"

    # Get average Y for each X position (to handle multi-pixel thick mouths)
    x_positions = sorted(x_to_y.keys())
    x_avg_y = {x: sum(x_to_y[x]) / len(x_to_y[x]) for x in x_positions}

    # Analyze the Y-coordinate pattern across the mouth width
    # Split into left, center, right thirds
    total_width = len(x_positions)
    third = total_width // 3

    if third < 1:
        return "neutral expression"

    left_third = x_positions[:third]
    center_third = x_positions[third:2*third]
    right_third = x_positions[2*third:]

    if not left_third or not center_third or not right_third:
        return "neutral expression"

    # Calculate average Y for each section
    avg_y_left = sum(x_avg_y[x] for x in left_third) / len(left_third)
    avg_y_center = sum(x_avg_y[x] for x in center_third) / len(center_third)
    avg_y_right = sum(x_avg_y[x] for x in right_third) / len(right_third)

    # Calculate variance in Y coordinates (how much the Y values vary)
    all_y_values = [x_avg_y[x] for x in x_positions]
    mean_y = sum(all_y_values) / len(all_y_values)
    variance = sum((y - mean_y) ** 2 for y in all_y_values) / len(all_y_values)
    std_dev = variance ** 0.5

    # NEUTRAL criteria: Very low variance (straight line)
    # For 512x512, neutral mouths have std_dev < 3-5 pixels
    # For 24x24, neutral mouths have std_dev < 0.5 pixels
    neutral_threshold = 5 * scale if width == 512 else 0.5

    if std_dev < neutral_threshold:
        return "neutral expression"

    # SMILE criteria: Center is noticeably different from edges (curve)
    # Check if mouth curves upward (smile) or downward
    avg_edges = (avg_y_left + avg_y_right) / 2
    center_diff = avg_y_center - avg_edges

    # For smile, center should be lower than edges (higher Y value in image coordinates)
    # OR edges lower than center (for certain smile styles)
    smile_threshold = 10 * scale if width == 512 else 1.5

    # Also check overall Y range
    y_range = max(all_y_values) - min(all_y_values)
    range_threshold = 15 * scale if width == 512 else 2

    # SMILE if:
    # 1. Significant curvature (high std_dev) AND
    # 2. Clear difference between center and edges OR significant Y range
    if std_dev >= neutral_threshold and (abs(center_diff) >= smile_threshold or y_range >= range_threshold):
        return "slight smile"

    # Default to neutral if unclear
    return "neutral expression"

def update_expression(caption_path, image_path, dry_run=False):
    """Update expression in caption file."""
    with open(caption_path, 'r') as f:
        caption = f.read().strip()

    new_expression = detect_expression_correct(image_path)

    # Find current expression
    if 'slight smile' in caption:
        old_expression = 'slight smile'
    elif 'neutral expression' in caption:
        old_expression = 'neutral expression'
    else:
        return False, None, None

    if old_expression == new_expression:
        return False, old_expression, new_expression

    # Update caption
    if not dry_run:
        updated_caption = caption.replace(old_expression, new_expression)
        with open(caption_path, 'w') as f:
            f.write(updated_caption)

    return True, old_expression, new_expression

def main():
    """Process all files."""
    import sys

    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"
    txt_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.txt')])

    print(f"Processing {len(txt_files)} files with CORRECTED smile detection...\n")

    # First do dry run on sample
    print("=" * 80)
    print("DRY RUN - Checking 10 random samples:\n")

    import random
    sample_files = random.sample(txt_files, min(10, len(txt_files)))

    for txt_file in sample_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            continue

        changed, old, new = update_expression(caption_path, image_path, dry_run=True)
        if changed:
            print(f"  {txt_file}: {old} → {new}")
        else:
            print(f"  {txt_file}: {old} (no change)")

    print("\n" + "=" * 80)
    proceed = input("\nProceed with full update? (y/n): ").strip().lower()

    if proceed != 'y':
        print("Aborted.")
        return

    print("\nProcessing all files...\n")

    changes = []
    unchanged = 0

    for txt_file in txt_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(image_path):
            continue

        changed, old, new = update_expression(caption_path, image_path, dry_run=False)

        if changed:
            changes.append((txt_file, old, new))
            print(f"✓ {txt_file}: {old} → {new}")
        else:
            unchanged += 1

    print(f"\n" + "=" * 80)
    print(f"Updated: {len(changes)} files")
    print(f"Unchanged: {unchanged} files")

    smile_to_neutral = sum(1 for _, old, new in changes if old == 'slight smile' and new == 'neutral expression')
    neutral_to_smile = sum(1 for _, old, new in changes if old == 'neutral expression' and new == 'slight smile')

    print(f"\nChanges:")
    print(f"  Smile → Neutral: {smile_to_neutral}")
    print(f"  Neutral → Smile: {neutral_to_smile}")

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

    print(f"\nFinal distribution:")
    print(f"  Slight smile: {final_smiles} ({100*final_smiles/len(txt_files):.1f}%)")
    print(f"  Neutral: {final_neutrals} ({100*final_neutrals/len(txt_files):.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
