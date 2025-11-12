#!/usr/bin/env python3
"""
CAREFUL DUPLICATE EYE FIX - Targeted fix for specific duplicate eye patterns
Only fixes clear duplicates, doesn't touch anything else
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")

def careful_fix_duplicate_eyes(cap):
    """Carefully fix only clear duplicate eye patterns"""

    # Pattern 1: "red eyes/pink eyes, ... blue eyes" → keep "blue eyes"
    if 'red eyes/pink eyes' in cap.lower() and 'blue eyes' in cap.lower():
        cap = re.sub(r'red eyes/pink eyes,\s*', '', cap, flags=re.I)

    # Pattern 2: "purple/periwinkle deep eyes, ... blue eyes" → keep "blue eyes"
    if 'purple/periwinkle deep eyes' in cap.lower() and 'blue eyes' in cap.lower():
        cap = re.sub(r'purple/periwinkle deep eyes,\s*', '', cap, flags=re.I)

    # Pattern 3: "medium brown light brown eyes" → "medium brown eyes"
    cap = re.sub(r'medium brown light brown eyes', 'medium brown eyes', cap, flags=re.I)

    # Pattern 4: "light brown medium brown eyes" → "light brown eyes"
    cap = re.sub(r'light brown medium brown eyes', 'light brown eyes', cap, flags=re.I)

    # Clean up spacing
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)

    return cap.strip()

print("🔍 CAREFUL DUPLICATE EYE FIX - Only targeting specific duplicates\n")

fixed_count = 0
for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    # Only fix files that have known duplicate patterns
    if any([
        'red eyes/pink eyes' in original.lower(),
        'purple/periwinkle deep eyes' in original.lower(),
        'medium brown light brown eyes' in original.lower(),
        'light brown medium brown eyes' in original.lower()
    ]):
        fixed = careful_fix_duplicate_eyes(original)

        if fixed != original:
            with open(txt_file, 'w') as f:
                f.write(fixed)

            print(f"✅ {txt_file.name}")
            print(f"   BEFORE: {original}")
            print(f"   AFTER:  {fixed}")
            print()
            fixed_count += 1

print(f"🎉 DONE! Fixed {fixed_count} captions with duplicate eyes")
