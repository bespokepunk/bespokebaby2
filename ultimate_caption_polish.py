#!/usr/bin/env python3
"""
ULTIMATE CAPTION POLISHING - Final pass to achieve WORLD CLASS quality
"""

import os
import re

SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

# All remaining typos
TYPO_FIXES = {
    "tone sthrough": "tones through",
    "brighth ": "bright ",
    "fillhzel": "fill, hazel",
    "hdangling": "dangling",
    "cgold": "gold",
    "colroed": "colored",
    "grradient": "gradient",
    "colore ": "colored ",
    "colros": "colors",
    "colothing": "clothing",
    "hippe ": "hippie ",
    "bnounce": "bounce",
    "falter to face": "frame face",
}

def remove_redundant_wearing(text):
    """Consolidate multiple 'wearing' statements"""
    # Count how many times "wearing" appears
    wearing_count = text.count("wearing")

    if wearing_count > 2:
        # Replace excessive "wearing" with commas after the first couple
        parts = text.split("wearing")
        if len(parts) > 3:
            # Keep first 2 "wearing", replace rest with commas
            fixed = "wearing".join(parts[:3])
            for part in parts[3:]:
                if part.strip():
                    fixed += ", " + part.strip()
            return fixed

    return text

def fix_caption(text):
    """Apply all fixes"""

    # Fix typos
    for typo, correct in TYPO_FIXES.items():
        text = text.replace(typo, correct)

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

    # Reduce redundant "wearing"
    text = remove_redundant_wearing(text)

    # Fix double spaces and punctuation
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r',\s*,', ',', text)
    text = text.strip()

    return text

def main():
    print("🎨 ULTIMATE CAPTION POLISHING...\n")

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
            print(f"  ✅ Polished: {filename}")
            fixed_count += 1

    print(f"\n✨ Polished {fixed_count} caption files!")

if __name__ == "__main__":
    main()
