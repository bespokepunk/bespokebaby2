#!/usr/bin/env python3
"""
Package Bespoke Punks V3 training data for CivitAI upload
Includes 24x24 images + updated captions
"""

import shutil
from pathlib import Path
import zipfile

def package_training_data():
    print("📦 PACKAGING TRAINING DATA FOR CIVITAI V3")
    print("="*80)

    # Directories
    source_dir = Path("FORTRAINING6/bespokepunks")
    temp_dir = Path("temp_v3_package")
    output_zip = Path("bespoke_punks_v3_training.zip")

    # Clean up temp dir if exists
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir()

    print(f"\n📁 Source: {source_dir}/")
    print(f"📁 Temp:   {temp_dir}/")
    print(f"📦 Output: {output_zip}")
    print()

    # Copy images and captions
    image_count = 0
    caption_count = 0

    print("Copying files...")

    for img_path in sorted(source_dir.glob("*.png")):
        # Skip the composite image
        if "ALL" in img_path.name:
            continue

        # Copy image
        shutil.copy(img_path, temp_dir / img_path.name)
        image_count += 1

        # Copy corresponding caption
        txt_path = img_path.with_suffix('.txt')
        if txt_path.exists():
            shutil.copy(txt_path, temp_dir / txt_path.name)
            caption_count += 1

        if image_count % 50 == 0:
            print(f"  Copied {image_count} images...")

    print(f"\n✅ Copied {image_count} images")
    print(f"✅ Copied {caption_count} captions")

    # Create zip file
    print(f"\n📦 Creating zip file...")

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in sorted(temp_dir.glob("*")):
            zipf.write(file_path, file_path.name)

    # Clean up temp directory
    shutil.rmtree(temp_dir)

    # Get file size
    size_mb = output_zip.stat().st_size / (1024 * 1024)

    print(f"✅ Created: {output_zip}")
    print(f"📊 Size: {size_mb:.2f} MB")
    print()
    print("="*80)
    print("✅ PACKAGE READY FOR UPLOAD")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Go to https://civitai.com/models/train")
    print("  2. Click 'New Training'")
    print("  3. Select 'LoRA' training type")
    print("  4. Select 'Nova Pixels XL v2.0' as base model")
    print(f"  5. Upload: {output_zip}")
    print()
    print("Training settings:")
    print("  - Resolution: 24")
    print("  - LoRA Rank: 32")
    print("  - Network Alpha: 16")
    print("  - Epochs: 3")
    print("  - Batch Size: 4")
    print("  - Learning Rate: 0.0001")
    print("  - Enable Buckets: NO")
    print("  - Augmentation: NO")
    print()
    print(f"Expected cost: $5-6")
    print(f"Expected time: 6-8 hours")
    print()
    print("See CIVITAI_TRAINING_CONFIG_V3.md for full instructions!")

if __name__ == "__main__":
    package_training_data()
