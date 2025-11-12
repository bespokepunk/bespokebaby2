#!/usr/bin/env python3
"""
ONE COMPREHENSIVE SCRIPT - Does EVERYTHING in one pass
No more version hell - this creates perfect world-class captions
"""

import re
from pathlib import Path
from PIL import Image
from collections import Counter

SOURCE = Path("runpod_package/training_data")
OUTPUT = Path("FINAL_WORLD_CLASS_CAPTIONS")
OUTPUT.mkdir(exist_ok=True)

def analyze_eye_region(img_path):
    """Quick eye color inference from middle region"""
    try:
        img = Image.open(img_path).convert('RGB')
        w, h = img.size
        # Middle strip for eyes
        pixels = []
        for y in range(h//3, 2*h//3):
            for x in range(w):
                pixels.append(img.getpixel((x, y)))
        
        # Get dominant non-background colors
        counts = Counter(pixels)
        for (r,g,b), _ in counts.most_common(15):
            if 70 <= r <= 140 and 35 <= g <= 90 and 15 <= b <= 65:
                return "brown eyes"
            if b > max(r,g) + 30 and b > 90:
                return "blue eyes"
            if g > max(r,b) + 20:
                return "green eyes"
            if abs(r-g) < 15 and abs(g-b) < 15 and 90 < r < 170:
                return "gray eyes"
        return None
    except:
        return None

def clean_comprehensively(cap, img_path):
    """ONE function to do ALL cleaning"""
    
    # 1. SURGICAL REMOVALS
    cap = re.sub(r'\bsimple\s+', '', cap, flags=re.I)
    cap = re.sub(r'\bmale\b', '', cap, flags=re.I)
    cap = re.sub(r'\bfemale\b', '', cap, flags=re.I)
    cap = re.sub(r'\bhispanic\b', '', cap, flags=re.I)
    cap = re.sub(r'\s*\((middle eastern|mexican|italian[^)]*)\)', '', cap, flags=re.I)
    cap = cap.replace('lips,', '').replace(', lips', '')
    cap = re.sub(r'#[0-9a-fA-F]{6}', '', cap)
    cap = re.sub(r',?\s*(hard color borders|sharp pixel edges|palette:[^,]*)', '', cap, flags=re.I)
    
    # 2. FIX "wearing" → remove for accessories, "with" for facial hair
    cap = re.sub(r'wearing\s+(combo rimmed glasses|glasses|gold chain|silver chain|cap|hat)', r'\1', cap, flags=re.I)
    cap = re.sub(r'wearing\s+([a-z\s]*?)(stubble|beard|mustache|goatee)', r'with \1\2', cap, flags=re.I)
    
    # 3. FIX BACKGROUNDS  
    cap = re.sub(r'split background', 'divided background', cap, flags=re.I)
    cap = re.sub(r'solid background', 'background', cap, flags=re.I)
    
    # 4. FIX misc issues
    cap = re.sub(r'medium to light', 'medium light', cap, flags=re.I)
    cap = re.sub(r'on top of a plain', '', cap, flags=re.I)
    cap = re.sub(r'for a wedding perhaps and a', 'and', cap, flags=re.I)
    cap = re.sub(r'collaredshirt', 'collared shirt', cap, flags=re.I)
    cap = re.sub(r'(gold|silver) chain thick', r'\1 chain', cap, flags=re.I)
    cap = re.sub(r'tee shirt', 't-shirt', cap, flags=re.I)
    cap = re.sub(r'unbuttoneded', 'unbuttoned', cap, flags=re.I)
    
    # 5. ADD MISSING EYE COLOR if needed
    has_eyes = bool(re.search(r'\b(brown|blue|green|gray|grey|hazel|black|dark|dual colored)\s+eyes\b', cap, flags=re.I))
    if not has_eyes or ', eyes,' in cap.lower():
        inferred = analyze_eye_region(img_path)
        if inferred:
            # Insert before skin tone
            cap = re.sub(r'(,\s*(?:light|medium|dark|tan)\s+(?:light\s+)?skin)', f', {inferred}\\1', cap)
    
    # 6. REMOVE duplicate eye colors (keep last one only)
    eye_matches = list(re.finditer(r'((?:light honey brown|dark brown|light brown|medium brown|brown|blue|green|gray|grey|hazel|black|dark)\s+eyes)', cap, flags=re.I))
    if len(eye_matches) > 1:
        # Remove all but last
        for match in eye_matches[:-1]:
            cap = cap[:match.start()] + cap[match.end():]
    
    # Remove standalone "eyes,"
    cap = re.sub(r',\s*eyes\s*,', ',', cap, flags=re.I)
    
    # 7. CLEAN UP spacing/commas
    cap = re.sub(r'\s+', ' ', cap)
    cap = re.sub(r'\s*,\s*', ', ', cap)
    cap = re.sub(r',\s*,+', ',', cap)
    cap = cap.strip().rstrip(', ')
    
    # 8. ENSURE proper ending
    if not cap.endswith('pixel art style'):
        cap += ', pixel art style'
    cap = cap.replace(', pixel art style, pixel art style', ', pixel art style')
    
    return cap

# PROCESS ALL 203
print("🎯 ONE SCRIPT TO RULE THEM ALL")
print("Processing all 203 captions with comprehensive fixes...")
print()

for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        original = f.read().strip()
    
    img_file = txt_file.with_suffix('.png')
    cleaned = clean_comprehensively(original, img_file)
    
    out_file = OUTPUT / txt_file.name
    with open(out_file, 'w') as f:
        f.write(cleaned)
    
    reduction = round((len(original) - len(cleaned)) / len(original) * 100, 1)
    status = "✅" if 150 <= len(cleaned) <= 220 else "📊"
    print(f"{status} {txt_file.name}: {len(original)} → {len(cleaned)} chars ({reduction}%)")

print(f"\n✨ DONE! All 203 captions in: {OUTPUT}/")
