#!/usr/bin/env python3
"""
Analyze if generated images are TRUE pixel art or have anti-aliasing
"""

from PIL import Image
import numpy as np
from pathlib import Path
from collections import Counter

def analyze_image(img_path):
    """Analyze an image for pixel art characteristics"""
    img = Image.open(img_path)
    arr = np.array(img)

    # Get unique colors
    pixels = arr.reshape(-1, arr.shape[2])
    unique_colors = np.unique(pixels, axis=0)

    # Calculate color histogram
    color_tuples = [tuple(p) for p in pixels]
    color_counts = Counter(color_tuples)

    # Sort by frequency
    top_colors = color_counts.most_common(10)

    return {
        "path": Path(img_path),
        "size": img.size,
        "total_pixels": arr.shape[0] * arr.shape[1],
        "unique_colors": len(unique_colors),
        "top_10_colors": top_colors,
        "dominant_color": top_colors[0] if top_colors else None
    }

print("🔍 PIXEL-PERFECT ANALYSIS")
print("=" * 80)

# Analyze real training punk (upscaled but from original)
print("\n📸 REAL BESPOKE PUNK (from training data):")
real_punk = analyze_image("FORTRAINING6/bespokepunks/lad_001_carbon.png")
print(f"   File: {real_punk['path'].name}")
print(f"   Size: {real_punk['size']}")
print(f"   Total Pixels: {real_punk['total_pixels']}")
print(f"   Unique Colors: {real_punk['unique_colors']}")
print(f"   Top 5 Colors:")
for i, (color, count) in enumerate(real_punk['top_10_colors'][:5], 1):
    pct = (count / real_punk['total_pixels']) * 100
    print(f"      {i}. RGB{color} - {count} pixels ({pct:.1f}%)")

# Analyze generated 24x24 images
print("\n" + "=" * 80)
print("🤖 GENERATED 24x24 IMAGES:")
print("=" * 80)

for model in ["V1_Epoch2", "V2_Epoch3"]:
    print(f"\n{model}:")
    for test_name in ["simple_green", "purple_sunglasses"]:
        img_path = Path(f"true_24x24_validation/{model}/{test_name}_24.png")
        if img_path.exists():
            result = analyze_image(img_path)
            print(f"\n   {test_name}:")
            print(f"      Size: {result['size']}")
            print(f"      Unique Colors: {result['unique_colors']}")
            print(f"      Top 5 Colors:")
            for i, (color, count) in enumerate(result['top_10_colors'][:5], 1):
                pct = (count / result['total_pixels']) * 100
                print(f"         {i}. RGB{color} - {count} pixels ({pct:.1f}%)")

print("\n" + "=" * 80)
print("📊 ANALYSIS:")
print("=" * 80)
print("Real Bespoke Punks should have ~8-15 unique colors")
print("If generated images have 100+ colors, they have anti-aliasing artifacts")
print("This means they DON'T match true Bespoke Punk pixel art style")
print("=" * 80)
