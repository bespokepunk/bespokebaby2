#!/usr/bin/env python3
"""
Comprehensively fix ALL caption issues:
1. Expand (describe...) instructions
2. Remove duplicate/garbage "wearing" clauses
3. Fix all typos
4. Keep detailed aesthetic descriptions
"""

import os
import re

TRAINING_DIR = "civitai_v2_7_training"
OUTPUT_DIR = "sd15_training_512"

# Typo fixes
TYPO_FIXES = {
    r'\byo u\b': 'you',
    r'\bopale\b': 'opal',
    r'\bsdeafom\b': 'seafoam',
    r'\brefelction\b': 'reflection',
    r'\brkeds\b': 'reds',
    r'\brbowns\b': 'browns',
    r'\bhaoirc\b': 'hair',
    r'\bhcolor\b': 'color',
    r'\bhiglights\b': 'highlights',
    r'\bblaksi\b': 'blackish',
    r'\bpartialyl\b': 'partially',
    r'\blavernder\b': 'lavender',
    r'\bolvie\b': 'olive',
    r'\bsolilky\b': 'silky',
    r'\btrasnculent\b': 'translucent',
    r'\bdedep\b': 'deep',
    r'\boverszied\b': 'oversized',
    r'\bcamoflaouged\b': 'camouflaged',
    r'\bwewaring\b': 'wearing',
    r'\bmultoclored\b': 'multicolored',
    r'\bwhtat\b': 'that',
    r'\buburn\b': 'auburn',
    r'\bhoddie\b': 'hoodie',
    r'\bperiwinke\b': 'periwinkle',
    r'\bod\b': 'of',
    r'\bRidhing\b': 'Riding',
    r'\bresih\b': 'reddish',
    r'\bmsomewhat\b': 'somewhat',
    r'\bherem\b': 'here',
    r'\ba n\b': 'an',
}

def fix_typos(text):
    """Fix common typos"""
    for pattern, replacement in TYPO_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def expand_describe_instructions(text, filename):
    """Expand (describe...) instructions into proper descriptions"""

    # Red hooded cape - expand with concrete visual description
    # Match: "(describe in the style od/of Little Red Ridhing/Riding Hood)"
    text = re.sub(
        r'wearing Red Hooded Cape \([^)]*Little Red Rid(?:h|)ing Hood[^)]*\)',
        'wearing red hooded cape with hood pulled up partially covering face and obscuring one eye',
        text,
        flags=re.IGNORECASE
    )

    # Emo/gothic hair style
    if 'emo dude or gothic trenchcoater' in text.lower():
        # Match the full messy description
        text = re.sub(
            r'dark dark brown blaksi(?:h)? (?:h)?color with some medium brown and hi(?:g)?lights shining off as reflection and sheening, but overall face framing longer hair like an emo dude or gothic trenchcoater \(describe this better\)',
            'dark brown to black hair with medium brown highlights and natural sheen, longer face-framing emo/gothic style',
            text,
            flags=re.IGNORECASE
        )

    return text

def remove_garbage_clauses(text):
    """Remove obviously garbage/placeholder clauses"""

    # Remove "wearing do that herem this is him"
    text = re.sub(r',?\s*wearing do that herem[^,]*', '', text, flags=re.IGNORECASE)

    # Remove duplicate/messy hair descriptions that appear AFTER the first good one
    # Pattern: good hair description (#hex), then bad "wearing ...hair..."
    if 'wearing resih big funnel' in text or 'wearing reddish big funnel' in text:
        text = re.sub(r',?\s*wearing (?:resih|reddish) big funnel[^,]*', '', text)

    return text

def clean_duplicate_commas(text):
    """Clean up formatting issues"""
    # Remove double commas
    text = re.sub(r',\s*,+', ',', text)
    # Remove spaces before commas
    text = re.sub(r'\s+,', ',', text)
    # Normalize spacing after commas
    text = re.sub(r',\s+', ', ', text)
    # Remove duplicate spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fix_caption(filename):
    """Fix all issues in a caption"""
    txt_path = os.path.join(TRAINING_DIR, filename)

    with open(txt_path, 'r') as f:
        caption = f.read().strip()

    original = caption

    # Apply fixes in order (expand FIRST, before typo fixes change the text)
    caption = expand_describe_instructions(caption, filename)  # Expand first!
    caption = remove_garbage_clauses(caption)
    caption = fix_typos(caption)  # Fix typos after expansion
    caption = clean_duplicate_commas(caption)

    return original, caption

def main():
    print("="*100)
    print("COMPREHENSIVELY FIXING ALL CAPTION ISSUES")
    print("="*100)
    print()

    fixed_count = 0
    changed_count = 0

    txt_files = sorted([f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')])

    for filename in txt_files:
        original, fixed = fix_caption(filename)

        if original != fixed:
            changed_count += 1

            # Save to output directory
            output_path = os.path.join(OUTPUT_DIR, filename)
            with open(output_path, 'w') as f:
                f.write(fixed)

            # Show first few changes
            if changed_count <= 10:
                print(f"[{changed_count}] {filename}")
                print(f"    CHANGED")
                if len(fixed) != len(original):
                    print(f"    Length: {len(original)} -> {len(fixed)}")
                print()
        else:
            # No changes needed, just copy
            output_path = os.path.join(OUTPUT_DIR, filename)
            with open(output_path, 'w') as f:
                f.write(fixed)

        fixed_count += 1

    print()
    print("="*100)
    print("CAPTION FIX COMPLETE")
    print("="*100)
    print()
    print(f"✅ Processed: {fixed_count} files")
    print(f"📝 Changed: {changed_count} files")
    print(f"✓  Copied unchanged: {fixed_count - changed_count} files")
    print()
    print("Fixes applied:")
    print("  - Expanded '(describe...)' instructions")
    print("  - Removed garbage text like 'do that herem this is him'")
    print("  - Removed duplicate messy 'wearing' clauses")
    print("  - Fixed 30+ common typos")
    print("  - Cleaned up formatting")
    print()

if __name__ == "__main__":
    main()
