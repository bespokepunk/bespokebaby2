#!/usr/bin/env python3
"""
Create accurate captions based on actual visual analysis
This will be populated with manual observations
"""
import csv
from pathlib import Path
from PIL import Image
import numpy as np

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def sample_bg_hex(img_path):
    """Sample background hex colors"""
    img = Image.open(img_path)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    samples = [
        img_array[0, 0][:3],
        img_array[0, w-1][:3],
        img_array[h-1, 0][:3],
        img_array[h-1, w-1][:3],
    ]

    hex_colors = [rgb_to_hex(s) for s in samples]
    unique = list(dict.fromkeys(hex_colors))
    return ', '.join(unique)

# Manual accurate annotations based on visual review
# This will be filled in as I review each image
accurate_data = {
    'lady_000_lemon': {
        'background': 'Yellow',
        'background_pattern': 'solid',
        'hair': 'Brown',
        'eyes': 'Blue',
        'headwear': 'red and white checkered bandana',
        'accessories': '',
        'clothing': 'blue top',
        'facial_features': 'orange lips',
        'skin_tone': 'light'
    },
    'lady_026_fur': {
        'background': 'Blue',
        'background_pattern': 'solid',
        'hair': 'Black',
        'eyes': 'Green',
        'headwear': 'brown bear/cat ears',
        'accessories': '',
        'clothing': 'grey/green top',
        'facial_features': 'pink lips',
        'skin_tone': 'light'
    },
    'lady_062_Dalia-BD': {
        'background': 'Blue',
        'background_pattern': 'solid',
        'hair': 'Black',
        'eyes': 'Brown',
        'headwear': 'white bear ears',
        'accessories': 'red bows (side)',
        'clothing': 'red top',
        'facial_features': 'pink lips',
        'skin_tone': 'light'
    },
    'lady_062_Dalia-2': {
        'background': 'Pink',
        'background_pattern': 'solid',
        'hair': 'Black',
        'eyes': 'Brown',
        'headwear': 'brown bear ears',
        'accessories': 'red bows (side)',
        'clothing': 'red top',
        'facial_features': 'pink lips',
        'skin_tone': 'light'
    },
}

def generate_caption(name, data, bg_hex):
    """Generate training caption from data"""
    parts = []
    parts.append("24x24 pixel art portrait")

    # Background
    if data.get('background_pattern') == 'gradient':
        parts.append(f"{data['background']} gradient background ({bg_hex})")
    elif data.get('background_pattern') == 'checkered':
        parts.append(f"{data['background']} checkered background ({bg_hex})")
    else:
        parts.append(f"{data['background']} background ({bg_hex})")

    # Hair
    if data.get('hair'):
        parts.append(f"{data['hair']} hair")

    # Eyes
    if data.get('eyes'):
        parts.append(f"{data['eyes']} eyes")

    # Skin tone
    if data.get('skin_tone'):
        parts.append(f"{data['skin_tone']} skin")

    # Headwear
    if data.get('headwear'):
        parts.append(f"wearing {data['headwear']}")

    # Accessories
    if data.get('accessories'):
        parts.append(f"accessories: {data['accessories']}")

    # Facial hair
    if data.get('facial_hair'):
        parts.append(f"{data['facial_hair']}")

    # Clothing
    if data.get('clothing'):
        parts.append(f"{data['clothing']}")

    return ", ".join(parts)

def main():
    images_dir = "FORTRAINING6/bespokepunks"
    output_csv = "Context 1106/Bespoke Punks - Accurate Captions.csv"

    print("Creating accurate captions CSV...")
    print(f"Currently have {len(accurate_data)} manually reviewed entries")
    print("Remaining entries will be marked for review\n")

    image_files = sorted(Path(images_dir).glob("*.png"))

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
        'Other_Details',
        'Training_Caption',
        'Review_Status'
    ]

    rows = []

    for img_path in image_files:
        name = img_path.stem

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
        if name in accurate_data:
            data = accurate_data[name]
            caption = generate_caption(name, data, bg_hex)
            review_status = "REVIEWED"
        else:
            data = {}
            caption = ""
            review_status = "NEEDS_REVIEW"

        row = {
            'Name': name,
            'Type': type_val,
            'Background': data.get('background', ''),
            'Background_Hex': bg_hex,
            'Background_Pattern': data.get('background_pattern', ''),
            'Hair': data.get('hair', ''),
            'Eyes': data.get('eyes', ''),
            'Skin_Tone': data.get('skin_tone', ''),
            'Headwear': data.get('headwear', ''),
            'Facial_Hair': data.get('facial_hair', ''),
            'Accessories': data.get('accessories', ''),
            'Clothing': data.get('clothing', ''),
            'Other_Details': data.get('other_details', ''),
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

    print(f"✅ Created {output_csv}")
    print(f"   Reviewed: {reviewed}")
    print(f"   Needs review: {needs_review}")
    print(f"   Total: {len(rows)}")

if __name__ == "__main__":
    main()
