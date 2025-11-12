#!/usr/bin/env python3
"""
FINAL POLISH PASS - Fix remaining duplicate eyes and "wearing" issues
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")
OUTPUT = Path("FINAL_WORLD_CLASS_CAPTIONS")  # Overwrite in place

def final_polish(cap):
    """Final pass to fix remaining issues"""

    # 1. Remove "wearing" before glasses/sunglasses/accessories
    cap = re.sub(r'wearing\s+(silver\s+rimmed\s+glasses|gold\s+rimmed\s+glasses|rimmed\s+glasses|rimmed\s+sunglasses|sunglasses|glasses)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+(red|blue|green|purple|orange|yellow|black|white)\s+forward\s+a\s+baseball\s+cap', r'\1 baseball cap (forward)', cap, flags=re.I)
    cap = re.sub(r'wearing\s+(red|blue|green|purple|orange|yellow|black|white)\s+baseball\s+cap', r'\1 baseball cap', cap, flags=re.I)

    # 2. Fix broken phrasing like "red forward a baseball cap"
    cap = re.sub(r'(\w+)\s+forward\s+a\s+baseball\s+cap', r'\1 baseball cap (forward)', cap, flags=re.I)

    # 3. AGGRESSIVELY remove duplicate eye colors
    # Strategy: Find all eye color mentions, keep ONLY the last one
    eye_pattern = r'\b((?:light\s+medium\s+brownred|light\s+honey\s+brown|dark\s+brown|light\s+brown|medium\s+brown|brown|blue|green|gray|grey|hazel|black|dark)\s+eyes)\b'

    eye_matches = list(re.finditer(eye_pattern, cap, flags=re.I))

    if len(eye_matches) > 1:
        # Work backwards to avoid index issues
        for match in reversed(eye_matches[:-1]):  # Keep last, remove all others
            # Remove the match and its trailing comma/space if present
            start = match.start()
            end = match.end()

            # Check if there's a comma after
            if end < len(cap) and cap[end:end+2] == ', ':
                end += 2
            # Check if there's a comma before
            elif start > 0 and cap[start-2:start] == ', ':
                start -= 2

            cap = cap[:start] + cap[end:]

    # 4. Clean up any resulting spacing issues
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)

    # 5. Fix any "wearing" that slipped through
    # Remove "wearing" before facial hair if it somehow remained
    cap = re.sub(r'wearing\s+(stubble|beard|mustache|goatee)', r'with \1', cap, flags=re.I)

    return cap.strip()

print("✨ FINAL POLISH PASS - Fixing duplicate eyes and wearing issues\n")

fixed_count = 0
for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    polished = final_polish(original)

    if polished != original:
        with open(txt_file, 'w') as f:
            f.write(polished)

        # Check what was fixed
        fixes = []
        if original.count('eyes') > polished.count('eyes'):
            fixes.append("removed dup eyes")
        if 'wearing' in original.lower() and 'wearing' not in polished.lower():
            fixes.append("removed wearing")
        if original.count('wearing') > polished.count('wearing'):
            fixes.append("reduced wearing")

        fix_str = ' + '.join(fixes) if fixes else 'cleaned'
        print(f"✅ {txt_file.name}: {fix_str}")
        fixed_count += 1

print(f"\n🎉 DONE! Fixed {fixed_count} captions")
print(f"All polished captions remain in: {OUTPUT}/")
