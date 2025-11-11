#!/usr/bin/env python3
"""
Smart caption cleaning - Keep color descriptions, remove hex codes

Strategy:
1. Remove hex codes IN PARENTHESES: (#ff66cc) → ""
2. Remove "palette:" section and everything after
3. Remove "sharp pixel edges..." junk
4. Keep all descriptive text (colors, features, etc.)

Example:
  BEFORE: "bright green hair (#03dc73), lips (#efbda4), palette: #03dc73..."
  AFTER:  "bright green hair, lips"

Usage:
    python scripts/smart_clean_captions.py runpod_package/training_data --fix
"""

import sys
import re
from pathlib import Path

def smart_clean_caption(caption: str) -> str:
    """
    Clean caption by removing hex codes but keeping descriptive text
    """
    # Step 1: Remove hex codes in parentheses
    # "hair (#ff66cc)" → "hair"
    # "bright green background (#00ff00)" → "bright green background"
    cleaned = re.sub(r'\s*\(#[0-9a-fA-F]{6}\)', '', caption)

    # Step 2: Remove "palette:" and everything after it
    cleaned = re.sub(r',?\s*palette:.*$', '', cleaned, flags=re.IGNORECASE)

    # Step 3: Remove "sharp pixel edges" and everything after
    cleaned = re.sub(r',?\s*sharp pixel edges.*$', '', cleaned, flags=re.IGNORECASE)

    # Step 4: Clean up formatting
    # Remove multiple commas
    cleaned = re.sub(r',\s*,+', ',', cleaned)
    # Remove spaces before commas
    cleaned = re.sub(r'\s+,', ',', cleaned)
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Trim
    cleaned = cleaned.strip().strip(',').strip()

    return cleaned

def process_file(filepath: Path, dry_run: bool = True) -> dict:
    """Process a single caption file"""
    with open(filepath, 'r') as f:
        original = f.read().strip()

    cleaned = smart_clean_caption(original)

    # Count hex codes removed
    original_hex = len(re.findall(r'#[0-9a-fA-F]{6}', original))
    cleaned_hex = len(re.findall(r'#[0-9a-fA-F]{6}', cleaned))

    changed = original != cleaned

    if not dry_run and changed:
        with open(filepath, 'w') as f:
            f.write(cleaned)

    return {
        'filepath': str(filepath),
        'changed': changed,
        'original': original,
        'cleaned': cleaned,
        'hex_removed': original_hex - cleaned_hex,
        'original_length': len(original),
        'cleaned_length': len(cleaned)
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    dry_run = '--fix' not in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("   Add --fix flag to apply changes\n")
    else:
        print("🔧 FIX MODE - Files will be modified!\n")

    caption_files = sorted(data_dir.glob('*.txt'))

    print(f"Processing {len(caption_files)} caption files...\n")

    total_hex_removed = 0
    files_changed = 0
    examples = []

    for filepath in caption_files:
        result = process_file(filepath, dry_run)

        if result['changed']:
            files_changed += 1
            total_hex_removed += result['hex_removed']

            # Collect first 5 examples
            if len(examples) < 5:
                examples.append({
                    'filename': filepath.name,
                    'original': result['original'][:200] + '...' if len(result['original']) > 200 else result['original'],
                    'cleaned': result['cleaned'][:200] + '...' if len(result['cleaned']) > 200 else result['cleaned'],
                    'hex_removed': result['hex_removed']
                })

    # Show examples
    if examples:
        print("\n📝 EXAMPLE TRANSFORMATIONS (first 5 files):\n")
        for ex in examples:
            print(f"File: {ex['filename']}")
            print(f"  BEFORE: {ex['original']}")
            print(f"  AFTER:  {ex['cleaned']}")
            print(f"  Removed: {ex['hex_removed']} hex codes\n")

    print("=" * 80)
    print(f"📊 SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(caption_files)}")
    print(f"Files that will change: {files_changed}")
    print(f"Total hex codes to remove: {total_hex_removed}")

    if dry_run:
        print(f"\n⚠️  DRY RUN - No files were modified")
        print(f"   Run with --fix to apply changes:")
        print(f"   python scripts/smart_clean_captions.py {data_dir} --fix")
    else:
        print(f"\n✅ Fixed {files_changed} files!")
        print(f"   Removed {total_hex_removed} hex codes total")
        print(f"   Kept all descriptive text intact")

    print()

if __name__ == "__main__":
    main()
