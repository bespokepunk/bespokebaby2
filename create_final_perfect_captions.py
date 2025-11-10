#!/usr/bin/env python3
"""
Create PERFECT captions:
- Strict template structure (consistency)
- Preserve ALL descriptive detail (quality)
"""

import json
import re

with open('supabase_export_FIXED_SAMPLING.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("CREATING PERFECT CAPTIONS - STRICT TEMPLATE + FULL DETAIL")
print("=" * 100)
print()

# Celebrity/special hair descriptions (preserve detail!)
SPECIAL_HAIR = {
    'lad_002_cash.png': 'white powdered hair pulled back in classic 18th century colonial style with side volume',
    'lad_015_jackson.png': 'reddish-brown hair pulled back in classic 18th century colonial style',
    'lad_016_tungsten.png': 'white-gray hair with balding top and long sides in classic 18th century style',
    'lad_017_ink.png': 'white powdered hair in classic 18th century colonial style',
    'lad_012_chromium.png': 'short modern haircut with textured top, professional and slightly tousled',
    'lad_026_chromiumabstractsalmon.png': 'short modern haircut with textured top, professional and slightly tousled',
    'lad_027_chromiumabstractyellow.png': 'short modern haircut with textured top, professional and slightly tousled',
    'lad_028_chromiumabstractgreen.png': 'short modern haircut with textured top, professional and slightly tousled',
    'lad_019_diamond.png': 'large voluminous messy brown hair with natural dimension and wild texture',
    'lady_060_winehouse.png': 'large black beehive updo with volume and shine, signature half-up style',
}

def create_perfect_caption(record):
    """Create caption with strict template + full detail"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors_FIXED', {})

    user_lower = user_corr.lower()
    gender = "lady" if filename.startswith("lady_") else "lad"

    parts = []

    # === TEMPLATE SECTION 1: BASE ===
    parts.append("pixel art, 24x24")
    parts.append(f"portrait of bespoke punk {gender}")

    # === TEMPLATE SECTION 2: HAIR (detailed) ===
    hair_region = sampled.get('hair_top', [])
    if hair_region:
        hair_hex = hair_region[0]['hex']

        # Check for special hair description
        if filename in SPECIAL_HAIR:
            parts.append(f"{SPECIAL_HAIR[filename]} ({hair_hex})")
        elif 'bald' in user_lower or 'no hair' in user_lower:
            parts.append("bald")
        else:
            # Extract from user text - preserve detail
            hair_match = re.search(r'([^.]*?hair[^.,]*)', user_corr, re.IGNORECASE)
            if hair_match:
                hair_desc = hair_match.group(1).strip()
                # Clean up typos but preserve detail
                hair_desc = re.sub(r'\byo u\b', 'you', hair_desc, flags=re.IGNORECASE)
                hair_desc = re.sub(r'\bhaoirc\b', 'hair', hair_desc, flags=re.IGNORECASE)
                parts.append(f"{hair_desc} ({hair_hex})")
            else:
                parts.append(f"hair ({hair_hex})")

    # === TEMPLATE SECTION 3: ACCESSORIES (detailed) ===
    accessories = []

    # Hat/cap/crown - preserve detail
    if 'crown' in user_lower:
        crown_match = re.search(r'([\w\s]+crown[^.,]*)', user_corr, re.IGNORECASE)
        if crown_match:
            accessories.append(f"wearing {crown_match.group(1).strip()}")
        else:
            accessories.append("wearing crown")
    elif 'bucket hat' in user_lower:
        hat_match = re.search(r'([^.,]*bucket hat[^.,]*)', user_corr, re.IGNORECASE)
        if hat_match:
            accessories.append(f"wearing {hat_match.group(1).strip()}")
        else:
            accessories.append("wearing bucket hat")
    elif 'hooded cap' in user_lower:
        cap_match = re.search(r'([^.,]*hooded cap[^.,]*)', user_corr, re.IGNORECASE)
        if cap_match:
            accessories.append(f"wearing {cap_match.group(1).strip()}")
        else:
            accessories.append("wearing hooded cap")
    elif 'hat' in user_lower or 'cap' in user_lower:
        hat_match = re.search(r'([\w\s]+(?:hat|cap)[^.,]*)', user_corr, re.IGNORECASE)
        if hat_match:
            accessories.append(f"wearing {hat_match.group(1).strip()}")

    # Sunglasses - preserve detail
    if 'black stunner shades with white reflection' in user_lower or 'black stunner shades with white refelction' in user_lower:
        accessories.append("wearing black stunner shades with white reflection")
    elif 'sunglasses' in user_lower or 'shades' in user_lower:
        sg_match = re.search(r'([\w\s]+(?:sunglasses|shades)[^.,]*)', user_corr, re.IGNORECASE)
        if sg_match:
            accessories.append(f"wearing {sg_match.group(1).strip()}")
        else:
            accessories.append("wearing sunglasses")
    elif 'glasses' in user_lower:
        g_match = re.search(r'([\w\s]+glasses[^.,]*)', user_corr, re.IGNORECASE)
        if g_match:
            accessories.append(f"wearing {g_match.group(1).strip()}")
        else:
            accessories.append("wearing glasses")

    # Earrings - check user corrections AND sampled data
    earring_hex = None
    if 'earring_left' in sampled and sampled['earring_left']:
        earring_hex = sampled['earring_left'][0]['hex']
    elif 'earring_right' in sampled and sampled['earring_right']:
        earring_hex = sampled['earring_right'][0]['hex']

    if 'earring' in user_lower or earring_hex:
        # Extract earring description from user text
        earring_match = re.search(r'([^.,]*earring[^.,]*)', user_corr, re.IGNORECASE)
        if earring_match:
            earring_desc = earring_match.group(1).strip()
            if earring_hex and '(' not in earring_desc:
                accessories.append(f"wearing {earring_desc} ({earring_hex})")
            else:
                accessories.append(f"wearing {earring_desc}")
        elif earring_hex:
            accessories.append(f"wearing earrings ({earring_hex})")

    # Necklace / chain / pendant
    if 'necklace' in user_lower or 'chain' in user_lower or 'pendant' in user_lower:
        necklace_match = re.search(r'([^.,]*(?:necklace|chain|pendant)[^.,]*)', user_corr, re.IGNORECASE)
        if necklace_match:
            accessories.append(f"wearing {necklace_match.group(1).strip()}")

    # Headband / bandana
    if 'headband' in user_lower or 'bandana' in user_lower:
        headband_match = re.search(r'([^.,]*(?:headband|bandana)[^.,]*)', user_corr, re.IGNORECASE)
        if headband_match:
            accessories.append(f"wearing {headband_match.group(1).strip()}")

    # Bow / ribbon
    if 'bow in hair' in user_lower or 'ribbon in hair' in user_lower:
        bow_match = re.search(r'([^.,]*(?:bow|ribbon)[^.,]*)', user_corr, re.IGNORECASE)
        if bow_match:
            accessories.append(f"wearing {bow_match.group(1).strip()}")

    # Flower - preserve detail
    if 'red flower' in user_lower:
        accessories.append("wearing red flower in hair")
    elif 'flower' in user_lower:
        accessories.append("wearing flower in hair")

    # Facial hair
    if 'stubble' in user_lower:
        if 'light grey stubble' in user_lower or 'light gray stubble' in user_lower:
            accessories.append("wearing light gray stubble")
        else:
            accessories.append("wearing stubble")
    elif 'beard' in user_lower:
        if 'full beard' in user_lower:
            accessories.append("wearing full beard")
        else:
            accessories.append("wearing beard")
    elif 'mustache' in user_lower or 'moustache' in user_lower:
        accessories.append("wearing mustache")

    # Mole
    if 'mole' in user_lower:
        accessories.append("mole on face")

    # Add all accessories in order
    if accessories:
        parts.extend(accessories)

    # === TEMPLATE SECTION 4: EYES (detailed) ===
    has_sunglasses = 'sunglasses' in user_lower or 'shades' in user_lower
    if not has_sunglasses:
        eyes_region = sampled.get('eyes_left', []) or sampled.get('eyes_right', [])
        if eyes_region:
            eye_hex = eyes_region[0]['hex']

            # Extract eye color - preserve detail
            eye_match = re.search(r'([^.,]*eyes[^.,]*)', user_corr, re.IGNORECASE)
            if eye_match:
                eye_desc = eye_match.group(1).strip()
                # Just add hex
                if '(' not in eye_desc:  # Don't double-add hex
                    parts.append(f"{eye_desc} ({eye_hex})")
                else:
                    parts.append(eye_desc)
            else:
                parts.append(f"eyes ({eye_hex})")

    # === TEMPLATE SECTION 5: LIPS (ladies only, detailed) ===
    if gender == "lady":
        mouth_region = sampled.get('mouth', [])
        if mouth_region:
            lip_hex = mouth_region[0]['hex']

            # Check if user specified lip color
            lip_match = re.search(r'([^.,]*lips[^.,]*)', user_corr, re.IGNORECASE)
            if lip_match and 'get lip' not in lip_match.group(0).lower():
                lip_desc = lip_match.group(1).strip()
                if '(' not in lip_desc:
                    parts.append(f"{lip_desc} ({lip_hex})")
                else:
                    parts.append(lip_desc)
            else:
                parts.append(f"lips ({lip_hex})")

    # === TEMPLATE SECTION 6: SKIN (detailed) ===
    face_region = sampled.get('face_center', [])
    if face_region:
        skin_hex = face_region[0]['hex']

        # Extract skin tone - preserve detail
        skin_match = re.search(r'([^.,]*skin[^.,]*)', user_corr, re.IGNORECASE)
        if skin_match:
            skin_desc = skin_match.group(1).strip()
            # Clean up
            skin_desc = skin_desc.replace('skinned', 'skin')
            if '(' not in skin_desc:
                parts.append(f"{skin_desc} ({skin_hex})")
            else:
                parts.append(skin_desc)
        else:
            parts.append(f"skin ({skin_hex})")

    # === TEMPLATE SECTION 7: BACKGROUND (detailed) ===
    bg_region = sampled.get('bg_top_left', [])
    if bg_region:
        bg_hex = bg_region[0]['hex']

        # Determine pattern
        if 'checkered' in user_lower or 'checker' in user_lower:
            # Extract full background description
            bg_match = re.search(r'([^.,]*(?:checkered|checker)[^.,]*background[^.,]*)', user_corr, re.IGNORECASE)
            if bg_match:
                bg_desc = bg_match.group(1).strip()
                if '(' not in bg_desc:
                    parts.append(f"{bg_desc} ({bg_hex})")
                else:
                    parts.append(bg_desc)
            else:
                parts.append(f"checkered background ({bg_hex})")
        elif 'gradient' in user_lower:
            parts.append(f"gradient background ({bg_hex})")
        elif 'split' in user_lower:
            parts.append(f"split background ({bg_hex})")
        else:
            # Extract background description
            bg_match = re.search(r'([^.,]*background[^.,]*)', user_corr, re.IGNORECASE)
            if bg_match:
                bg_desc = bg_match.group(1).strip()
                if '(' not in bg_desc:
                    parts.append(f"{bg_desc} ({bg_hex})")
                else:
                    parts.append(bg_desc)
            else:
                parts.append(f"solid background ({bg_hex})")

    # === TEMPLATE SECTION 8: CLOTHING (detailed) ===
    clothing_region = sampled.get('clothing_top', [])
    if clothing_region:
        clothing_hex = clothing_region[0]['hex']

        # Extract clothing description
        clothing_keywords = ['hoodie', 'jacket', 'suit', 'shirt', 'coat', 'undergarments']
        clothing_desc = None

        for keyword in clothing_keywords:
            if keyword in user_lower:
                match = re.search(rf'([^.,]*{keyword}[^.,]*)', user_corr, re.IGNORECASE)
                if match:
                    clothing_desc = match.group(1).strip()
                    break

        if clothing_desc:
            if '(' not in clothing_desc:
                parts.append(f"{clothing_desc} ({clothing_hex})")
            else:
                parts.append(clothing_desc)
        else:
            parts.append(f"clothing ({clothing_hex})")

    # === TEMPLATE SECTION 9: PALETTE (always 5) ===
    palette_hexes = []
    for region_name in ['hair_top', 'eyes_left', 'face_center', 'bg_top_left', 'clothing_top', 'earring_left', 'earring_right']:
        region = sampled.get(region_name, [])
        if region:
            hex_val = region[0]['hex']
            if hex_val not in palette_hexes:
                palette_hexes.append(hex_val)
                if len(palette_hexes) >= 5:
                    break

    while len(palette_hexes) < 5:
        palette_hexes.append("#000000")

    parts.append(f"palette: {', '.join(palette_hexes[:5])}")

    # === TEMPLATE SECTION 10: STYLE TAGS (always same) ===
    parts.append("sharp pixel edges")
    parts.append("hard color borders")
    parts.append("retro pixel art style")

    # Clean up
    caption = ", ".join(parts)
    # Fix typos
    caption = re.sub(r'\byo u\b', 'you', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\brefelction\b', 'reflection', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\brkeds\b', 'reds', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\brbowns\b', 'browns', caption, flags=re.IGNORECASE)

    return caption

# Generate all
print("Generating perfect captions...\n")

for idx, record in enumerate(records, 1):
    filename = record['filename']
    caption = create_perfect_caption(record)

    txt_path = f"civitai_v2_7_training/{filename.replace('.png', '.txt')}"
    with open(txt_path, 'w') as f:
        f.write(caption)

    if idx <= 10 or idx % 50 == 0:
        print(f"  [{idx}/203] {filename}")
        if idx <= 3:
            print(f"    {caption[:200]}...")
            print()

print(f"\n✓ Generated {len(records)} perfect captions")
print()
print("✅ PERFECT CAPTIONS: Strict template + full descriptive detail!")
print()
