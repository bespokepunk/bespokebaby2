#!/usr/bin/env python3
"""
Fix celebrity/instruction text with actual proper hair descriptions
Based on actual images + user intent
"""

import json

# Load data with correct sampling
with open('supabase_export_FIXED_SAMPLING.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("FIXING CELEBRITY REFERENCES WITH ACTUAL DESCRIPTIONS")
print("=" * 100)
print()

# Define proper descriptions based on images + user intent
celebrity_fixes = {
    'lad_002_cash.png': {
        'hair_desc': 'white powdered hair pulled back in classic 18th century colonial style with side volume',
        'notes': 'George Washington - founding father powdered wig look'
    },
    'lad_015_jackson.png': {
        'hair_desc': 'reddish-brown hair pulled back in classic 18th century colonial style',
        'notes': 'Thomas Jefferson - founding father style, reddish tones'
    },
    'lad_016_tungsten.png': {
        'hair_desc': 'white-gray hair with balding top and long sides in classic 18th century style',
        'notes': 'Benjamin Franklin - older founding father, receding hairline'
    },
    'lad_017_ink.png': {
        'hair_desc': 'white powdered hair in classic 18th century colonial style',
        'notes': 'John Adams - founding father powdered wig'
    },
    'lad_012_chromium.png': {
        'hair_desc': 'short modern haircut with textured top, professional and slightly tousled',
        'notes': 'Sam Altman - modern tech executive, longer on top, styled'
    },
    'lad_026_chromiumabstractsalmon.png': {
        'hair_desc': 'short modern haircut with textured top, professional and slightly tousled',
        'notes': 'Sam Altman variant'
    },
    'lad_027_chromiumabstractyellow.png': {
        'hair_desc': 'short modern haircut with textured top, professional and slightly tousled',
        'notes': 'Sam Altman variant'
    },
    'lad_028_chromiumabstractgreen.png': {
        'hair_desc': 'short modern haircut with textured top, professional and slightly tousled',
        'notes': 'Sam Altman variant'
    },
    'lad_019_diamond.png': {
        'hair_desc': 'large voluminous messy brown hair with natural dimension and wild texture',
        'notes': 'Vitalik Buterin - big funnel-like hair, very voluminous'
    },
    'lady_060_winehouse.png': {
        'hair_desc': 'large black beehive updo with volume and shine, signature half-up style',
        'notes': 'Amy Winehouse - iconic beehive, red flower accessory'
    },
}

def build_fixed_caption(record, hair_override=None):
    """Build caption with proper descriptions"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors_FIXED', {})

    user_lower = user_corr.lower()
    gender = "lady" if filename.startswith("lady_") else "lad"

    parts = ["pixel art, 24x24", f"portrait of bespoke punk {gender}"]

    # HAIR - use override if provided
    if hair_override:
        hair_region = sampled.get('hair_top', [])
        if hair_region:
            hair_hex = hair_region[0]['hex']
            parts.append(f"{hair_override} ({hair_hex})")
    else:
        # Default hair handling
        hair_region = sampled.get('hair_top', [])
        if hair_region:
            hair_hex = hair_region[0]['hex']
            parts.append(f"hair ({hair_hex})")

    # ACCESSORIES
    # Red flower for Amy Winehouse
    if 'red flower' in user_lower:
        parts.append('wearing red flower in hair')

    # HAT/CAP/CROWN
    if 'hat' in user_lower or 'cap' in user_lower or 'crown' in user_lower:
        if 'hat' not in 'hat in hair':  # Skip if it's "flower in hair"
            import re
            hat_match = re.search(r'((?:[\w\s]+\s)?(?:hat|cap|crown))', user_lower)
            if hat_match and 'flower' not in hat_match.group(0):
                parts.append(f"wearing {hat_match.group(1).strip()}")

    # SUNGLASSES
    has_sunglasses = False
    if 'sunglasses' in user_lower or 'shades' in user_lower or 'stunner shades' in user_lower:
        if 'black stunner shades' in user_lower:
            parts.append('wearing black stunner shades with white reflection')
        else:
            parts.append('wearing sunglasses')
        has_sunglasses = True
    elif 'glasses' in user_lower:
        parts.append('wearing glasses')

    # FACIAL HAIR
    if 'stubble' in user_lower:
        parts.append('wearing stubble')
    elif 'beard' in user_lower:
        parts.append('wearing beard')
    elif 'mustache' in user_lower:
        parts.append('wearing mustache')

    # MOLE
    if 'mole' in user_lower:
        parts.append('mole on face')

    # EYES (if not covered)
    if not has_sunglasses:
        eyes_region = sampled.get('eyes_left', []) or sampled.get('eyes_right', [])
        if eyes_region:
            eye_hex = eyes_region[0]['hex']

            # Check for user descriptions
            import re
            if 'hazel green deep eyes' in user_lower:
                parts.append(f"hazel green eyes ({eye_hex})")
            elif 'deep blue sea like' in user_lower:
                parts.append(f"deep blue eyes ({eye_hex})")
            elif 'light opale seafom green blue eyes' in user_lower or 'light opale sdeafom green blue eyes' in user_lower:
                parts.append(f"light seafoam blue-green eyes ({eye_hex})")
            else:
                eye_match = re.search(r'([\w\s]+)\s+eyes', user_lower)
                if eye_match:
                    parts.append(f"{eye_match.group(1).strip()} eyes ({eye_hex})")
                else:
                    parts.append(f"eyes ({eye_hex})")

    # LIPS (ladies)
    if gender == "lady":
        mouth_region = sampled.get('mouth', [])
        if mouth_region:
            lip_hex = mouth_region[0]['hex']
            parts.append(f"lips ({lip_hex})")

    # SKIN
    face_region = sampled.get('face_center', [])
    if face_region:
        skin_hex = face_region[0]['hex']

        # Check for user skin descriptions
        if 'light skin' in user_lower:
            parts.append(f"light skin ({skin_hex})")
        elif 'medium skin' in user_lower:
            parts.append(f"medium skin ({skin_hex})")
        elif 'light grey skin' in user_lower or 'grayscale' in user_lower:
            parts.append(f"light gray skin ({skin_hex})")
        elif 'light/medium pale green tone' in user_lower:
            parts.append(f"pale green-tinted skin ({skin_hex})")
        else:
            parts.append(f"skin ({skin_hex})")

    # BACKGROUND
    bg_region = sampled.get('bg_top_left', [])
    if bg_region:
        bg_hex = bg_region[0]['hex']

        if 'bright neon green background' in user_lower or 'bright green background' in user_lower:
            parts.append(f"bright neon green background ({bg_hex})")
        elif 'purple lavender light background' in user_lower:
            parts.append(f"light purple lavender background ({bg_hex})")
        else:
            parts.append(f"background ({bg_hex})")

    # CLOTHING
    clothing_region = sampled.get('clothing_top', [])
    if clothing_region:
        clothing_hex = clothing_region[0]['hex']

        import re
        # Check for specific clothing descriptions
        if 'dark grey suit' in user_lower:
            parts.append(f"dark gray suit ({clothing_hex})")
        elif 'light grey suit' in user_lower:
            parts.append(f"light gray suit ({clothing_hex})")
        elif 'dark golden yellow shirt' in user_lower:
            parts.append(f"dark golden yellow shirt ({clothing_hex})")
        elif 'dark salmon pink shirt' in user_lower:
            parts.append(f"dark salmon pink shirt ({clothing_hex})")
        elif 'dark paleish green shirt' in user_lower:
            parts.append(f"dark pale green shirt ({clothing_hex})")
        elif 'teal blue shirt' in user_lower:
            parts.append(f"teal blue shirt with white logo ({clothing_hex})")
        elif 'plain white' in user_lower or 'white undergarments' in user_lower:
            parts.append(f"classic vintage suit with white undergarments ({clothing_hex})")
        else:
            if 'suit' in user_lower:
                parts.append(f"suit ({clothing_hex})")
            elif 'shirt' in user_lower:
                parts.append(f"shirt ({clothing_hex})")
            else:
                parts.append(f"clothing ({clothing_hex})")

    # PALETTE
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

# Fix each file
print("Generating fixed captions:\n")

for filename, fix_info in celebrity_fixes.items():
    # Find record
    record = next((r for r in records if r['filename'] == filename), None)
    if not record:
        print(f"⚠️  Could not find {filename}")
        continue

    # Generate caption with proper hair description
    caption = build_fixed_caption(record, hair_override=fix_info['hair_desc'])

    # Write to txt file
    txt_path = f"civitai_v2_7_training/{filename.replace('.png', '.txt')}"
    with open(txt_path, 'w') as f:
        f.write(caption)

    print(f"✓ {filename}")
    print(f"  {fix_info['notes']}")
    print(f"  {caption[:180]}...")
    print()

print("=" * 100)
print("✅ All celebrity references fixed with proper descriptions!")
print()
