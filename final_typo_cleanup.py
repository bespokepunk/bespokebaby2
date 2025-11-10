#!/usr/bin/env python3
"""
COMPREHENSIVE WORLD-CLASS TYPO CLEANUP
Catch ALL typos and improve caption quality for perfect training
"""

import os
import re

SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

# Comprehensive typo dictionary
TYPO_FIXES = {
    # New typos found
    "flasses": "glasses",
    "brwin": "brown",
    "bouse": "blouse",
    "creem": "cream",

    # Previous typos
    "balck": "black",
    "ligth": "light",
    "pruple": "purple",
    "dimesion": "dimension",
    "greren": "green",
    "somehwat": "somewhat",
    "unershirt": "undershirt",
    "colalred": "collared",
    "collare d": "collared",
    "framemd": "framed",
    "glsses": "glasses",
    "hacket": "jacket",
    "vblazer": "blazer",
    "earrisngs": "earrings",
    "diamons": "diamonds",
    "diamon ": "diamond ",
    "fdark": "dark",
    "lavendar": "lavender",
    "splut": "split",
    "rimme ": "rimmed ",
    "tins of": "tints of",
    "lgith": "light",
    "schoo lkid": "school kid",
    "logner": "longer",
    "middel": "middle",
    "oranger": "orange",
    "abaseball": "a baseball",
    "mediu mto": "medium to",
    "ts hirt": "t shirt",
    "uneanrth": "underneath",
    "dakr": "dark",
    "pinkpiskpurple": "pink purple",
    "bodyusuit": "bodysuit",
    "clight": "light",
}

# Patterns for missing spaces after "wearing" + word combinations
WEARING_SPACE_FIXES = [
    (r'glasseswearing', 'glasses, wearing'),
    (r'glassesmedium', 'glasses, medium'),
    (r'glasseslight', 'glasses, light'),
    (r'glassesdark', 'glasses, dark'),
    (r'glassesbrown', 'glasses, brown'),
    (r'glassesblack', 'glasses, black'),
    (r'capwearing', 'cap, wearing'),
    (r'hatwearing', 'hat, wearing'),
    (r'crownwearing', 'crown, wearing'),
    (r'crownmedium', 'crown, medium'),
    (r'crownDark', 'crown, dark'),
    (r'earringwearing', 'earring, wearing'),
    (r'hatdark', 'hat, dark'),
    (r'eyesand', 'eyes and'),
    (r'eyesblack', 'eyes, black'),
    (r'diamondsmedium', 'diamonds, medium'),
    (r'purplelips', 'purple, lips'),
]

def fix_caption(text):
    """Fix ALL typos and spacing issues"""

    # Apply typo fixes
    for typo, correct in TYPO_FIXES.items():
        text = text.replace(typo, correct)

    # Fix wearing + word combinations (missing spaces/commas)
    for pattern, replacement in WEARING_SPACE_FIXES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Fix double spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove phrases "like" when used as filler
    text = re.sub(r'\sbob like\s', ' bob ', text)
    text = re.sub(r'\shippie like\s', ' hippie ', text)

    return text

def main():
    print("🔧 FINAL COMPREHENSIVE TYPO CLEANUP...\n")

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

if __name__ == "__main__":
    main()
