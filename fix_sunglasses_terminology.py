#!/usr/bin/env python3
"""
Fix sunglasses terminology:
- "innerlips" → "lenses"
- "inners" → "lenses"
"""

import os
import re

TRAINING_DIR = "sd15_training_512"

fixes_made = []

for txt_file in sorted(os.listdir(TRAINING_DIR)):
    if not txt_file.endswith('.txt'):
        continue

    txt_path = os.path.join(TRAINING_DIR, txt_file)

    with open(txt_path, 'r') as f:
        caption = f.read().strip()

    original = caption

    # Fix "innerlips" → "lenses"
    caption = re.sub(r'\binnerlips\b', 'lenses', caption, flags=re.IGNORECASE)

    # Fix "inners" (in context of sunglasses) → "lenses"
    caption = re.sub(r'\binners\b', 'lenses', caption, flags=re.IGNORECASE)

    # Fix formatting issues from these changes
    # "lenseswearing" → "lenses, wearing"
    caption = re.sub(r'lenseswearing', 'lenses, wearing', caption, flags=re.IGNORECASE)

    # "reflectionlips" → "reflection, lips"
    caption = re.sub(r'reflectionlips', 'reflection, lips', caption, flags=re.IGNORECASE)

    # Clean up spacing
    caption = re.sub(r'\s+', ' ', caption)
    caption = re.sub(r'\s*,\s*', ', ', caption)
    caption = re.sub(r',\s*,+', ', ', caption)

    caption = caption.strip()

    if original != caption:
        fixes_made.append(txt_file)
        with open(txt_path, 'w') as f:
            f.write(caption)

        print(f"✓ {txt_file}")
        snippet_start = max(0, original.lower().find('sunglasses') - 20)
        snippet_end = min(len(original), snippet_start + 100)
        print(f"  Before: ...{original[snippet_start:snippet_end]}...")
        print(f"  After:  ...{caption[snippet_start:snippet_end]}...")
        print()

print()
print(f"Fixed terminology in {len(fixes_made)} files")
