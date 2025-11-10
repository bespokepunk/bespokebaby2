#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE CLEANUP - Fix EVERYTHING once and for all
"""

import os
import re
from PIL import Image
from collections import Counter

SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

# EVERY SINGLE TYPO - comprehensive list
ALL_TYPOS = {
    # Double letters that should be single
    "mmedium": "medium",

    # Latest typos
    "lavendar": "lavender",
    "lavelnder": "lavender",
    ";lavelnder": ", lavender",
    "mediu mbrown": "medium brown",
    "moeny": "money",
    "bluie": "blue",
    "al ot": "a lot",
    "lssing": "losing",

    # All previous typos
    "yelloworangeeee": "yellow orange",
    "voluptuos": "voluptuous",
    "medum": "medium",
    "orangeeee": "orange",
    "mmedium toi": "medium to",
    " toi ": " to ",
    "availabe": "available",
    "ahs": "has",
    "reddsish": "reddish",
    "coimpletely": "completely",
    "briads": "braids",
    "so little bans": "bangs",
    "gbright": "bright",
    "ggreen": "green",
    "voluinous": "voluminous",
    "white4": "white",
    "coolors": "colors",
    "pinkrasperby": "pink raspberry",
    "lwocut": "low cut",
    "hald": "half",
    "bobb": "bob",
    "adn": "and",
    "pinstrip[": "pinstripe",
    "bneclance": "necklace",
    "tioned": "toned",
    "ainsides": "lenses",
    "refelctions": "reflections",
    "gree nad": "green and",
    "pinstri[s": "pinstripes",
    "synmetriy": "symmetry",
    "higlighted": "highlighted",
    "reddsih": "reddish",
    "refelctive": "reflective",
    "biege": "beige",
    "goldren": "golden",
    "neckalcen": "necklace",
    "neckalce": "necklace",
    "sillky": "silky",
    "bnounce": "bounce",
    "falter to face": "frame face",
    "legnth": "length",
    "balack": "black",
    "seni": "semi",
    "limedium": "light medium",
    "edium": "medium",
    "bl, onde": "blonde",
    "nmatural": "natural",
    "colro": "color",
    "nad": "and",
    "staight": "straight",
    "cxolor": "color",
    "brighth ": "bright ",
    "tone sthrough": "tones through",
    "tones throughh": "tones through",
    "hzel": "hazel",
    "alsmot": "almost",
    "tone strhough": "tones through",
    "hdangling": "dangling",
    "fillhzel": "fill, hazel",
    "cgold": "gold",
    "colroed": "colored",
    "colore ": "colored ",
    "colros": "colors",
    "colothing": "clothing",
    "grradient": "gradient",
    "hippe ": "hippie ",
    "flasses": "glasses",
    "brwin": "brown",
    "bouse": "blouse",
    "creem": "cream",
    "buna": "bun",
    "dakr": "dark",
    "balck": "black",
    "ligth": "light",
    "pruple": "purple",
    "yelow": "yellow",
    "graey": "gray",
    "grene": "green",
    "orang": "orange",
    "tesal": "teal",
    "backround": "background",
    "backgorund": "background",
    "backtround": "background",
    "amroon": "maroon",
    "bluise": "bluish",
    "blusieh": "bluish",
    "checkerd": "checkered",
    "dimaond": "diamond",
    "earings": "earrings",
    "earsings": "earrings",
    "glases": "glasses",
    "gorgeus": "gorgeous",
    "hiar": "hair",
    "jewlery": "jewelry",
    "layerd": "layered",
    "neklace": "necklace",
    "pendnat": "pendant",
    "portait": "portrait",
    "shiney": "shiny",
    "slighty": "slightly",
    "somehwat": "somewhat",
    "straigt": "straight",
    "throug": "through",
    "touhg": "tough",
    "wavey": "wavy",
    "grayscalewearing": "grayscale, wearing",
}

def get_image_palette(image_path, num_colors=15):
    """Extract top colors from image"""
    try:
        img = Image.open(image_path).convert('RGB')
        pixels = list(img.getdata())
        color_counts = Counter(pixels)
        top_colors = color_counts.most_common(num_colors)
        hex_colors = []
        for (r, g, b), count in top_colors:
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            hex_colors.append(hex_color)
        return hex_colors
    except:
        return []

def expand_palette_if_needed(text, image_path):
    """Ensure palette has 12-15 colors"""
    # Find existing palette
    palette_match = re.search(r'palette: ([^,]+(?:, [^,]+)*),', text)
    if palette_match:
        current_palette = palette_match.group(1)
        current_colors = [c.strip() for c in current_palette.split(',')]

        # If less than 10 colors, expand
        if len(current_colors) < 10:
            # Get colors from image
            image_colors = get_image_palette(image_path, 15)
            if image_colors:
                # Combine existing with new colors (keep existing first, add new)
                all_colors = current_colors.copy()
                for color in image_colors:
                    if color not in all_colors and len(all_colors) < 15:
                        all_colors.append(color)

                # Replace palette in text
                new_palette = ', '.join(all_colors)
                text = text.replace(f'palette: {current_palette},', f'palette: {new_palette},')

    return text

def fix_all_typos(text):
    """Fix every typo"""
    for typo, correct in ALL_TYPOS.items():
        text = text.replace(typo, correct)
    return text

def fix_spacing(text):
    """Fix spacing issues"""
    # Fix concatenated words
    patterns = [
        (r'glasses([A-Z])', r'glasses, \1'),
        (r'glassesmedium', 'glasses, medium'),
        (r'glassesMedium', 'glasses, medium'),
        (r'wearing([A-Z])', r'wearing \1'),
        (r'hair([A-Z])', r'hair, \1'),
        (r'eyes([A-Z])', r'eyes, \1'),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)

    # Fix double spaces and punctuation
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r';\s*', ', ', text)  # Fix semicolons
    text = text.strip()

    return text

def main():
    print("🎯 FINAL COMPREHENSIVE CLEANUP...\\n")

    fixed_count = 0
    for filename in sorted(os.listdir(SOURCE_DIR)):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(SOURCE_DIR, filename)
        image_path = filepath.replace('.txt', '.png')

        with open(filepath, 'r') as f:
            original = f.read()

        # Apply all fixes
        fixed = original
        fixed = fix_all_typos(fixed)
        fixed = fix_spacing(fixed)
        fixed = expand_palette_if_needed(fixed, image_path)

        if fixed != original:
            with open(filepath, 'w') as f:
                f.write(fixed)
            print(f"  ✅ Fixed: {filename}")
            fixed_count += 1

    print(f"\\n✨ Fixed {fixed_count} caption files!")
    print("🏆 FINAL CLEANUP COMPLETE!")

if __name__ == "__main__":
    main()
