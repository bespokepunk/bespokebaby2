#!/usr/bin/env python3
"""
Analyze punk NFT images and extract visual characteristics
"""
import os
from PIL import Image
import numpy as np
from collections import Counter

def get_dominant_colors(image_path, n=5):
    """Extract dominant colors from image"""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).reshape(-1, 3)

    # Filter out background (first pixel is usually background)
    bg_color = pixels[0]
    pixels = pixels[~np.all(pixels == bg_color, axis=1)]

    # Get unique colors and their counts
    unique, counts = np.unique(pixels, axis=0, return_counts=True)

    # Sort by frequency
    sorted_indices = np.argsort(-counts)
    top_colors = unique[sorted_indices[:n]]

    return top_colors

def describe_color(rgb):
    """Convert RGB to color description"""
    r, g, b = rgb

    # Color mapping logic
    if r > 200 and g > 200 and b > 200:
        return "white/light"
    elif r < 50 and g < 50 and b < 50:
        return "black/dark"
    elif r > 150 and g < 100 and b < 100:
        return "red"
    elif r > 200 and g > 150 and b < 100:
        return "orange"
    elif r > 200 and g > 200 and b < 100:
        return "yellow/blonde"
    elif r < 100 and g > 150 and b < 100:
        return "green"
    elif r < 100 and g < 100 and b > 150:
        return "blue"
    elif r > 150 and g < 100 and b > 150:
        return "purple/pink"
    elif r > 100 and g > 50 and b < 50:
        return "brown"
    elif r > 150 and g > 100 and b > 100:
        return "pink/light"
    elif r > 100 and g > 100 and b > 100:
        return "gray/silver"
    else:
        return "mixed"

def analyze_punk(image_path):
    """Analyze a single punk image"""
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)

    # Get background color (first pixel)
    bg_color = pixels[0, 0]

    # Get hair region (top portion, excluding background)
    hair_region = pixels[0:12, :]  # Top half for hair
    hair_pixels = hair_region.reshape(-1, 3)
    hair_pixels = hair_pixels[~np.all(hair_pixels == bg_color, axis=1)]

    if len(hair_pixels) > 0:
        unique_hair, counts_hair = np.unique(hair_pixels, axis=0, return_counts=True)
        dominant_hair = unique_hair[np.argmax(counts_hair)]
        hair_color = describe_color(dominant_hair)
    else:
        hair_color = "unknown"

    # Get skin tone (middle region)
    face_region = pixels[8:16, 8:16]
    face_pixels = face_region.reshape(-1, 3)
    face_pixels = face_pixels[~np.all(face_pixels == bg_color, axis=1)]

    if len(face_pixels) > 0:
        unique_face, counts_face = np.unique(face_pixels, axis=0, return_counts=True)
        # Get most common non-black color
        for color, count in zip(unique_face[np.argsort(-counts_face)], sorted(counts_face, reverse=True)):
            if not (color[0] < 50 and color[1] < 50 and color[2] < 50):
                skin_tone = describe_color(color)
                break
        else:
            skin_tone = "unknown"
    else:
        skin_tone = "unknown"

    # Check for accessories (look for unusual colors)
    all_pixels = pixels.reshape(-1, 3)
    unique_all, counts_all = np.unique(all_pixels, axis=0, return_counts=True)

    accessories = []
    for color, count in zip(unique_all, counts_all):
        if count > 10 and count < 100:  # Small but significant regions
            desc = describe_color(color)
            if desc not in ["black/dark", skin_tone, hair_color]:
                accessories.append(desc)

    return {
        "hair_color": hair_color,
        "skin_tone": skin_tone,
        "accessories": list(set(accessories[:3])),
        "dominant_colors": [describe_color(c) for c in get_dominant_colors(image_path, 5)]
    }

if __name__ == "__main__":
    punk_dir = "/Users/ilyssaevans/Documents/0NFTS/FORTRAINING6/all/"

    # Analyze all punks
    results = {}
    for filename in sorted(os.listdir(punk_dir)):
        if filename.endswith('.png'):
            punk_name = filename.replace('.png', '')
            try:
                analysis = analyze_punk(os.path.join(punk_dir, filename))
                results[punk_name] = analysis
                print(f"{punk_name}: hair={analysis['hair_color']}, skin={analysis['skin_tone']}")
            except Exception as e:
                print(f"Error analyzing {punk_name}: {e}")

    # Save results
    import json
    with open('/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/punk_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nAnalyzed {len(results)} punks")
