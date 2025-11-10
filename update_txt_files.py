#!/usr/bin/env python3
"""
Update all .txt files with final accurate captions
"""

import json
import re

# Load FIXED sampling data
with open('supabase_export_FIXED_SAMPLING.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("UPDATING ALL 203 .TXT FILES WITH FINAL ACCURATE CAPTIONS")
print("=" * 100)
print()

def extract_user_trait(user_text, trait_type):
    """Extract specific trait from user text"""
    user_lower = user_text.lower()

    if trait_type == 'eyes':
        eye_patterns = [
            r'(very dark brown|dark brown|light brown|medium brown|brown|'
            r'very light blue|light blue|dark blue|medium blue|blue|'
            r'bright green|light green|dark green|green|'
            r'red|gray|grey|black|hazel|amber)\s+eyes',
        ]
        for pattern in eye_patterns:
            match = re.search(pattern, user_lower)
            if match:
                return match.group(1)

    elif trait_type == 'skin':
        skin_patterns = [
            r'(very light|light|medium|tan|dark|brown|pale|fair)\s+(?:skin|skinned|tone)',
            r'(light|medium|dark)\s+skinned',
        ]
        for pattern in skin_patterns:
            match = re.search(pattern, user_lower)
            if match:
                return match.group(1)

    return None

def build_final_caption(record):
    """Build final caption with user descriptions + CORRECT hex codes"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors_FIXED', {})

    user_lower = user_corr.lower()
    gender = "lady" if filename.startswith("lady_") else "lad"

    parts = ["pixel art, 24x24", f"portrait of bespoke punk {gender}"]

    # HAIR
    hair_region = sampled.get('hair_top', [])
    if 'bald' in user_lower or 'no hair' in user_lower:
        parts.append("bald")
    elif hair_region:
        hair_hex = hair_region[0]['hex']
        # Check if user specified hair color
        user_hair_match = re.search(r'([\w\s]+)\s+hair', user_lower)
        if user_hair_match:
            parts.append(f"{user_hair_match.group(1).strip()} hair ({hair_hex})")
        else:
            parts.append(f"hair ({hair_hex})")

    # HEADWEAR
    if 'hat' in user_lower or 'cap' in user_lower or 'crown' in user_lower:
        hat_match = re.search(r'((?:[\w\s]+\s)?(?:hat|cap|crown))', user_lower, re.IGNORECASE)
        if hat_match:
            parts.append(f"wearing {hat_match.group(1).strip()}")

    # SUNGLASSES
    has_sunglasses = False
    if 'sunglasses' in user_lower or 'shades' in user_lower:
        sg_match = re.search(r'((?:[\w\s]+\s)?(?:sunglasses|shades))', user_lower, re.IGNORECASE)
        if sg_match:
            parts.append(f"wearing {sg_match.group(1).strip()}")
            has_sunglasses = True
    elif 'glasses' in user_lower:
        g_match = re.search(r'((?:[\w\s]+\s)?glasses)', user_lower, re.IGNORECASE)
        if g_match:
            parts.append(f"wearing {g_match.group(1).strip()}")

    # FACIAL HAIR
    if 'stubble' in user_lower:
        parts.append('wearing stubble')
    elif 'beard' in user_lower:
        parts.append('wearing beard')
    elif 'mustache' in user_lower:
        parts.append('wearing mustache')

    # EYES (if not covered)
    if not has_sunglasses:
        user_eye_color = extract_user_trait(user_corr, 'eyes')
        eyes_region = sampled.get('eyes_left', []) or sampled.get('eyes_right', [])
        if eyes_region:
            eye_hex = eyes_region[0]['hex']
            if user_eye_color:
                parts.append(f"{user_eye_color} eyes ({eye_hex})")
            else:
                parts.append(f"eyes ({eye_hex})")

    # LIPS (ladies)
    if gender == "lady":
        mouth_region = sampled.get('mouth', [])
        if mouth_region:
            lip_hex = mouth_region[0]['hex']
            parts.append(f"lips ({lip_hex})")

    # SKIN
    user_skin = extract_user_trait(user_corr, 'skin')
    face_region = sampled.get('face_center', [])
    if face_region:
        skin_hex = face_region[0]['hex']
        if user_skin:
            parts.append(f"{user_skin} skin ({skin_hex})")
        else:
            parts.append(f"skin ({skin_hex})")

    # BACKGROUND
    bg_region = sampled.get('bg_top_left', [])
    if bg_region:
        bg_hex = bg_region[0]['hex']
        pattern = "solid"
        if 'checkered' in user_lower or 'checker' in user_lower:
            pattern = "checkered"
        elif 'gradient' in user_lower:
            pattern = "gradient"
        elif 'split' in user_lower:
            if 'horizontal' in user_lower:
                pattern = "split-horizontal"
            elif 'vertical' in user_lower:
                pattern = "split-vertical"
            else:
                pattern = "split"

        parts.append(f"{pattern} background ({bg_hex})")

    # CLOTHING
    clothing_region = sampled.get('clothing_top', [])
    if clothing_region:
        clothing_hex = clothing_region[0]['hex']
        clothing_type = None
        if 'hoodie' in user_lower:
            clothing_type = 'hoodie'
        elif 'jacket' in user_lower:
            clothing_type = 'jacket'
        elif 'suit' in user_lower:
            clothing_type = 'suit'
        elif 'shirt' in user_lower:
            clothing_type = 'shirt'

        if clothing_type:
            parts.append(f"{clothing_type} ({clothing_hex})")
        else:
            parts.append(f"clothing ({clothing_hex})")

    # PALETTE (top 5 unique hexes)
    palette_hexes = []
    for region_name in ['hair_top', 'eyes_left', 'face_center', 'bg_top_left', 'clothing_top']:
        region = sampled.get(region_name, [])
        if region:
            hex_val = region[0]['hex']
            if hex_val not in palette_hexes:
                palette_hexes.append(hex_val)
                if len(palette_hexes) >= 5:
                    break

    if palette_hexes:
        parts.append(f"palette: {', '.join(palette_hexes)}")

    parts.extend(["sharp pixel edges", "hard color borders", "retro pixel art style"])

    return ", ".join(parts)

# Generate and update
updated = 0
errors = []

for record in records:
    filename = record['filename']
    caption = build_final_caption(record)

    if not caption:
        errors.append(f"{filename}: No caption generated")
        continue

    # Get txt path
    txt_path = f"civitai_v2_7_training/{filename.replace('.png', '.txt')}"

    try:
        # Write caption
        with open(txt_path, 'w') as f:
            f.write(caption)
        updated += 1

        if updated <= 5 or updated % 50 == 0:
            print(f"  [{updated}/203] {filename}")
            if updated <= 3:
                print(f"    {caption[:150]}...")

    except Exception as e:
        errors.append(f"{filename}: {e}")

print(f"\n✓ Updated {updated} caption files")

if errors:
    print(f"\n⚠️  {len(errors)} errors:")
    for err in errors[:10]:
        print(f"  - {err}")

print()
print("✅ All .txt files updated with final accurate captions!")
print()
