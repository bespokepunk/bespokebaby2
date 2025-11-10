#!/usr/bin/env python3
"""
Fix caption issues:
1. Expand palettes from 5 colors to 12-15 colors by extracting from image
2. Fix typos (buna -> bun, dakr blow -> dark, etc.)
3. Remove vague words like "like" and "somewhat"
4. Clarify checkered patterns (bricklike for rectangles)
5. Fix spacing issues
"""

import os
import re
from PIL import Image
from collections import Counter

SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

def get_image_palette(image_path, num_colors=15):
    """Extract top colors from image"""
    try:
        img = Image.open(image_path).convert('RGB')
        pixels = list(img.getdata())
        color_counts = Counter(pixels)
        top_colors = color_counts.most_common(num_colors)

        hex_colors = []
        for (r, g, b), count in top_colors:
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            hex_colors.append(hex_color)

        return hex_colors
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def fix_caption_text(text):
    """Fix typos and improve wording"""

    # Specific typo fixes
    fixes = {
        "buna ": "bun ",
        "dakr blow ": "dark ",
        "dakr ": "dark ",
        "pinkpiskpurple": "pink purple",
        "purplelips": "purple, lips",
        "bodyusuit": "bodysuit",
        "clight creme": "light creme",
        "multicolored background 0": "multicolored background of",

        # Remove vague words
        " like ": " ",
        " somewhat ": " slightly ",
        "somewhat ": "slightly ",
    }

    for old, new in fixes.items():
        text = text.replace(old, new)

    # Fix double spaces
    text = re.sub(r'\s+', ' ', text)

    # Clarify checkered patterns
    if "checkered" in text and "brick" not in text:
        # Check if it should be brick pattern (rectangles)
        text = text.replace("checkered background", "checkered brick background")

    return text

def expand_palette(text, png_filename):
    """Expand palette from 5 to 12-15 colors"""

    png_path = os.path.join(SOURCE_DIR, png_filename)
    if not os.path.exists(png_path):
        return text

    # Extract current palette
    palette_match = re.search(r'palette: ([^,]+(?:, [^,]+)*)', text)
    if not palette_match:
        return text

    current_palette = palette_match.group(1)
    current_colors = [c.strip() for c in current_palette.split(',')]

    # Get extended palette from image
    image_colors = get_image_palette(png_path, 15)
    if not image_colors:
        return text

    # Combine current colors with new ones, removing duplicates while preserving order
    all_colors = []
    seen = set()

    # Keep existing colors first
    for color in current_colors:
        color_lower = color.lower()
        if color_lower not in seen:
            all_colors.append(color)
            seen.add(color_lower)

    # Add new colors from image
    for color in image_colors:
        color_lower = color.lower()
        if color_lower not in seen and len(all_colors) < 15:
            all_colors.append(color)
            seen.add(color_lower)

    # Ensure we have at least 12 colors
    if len(all_colors) < 12:
        return text

    # Replace palette
    new_palette = ", ".join(all_colors[:15])  # Cap at 15
    text = re.sub(r'palette: [^,]+(?:, [^,]+)*', f'palette: {new_palette}', text)

    return text

def main():
    print("🔧 Fixing caption improvements...\n")

    fixed_count = 0
    for filename in sorted(os.listdir(SOURCE_DIR)):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(SOURCE_DIR, filename)
        png_filename = filename.replace('.txt', '.png')

        with open(filepath, 'r') as f:
            original = f.read()

        # Fix text issues first
        fixed = fix_caption_text(original)

        # Expand palette
        fixed = expand_palette(fixed, png_filename)

        if fixed != original:
            with open(filepath, 'w') as f:
                f.write(fixed)
            print(f"  ✅ Fixed: {filename}")
            fixed_count += 1

    print(f"\n✨ Fixed {fixed_count} caption files!")

if __name__ == "__main__":
    main()
