#!/usr/bin/env python3
"""
Extract dominant colors from training images to fix caption hex codes

For each image, extract:
- Background color (edges of image)
- Hair color (top region)
- Skin color (center region)
- Most common colors overall

Usage:
    python scripts/extract_image_colors.py runpod_package/training_data
"""

import sys
from pathlib import Path
from PIL import Image
from collections import Counter
import re

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def extract_background_color(img):
    """Extract background color from image edges"""
    width, height = img.size

    # Sample pixels from all 4 edges
    edge_pixels = []

    # Top edge
    for x in range(width):
        edge_pixels.append(img.getpixel((x, 0)))

    # Bottom edge
    for x in range(width):
        edge_pixels.append(img.getpixel((x, height - 1)))

    # Left edge
    for y in range(height):
        edge_pixels.append(img.getpixel((0, y)))

    # Right edge
    for y in range(height):
        edge_pixels.append(img.getpixel((width - 1, y)))

    # Find most common color
    counter = Counter(edge_pixels)
    most_common_rgb = counter.most_common(1)[0][0]

    return rgb_to_hex(most_common_rgb)

def extract_hair_color(img):
    """Extract hair color from top region of image"""
    width, height = img.size

    # Sample top 30% of image (where hair usually is)
    hair_pixels = []
    for y in range(int(height * 0.3)):
        for x in range(width):
            hair_pixels.append(img.getpixel((x, y)))

    counter = Counter(hair_pixels)
    # Get top 3 most common colors (hair might have highlights/shadows)
    top_colors = counter.most_common(3)

    return [rgb_to_hex(rgb) for rgb, count in top_colors]

def extract_skin_color(img):
    """Extract skin color from center region"""
    width, height = img.size

    # Sample center region (where face usually is)
    skin_pixels = []
    center_x_start = int(width * 0.3)
    center_x_end = int(width * 0.7)
    center_y_start = int(height * 0.3)
    center_y_end = int(height * 0.7)

    for y in range(center_y_start, center_y_end):
        for x in range(center_x_start, center_x_end):
            skin_pixels.append(img.getpixel((x, y)))

    counter = Counter(skin_pixels)
    most_common_rgb = counter.most_common(1)[0][0]

    return rgb_to_hex(most_common_rgb)

def extract_all_colors(img, top_n=10):
    """Extract top N most common colors from entire image"""
    pixels = list(img.getdata())
    counter = Counter(pixels)
    top_colors = counter.most_common(top_n)

    return [(rgb_to_hex(rgb), count, count/len(pixels)*100) for rgb, count in top_colors]

def analyze_image(image_path: Path) -> dict:
    """Analyze a single image and extract color information"""
    try:
        img = Image.open(image_path).convert('RGB')

        return {
            'filepath': str(image_path),
            'background': extract_background_color(img),
            'hair': extract_hair_color(img),
            'skin': extract_skin_color(img),
            'top_colors': extract_all_colors(img, top_n=10)
        }
    except Exception as e:
        return {
            'filepath': str(image_path),
            'error': str(e)
        }

def find_duplicate_hex_codes(caption: str) -> dict:
    """Find duplicate hex codes in caption"""
    pattern = r'(\w+(?:\s+\w+)*)\s*\(#([0-9a-fA-F]{6})\)'
    matches = re.findall(pattern, caption)

    hex_to_features = {}
    for label, hex_code in matches:
        hex_code_lower = f"#{hex_code.lower()}"
        if hex_code_lower not in hex_to_features:
            hex_to_features[hex_code_lower] = []
        hex_to_features[hex_code_lower].append(label)

    duplicates = {hex_code: features for hex_code, features in hex_to_features.items()
                  if len(features) > 1}

    return duplicates

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    # Find all image files
    image_files = sorted(list(data_dir.glob('*.png')) + list(data_dir.glob('*.jpg')))

    print(f"🎨 Analyzing {len(image_files)} images...\n")

    results = []

    for image_path in image_files[:10]:  # Analyze first 10 as sample
        result = analyze_image(image_path)

        if 'error' not in result:
            print(f"✅ {image_path.name}")
            print(f"   Background: {result['background']}")
            print(f"   Hair (top 3): {', '.join(result['hair'])}")
            print(f"   Skin: {result['skin']}")
            print(f"   Top 3 colors: {', '.join([f'{hex} ({pct:.1f}%)' for hex, count, pct in result['top_colors'][:3]])}")

            # Check corresponding caption for duplicates
            caption_path = image_path.with_suffix('.txt')
            if caption_path.exists():
                with open(caption_path, 'r') as f:
                    caption = f.read()

                duplicates = find_duplicate_hex_codes(caption)
                if duplicates:
                    print(f"   ⚠️  DUPLICATE HEX CODES IN CAPTION:")
                    for hex_code, features in duplicates.items():
                        print(f"      {hex_code}: {', '.join(features)}")

            print()
            results.append(result)
        else:
            print(f"❌ {image_path.name}: {result['error']}\n")

    print("=" * 80)
    print(f"📊 ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Images analyzed: {len(results)}")
    print(f"\nThis provides color data to fix duplicate hex codes in captions.")
    print(f"Use this data to manually update captions where features share hex codes.")

if __name__ == "__main__":
    main()
