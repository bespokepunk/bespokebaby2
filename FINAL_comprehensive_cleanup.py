#!/usr/bin/env python3
"""
FINAL Comprehensive Cleanup - Fix EVERY remaining issue
"""

import re
from pathlib import Path

V8_DIR = Path("improved_samples_v8_SMART")
OUTPUT_DIR = Path("improved_samples_v9_FINAL_CLEAN")
OUTPUT_DIR.mkdir(exist_ok=True)

def comprehensive_clean(caption):
    """Fix EVERY issue comprehensively"""
    
    # 1. Remove ALL instances of "simple"
    caption = re.sub(r'\bsimple\s+', '', caption, flags=re.IGNORECASE)
    
    # 2. Remove ALL instances of "male", "female"  
    caption = re.sub(r'\bmale\b', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\bfemale\b', '', caption, flags=re.IGNORECASE)
    
    # 3. Remove ALL ethnic descriptors
    caption = re.sub(r'\bhispanic\b', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\s*\(middle eastern\)', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\s*\(mexican\)', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\s*\(italian[^)]*\)', '', caption, flags=re.IGNORECASE)
    
    # 4. Fix ALL "wearing" accessories → remove "wearing"
    caption = re.sub(r'wearing\s+(combo\s+rimmed\s+glasses|glasses|gold\s+chain|silver\s+chain|cap|hat)', r'\1', caption, flags=re.IGNORECASE)
    
    # 5. Fix ALL "wearing" facial hair → "with"
    caption = re.sub(r'wearing\s+(light\s+gray|dark\s+brown|brown|gray|grey)?\s*(stubble|beard|mustache|goatee)', r'with \1 \2' if r'\1' else r'with \2', caption, flags=re.IGNORECASE)
    
    # 6. Remove "lips"
    caption = caption.replace('lips,', '').replace(', lips', '')
    
    # 7. Remove hex codes
    caption = re.sub(r'#[0-9a-fA-F]{6}', '', caption)
    
    # 8. Remove style markers
    caption = re.sub(r',?\s*hard color borders', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r',?\s*sharp pixel edges', '', caption, flags=re.IGNORECASE)
    
    # 9. Fix backgrounds
    caption = re.sub(r'split background', 'divided background', caption, flags=re.IGNORECASE)
    caption = re.sub(r'solid background', 'background', caption, flags=re.IGNORECASE)
    
    # 10. Fix "medium to light" → "medium light"
    caption = re.sub(r'medium to light', 'medium light', caption, flags=re.IGNORECASE)
    
    # 11. Remove verbose phrases
    caption = re.sub(r'on top of a plain', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'for a wedding perhaps and a', 'and', caption, flags=re.IGNORECASE)
    
    # 12. Fix spacing/typos
    caption = re.sub(r'collaredshirt', 'collared shirt', caption, flags=re.IGNORECASE)
    caption = re.sub(r'tee shirt', 't-shirt', caption, flags=re.IGNORECASE)
    
    # 13. Remove "thick" after accessories
    caption = re.sub(r'(gold|silver)\s+chain\s+thick', r'\1 chain', caption, flags=re.IGNORECASE)
    
    # 14. Remove standalone "eyes," with no color
    caption = re.sub(r',\s*eyes,', ',', caption, flags=re.IGNORECASE)
    
    # 15. Remove duplicate words in immediate sequence
    words = caption.split(', ')
    cleaned_words = []
    prev_word = None
    for word in words:
        if word.lower() != (prev_word.lower() if prev_word else ''):
            cleaned_words.append(word)
            prev_word = word
    caption = ', '.join(cleaned_words)
    
    # 16. Clean up spacing
    caption = re.sub(r'\s+', ' ', caption)
    caption = re.sub(r'\s*,\s*', ', ', caption)
    caption = re.sub(r',\s*,+', ',', caption)
    caption = caption.strip().rstrip(', ')
    
    # 17. Ensure proper ending
    if not caption.endswith('pixel art style'):
        caption += ', pixel art style'
    caption = caption.replace(', pixel art style, pixel art style', ', pixel art style')
    
    return caption

# Process all files
count = 0
for txt_file in sorted(V8_DIR.glob("*.txt")):
    if txt_file.name == "NEEDS_REVIEW.json":
        continue
        
    with open(txt_file, 'r') as f:
        original = f.read().strip()
    
    cleaned = comprehensive_clean(original)
    
    output_file = OUTPUT_DIR / txt_file.name
    with open(output_file, 'w') as f:
        f.write(cleaned)
    
    if cleaned != original:
        count += 1
        print(f"✅ {txt_file.name}: {len(original)} → {len(cleaned)} chars")

print(f"\n✨ Final cleanup complete! Fixed {count} captions")
print(f"📁 Output: {OUTPUT_DIR}/")
