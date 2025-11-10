#!/usr/bin/env python3
"""
Generate CLEAN training captions with proper color-to-attribute mappings
No messy narrative text - only structured descriptions
"""

import json
import re
from colorsys import rgb_to_hls

def rgb_to_color_name(r, g, b):
    """Convert RGB to descriptive color name"""
    h, l, s = rgb_to_hls(r/255, g/255, b/255)
    h_deg = h * 360

    # Black/White/Gray check (low saturation)
    if s < 0.1:
        if l < 0.15:
            return "black"
        elif l > 0.85:
            return "white"
        elif l < 0.35:
            return "dark gray"
        elif l < 0.65:
            return "gray"
        else:
            return "light gray"

    # Chromatic colors
    if l < 0.15:
        return "black"
    elif l > 0.9:
        return "white"

    # Determine hue-based color with lightness/saturation modifiers
    brightness_mod = ""
    saturation_mod = ""

    if l < 0.25:
        brightness_mod = "very dark "
    elif l < 0.4:
        brightness_mod = "dark "
    elif l > 0.75:
        brightness_mod = "light "
    elif l > 0.6:
        brightness_mod = "pale "

    if s < 0.25:
        saturation_mod = "grayish "
    elif s > 0.8:
        saturation_mod = "vibrant "

    # Hue determination
    if h_deg < 15 or h_deg >= 345:
        base = "red"
    elif h_deg < 40:
        base = "orange"
    elif h_deg < 70:
        base = "yellow"
    elif h_deg < 150:
        base = "green"
    elif h_deg < 200:
        base = "cyan"
    elif h_deg < 250:
        base = "blue"
    elif h_deg < 290:
        base = "purple"
    elif h_deg < 320:
        base = "magenta"
    else:
        base = "pink"

    return f"{brightness_mod}{saturation_mod}{base}".strip()

def hair_color_name(r, g, b):
    """Specific mapping for hair colors"""
    h, l, s = rgb_to_hls(r/255, g/255, b/255)

    # Black hair
    if l < 0.2:
        return "black"

    # Blonde/yellow hair
    if 30 <= h*360 < 70 and l > 0.5:
        if l > 0.7:
            return "blonde"
        else:
            return "dirty blonde"

    # Brown hair
    if 10 <= h*360 < 50 and 0.2 <= l < 0.5:
        if l < 0.3:
            return "dark brown"
        else:
            return "brown"

    # Red hair
    if h*360 < 25 and s > 0.3:
        return "red"

    # Use generic color naming for unusual colors
    return rgb_to_color_name(r, g, b)

def eye_color_name(r, g, b):
    """Specific mapping for eye colors"""
    h, l, s = rgb_to_hls(r/255, g/255, b/255)

    # Brown eyes
    if 10 <= h*360 < 50:
        if l < 0.3:
            return "dark brown"
        elif l < 0.5:
            return "brown"
        else:
            return "light brown"

    # Blue eyes
    if 180 <= h*360 < 250:
        if l > 0.6:
            return "light blue"
        else:
            return "blue"

    # Green eyes
    if 80 <= h*360 < 180:
        return "green"

    # Gray eyes
    if s < 0.15:
        return "gray"

    return rgb_to_color_name(r, g, b)

def skin_tone_name(r, g, b):
    """Specific mapping for skin tones"""
    h, l, s = rgb_to_hls(r/255, g/255, b/255)

    # Skin tones are typically in the orange/red-orange range
    if l < 0.25:
        return "dark skin"
    elif l < 0.45:
        return "medium dark skin"
    elif l < 0.6:
        return "medium skin"
    elif l < 0.75:
        return "light skin"
    else:
        return "very light skin"

def extract_accessories(user_text):
    """Extract structured accessories from user corrections"""
    user_lower = user_text.lower()
    accessories = []

    # Hat/Cap/Crown patterns
    if 'crown' in user_lower:
        if 'minecraft' in user_lower:
            accessories.append("wearing minecraft-style crown")
        elif 'diamond' in user_lower and 'crown' in user_lower:
            accessories.append("wearing diamond crown")
        else:
            accessories.append("wearing crown")
    elif 'cowboy hat' in user_lower:
        accessories.append("wearing cowboy hat")
    elif 'baseball cap' in user_lower or 'cap' in user_lower:
        if 'forward' in user_lower or 'backwards' in user_lower:
            direction = 'forward' if 'forward' in user_lower else 'backwards'
            accessories.append(f"wearing {direction} baseball cap")
        else:
            accessories.append("wearing baseball cap")
    elif 'bucket hat' in user_lower:
        accessories.append("wearing bucket hat")
    elif 'beret' in user_lower:
        accessories.append("wearing beret")
    elif 'hat' in user_lower:
        accessories.append("wearing hat")

    # Eyewear
    if 'stunner shades' in user_lower or 'black stunner shades' in user_lower:
        accessories.append("wearing black stunner shades")
    elif 'sunglasses' in user_lower or ('shades' in user_lower and 'stunner' not in user_lower):
        accessories.append("wearing sunglasses")
    elif 'glasses' in user_lower:
        if 'rimmed' in user_lower:
            # Extract rim color if mentioned
            if 'silver' in user_lower:
                accessories.append("wearing silver-rimmed glasses")
            elif 'gold' in user_lower:
                accessories.append("wearing gold-rimmed glasses")
            else:
                accessories.append("wearing rimmed glasses")
        else:
            accessories.append("wearing glasses")

    # Jewelry
    if 'earring' in user_lower:
        accessories.append("wearing earrings")

    if 'necklace' in user_lower:
        if 'silver' in user_lower:
            accessories.append("wearing silver necklace")
        elif 'gold' in user_lower:
            accessories.append("wearing gold necklace")
        else:
            accessories.append("wearing necklace")

    if 'chain' in user_lower and 'necklace' not in user_lower:
        accessories.append("wearing chain")

    # Hair accessories
    if 'bow in hair' in user_lower or 'bow' in user_lower and 'hair' in user_lower:
        accessories.append("wearing bow in hair")
    if 'flower' in user_lower and 'hair' in user_lower:
        accessories.append("wearing flower in hair")
    if 'headband' in user_lower:
        accessories.append("wearing headband")

    # Facial hair
    if 'stubble' in user_lower:
        accessories.append("wearing stubble")
    elif 'beard' in user_lower:
        accessories.append("wearing beard")
    elif 'mustache' in user_lower or 'moustache' in user_lower:
        accessories.append("wearing mustache")

    return accessories

def get_background_type(user_text):
    """Determine background pattern"""
    user_lower = user_text.lower()
    if 'checkered' in user_lower or 'checker' in user_lower:
        return "checkered background"
    elif 'gradient' in user_lower:
        return "gradient background"
    elif 'split' in user_lower:
        return "split background"
    else:
        return "solid background"

def generate_clean_caption(record):
    """Generate clean, structured caption"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    sampled = record.get('sampled_trait_colors_FIXED', {})

    gender = "lady" if filename.startswith("lady_") else "lad"
    parts = []

    # Base
    parts.append("pixel art, 24x24")
    parts.append(f"portrait of bespoke punk {gender}")

    # Hair
    if 'bald' in user_corr.lower():
        parts.append("bald")
    elif 'hair_top' in sampled and sampled['hair_top']:
        hair_hex = sampled['hair_top'][0]['hex']
        r, g, b = sampled['hair_top'][0]['rgb']
        hair_desc = hair_color_name(r, g, b)
        parts.append(f"{hair_desc} hair")

    # Accessories
    accessories = extract_accessories(user_corr)
    parts.extend(accessories)

    # Eyes (only if no sunglasses)
    has_sunglasses = 'sunglasses' in user_corr.lower() or 'shades' in user_corr.lower()
    if not has_sunglasses and 'eyes_left' in sampled and sampled['eyes_left']:
        eye_hex = sampled['eyes_left'][0]['hex']
        r, g, b = sampled['eyes_left'][0]['rgb']
        eye_desc = eye_color_name(r, g, b)
        parts.append(f"{eye_desc} eyes")

    # Skin
    if 'face_center' in sampled and sampled['face_center']:
        skin_hex = sampled['face_center'][0]['hex']
        r, g, b = sampled['face_center'][0]['rgb']
        skin_desc = skin_tone_name(r, g, b)
        parts.append(skin_desc)

    # Background
    if 'bg_top_left' in sampled and sampled['bg_top_left']:
        bg_hex = sampled['bg_top_left'][0]['hex']
        r, g, b = sampled['bg_top_left'][0]['rgb']
        bg_color = rgb_to_color_name(r, g, b)
        bg_type = get_background_type(user_corr)
        parts.append(f"{bg_color} {bg_type}")

    # Clothing
    if 'clothing_top' in sampled and sampled['clothing_top']:
        clothing_hex = sampled['clothing_top'][0]['hex']
        r, g, b = sampled['clothing_top'][0]['rgb']
        clothing_color = rgb_to_color_name(r, g, b)
        parts.append(f"{clothing_color} clothing")

    # Palette (top 5 colors)
    palette_hexes = []
    for region_name in ['hair_top', 'eyes_left', 'face_center', 'bg_top_left', 'clothing_top', 'earring_left']:
        if region_name in sampled and sampled[region_name]:
            hex_val = sampled[region_name][0]['hex']
            if hex_val not in palette_hexes:
                palette_hexes.append(hex_val)
                if len(palette_hexes) >= 5:
                    break

    while len(palette_hexes) < 5:
        palette_hexes.append("#000000")

    parts.append(f"palette: {', '.join(palette_hexes[:5])}")

    # Style tags
    parts.append("sharp pixel edges")
    parts.append("hard color borders")
    parts.append("retro pixel art style")

    return ", ".join(parts)

def main():
    print("=" * 100)
    print("GENERATING CLEAN CAPTIONS - COLOR-BASED MAPPINGS")
    print("=" * 100)
    print()

    # Load data
    with open('supabase_export_FIXED_SAMPLING.json', 'r') as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records")
    print()

    # Generate captions
    for idx, record in enumerate(records, 1):
        filename = record['filename']
        caption = generate_clean_caption(record)

        # Save to training directory
        txt_path = f"sd15_training_512/{filename.replace('.png', '.txt')}"
        with open(txt_path, 'w') as f:
            f.write(caption)

        if idx <= 5:
            print(f"[{idx}] {filename}")
            print(f"    {caption[:150]}...")
            print()

    print(f"\n✅ Generated {len(records)} clean captions!")
    print("\nSample caption format:")
    print("  pixel art, 24x24, portrait of bespoke punk lad, black hair, wearing hat,")
    print("  wearing sunglasses, brown eyes, light skin, blue solid background,")
    print("  gray clothing, palette: #xxx, #xxx, #xxx, #xxx, #xxx,")
    print("  sharp pixel edges, hard color borders, retro pixel art style")
    print()

if __name__ == "__main__":
    main()
