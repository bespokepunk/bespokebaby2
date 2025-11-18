#!/usr/bin/env python3
"""
Script to enhance Freepik prompts with color palette data from Aseprite files
"""

import os
import re
from pathlib import Path
from PIL import Image
import json
from collections import Counter

# Paths
BASE_DIR = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2")
PROMPTS_FILE = BASE_DIR / "bespoke-punks-website/FREEPIK_PROMPTS.md"
ASEPRITE_DIR = BASE_DIR / "Aseperite/all"
OUTPUT_FILE = BASE_DIR / "bespoke-punks-website/FREEPIK_PROMPTS_ENHANCED_COMPLETE_2025-11-18.md"

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_color_palette_from_png(png_path):
    """Extract color palette from PNG file"""
    try:
        img = Image.open(png_path).convert('RGB')
        pixels = list(img.getdata())

        # Count color occurrences
        color_counts = Counter(pixels)

        # Get top colors (excluding pure black and white for transparency)
        colors = []
        for color, count in color_counts.most_common(20):
            # Skip pure black and pure white (likely transparency/background)
            if color == (0, 0, 0) or color == (255, 255, 255):
                continue
            colors.append({
                'hex': rgb_to_hex(color),
                'rgb': color,
                'count': count
            })
            if len(colors) >= 10:
                break

        return colors
    except Exception as e:
        print(f"Error reading {png_path}: {e}")
        return []

def get_punk_aseprite_files():
    """Get dictionary of punk name -> aseprite file path"""
    aseprite_files = {}

    for file in ASEPRITE_DIR.glob("*.aseprite"):
        # Extract punk identifier (e.g., "lady_000_lemon" from "lady_000_lemon.aseprite")
        punk_name = file.stem
        aseprite_files[punk_name] = file

    return aseprite_files

def get_punk_png_files():
    """Get dictionary of punk name -> PNG file path"""
    png_files = {}

    for file in ASEPRITE_DIR.glob("*.png"):
        punk_name = file.stem
        png_files[punk_name] = file

    return png_files

def extract_punk_name_from_header(line):
    """Extract punk identifier from header line like '### lady_000_lemon'"""
    match = re.match(r'###\s+(lad(?:y)?_\d+_[\w\-]+)', line)
    if match:
        return match.group(1)
    return None

def get_color_description(colors):
    """Generate rich color description from palette"""
    if not colors:
        return ""

    # Describe dominant colors
    descriptions = []
    for i, color in enumerate(colors[:5]):
        hex_val = color['hex']
        descriptions.append(hex_val)

    return ", ".join(descriptions)

def enhance_prompt_with_colors(prompt_text, colors):
    """Enhance a prompt with color palette information"""
    if not colors:
        return prompt_text

    # Get hex values
    hex_colors = [c['hex'] for c in colors[:6]]
    color_list = ", ".join(hex_colors)

    # Insert color information at the beginning of the prompt
    # Look for the first sentence that describes the scene
    lines = prompt_text.split('\n')
    enhanced_lines = []

    for i, line in enumerate(lines):
        if i == 0 and line.strip():
            # Add color palette to the first line of the prompt
            enhanced_line = line.rstrip('.')
            enhanced_line += f". **Color palette: {color_list}**. "
            enhanced_lines.append(enhanced_line)
        else:
            enhanced_lines.append(line)

    return '\n'.join(enhanced_lines)

def process_prompts():
    """Main processing function"""
    print("=" * 80)
    print("FREEPIK PROMPT ENHANCER")
    print("=" * 80)

    # Get available files
    aseprite_files = get_punk_aseprite_files()
    png_files = get_punk_png_files()

    print(f"\nFound {len(aseprite_files)} Aseprite files")
    print(f"Found {len(png_files)} PNG files")

    # Read original prompts
    with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into sections by punk
    sections = re.split(r'(###\s+lad(?:y)?_\d+_[\w\-]+)', content)

    # Reconstruct with enhancements
    enhanced_content = []
    enhanced_content.append(sections[0])  # Header/intro

    stats = {
        'total': 0,
        'enhanced': 0,
        'marked_todo': 0
    }

    # Process each punk section
    for i in range(1, len(sections), 2):
        if i >= len(sections):
            break

        header = sections[i]
        prompt_text = sections[i + 1] if i + 1 < len(sections) else ""

        punk_name = extract_punk_name_from_header(header)

        if not punk_name:
            enhanced_content.append(header)
            enhanced_content.append(prompt_text)
            continue

        stats['total'] += 1

        # Check if we have files for this punk
        has_aseprite = punk_name in aseprite_files
        has_png = punk_name in png_files

        if has_aseprite or has_png:
            # Get color palette from PNG
            colors = []
            if has_png:
                colors = get_color_palette_from_png(png_files[punk_name])

            if colors:
                # Enhance the prompt
                enhanced_prompt = enhance_prompt_with_colors(prompt_text, colors)
                enhanced_content.append(header)
                enhanced_content.append(enhanced_prompt)
                stats['enhanced'] += 1
                print(f"✓ Enhanced: {punk_name} ({len(colors)} colors)")
            else:
                # Has file but couldn't extract colors
                enhanced_content.append(header)
                enhanced_content.append(prompt_text)
                print(f"⚠ No colors extracted: {punk_name}")
        else:
            # No files available - mark as TODO
            enhanced_content.append(header)
            enhanced_content.append(f"\n**[TODO: ENHANCE WHEN ASEPRITE FILE AVAILABLE]**\n{prompt_text}")
            stats['marked_todo'] += 1
            print(f"⊗ Marked TODO: {punk_name}")

    # Write enhanced file
    final_content = ''.join(enhanced_content)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total punks: {stats['total']}")
    print(f"Enhanced: {stats['enhanced']}")
    print(f"Marked TODO: {stats['marked_todo']}")
    print(f"\nOutput saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_prompts()
