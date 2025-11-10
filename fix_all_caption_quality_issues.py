#!/usr/bin/env python3
"""
Fix all caption quality issues:
- Remove garbage text
- Remove duplicates
- Fix typos
- Fix spacing
- Standardize capitalization
"""

import os
import re

TRAINING_DIR = "sd15_training_512"

# Common typos
TYPOS = {
    r'\beand\b': 'and',
    r'\bmeidum\b': 'medium',
    r'\bnekclace\b': 'necklace',
    r'\bckip\b': 'clip',
    r'\bshari\b': 'shiny',
    r'\bblackgrey\b': 'black-grey',
    r'\ban\s+reflection\b': 'and reflection',
    r'\bwoudl\b': 'would',
    r'\bjsut\b': 'just',
    r'\biwth\b': 'with',
    r'\bjewisah\b': 'jewish',
    r'\bskined\b': 'skinned',
    r'\bpgimented\b': 'pigmented',
    r'\braspervyy\b': 'raspberry',
    r'\bton\b(?! of)': 'tone',  # "ton" -> "tone" except "ton of"
}

def fix_caption(caption, filename):
    """Fix all issues in a caption"""
    original = caption

    # Remove obvious garbage text patterns
    # "wearing but those woudl jsut be darker brown etc so adjust for that"
    caption = re.sub(
        r'wearing but those [^,]*adjust for that',
        '',
        caption,
        flags=re.IGNORECASE
    )

    # Remove duplicate hair descriptions
    # Find pattern: "hair description (#hex), wearing [same hair description]"
    # This is complex, so let's handle specific patterns

    # Fix spacing issues
    caption = re.sub(r'\s+', ' ', caption)  # Double spaces
    caption = re.sub(r'\s*,\s*', ', ', caption)  # Comma spacing
    caption = re.sub(r',\s*,+', ', ', caption)  # Double commas

    # Fix missing commas after hex codes
    caption = re.sub(r'\(#([0-9a-fA-F]{6})\)([a-z])', r'(#\1), \2', caption)

    # Fix typos
    for pattern, replacement in TYPOS.items():
        caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)

    # Fix capitalization issues
    # Lowercase "Sandy" when mid-sentence
    caption = re.sub(r',\s+Sandy\s+/', ', sandy /', caption)

    # Normalize spacing again
    caption = re.sub(r'\s+', ' ', caption)
    caption = caption.strip()

    return caption

def main():
    print("="*100)
    print("FIXING ALL CAPTION QUALITY ISSUES")
    print("="*100)
    print()

    fixed_count = 0

    for txt_file in sorted(os.listdir(TRAINING_DIR)):
        if not txt_file.endswith('.txt'):
            continue

        txt_path = os.path.join(TRAINING_DIR, txt_file)

        with open(txt_path, 'r') as f:
            caption = f.read().strip()

        original = caption
        fixed = fix_caption(caption, txt_file)

        if original != fixed:
            fixed_count += 1

            with open(txt_path, 'w') as f:
                f.write(fixed)

            if fixed_count <= 15:
                print(f"[{fixed_count}] {txt_file}")
                print(f"  Length: {len(original)} -> {len(fixed)}")
                if len(fixed) < len(original) - 10:
                    print(f"  Removed significant text")
                print()

    print()
    print("="*100)
    print("FIX COMPLETE")
    print("="*100)
    print()
    print(f"✅ Fixed: {fixed_count} files")
    print(f"✓  Already clean: {len([f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')]) - fixed_count} files")
    print()

if __name__ == "__main__":
    main()
