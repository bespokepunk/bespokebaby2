#!/usr/bin/env python3
"""
Validate that region sampling is correct by checking actual images
"""

import json
from PIL import Image
import numpy as np
from collections import Counter

# Load one example to debug
test_file = 'civitai_v2_7_training/lad_001_carbon.png'

print("=" * 100)
print("VALIDATING REGION SAMPLING")
print("=" * 100)
print()

# Load image
img = Image.open(test_file).convert('RGB')
arr = np.array(img)

print(f"Image: {test_file}")
print(f"Size: {arr.shape}")
print()

# Show what's actually in each region
regions = {
    'hair_top': arr[0:8, :],
    'hair_left': arr[4:12, 0:8],
    'hair_right': arr[4:12, 16:24],
    'eyes_left': arr[9:13, 7:11],
    'eyes_right': arr[9:13, 13:17],
    'face_center': arr[10:16, 8:16],
    'nose': arr[13:15, 11:13],
    'mouth': arr[15:17, 9:15],
    'chin': arr[17:20, 9:15],
    'bg_top_left': arr[0:4, 0:4],
    'bg_top_right': arr[0:4, 20:24],
    'bg_bottom_left': arr[20:24, 0:4],
    'bg_bottom_right': arr[20:24, 20:24],
}

def get_dominant_colors(region_arr, name):
    """Get dominant colors from a region"""
    pixels = region_arr.reshape(-1, 3)

    # Count unique colors
    color_counts = Counter()
    for pixel in pixels:
        hex_color = '#{:02x}{:02x}{:02x}'.format(pixel[0], pixel[1], pixel[2])
        color_counts[hex_color] += 1

    # Get top 3
    top_colors = color_counts.most_common(3)

    print(f"\n{name} (rows {region_arr.shape[0]}, cols {region_arr.shape[1]}):")
    for hex_color, count in top_colors:
        percentage = (count / len(pixels)) * 100
        print(f"  {hex_color}: {count} pixels ({percentage:.1f}%)")

    return top_colors

print("\nREGION ANALYSIS:")
print("-" * 100)

for region_name, region_arr in regions.items():
    get_dominant_colors(region_arr, region_name)

# Now check what the user actually said
print("\n" + "=" * 100)
print("USER CORRECTIONS:")
print("=" * 100)

with open('supabase_export_complete.json', 'r') as f:
    records = json.load(f)

for record in records:
    if record['filename'] == 'lad_001_carbon.png':
        print(f"\nUser said: {record['user_corrections']}")
        print()

print("=" * 100)
print("ANALYSIS:")
print("=" * 100)
print("""
User said:
- Red brick checkered background (lighter and darker brick reds/browns)
- Grey hat
- Dark brown eyes
- Medium skin
- Medium grey shirt

So we should expect:
- Background regions: Red/brown brick colors (#a76857, #c06148)
- Eyes regions: Dark brown (different from background)
- Hair/hat: Grey colors
- Face: Medium skin tone
- Clothing: Grey

The issue is: Are the eye regions actually sampling the EYES or are they sampling the background/hat?
""")
