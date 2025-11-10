#!/usr/bin/env python3
"""
Fix common typos and spacing issues in all SD 1.5 caption files
"""

import os
import re

SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

# Common typo mappings
TYPO_FIXES = {
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
}

# Patterns for missing spaces
SPACE_FIXES = [
    (r'glasseswearing', 'glasses, wearing'),
    (r'capwearing', 'cap, wearing'),
    (r'hatwearing', 'hat, wearing'),
    (r'crownwearing', 'crown, wearing'),
    (r'earringwearing', 'earring, wearing'),
    (r'hatdark', 'hat, dark'),
    (r'crownDark', 'crown, dark'),
    (r'crownmedium', 'crown, medium'),
    (r'eyesand', 'eyes and'),
    (r'eyesblack', 'eyes, black'),
    (r'diamondsmedium', 'diamonds, medium'),
]

def fix_caption(text):
    """Fix all typos and spacing issues in a caption"""
    # Fix common typos
    for typo, correct in TYPO_FIXES.items():
        text = text.replace(typo, correct)

    # Fix missing spaces with patterns
    for pattern, replacement in SPACE_FIXES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

def main():
    print("🔧 Fixing typos and spacing in all caption files...\n")

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
