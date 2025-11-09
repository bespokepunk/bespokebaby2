#!/usr/bin/env python3
"""
Post-process 24x24 outputs to enhance pixel art quality.

Applies:
1. Color quantization (reduce to limited palette like original Bespoke Punks)
2. Edge sharpening and posterization
3. Optional dithering
"""

import os
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from sklearn.cluster import KMeans
import glob

# Directories
INPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_test_outputs"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_test_outputs_postprocessed"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def analyze_original_palette():
    """Analyze color palette used in original Bespoke Punks"""
    print("Analyzing original Bespoke Punks color palette...")

    # Sample a few original punks
    original_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks"
    sample_files = glob.glob(os.path.join(original_dir, "*.png"))[:20]

    all_colors = set()

    for img_path in sample_files:
        img = Image.open(img_path).convert('RGB')
        pixels = np.array(img).reshape(-1, 3)
        for pixel in pixels:
            all_colors.add(tuple(pixel))

    print(f"Found {len(all_colors)} unique colors in sample of 20 originals")
    print(f"Average colors per image: {len(all_colors) / 20:.1f}")

    return all_colors


def quantize_colors(img, num_colors=12):
    """
    Reduce image to limited color palette using k-means clustering.
    Original Bespoke Punks typically use 5-15 colors per character.
    """
    # Convert to numpy array
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    # Reshape to list of pixels
    pixels = img_array.reshape(-1, 3)

    # Use k-means to find dominant colors
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # Replace each pixel with nearest cluster center
    labels = kmeans.predict(pixels)
    quantized = kmeans.cluster_centers_[labels]

    # Reshape back to image
    quantized_img = quantized.reshape(h, w, 3).astype(np.uint8)

    return Image.fromarray(quantized_img)


def posterize_colors(img, bits=4):
    """
    Posterize to reduce color gradations.
    Lower bits = fewer colors, more pixel-art-like.
    bits=4 gives 16 levels per channel
    """
    from PIL import ImageOps
    # Use posterize which reduces bits per channel
    return ImageOps.posterize(img, bits)


def sharpen_edges(img, strength=2.0):
    """Apply edge sharpening to make pixels more distinct"""
    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(strength)


def process_image(input_path, num_colors=10, sharpen=True, posterize=True):
    """
    Full post-processing pipeline:
    1. Color quantization (reduce to limited palette)
    2. Edge sharpening (make pixels crisp)
    3. Posterization (reduce color gradations)
    """
    img = Image.open(input_path).convert('RGB')

    # Step 1: Quantize to limited palette
    img_quant = quantize_colors(img, num_colors=num_colors)

    # Step 2: Sharpen edges
    if sharpen:
        img_sharp = sharpen_edges(img_quant, strength=2.5)
    else:
        img_sharp = img_quant

    # Step 3: Posterize to reduce gradations
    if posterize:
        img_post = posterize_colors(img_sharp, bits=4)
    else:
        img_post = img_sharp

    return img_post


def create_comparison_grid(original_path, processed_img, save_path):
    """Create side-by-side comparison: original vs processed (upscaled for visibility)"""
    original = Image.open(original_path).convert('RGB')

    # Upscale to 240x240 for visibility (10x)
    scale = 10
    orig_large = original.resize((24*scale, 24*scale), Image.NEAREST)
    proc_large = processed_img.resize((24*scale, 24*scale), Image.NEAREST)

    # Create side-by-side
    comparison = Image.new('RGB', (24*scale*2 + 20, 24*scale), (255, 255, 255))
    comparison.paste(orig_large, (0, 0))
    comparison.paste(proc_large, (24*scale + 20, 0))

    comparison.save(save_path)


def main():
    # Analyze original palette first
    # analyze_original_palette()

    print("\n" + "="*60)
    print("POST-PROCESSING 24x24 OUTPUTS")
    print("="*60 + "\n")

    # Find all 24x24 NEAREST neighbor outputs
    pattern = os.path.join(INPUT_DIR, "*_24x24_NEAREST.png")
    files = sorted(glob.glob(pattern))

    print(f"Found {len(files)} files to process\n")

    # Test different color palette sizes
    color_options = [8, 10, 12, 16]

    for input_path in files:
        basename = os.path.basename(input_path)
        print(f"Processing: {basename}")

        # Try different quantization levels
        for num_colors in color_options:
            # Process image
            processed = process_image(
                input_path,
                num_colors=num_colors,
                sharpen=True,
                posterize=True
            )

            # Save processed version
            output_name = basename.replace("_NEAREST.png", f"_PROCESSED_{num_colors}colors.png")
            output_path = os.path.join(OUTPUT_DIR, output_name)
            processed.save(output_path)

            # Create comparison grid
            comparison_name = basename.replace("_NEAREST.png", f"_COMPARISON_{num_colors}colors.png")
            comparison_path = os.path.join(OUTPUT_DIR, comparison_name)
            create_comparison_grid(input_path, processed, comparison_path)

            print(f"  ✓ {num_colors} colors: {output_name}")

        print()

    print("="*60)
    print(f"DONE! Processed images saved to:")
    print(f"{OUTPUT_DIR}")
    print("="*60)

    # Print summary
    print("\nSummary:")
    print(f"- Tested {len(color_options)} color palette sizes: {color_options}")
    print(f"- Generated {len(files) * len(color_options)} processed images")
    print(f"- Generated {len(files) * len(color_options)} comparison images")
    print("\nReview the comparison images to see which color count looks most like original Bespoke Punks!")


if __name__ == "__main__":
    main()
