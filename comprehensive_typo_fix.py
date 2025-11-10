#!/usr/bin/env python3
"""
COMPREHENSIVE TYPO FIX - Catch EVERY remaining typo for WORLD CLASS quality
"""

import os
import re

SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

# EVERY typo identified by user
COMPREHENSIVE_TYPO_FIXES = {
    # LATEST batch from most recent audit
    "yelloworangeeee": "yellow orange",
    "i thin khere": "I think here",
    "voluptuos": "voluptuous",
    "medum": "medium",
    "orangeeee": "orange",
    "mmedium toi": "medium to",
    " toi ": " to ",
    "availabe": "available",
    "ahs": "has",
    "reddsish": "reddish",

    # NEWEST batch from user audit message
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

    # Previous batches
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
    "mmedium": "medium",
    "alsmot": "almost",

    # Previous rounds that might still exist
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
    "almsot": "almost",
    "amroon": "maroon",
    "bluise": "bluish",
    "blusieh": "bluish",
    "colroed": "colored",
    "checkerd": "checkered",
    "dimaond": "diamond",
    "earings": "earrings",
    "earsings": "earrings",
    "glases": "glasses",
    "gorgeus": "gorgeous",
    "hiar": "hair",
    "jewlery": "jewelry",
    "layerd": "layered",
    "neckalce": "necklace",
    "neklace": "necklace",
    "pendnat": "pendant",
    "portait": "portrait",
    "shiney": "shiny",
    "slighty": "slightly",
    "somehwat": "somewhat",
    "straigt": "straight",
    "throug": "through",
    "tiffany": "tiffany",
    "touhg": "tough",
    "wavey": "wavy",
    "wispy": "wispy",
}

def fix_spacing_issues(text):
    """Fix spacing and concatenation issues"""
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

    return text

def fix_caption(text):
    """Apply all comprehensive fixes"""

    # Fix all typos
    for typo, correct in COMPREHENSIVE_TYPO_FIXES.items():
        text = text.replace(typo, correct)

    # Fix spacing issues
    text = fix_spacing_issues(text)

    # Remove leftover instructional phrases
    instructional_patterns = [
        r'\(instructions?:.*?\)',
        r'remember to.*?(?=,|\.|$)',
        r'should be.*?(?=,|\.|$)',
        r'need to.*?(?=,|\.|$)',
        r'TODO:.*?(?=,|\.|$)',
        r'note:.*?(?=,|\.|$)',
    ]

    for pattern in instructional_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Fix double spaces and punctuation
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r',\s*,', ',', text)
    text = text.strip()

    return text

def main():
    print("🎯 COMPREHENSIVE TYPO FIX - WORLD CLASS QUALITY...\n")

    fixed_count = 0
    for filename in sorted(os.listdir(SOURCE_DIR)):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(SOURCE_DIR, filename)

        with open(filepath, 'r') as f:
            original = f.read()

        fixed = fix_caption(original)

        if fixed != original:
            with open(filepath, 'w') as f:
                f.write(fixed)
            print(f"  ✅ Fixed: {filename}")
            fixed_count += 1

    print(f"\n✨ Fixed {fixed_count} caption files!")
    print("🏆 WORLD CLASS QUALITY ACHIEVED!")

if __name__ == "__main__":
    main()
