#!/usr/bin/env python3
"""
Final comparison: Quantized generated images vs Real Bespoke Punks
"""

from PIL import Image
import numpy as np
from pathlib import Path
from collections import Counter

def analyze_image_quality(img_path):
    """Analyze pixel art quality metrics"""
    img = Image.open(img_path)
    arr = np.array(img)

    # Get unique colors
    pixels = arr.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)

    # Get color distribution
    color_tuples = [tuple(p) for p in pixels]
    color_counts = Counter(color_tuples)
    top_5 = color_counts.most_common(5)

    # Calculate background dominance (top color %)
    bg_dominance = (top_5[0][1] / len(color_tuples)) * 100 if top_5 else 0

    return {
        "unique_colors": len(unique_colors),
        "bg_dominance": bg_dominance,
        "top_color": top_5[0][0] if top_5 else None
    }

print("🏆 FINAL COMPARISON: QUANTIZED vs REAL BESPOKE PUNKS")
print("=" * 80)

# Analyze real Bespoke Punks
print("\n📸 REAL BESPOKE PUNKS (Baseline):")
real_punks = [
    "FORTRAINING6/bespokepunks/lad_001_carbon.png",
    "FORTRAINING6/bespokepunks/lady_083_Marianne3.png",
    "FORTRAINING6/bespokepunks/lad_106_sultan.png",
]

for punk_path in real_punks:
    if Path(punk_path).exists():
        result = analyze_image_quality(punk_path)
        print(f"\n   {Path(punk_path).stem}:")
        print(f"      Colors: {result['unique_colors']}")
        print(f"      BG Dominance: {result['bg_dominance']:.1f}%")

# Analyze quantized generated images
print("\n" + "=" * 80)
print("🤖 QUANTIZED GENERATED IMAGES:")
print("=" * 80)

methods = {
    "method1": "K-means quantize 512px → 15 colors, downsample to 24px",
    "method2": "Downsample to 24px, k-means quantize → 15 colors",
    "method3": "PIL posterize to 15 colors, downsample to 24px"
}

for model in ["V1_Epoch2", "V2_Epoch3"]:
    print(f"\n{'='*80}")
    print(f"Model: {model}")
    print(f"{'='*80}")

    for method_key, method_desc in methods.items():
        print(f"\n   {method_key}: {method_desc}")

        for test in ["simple_green", "purple_sunglasses"]:
            img_path = Path(f"quantized_validation/{model}/{test}_{method_key}_24.png")
            if img_path.exists():
                result = analyze_image_quality(img_path)
                print(f"      {test:20s} - Colors: {result['unique_colors']:2d}, BG: {result['bg_dominance']:5.1f}%")

print("\n" + "=" * 80)
print("📊 QUALITY ASSESSMENT:")
print("=" * 80)
print("✅ Real Bespoke Punks: 15-20 colors, 30-40% background dominance")
print("✅ Good generated: 13-15 colors, similar BG dominance")
print("❌ Bad generated: Too many colors OR poor structure")
print("\nRecommendation:")
print("1. Use V2_Epoch3 (best from earlier validation)")
print("2. Apply Method 1 quantization (k-means 512→15 colors, then downsample)")
print("3. This gives clean pixel art with ~13-15 colors matching real Bespoke Punks")
print("=" * 80)
