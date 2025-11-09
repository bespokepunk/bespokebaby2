#!/usr/bin/env python3
"""
Generate AI captions for ALL images based on pixel analysis.
User reviews and edits these instead of starting from scratch.
"""

import os
from PIL import Image
import numpy as np
from collections import Counter
import re
import json

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def analyze_image_regions(image_path):
    """Analyze different regions and return dominant colors."""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Define regions for 24x24 pixel art
    regions = {
        'hair': arr[0:8, :],
        'eyes': arr[8:14, 6:18],
        'skin': arr[10:16, 8:16],
        'background': np.concatenate([
            arr[0:6, 0:6].reshape(-1, 3),
            arr[0:6, 18:24].reshape(-1, 3),
            arr[18:24, 0:6].reshape(-1, 3),
            arr[18:24, 18:24].reshape(-1, 3)
        ]),
        'clothing': arr[16:24, 6:18],
    }

    region_colors = {}
    for region_name, pixels in regions.items():
        if len(pixels.shape) == 3:
            pixels = pixels.reshape(-1, 3)

        color_counts = Counter(tuple(int(c) for c in p) for p in pixels)
        top_3 = []
        for (r, g, b), count in color_counts.most_common(3):
            top_3.append({
                'rgb': (r, g, b),
                'hex': rgb_to_hex(r, g, b),
                'count': count
            })
        region_colors[region_name] = top_3

    return region_colors

def describe_color(r, g, b):
    """Convert RGB to color name."""
    r, g, b = int(r), int(g), int(b)

    if r < 50 and g < 50 and b < 50:
        return "black"
    if r > 200 and g > 200 and b > 200:
        return "white"
    if abs(r - g) < 30 and abs(g - b) < 30:
        if r < 100:
            return "dark gray"
        elif r < 160:
            return "gray"
        else:
            return "light gray"
    if 60 < r < 200 and 40 < g < 140 and 20 < b < 100 and r > g > b:
        return "brown"
    if r > 150 and r > g + 40 and r > b + 40:
        return "orange" if g > 100 else "red"
    if r > 180 and g > 160 and b < 140:
        return "blonde"
    if b > 100 and b > r + 30 and b > g + 20:
        return "blue"
    if b > 100 and g > 100 and abs(b - g) < 50:
        return "cyan"
    if g > 100 and g > r + 30 and g > b + 30:
        return "green"
    if r > 100 and b > 100 and r > g and b > g:
        return "purple"
    if r > 180 and g > 100 and b > 100 and r > b:
        return "pink"

    return "mixed"

def generate_caption_from_analysis(filename, region_colors, current_caption=""):
    """Generate complete caption from pixel analysis."""

    # Detect if lad or lady
    gender = "lad" if "lad_" in filename else "lady"

    # Analyze each region
    hair_color = describe_color(*region_colors['hair'][0]['rgb']) if region_colors['hair'] else "unknown"
    eye_color = describe_color(*region_colors['eyes'][0]['rgb']) if region_colors['eyes'] else "unknown"
    bg_hex = region_colors['background'][0]['hex'] if region_colors['background'] else "#000000"
    bg_color = describe_color(*region_colors['background'][0]['rgb']) if region_colors['background'] else "unknown"

    # Try to preserve style info from current caption
    hair_style = ""
    if current_caption:
        style_match = re.search(r'(fluffy|voluminous|long|short|afro|pixelated)', current_caption, re.IGNORECASE)
        if style_match:
            hair_style = style_match.group(1).lower()

    # Detect skin tone
    skin_rgb = region_colors['skin'][0]['rgb'] if region_colors['skin'] else (200, 150, 120)
    if skin_rgb[0] > 180:
        skin_tone = "light"
    elif skin_rgb[0] > 120:
        skin_tone = "tan"
    else:
        skin_tone = "dark"

    # Check for accessories
    accessories = ""
    if "sunglasses" in current_caption.lower():
        accessories = "wearing sunglasses, "
    elif "earrings" in current_caption.lower():
        accessories = "wearing earrings, "

    # Build caption
    caption_parts = []
    caption_parts.append("pixel art, 24x24")
    caption_parts.append(f"portrait of bespoke punk {gender}")

    # Hair
    if hair_style:
        caption_parts.append(f"{hair_color} {hair_style} hair")
    else:
        caption_parts.append(f"{hair_color} hair")

    # Accessories
    if accessories:
        caption_parts.append(accessories.rstrip(', '))

    # Eyes (only if not wearing sunglasses)
    if "sunglasses" not in current_caption.lower():
        caption_parts.append(f"{eye_color} eyes")

    # Skin
    caption_parts.append(f"{skin_tone} skin")

    # Background
    caption_parts.append(f"{bg_color} solid background ({bg_hex})")

    # Style
    caption_parts.append("sharp pixel edges, hard color borders, retro pixel art style")

    return ", ".join(caption_parts)

print("="*80)
print("GENERATING AI CAPTIONS FOR REVIEW")
print("="*80)
print()

generated_captions = []
comparison_report = []

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

    # Analyze image
    region_colors = analyze_image_regions(png_path)

    # Generate new caption
    ai_caption = generate_caption_from_analysis(png_file, region_colors, current_caption)

    # Create entry for review
    entry = {
        'filename': png_file,
        'currentCaption': current_caption,
        'aiGeneratedCaption': ai_caption,
        'colorPalette': {
            'hair': region_colors['hair'][0]['hex'] if region_colors['hair'] else None,
            'eyes': region_colors['eyes'][0]['hex'] if region_colors['eyes'] else None,
            'background': region_colors['background'][0]['hex'] if region_colors['background'] else None,
        },
        'needsReview': current_caption != ai_caption,
        'userApproved': False,
        'userEdits': '',
        'finalCaption': ''
    }

    generated_captions.append(entry)

    # Show comparison
    if current_caption != ai_caption:
        comparison_report.append(f"\n{png_file}:")
        comparison_report.append(f"  OLD: {current_caption}")
        comparison_report.append(f"  AI:  {ai_caption}")

print(f"Generated captions for {len(generated_captions)} images")
print(f"Changes suggested: {len([e for e in generated_captions if e['needsReview']])}")
print()

# Save for UI
with open('ai_generated_captions.json', 'w') as f:
    json.dump(generated_captions, f, indent=2)

print("✓ Saved: ai_generated_captions.json")

# Save comparison report
with open('caption_comparison_report.txt', 'w') as f:
    f.write('\n'.join(comparison_report))

print("✓ Saved: caption_comparison_report.txt")
print()
print("First 10 comparisons:")
print('\n'.join(comparison_report[:30]))
