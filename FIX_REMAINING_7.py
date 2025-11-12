#!/usr/bin/env python3
"""
Fix the remaining 7 captions with concatenated "wearing" issues
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")

def fix_remaining(cap):
    """Fix concatenated wearing patterns"""

    # Fix concatenated "wearing stubble/beard/etc"
    cap = re.sub(r'(\w+)wearing\s+(stubble|beard|mustache|goatee)', r'\1, with \2', cap, flags=re.I)

    # Fix "stubble/facial hair" patterns
    cap = re.sub(r'stubble/facial hair fuul beard', 'full beard', cap, flags=re.I)

    # Fix "with all cpatterns"
    cap = re.sub(r'with all cpatterns and shades of', 'with', cap, flags=re.I)

    # Fix duplicate eyes
    if cap.count(' eyes') > 1:
        # Keep last eye color mention
        eye_pattern = r'\b[\w\s]+ eyes\b'
        matches = list(re.finditer(eye_pattern, cap, flags=re.I))
        if len(matches) > 1:
            for match in matches[:-1]:
                start, end = match.start(), match.end()
                if end < len(cap) and cap[end:end+2] == ', ':
                    end += 2
                cap = cap[:start] + cap[end:]

    # Clean up spacing
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)

    return cap.strip()

# Fix the 7 problematic files
files = [
    "lad_029_famous4.txt",
    "lad_054_sterlingglasses.txt",
    "lad_066_napoli2.txt",
    "lad_068_mayor.txt",
    "lad_078_btoshi.txt",
    "lad_081_iggy2.txt",
    "lad_105_inkspired.txt"
]

print("🔧 Fixing remaining 7 captions\n")

for filename in files:
    filepath = SOURCE / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            original = f.read().strip()

        fixed = fix_remaining(original)

        with open(filepath, 'w') as f:
            f.write(fixed)

        print(f"✅ {filename}")
        print(f"   BEFORE: {original[:80]}...")
        print(f"   AFTER:  {fixed[:80]}...")
        print()

print("🎉 Done!")
