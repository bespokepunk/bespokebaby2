#!/usr/bin/env python3
"""
DEEP VISUAL ANALYSIS: Compare generated outputs to real Bespoke Punks
Identify what's missing or wrong to make better training recommendations
"""

import numpy as np
from PIL import Image
from pathlib import Path
from collections import Counter
import json

def analyze_image(img_path):
    """Analyze a single image for pixel art qualities"""
    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)

    # Get unique colors
    pixels = arr.reshape(-1, 3)
    unique_colors = set(tuple(p) for p in pixels)

    # Color histogram
    color_counts = Counter(tuple(p) for p in pixels)
    total_pixels = len(pixels)

    # Find dominant background color (most frequent)
    most_common = color_counts.most_common(1)[0]
    bg_color = most_common[0]
    bg_percentage = (most_common[1] / total_pixels) * 100

    # Check for anti-aliasing (colors that appear very few times)
    rare_colors = [c for c, count in color_counts.items() if count < 5]

    # Check for gradients (many similar colors)
    has_gradient = len(unique_colors) > 25

    # Analyze pixel sharpness
    # True pixel art should have sharp edges, not blurred
    is_sharp = len(rare_colors) < len(unique_colors) * 0.3

    return {
        'path': str(img_path),
        'size': img.size,
        'total_colors': len(unique_colors),
        'bg_color': bg_color,
        'bg_percentage': bg_percentage,
        'rare_colors': len(rare_colors),
        'has_gradient': has_gradient,
        'is_sharp': is_sharp,
        'color_distribution': dict(color_counts.most_common(10))
    }

def analyze_directory(dir_path, label):
    """Analyze all images in a directory"""
    results = []
    for img_path in Path(dir_path).glob('*.png'):
        try:
            analysis = analyze_image(img_path)
            analysis['label'] = label
            results.append(analysis)
        except Exception as e:
            print(f"Error analyzing {img_path}: {e}")
    return results

def compare_to_originals(generated_results, original_results):
    """Compare generated images to originals"""

    gen_avg_colors = np.mean([r['total_colors'] for r in generated_results])
    orig_avg_colors = np.mean([r['total_colors'] for r in original_results])

    gen_sharp = sum(1 for r in generated_results if r['is_sharp']) / len(generated_results)
    orig_sharp = sum(1 for r in original_results if r['is_sharp']) / len(original_results)

    gen_gradient = sum(1 for r in generated_results if r['has_gradient']) / len(generated_results)
    orig_gradient = sum(1 for r in original_results if r['has_gradient']) / len(original_results)

    print("\n" + "="*80)
    print("📊 COMPARISON: Generated vs Original Bespoke Punks")
    print("="*80)

    print(f"\n📈 Average Color Count:")
    print(f"  Generated: {gen_avg_colors:.1f} colors")
    print(f"  Original:  {orig_avg_colors:.1f} colors")
    print(f"  Difference: {abs(gen_avg_colors - orig_avg_colors):.1f} colors")

    print(f"\n✨ Sharpness (true pixel art):")
    print(f"  Generated: {gen_sharp*100:.1f}% sharp")
    print(f"  Original:  {orig_sharp*100:.1f}% sharp")

    print(f"\n🌈 Gradient Usage:")
    print(f"  Generated: {gen_gradient*100:.1f}% have gradients")
    print(f"  Original:  {orig_gradient*100:.1f}% have gradients")

    # Identify problems
    problems = []
    recommendations = []

    if gen_avg_colors > orig_avg_colors + 5:
        problems.append(f"Generated images have TOO MANY colors ({gen_avg_colors:.0f} vs {orig_avg_colors:.0f})")
        recommendations.append("Reduce color count in training or use stronger quantization (8-12 colors)")

    if gen_avg_colors < orig_avg_colors - 5:
        problems.append(f"Generated images have TOO FEW colors ({gen_avg_colors:.0f} vs {orig_avg_colors:.0f})")
        recommendations.append("Allow more colors in training captions or use weaker quantization")

    if gen_sharp < orig_sharp - 0.2:
        problems.append(f"Generated images are BLURRY/ANTI-ALIASED ({gen_sharp*100:.0f}% vs {orig_sharp*100:.0f}%)")
        recommendations.append("Add 'no anti-aliasing, sharp pixel edges' to ALL captions")
        recommendations.append("Consider using ControlNet with edge detection")

    if gen_gradient > orig_gradient + 0.2:
        problems.append(f"Generated images have TOO MANY GRADIENTS ({gen_gradient*100:.0f}% vs {orig_gradient*100:.0f}%)")
        recommendations.append("Add 'flat colors, no gradients' to captions")
        recommendations.append("Remove gradient examples from training or label them clearly")

    return problems, recommendations

def main():
    print("🔍 DEEP VISUAL ANALYSIS - Bespoke Punks")
    print("Comparing generated outputs to original training images\n")

    # Analyze original Bespoke Punks
    print("📁 Analyzing original Bespoke Punks...")
    originals = analyze_directory("FORTRAINING6/bespokepunks", "Original")
    print(f"   Found {len(originals)} original images")

    # Analyze generated outputs from best models
    print("\n📁 Analyzing V1_Epoch2 outputs...")
    v1_outputs = []
    for prompt_dir in Path("comprehensive_evaluation/V1_Epoch2").iterdir():
        if prompt_dir.is_dir():
            # Only analyze the 24x24 final outputs
            for img in prompt_dir.glob("*_24.png"):
                v1_outputs.append(analyze_image(img))
    print(f"   Found {len(v1_outputs)} generated images")

    print("\n📁 Analyzing V2_Epoch2 outputs...")
    v2_outputs = []
    for prompt_dir in Path("comprehensive_evaluation/V2_Epoch2").iterdir():
        if prompt_dir.is_dir():
            for img in prompt_dir.glob("*_24.png"):
                v2_outputs.append(analyze_image(img))
    print(f"   Found {len(v2_outputs)} generated images")

    # Compare V1 to originals
    print("\n" + "="*80)
    print("V1_EPOCH2 vs ORIGINALS")
    print("="*80)
    v1_problems, v1_recs = compare_to_originals(v1_outputs, originals)

    # Compare V2 to originals
    print("\n" + "="*80)
    print("V2_EPOCH2 vs ORIGINALS")
    print("="*80)
    v2_problems, v2_recs = compare_to_originals(v2_outputs, originals)

    # Final recommendations
    print("\n" + "="*80)
    print("🎯 PROBLEMS IDENTIFIED")
    print("="*80)

    all_problems = set(v1_problems + v2_problems)
    if all_problems:
        for i, problem in enumerate(all_problems, 1):
            print(f"\n{i}. {problem}")
    else:
        print("\n✅ No major problems detected!")

    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS FOR V3 TRAINING")
    print("="*80)

    all_recs = set(v1_recs + v2_recs)
    if all_recs:
        for i, rec in enumerate(all_recs, 1):
            print(f"\n{i}. {rec}")
    else:
        print("\n✅ Current approach is optimal!")

    # Save detailed results
    results = {
        'originals': originals[:10],  # Sample
        'v1_outputs': v1_outputs[:10],
        'v2_outputs': v2_outputs[:10],
        'problems': list(all_problems),
        'recommendations': list(all_recs)
    }

    with open('deep_visual_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n📄 Detailed results saved to: deep_visual_analysis_results.json")

if __name__ == "__main__":
    main()
