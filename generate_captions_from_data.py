#!/usr/bin/env python3
"""
Generate training captions and CSV from comprehensive_accurate_data.py
"""
import csv
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
    output_csv = "Context 1106/Bespoke Punks - Accurate Captions.csv"

    print(f"Generating captions from {len(ACCURATE_DATA)} documented images...")

    # Get all images
    all_images = sorted([p.stem for p in images_dir.glob("*.png")])

    fieldnames = [
        'Name',
        'Type',
        'Background',
        'Background_Hex',
        'Background_Pattern',
        'Hair',
        'Eyes',
        'Skin_Tone',
        'Headwear',
        'Facial_Hair',
        'Accessories',
        'Clothing',
        'Lips',
        'Training_Caption',
        'Review_Status'
    ]

    rows = []

    for name in all_images:
        img_path = images_dir / f"{name}.png"

        # Type
        if name.startswith('lady_'):
            type_val = "Female"
        elif name.startswith('lad_'):
            type_val = "Male"
        else:
            type_val = ""

        # Get background hex
        bg_hex = sample_bg_hex(img_path)

        # Check if we have manual data
        if name in ACCURATE_DATA:
            data = ACCURATE_DATA[name]
            caption = generate_caption(name, data, bg_hex)
            review_status = "REVIEWED"
        else:
            data = {}
            caption = ""
            review_status = "NEEDS_REVIEW"

        row = {
            'Name': name,
            'Type': type_val,
            'Background': data.get('bg', ''),
            'Background_Hex': bg_hex,
            'Background_Pattern': data.get('bg_pattern', ''),
            'Hair': data.get('hair', ''),
            'Eyes': data.get('eyes', ''),
            'Skin_Tone': data.get('skin', ''),
            'Headwear': data.get('headwear', ''),
            'Facial_Hair': data.get('facial_hair', ''),
            'Accessories': data.get('accessories', ''),
            'Clothing': data.get('clothing', ''),
            'Lips': data.get('lips', ''),
            'Training_Caption': caption,
            'Review_Status': review_status
        }

        rows.append(row)

    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    reviewed = sum(1 for r in rows if r['Review_Status'] == 'REVIEWED')
    needs_review = sum(1 for r in rows if r['Review_Status'] == 'NEEDS_REVIEW')

    print(f"\n✅ Created {output_csv}")
    print(f"   Reviewed: {reviewed} ({reviewed/len(rows)*100:.1f}%)")
    print(f"   Needs review: {needs_review} ({needs_review/len(rows)*100:.1f}%)")
    print(f"   Total: {len(rows)}")

    # Show a few sample captions
    print(f"\n📝 Sample captions:")
    for i, row in enumerate(rows[:5]):
        if row['Training_Caption']:
            print(f"\n{i+1}. {row['Name']}")
            print(f"   {row['Training_Caption']}")

if __name__ == "__main__":
    main()
