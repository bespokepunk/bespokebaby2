#!/usr/bin/env python3
"""
FIX: Region sampling with correct scaling for 576x576 images
"""

import json
from PIL import Image
import numpy as np
from collections import Counter

# Load data
with open('supabase_export_complete.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("FIXING REGION SAMPLING - CORRECT COORDINATES FOR 576x576 IMAGES")
print("=" * 100)
print()

def get_dominant_colors(region_arr):
    """Get dominant colors from region"""
    pixels = region_arr.reshape(-1, 3)

    color_counts = Counter()
    for pixel in pixels:
        hex_color = '#{:02x}{:02x}{:02x}'.format(pixel[0], pixel[1], pixel[2])
        color_counts[hex_color] += 1

    # Return top 3 with percentages
    total = len(pixels)
    results = []
    for hex_color, count in color_counts.most_common(3):
        results.append({
            'hex': hex_color,
            'rgb': [int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)],
            'count': count,
            'percentage': (count / total) * 100
        })

    return results

def sample_image_regions_correct(image_path):
    """Sample image regions with CORRECT scaling for 576x576 images"""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Check if image is 24x24 or 576x576
    scale = arr.shape[0] // 24  # Should be 24 for 576x576 images

    # Define regions for 24x24, then scale
    regions_24x24 = {
        'hair_top': (0, 8, 0, 24),
        'hair_left': (4, 12, 0, 8),
        'hair_right': (4, 12, 16, 24),
        'eyes_left': (9, 13, 7, 11),
        'eyes_right': (9, 13, 13, 17),
        'face_center': (10, 16, 8, 16),
        'nose': (13, 15, 11, 13),
        'mouth': (15, 17, 9, 15),
        'chin': (17, 20, 9, 15),
        'bg_top_left': (0, 4, 0, 4),
        'bg_top_right': (0, 4, 20, 24),
        'bg_bottom_left': (20, 24, 0, 4),
        'bg_bottom_right': (20, 24, 20, 24),
        'earring_left': (11, 14, 6, 8),
        'earring_right': (11, 14, 16, 18),
        'clothing_top': (18, 24, 8, 16),
        'clothing_bottom': (21, 24, 10, 14),
        'accessory_top': (0, 6, 8, 16),
    }

    # Scale regions
    sampled = {}
    for region_name, (r1, r2, c1, c2) in regions_24x24.items():
        # Scale coordinates
        r1_scaled = r1 * scale
        r2_scaled = r2 * scale
        c1_scaled = c1 * scale
        c2_scaled = c2 * scale

        # Extract region
        region_arr = arr[r1_scaled:r2_scaled, c1_scaled:c2_scaled]

        # Get dominant colors
        colors = get_dominant_colors(region_arr)

        sampled[region_name] = colors

    return sampled

# Test on first image
print("Testing on lad_001_carbon.png:\n")

test_path = 'civitai_v2_7_training/lad_001_carbon.png'
sampled = sample_image_regions_correct(test_path)

print("SAMPLED REGIONS:")
print("-" * 100)

for region_name in ['hair_top', 'eyes_left', 'eyes_right', 'face_center', 'mouth', 'bg_top_left', 'clothing_top']:
    colors = sampled.get(region_name, [])
    print(f"\n{region_name}:")
    for c in colors[:2]:
        print(f"  {c['hex']}: {c['percentage']:.1f}%")

# Get user correction for comparison
for record in records:
    if record['filename'] == 'lad_001_carbon.png':
        print("\n" + "=" * 100)
        print("USER SAID:")
        print(record['user_corrections'])
        print()

print("=" * 100)
print("\nNow re-sampling ALL 203 images with correct coordinates...")
print()

fixed_records = []

for idx, record in enumerate(records, 1):
    filename = record['filename']
    image_path = f'civitai_v2_7_training/{filename}'

    try:
        # Sample with correct scaling
        sampled_correct = sample_image_regions_correct(image_path)

        # Update record
        record['sampled_trait_colors_FIXED'] = sampled_correct

        fixed_records.append(record)

        if idx <= 5 or idx % 50 == 0:
            print(f"  [{idx}/203] {filename}")

    except Exception as e:
        print(f"  ERROR on {filename}: {e}")
        fixed_records.append(record)

print(f"\n✓ Re-sampled all 203 images with correct region coordinates\n")

# Save
with open('supabase_export_FIXED_SAMPLING.json', 'w') as f:
    json.dump(fixed_records, f, indent=2)

print(f"💾 Saved to: supabase_export_FIXED_SAMPLING.json")
print()
print("✅ Region sampling fixed!")
print()
