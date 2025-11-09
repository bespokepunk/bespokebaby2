"""
Upscale 24x24 Bespoke Punk images to 512x512 for SD 1.5 training
Uses NEAREST neighbor to preserve pixel art aesthetic
"""

from PIL import Image
import os
import shutil

# Paths
SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_training_data_512/10_bespokepunks"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get all PNG files
png_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.png')]

print(f"Found {len(png_files)} PNG files to upscale")
print(f"Upscaling from 24x24 → 512x512 using NEAREST neighbor (pixel-perfect)")
print("=" * 70)

success_count = 0
for idx, filename in enumerate(sorted(png_files), 1):
    source_path = os.path.join(SOURCE_DIR, filename)

    # Open 24x24 image
    img = Image.open(source_path)

    # Verify it's actually 24x24
    if img.size != (24, 24):
        print(f"⚠️  [{idx}/{len(png_files)}] {filename} is {img.size}, skipping...")
        continue

    # Upscale to 512x512 using NEAREST (preserves sharp pixels)
    upscaled = img.resize((512, 512), Image.NEAREST)

    # Save to output directory
    output_path = os.path.join(OUTPUT_DIR, filename)
    upscaled.save(output_path)

    # Copy corresponding caption file
    txt_filename = filename.replace('.png', '.txt')
    source_txt = os.path.join(SOURCE_DIR, txt_filename)
    output_txt = os.path.join(OUTPUT_DIR, txt_filename)

    if os.path.exists(source_txt):
        shutil.copy2(source_txt, output_txt)
        print(f"✓ [{idx}/{len(png_files)}] {filename} + caption")
    else:
        print(f"✓ [{idx}/{len(png_files)}] {filename} (no caption found)")

    success_count += 1

print("=" * 70)
print(f"✅ Successfully upscaled {success_count}/{len(png_files)} images to 512x512")
print(f"📁 Output: {OUTPUT_DIR}")
print("\nReady for Kohya training at 512x512 resolution!")
