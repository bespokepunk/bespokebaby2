#!/usr/bin/env python3
"""
FINAL EDGE CASE FIX - Handle unusual eye color patterns and remaining duplicates
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")

def fix_edge_cases(cap):
    """Fix edge cases like multiple eye colors, unusual patterns"""

    # Pattern to match ANY mention of eyes (standard and non-standard colors)
    # This will catch: "brown eyes", "blue eyes", "red eyes/pink eyes", "purple/periwinkle deep eyes", etc.
    all_eye_patterns = [
        r'\b[\w/]+\s+eyes',  # Standard: "brown eyes", "red eyes/pink eyes"
        r'\b[\w/]+\s+[\w/]+\s+eyes',  # Two words: "light brown eyes", "medium brown light brown eyes"
        r'\b[\w/]+\s+[\w/]+\s+[\w/]+\s+eyes',  # Three words: "light honey brown eyes"
        r'\b[\w/]+\s+deep\s+eyes',  # Special: "purple/periwinkle deep eyes"
    ]

    # Find all eye mentions
    eye_mentions = []
    for pattern in all_eye_patterns:
        for match in re.finditer(pattern, cap, flags=re.I):
            eye_mentions.append((match.start(), match.end(), match.group()))

    # Remove duplicates by position
    eye_mentions = sorted(set(eye_mentions), key=lambda x: x[0])

    # If we have multiple eye mentions, keep only the LAST standard one
    if len(eye_mentions) > 1:
        # Find the last standard eye color (brown, blue, green, gray)
        standard_pattern = r'\b(brown|blue|green|gray|grey)\s+eyes\b'
        standard_eyes = []
        for start, end, text in eye_mentions:
            if re.search(standard_pattern, text, flags=re.I):
                standard_eyes.append((start, end, text))

        if standard_eyes:
            # Keep the last standard eye color, remove all others
            keep_start, keep_end, keep_text = standard_eyes[-1]

            # Remove all other eye mentions
            for start, end, text in reversed(eye_mentions):
                if start != keep_start:
                    # Remove this mention
                    cap = cap[:start] + cap[end:]
                    # Clean up spacing
                    cap = re.sub(r',\s*,', ',', cap)

    # Clean up spacing
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)

    # Fix "medium brown light brown eyes" → "medium brown eyes"
    cap = re.sub(r'medium brown light brown eyes', 'medium brown eyes', cap, flags=re.I)
    cap = re.sub(r'light brown medium brown eyes', 'light brown eyes', cap, flags=re.I)

    return cap.strip()

print("🔧 FINAL EDGE CASE FIX - Unusual eye patterns\n")

fixed_count = 0
for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    fixed = fix_edge_cases(original)

    if fixed != original:
        with open(txt_file, 'w') as f:
            f.write(fixed)

        print(f"✅ {txt_file.name}")
        print(f"   BEFORE: {original[:100]}...")
        print(f"   AFTER:  {fixed[:100]}...")
        print()
        fixed_count += 1

print(f"🎉 DONE! Fixed {fixed_count} captions with edge cases")
