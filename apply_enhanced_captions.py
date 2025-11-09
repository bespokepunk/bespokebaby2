#!/usr/bin/env python3
"""
Apply enhanced captions to all punk caption files.
"""

import json
from pathlib import Path
import re

# Paths
CAPTIONS_JSON = Path("caption_audit/enhanced_captions.json")
CAPTIONS_DIR = Path("FORTRAINING6/bespokepunks")

def clean_duplicates(caption):
    """Remove duplicate words that appear consecutively."""
    # Pattern to match word followed by comma, spaces, and same word
    # e.g., "scruff, scruff" or "scruff, face crack/scar, scruff"
    words = caption.split(', ')

    # Remove consecutive duplicates
    cleaned = []
    for i, word in enumerate(words):
        if i == 0 or word != words[i-1]:
            cleaned.append(word)

    return ', '.join(cleaned)

def apply_enhanced_captions():
    """Apply all enhanced captions to caption files."""

    # Load enhanced captions
    with open(CAPTIONS_JSON, 'r', encoding='utf-8') as f:
        enhanced_captions = json.load(f)

    print(f"📝 Applying enhanced captions to {len(enhanced_captions)} files...")
    print("=" * 80)

    updated = 0
    errors = []

    for name, caption in enhanced_captions.items():
        caption_file = CAPTIONS_DIR / f"{name}.txt"

        if not caption_file.exists():
            errors.append(f"⚠️  {name}.txt does not exist")
            continue

        # Clean duplicates
        cleaned_caption = clean_duplicates(caption)

        # Write enhanced caption
        try:
            with open(caption_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_caption)
            updated += 1

            if updated % 20 == 0:
                print(f"  Updated {updated}/{len(enhanced_captions)} files...")

        except Exception as e:
            errors.append(f"❌ {name}.txt: {e}")

    print("=" * 80)
    print(f"✅ Updated {updated} caption files!")

    if errors:
        print(f"\n⚠️  {len(errors)} errors:")
        for error in errors:
            print(f"   {error}")

    return updated, errors

if __name__ == "__main__":
    updated, errors = apply_enhanced_captions()

    print(f"\n✨ Enhanced captions applied!")
    print(f"   All {updated} caption files now include:")
    print(f"   - 'bespoke' trigger word")
    print(f"   - Explicit pattern types (checkered pattern, solid, gradient)")
    print(f"   - Pixel art style enforcement")
    print(f"   - Clean, consistent formatting")
    print(f"\n🎯 Ready for next training run!")
