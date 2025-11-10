#!/usr/bin/env python3
"""
Measure Pixel Art Style Quality - Quantitative Metrics

Measures whether generated image matches pixel art aesthetic vs photorealistic rendering.

Metrics:
- Edge sharpness (pixel art has sharp, clean edges)
- Photorealism detection (smooth gradients = bad)
- Color palette size (pixel art has limited palette)
- Anti-aliasing detection (should be minimal)
- Dithering quality (intentional patterns vs noise)

Usage:
    python scripts/measure_pixel_art_quality.py /path/to/image.png

Or import as module:
    from measure_pixel_art_quality import measure_pixel_art_quality
    metrics = measure_pixel_art_quality(image_path)
"""

import sys
import json
import numpy as np
from PIL import Image
from collections import Counter
from typing import Dict, Tuple

def measure_edge_sharpness(image: Image.Image) -> Dict:
    """
    Measure edge sharpness using gradient analysis

    Pixel art should have very sharp edges (high gradient values).
    Photorealistic images have smooth transitions (low gradients).
    """
    img_array = np.array(image.convert('L'))  # Convert to grayscale

    # Calculate gradients (Sobel-like)
    grad_x = np.abs(np.diff(img_array, axis=1))
    grad_y = np.abs(np.diff(img_array, axis=0))

    # Combine gradients
    grad_magnitude = np.sqrt(grad_x[:-1, :] ** 2 + grad_y[:, :-1] ** 2)

    # Calculate statistics
    mean_gradient = np.mean(grad_magnitude)
    max_gradient = np.max(grad_magnitude)
    high_gradient_ratio = np.sum(grad_magnitude > 50) / grad_magnitude.size

    # Score: Higher gradient = sharper edges = better pixel art
    # Pixel art typically has mean gradient > 20, high_gradient_ratio > 0.1
    sharpness_score = 0

    if mean_gradient > 30:
        sharpness_score += 40
    elif mean_gradient > 20:
        sharpness_score += 25
    elif mean_gradient > 10:
        sharpness_score += 10

    if high_gradient_ratio > 0.15:
        sharpness_score += 30
    elif high_gradient_ratio > 0.10:
        sharpness_score += 20
    elif high_gradient_ratio > 0.05:
        sharpness_score += 10

    if max_gradient > 200:
        sharpness_score += 30
    elif max_gradient > 150:
        sharpness_score += 20

    return {
        "mean_gradient": round(float(mean_gradient), 2),
        "max_gradient": round(float(max_gradient), 2),
        "high_gradient_ratio": round(float(high_gradient_ratio), 4),
        "sharpness_score": min(sharpness_score, 100),
        "is_sharp": bool(mean_gradient > 20 and high_gradient_ratio > 0.1)
    }

def detect_photorealism(image: Image.Image) -> Dict:
    """
    Detect photorealistic rendering vs pixel art

    Photorealism indicators:
    - Smooth gradients (low color variance in local regions)
    - Many similar colors (anti-aliasing)
    - High color count relative to image size
    """
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    total_pixels = height * width

    # Count unique colors
    pixels = [tuple(p) for p in img_array.reshape(-1, 3)]
    unique_colors = len(set(pixels))

    # Color-to-pixel ratio
    # Pixel art: 20-100 colors for 576 pixels (24x24) = ratio ~0.05-0.17
    # Photorealistic: 400+ colors for 576 pixels = ratio ~0.7+
    color_ratio = unique_colors / total_pixels

    # Calculate local color variance
    # Photorealistic images have smooth transitions (low local variance)
    # Pixel art has abrupt changes (high local variance)

    # Sample 5x5 blocks and calculate variance
    block_size = min(5, height // 4, width // 4)
    if block_size < 2:
        block_size = 2

    variances = []
    for i in range(0, height - block_size, block_size):
        for j in range(0, width - block_size, block_size):
            block = img_array[i:i+block_size, j:j+block_size]
            block_variance = np.var(block)
            variances.append(block_variance)

    mean_local_variance = np.mean(variances) if variances else 0

    # Photorealism score (lower is better for pixel art)
    # High color_ratio + low variance = photorealistic
    photorealism_score = 0

    if color_ratio > 0.5:
        photorealism_score += 40  # Very high color count
    elif color_ratio > 0.3:
        photorealism_score += 20
    elif color_ratio < 0.2:
        photorealism_score -= 20  # Good for pixel art

    if mean_local_variance < 1000:
        photorealism_score += 30  # Smooth (bad for pixel art)
    elif mean_local_variance > 3000:
        photorealism_score -= 20  # Abrupt changes (good for pixel art)

    # Pixel art purity score (inverse of photorealism)
    pixel_art_purity = 100 - max(0, min(photorealism_score + 50, 100))

    is_photorealistic = color_ratio > 0.4 and mean_local_variance < 1500

    return {
        "unique_colors": int(unique_colors),
        "total_pixels": int(total_pixels),
        "color_to_pixel_ratio": round(color_ratio, 4),
        "mean_local_variance": round(float(mean_local_variance), 2),
        "photorealism_score": int(max(0, min(photorealism_score + 50, 100))),
        "pixel_art_purity": round(pixel_art_purity, 2),
        "is_photorealistic": bool(is_photorealistic)
    }

def measure_color_palette(image: Image.Image) -> Dict:
    """
    Analyze color palette characteristics

    Pixel art typically has:
    - Limited palette (20-100 colors)
    - Clear dominant colors
    - Distinct color clusters
    """
    img_array = np.array(image)
    pixels = [tuple(p) for p in img_array.reshape(-1, 3)]

    # Count colors
    color_counts = Counter(pixels)
    unique_colors = len(color_counts)
    total_pixels = len(pixels)

    # Get dominant colors
    dominant_colors = color_counts.most_common(20)
    top_5_count = sum(count for _, count in dominant_colors[:5])
    top_10_count = sum(count for _, count in dominant_colors[:10])
    top_20_count = sum(count for _, count in dominant_colors[:20])

    top_5_ratio = top_5_count / total_pixels
    top_10_ratio = top_10_count / total_pixels
    top_20_ratio = top_20_count / total_pixels

    # Palette quality score
    palette_score = 0

    # Ideal pixel art: 20-60 colors
    if 20 <= unique_colors <= 60:
        palette_score += 40
    elif 15 <= unique_colors <= 100:
        palette_score += 25
    elif unique_colors < 15:
        palette_score += 10  # Too few (might be broken)
    else:
        palette_score -= 20  # Too many

    # Top colors should dominate
    if top_10_ratio > 0.7:
        palette_score += 30
    elif top_10_ratio > 0.5:
        palette_score += 20

    if top_20_ratio > 0.85:
        palette_score += 30
    elif top_20_ratio > 0.7:
        palette_score += 15

    return {
        "unique_colors": int(unique_colors),
        "total_pixels": int(total_pixels),
        "top_5_coverage": round(top_5_ratio, 4),
        "top_10_coverage": round(top_10_ratio, 4),
        "top_20_coverage": round(top_20_ratio, 4),
        "palette_quality_score": int(max(0, min(palette_score, 100))),
        "is_limited_palette": bool(20 <= unique_colors <= 100 and top_10_ratio > 0.5)
    }

def detect_dithering(image: Image.Image) -> Dict:
    """
    Detect dithering patterns

    Intentional dithering (good): Checkerboard or ordered patterns
    Random noise (bad): No pattern, looks messy
    """
    img_array = np.array(image)

    # Simple dithering detection:
    # Check for alternating pixel patterns in small regions

    # This is a simplified detection - full dithering analysis would be complex
    # For now, we'll estimate based on local color alternation

    height, width = img_array.shape[:2]

    # Sample horizontal alternations
    h_alternations = 0
    for i in range(0, height, 2):
        for j in range(0, width - 1, 2):
            if not np.array_equal(img_array[i, j], img_array[i, j+1]):
                h_alternations += 1

    h_alt_ratio = h_alternations / (height * width / 2) if height * width > 0 else 0

    # Rough heuristic: some alternation is normal, extreme alternation suggests dithering
    dithering_present = h_alt_ratio > 0.3

    dithering_score = 50  # Neutral baseline
    if 0.1 < h_alt_ratio < 0.4:
        dithering_score += 20  # Moderate dithering (intentional, good)
    elif h_alt_ratio > 0.6:
        dithering_score -= 20  # Excessive noise (bad)

    return {
        "horizontal_alternation_ratio": round(h_alt_ratio, 4),
        "dithering_detected": bool(dithering_present),
        "dithering_quality_score": int(max(0, min(dithering_score, 100)))
    }

def measure_pixel_art_quality(image_path: str) -> Dict:
    """
    Main function: Measure all pixel art style quality metrics

    Args:
        image_path: Path to generated image

    Returns:
        Complete style quality metrics
    """
    # Load image
    image = Image.open(image_path)

    # Measure edge sharpness
    edge_metrics = measure_edge_sharpness(image)

    # Detect photorealism
    photorealism_metrics = detect_photorealism(image)

    # Measure color palette
    palette_metrics = measure_color_palette(image)

    # Detect dithering
    dithering_metrics = detect_dithering(image)

    # Overall style quality score
    # Weighted combination of metrics
    overall_score = (
        edge_metrics["sharpness_score"] * 0.25 +
        photorealism_metrics["pixel_art_purity"] * 0.35 +
        palette_metrics["palette_quality_score"] * 0.25 +
        dithering_metrics["dithering_quality_score"] * 0.15
    )

    # Is it good pixel art?
    is_good_pixel_art = bool(
        edge_metrics["is_sharp"] and
        not photorealism_metrics["is_photorealistic"] and
        palette_metrics["is_limited_palette"]
    )

    return {
        "overall_style_quality": round(overall_score, 2),
        "is_pixel_art": bool(is_good_pixel_art),
        "edge_sharpness": edge_metrics,
        "photorealism_detection": photorealism_metrics,
        "color_palette": palette_metrics,
        "dithering": dithering_metrics
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python measure_pixel_art_quality.py <image_path>")
        print("\nExample:")
        print("  python measure_pixel_art_quality.py test_24.png")
        return

    image_path = sys.argv[1]

    print(f"\n🎨 Measuring pixel art style quality: {image_path}\n")

    metrics = measure_pixel_art_quality(image_path)

    # Pretty print results
    print("=" * 80)
    print(f"OVERALL STYLE QUALITY: {metrics['overall_style_quality']:.2f}/100")
    print(f"IS PIXEL ART: {'✅ YES' if metrics['is_pixel_art'] else '❌ NO'}")
    print("=" * 80)

    print("\n✂️ Edge Sharpness:")
    edge = metrics["edge_sharpness"]
    print(f"  Mean gradient: {edge['mean_gradient']:.2f}")
    print(f"  Max gradient: {edge['max_gradient']:.2f}")
    print(f"  High gradient ratio: {edge['high_gradient_ratio']:.4f}")
    print(f"  Sharpness score: {edge['sharpness_score']}/100")
    print(f"  Sharp edges: {'✅ YES' if edge['is_sharp'] else '❌ NO'}")

    print("\n📸 Photorealism Detection:")
    photo = metrics["photorealism_detection"]
    print(f"  Unique colors: {photo['unique_colors']}")
    print(f"  Color/pixel ratio: {photo['color_to_pixel_ratio']:.4f}")
    print(f"  Local variance: {photo['mean_local_variance']:.2f}")
    print(f"  Photorealism score: {photo['photorealism_score']}/100")
    print(f"  Pixel art purity: {photo['pixel_art_purity']:.2f}/100")
    print(f"  Is photorealistic: {'❌ YES (BAD)' if photo['is_photorealistic'] else '✅ NO (GOOD)'}")

    print("\n🎨 Color Palette:")
    palette = metrics["color_palette"]
    print(f"  Unique colors: {palette['unique_colors']}")
    print(f"  Top 5 coverage: {palette['top_5_coverage']:.2%}")
    print(f"  Top 10 coverage: {palette['top_10_coverage']:.2%}")
    print(f"  Top 20 coverage: {palette['top_20_coverage']:.2%}")
    print(f"  Palette quality: {palette['palette_quality_score']}/100")
    print(f"  Limited palette: {'✅ YES' if palette['is_limited_palette'] else '❌ NO'}")

    print("\n🔲 Dithering:")
    dither = metrics["dithering"]
    print(f"  H-alternation ratio: {dither['horizontal_alternation_ratio']:.4f}")
    print(f"  Dithering detected: {'YES' if dither['dithering_detected'] else 'NO'}")
    print(f"  Dithering quality: {dither['dithering_quality_score']}/100")

    print("\n" + "=" * 80)
    print(f"Overall: {metrics['overall_style_quality']:.2f}/100")
    print(f"Verdict: {'✅ GOOD PIXEL ART' if metrics['is_pixel_art'] else '❌ NOT PIXEL ART'}")
    print("=" * 80)

    # Save JSON
    json_path = image_path.replace('.png', '_style_metrics.json')
    with open(json_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n✅ Metrics saved to: {json_path}")

if __name__ == "__main__":
    main()
