#!/usr/bin/env python3
"""
PROPERLY clean captions:
1. Remove duplicate/messy "wearing" clauses
2. Expand instruction notes like "(describe...)" into proper descriptions
3. Fix typos
4. Keep ALL detailed aesthetic descriptions
"""

import json
import re

# Load supabase data
with open('supabase_export_FIXED_SAMPLING.json', 'r') as f:
    records = json.load(f)

# Manual fixes for specific cases that need human judgment
MANUAL_FIXES = {
    'lady_099_domino.png': {
        'before': 'wearing Red Hooded Cape (describe in the style od Little Red Ridhing Hood)',
        'after': 'wearing classic red hooded cape in fairy tale Little Red Riding Hood style with hood partially covering face'
    },
    'lad_007_titanium.png': {
        'before': 'dark dark brown blaksi hcolor with some medium brown and higlights shining off as reflection and sheening, but overall face framing longer hair like an emo dude or gothic trenchcoater (describe this better)',
        'after': 'dark brown to black hair with medium brown highlights and natural sheen, longer face-framing emo/gothic style'
    },
    'lad_019_diamond.png': {
        # Remove the duplicate messy "wearing" clause
        'remove': 'wearing resih big funnel like hair msomewhat messy and long'
    },
    'lad_005_copper.png': {
        # Remove garbage text
        'remove': 'wearing do that herem this is him'
    }
}

def fix_caption_text(text, filename):
    """Fix typos and grammar in caption text"""

    # Common typo fixes
    fixes = {
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
        r'\bstunner shades\b': 'stunner shades with white reflection',
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
    }

    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

def clean_caption(filename):
    """Clean up a caption for a specific file"""

    # Read current caption
    txt_path = f'civitai_v2_7_training/{filename.replace(".png", ".txt")}'
    try:
        with open(txt_path, 'r') as f:
            caption = f.read().strip()
    except:
        return None

    # Apply manual fixes first
    if filename in MANUAL_FIXES:
        fix_data = MANUAL_FIXES[filename]

        if 'before' in fix_data and 'after' in fix_data:
            caption = caption.replace(fix_data['before'], fix_data['after'])

        if 'remove' in fix_data:
            # Remove the messy clause
            caption = caption.replace(f", {fix_data['remove']}", "")
            caption = caption.replace(fix_data['remove'], "")

    # Fix typos
    caption = fix_caption_text(caption, filename)

    # Clean up double commas and spaces
    caption = re.sub(r',\s*,', ',', caption)
    caption = re.sub(r'\s+', ' ', caption)
    caption = re.sub(r',\s+', ', ', caption)

    return caption

def main():
    print("="*100)
    print("PROPERLY CLEANING CAPTIONS")
    print("="*100)
    print()

    fixed_count = 0

    for record in records:
        filename = record['filename']
        clean = clean_caption(filename)

        if clean:
            # Save cleaned caption
            txt_path = f'sd15_training_512/{filename.replace(".png", ".txt")}'
            with open(txt_path, 'w') as f:
                f.write(clean)

            fixed_count += 1

            # Show first few examples
            if fixed_count <= 5:
                print(f"[{fixed_count}] {filename}")
                print(f"    {clean[:180]}...")
                print()

    print(f"\n✅ Cleaned {fixed_count} captions!")
    print()
    print("Examples of fixes:")
    print("  - Removed duplicate/messy 'wearing' clauses")
    print("  - Expanded '(describe...)' instructions into proper descriptions")
    print("  - Fixed typos (yo u -> you, opale sdeafom -> opal seafoam, etc.)")
    print("  - Kept ALL detailed aesthetic descriptions")
    print()

if __name__ == "__main__":
    main()
