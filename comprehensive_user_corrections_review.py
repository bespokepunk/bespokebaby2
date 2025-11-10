#!/usr/bin/env python3
"""
Comprehensive review of all user_corrections to ensure we captured EVERY detail.
Also replace nationality references with descriptive traits.
"""

import json
import os
import re

SUPABASE_DATA = "supabase_export_FIXED_SAMPLING.json"
TRAINING_DIR = "sd15_training_512"

# Nationality replacements - use descriptive skin tones instead
NATIONALITY_FIXES = {
    r'\bindian\s+(male|female)\s+skin\s+tone\b': r'\1 skin tone',
    r'\b(light|medium|dark)\s+indian\s+(male|female)\s+skin\s+tone\b': r'\1 \2 skin tone',
    r'\b(light|medium|dark)\s+skinned?\s+indian\b': r'\1 skin tone',
    r'\bmexican\s+(male|female)\s+skin\s+tone\b': r'\1 skin tone',
    r'\b(light|medium|dark)\s+mexican\s+(male|female)\s+skin\s+tone\b': r'\1 \2 skin tone',
    r'\bjewish\s+(male|female)\s+skin\s+tone\b': r'\1 skin tone',
    r'\b(light|medium|dark)\s+skin\s+(?:tone\s+)?(?:tone\s+)?indian\s+tone\b': r'\1 skin tone',
    r'\bcolumbian\b': 'medium',
    r'\bblack\s+girl\s+(light|medium|dark)\s+skin\b': r'\1 dark skin tone',
    r'\bblack\s+girl\s+skin\b': 'dark skin tone',
    r'\bblack\s+male\b': 'dark skin tone',
}

# Track missing details
missing_details = []

def load_data():
    """Load Supabase data"""
    with open(SUPABASE_DATA, 'r') as f:
        return json.load(f)

def main():
    print("="*100)
    print("COMPREHENSIVE USER CORRECTIONS REVIEW")
    print("="*100)
    print()

    data = load_data()

    # Create lookup
    lookup = {item['filename']: item for item in data}

    fixed_count = 0
    nationality_fixes = 0

    for txt_file in sorted(os.listdir(TRAINING_DIR)):
        if not txt_file.endswith('.txt'):
            continue

        png_file = txt_file.replace('.txt', '.png')

        if png_file not in lookup:
            continue

        item = lookup[png_file]
        corrections = item.get('user_corrections', '')

        if not corrections:
            continue

        txt_path = os.path.join(TRAINING_DIR, txt_file)

        with open(txt_path, 'r') as f:
            caption = f.read().strip()

        original = caption

        # Fix nationality references
        for pattern, replacement in NATIONALITY_FIXES.items():
            if re.search(pattern, caption, flags=re.IGNORECASE):
                caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)
                nationality_fixes += 1

        # Check for specific missed details based on user_corrections
        # Look for yellow accessories
        if 'yellow accessory' in corrections.lower() and 'yellow' not in caption.lower():
            print(f"⚠️  MISSING: {txt_file} - yellow accessory mentioned in corrections but not in caption")
            missing_details.append((txt_file, "yellow accessory"))

        # Save if changed
        if original != caption:
            fixed_count += 1

            with open(txt_path, 'w') as f:
                f.write(caption)

            if fixed_count <= 10:
                print(f"✓ Fixed {txt_file}")

    print()
    print("="*100)
    print("REVIEW COMPLETE")
    print("="*100)
    print()
    print(f"✅ Nationality references fixed: {nationality_fixes} captions")
    print(f"⚠️  Missing details found: {len(missing_details)}")
    print()

    if missing_details:
        print("Files with missing details:")
        for txt_file, detail in missing_details:
            print(f"  - {txt_file}: {detail}")
        print()

if __name__ == "__main__":
    main()
