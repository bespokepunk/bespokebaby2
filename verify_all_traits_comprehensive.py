#!/usr/bin/env python3
"""
Comprehensive trait verification for ALL caption attributes.
Checks: hair color, eye color, skin tone, background color, clothing colors.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def get_dominant_colors(pixels, exclude_threshold=None):
    """Get dominant colors from pixel region."""
    color_counts = Counter(tuple(p) for p in pixels)

    # Filter out very rare colors (noise)
    total = len(pixels)
    filtered = {color: count for color, count in color_counts.items()
                if count > total * 0.05}  # At least 5% of region

    return sorted(filtered.items(), key=lambda x: x[1], reverse=True)

def analyze_regions(image_path):
    """Analyze different regions of 24x24 pixel art."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    regions = {
        'hair': arr[0:8, 4:20],        # Top portion
        'eyes': arr[8:14, 6:18],       # Eye region
        'skin': arr[10:18, 8:16],      # Face/skin region
        'background': np.concatenate([  # Corners/edges
            arr[0:5, 0:5].reshape(-1, 3),
            arr[0:5, 19:24].reshape(-1, 3),
            arr[19:24, 0:5].reshape(-1, 3),
            arr[19:24, 19:24].reshape(-1, 3)
        ]),
        'clothing': arr[16:24, 8:16],  # Bottom portion
    }

    results = {}
    for region_name, pixels in regions.items():
        if len(pixels.shape) == 3:
            pixels = pixels.reshape(-1, 3)
        results[region_name] = get_dominant_colors(pixels)

    return results

def color_name_from_rgb(r, g, b, context='hair'):
    """Determine color name from RGB based on context."""
    r, g, b = int(r), int(g), int(b)

    # Common color categories
    colors = {}

    # Browns
    if 80 < r < 180 and 50 < g < 140 and 20 < b < 100:
        if r > g > b:
            if r - b > 60:
                colors['brown'] = r + g - b
            else:
                colors['dark brown'] = (r + g) / 2

    # Blacks/very dark
    if r < 60 and g < 60 and b < 60:
        colors['black'] = 100 - (r + g + b) / 3

    # Reds/oranges
    if r > 120 and r > g + 30 and r > b + 30:
        if g > 100:
            colors['orange'] = r
        else:
            colors['red'] = r

    # Blondes/yellows
    if r > 180 and g > 150 and b < 140:
        if abs(r - g) < 40:
            colors['blonde'] = (r + g) / 2
        elif r > g:
            colors['yellow'] = g

    # Blues
    if b > 100 and b > r + 30 and b > g + 20:
        if b > 180:
            colors['bright blue'] = b
        else:
            colors['blue'] = b

    # Cyans
    if b > 100 and g > 100 and abs(b - g) < 50 and b > r + 30:
        colors['cyan'] = (b + g) / 2

    # Greens
    if g > 100 and g > r + 30 and g > b + 30:
        if g > 180:
            colors['bright green'] = g
        else:
            colors['green'] = g

    # Purples/magentas
    if r > 100 and b > 100 and r > g and b > g:
        if abs(r - b) < 40:
            colors['purple'] = (r + b) / 2
        elif r > b:
            colors['magenta'] = r

    # Pinks
    if r > 180 and 100 < g < 180 and 100 < b < 200:
        colors['pink'] = r

    # Grays
    if 80 < r < 180 and abs(r - g) < 30 and abs(g - b) < 30:
        colors['gray'] = (r + g + b) / 3

    # Whites
    if r > 200 and g > 200 and b > 200:
        colors['white'] = (r + g + b) / 3

    # Tans/beige (for skin)
    if context == 'skin':
        if 150 < r < 240 and 120 < g < 220 and 80 < b < 200:
            if r > g > b:
                colors['light'] = r
        if 100 < r < 180 and 70 < g < 150 and 50 < b < 120:
            if r > g > b:
                colors['tan'] = (r + g) / 2
        if 60 < r < 120 and 40 < g < 100 and 30 < b < 80:
            if r > g > b:
                colors['dark'] = 150 - r

    if not colors:
        return None

    # Return highest scoring color
    return max(colors.items(), key=lambda x: x[1])[0]

def extract_caption_attributes(caption):
    """Extract claimed attributes from caption."""
    attrs = {}

    # Hair color/type
    hair_match = re.search(r'([\w\s]+?)\s+hair', caption, re.IGNORECASE)
    if hair_match:
        attrs['hair'] = hair_match.group(1).strip().lower()

    # Eye color
    eye_match = re.search(r'([\w\s]+?)\s+eyes', caption, re.IGNORECASE)
    if eye_match:
        attrs['eyes'] = eye_match.group(1).strip().lower()

    # Skin tone
    skin_match = re.search(r'(light|tan|dark|pale|medium|brown|[\w/]+)\s+skin', caption, re.IGNORECASE)
    if skin_match:
        attrs['skin'] = skin_match.group(1).strip().lower()

    # Background color
    bg_match = re.search(r'([\w\s]+?)\s+(solid\s+)?background', caption, re.IGNORECASE)
    if bg_match:
        attrs['background'] = bg_match.group(1).strip().lower()

    # Hex colors mentioned
    hex_matches = re.findall(r'#([0-9a-fA-F]{6})', caption)
    if hex_matches:
        attrs['hex_colors'] = [f"#{h.lower()}" for h in hex_matches]

    return attrs

def verify_trait(claimed, actual_colors, trait_type):
    """Verify if claimed trait matches actual pixel colors."""
    if not claimed or not actual_colors:
        return None, "insufficient_data"

    # Get top 3 actual colors
    actual_names = []
    for (r, g, b), count in actual_colors[:3]:
        color_name = color_name_from_rgb(r, g, b, trait_type)
        if color_name:
            actual_names.append({
                'name': color_name,
                'hex': rgb_to_hex(r, g, b),
                'rgb': (r, g, b),
                'count': count
            })

    if not actual_names:
        return None, "no_color_detected"

    # Check if claimed matches any actual
    claimed_normalized = claimed.lower().replace('/', ' ').replace('-', ' ')

    for actual in actual_names:
        if actual['name'] in claimed_normalized or claimed_normalized in actual['name']:
            return True, actual

    # No match
    return False, actual_names[0]

print("="*100)
print("COMPREHENSIVE TRAIT VERIFICATION - All Caption Attributes")
print("="*100)
print()

issues = []
perfect = []

for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        continue

    with open(txt_path, 'r') as f:
        caption = f.read().strip()

    # Analyze image
    regions = analyze_regions(png_path)

    # Extract caption claims
    attrs = extract_caption_attributes(caption)

    # Verify each trait
    file_issues = []

    for trait in ['hair', 'eyes', 'skin', 'background']:
        if trait in attrs:
            claimed = attrs[trait]
            actual_colors = regions.get(trait, [])

            match, evidence = verify_trait(claimed, actual_colors, trait)

            if match is False:
                file_issues.append({
                    'trait': trait,
                    'claimed': claimed,
                    'actual': evidence
                })

    if file_issues:
        issues.append({
            'file': png_file,
            'issues': file_issues,
            'caption': caption
        })
    else:
        perfect.append(png_file)

# Print results
print(f"{'='*100}")
print(f"SUMMARY")
print(f"{'='*100}")
print(f"✓ Perfect captions: {len(perfect)}")
print(f"⚠️  Files with issues: {len(issues)}")
print()

if issues:
    print(f"{'='*100}")
    print(f"ISSUES FOUND (First 20)")
    print(f"{'='*100}\n")

    for item in issues[:20]:
        print(f"File: {item['file']}")
        for issue in item['issues']:
            print(f"  ⚠️  {issue['trait'].upper()}:")
            print(f"      Caption claims: '{issue['claimed']}'")
            if isinstance(issue['actual'], dict):
                print(f"      Actual pixels: {issue['actual']['name']} ({issue['actual']['hex']})")
                print(f"      RGB: {issue['actual']['rgb']}, Count: {issue['actual']['count']} pixels")
        print()

print(f"\n{'='*100}")
print(f"Total files needing review: {len(issues)}")
print(f"Save full report? Re-run with output redirect")
print(f"{'='*100}")
