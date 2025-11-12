#!/usr/bin/env python3
"""Final Cleanup - Write ALL files"""
import re
from pathlib import Path

V8_DIR = Path("improved_samples_v8_SMART")
OUTPUT_DIR = Path("improved_samples_FINAL")
OUTPUT_DIR.mkdir(exist_ok=True)

def clean(caption):
    """Comprehensive cleaning"""
    # All the surgical fixes
    caption = re.sub(r'\bsimple\s+', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\bmale\b', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\bfemale\b', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\bhispanic\b', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'wearing\s+(combo\s+rimmed\s+glasses|glasses|gold\s+chain|silver\s+chain)', r'\1', caption, flags=re.IGNORECASE)
    caption = caption.replace('lips,', '').replace(', lips', '')
    caption = re.sub(r',?\s*hard color borders', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r',?\s*sharp pixel edges', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'on top of a plain', '', caption, flags=re.IGNORECASE)
    caption = re.sub(r'for a wedding perhaps and a', 'and', caption, flags=re.IGNORECASE)
    caption = re.sub(r'collaredshirt', 'collared shirt', caption, flags=re.IGNORECASE)
    caption = re.sub(r'(gold|silver)\s+chain\s+thick', r'\1 chain', caption, flags=re.IGNORECASE)
    caption = re.sub(r', bald neutral/, neutral/g" "$f"
  # Fix duplicate eye colors
  sed -i '' 's/light honey brown eyes, dark brown eyes/dark brown eyes/g' "$f"
  # Fix mustache/goatee
  sed -i '' 's/, mustache,/, with mustache,/g' "$f"
  sed -i '' 's/, goatee,/, with goatee,/g' "$f"
done && echo "✅ Fixed!" && cat improved_samples_FINAL/lad_022_x.txt && echo "---" && cat improved_samples_FINAL/lad_011_chocolate.txt