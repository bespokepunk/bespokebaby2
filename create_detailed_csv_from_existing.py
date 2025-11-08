#!/usr/bin/env python3
import csv
from pathlib import Path
from PIL import Image
import numpy as np
from collections import Counter
import re

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def extract_hex_from_image(img_path, sample_position='background'):
    """Extract hex color from specific position in image"""
    try:
        img = Image.open(img_path)
        img_array = np.array(img)
        h, w = img_array.shape[:2]

        if sample_position == 'background':
            # Sample corner for background
            pixel = img_array[0, 0][:3]
        elif sample_position == 'hair':
            # Sample top middle
            pixel = img_array[int(h*0.15), int(w*0.5)][:3]
        elif sample_position == 'eyes':
            # Sample eye position
            pixel = img_array[int(h*0.5), int(w*0.4)][:3]

        return rgb_to_hex(pixel)
    except:
        return ""

def sample_background_colors(img_path):
    """Sample all corners and edges to detect solid vs gradient"""
    try:
        img = Image.open(img_path)
        img_array = np.array(img)
        h, w = img_array.shape[:2]

        # Sample corners
        corners = [
            img_array[0, 0][:3],
            img_array[0, w-1][:3],
            img_array[h-1, 0][:3],
            img_array[h-1, w-1][:3]
        ]

        # Sample top and bottom edges
        top_edge = [img_array[0, w//4][:3], img_array[0, w//2][:3], img_array[0, 3*w//4][:3]]
        bottom_edge = [img_array[h-1, w//4][:3], img_array[h-1, w//2][:3], img_array[h-1, 3*w//4][:3]]

        all_samples = corners + top_edge + bottom_edge
        unique_colors = []

        for sample in all_samples:
            hex_val = rgb_to_hex(sample)
            if hex_val not in unique_colors:
                unique_colors.append(hex_val)

        return unique_colors
    except:
        return []

def parse_description_for_details(description):
    """Parse Description 1 field for detailed attributes"""
    if not description:
        return {}

    details = {}

    # Extract background
    if 'background' in description.lower():
        # Look for color mentions before "background"
        bg_match = re.search(r'(\w+(?:\s+\w+)?)\s+background', description, re.IGNORECASE)
        if bg_match:
            details['background'] = bg_match.group(1).strip()

    # Extract hair details
    if 'hair' in description.lower():
        hair_match = re.search(r'(\w+(?:\s+\w+)?)\s+hair', description, re.IGNORECASE)
        if hair_match:
            details['hair'] = hair_match.group(1).strip()

    # Extract specific props
    if 'chef hat' in description.lower():
        details['headwear'] = 'chef hat'
    if 'crown' in description.lower():
        details['headwear'] = 'crown'
    if 'cap' in description.lower() or 'hat' in description.lower():
        if 'headwear' not in details:
            details['headwear'] = 'hat'

    # Extract accessories
    accessories = []
    if 'bear ears' in description.lower():
        accessories.append('bear ears')
    if 'cat ears' in description.lower():
        accessories.append('cat ears')
    if 'bow' in description.lower() and 'elbow' not in description.lower():
        accessories.append('bows')
    if 'glasses' in description.lower() or 'sunglasses' in description.lower():
        accessories.append('glasses')
    if 'earring' in description.lower():
        accessories.append('earrings')
    if 'necklace' in description.lower():
        accessories.append('necklace')

    if accessories:
        details['accessories'] = ', '.join(accessories)

    return details

def main():
    # Paths
    existing_csv = "Context 1106/Bespoke Punks - Sheet2.csv"
    images_dir = "FORTRAINING6/bespokepunks"
    output_csv = "Context 1106/Bespoke Punks - Detailed Captions v2.csv"

    print("Reading existing CSV data...")
    with open(existing_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    data_rows = rows[1:]

    # Create mapping of existing data
    existing_data = {}
    for row in data_rows:
        if len(row) > 1 and row[1]:  # Has a name
            name = row[1]
            existing_data[name] = {
                'type': row[3] if len(row) > 3 else '',
                'background': row[6] if len(row) > 6 else '',
                'hair': row[7] if len(row) > 7 else '',
                'eyes': row[8] if len(row) > 8 else '',
                'props': row[12] if len(row) > 12 else '',
                'description_1': row[15] if len(row) > 15 else ''
            }

    print(f"Found {len(existing_data)} entries in existing CSV")

    # Get all images
    image_files = sorted(Path(images_dir).glob("*.png"))
    print(f"Found {len(image_files)} images")

    # Create new detailed CSV
    output_rows = []

    fieldnames = [
        'Name',
        'Type',
        'Background',
        'Background_Hex',
        'Background_Type',
        'Hair',
        'Hair_Hex',
        'Eyes',
        'Eyes_Hex',
        'Headwear',
        'Props',
        'Accessories',
        'Training_Caption'
    ]

    for i, img_path in enumerate(image_files, 1):
        name = img_path.stem
        print(f"  [{i}/{len(image_files)}] Processing {name}...")

        # Get existing data if available
        existing = existing_data.get(name, {})

        # Determine type
        type_val = existing.get('type', '')
        if not type_val:
            if name.startswith('lady_'):
                type_val = "Female"
            elif name.startswith('lad_'):
                type_val = "Male"

        # Parse description for additional details
        desc_details = parse_description_for_details(existing.get('description_1', ''))

        # Background
        background = existing.get('background', '') or desc_details.get('background', '')
        bg_hex_colors = sample_background_colors(img_path)
        bg_hex = ', '.join(bg_hex_colors) if bg_hex_colors else ''

        # Determine if gradient
        if len(bg_hex_colors) > 2:
            bg_type = "gradient"
        elif len(bg_hex_colors) == 1:
            bg_type = "solid"
        else:
            bg_type = "pattern"

        # Hair
        hair = existing.get('hair', '') or desc_details.get('hair', '')
        hair_hex = extract_hex_from_image(img_path, 'hair')

        # Eyes
        eyes = existing.get('eyes', '')
        eyes_hex = extract_hex_from_image(img_path, 'eyes')

        # Headwear
        headwear = desc_details.get('headwear', '')

        # Props
        props = existing.get('props', '')

        # Accessories
        accessories = desc_details.get('accessories', '')
        if props and not accessories:
            # If props exist but no parsed accessories, use props
            accessories = props

        # Build training caption
        caption_parts = []
        caption_parts.append("24x24 pixel art portrait")

        if background:
            if bg_hex:
                caption_parts.append(f"background: {background} ({bg_hex})")
            else:
                caption_parts.append(f"background: {background}")

        if hair:
            if hair_hex:
                caption_parts.append(f"hair: {hair} {hair_hex}")
            else:
                caption_parts.append(f"hair: {hair}")

        if eyes:
            if eyes_hex:
                caption_parts.append(f"eyes: {eyes} {eyes_hex}")
            else:
                caption_parts.append(f"eyes: {eyes}")

        if headwear:
            caption_parts.append(f"wearing {headwear}")

        if accessories:
            caption_parts.append(f"accessories: {accessories}")

        training_caption = ", ".join(caption_parts)

        # Create row
        row = {
            'Name': name,
            'Type': type_val,
            'Background': background,
            'Background_Hex': bg_hex,
            'Background_Type': bg_type,
            'Hair': hair,
            'Hair_Hex': hair_hex,
            'Eyes': eyes,
            'Eyes_Hex': eyes_hex,
            'Headwear': headwear,
            'Props': props,
            'Accessories': accessories,
            'Training_Caption': training_caption
        }

        output_rows.append(row)

    # Write new CSV
    print(f"\nWriting detailed CSV with {len(output_rows)} entries...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\n✅ Done! Created {output_csv}")
    print(f"   Total entries: {len(output_rows)}")

    # Show stats
    with_data = sum(1 for row in output_rows if row['Background'] or row['Hair'] or row['Eyes'])
    print(f"   Entries with existing data: {with_data}")
    print(f"   Entries needing manual review: {len(output_rows) - with_data}")

if __name__ == "__main__":
    main()
