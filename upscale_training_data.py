#!/usr/bin/env python3
"""
Upscale 24x24 pixel art to 512x512 while preserving pixel boundaries
This allows training on resolution AI models expect while maintaining pixel art style
"""

from PIL import Image
from pathlib import Path
from tqdm import tqdm
import shutil

def upscale_dataset():
    """Upscale all training images from 24x24 to 512x512"""

    print("=" * 80)
    print("🔼 UPSCALING TRAINING DATA: 24x24 → 512x512")
    print("=" * 80)

    # Source and destination directories
    source_img_dir = Path("FORTRAINING6/bespokepunktextimages")
    source_txt_dir = Path("FORTRAINING6/bespokepunktext")

    dest_img_dir = Path("FORTRAINING6_UPSCALED/images")
    dest_txt_dir = Path("FORTRAINING6_UPSCALED/captions")

    # Create destination directories
    dest_img_dir.mkdir(parents=True, exist_ok=True)
    dest_txt_dir.mkdir(parents=True, exist_ok=True)

    # Get all image files
    image_files = sorted(source_img_dir.glob("*.png"))

    print(f"\n📊 Found {len(image_files)} images to upscale")
    print(f"📁 Source: {source_img_dir}")
    print(f"📁 Destination: {dest_img_dir}")
    print(f"🎨 Method: Nearest Neighbor (preserves pixel boundaries)")
    print(f"📏 Target size: 512x512 pixels")
    print()

    success_count = 0
    error_count = 0

    for img_path in tqdm(image_files, desc="Upscaling images"):
        try:
            # Load original image
            img = Image.open(img_path)

            # Upscale with NEAREST neighbor to preserve sharp pixels
            img_upscaled = img.resize((512, 512), Image.NEAREST)

            # Save upscaled image
            dest_img_path = dest_img_dir / img_path.name
            img_upscaled.save(dest_img_path, "PNG")

            # Copy corresponding caption file
            txt_filename = img_path.stem + ".txt"
            source_txt_path = source_txt_dir / txt_filename
            dest_txt_path = dest_txt_dir / txt_filename

            if source_txt_path.exists():
                shutil.copy2(source_txt_path, dest_txt_path)
            else:
                print(f"⚠️  Warning: No caption file for {img_path.name}")

            success_count += 1

        except Exception as e:
            print(f"❌ Error processing {img_path.name}: {e}")
            error_count += 1

    print("\n" + "=" * 80)
    print("✅ UPSCALING COMPLETE!")
    print("=" * 80)
    print(f"✅ Successfully upscaled: {success_count} images")
    print(f"📝 Caption files copied: {success_count}")
    if error_count > 0:
        print(f"❌ Errors: {error_count}")
    print(f"\n📁 Upscaled dataset location:")
    print(f"   Images:   {dest_img_dir.absolute()}")
    print(f"   Captions: {dest_txt_dir.absolute()}")
    print("\n💡 Next steps:")
    print("   1. Review a few upscaled images to verify quality")
    print("   2. Train on Replicate using this upscaled dataset")
    print("   3. When generating, use 512x512 then downscale to 24x24")

if __name__ == "__main__":
    upscale_dataset()
