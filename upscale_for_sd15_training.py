#!/usr/bin/env python3
"""
Upscale 24x24 images to 512x512 for SD 1.5 training
Using nearest-neighbor to preserve pixel art style
"""

import os
from PIL import Image
from pathlib import Path

SOURCE_DIR = "civitai_v2_7_training"
OUTPUT_DIR = "sd15_training_512"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("UPSCALING 24x24 → 512x512 FOR SD 1.5 TRAINING")
print("=" * 80)
print(f"Source: {SOURCE_DIR}")
print(f"Output: {OUTPUT_DIR}")
print()

# Process all PNG images
png_files = sorted(Path(SOURCE_DIR).glob("*.png"))

print(f"Found {len(png_files)} images to process")
print()

for idx, img_path in enumerate(png_files, 1):
    # Load image
    img = Image.open(img_path)

    # Upscale to 512x512 using nearest-neighbor (no smoothing)
    img_512 = img.resize((512, 512), Image.NEAREST)

    # Save to output directory
    output_path = Path(OUTPUT_DIR) / img_path.name
    img_512.save(output_path)

    # Also copy the .txt caption file
    txt_file = img_path.with_suffix('.txt')
    if txt_file.exists():
        output_txt = Path(OUTPUT_DIR) / txt_file.name
        with open(txt_file, 'r') as f:
            caption = f.read()
        with open(output_txt, 'w') as f:
            f.write(caption)

    if idx <= 5 or idx % 50 == 0:
        print(f"  [{idx}/{len(png_files)}] {img_path.name} → 512x512")

print()
print("=" * 80)
print(f"✅ DONE! Upscaled {len(png_files)} images to 512x512")
print("=" * 80)
print(f"Output directory: {OUTPUT_DIR}")
print()
print("Next steps:")
print("1. Upload sd15_training_512/ folder to RunPod")
print("2. Run the SD 1.5 training script")
print()
