#!/usr/bin/env python3
"""
Create individual .txt caption files for each image for training
"""
from pathlib import Path
from PIL import Image
import numpy as np

from comprehensive_accurate_data import ACCURATE_DATA

def rgb_to_hex(rgb):
    """Convert RGB to hex"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def sample_bg_hex(img_path):
    """Sample background hex colors from corners"""
    img = Image.open(img_path)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    corners = [
        img_array[0, 0][:3],
        img_array[0, w-1][:3],
        img_array[h-1, 0][:3],
        img_array[h-1, w-1][:3],
    ]

    hex_colors = [rgb_to_hex(c) for c in corners]
    unique = list(dict.fromkeys(hex_colors))
    return ', '.join(unique)

def generate_caption(name, data, bg_hex):
    """Generate training caption from data"""
    parts = []
    parts.append("24x24 pixel art portrait")

    img_type = "lady" if name.startswith("lady_") else "lad"

    # Background
    if data.get('bg'):
        if data.get('bg_pattern') in ['gradient', 'checkered', 'split', 'striped']:
            parts.append(f"{data['bg']} {data['bg_pattern']} background ({bg_hex})")
        else:
            parts.append(f"{data['bg']} background ({bg_hex})")

    # Hair
    if data.get('hair'):
        parts.append(f"{data['hair']} hair")

    # Eyes
    if data.get('eyes'):
        parts.append(f"{data['eyes']} eyes")

    # Skin tone
    if data.get('skin'):
        parts.append(f"{data['skin']} skin")

    # Headwear
    if data.get('headwear'):
        parts.append(f"wearing {data['headwear']}")

    # Accessories
    if data.get('accessories'):
        parts.append(f"{data['accessories']}")

    # Facial hair (for male characters)
    if img_type == "lad" and data.get('facial_hair'):
        parts.append(f"{data['facial_hair']}")

    # Clothing
    if data.get('clothing'):
        parts.append(f"{data['clothing']}")

    # Lips (for female characters)
    if img_type == "lady" and data.get('lips'):
        parts.append(f"{data['lips']} lips")

    return ", ".join(parts)

def main():
    images_dir = Path("FORTRAINING6/bespokepunks")

    print(f"Creating caption .txt files for {len(ACCURATE_DATA)} documented images...")

    created_count = 0
    skipped_count = 0

    for name, data in ACCURATE_DATA.items():
        img_path = images_dir / f"{name}.png"
        txt_path = images_dir / f"{name}.txt"

        if not img_path.exists():
            print(f"⚠️  Image not found: {img_path}")
            skipped_count += 1
            continue

        # Get background hex
        bg_hex = sample_bg_hex(img_path)

        # Generate caption
        caption = generate_caption(name, data, bg_hex)

        # Write caption to .txt file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(caption)

        created_count += 1

    print(f"\n✅ Created {created_count} caption files")
    if skipped_count > 0:
        print(f"⚠️  Skipped {skipped_count} (image not found)")
    print(f"\n📁 Caption files location: {images_dir}")

    # Show some examples
    print(f"\n📝 Sample caption files created:")
    for i, (name, data) in enumerate(list(ACCURATE_DATA.items())[:5]):
        txt_path = images_dir / f"{name}.txt"
        if txt_path.exists():
            with open(txt_path, 'r', encoding='utf-8') as f:
                caption = f.read()
            print(f"\n{i+1}. {name}.txt:")
            print(f"   {caption}")

if __name__ == "__main__":
    main()
