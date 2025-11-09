#!/usr/bin/env python3
"""
Prepare validation data for UI - pre-fill captions based on current analysis.
User just reviews and corrects rather than starting from scratch.
"""

import os
import json
from PIL import Image
import numpy as np
from collections import Counter
import re
import base64
from io import BytesIO

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def get_image_palette(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)

    color_counts = Counter(tuple(int(c) for c in p) for p in pixels)
    palette = []

    for (r, g, b), count in color_counts.most_common(10):
        percentage = (count / len(pixels)) * 100
        palette.append({
            'hex': rgb_to_hex(r, g, b),
            'rgb': [r, g, b],
            'percentage': round(percentage, 1)
        })

    return palette

def image_to_base64(image_path):
    """Convert image to base64 for embedding in JSON."""
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def extract_caption_attrs(caption):
    """Extract current caption attributes."""
    attrs = {}

    # Hair
    hair_match = re.search(r'([\w\s\-/]+?)\s+hair', caption, re.IGNORECASE)
    if hair_match:
        attrs['hair'] = hair_match.group(1).strip()

    # Eyes
    eye_match = re.search(r'([\w\s]+?)\s+eyes', caption, re.IGNORECASE)
    if eye_match:
        attrs['eyes'] = eye_match.group(1).strip()

    # Skin
    skin_match = re.search(r'([\w/\-\s]+?)\s+skin', caption, re.IGNORECASE)
    if skin_match:
        attrs['skin'] = skin_match.group(1).strip()

    # Background
    bg_match = re.search(r'([\w\s]+?)\s+(solid\s+)?background', caption, re.IGNORECASE)
    if bg_match:
        attrs['background'] = bg_match.group(1).strip()

    # Accessories
    accessories = []
    if 'sunglasses' in caption.lower():
        accessories.append('sunglasses')
    if 'earrings' in caption.lower():
        accessories.append('earrings')
    if 'crown' in caption.lower():
        accessories.append('crown')

    attrs['accessories'] = ', '.join(accessories) if accessories else ''

    # Hex colors
    hex_colors = re.findall(r'(#[0-9a-fA-F]{6})', caption)
    attrs['hex_colors'] = hex_colors

    return attrs

print("Preparing validation data for UI...")
print()

validation_data = []
issues_only = []

for png_file in sorted(os.listdir(TRAINING_DIR)):
    if not png_file.endswith('.png'):
        continue

    txt_file = png_file.replace('.png', '.txt')
    png_path = os.path.join(TRAINING_DIR, png_file)
    txt_path = os.path.join(TRAINING_DIR, txt_file)

    if not os.path.exists(txt_path):
        continue

    with open(txt_path, 'r') as f:
        current_caption = f.read().strip()

    # Get image data
    palette = get_image_palette(png_path)
    current_attrs = extract_caption_attrs(current_caption)

    # Create entry
    entry = {
        'filename': png_file,
        'imagePath': png_path,
        # 'imageBase64': image_to_base64(png_path),  # Commented out - makes file huge
        'palette': palette,
        'currentCaption': current_caption,
        'prefilled': {
            'hairColor': current_attrs.get('hair', '').split()[0] if current_attrs.get('hair') else '',
            'hairStyle': ' '.join(current_attrs.get('hair', '').split()[1:]) if current_attrs.get('hair') else '',
            'eyeColor': current_attrs.get('eyes', ''),
            'skinTone': current_attrs.get('skin', ''),
            'backgroundColor': current_attrs.get('background', ''),
            'backgroundHex': current_attrs['hex_colors'][0] if current_attrs.get('hex_colors') else '',
            'accessories': current_attrs.get('accessories', ''),
        },
        'needsReview': True if not current_attrs.get('eyes') else False,
        'notes': ''
    }

    validation_data.append(entry)

    # Filter for items that definitely need review
    if not current_attrs.get('eyes') or 'sunglasses' in current_caption.lower():
        issues_only.append(entry)

print(f"Total images: {len(validation_data)}")
print(f"Images definitely needing review: {len(issues_only)}")
print()

# Save full dataset
with open('validation_data_full.json', 'w') as f:
    json.dump(validation_data, f, indent=2)

print("✓ Saved: validation_data_full.json (all images)")

# Save issues-only dataset
with open('validation_data_issues.json', 'w') as f:
    json.dump(issues_only, f, indent=2)

print(f"✓ Saved: validation_data_issues.json ({len(issues_only)} images)")

# Create sample for testing
sample = validation_data[:5]
with open('validation_data_sample.json', 'w') as f:
    json.dump(sample, f, indent=2)

print("✓ Saved: validation_data_sample.json (5 images for testing)")
print()
print("Ready to use with caption_validation_ui.html!")
print()
print("Files created:")
print("  - validation_data_full.json: All 203 images")
print("  - validation_data_issues.json: Images needing review")
print("  - validation_data_sample.json: 5 sample images")
