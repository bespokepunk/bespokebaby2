#!/usr/bin/env python3
import csv
import os
from pathlib import Path
from PIL import Image
import numpy as np
from collections import Counter

def get_dominant_color(image_array, region=None):
    """Extract dominant color from a region of the image"""
    if region:
        x1, y1, x2, y2 = region
        sample = image_array[y1:y2, x1:x2]
    else:
        sample = image_array

    # Flatten the region and get unique colors
    pixels = sample.reshape(-1, sample.shape[-1])

    # Remove alpha channel if present
    if pixels.shape[1] == 4:
        pixels = pixels[:, :3]

    # Convert to tuples for counting
    pixel_tuples = [tuple(p) for p in pixels]

    # Get most common color
    counter = Counter(pixel_tuples)
    most_common = counter.most_common(1)[0][0]

    return most_common

def rgb_to_color_name(rgb):
    """Convert RGB to approximate color name"""
    r, g, b = rgb

    # Define color ranges
    if r < 30 and g < 30 and b < 30:
        return "Black"
    elif r > 225 and g > 225 and b > 225:
        return "White"
    elif r > 200 and g < 100 and b < 100:
        return "Red"
    elif r > 200 and g > 150 and b < 100:
        return "Orange"
    elif r > 200 and g > 200 and b < 100:
        return "Yellow"
    elif r < 100 and g > 150 and b < 100:
        return "Green"
    elif r < 100 and g < 100 and b > 200:
        return "Blue"
    elif r > 150 and g < 100 and b > 150:
        return "Purple"
    elif r > 150 and g > 100 and b > 150:
        return "Pink"
    elif r > 150 and g > 150 and b > 100:
        return "Lavender"
    elif r > 100 and g > 50 and b < 50:
        return "Brown"
    elif 80 < r < 150 and 80 < g < 150 and 80 < b < 150:
        return "Grey"
    else:
        # Multi-color or gradient
        return "Multi"

def analyze_image(image_path):
    """Analyze image and extract attributes"""
    try:
        img = Image.open(image_path)
        img_array = np.array(img)

        height, width = img_array.shape[:2]

        # Extract background (corners of image)
        bg_samples = [
            img_array[0, 0],  # top-left
            img_array[0, width-1],  # top-right
            img_array[height-1, 0],  # bottom-left
            img_array[height-1, width-1]  # bottom-right
        ]

        # Get most common background color
        bg_color = get_dominant_color(np.array(bg_samples).reshape(1, -1, 3))
        background = rgb_to_color_name(bg_color)

        # Extract hair color (top third of image, middle columns)
        hair_region = img_array[0:height//3, width//3:2*width//3]
        hair_color_rgb = get_dominant_color(hair_region)
        hair = rgb_to_color_name(hair_color_rgb)

        # Extract eye color (middle of image, around eyes)
        eye_y = height // 2
        eye_region = img_array[eye_y-2:eye_y+2, width//3:2*width//3]
        eye_color_rgb = get_dominant_color(eye_region)
        eyes = rgb_to_color_name(eye_color_rgb)

        # Check for props (look for distinct colors in specific regions)
        props = ""

        return {
            'background': background,
            'hair': hair,
            'eyes': eyes,
            'props': props
        }
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
        return {
            'background': '',
            'hair': '',
            'eyes': '',
            'props': ''
        }

def main():
    # Paths
    csv_path = "Context 1106/Bespoke Punks - Sheet2.csv"
    images_dir = "FORTRAINING6/bespokepunks"
    output_csv = "Context 1106/Bespoke Punks - Sheet2.csv"

    # Read existing CSV
    print("Reading CSV...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    data_rows = rows[1:]

    # Get existing names from CSV
    existing_names = set()
    for row in data_rows:
        if len(row) > 1 and row[1]:  # Check Name column
            existing_names.add(row[1])

    print(f"Found {len(existing_names)} existing names in CSV")

    # Get all PNG files
    print("Scanning image directory...")
    image_files = sorted(Path(images_dir).glob("*.png"))

    # Extract names from filenames
    image_names = []
    for img_path in image_files:
        name = img_path.stem  # filename without extension
        image_names.append((name, img_path))

    print(f"Found {len(image_names)} images")

    # Find missing names
    missing = []
    for name, path in image_names:
        if name not in existing_names:
            missing.append((name, path))

    print(f"Found {len(missing)} missing entries")

    # Analyze missing images and create new rows
    new_rows = []
    print("\nAnalyzing images...")
    for i, (name, img_path) in enumerate(missing, 1):
        print(f"  [{i}/{len(missing)}] Analyzing {name}...")

        # Determine type
        if name.startswith('lady_'):
            type_val = "Female"
        elif name.startswith('lad_'):
            type_val = "Male"
        else:
            type_val = ""

        # Analyze image
        attrs = analyze_image(img_path)

        # Create new row matching CSV structure
        new_row = [
            'NEW',  # Duplicate? column
            name,  # Name
            '',  # Description
            type_val,  # Type
            '',  # Status
            '',  # Character
            attrs['background'],  # Background
            attrs['hair'],  # Hair
            attrs['eyes'],  # Eyes
            '',  # Empty column
            '',  # Empty column
            '',  # Empty column
            attrs['props'],  # Props
            '',  # Owner Name
            '',  # Owner Wallet
            '',  # Description 1
            ''   # Description 2
        ]

        new_rows.append(new_row)

    # Append new rows to existing data
    all_rows = [header] + data_rows + new_rows

    # Write updated CSV
    print(f"\nWriting {len(new_rows)} new rows to CSV...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    print(f"\nDone! Updated CSV saved to {output_csv}")
    print(f"Added {len(new_rows)} new entries marked with 'NEW' in the Duplicate? column")

    # Print summary
    ladies_added = sum(1 for name, _ in missing if name.startswith('lady_'))
    lads_added = sum(1 for name, _ in missing if name.startswith('lad_'))
    print(f"\nSummary:")
    print(f"  Ladies added: {ladies_added}")
    print(f"  Lads added: {lads_added}")

if __name__ == "__main__":
    main()
