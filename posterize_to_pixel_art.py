#!/usr/bin/env python3
"""
Post-process generated images to true pixel art with color quantization
"""

from PIL import Image
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans

def extract_palette_from_real_punk(img_path, n_colors=15):
    """Extract the exact color palette from a real Bespoke Punk"""
    img = Image.open(img_path)
    arr = np.array(img)

    # Get unique colors
    pixels = arr.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)

    print(f"   Real punk has {len(unique_colors)} unique colors")
    return unique_colors

def quantize_to_n_colors(img, n_colors=15):
    """Reduce image to n_colors using k-means clustering"""
    arr = np.array(img)
    original_shape = arr.shape

    # Reshape to list of pixels
    pixels = arr.reshape(-1, 3)

    # Use k-means to find n dominant colors
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # Replace each pixel with its cluster center
    quantized_pixels = kmeans.cluster_centers_[kmeans.labels_]

    # Round to integers
    quantized_pixels = np.round(quantized_pixels).astype(np.uint8)

    # Reshape back to image
    quantized_arr = quantized_pixels.reshape(original_shape)

    return Image.fromarray(quantized_arr)

def posterize_image(img, levels=4):
    """Apply posterization to reduce color depth"""
    # Posterize reduces bits per channel
    # levels=4 means 2^4 = 16 values per channel
    return img.convert('RGB').quantize(colors=16).convert('RGB')

print("🎨 COLOR QUANTIZATION PIPELINE")
print("=" * 80)

# Analyze a real Bespoke Punk to get target color count
print("\n📸 Analyzing real Bespoke Punk color palette:")
real_palette = extract_palette_from_real_punk("FORTRAINING6/bespokepunks/lad_001_carbon.png")

# Test different quantization approaches on generated images
MODELS = ["V1_Epoch2", "V2_Epoch3"]
TESTS = ["simple_green", "purple_sunglasses"]

output_dir = Path("quantized_validation")
output_dir.mkdir(exist_ok=True)

for model in MODELS:
    print(f"\n{'='*80}")
    print(f"🧪 Processing: {model}")
    print(f"{'='*80}")

    model_dir = output_dir / model
    model_dir.mkdir(exist_ok=True)

    for test in TESTS:
        # Load 512x512 generated image
        gen_path = Path(f"true_24x24_validation/{model}/{test}_512.png")
        if not gen_path.exists():
            continue

        print(f"\n  → {test}")
        img_512 = Image.open(gen_path)

        # Method 1: Quantize 512x512 to 15 colors, THEN downsample
        print(f"     Method 1: Quantize 512→15 colors, then downsample to 24x24")
        quantized_512 = quantize_to_n_colors(img_512, n_colors=15)
        quantized_24 = quantized_512.resize((24, 24), Image.NEAREST)

        # Check final color count
        arr = np.array(quantized_24)
        unique_colors_m1 = len(np.unique(arr.reshape(-1, 3), axis=0))

        quantized_512.save(model_dir / f"{test}_method1_512.png")
        quantized_24.save(model_dir / f"{test}_method1_24.png")
        print(f"        512x512: {model_dir / f'{test}_method1_512.png'}")
        print(f"         24x24: {model_dir / f'{test}_method1_24.png'} ({unique_colors_m1} colors)")

        # Method 2: Downsample first, THEN quantize 24x24
        print(f"     Method 2: Downsample to 24x24, then quantize to 15 colors")
        down_24 = img_512.resize((24, 24), Image.NEAREST)
        quantized_24_m2 = quantize_to_n_colors(down_24, n_colors=15)

        arr = np.array(quantized_24_m2)
        unique_colors_m2 = len(np.unique(arr.reshape(-1, 3), axis=0))

        quantized_24_m2.save(model_dir / f"{test}_method2_24.png")
        print(f"         24x24: {model_dir / f'{test}_method2_24.png'} ({unique_colors_m2} colors)")

        # Method 3: Aggressive posterization
        print(f"     Method 3: Posterize to 16 colors, downsample")
        posterized_512 = img_512.quantize(colors=15).convert('RGB')
        posterized_24 = posterized_512.resize((24, 24), Image.NEAREST)

        arr = np.array(posterized_24)
        unique_colors_m3 = len(np.unique(arr.reshape(-1, 3), axis=0))

        posterized_512.save(model_dir / f"{test}_method3_512.png")
        posterized_24.save(model_dir / f"{test}_method3_24.png")
        print(f"        512x512: {model_dir / f'{test}_method3_512.png'}")
        print(f"         24x24: {model_dir / f'{test}_method3_24.png'} ({unique_colors_m3} colors)")

print("\n" + "=" * 80)
print("✅ QUANTIZATION COMPLETE!")
print(f"📁 Results: {output_dir}/")
print("\nCompare the quantized versions to see which method produces")
print("the most authentic Bespoke Punk pixel art style")
print("=" * 80)
