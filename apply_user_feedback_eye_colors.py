#!/usr/bin/env python3
"""
Apply User Feedback for Eye Colors

Parse user feedback JSON and extract eye color mentions to apply automatically.
"""

import json
import re
from pathlib import Path

V5_AUTO_DIR = Path("improved_samples_v5_auto")
OUTPUT_DIR = Path("improved_samples_v5")
OUTPUT_DIR.mkdir(exist_ok=True)
FEEDBACK_FILE = Path("improved_samples_v3/review_feedback.json")

def add_eye_color_to_caption(caption, eye_color):
    """Add eye color to caption"""
    if not eye_color.endswith('eyes'):
        eye_color = f"{eye_color} eyes"

    # Insert after expression or before skin
    if 'neutral expression' in caption:
        caption = caption.replace('neutral expression', f'neutral expression, {eye_color}')
    elif 'slight smile' in caption:
        caption = caption.replace('slight smile', f'slight smile, {eye_color}')
    elif ', eyes,' in caption:
        caption = caption.replace(', eyes,', f', {eye_color},')
    else:
        caption = re.sub(r'(,\s*(?:light|medium|dark|tan)\s+(?:light\s+)?(?:skin|green skin))',
                       f', {eye_color}\\1', caption)

    return caption

# Manual mappings from user feedback
eye_color_feedback = {
    'lad_007_titanium.txt': 'dark brown',
    'lad_012_chromium.txt': 'deep blue',  # Already has it but user emphasized
    'lad_013_caramel.txt': None,  # User said missing but didn't specify color
    'lad_014_sugar.txt': 'blue',
}

# Load user feedback JSON
if FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, 'r') as f:
        user_feedback = json.load(f)
else:
    user_feedback = {}

applied_count = 0
unchanged_count = 0

print("🔍 Applying user feedback eye colors...")
print()

for txt_file in sorted(V5_AUTO_DIR.glob("*.txt")):
    with open(txt_file, 'r') as f:
        caption = f.read().strip()

    # Check if this file has eye color feedback
    feedback_key = txt_file.name.replace('.txt', '.png')

    if txt_file.name in eye_color_feedback and eye_color_feedback[txt_file.name]:
        eye_color = eye_color_feedback[txt_file.name]
        caption = add_eye_color_to_caption(caption, eye_color)
        applied_count += 1
        print(f"✅ {txt_file.name}: Applied '{eye_color} eyes' from user feedback")
    else:
        unchanged_count += 1

    # Save to V5
    output_file = OUTPUT_DIR / txt_file.name
    with open(output_file, 'w') as f:
        f.write(caption)

print()
print("=" * 70)
print(f"Applied eye colors from feedback: {applied_count}")
print(f"Unchanged: {unchanged_count}")
print(f"📁 Output: {OUTPUT_DIR}/")
print("=" * 70)
