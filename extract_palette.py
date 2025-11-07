#!/usr/bin/env python3
"""
Extract unique colors from training images to create a palette for SD-πXL
"""

from PIL import Image
from pathlib import Path
from collections import Counter

def extract_palette():
    """Extract all unique colors from training images"""

    print("=" * 80)
    print("🎨 EXTRACTING COLOR PALETTE FROM TRAINING IMAGES")
    print("=" * 80)

    image_dir = Path("FORTRAINING6/bespokepunktextimages")
    image_files = sorted(image_dir.glob("*.png"))

    print(f"\n📊 Analyzing {len(image_files)} images...")

    all_colors = set()
    color_counts = Counter()

    for img_path in image_files:
        img = Image.open(img_path).convert('RGB')
        pixels = list(img.getdata())

        for pixel in pixels:
            all_colors.add(pixel)
            color_counts[pixel] += 1

    print(f"✅ Found {len(all_colors)} unique colors")

    # Sort by frequency
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

    # Save as .hex file for SD-πXL
    palette_path = Path("SD-piXL/assets/palettes/bespoke_punk.hex")
    palette_path.parent.mkdir(parents=True, exist_ok=True)

    with open(palette_path, 'w') as f:
        for (r, g, b), count in sorted_colors:
            hex_color = f"{r:02x}{g:02x}{b:02x}"
            f.write(f"{hex_color}\n")

    print(f"\n💾 Saved palette to: {palette_path}")
    print(f"📊 Total colors: {len(all_colors)}")
    print(f"\n🎨 Top 10 most used colors:")
    for i, ((r, g, b), count) in enumerate(sorted_colors[:10], 1):
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        print(f"   {i:2d}. {hex_color} - used {count:5d} times")

    print("\n✅ Palette extraction complete!")
    return palette_path

if __name__ == "__main__":
    extract_palette()
