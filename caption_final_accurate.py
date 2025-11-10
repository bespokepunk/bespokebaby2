#!/usr/bin/env python3
"""
Final Accurate Captions
Priority: USER's color descriptions + sampled hex codes for accuracy
"""

import json
import re

# Load data
with open('merged_captions_v3_final.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("FINAL ACCURATE CAPTION GENERATION")
print("Priority: User descriptions + Hex codes from actual pixels")
print("=" * 100)
print()

def extract_user_trait(user_text, trait_type):
    """Extract specific trait description from user's text"""
    user_lower = user_text.lower()

    if trait_type == 'eyes':
        # Look for eye color mentions
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

    elif trait_type == 'hair_color':
        # Look for hair color
        hair_patterns = [
            r'(very dark brown|dark brown|light brown|medium brown|brown|black|'
            r'blonde|dirty blonde|sandy|red|auburn|gray|grey|white|silver)\s+(?:hair|afro|curly)',
            r'(afro|curly|long|short|wavy|buzzed|mohawk|bald)',
        ]
        colors = []
        for pattern in hair_patterns:
            matches = re.findall(pattern, user_lower)
            colors.extend(matches)
        return ' '.join(colors) if colors else None

    elif trait_type == 'skin':
        # Look for skin tone
        skin_patterns = [
            r'(very light|light|medium|tan|dark|brown|pale|fair)\s+(?:skin|skinned|tone)',
            r'(light|medium|dark)\s+skinned',
        ]
        for pattern in skin_patterns:
            match = re.search(pattern, user_lower)
            if match:
                return match.group(1)

    elif trait_type == 'background':
        # Look for background
        bg_patterns = [
            r'([\w\s]+?)\s+(?:checkered|checker)\s+(?:background|backdrop)',
            r'([\w\s]+?)\s+(?:gradient|split)\s+(?:background|backdrop)',
            r'([\w\s]+?)\s+(?:solid\s+)?(?:background|backdrop)',
            r'background\s+is\s+([\w\s]+)',
        ]
        for pattern in bg_patterns:
            match = re.search(pattern, user_lower)
            if match:
                return match.group(1).strip()

    return None

def clean_and_structure_caption(record):
    """Create clean, structured caption using user's descriptions + hex codes"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors', {})

    user_lower = user_corr.lower()
    gender = "lady" if filename.startswith("lady_") else "lad"

    # Start caption
    parts = ["pixel art, 24x24", f"portrait of bespoke punk {gender}"]

    # === HAIR ===
    user_hair_color = extract_user_trait(user_corr, 'hair_color')
    hair_region = sampled.get('hair_top', [])

    if 'bald' in user_lower or 'no hair' in user_lower:
        parts.append("bald")
    elif user_hair_color or hair_region:
        hair_desc_parts = []

        # Get hex from sampled data
        hair_hex = hair_region[0]['hex'] if hair_region else None

        # Use user's description if available
        if user_hair_color:
            hair_desc_parts.append(user_hair_color)
        elif hair_hex:
            # Fallback to sampled if user didn't specify
            hair_desc_parts.append(hair_region[0]['description'])

        # Add "hair" at the end
        hair_desc_parts.append("hair")

        # Add hex if available
        if hair_hex:
            parts.append(f"{' '.join(hair_desc_parts)} ({hair_hex})")
        else:
            parts.append(' '.join(hair_desc_parts))

    # === HEADWEAR ===
    if 'hat' in user_lower or 'cap' in user_lower or 'crown' in user_lower:
        hat_match = re.search(r'((?:[\w\s]+\s)?(?:hat|cap|crown))', user_lower, re.IGNORECASE)
        if hat_match:
            parts.append(f"wearing {hat_match.group(1).strip()}")

    # === SUNGLASSES / GLASSES ===
    has_sunglasses = False
    if 'sunglasses' in user_lower or 'shades' in user_lower:
        sunglass_match = re.search(r'((?:[\w\s]+\s)?(?:sunglasses|shades))', user_lower, re.IGNORECASE)
        if sunglass_match:
            parts.append(f"wearing {sunglass_match.group(1).strip()}")
            has_sunglasses = True
    elif 'glasses' in user_lower:
        glasses_match = re.search(r'((?:[\w\s]+\s)?glasses)', user_lower, re.IGNORECASE)
        if glasses_match:
            parts.append(f"wearing {glasses_match.group(1).strip()}")

    # === FACIAL HAIR ===
    if 'stubble' in user_lower:
        parts.append('wearing stubble')
    elif 'beard' in user_lower:
        parts.append('wearing beard')
    elif 'mustache' in user_lower or 'moustache' in user_lower:
        parts.append('wearing mustache')

    # === EYES (only if not wearing sunglasses) ===
    if not has_sunglasses:
        user_eye_color = extract_user_trait(user_corr, 'eyes')
        eyes_region = sampled.get('eyes_left', []) or sampled.get('eyes_right', [])

        if user_eye_color or eyes_region:
            eye_hex = eyes_region[0]['hex'] if eyes_region else None

            if user_eye_color:
                # User specified - use their description
                if eye_hex:
                    parts.append(f"{user_eye_color} eyes ({eye_hex})")
                else:
                    parts.append(f"{user_eye_color} eyes")
            elif eye_hex:
                # User didn't specify - use sampled
                eye_desc = eyes_region[0]['description']
                parts.append(f"{eye_desc} eyes ({eye_hex})")

    # === LIPS (for ladies) ===
    if gender == "lady":
        mouth_region = sampled.get('mouth', [])
        if mouth_region:
            lip_hex = mouth_region[0]['hex']
            lip_desc = mouth_region[0]['description']
            # Check if user mentioned lips
            if 'lips' in user_lower or 'lip color' in user_lower:
                lip_match = re.search(r'([\w\s]+)\s+lips', user_lower)
                if lip_match:
                    parts.append(f"{lip_match.group(1)} lips ({lip_hex})")
                else:
                    parts.append(f"{lip_desc} lips ({lip_hex})")
            else:
                parts.append(f"{lip_desc} lips ({lip_hex})")

    # === SKIN ===
    user_skin = extract_user_trait(user_corr, 'skin')
    face_region = sampled.get('face_center', [])

    if user_skin or face_region:
        skin_hex = face_region[0]['hex'] if face_region else None

        if user_skin:
            # User specified
            if skin_hex:
                parts.append(f"{user_skin} skin ({skin_hex})")
            else:
                parts.append(f"{user_skin} skin")
        elif skin_hex:
            # User didn't specify
            skin_desc = face_region[0]['description']
            parts.append(f"{skin_desc} skin ({skin_hex})")

    # === BACKGROUND ===
    user_bg = extract_user_trait(user_corr, 'background')
    bg_region = sampled.get('bg_top_left', [])

    if user_bg or bg_region:
        bg_hex = bg_region[0]['hex'] if bg_region else None

        # Determine pattern
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

        if user_bg:
            if bg_hex:
                parts.append(f"{user_bg} {pattern} background ({bg_hex})")
            else:
                parts.append(f"{user_bg} {pattern} background")
        elif bg_hex:
            bg_desc = bg_region[0]['description']
            parts.append(f"{bg_desc} {pattern} background ({bg_hex})")

    # === CLOTHING ===
    clothing_region = sampled.get('clothing_top', [])
    if clothing_region:
        clothing_hex = clothing_region[0]['hex']
        clothing_desc = clothing_region[0]['description']

        # Extract clothing type from user
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
            parts.append(f"{clothing_desc} {clothing_type}")
        else:
            parts.append(f"{clothing_desc} clothing")

    # === PALETTE ===
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

    # === STYLE TAGS ===
    parts.extend(["sharp pixel edges", "hard color borders", "retro pixel art style"])

    return ", ".join(parts)

print("🎨 Generating final accurate captions...\n")

final_records = []

for idx, record in enumerate(records, 1):
    filename = record['filename']

    # Generate caption
    accurate_caption = clean_and_structure_caption(record)

    record['merged_caption_final_accurate'] = accurate_caption
    final_records.append(record)

    if idx <= 10 or idx % 50 == 0:
        print(f"  [{idx}/203] {filename}")

print(f"\n✓ Generated 203 accurate captions\n")

# Save
with open('merged_captions_final_accurate.json', 'w') as f:
    json.dump(final_records, f, indent=2)

print(f"💾 Saved to: merged_captions_final_accurate.json")
print()

# Show examples
print("=" * 100)
print("SAMPLE CAPTIONS")
print("=" * 100)
print()

for i in [0, 1, 2, 10, 50, 100]:
    record = final_records[i]
    print(f"{record['filename']}:")
    print(f"  USER: {record['user_corrections'][:150]}...")
    print(f"  FINAL: {record['merged_caption_final_accurate']}")
    print()

print("✅ Final accurate caption generation complete!")
print("User's color descriptions are preserved, hex codes added for precision")
print()
