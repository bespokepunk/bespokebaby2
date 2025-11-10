#!/usr/bin/env python3
"""
Create STRICTLY TEMPLATED captions - maximum consistency, no variation
Every caption follows the exact same structure
"""

import json
import re

# Load data
with open('supabase_export_FIXED_SAMPLING.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("CREATING STRICTLY TEMPLATED CAPTIONS - MAXIMUM CONSISTENCY")
print("=" * 100)
print()

def hex_to_color_name(hex_code):
    """Convert hex to consistent color name"""
    hex_code = hex_code.strip('#')
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    brightness = (r + g + b) / 3
    saturation = max(r, g, b) - min(r, g, b)

    # Grayscale
    if saturation < 25:
        if brightness > 220: return "white"
        elif brightness > 180: return "very light gray"
        elif brightness > 140: return "light gray"
        elif brightness > 100: return "medium gray"
        elif brightness > 60: return "dark gray"
        else: return "black"

    # Colors
    if r > g and r > b:
        if g > b + 20:  # Orange/brown
            if brightness > 160: return "light orange"
            elif brightness > 120: return "orange"
            elif brightness > 90: return "light brown"
            else: return "dark brown"
        else:  # Red/pink
            if brightness > 180: return "light pink"
            elif brightness > 140: return "pink"
            else: return "red"
    elif g > r and g > b:
        if r > b + 20:  # Yellow
            if brightness > 160: return "light yellow"
            else: return "yellow"
        else:  # Green
            if brightness > 180: return "light green"
            elif brightness > 120: return "green"
            else: return "dark green"
    elif b > r and b > g:
        if g > r + 20:  # Cyan
            if brightness > 160: return "light cyan"
            else: return "cyan"
        elif r > g + 20:  # Purple
            if brightness > 160: return "light purple"
            else: return "purple"
        else:  # Blue
            if brightness > 180: return "light blue"
            elif brightness > 120: return "blue"
            else: return "dark blue"

    return "mixed color"

def extract_hair_style(user_text):
    """Extract consistent hair style"""
    user_lower = user_text.lower()
    styles = []

    # Check for specific styles
    if 'afro' in user_lower:
        return "afro"
    elif 'beehive' in user_lower:
        return "beehive updo"
    elif 'mohawk' in user_lower:
        return "mohawk"
    elif 'powdered hair' in user_lower or '18th century' in user_lower or 'colonial' in user_lower:
        return "pulled back colonial style"
    elif 'modern haircut' in user_lower or 'textured top' in user_lower:
        return "short modern"
    elif 'voluminous messy' in user_lower or 'big' in user_lower and 'hair' in user_lower:
        return "voluminous messy"
    elif 'long' in user_lower:
        if 'wavy' in user_lower or 'curly' in user_lower:
            return "long wavy"
        return "long"
    elif 'short' in user_lower:
        return "short"
    elif 'buzzed' in user_lower:
        return "buzzed"
    elif 'curly' in user_lower or 'wavy' in user_lower:
        return "curly"
    elif 'side-swept' in user_lower or 'side swept' in user_lower:
        return "side-swept"
    elif 'parted' in user_lower:
        return "parted"

    return "medium length"

def create_templated_caption(record):
    """Create STRICTLY templated caption"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors_FIXED', {})

    user_lower = user_corr.lower()
    gender = "lady" if filename.startswith("lady_") else "lad"

    # Start with template
    parts = []

    # BASE
    parts.append("pixel art, 24x24")
    parts.append(f"portrait of bespoke punk {gender}")

    # HAIR - ALWAYS present
    hair_region = sampled.get('hair_top', [])
    if hair_region:
        hair_hex = hair_region[0]['hex']

        # Get hair color - prefer user description
        user_hair_match = re.search(r'([\w\s-]+)\s+hair', user_corr, re.IGNORECASE)
        if user_hair_match:
            hair_color = user_hair_match.group(1).strip()
        else:
            hair_color = hex_to_color_name(hair_hex)

        # Get hair style
        hair_style = extract_hair_style(user_corr)

        if 'bald' in user_lower or 'no hair' in user_lower:
            parts.append("bald")
        else:
            parts.append(f"{hair_color} {hair_style} hair ({hair_hex})")

    # ACCESSORIES - standardized format
    accessories = []

    # Hat/cap/crown
    if 'crown' in user_lower:
        accessories.append("wearing crown")
    elif 'hat' in user_lower or 'cap' in user_lower:
        if 'bucket hat' in user_lower:
            accessories.append("wearing bucket hat")
        elif 'hooded cap' in user_lower:
            accessories.append("wearing hooded cap")
        else:
            accessories.append("wearing hat")

    # Sunglasses
    if 'sunglasses' in user_lower or 'shades' in user_lower:
        accessories.append("wearing sunglasses")
    elif 'glasses' in user_lower:
        accessories.append("wearing glasses")

    # Flower
    if 'flower' in user_lower:
        accessories.append("wearing flower in hair")

    # Facial hair
    if 'stubble' in user_lower:
        accessories.append("wearing stubble")
    elif 'beard' in user_lower:
        accessories.append("wearing beard")
    elif 'mustache' in user_lower or 'moustache' in user_lower:
        accessories.append("wearing mustache")

    # Mole
    if 'mole' in user_lower:
        accessories.append("mole on face")

    # Add all accessories
    if accessories:
        parts.extend(accessories)

    # EYES - ALWAYS if not covered by sunglasses
    has_sunglasses = 'sunglasses' in user_lower or 'shades' in user_lower
    if not has_sunglasses:
        eyes_region = sampled.get('eyes_left', []) or sampled.get('eyes_right', [])
        if eyes_region:
            eye_hex = eyes_region[0]['hex']

            # Get eye color - prefer user description
            user_eye_match = re.search(r'([\w\s-]+)\s+eyes', user_corr, re.IGNORECASE)
            if user_eye_match:
                eye_color = user_eye_match.group(1).strip()
            else:
                eye_color = hex_to_color_name(eye_hex)

            parts.append(f"{eye_color} eyes ({eye_hex})")

    # LIPS - ALWAYS for ladies
    if gender == "lady":
        mouth_region = sampled.get('mouth', [])
        if mouth_region:
            lip_hex = mouth_region[0]['hex']
            lip_color = hex_to_color_name(lip_hex)
            parts.append(f"{lip_color} lips ({lip_hex})")

    # SKIN - ALWAYS present
    face_region = sampled.get('face_center', [])
    if face_region:
        skin_hex = face_region[0]['hex']

        # Get skin tone - prefer user description
        user_skin_match = re.search(r'([\w\s-]+)\s+skin', user_corr, re.IGNORECASE)
        if user_skin_match:
            skin_tone = user_skin_match.group(1).strip()
        else:
            skin_tone = hex_to_color_name(skin_hex)

        parts.append(f"{skin_tone} skin ({skin_hex})")

    # BACKGROUND - ALWAYS present
    bg_region = sampled.get('bg_top_left', [])
    if bg_region:
        bg_hex = bg_region[0]['hex']
        bg_color = hex_to_color_name(bg_hex)

        # Pattern
        if 'checkered' in user_lower or 'checker' in user_lower:
            pattern = "checkered"
        elif 'gradient' in user_lower:
            pattern = "gradient"
        elif 'split' in user_lower:
            pattern = "split"
        else:
            pattern = "solid"

        parts.append(f"{bg_color} {pattern} background ({bg_hex})")

    # CLOTHING - ALWAYS present
    clothing_region = sampled.get('clothing_top', [])
    if clothing_region:
        clothing_hex = clothing_region[0]['hex']
        clothing_color = hex_to_color_name(clothing_hex)

        # Type
        if 'hoodie' in user_lower:
            clothing_type = "hoodie"
        elif 'jacket' in user_lower or 'coat' in user_lower:
            clothing_type = "jacket"
        elif 'suit' in user_lower:
            clothing_type = "suit"
        else:
            clothing_type = "shirt"

        parts.append(f"{clothing_color} {clothing_type} ({clothing_hex})")

    # PALETTE - ALWAYS exactly 5 hex codes
    palette_hexes = []
    for region_name in ['hair_top', 'eyes_left', 'face_center', 'bg_top_left', 'clothing_top']:
        region = sampled.get(region_name, [])
        if region:
            hex_val = region[0]['hex']
            if hex_val not in palette_hexes:
                palette_hexes.append(hex_val)
                if len(palette_hexes) >= 5:
                    break

    # Pad to 5 if needed
    while len(palette_hexes) < 5:
        palette_hexes.append("#000000")

    parts.append(f"palette: {', '.join(palette_hexes[:5])}")

    # STYLE TAGS - ALWAYS the same
    parts.append("sharp pixel edges")
    parts.append("hard color borders")
    parts.append("retro pixel art style")

    return ", ".join(parts)

# Generate all captions
print("Generating strictly templated captions...\n")

for idx, record in enumerate(records, 1):
    filename = record['filename']
    caption = create_templated_caption(record)

    # Write to file
    txt_path = f"civitai_v2_7_training/{filename.replace('.png', '.txt')}"
    with open(txt_path, 'w') as f:
        f.write(caption)

    if idx <= 10 or idx % 50 == 0:
        print(f"  [{idx}/203] {filename}")
        if idx <= 3:
            print(f"    {caption[:150]}...")

print(f"\n✓ Generated {len(records)} templated captions")
print()
print("✅ ALL CAPTIONS NOW USE STRICT TEMPLATE - MAXIMUM CONSISTENCY!")
print()
