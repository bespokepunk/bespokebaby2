#!/usr/bin/env python3
"""
NUCLEAR CAPTION FIX - Most aggressive cleaning possible
Fixes even the most severely broken captions
"""

import re
from pathlib import Path
from PIL import Image
from collections import Counter

SOURCE = Path("runpod_package/training_data")
OUTPUT = Path("FINAL_WORLD_CLASS_CAPTIONS")
OUTPUT.mkdir(exist_ok=True)

def analyze_eye_region(img_path):
    """Infer eye color from middle region"""
    try:
        img = Image.open(img_path).convert('RGB')
        w, h = img.size
        pixels = []
        for y in range(h//3, 2*h//3):
            for x in range(w):
                pixels.append(img.getpixel((x, y)))

        counts = Counter(pixels)
        for (r,g,b), _ in counts.most_common(20):
            if 70 <= r <= 140 and 35 <= g <= 90 and 15 <= b <= 65:
                return "brown eyes"
            if b > max(r,g) + 30 and b > 90:
                return "blue eyes"
            if g > max(r,b) + 20:
                return "green eyes"
            if abs(r-g) < 15 and abs(g-b) < 15 and 90 < r < 170:
                return "gray eyes"
        return "brown eyes"
    except:
        return "brown eyes"

def nuclear_clean(cap, img_path):
    """NUCLEAR cleaning - fixes everything"""

    # 1. REMOVE artifacts and junk
    cap = re.sub(r'hard color borders', '', cap, flags=re.I)
    cap = re.sub(r'sharp pixel edges', '', cap, flags=re.I)
    cap = re.sub(r'palette:[^,]*', '', cap, flags=re.I)
    cap = re.sub(r'#[0-9a-fA-F]{6}', '', cap)

    # 2. REMOVE unwanted words
    cap = re.sub(r'\bsimple\s+', '', cap, flags=re.I)
    cap = re.sub(r'\bmale\b', '', cap, flags=re.I)
    cap = re.sub(r'\bfemale\b', '', cap, flags=re.I)
    cap = re.sub(r'\bhispanic\b', '', cap, flags=re.I)
    cap = re.sub(r'\blips\b,?', '', cap, flags=re.I)
    cap = re.sub(r',\s*lips\b', '', cap, flags=re.I)

    # 3. FIX BROKEN DUPLICATE TEXT PATTERNS
    # Remove obvious duplicates like "wearing short layered but longe... hairlight light sage"
    # Strategy: if we see the same phrase twice in a row, keep only one
    parts = cap.split(',')
    cleaned_parts = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        # Check if this part is very similar to previous (broken duplicate)
        if cleaned_parts and len(part) > 20:
            prev = cleaned_parts[-1]
            # If more than 50% overlap, skip this part
            overlap = sum(1 for a, b in zip(part[:20], prev[-20:]) if a == b)
            if overlap > 10:
                continue
        cleaned_parts.append(part)
    cap = ', '.join(cleaned_parts)

    # 4. REMOVE obviously broken patterns
    cap = re.sub(r'wearing [^,]*?hairlight', '', cap, flags=re.I)
    cap = re.sub(r'short layered but longe', 'short layered', cap, flags=re.I)
    cap = re.sub(r'on top of a plain\s+', '', cap, flags=re.I)
    cap = re.sub(r'for a wedding perhaps and a\s+', '', cap, flags=re.I)
    cap = re.sub(r'collaredshirt', 'collared shirt', cap, flags=re.I)
    cap = re.sub(r'(gold|silver) chain thick', r'\1 chain', cap, flags=re.I)
    cap = re.sub(r'tee shirt', 't-shirt', cap, flags=re.I)
    cap = re.sub(r'unbuttoneded', 'unbuttoned', cap, flags=re.I)

    # 5. FIX "wearing" issues
    cap = re.sub(r'wearing\s+(combo rimmed glasses|glasses|rimmed sunglasses|sunglasses)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+(gold chain|silver chain)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+([a-z\s]*?)(stubble|beard|mustache|goatee)', r'with \1\2', cap, flags=re.I)

    # Fix naked facial hair (missing "with")
    cap = re.sub(r',\s*(stubble|beard|mustache|goatee),', r', with \1,', cap, flags=re.I)

    # Remove "wearing" before accessories/hats (but keep for clothing)
    cap = re.sub(r'wearing\s+([A-Z][a-z]+\s+(?:Blue|Red|Green|Purple|Black|White|Grey|Gray|Yellow)[^,]*(?:cap|hat|beanie))', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+(gray|grey|red|blue|green|purple|orange|yellow|black|white)\s+baseball\s+cap', r'\1 baseball cap', cap, flags=re.I)

    # 6. FIX backgrounds
    cap = re.sub(r'split background', 'divided background', cap, flags=re.I)
    cap = re.sub(r'solid background', 'background', cap, flags=re.I)

    # 7. FIX duplicate "bald" mentions
    if cap.lower().count('bald') > 1:
        # Keep first bald, remove others
        parts = cap.split(', ')
        seen_bald = False
        new_parts = []
        for part in parts:
            if 'bald' in part.lower():
                if not seen_bald:
                    new_parts.append(part)
                    seen_bald = True
                # Skip subsequent "bald" mentions
            else:
                new_parts.append(part)
        cap = ', '.join(new_parts)

    # 8. ENSURE eye color exists
    eye_pattern = r'\b(brown|blue|green|gray|grey|hazel|black|dark|light honey brown|dark brown|light brown|medium brown|dual colored)\s+eyes\b'
    has_eyes = bool(re.search(eye_pattern, cap, flags=re.I))
    has_broken_eyes = ', eyes,' in cap.lower() or cap.lower().endswith(', eyes')

    if not has_eyes or has_broken_eyes:
        cap = re.sub(r',\s*eyes\s*,', ',', cap, flags=re.I)
        cap = re.sub(r',\s*eyes\s*$', '', cap, flags=re.I)
        inferred = analyze_eye_region(img_path)
        cap = re.sub(r'(,\s*(?:light|medium|dark|tan|pale)(?:\s+light|\s+dark)?\s+(?:skin|black skin|brown skin))', f', {inferred}\\1', cap)

    # 9. REMOVE duplicate eye colors (keep last)
    eye_matches = list(re.finditer(eye_pattern, cap, flags=re.I))
    if len(eye_matches) > 1:
        for match in eye_matches[:-1]:
            start, end = match.start(), match.end()
            # Remove with comma handling
            if end < len(cap) and cap[end:end+2] == ', ':
                end += 2
            elif start > 0 and cap[start-2:start] == ', ':
                start -= 2
            cap = cap[:start] + cap[end:]
            eye_matches = list(re.finditer(eye_pattern, cap, flags=re.I))

    # 10. CLEAN UP spacing/commas
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ', ', cap)
    cap = cap.strip().rstrip(', ')

    # 11. ENSURE proper ending
    if not cap.endswith('pixel art style'):
        cap = re.sub(r',?\s*pixel art style$', '', cap, flags=re.I)
        cap = re.sub(r',?\s*hard color borders.*$', '', cap, flags=re.I)
        cap = re.sub(r',?\s*sharp pixel.*$', '', cap, flags=re.I)
        cap += ', pixel art style'

    # Remove duplicate ending
    cap = re.sub(r'(, pixel art style)+', ', pixel art style', cap, flags=re.I)

    # Final cleanup
    cap = re.sub(r',\s*,+', ', ', cap)
    cap = cap.strip().rstrip(',').strip()
    if not cap.endswith('pixel art style'):
        cap += ', pixel art style'

    return cap

# PROCESS ALL 203
print("☢️  NUCLEAR CAPTION FIX - Maximum aggression\n")

for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    img_file = txt_file.with_suffix('.png')
    cleaned = nuclear_clean(original, img_file)

    out_file = OUTPUT / txt_file.name
    with open(out_file, 'w') as f:
        f.write(cleaned)

    reduction = round((len(original) - len(cleaned)) / len(original) * 100, 1)
    status = "✅" if 150 <= len(cleaned) <= 280 else "📊"
    print(f"{status} {txt_file.name}: {len(original)} → {len(cleaned)} chars ({reduction}%)")

print(f"\n✨ DONE! All 203 captions in: {OUTPUT}/")
