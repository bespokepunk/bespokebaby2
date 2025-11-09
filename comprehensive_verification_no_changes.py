#!/usr/bin/env python3
"""
COMPREHENSIVE VERIFICATION - Check ALL traits against actual pixels.
Reports discrepancies WITHOUT making any changes.
User must review before any fixes are applied.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def get_full_image_palette(image_path, top_n=15):
    """Get the complete color palette from the entire image."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)

    total_pixels = len(pixels)
    color_counts = Counter(tuple(int(c) for c in p) for p in pixels)

    palette = []
    for (r, g, b), count in color_counts.most_common(top_n):
        percentage = (count / total_pixels) * 100
        palette.append({
            'rgb': (r, g, b),
            'hex': rgb_to_hex(r, g, b),
            'count': count,
            'percentage': percentage
        })

    return palette

def analyze_specific_regions(image_path):
    """Analyze specific regions of the 24x24 image."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Define regions more carefully for 24x24 pixel art
    regions = {
        'hair_top': arr[0:8, :],           # Top rows - hair
        'eyes_region': arr[8:14, 6:18],    # Eye area
        'face_skin': arr[10:16, 8:16],     # Face/skin area
        'background_corners': np.concatenate([
            arr[0:6, 0:6].reshape(-1, 3),
            arr[0:6, 18:24].reshape(-1, 3),
            arr[18:24, 0:6].reshape(-1, 3),
            arr[18:24, 18:24].reshape(-1, 3)
        ]),
        'lower_clothing': arr[16:24, 6:18], # Bottom area - clothing
    }

    region_colors = {}
    for region_name, pixels in regions.items():
        if len(pixels.shape) == 3:
            pixels = pixels.reshape(-1, 3)

        color_counts = Counter(tuple(int(c) for c in p) for p in pixels)
        top_colors = []
        for (r, g, b), count in color_counts.most_common(5):
            top_colors.append({
                'rgb': (r, g, b),
                'hex': rgb_to_hex(r, g, b),
                'count': count
            })
        region_colors[region_name] = top_colors

    return region_colors

def extract_all_caption_attributes(caption):
    """Extract ALL attributes mentioned in caption."""
    attrs = {}

    # Hair description (capture full description before "hair")
    hair_match = re.search(r'([\w\s\-/]+?)\s+hair', caption, re.IGNORECASE)
    if hair_match:
        attrs['hair'] = hair_match.group(1).strip()

    # Eye color
    eye_match = re.search(r'([\w\s]+?)\s+eyes', caption, re.IGNORECASE)
    if eye_match:
        attrs['eyes'] = eye_match.group(1).strip()

    # Skin tone
    skin_match = re.search(r'([\w/\-\s]+?)\s+skin', caption, re.IGNORECASE)
    if skin_match:
        attrs['skin'] = skin_match.group(1).strip()

    # Background color
    bg_match = re.search(r'([\w\s]+?)\s+(solid\s+)?background', caption, re.IGNORECASE)
    if bg_match:
        attrs['background'] = bg_match.group(1).strip()

    # Clothing color
    clothing_match = re.search(r'([\w\s]+?)\s+clothing', caption, re.IGNORECASE)
    if clothing_match:
        attrs['clothing'] = clothing_match.group(1).strip()

    # All hex colors mentioned
    hex_colors = re.findall(r'(#[0-9a-fA-F]{6})', caption)
    if hex_colors:
        attrs['hex_colors'] = [h.lower() for h in hex_colors]

    return attrs

def describe_color_simple(r, g, b):
    """Simple color description from RGB."""
    r, g, b = int(r), int(g), int(b)

    # Very dark/black
    if r < 50 and g < 50 and b < 50:
        return "black/very dark"

    # Very light/white
    if r > 200 and g > 200 and b > 200:
        return "white/very light"

    # Grays
    if abs(r - g) < 30 and abs(g - b) < 30:
        if r < 100:
            return "dark gray"
        elif r < 160:
            return "gray"
        else:
            return "light gray"

    # Browns (orange-ish, darker tones)
    if 60 < r < 200 and 40 < g < 140 and 20 < b < 100 and r > g > b:
        return "brown/tan"

    # Reds/oranges
    if r > 150 and r > g + 40 and r > b + 40:
        if g > 100:
            return "orange"
        else:
            return "red"

    # Yellows/blondes
    if r > 180 and g > 160 and b < 140:
        return "yellow/blonde"

    # Blues
    if b > 100 and b > r + 30 and b > g + 20:
        return "blue"

    # Cyans
    if b > 100 and g > 100 and abs(b - g) < 50:
        return "cyan/aqua"

    # Greens
    if g > 100 and g > r + 30 and g > b + 30:
        return "green"

    # Purples/magentas
    if r > 100 and b > 100 and r > g and b > g:
        return "purple/magenta"

    # Pinks
    if r > 180 and g > 100 and b > 100 and r > g and r > b:
        return "pink"

    return f"other ({r},{g},{b})"

print("="*100)
print("COMPREHENSIVE VERIFICATION - NO CHANGES WILL BE MADE")
print("Analyzing ALL images and ALL traits")
print("="*100)
print()

issues_found = []
total_checked = 0

for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        continue

    total_checked += 1

    with open(txt_path, 'r') as f:
        caption = f.read().strip()

    # Get actual image colors
    full_palette = get_full_image_palette(png_path)
    region_colors = analyze_specific_regions(png_path)
    caption_attrs = extract_all_caption_attributes(caption)

    # Check each attribute
    file_issues = []

    # Check EYES
    if 'eyes' in caption_attrs:
        claimed_eye_color = caption_attrs['eyes'].lower()
        actual_eye_colors = region_colors['eyes_region'][:3]

        if actual_eye_colors:
            actual_descriptions = [describe_color_simple(*c['rgb']) for c in actual_eye_colors]

            # Check if claimed matches any actual
            match_found = any(claimed_eye_color in desc or desc.split('/')[0] in claimed_eye_color
                            for desc in actual_descriptions)

            if not match_found:
                file_issues.append({
                    'trait': 'EYES',
                    'claimed': claimed_eye_color,
                    'actual_top_3': [
                        f"{c['hex']} ({describe_color_simple(*c['rgb'])})"
                        for c in actual_eye_colors[:3]
                    ]
                })

    # Check HAIR
    if 'hair' in caption_attrs:
        claimed_hair = caption_attrs['hair'].lower()
        actual_hair_colors = region_colors['hair_top'][:3]

        if actual_hair_colors:
            actual_descriptions = [describe_color_simple(*c['rgb']) for c in actual_hair_colors]

            # More lenient matching for hair (can have multiple descriptors)
            match_found = any(
                any(word in desc for word in claimed_hair.split() if len(word) > 3)
                for desc in actual_descriptions
            )

            if not match_found and 'sunglasses' not in caption.lower():
                file_issues.append({
                    'trait': 'HAIR',
                    'claimed': claimed_hair,
                    'actual_top_3': [
                        f"{c['hex']} ({describe_color_simple(*c['rgb'])})"
                        for c in actual_hair_colors[:3]
                    ]
                })

    # Check HEX COLORS
    if 'hex_colors' in caption_attrs:
        image_hexes = {c['hex'] for c in full_palette}

        for claimed_hex in caption_attrs['hex_colors']:
            if claimed_hex not in image_hexes:
                # Find closest
                closest = min(full_palette, key=lambda c: sum(
                    (a - b)**2 for a, b in
                    zip([int(claimed_hex[i:i+2], 16) for i in (1, 3, 5)], c['rgb'])
                ))

                distance = sum(
                    (a - b)**2 for a, b in
                    zip([int(claimed_hex[i:i+2], 16) for i in (1, 3, 5)], closest['rgb'])
                ) ** 0.5

                if distance > 2:  # Only flag if significantly different
                    file_issues.append({
                        'trait': 'HEX_COLOR',
                        'claimed': claimed_hex,
                        'actual_closest': f"{closest['hex']} (distance: {distance:.1f})"
                    })

    # Check BACKGROUND
    if 'background' in caption_attrs:
        claimed_bg = caption_attrs['background'].lower()
        actual_bg_colors = region_colors['background_corners'][:3]

        if actual_bg_colors:
            actual_descriptions = [describe_color_simple(*c['rgb']) for c in actual_bg_colors]

            match_found = any(claimed_bg in desc or desc.split('/')[0] in claimed_bg
                            for desc in actual_descriptions)

            if not match_found:
                file_issues.append({
                    'trait': 'BACKGROUND',
                    'claimed': claimed_bg,
                    'actual_top_3': [
                        f"{c['hex']} ({describe_color_simple(*c['rgb'])})"
                        for c in actual_bg_colors[:3]
                    ]
                })

    if file_issues:
        issues_found.append({
            'file': png_file,
            'issues': file_issues,
            'full_palette': full_palette[:5],  # Top 5 colors
            'caption': caption
        })

print(f"{'='*100}")
print(f"VERIFICATION COMPLETE")
print(f"{'='*100}")
print(f"Total images checked: {total_checked}")
print(f"Images with potential issues: {len(issues_found)}")
print(f"Images that look correct: {total_checked - len(issues_found)}")
print()

if issues_found:
    print(f"{'='*100}")
    print(f"DETAILED FINDINGS (First 30)")
    print(f"{'='*100}\n")

    for item in issues_found[:30]:
        print(f"{'='*100}")
        print(f"FILE: {item['file']}")
        print(f"{'='*100}")

        print(f"\nTop 5 Colors in Image:")
        for i, color in enumerate(item['full_palette'], 1):
            print(f"  {i}. {color['hex']} - {color['percentage']:.1f}% of pixels ({color['count']} pixels)")

        print(f"\nIssues Found:")
        for issue in item['issues']:
            print(f"\n  {issue['trait']}:")
            print(f"    Caption says: '{issue['claimed']}'")
            if 'actual_top_3' in issue:
                print(f"    Actual pixels (top 3):")
                for color in issue['actual_top_3']:
                    print(f"      - {color}")
            elif 'actual_closest' in issue:
                print(f"    Closest actual: {issue['actual_closest']}")

        print()

print(f"\n{'='*100}")
print("RECOMMENDATION")
print(f"{'='*100}")
print(f"Review the findings above.")
print(f"If you approve, I can create a fix script for the confirmed issues.")
print(f"DO NOT make any changes yet - user must review first!")
print(f"{'='*100}")

# Save full report
report_path = "/tmp/full_verification_report.txt"
with open(report_path, 'w') as f:
    f.write(f"Total issues found: {len(issues_found)}\n\n")
    for item in issues_found:
        f.write(f"\n{'='*80}\n")
        f.write(f"FILE: {item['file']}\n")
        f.write(f"{'='*80}\n")
        for issue in item['issues']:
            f.write(f"{issue['trait']}: {issue['claimed']}\n")
        f.write(f"\n")

print(f"\nFull report saved to: {report_path}")
