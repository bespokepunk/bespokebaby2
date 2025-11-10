#!/usr/bin/env python3
"""
Add lips (with hex color) and facial expression to caption files missing them.
Version 2: Handles edge cases better.
"""

import os
import re
from PIL import Image
from collections import Counter

def rgb_to_hex(r, g, b):
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"

def get_dominant_lip_color(image_path):
    """
    Extract the dominant lip color from a 24x24 pixel art image.
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Focus on lower face area where lips typically are
    lip_colors = []

    for y in range(14, 18):
        for x in range(8, 17):
            if x < width and y < height:
                color = pixels[x, y]
                lip_colors.append(color)

    if not lip_colors:
        for y in range(height//2, height):
            for x in range(width//3, 2*width//3):
                lip_colors.append(pixels[x, y])

    color_counts = Counter(lip_colors)
    color_counts = {k: v for k, v in color_counts.items() if k != (0, 0, 0)}

    if not color_counts:
        return None

    dominant_color = max(color_counts.items(), key=lambda x: x[1])[0]
    return rgb_to_hex(*dominant_color)

def detect_expression(image_path):
    """Detect if the character has a smile or neutral expression."""
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    mouth_pixels = []
    for y in range(15, 19):
        for x in range(9, 16):
            if x < width and y < height:
                color = pixels[x, y]
                if color != (0, 0, 0):
                    mouth_pixels.append((x, y, color))

    if len(mouth_pixels) > 3:
        y_coords = [p[1] for p in mouth_pixels]
        if max(y_coords) - min(y_coords) >= 2:
            return "slight smile"

    return "neutral expression"

def update_caption_with_lips(caption_path, image_path):
    """
    Update a caption file to include lips with hex color and expression.
    """
    with open(caption_path, 'r') as f:
        caption = f.read().strip()

    lip_color = get_dominant_lip_color(image_path)
    if not lip_color:
        print(f"⚠️  Could not detect lip color for {os.path.basename(caption_path)}")
        return False

    expression = detect_expression(image_path)
    lips_text = f"lips ({lip_color}), {expression}, "

    # Strategy: Insert lips before "skin tone" pattern
    # This covers most variations

    # Pattern 1: "medium/light/dark/pale ... skin"
    skin_patterns = [
        r'(medium|light|dark|pale|olive)\s+.*?skin',
        r'(medium|light|dark|pale)\s+(black|white|brown|green|pink|yellow|blue|red|purple|orange)\s+skin',
        r'skin\s+\(#[0-9a-f]{6}\)',
    ]

    inserted = False
    for pattern in skin_patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            insert_pos = match.start()
            updated_caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
            with open(caption_path, 'w') as f:
                f.write(updated_caption)
            print(f"✓ Updated {os.path.basename(caption_path)}: lips {lip_color}, {expression}")
            inserted = True
            break

    if not inserted:
        # Fallback: Insert after eyes pattern (any variation)
        eye_patterns = [
            r'eyes\s+\(#[0-9a-f]{6}\),\s*',
            r'eyes\s+underneath\s+\(#[0-9a-f]{6}\),\s*',
        ]

        for pattern in eye_patterns:
            match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                insert_pos = match.end()
                updated_caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
                with open(caption_path, 'w') as f:
                    f.write(updated_caption)
                print(f"✓ Updated {os.path.basename(caption_path)}: lips {lip_color}, {expression}")
                inserted = True
                break

    if not inserted:
        # Last resort: Insert before "background"
        bg_match = re.search(r'(solid|gradient|checkered|brick|striped)\s+background', caption, re.IGNORECASE)
        if bg_match:
            insert_pos = bg_match.start()
            updated_caption = caption[:insert_pos] + lips_text + caption[insert_pos:]
            with open(caption_path, 'w') as f:
                f.write(updated_caption)
            print(f"✓ Updated {os.path.basename(caption_path)}: lips {lip_color}, {expression}")
            inserted = True

    if not inserted:
        print(f"⚠️  Could not find insertion point for {os.path.basename(caption_path)}")
        print(f"    Caption preview: {caption[:150]}...")
        return False

    return True

def main():
    """Process all caption files missing lips."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

    # Get the 14 failed files from previous run
    failed_files = [
        "lad_024_x.txt",
        "lad_032_shaman-4.txt",
        "lad_036_x.txt",
        "lad_037_aressprout.txt",
        "lad_038_cashking-6.txt",
        "lad_047_CYGAAR1.txt",
        "lad_061_DOPE10.txt",
        "lad_061_DOPE7.txt",
        "lad_061_DOPE9.txt",
        "lad_081_iggy2.txt",
        "lad_086_Scooby.txt",
        "lad_088_Kareem.txt",
        "lad_090_drscott.txt",
        "lady_099_VQ.txt",
    ]

    print(f"Processing {len(failed_files)} failed caption files...\n")

    success_count = 0
    failed_count = 0

    for txt_file in failed_files:
        caption_path = os.path.join(base_dir, txt_file)
        image_path = caption_path.replace('.txt', '.png')

        if not os.path.exists(caption_path):
            print(f"⚠️  Caption not found: {caption_path}")
            failed_count += 1
            continue

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found: {image_path}")
            failed_count += 1
            continue

        if update_caption_with_lips(caption_path, image_path):
            success_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*60}")
    print(f"✓ Successfully updated: {success_count} files")
    print(f"✗ Failed: {failed_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
