#!/usr/bin/env python3
"""
Final V8 Cleanup - Remove duplicate eye colors and last issues
"""

import re
from pathlib import Path

V8_DIR = Path("improved_samples_v8_SMART")

def clean_caption(caption):
    """Final cleanup pass"""
    
    # Remove duplicate eye color mentions - keep only the LAST one
    eye_colors = []
    eye_positions = []
    
    # Find all eye color mentions
    for match in re.finditer(r'(light honey brown eyes|dark brown eyes|brown eyes|blue eyes|green eyes|gray eyes|grey eyes|black eyes|hazel eyes|dark eyes|dual colored eyes[^,]*|eyes medium brown)', caption, re.IGNORECASE):
        eye_colors.append(match.group(0))
        eye_positions.append(match.span())
    
    # If multiple eye colors found, remove all but the last
    if len(eye_colors) > 1:
        # Remove from beginning (keep last)
        for i in range(len(eye_colors) - 1):
            start, end = eye_positions[i]
            caption = caption[:start] + caption[end:]
            # Adjust positions for subsequent matches
            offset = end - start
            eye_positions = [(s if s < start else s - offset, e if e < start else e - offset) for s, e in eye_positions[i+1:]]
    
    # Remove standalone "eyes," with no color
    caption = re.sub(r',\s*eyes,', ',', caption, flags=re.IGNORECASE)
    
    # Remove extra commas and spaces
    caption = re.sub(r'\s+', ' ', caption)
    caption = re.sub(r'\s*,\s*', ', ', caption)
    caption = re.sub(r',\s*,+', ',', caption)
    caption = caption.strip().rstrip(', ')
    
    # Ensure proper ending
    if not caption.endswith('pixel art style'):
        caption += ', pixel art style'
    
    return caption

# Process all files
for txt_file in V8_DIR.glob("*.txt"):
    if txt_file.name == "NEEDS_REVIEW.json":
        continue
        
    with open(txt_file, 'r') as f:
        original = f.read().strip()
    
    cleaned = clean_caption(original)
    
    if cleaned != original:
        with open(txt_file, 'w') as f:
            f.write(cleaned)
        print(f"✅ Cleaned: {txt_file.name}")

print("\n✨ Final cleanup complete!")
