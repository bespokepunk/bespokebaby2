#!/usr/bin/env python3
"""
BALANCED SIMPLIFIER - Keep important details, remove junk and verbosity
- Keep: logos, accessories, unique features, facial hair colors
- Remove: junk, broken text, excessive detail
- Simplify: overly verbose descriptions
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")
OUTPUT = Path("FINAL_WORLD_CLASS_CAPTIONS")  # Overwrite in place

def balanced_simplify(cap):
    """Simplify while keeping important visual details"""

    # 1. Simplify overly detailed descriptions but KEEP the key info
    # "gray baseball cap with multicolored (red gold and white) logo in the center"
    # → "gray cap with multicolored logo"
    cap = re.sub(r'baseball cap with multicolored \([^)]+\) logo in the center', 'cap with multicolored logo', cap, flags=re.I)
    cap = re.sub(r'baseball cap with ([^,]+) logo', r'cap with \1 logo', cap, flags=re.I)

    # Simplify "baseball cap" to "cap" when no logo mentioned
    cap = re.sub(r'baseball cap(?! with)', 'cap', cap, flags=re.I)

    # 2. Simplify skin tone (remove "tone" but keep color)
    cap = re.sub(r'(\w+)\s+skin tone', r'\1 skin', cap, flags=re.I)

    # 3. Simplify overly detailed hair BUT keep color
    cap = re.sub(r'short layered medium brown middle parted decently thick hair', 'medium brown hair', cap, flags=re.I)
    cap = re.sub(r'short layered but longe medium brown[^,]*', 'medium brown hair', cap, flags=re.I)

    # 4. Simplify eye color variations to standard colors
    cap = re.sub(r'light honey brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'dark brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'light brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'medium brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'light sage green eyes', 'green eyes', cap, flags=re.I)

    # 5. Simplify backgrounds (but keep descriptive ones like "checkered")
    cap = re.sub(r'divided background', 'background', cap, flags=re.I)
    cap = re.sub(r'gradient background', 'background', cap, flags=re.I)
    # Remove "brick" from checkered - pattern is what matters, not material
    cap = re.sub(r'checkered brick background', 'checkered background', cap, flags=re.I)

    # 6. Simplify clothing slightly
    cap = re.sub(r'medium grey shirt', 'grey shirt', cap, flags=re.I)
    cap = re.sub(r'medium (\w+) shirt', r'\1 shirt', cap, flags=re.I)
    cap = re.sub(r'a salmon collared shirt dark black grey suit', 'salmon shirt and dark grey suit', cap, flags=re.I)

    # 7. Remove generic "clothing" placeholder
    cap = re.sub(r',\s*clothing,', ',', cap, flags=re.I)
    cap = re.sub(r',\s*clothing\s*$', '', cap, flags=re.I)

    # 8. Remove "hair," when it's just a placeholder
    cap = re.sub(r',\s*hair,\s*', ', ', cap, flags=re.I)

    # 9. Clean up spacing
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)
    cap = cap.strip().rstrip(', ')

    # 10. Ensure ending
    if not cap.endswith('pixel art style'):
        cap += ', pixel art style'

    return cap

print("⚖️  BALANCED SIMPLIFIER - Keep details, remove junk\n")

total_before = 0
total_after = 0

for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    simplified = balanced_simplify(original)

    with open(txt_file, 'w') as f:
        f.write(simplified)

    before = len(original)
    after = len(simplified)
    total_before += before
    total_after += after

    reduction = round((before - after) / before * 100, 1) if before > 0 else 0

    if reduction > 5:
        status = "✂️"
    else:
        status = "✅"

    print(f"{status} {txt_file.name}: {before} → {after} chars ({reduction}% reduction)")

avg_before = total_before // len(list(SOURCE.glob("*.txt")))
avg_after = total_after // len(list(SOURCE.glob("*.txt")))

print(f"\n📊 SUMMARY:")
print(f"   Average before: {avg_before} chars")
print(f"   Average after: {avg_after} chars")
print(f"   Average reduction: {round((avg_before - avg_after) / avg_before * 100, 1)}%")
print(f"\n✨ Balanced captions in: {OUTPUT}/")
