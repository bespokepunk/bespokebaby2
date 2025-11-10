#!/usr/bin/env python3
"""
Debug Feature Extraction Issues
Analyze what SimpleFeatureExtractor is detecting vs what it should detect
"""

from PIL import Image
import numpy as np
from user_to_bespoke_punk_PRODUCTION import SimpleFeatureExtractor, ColorPaletteExtractor
import sys

def debug_image(image_path):
    """Debug feature extraction for a specific image"""
    print("="*80)
    print(f"DEBUGGING: {image_path}")
    print("="*80)
    print()

    # Load image
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    height, width = arr.shape[:2]

    print(f"Image size: {width}x{height}")
    print()

    # Show what regions are being sampled
    print("REGION SAMPLING:")
    print(f"  Hair region: Top 30% (0 to {int(height * 0.3)} pixels)")
    print(f"  Eye region: 30%-50% height, 30%-70% width")
    print(f"  Skin region: 30%-70% height, 25%-75% width")
    print()

    # Hair detection debug
    print("HAIR DETECTION:")
    hair_region = arr[:int(height * 0.3), :]
    pixels = hair_region.reshape(-1, 3)
    avg_color = pixels.mean(axis=0).astype(int)
    print(f"  Average RGB in hair region: {avg_color}")
    print(f"  Brightness: {avg_color.mean():.1f}")

    # Get all unique colors in hair region to see what's there
    unique_colors = np.unique(hair_region.reshape(-1, 3), axis=0)
    print(f"  Unique colors in hair region: {len(unique_colors)}")

    # Show dominant colors
    print(f"  Top 5 colors by pixel count:")
    color_counts = {}
    for pixel in pixels:
        color_tuple = tuple(pixel)
        color_counts[color_tuple] = color_counts.get(color_tuple, 0) + 1

    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (color, count) in enumerate(sorted_colors, 1):
        pct = (count / len(pixels)) * 100
        r, g, b = color
        print(f"    {i}. RGB({r:3d}, {g:3d}, {b:3d}) - {pct:.1f}% of pixels")

    print()

    # Eye detection debug
    print("EYE DETECTION:")
    eye_region = arr[int(height*0.3):int(height*0.5), int(width*0.3):int(width*0.7)]
    eye_pixels = eye_region.reshape(-1, 3)
    dark_pixels = eye_pixels[eye_pixels.mean(axis=1) < 100]

    print(f"  Total pixels in eye region: {len(eye_pixels)}")
    print(f"  Dark pixels (brightness < 100): {len(dark_pixels)}")

    if len(dark_pixels) > 0:
        avg_dark_color = dark_pixels.mean(axis=0).astype(int)
        print(f"  Average dark pixel RGB: {avg_dark_color}")
    else:
        print(f"  No dark pixels found!")
    print()

    # Skin detection debug
    print("SKIN DETECTION:")
    face_region = arr[int(height*0.3):int(height*0.7), int(width*0.25):int(width*0.75)]
    face_pixels = face_region.reshape(-1, 3)
    skin_pixels = face_pixels[(face_pixels[:, 0] > 80) & (face_pixels[:, 1] > 50)]

    print(f"  Total pixels in face region: {len(face_pixels)}")
    print(f"  Skin-toned pixels (R>80, G>50): {len(skin_pixels)}")

    if len(skin_pixels) > 0:
        avg_skin = skin_pixels.mean(axis=0).astype(int)
        brightness = avg_skin.mean()
        print(f"  Average skin RGB: {avg_skin}")
        print(f"  Brightness: {brightness:.1f}")
    print()

    # Run actual extractor
    print("ACTUAL EXTRACTION RESULTS:")
    extractor = SimpleFeatureExtractor(image_path)
    print(f"  Hair: {extractor.detect_hair_color()}")
    print(f"  Eyes: {extractor.detect_eye_color()}")
    print(f"  Skin: {extractor.detect_skin_tone()}")
    print()

    # Get dominant palette colors
    print("DOMINANT COLOR PALETTE (top 12 colors):")
    color_extractor = ColorPaletteExtractor(image_path)
    palette = color_extractor.get_palette(n_colors=12)
    for i, hex_color in enumerate(palette, 1):
        print(f"  {i:2d}. {hex_color}")
    print()

if __name__ == "__main__":
    # Test both images
    images = [
        "/Users/ilyssaevans/Desktop/Screenshot 2025-11-09 at 10.16.19 PM.png",
        "/Users/ilyssaevans/Desktop/Screenshot 2025-11-09 at 10.18.09 PM.png"
    ]

    for image_path in images:
        try:
            debug_image(image_path)
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
            import traceback
            traceback.print_exc()
            print()
