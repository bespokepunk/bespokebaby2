#!/usr/bin/env python3
"""
Comprehensive caption enhancement:
- Fix all remaining typos
- Remove redundancy
- Improve grammar and flow
- Standardize formatting
- Better templating while preserving detail
"""

import os
import re

# Work on the already-fixed files to enhance them further
TRAINING_DIR = "sd15_training_512"
OUTPUT_DIR = "sd15_training_512"

def enhance_caption(caption, filename):
    """Comprehensively enhance a caption"""

    # === STEP 1: Fix remaining typos ===
    typo_fixes = {
        r'\byo ucan\b': 'you can',
        r'\byo u\b': 'you',
        r'\ba n\b': 'an',
        r'\bthe the\b': 'the',
        r'\bhis his\b': 'his',
        r'\bher her\b': 'her',
    }

    for pattern, replacement in typo_fixes.items():
        caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)

    # === STEP 2: Standardize capitalization ===
    # Fix random capitals in middle of sentence
    caption = re.sub(r', Eyes\b', ', eyes', caption)
    caption = re.sub(r'\bGrey\b', 'gray', caption)
    caption = re.sub(r'\bWhite\b(?! )', 'white', caption)  # Don't change if part of name

    # === STEP 3: Remove redundancy ===
    # "medium skin tone light skin tone" → "medium light skin tone"
    caption = re.sub(r'medium skin tone light skin tone', 'medium light skin tone', caption)
    caption = re.sub(r'light skin tone medium skin tone', 'medium light skin tone', caption)
    caption = re.sub(r'dark skin tone dark skin', 'dark skin', caption)

    # === STEP 4: Improve verbose hair descriptions ===
    # "his hair is dark brown mostly but you can obviously see the sheen and reflection for the light on it because its so shiny and also has natural highlights"
    # → "dark brown hair with natural sheen, highlights, and reflective shine"

    # "dark dark brown blackish color with some medium brown and highlights shining off as reflection and sheening, but overall face framing longer hair like an emo dude or gothic trenchcoater (describe this better)"
    # → "dark brown to black hair with medium brown highlights and natural sheen, longer face-framing emo/gothic style"

    verbose_hair_patterns = [
        (
            r'his hair is dark brown mostly but you can obviously see the sheen and reflection for the light on it because its so shiny and also has natural highlights',
            'dark brown hair with natural sheen, highlights, and reflective shine'
        ),
        (
            r'her hair is dark brown mostly but you can obviously see the sheen and reflection for the light on it because its so shiny and also has natural highlights',
            'dark brown hair with natural sheen, highlights, and reflective shine'
        ),
        (
            r'dark dark brown (?:blackish|blaksi) (?:h)?color with some medium brown and (?:highlights|higlights) shining off as reflection and sheening,? but overall face framing longer hair like an emo dude or gothic trenchcoater \(describe this better\)',
            'dark brown to black hair with medium brown highlights and natural sheen, longer face-framing emo/gothic style'
        ),
    ]

    for pattern, replacement in verbose_hair_patterns:
        caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)

    # Remove any remaining "(describe...)" instructions
    caption = re.sub(r'\s*\(describe[^)]*\)', '', caption, flags=re.IGNORECASE)

    # === STEP 5: Improve awkward grammar ===
    # "the background is brown" → "brown background"
    caption = re.sub(r'the background is (\w+)', r'\1 background', caption)

    # "he is wearing an outfit classic of the time also a simple suit and tie"
    # → "wearing classic suit and tie"
    caption = re.sub(
        r'he is wearing an? outfit classic of the time also an? (\w+\s+\w+(?:\s+and\s+\w+)?)',
        r'wearing classic \1',
        caption,
        flags=re.IGNORECASE
    )

    # "she is wearing" → "wearing"
    caption = re.sub(r'\b(?:he|she) is wearing\b', 'wearing', caption, flags=re.IGNORECASE)

    # === STEP 6: Improve ethnicity/gender descriptions ===
    # "medium skin indian male" → "medium indian male skin tone"
    # "light skin mexican male" → "light mexican male skin tone"
    # "light mexican male skin tone tone" → "light mexican male skin tone"

    ethnicity_patterns = [
        (r'(\w+) skin (indian|mexican|asian|black|white) (male|female)', r'\1 \2 \3 skin tone'),
        (r'(\w+) (indian|mexican|asian|black|white) (male|female) skin', r'\1 \2 \3 skin tone'),
    ]

    for pattern, replacement in ethnicity_patterns:
        caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)

    # Fix "skin tone tone" duplication
    caption = re.sub(r'\bskin tone tone\b', 'skin tone', caption, flags=re.IGNORECASE)

    # === STEP 6.5: More specific typo fixes ===
    specific_typos = {
        r'\bblaksi hcolor\b': 'blackish color',
        r'\bhiglights\b': 'highlights',
        r'\bbuzszzed\b': 'buzzed',
        r'\bo nleft\b': 'on left',
        r'\bmultoclored\b': 'multicolored',
    }

    for pattern, replacement in specific_typos.items():
        caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)

    # === STEP 7: Clean up spacing and formatting ===
    # Remove double spaces
    caption = re.sub(r'\s+', ' ', caption)

    # Remove double commas
    caption = re.sub(r',\s*,+', ',', caption)

    # Normalize comma spacing
    caption = re.sub(r'\s*,\s*', ', ', caption)

    # Remove trailing/leading spaces
    caption = caption.strip()

    # === STEP 8: Ensure consistent hex code placement ===
    # Make sure hex codes are always in parentheses with #
    caption = re.sub(r'\(#([0-9a-fA-F]{6})\)', r'(#\1)', caption)

    return caption

def main():
    print("="*100)
    print("COMPREHENSIVE CAPTION ENHANCEMENT")
    print("="*100)
    print()
    print("Enhancements:")
    print("  ✓ Fix remaining typos")
    print("  ✓ Remove redundancy")
    print("  ✓ Improve grammar and flow")
    print("  ✓ Standardize formatting")
    print("  ✓ Better templating")
    print("  ✓ Preserve ALL detail")
    print()

    txt_files = sorted([f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')])

    changed_count = 0
    examples_shown = 0

    for filename in txt_files:
        # Read original
        txt_path = os.path.join(TRAINING_DIR, filename)
        with open(txt_path, 'r') as f:
            original = f.read().strip()

        # Enhance
        enhanced = enhance_caption(original, filename)

        # Save
        output_path = os.path.join(OUTPUT_DIR, filename)
        with open(output_path, 'w') as f:
            f.write(enhanced)

        # Track changes
        if original != enhanced:
            changed_count += 1

            # Show first few examples
            if examples_shown < 5:
                print(f"[{changed_count}] {filename}")
                print(f"  BEFORE: {original[:120]}...")
                print(f"  AFTER:  {enhanced[:120]}...")
                print()
                examples_shown += 1

    print()
    print("="*100)
    print("ENHANCEMENT COMPLETE")
    print("="*100)
    print()
    print(f"✅ Processed: {len(txt_files)} files")
    print(f"📝 Enhanced: {changed_count} files")
    print(f"✓  Already clean: {len(txt_files) - changed_count} files")
    print()

if __name__ == "__main__":
    main()
