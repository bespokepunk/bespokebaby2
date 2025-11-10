#!/usr/bin/env python3
"""
Measure Color Accuracy - Quantitative Metrics for LoRA Testing

Replaces subjective scoring with pixel-level color accuracy measurements.

Measures:
- Background color accuracy (% pixels matching expected hex)
- Hair color accuracy (dominant color vs expected)
- Two-tone hair detection (multiple dominant colors = bad)
- Accessory presence/accuracy (crown, earrings, necklace)
- Color purity (solid vs multi-toned regions)

Usage:
    python scripts/measure_color_accuracy.py /path/to/image.png --prompt-data '{"background": "#00FF00", "hair": "#FF1493"}'

Or import as module:
    from measure_color_accuracy import measure_color_accuracy
    metrics = measure_color_accuracy(image, expected_colors)
"""

import sys
import json
from PIL import Image
import numpy as np
from collections import Counter
from typing import Dict, Tuple, List

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex string"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two RGB colors"""
    return np.sqrt(sum((int(c1) - int(c2)) ** 2 for c1, c2 in zip(color1, color2)))

def colors_match(color1: Tuple[int, int, int], color2: Tuple[int, int, int], tolerance: int = 30) -> bool:
    """Check if two colors match within tolerance"""
    return color_distance(color1, color2) <= tolerance

def get_dominant_colors(pixels: List[Tuple[int, int, int]], n: int = 5) -> List[Tuple[Tuple[int, int, int], int]]:
    """Get top N dominant colors and their counts"""
    color_counts = Counter(pixels)
    return color_counts.most_common(n)

def measure_background_accuracy(image: Image.Image, expected_hex: str, tolerance: int = 30) -> Dict:
    """
    Measure background color accuracy

    Strategy:
    1. Sample edge pixels (likely background in 24x24 portraits)
    2. Find dominant color in edge pixels
    3. Count % of edge pixels matching expected color
    """
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # Sample edge pixels (outer 20% border)
    border_width = max(1, int(width * 0.2))
    border_height = max(1, int(height * 0.2))

    edge_pixels = []

    # Top and bottom edges
    edge_pixels.extend(img_array[0:border_height, :].reshape(-1, 3))
    edge_pixels.extend(img_array[-border_height:, :].reshape(-1, 3))

    # Left and right edges (excluding corners already counted)
    edge_pixels.extend(img_array[border_height:-border_height, 0:border_width].reshape(-1, 3))
    edge_pixels.extend(img_array[border_height:-border_height, -border_width:].reshape(-1, 3))

    # Convert to list of tuples
    edge_pixels = [tuple(p) for p in edge_pixels]

    # Expected background color
    expected_rgb = hex_to_rgb(expected_hex)

    # Count matching pixels
    matching_count = sum(1 for p in edge_pixels if colors_match(p, expected_rgb, tolerance))
    total_count = len(edge_pixels)

    accuracy = (matching_count / total_count * 100) if total_count > 0 else 0

    # Find actual dominant background color
    dominant_colors = get_dominant_colors(edge_pixels, n=3)
    actual_dominant = dominant_colors[0][0] if dominant_colors else (0, 0, 0)
    actual_dominant_hex = rgb_to_hex(actual_dominant)

    return {
        "expected_color": expected_hex,
        "actual_dominant_color": actual_dominant_hex,
        "accuracy_percent": round(accuracy, 2),
        "matching_pixels": matching_count,
        "total_pixels": total_count,
        "is_correct": accuracy >= 70  # Threshold for "correct"
    }

def measure_hair_accuracy(image: Image.Image, expected_hex: str, tolerance: int = 40) -> Dict:
    """
    Measure hair color accuracy and detect two-toning

    Strategy:
    1. Sample top 1/3 of image (likely hair region)
    2. Exclude very light colors (likely face/skin)
    3. Find dominant colors in hair region
    4. Check for two-toning (multiple strong colors)
    """
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # Sample top 1/3 (hair region)
    hair_height = int(height * 0.33)
    hair_region = img_array[0:hair_height, :]

    # Convert to list of tuples
    hair_pixels = [tuple(p) for p in hair_region.reshape(-1, 3)]

    # Filter out very light colors (skin tones, white, beige)
    # Keep only colors with at least one channel < 200
    dark_hair_pixels = [p for p in hair_pixels if min(p) < 200]

    if len(dark_hair_pixels) == 0:
        return {
            "expected_color": expected_hex,
            "actual_dominant_color": "#FFFFFF",
            "accuracy_percent": 0,
            "is_two_toned": False,
            "two_tone_confidence": 0,
            "dominant_colors": []
        }

    # Expected hair color
    expected_rgb = hex_to_rgb(expected_hex)

    # Count matching pixels
    matching_count = sum(1 for p in dark_hair_pixels if colors_match(p, expected_rgb, tolerance))
    accuracy = (matching_count / len(dark_hair_pixels) * 100)

    # Find dominant colors
    dominant_colors = get_dominant_colors(dark_hair_pixels, n=5)

    # Detect two-toning
    # If 2nd most common color has > 20% the frequency of 1st, it's two-toned
    is_two_toned = False
    two_tone_confidence = 0

    if len(dominant_colors) >= 2:
        first_count = dominant_colors[0][1]
        second_count = dominant_colors[1][1]

        # Check if colors are actually different (not just noise)
        first_color = dominant_colors[0][0]
        second_color = dominant_colors[1][0]

        if color_distance(first_color, second_color) > 40:  # Significantly different
            ratio = second_count / first_count
            if ratio > 0.2:  # Second color is > 20% as common as first
                is_two_toned = True
                two_tone_confidence = min(ratio * 100, 100)

    # Format dominant colors for output
    dominant_colors_formatted = [
        {
            "color": rgb_to_hex(color),
            "count": count,
            "percent": round(count / len(dark_hair_pixels) * 100, 2)
        }
        for color, count in dominant_colors[:3]
    ]

    actual_dominant_hex = rgb_to_hex(dominant_colors[0][0]) if dominant_colors else "#000000"

    return {
        "expected_color": expected_hex,
        "actual_dominant_color": actual_dominant_hex,
        "accuracy_percent": round(accuracy, 2),
        "is_two_toned": is_two_toned,
        "two_tone_confidence": round(two_tone_confidence, 2),
        "dominant_colors": dominant_colors_formatted
    }

def measure_accessory_presence(image: Image.Image, expected_colors: Dict[str, str], tolerance: int = 40) -> Dict:
    """
    Detect presence of accessories by color

    Strategy:
    - Crown: Yellow/gold in top 1/4
    - Necklace: Green in middle-bottom area
    - Earrings: Gold on sides of middle region
    """
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    results = {}

    # Crown detection (yellow/gold in top 1/4)
    if "crown" in expected_colors:
        crown_expected = hex_to_rgb(expected_colors["crown"])
        crown_region = img_array[0:int(height*0.25), :]
        crown_pixels = [tuple(p) for p in crown_region.reshape(-1, 3)]

        crown_matches = sum(1 for p in crown_pixels if colors_match(p, crown_expected, tolerance))
        crown_percent = (crown_matches / len(crown_pixels) * 100)

        results["crown"] = {
            "expected_color": expected_colors["crown"],
            "detection_confidence": round(crown_percent, 2),
            "is_present": crown_percent > 2  # At least 2% of region
        }

    # Necklace detection (green in middle-bottom)
    if "necklace" in expected_colors:
        necklace_expected = hex_to_rgb(expected_colors["necklace"])
        necklace_region = img_array[int(height*0.4):int(height*0.8), :]
        necklace_pixels = [tuple(p) for p in necklace_region.reshape(-1, 3)]

        necklace_matches = sum(1 for p in necklace_pixels if colors_match(p, necklace_expected, tolerance))
        necklace_percent = (necklace_matches / len(necklace_pixels) * 100)

        results["necklace"] = {
            "expected_color": expected_colors["necklace"],
            "detection_confidence": round(necklace_percent, 2),
            "is_present": necklace_percent > 2
        }

    return results

def measure_color_purity(image: Image.Image) -> Dict:
    """
    Measure color purity (solid vs noisy/multi-toned)

    Pixel art should have limited palette and solid color regions.
    """
    img_array = np.array(image)
    pixels = [tuple(p) for p in img_array.reshape(-1, 3)]

    # Count unique colors
    unique_colors = len(set(pixels))
    total_pixels = len(pixels)

    # Get dominant colors
    dominant_colors = get_dominant_colors(pixels, n=10)

    # Calculate entropy (color variety)
    # Lower entropy = more solid colors
    top_10_count = sum(count for _, count in dominant_colors[:10])
    top_10_ratio = top_10_count / total_pixels

    # Purity score: Higher is better (more solid, less noisy)
    # Perfect pixel art: 20-50 colors, top 10 colors cover 80%+
    purity_score = 0

    if unique_colors <= 50:
        purity_score += 30  # Good palette size
    elif unique_colors <= 100:
        purity_score += 15

    if top_10_ratio >= 0.8:
        purity_score += 40  # Top 10 colors dominate
    elif top_10_ratio >= 0.6:
        purity_score += 20

    # Bonus for very limited palette (true pixel art)
    if unique_colors <= 30:
        purity_score += 30

    return {
        "unique_colors": unique_colors,
        "color_purity_score": min(purity_score, 100),
        "top_10_coverage_percent": round(top_10_ratio * 100, 2),
        "is_clean_pixel_art": unique_colors <= 50 and top_10_ratio >= 0.7
    }

def measure_color_accuracy(image_path: str, expected_colors: Dict[str, str]) -> Dict:
    """
    Main function: Measure all color accuracy metrics

    Args:
        image_path: Path to generated image
        expected_colors: Dict with keys like "background", "hair", "crown", "necklace"

    Returns:
        Complete color accuracy metrics
    """
    # Load image
    image = Image.open(image_path)

    # Measure background
    background_metrics = measure_background_accuracy(
        image,
        expected_colors.get("background", "#00FF00"),
        tolerance=30
    )

    # Measure hair
    hair_metrics = measure_hair_accuracy(
        image,
        expected_colors.get("hair", "#FF1493"),
        tolerance=40
    )

    # Measure accessories
    accessory_metrics = measure_accessory_presence(
        image,
        {k: v for k, v in expected_colors.items() if k in ["crown", "necklace", "earrings"]},
        tolerance=40
    )

    # Measure color purity
    purity_metrics = measure_color_purity(image)

    # Calculate overall color accuracy score (0-100)
    overall_score = (
        background_metrics["accuracy_percent"] * 0.4 +  # 40% weight
        hair_metrics["accuracy_percent"] * 0.4 +         # 40% weight
        purity_metrics["color_purity_score"] * 0.2       # 20% weight
    )

    return {
        "overall_color_accuracy": round(overall_score, 2),
        "background": background_metrics,
        "hair": hair_metrics,
        "accessories": accessory_metrics,
        "color_purity": purity_metrics
    }

# Default test prompt colors
DEFAULT_EXPECTED_COLORS = {
    "background": "#00FF00",  # green
    "hair": "#FF1493",        # deep pink
    "crown": "#FFD700",       # gold
    "necklace": "#00FF00",    # green
    "earrings": "#FFD700",    # gold
    "lips": "#FF69B4"         # pink
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python measure_color_accuracy.py <image_path> [--expected-colors JSON]")
        print("\nExample:")
        print('  python measure_color_accuracy.py test_512.png')
        print('  python measure_color_accuracy.py test_512.png --expected-colors \'{"background": "#00FF00"}\'')
        return

    image_path = sys.argv[1]

    # Parse expected colors
    expected_colors = DEFAULT_EXPECTED_COLORS.copy()
    if len(sys.argv) > 2 and sys.argv[2] == "--expected-colors":
        custom_colors = json.loads(sys.argv[3])
        expected_colors.update(custom_colors)

    # Measure
    print(f"\n📊 Measuring color accuracy: {image_path}")
    print(f"Expected colors: {json.dumps(expected_colors, indent=2)}\n")

    metrics = measure_color_accuracy(image_path, expected_colors)

    # Pretty print results
    print("=" * 80)
    print(f"OVERALL COLOR ACCURACY: {metrics['overall_color_accuracy']:.2f}%")
    print("=" * 80)

    print("\n🎨 Background:")
    bg = metrics["background"]
    print(f"  Expected: {bg['expected_color']}")
    print(f"  Actual:   {bg['actual_dominant_color']}")
    print(f"  Accuracy: {bg['accuracy_percent']:.2f}% ({bg['matching_pixels']}/{bg['total_pixels']} pixels)")
    print(f"  Correct:  {'✅ YES' if bg['is_correct'] else '❌ NO'}")

    print("\n💇 Hair:")
    hair = metrics["hair"]
    print(f"  Expected: {hair['expected_color']}")
    print(f"  Actual:   {hair['actual_dominant_color']}")
    print(f"  Accuracy: {hair['accuracy_percent']:.2f}%")
    print(f"  Two-toned: {'⚠️ YES' if hair['is_two_toned'] else '✅ NO'} (confidence: {hair['two_tone_confidence']:.1f}%)")
    if hair.get("dominant_colors"):
        print(f"  Dominant colors:")
        for dc in hair["dominant_colors"]:
            print(f"    - {dc['color']}: {dc['percent']:.1f}%")

    print("\n👑 Accessories:")
    for accessory, data in metrics["accessories"].items():
        print(f"  {accessory.capitalize()}:")
        print(f"    Expected: {data['expected_color']}")
        print(f"    Confidence: {data['detection_confidence']:.2f}%")
        print(f"    Present: {'✅ YES' if data['is_present'] else '❌ NO'}")

    print("\n🎨 Color Purity:")
    purity = metrics["color_purity"]
    print(f"  Unique colors: {purity['unique_colors']}")
    print(f"  Top 10 coverage: {purity['top_10_coverage_percent']:.1f}%")
    print(f"  Purity score: {purity['color_purity_score']:.1f}/100")
    print(f"  Clean pixel art: {'✅ YES' if purity['is_clean_pixel_art'] else '❌ NO'}")

    print("\n" + "=" * 80)
    print(f"Overall: {metrics['overall_color_accuracy']:.2f}/100")
    print("=" * 80)

    # Also save JSON
    json_path = image_path.replace('.png', '_color_metrics.json')
    with open(json_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n✅ Metrics saved to: {json_path}")

if __name__ == "__main__":
    main()
