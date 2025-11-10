#!/usr/bin/env python3
"""
Remove ALL accessories that weren't explicitly specified by the user.

The original captions incorrectly added "wearing earrings" to most images
even though the user never specified earrings in the accessories field.
"""

import json
import os
import re

SUPABASE_DATA = "supabase_export_FIXED_SAMPLING.json"
TRAINING_DIR = "sd15_training_512"

def main():
    print("="*100)
    print("REMOVING INCORRECTLY ADDED ACCESSORIES")
    print("="*100)
    print()

    # Load Supabase data to check what was actually specified
    with open(SUPABASE_DATA, 'r') as f:
        data = json.load(f)

    # Create lookup by filename
    lookup = {item['filename']: item for item in data}

    fixed_count = 0

    for txt_file in sorted(os.listdir(TRAINING_DIR)):
        if not txt_file.endswith('.txt'):
            continue

        png_file = txt_file.replace('.txt', '.png')

        if png_file not in lookup:
            print(f"⚠️  Warning: {png_file} not found in Supabase data")
            continue

        item = lookup[png_file]
        accessories = item.get('accessories', '')

        txt_path = os.path.join(TRAINING_DIR, txt_file)

        with open(txt_path, 'r') as f:
            caption = f.read().strip()

        original = caption

        # Remove "wearing earrings (#hex)" if earrings not specified
        if accessories is None or 'earring' not in accessories.lower():
            # Match "wearing earrings (#hex), " or ", wearing earrings (#hex)"
            caption = re.sub(r',?\s*wearing earrings \(#[0-9a-fA-F]{6}\),?\s*', '', caption)
            caption = re.sub(r',?\s*wearing earing \(#[0-9a-fA-F]{6}\),?\s*', '', caption)

        # Remove "wearing necklace (#hex)" if necklace not specified
        if accessories is None or 'necklace' not in accessories.lower():
            caption = re.sub(r',?\s*wearing necklaces? \(#[0-9a-fA-F]{6}\),?\s*', '', caption)

        # Clean up any double commas or spacing issues
        caption = re.sub(r',\s*,+', ', ', caption)
        caption = re.sub(r'\s+,', ',', caption)
        caption = re.sub(r',\s+', ', ', caption)
        caption = re.sub(r'\s+', ' ', caption)
        caption = caption.strip()

        if original != caption:
            fixed_count += 1

            with open(txt_path, 'w') as f:
                f.write(caption)

            if fixed_count <= 5:
                print(f"[{fixed_count}] {txt_file}")
                print(f"  Removed incorrectly added accessory")
                print()

    print()
    print("="*100)
    print("ACCESSORY REMOVAL COMPLETE")
    print("="*100)
    print()
    print(f"✅ Fixed: {fixed_count} files")
    print(f"✓  Already correct: {len([f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')]) - fixed_count} files")
    print()

if __name__ == "__main__":
    main()
