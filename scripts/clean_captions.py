#!/usr/bin/env python3
"""
Clean caption files - Remove problematic hex codes

Two modes:
1. --remove-uncaptioned: Remove only uncaptioned hex codes (after "retro pixel art style")
2. --remove-all-hex: Remove ALL hex codes (safest, eliminates all issues)

Usage:
    # Conservative (remove only uncaptioned)
    python scripts/clean_captions.py runpod_package/training_data --remove-uncaptioned --fix

    # Aggressive (remove ALL hex codes)
    python scripts/clean_captions.py runpod_package/training_data --remove-all-hex --fix

    # Dry-run (shows what would change)
    python scripts/clean_captions.py runpod_package/training_data --remove-all-hex
"""

import sys
import re
from pathlib import Path

def remove_uncaptioned_hex_codes(caption: str) -> str:
    """Remove hex codes after 'retro pixel art style'"""
    match = re.search(r'(.*retro pixel art style)', caption, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return caption

def remove_all_hex_codes(caption: str) -> str:
    """Remove ALL hex codes from caption (including labeled ones)"""
    # Remove hex codes in parentheses: (#ff66cc) -> empty
    cleaned = re.sub(r'\s*\(#[0-9a-fA-F]{6}\)', '', caption)

    # Remove hex codes after "palette:"
    cleaned = re.sub(r',\s*palette:.*$', '', cleaned, flags=re.IGNORECASE)

    # Remove "retro pixel art style" and everything after
    cleaned = re.sub(r',?\s*sharp pixel edges.*$', '', cleaned, flags=re.IGNORECASE)

    # Clean up multiple commas and spaces
    cleaned = re.sub(r',\s*,', ',', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip().strip(',').strip()

    return cleaned

def clean_caption_file(filepath: Path, mode: str, dry_run: bool = True) -> dict:
    """Clean a single caption file"""
    with open(filepath, 'r') as f:
        original = f.read().strip()

    if mode == 'remove-uncaptioned':
        cleaned = remove_uncaptioned_hex_codes(original)
    elif mode == 'remove-all-hex':
        cleaned = remove_all_hex_codes(original)
    else:
        return {'error': f'Unknown mode: {mode}'}

    changed = original != cleaned

    if not dry_run and changed:
        with open(filepath, 'w') as f:
            f.write(cleaned)

    # Count hex codes
    original_hex_count = len(re.findall(r'#[0-9a-fA-F]{6}', original))
    cleaned_hex_count = len(re.findall(r'#[0-9a-fA-F]{6}', cleaned))

    return {
        'filepath': str(filepath),
        'changed': changed,
        'original_hex_count': original_hex_count,
        'cleaned_hex_count': cleaned_hex_count,
        'hex_removed': original_hex_count - cleaned_hex_count,
        'original_length': len(original),
        'cleaned_length': len(cleaned)
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    dry_run = '--fix' not in sys.argv

    # Determine mode
    if '--remove-all-hex' in sys.argv:
        mode = 'remove-all-hex'
        mode_desc = "Remove ALL hex codes"
    elif '--remove-uncaptioned' in sys.argv:
        mode = 'remove-uncaptioned'
        mode_desc = "Remove uncaptioned hex codes only"
    else:
        print("❌ Error: Must specify either --remove-uncaptioned or --remove-all-hex")
        print(__doc__)
        sys.exit(1)

    if dry_run:
        print(f"🔍 DRY RUN MODE - No files will be modified")
        print(f"   Mode: {mode_desc}")
        print(f"   Add --fix flag to actually modify files\n")
    else:
        print(f"🔧 FIX MODE - Files will be modified!")
        print(f"   Mode: {mode_desc}\n")

    caption_files = sorted(data_dir.glob('*.txt'))

    print(f"Processing {len(caption_files)} caption files...\n")

    total_hex_removed = 0
    files_changed = 0
    examples = []

    for filepath in caption_files:
        result = clean_caption_file(filepath, mode, dry_run)

        if 'error' in result:
            print(f"❌ {filepath.name}: {result['error']}")
            continue

        if result['changed']:
            files_changed += 1
            total_hex_removed += result['hex_removed']

            # Show first 5 examples
            if len(examples) < 5:
                with open(filepath, 'r') as f:
                    original = f.read().strip()

                if mode == 'remove-uncaptioned':
                    cleaned = remove_uncaptioned_hex_codes(original)
                else:
                    cleaned = remove_all_hex_codes(original)

                examples.append({
                    'filename': filepath.name,
                    'original': original[:150] + '...' if len(original) > 150 else original,
                    'cleaned': cleaned[:150] + '...' if len(cleaned) > 150 else cleaned,
                    'hex_removed': result['hex_removed']
                })

    # Show examples
    if examples:
        print("\n📝 EXAMPLE CHANGES (first 5 files):\n")
        for ex in examples:
            print(f"File: {ex['filename']}")
            print(f"  BEFORE: {ex['original']}")
            print(f"  AFTER:  {ex['cleaned']}")
            print(f"  Removed: {ex['hex_removed']} hex codes\n")

    print("=" * 80)
    print(f"📊 SUMMARY")
    print("=" * 80)
    print(f"Mode: {mode_desc}")
    print(f"Total files processed: {len(caption_files)}")
    print(f"Files that would change: {files_changed}")
    print(f"Total hex codes to remove: {total_hex_removed}")

    if dry_run:
        print(f"\n⚠️  DRY RUN - No files were modified")
        print(f"   Run with --fix to apply changes:")
        print(f"   python scripts/clean_captions.py {data_dir} --{mode.replace('_', '-')} --fix")
    else:
        print(f"\n✅ Fixed {files_changed} files!")
        print(f"   Removed {total_hex_removed} hex codes total")

    print()

if __name__ == "__main__":
    main()
