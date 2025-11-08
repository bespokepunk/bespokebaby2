#!/usr/bin/env python3
"""
Manual image review helper - processes images and allows for accurate documentation
"""
import csv
from pathlib import Path
from PIL import Image
import numpy as np

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def sample_background_colors(img_array):
    """Sample background colors from corners and edges"""
    h, w = img_array.shape[:2]

    samples = [
        img_array[0, 0][:3],           # top-left
        img_array[0, w//2][:3],         # top-center
        img_array[0, w-1][:3],          # top-right
        img_array[h-1, 0][:3],          # bottom-left
        img_array[h-1, w//2][:3],       # bottom-center
        img_array[h-1, w-1][:3],        # bottom-right
    ]

    hex_colors = [rgb_to_hex(s) for s in samples]
    unique_hex = list(dict.fromkeys(hex_colors))  # preserve order, remove duplicates

    return unique_hex

def analyze_image_structure(img_path):
    """Extract technical details from image"""
    img = Image.open(img_path)
    img_array = np.array(img)

    bg_colors = sample_background_colors(img_array)

    return {
        'bg_hex': bg_colors,
        'has_gradient': len(bg_colors) > 2,
        'size': f"{img.width}x{img.height}"
    }

# This will store manual annotations
# Format: name -> {attributes}
manual_annotations = {}

def main():
    """Generate template for manual review"""
    images_dir = "FORTRAINING6/bespokepunks"
    output_template = "Context 1106/image_review_template.csv"

    image_files = sorted(Path(images_dir).glob("*.png"))

    print(f"Creating review template for {len(image_files)} images...")

    rows = []
    fieldnames = [
        'Name',
        'Type',
        'Background_Color',
        'Background_Hex',
        'Background_Pattern',
        'Hair_Color',
        'Hair_Style',
        'Eye_Color',
        'Skin_Tone',
        'Headwear',
        'Headwear_Color',
        'Facial_Hair',
        'Accessories',
        'Clothing',
        'Other_Props',
        'Notes'
    ]

    for img_path in image_files:
        name = img_path.stem

        # Determine type
        if name.startswith('lady_'):
            type_val = "Female"
        elif name.startswith('lad_'):
            type_val = "Male"
        else:
            type_val = ""

        # Get background hex
        analysis = analyze_image_structure(img_path)
        bg_hex = ', '.join(analysis['bg_hex'])

        row = {
            'Name': name,
            'Type': type_val,
            'Background_Color': '',
            'Background_Hex': bg_hex,
            'Background_Pattern': 'gradient' if analysis['has_gradient'] else 'solid',
            'Hair_Color': '',
            'Hair_Style': '',
            'Eye_Color': '',
            'Skin_Tone': '',
            'Headwear': '',
            'Headwear_Color': '',
            'Facial_Hair': '',
            'Accessories': '',
            'Clothing': '',
            'Other_Props': '',
            'Notes': ''
        }

        rows.append(row)

    # Write template
    with open(output_template, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Created template: {output_template}")
    print(f"   Background hex colors extracted automatically")
    print(f"   Ready for manual review")

if __name__ == "__main__":
    main()
