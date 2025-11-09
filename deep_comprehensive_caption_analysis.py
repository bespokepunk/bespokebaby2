#!/usr/bin/env python3
"""
DEEP COMPREHENSIVE CAPTION ANALYSIS
Extracts EVERY detail from each punk:
- Full 15-color palette with hex codes
- Hair: color, style, shape (afro, fluffy, long, short, spiky, etc.)
- Eyes: color with exact hex
- Skin: tone with exact hex
- Accessories: sunglasses, earrings, crown, hat, bandana, etc.
- Clothing: colors, patterns, accents
- Background: color with exact hex
- Special features: highlights, shadows, outlines
"""

import os
import json
from PIL import Image
import numpy as np
from collections import Counter
import re

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def get_full_palette(image_path, top_n=15):
    """Extract top N colors from entire image."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)

    total_pixels = len(pixels)
    color_counts = Counter(tuple(int(c) for c in p) for p in pixels)

    palette = []
    for (r, g, b), count in color_counts.most_common(top_n):
        percentage = (count / total_pixels) * 100
        palette.append({
            'hex': rgb_to_hex(r, g, b),
            'rgb': [r, g, b],
            'count': count,
            'percentage': round(percentage, 2)
        })

    return palette

def analyze_regions_detailed(image_path):
    """Deep analysis of specific regions."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Define precise regions for 24x24 pixel art
    regions = {
        'hair_top': arr[0:8, :],           # Top 8 rows
        'hair_left': arr[4:12, 0:8],       # Left side hair
        'hair_right': arr[4:12, 16:24],    # Right side hair
        'eyes_left': arr[9:13, 7:11],      # Left eye
        'eyes_right': arr[9:13, 13:17],    # Right eye
        'face_center': arr[10:16, 8:16],   # Face/skin
        'nose': arr[13:15, 11:13],         # Nose area
        'mouth': arr[15:17, 9:15],         # Mouth area
        'accessories_top': arr[5:10, 2:22],# Head accessories
        'earrings_left': arr[12:16, 2:6],  # Left earring area
        'earrings_right': arr[12:16, 18:22],# Right earring area
        'background_top_left': arr[0:6, 0:6],
        'background_top_right': arr[0:6, 18:24],
        'background_bottom_left': arr[18:24, 0:6],
        'background_bottom_right': arr[18:24, 18:24],
        'clothing_top': arr[16:20, 6:18],  # Upper clothing
        'clothing_bottom': arr[20:24, 8:16], # Lower clothing
    }

    analyzed = {}
    for region_name, pixels in regions.items():
        if len(pixels.shape) == 3:
            pixels = pixels.reshape(-1, 3)

        if len(pixels) == 0:
            continue

        color_counts = Counter(tuple(int(c) for c in p) for p in pixels)
        top_colors = []

        for (r, g, b), count in color_counts.most_common(5):
            top_colors.append({
                'hex': rgb_to_hex(r, g, b),
                'rgb': [r, g, b],
                'count': count,
                'percentage': round((count / len(pixels)) * 100, 2)
            })

        analyzed[region_name] = top_colors

    return analyzed

def describe_color_advanced(r, g, b):
    """Advanced color description with more precision."""
    r, g, b = int(r), int(g), int(b)

    # Very dark/black
    if r < 40 and g < 40 and b < 40:
        return "black"

    # Very light/white
    if r > 220 and g > 220 and b > 220:
        return "white"

    # Grays
    if abs(r - g) < 25 and abs(g - b) < 25:
        if r < 80:
            return "dark gray"
        elif r < 140:
            return "medium gray"
        elif r < 200:
            return "light gray"
        else:
            return "very light gray"

    # Browns (multiple shades)
    if r > g and g > b and r - b > 30:
        if r > 160:
            return "light brown"
        elif r > 100:
            return "brown"
        else:
            return "dark brown"

    # Tans/beiges
    if 150 < r < 240 and 120 < g < 220 and 80 < b < 180:
        if r > g > b and r - b < 80:
            return "tan"

    # Reds/oranges
    if r > 120 and r > g + 30:
        if g > 80 and b < 80:
            return "orange"
        elif g > 100:
            return "orange-red"
        else:
            return "red"

    # Yellows/golds
    if r > 180 and g > 150 and b < 120:
        if abs(r - g) < 40:
            return "yellow"
        else:
            return "golden"

    # Pinks
    if r > 180 and g < 180 and b > 100:
        return "pink"

    # Purples/magentas
    if r > 80 and b > 80 and r > g and b > g:
        if abs(r - b) < 40:
            return "purple"
        elif r > b:
            return "magenta"
        else:
            return "violet"

    # Blues (multiple shades)
    if b > r + 25 and b > g + 15:
        if b > 180:
            return "bright blue"
        elif b > 120:
            return "blue"
        else:
            return "dark blue"

    # Cyans/aquas
    if b > 100 and g > 100:
        if abs(b - g) < 40:
            if b > 180:
                return "bright cyan"
            else:
                return "cyan"

    # Greens
    if g > r + 25 and g > b + 25:
        if g > 180:
            return "bright green"
        elif g > 120:
            return "green"
        else:
            return "dark green"

    return f"mixed-{r}-{g}-{b}"

def detect_hair_style(hair_regions):
    """Detect hair style from multiple hair regions."""
    styles = []

    # Check if afro (lots of volume on top and sides)
    if hair_regions.get('hair_top') and hair_regions.get('hair_left') and hair_regions.get('hair_right'):
        if len(hair_regions['hair_left']) > 2 and len(hair_regions['hair_right']) > 2:
            styles.append("afro")

    # Check if long (extends down sides)
    if hair_regions.get('hair_left') and hair_regions.get('hair_right'):
        if len(hair_regions['hair_left']) > 3 or len(hair_regions['hair_right']) > 3:
            styles.append("long")

    # Default descriptions
    if not styles:
        if hair_regions.get('hair_top'):
            if len(hair_regions['hair_top']) > 2:
                styles.append("fluffy")
            else:
                styles.append("short")

    return " ".join(styles) if styles else "short"

def detect_accessories(regions, current_caption=""):
    """Detect accessories from image regions and current caption."""
    accessories = []

    # Check for sunglasses (often mentioned in caption)
    if "sunglasses" in current_caption.lower():
        accessories.append("wearing sunglasses")

    # Check for earrings (bright colors in earring regions)
    left_ear = regions.get('earrings_left', [])
    right_ear = regions.get('earrings_right', [])

    if left_ear and left_ear[0]['percentage'] > 5:
        # Significant color in earring area
        if "earring" not in current_caption.lower():
            accessories.append(f"wearing {describe_color_advanced(*left_ear[0]['rgb'])} earrings")
        else:
            accessories.append("wearing earrings")

    # Check caption for other accessories
    if "crown" in current_caption.lower():
        accessories.append("wearing crown")
    if "hat" in current_caption.lower():
        accessories.append("wearing hat")
    if "bandana" in current_caption.lower():
        accessories.append("wearing bandana")

    return accessories

def generate_comprehensive_caption(filename, palette, regions, current_caption=""):
    """Generate the most comprehensive caption possible."""

    # Determine gender
    gender = "lad" if "lad_" in filename else "lady"

    # Hair analysis
    hair_colors = regions.get('hair_top', [])
    hair_color = describe_color_advanced(*hair_colors[0]['rgb']) if hair_colors else "unknown"
    hair_style = detect_hair_style(regions)

    # Eye analysis (if not wearing sunglasses)
    wearing_sunglasses = "sunglasses" in current_caption.lower()
    eye_left = regions.get('eyes_left', [])
    eye_right = regions.get('eyes_right', [])

    # Use both eyes to determine color
    eye_colors = []
    if eye_left:
        eye_colors.append(describe_color_advanced(*eye_left[0]['rgb']))
    if eye_right:
        eye_colors.append(describe_color_advanced(*eye_right[0]['rgb']))

    # Most common eye color
    eye_color = max(set(eye_colors), key=eye_colors.count) if eye_colors else "unknown"

    # Skin analysis
    skin_region = regions.get('face_center', [])
    skin_rgb = skin_region[0]['rgb'] if skin_region else [200, 150, 120]

    if skin_rgb[0] > 180:
        skin_tone = "light"
    elif skin_rgb[0] > 120:
        skin_tone = "tan"
    else:
        skin_tone = "dark"

    # Background analysis
    bg_colors = []
    for corner in ['background_top_left', 'background_top_right', 'background_bottom_left', 'background_bottom_right']:
        if corner in regions and regions[corner]:
            bg_colors.append(regions[corner][0])

    # Most common background color
    if bg_colors:
        bg_hex = max(set(c['hex'] for c in bg_colors), key=[c['hex'] for c in bg_colors].count)
        bg_rgb = [c['rgb'] for c in bg_colors if c['hex'] == bg_hex][0]
        bg_color = describe_color_advanced(*bg_rgb)
    else:
        bg_hex = palette[0]['hex']
        bg_color = describe_color_advanced(*palette[0]['rgb'])

    # Accessories
    accessories = detect_accessories(regions, current_caption)

    # Build caption parts
    parts = []
    parts.append("pixel art, 24x24")
    parts.append(f"portrait of bespoke punk {gender}")

    # Hair
    if hair_style and hair_color:
        parts.append(f"{hair_color} {hair_style} hair")

    # Accessories
    for acc in accessories:
        parts.append(acc)

    # Eyes (only if not wearing sunglasses)
    if not wearing_sunglasses and eye_color != "unknown":
        parts.append(f"{eye_color} eyes")

    # Skin
    parts.append(f"{skin_tone} skin")

    # Background
    parts.append(f"{bg_color} solid background ({bg_hex})")

    # Add palette colors
    top_5_colors = [c['hex'] for c in palette[:5]]
    parts.append(f"palette: {', '.join(top_5_colors)}")

    # Style
    parts.append("sharp pixel edges, hard color borders, retro pixel art style")

    return ", ".join(parts)

print("="*100)
print("DEEP COMPREHENSIVE CAPTION ANALYSIS")
print("="*100)
print("Extracting EVERY detail from each punk...")
print()

comprehensive_data = []

for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    # Get current caption
    current_caption = ""
    if os.path.exists(txt_path):
        with open(txt_path, 'r') as f:
            current_caption = f.read().strip()

    print(f"Analyzing: {png_file}")

    # Extract full palette
    palette = get_full_palette(png_path, 15)

    # Analyze all regions
    regions = analyze_regions_detailed(png_path)

    # Generate comprehensive caption
    ai_caption = generate_comprehensive_caption(png_file, palette, regions, current_caption)

    # Create comprehensive entry
    entry = {
        'filename': png_file,
        'currentCaption': current_caption,
        'aiComprehensiveCaption': ai_caption,
        'fullPalette15': palette,
        'regionAnalysis': regions,
        'detectedTraits': {
            'hairColor': describe_color_advanced(*regions['hair_top'][0]['rgb']) if regions.get('hair_top') else None,
            'eyeColorLeft': describe_color_advanced(*regions['eyes_left'][0]['rgb']) if regions.get('eyes_left') else None,
            'eyeColorRight': describe_color_advanced(*regions['eyes_right'][0]['rgb']) if regions.get('eyes_right') else None,
            'skinTone': describe_color_advanced(*regions['face_center'][0]['rgb']) if regions.get('face_center') else None,
            'backgroundColor': describe_color_advanced(*regions['background_top_left'][0]['rgb']) if regions.get('background_top_left') else None,
        },
        'userApproved': False,
        'userEdits': '',
        'finalCaption': ''
    }

    comprehensive_data.append(entry)

print()
print(f"✓ Analyzed {len(comprehensive_data)} images")
print()

# Save comprehensive data
with open('comprehensive_captions_for_review.json', 'w') as f:
    json.dump(comprehensive_data, f, indent=2)

print("✓ Saved: comprehensive_captions_for_review.json")
print()
print("This file contains:")
print("  - Full 15-color palette for each punk")
print("  - Detailed region analysis (hair, eyes, skin, accessories, background)")
print("  - AI-generated comprehensive captions")
print("  - Current captions for comparison")
print()
print("Ready for your review!")
