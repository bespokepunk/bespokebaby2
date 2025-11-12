#!/usr/bin/env python3
"""
TRUE SIMPLIFIER - Actually simplify captions to world-class 150-200 char format
Like SD15_PERFECT which got 9/10 quality with ~180 char captions
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")
OUTPUT = Path("SIMPLIFIED_WORLD_CLASS")
OUTPUT.mkdir(exist_ok=True)

def true_simplify(cap):
    """Actually simplify - remove excessive detail"""

    # 1. Simplify overly detailed hair/cap descriptions
    cap = re.sub(r'gray baseball cap with multicolored \([^)]+\) logo in the center', 'gray cap', cap, flags=re.I)
    cap = re.sub(r'baseball cap with [^,]+', 'cap', cap, flags=re.I)
    cap = re.sub(r'baseball cap \([^)]+\)', 'cap', cap, flags=re.I)
    cap = re.sub(r'baseball cap', 'cap', cap, flags=re.I)

    # 2. Simplify skin descriptions - remove "tone"
    cap = re.sub(r'(\w+)\s+skin tone', r'\1 skin', cap, flags=re.I)

    # 3. Simplify background descriptions
    cap = re.sub(r'checkered brick background', 'checkered background', cap, flags=re.I)
    cap = re.sub(r'divided background', 'background', cap, flags=re.I)
    cap = re.sub(r'gradient background', 'background', cap, flags=re.I)
    cap = re.sub(r'(\w+)\s+background', r'\1 background', cap, flags=re.I)

    # 4. Simplify color descriptions
    cap = re.sub(r'dark brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'light brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'light honey brown eyes', 'brown eyes', cap, flags=re.I)
    cap = re.sub(r'medium brown eyes', 'brown eyes', cap, flags=re.I)

    # 5. Simplify clothing descriptions
    cap = re.sub(r'medium grey shirt', 'grey shirt', cap, flags=re.I)
    cap = re.sub(r'medium (\w+) shirt', r'\1 shirt', cap, flags=re.I)

    # 6. Remove excessive hair detail
    cap = re.sub(r'short layered medium brown middle parted decently thick hair', 'brown hair', cap, flags=re.I)
    cap = re.sub(r'short layered but longe medium brown[^,]*', 'brown hair', cap, flags=re.I)
    cap = re.sub(r'medium brown middle parted[^,]*hair', 'brown hair', cap, flags=re.I)

    # 7. Simplify complex clothing
    cap = re.sub(r'a salmon collared shirt dark black grey suit', 'suit and shirt', cap, flags=re.I)
    cap = re.sub(r'salmon collared shirt and dark[^,]+suit', 'suit and shirt', cap, flags=re.I)

    # 8. Remove "hair," at beginning when there's detailed hair later
    cap = re.sub(r',\s*hair,\s*', ', ', cap, flags=re.I)

    # 9. Simplify eye color variations
    cap = re.sub(r'light sage green eyes', 'green eyes', cap, flags=re.I)

    # 10. Remove generic "clothing"
    cap = re.sub(r',\s*clothing,', ',', cap, flags=re.I)
    cap = re.sub(r',\s*clothing\s*,', ',', cap, flags=re.I)

    # 11. Clean up spacing
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)
    cap = cap.strip().rstrip(', ')

    # 12. Ensure ending
    if not cap.endswith('pixel art style'):
        cap += ', pixel art style'

    return cap

print("✂️ TRUE SIMPLIFIER - Reducing to world-class format\n")
print(f"Target: 150-200 characters (SD15_PERFECT averaged ~180)\n")

total_before = 0
total_after = 0
shortened_count = 0

for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    simplified = true_simplify(original)

    out_file = OUTPUT / txt_file.name
    with open(out_file, 'w') as f:
        f.write(simplified)

    before = len(original)
    after = len(simplified)
    total_before += before
    total_after += after

    if after < before:
        shortened_count += 1

    reduction = round((before - after) / before * 100, 1) if before > 0 else 0
    status = "✅" if 150 <= after <= 220 else "📊"

    print(f"{status} {txt_file.name}: {before} → {after} chars ({reduction}% reduction)")

avg_before = total_before // len(list(SOURCE.glob("*.txt")))
avg_after = total_after // len(list(SOURCE.glob("*.txt")))

print(f"\n📊 SUMMARY:")
print(f"   Average before: {avg_before} chars")
print(f"   Average after: {avg_after} chars")
print(f"   Shortened: {shortened_count}/{len(list(SOURCE.glob('*.txt')))}")
print(f"\n✨ DONE! Simplified captions in: {OUTPUT}/")
