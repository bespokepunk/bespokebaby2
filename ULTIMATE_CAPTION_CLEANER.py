#!/usr/bin/env python3
"""
ULTIMATE CAPTION CLEANER - Handles even the most broken captions
Aggressive cleaning + Image analysis for missing features
"""

import re
from pathlib import Path
from PIL import Image
from collections import Counter

SOURCE = Path("runpod_package/training_data")
OUTPUT = Path("FINAL_WORLD_CLASS_CAPTIONS")
OUTPUT.mkdir(exist_ok=True)

def analyze_eye_region(img_path):
    """Infer eye color from middle region of image"""
    try:
        img = Image.open(img_path).convert('RGB')
        w, h = img.size
        pixels = []
        # Middle strip where eyes are
        for y in range(h//3, 2*h//3):
            for x in range(w):
                pixels.append(img.getpixel((x, y)))

        counts = Counter(pixels)
        for (r,g,b), _ in counts.most_common(20):
            # Brown eyes
            if 70 <= r <= 140 and 35 <= g <= 90 and 15 <= b <= 65:
                return "brown eyes"
            # Blue eyes
            if b > max(r,g) + 30 and b > 90:
                return "blue eyes"
            # Green eyes
            if g > max(r,b) + 20:
                return "green eyes"
            # Gray eyes
            if abs(r-g) < 15 and abs(g-b) < 15 and 90 < r < 170:
                return "gray eyes"
        return "brown eyes"  # Default fallback
    except:
        return "brown eyes"

def ultra_clean(cap, img_path):
    """ULTRA aggressive cleaning for even the worst captions"""

    # 1. REMOVE broken patterns and artifacts
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
    cap = re.sub(r'\s*\((middle eastern|mexican|italian[^)]*)\)', '', cap, flags=re.I)

    # 3. FIX DUPLICATE TEXT - remove obvious duplications
    # Split into parts and check for consecutive duplicates
    parts = [p.strip() for p in cap.split(',')]
    cleaned_parts = []
    prev = None
    for part in parts:
        # Skip if this part is very similar to previous (duplicate detection)
        if prev and part and len(part) > 10:
            # Check if this part contains the previous part or vice versa
            if part not in prev and prev not in part:
                cleaned_parts.append(part)
                prev = part
            # If it's a duplicate, skip it
        else:
            if part:  # Only add non-empty parts
                cleaned_parts.append(part)
                prev = part
    cap = ', '.join(cleaned_parts)

    # 4. FIX "wearing" issues - ULTRA aggressive
    # Remove "wearing" before accessories/descriptions that shouldn't have it
    cap = re.sub(r'wearing\s+(slight smile|neutral expression|smirk)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+(combo rimmed glasses|glasses|rimmed sunglasses|sunglasses)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+(gold chain|silver chain|cap|hat)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+([A-Z][a-z]+\s+(?:Blue|Red|Green|Purple|Black|White|Grey|Gray|Yellow)[^,]*(?:cap|hat|beanie))', r'\1', cap, flags=re.I)

    # Fix "wearing" before facial hair → "with"
    cap = re.sub(r'wearing\s+([a-z\s]*?)(stubble|beard|mustache|goatee)', r'with \1\2', cap, flags=re.I)

    # Fix naked facial hair (no "with")
    cap = re.sub(r',\s*(stubble|beard|mustache|goatee)\s*,', r', with \1,', cap, flags=re.I)

    # 5. FIX BACKGROUNDS
    cap = re.sub(r'split background', 'divided background', cap, flags=re.I)
    cap = re.sub(r'solid background', 'background', cap, flags=re.I)

    # 6. FIX misc broken patterns
    cap = re.sub(r'medium to light', 'medium light', cap, flags=re.I)
    cap = re.sub(r'on top of a plain', '', cap, flags=re.I)
    cap = re.sub(r'for a wedding perhaps and a', 'and', cap, flags=re.I)
    cap = re.sub(r'collaredshirt', 'collared shirt', cap, flags=re.I)
    cap = re.sub(r'(gold|silver) chain thick', r'\1 chain', cap, flags=re.I)
    cap = re.sub(r'tee shirt', 't-shirt', cap, flags=re.I)
    cap = re.sub(r'unbuttoneded', 'unbuttoned', cap, flags=re.I)

    # 7. ENSURE eye color exists and is valid
    has_eyes = bool(re.search(r'\b(brown|blue|green|gray|grey|hazel|black|dark|light honey brown|dark brown|light brown|medium brown|dual colored)\s+eyes\b', cap, flags=re.I))

    # Check for broken eye color (just "eyes," with no color)
    has_broken_eyes = ', eyes,' in cap.lower() or cap.lower().endswith(', eyes')

    if not has_eyes or has_broken_eyes:
        # Remove broken "eyes" first
        cap = re.sub(r',\s*eyes\s*,', ',', cap, flags=re.I)
        cap = re.sub(r',\s*eyes\s*$', '', cap, flags=re.I)

        # Add inferred eye color before skin tone
        inferred = analyze_eye_region(img_path)
        cap = re.sub(r'(,\s*(?:light|medium|dark|tan|pale)(?:\s+light|\s+dark)?\s+(?:skin|black skin|brown skin))', f', {inferred}\\1', cap)

    # 8. REMOVE duplicate eye colors (keep last one only)
    eye_pattern = r'((?:light honey brown|dark brown|light brown|medium brown|brown|blue|green|gray|grey|hazel|black|dark)\s+eyes)'
    eye_matches = list(re.finditer(eye_pattern, cap, flags=re.I))
    if len(eye_matches) > 1:
        # Keep the last mention, remove all previous
        for match in eye_matches[:-1]:
            cap = cap[:match.start()] + cap[match.end():]
            # Recompile matches after modification
            eye_matches = list(re.finditer(eye_pattern, cap, flags=re.I))

    # 9. CLEAN UP spacing/commas
    cap = re.sub(r'\s+', ' ', cap)  # Multiple spaces → single
    cap = re.sub(r'\s*,\s*', ', ', cap)  # Normalize comma spacing
    cap = re.sub(r',\s*,+', ',', cap)  # Multiple commas → single
    cap = re.sub(r',\s*,', ',', cap)  # Double commas
    cap = cap.strip().rstrip(', ')

    # Remove any remaining standalone "eyes," or ", eyes"
    cap = re.sub(r',\s*eyes\s*,', ',', cap, flags=re.I)

    # 10. ENSURE proper ending
    if not cap.endswith('pixel art style'):
        # Remove old ending variations first
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
print("🔥 ULTIMATE CAPTION CLEANER - Nuclear option for broken captions")
print("Processing all 203 captions with maximum aggression...\n")

issues_found = []

for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()

    img_file = txt_file.with_suffix('.png')
    cleaned = ultra_clean(original, img_file)

    out_file = OUTPUT / txt_file.name
    with open(out_file, 'w') as f:
        f.write(cleaned)

    reduction = round((len(original) - len(cleaned)) / len(original) * 100, 1) if len(original) > 0 else 0
    status = "✅" if 150 <= len(cleaned) <= 220 else "📊"

    # Flag potential issues
    flags = []
    if 'wearing' in cleaned.lower() and ('stubble' in cleaned.lower() or 'beard' in cleaned.lower()):
        flags.append("⚠️ wearing+facial_hair")
    if cleaned.lower().count('eyes') > 1:
        flags.append("⚠️ dup_eyes")
    if ', eyes,' in cleaned.lower():
        flags.append("⚠️ broken_eyes")
    if 'simple' in cleaned.lower():
        flags.append("⚠️ simple")
    if 'male' in cleaned.lower() or 'female' in cleaned.lower():
        flags.append("⚠️ gender")

    flag_str = ' '.join(flags) if flags else ''
    print(f"{status} {txt_file.name}: {len(original)} → {len(cleaned)} chars ({reduction}%) {flag_str}")

    if flags:
        issues_found.append((txt_file.name, flags, cleaned))

print(f"\n✨ DONE! All 203 captions in: {OUTPUT}/")

if issues_found:
    print(f"\n⚠️  Found {len(issues_found)} captions with potential issues:")
    for name, flags, caption in issues_found[:10]:  # Show first 10
        print(f"\n{name}: {', '.join(flags)}")
        print(f"  → {caption[:120]}...")
