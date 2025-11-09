#!/usr/bin/env python3
"""
TEST: Better post-processing on existing outputs
Can we get closer to original Bespoke Punks without retraining?
"""

from PIL import Image, ImageFilter
import numpy as np
from pathlib import Path

def quantize_better(img, n_colors=40):
    """Improved quantization that preserves more color detail"""
    # Use PIL's built-in quantization with more colors
    return img.quantize(colors=n_colors, method=2, dither=0).convert('RGB')

def sharpen_image(img):
    """Apply sharpening to reduce SDXL's anti-aliasing"""
    # Apply unsharp mask
    sharpened = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    return sharpened

def posterize_smart(img, bits=6):
    """Smart posterization that creates hard edges"""
    # Posterize to reduce color smoothness
    return img.convert('RGB').quantize(colors=256, method=2, kmeans=bits).convert('RGB')

def resize_pixelart(img, target_size):
    """Resize using nearest neighbor (no blur)"""
    return img.resize(target_size, Image.Resampling.NEAREST)

def process_image_better(input_path, output_dir, n_colors=40):
    """Apply improved post-processing pipeline"""
    img = Image.open(input_path).convert('RGB')

    # Step 1: Sharpen to fight anti-aliasing
    img = sharpen_image(img)

    # Step 2: Quantize to MORE colors (40 instead of 15)
    img = quantize_better(img, n_colors=n_colors)

    # Step 3: Smart posterization for hard edges
    img = posterize_smart(img, bits=6)

    # Step 4: Resize to 24x24 with nearest neighbor
    img_24 = resize_pixelart(img, (24, 24))

    # Save both versions
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(input_path).stem
    img.save(output_dir / f"{filename}_improved_512.png")
    img_24.save(output_dir / f"{filename}_improved_24.png")

    return img, img_24

def main():
    print("🧪 TESTING: Better Post-Processing")
    print("="*80)

    # Test on some existing outputs
    test_images = [
        "comprehensive_evaluation/V1_Epoch2/simple_solid_bg/default_raw_512.png",
        "comprehensive_evaluation/V2_Epoch2/simple_solid_bg/default_raw_512.png",
        "comprehensive_evaluation/V1_Epoch2/checkered_pattern/default_raw_512.png",
        "comprehensive_evaluation/V2_Epoch2/checkered_pattern/default_raw_512.png",
        "comprehensive_evaluation/V1_Epoch2/gradient_bg/default_raw_512.png",
        "comprehensive_evaluation/V2_Epoch2/gradient_bg/default_raw_512.png",
    ]

    output_dir = Path("test_improved_postprocessing")
    output_dir.mkdir(exist_ok=True)

    print("\nProcessing images with improved pipeline:")
    print("  - Sharpening filter (fight anti-aliasing)")
    print("  - 40-color quantization (vs old 15)")
    print("  - Smart posterization (hard edges)")
    print("  - Nearest-neighbor resize\n")

    for img_path in test_images:
        if not Path(img_path).exists():
            print(f"⏭️  Skipping {img_path} (not found)")
            continue

        print(f"📸 Processing: {Path(img_path).name}")

        try:
            img_512, img_24 = process_image_better(img_path, output_dir, n_colors=40)

            # Analyze color count
            arr = np.array(img_512)
            pixels = arr.reshape(-1, 3)
            unique_colors = len(set(tuple(p) for p in pixels))

            print(f"   ✅ Saved with {unique_colors} colors")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "="*80)
    print("✅ Processing complete!")
    print(f"\n📁 Check results in: {output_dir}/")
    print("\nCompare these to:")
    print("  - Original generated (15 colors, soft edges)")
    print("  - Real Bespoke Punks (45 colors, sharp edges)")
    print("\nDoes this look closer to the real thing?")

if __name__ == "__main__":
    main()
