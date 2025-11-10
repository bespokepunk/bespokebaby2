#!/usr/bin/env python3
"""
Intelligent Caption Finalizer
Uses sampled hex codes to auto-correct color descriptions and generate perfect captions
"""

import json
import re
from collections import Counter

# Load data
with open('merged_captions_v3_final.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("INTELLIGENT CAPTION FINALIZER - AUTO-CORRECTING COLOR DESCRIPTIONS")
print("=" * 100)
print()

def hex_to_accurate_description(hex_code):
    """Convert hex code to accurate color description"""
    # Remove # if present
    hex_code = hex_code.strip('#')

    # Convert to RGB
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    # Calculate properties
    brightness = (r + g + b) / 3
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    saturation = max_c - min_c

    # Grayscale detection
    if saturation < 25:
        if brightness > 230: return "white"
        elif brightness > 200: return "very light gray"
        elif brightness > 170: return "light gray"
        elif brightness > 130: return "medium gray"
        elif brightness > 90: return "dark gray"
        elif brightness > 40: return "very dark gray"
        else: return "black"

    # Determine dominant color channel
    if r >= g and r >= b:
        # Red dominant
        if r > 200 and g < 100 and b < 100:
            return "bright red" if brightness > 150 else "red"
        elif r > g + 40 and r > b + 40:
            if brightness > 180: return "light red"
            elif brightness > 120: return "red"
            else: return "dark red"
        elif r > g + 20 and g > b + 20:
            # Orange/brown range
            if saturation < 40: return "light brown"
            if brightness > 200: return "light orange"
            elif brightness > 160: return "orange"
            elif brightness > 120: return "light brown"
            elif brightness > 80: return "brown"
            else: return "dark brown"
        elif r > b + 30 and abs(r - g) < 40:
            # Pink range
            if brightness > 220: return "light pink"
            elif brightness > 180: return "pink"
            else: return "dark pink"

    elif g >= r and g >= b:
        # Green dominant
        if g > 200 and r < 130 and b < 130:
            return "bright green" if g > 220 else "light green"
        elif g > r + 40 and g > b + 40:
            if brightness > 180: return "light green"
            elif brightness > 120: return "green"
            else: return "dark green"
        elif g > b + 20 and abs(g - r) < 40:
            # Yellow/olive range
            if brightness > 200: return "light yellow"
            elif brightness > 160: return "yellow"
            elif brightness > 120: return "olive"
            else: return "dark olive"

    elif b >= r and b >= g:
        # Blue dominant
        if b > 200 and r < 130 and g < 130:
            return "bright blue" if b > 220 else "light blue"
        elif b > r + 40 and b > g + 40:
            if brightness > 180: return "light blue"
            elif brightness > 120: return "blue"
            else: return "dark blue"
        elif b > r + 20 and abs(b - g) < 40:
            # Cyan range
            if brightness > 200: return "bright cyan"
            elif brightness > 150: return "cyan"
            else: return "dark cyan"
        elif b > g + 20 and abs(b - r) < 40:
            # Purple range
            if brightness > 200: return "light purple"
            elif brightness > 150: return "purple"
            else: return "dark purple"

    # Fallback - use brightness
    if brightness > 180: return "light"
    elif brightness > 100: return "medium"
    else: return "dark"

def generate_clean_caption(record):
    """Generate clean, accurate caption using sampled hex codes"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors', {})

    # Determine gender
    gender = "lady" if filename.startswith("lady_") else "lad"

    # Start with base
    parts = ["pixel art, 24x24", f"portrait of bespoke punk {gender}"]

    # Parse user corrections for structure
    user_lower = user_corr.lower()

    # === HAIR ===
    hair_region = sampled.get('hair_top', [])
    if hair_region:
        dominant_hair = hair_region[0]
        hair_hex = dominant_hair['hex']
        hair_color_accurate = hex_to_accurate_description(hair_hex)

        # Extract hair style from user text
        hair_styles = []
        if 'afro' in user_lower:
            hair_styles.append('afro')
        if 'curly' in user_lower or 'wavy' in user_lower:
            hair_styles.append('curly')
        if 'long' in user_lower and 'hair' in user_lower:
            hair_styles.append('long')
        if 'short' in user_lower and 'hair' in user_lower:
            hair_styles.append('short')
        if 'mohawk' in user_lower:
            hair_styles.append('mohawk')
        if 'side-swept' in user_lower or 'side swept' in user_lower:
            hair_styles.append('side-swept')
        if 'parted' in user_lower:
            hair_styles.append('parted')
        if 'buzzed' in user_lower:
            hair_styles.append('buzzed')
        if 'bald' in user_lower or 'no hair' in user_lower:
            hair_styles.append('bald')

        # Build hair description
        if hair_styles:
            if 'bald' in hair_styles:
                # Don't add hair color if bald
                pass
            else:
                hair_desc = f"{hair_color_accurate} {' '.join(hair_styles)} hair"
                parts.append(hair_desc)
        else:
            parts.append(f"{hair_color_accurate} hair")

    # === ACCESSORIES (HEADWEAR, SUNGLASSES) ===
    accessories = []
    if 'hat' in user_lower or 'cap' in user_lower or 'crown' in user_lower or 'bucket hat' in user_lower:
        # Extract hat description from user text
        hat_match = re.search(r'([\w\s]+?(?:hat|cap|crown))', user_lower)
        if hat_match:
            accessories.append(f"wearing {hat_match.group(1).strip()}")

    if 'sunglasses' in user_lower or 'shades' in user_lower:
        # Extract sunglasses description
        sunglass_match = re.search(r'([\w\s]+?(?:sunglasses|shades))', user_lower)
        if sunglass_match:
            accessories.append(f"wearing {sunglass_match.group(1).strip()}")
    elif 'glasses' in user_lower:
        # Regular glasses
        glasses_match = re.search(r'([\w\s]+?glasses)', user_lower)
        if glasses_match:
            accessories.append(f"wearing {glasses_match.group(1).strip()}")

    if accessories:
        parts.extend(accessories)

    # === FACIAL HAIR ===
    if 'stubble' in user_lower:
        parts.append('wearing stubble')
    elif 'beard' in user_lower:
        parts.append('wearing beard')
    elif 'mustache' in user_lower or 'moustache' in user_lower:
        parts.append('wearing mustache')

    # === EYES (only if not covered by sunglasses) ===
    has_sunglasses = 'sunglasses' in user_lower or 'shades' in user_lower
    if not has_sunglasses:
        eyes_region = sampled.get('eyes_left', []) or sampled.get('eyes_right', [])
        if eyes_region:
            dominant_eye = eyes_region[0]
            eye_hex = dominant_eye['hex']
            eye_color_accurate = hex_to_accurate_description(eye_hex)
            parts.append(f"{eye_color_accurate} eyes ({eye_hex})")

    # === LIPS ===
    mouth_region = sampled.get('mouth', [])
    if mouth_region and gender == "lady":
        dominant_lip = mouth_region[0]
        lip_hex = dominant_lip['hex']
        lip_color_accurate = hex_to_accurate_description(lip_hex)
        parts.append(f"{lip_color_accurate} lips ({lip_hex})")

    # === SKIN ===
    face_region = sampled.get('face_center', [])
    if face_region:
        dominant_skin = face_region[0]
        skin_hex = dominant_skin['hex']
        skin_color_accurate = hex_to_accurate_description(skin_hex)

        # Enhance skin description with user's specific terms
        if 'light skin' in user_lower or 'pale' in user_lower:
            skin_desc = f"light skin ({skin_hex})"
        elif 'medium skin' in user_lower or 'tan' in user_lower:
            skin_desc = f"medium skin ({skin_hex})"
        elif 'dark skin' in user_lower or 'brown skin' in user_lower:
            skin_desc = f"dark skin ({skin_hex})"
        else:
            skin_desc = f"{skin_color_accurate} skin ({skin_hex})"

        parts.append(skin_desc)

    # === BACKGROUND ===
    bg_corners = sampled.get('bg_top_left', [])
    if bg_corners:
        dominant_bg = bg_corners[0]
        bg_hex = dominant_bg['hex']
        bg_color_accurate = hex_to_accurate_description(bg_hex)

        # Detect pattern from user text
        if 'checkered' in user_lower or 'checker' in user_lower:
            parts.append(f"{bg_color_accurate} checkered background ({bg_hex})")
        elif 'gradient' in user_lower:
            parts.append(f"{bg_color_accurate} gradient background ({bg_hex})")
        elif 'split' in user_lower:
            if 'horizontal' in user_lower:
                parts.append(f"{bg_color_accurate} split-horizontal background ({bg_hex})")
            elif 'vertical' in user_lower:
                parts.append(f"{bg_color_accurate} split-vertical background ({bg_hex})")
            else:
                parts.append(f"{bg_color_accurate} split background ({bg_hex})")
        else:
            parts.append(f"{bg_color_accurate} solid background ({bg_hex})")

    # === CLOTHING ===
    clothing_region = sampled.get('clothing_top', [])
    if clothing_region:
        dominant_clothing = clothing_region[0]
        clothing_hex = dominant_clothing['hex']
        clothing_color_accurate = hex_to_accurate_description(clothing_hex)

        # Extract clothing type from user text
        clothing_type = None
        if 'hoodie' in user_lower:
            clothing_type = 'hoodie'
        elif 'jacket' in user_lower:
            clothing_type = 'jacket'
        elif 'suit' in user_lower:
            clothing_type = 'suit'
        elif 'shirt' in user_lower:
            clothing_type = 'shirt'
        elif 'coat' in user_lower:
            clothing_type = 'coat'

        if clothing_type:
            parts.append(f"{clothing_color_accurate} {clothing_type}")
        else:
            parts.append(f"{clothing_color_accurate} clothing")

    # === PALETTE (top 5 hex codes) ===
    all_colors = sampled.get('hair_top', []) + sampled.get('face_center', []) + \
                 sampled.get('bg_top_left', []) + sampled.get('clothing_top', [])

    # Get unique hexes
    seen_hexes = set()
    palette_hexes = []
    for region_colors in [sampled.get('hair_top', []), sampled.get('face_center', []),
                          sampled.get('bg_top_left', []), sampled.get('clothing_top', [])]:
        for color_info in region_colors[:2]:  # Top 2 from each region
            hex_val = color_info.get('hex', '')
            if hex_val and hex_val not in seen_hexes:
                palette_hexes.append(hex_val)
                seen_hexes.add(hex_val)
                if len(palette_hexes) >= 5:
                    break
        if len(palette_hexes) >= 5:
            break

    if palette_hexes:
        parts.append(f"palette: {', '.join(palette_hexes)}")

    # === STYLE TAGS ===
    parts.extend(["sharp pixel edges", "hard color borders", "retro pixel art style"])

    # Join all parts
    caption = ", ".join(parts)

    return caption

print("🎨 Generating intelligent captions with accurate color descriptions...\n")

final_records = []
changes = 0

for idx, record in enumerate(records, 1):
    filename = record['filename']

    # Generate intelligent caption
    intelligent_caption = generate_clean_caption(record)

    # Compare to previous
    previous = record.get('merged_caption_v3_final', '')
    if intelligent_caption != previous:
        changes += 1

    # Save
    record['merged_caption_intelligent'] = intelligent_caption
    final_records.append(record)

    if idx <= 5 or idx % 50 == 0:
        print(f"  [{idx}/203] {filename}")

print(f"\n✓ Generated 203 intelligent captions ({changes} improved)\n")

# Save
with open('merged_captions_intelligent.json', 'w') as f:
    json.dump(final_records, f, indent=2)

print(f"💾 Saved to: merged_captions_intelligent.json")
print()

# Show examples
print("=" * 100)
print("EXAMPLES OF INTELLIGENT CAPTIONS")
print("=" * 100)
print()

for i in [0, 1, 2, 50, 100, 150]:
    record = final_records[i]
    print(f"{record['filename']}:")
    print(f"  {record['merged_caption_intelligent']}")
    print()

print("✅ Intelligent caption generation complete!")
print()
print("These captions use ACTUAL sampled hex codes with accurate color descriptions")
print()
