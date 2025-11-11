#!/usr/bin/env python3
"""
Fix caption hex code issues

Phase 1: Remove ALL uncaptioned hex codes (after "retro pixel art style")
Phase 2: Report on duplicate hex codes (manual review needed)

Usage:
    python scripts/fix_caption_hex_codes.py runpod_package/training_data --fix

Without --fix flag, runs in dry-run mode (shows what would change)
"""

import sys
import re
from pathlib import Path

def remove_uncaptioned_hex_codes(caption: str) -> tuple:
    """
    Remove hex codes after 'retro pixel art style'

    Returns: (cleaned_caption, removed_count)
    """
    # Find "retro pixel art style" and everything after
    match = re.search(r'(.*retro pixel art style)', caption, re.IGNORECASE)

    if not match:
        return caption, 0

    # Keep everything up to and including "retro pixel art style"
    cleaned = match.group(1)

    # Count how many hex codes we're removing
    tail = caption[len(cleaned):]
    removed_hex = len(re.findall(r'#[0-9a-fA-F]{6}', tail))

    return cleaned, removed_hex

def fix_caption_file(filepath: Path, dry_run: bool = True) -> dict:
    """Fix a single caption file"""
    with open(filepath, 'r') as f:
        original = f.read().strip()

    cleaned, removed_count = remove_uncaptioned_hex_codes(original)

    if not dry_run and removed_count > 0:
        with open(filepath, 'w') as f:
            f.write(cleaned)

    return {
        'filepath': str(filepath),
        'removed_count': removed_count,
        'original_length': len(original),
        'cleaned_length': len(cleaned),
        'changed': removed_count > 0
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    dry_run = '--fix' not in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("   Add --fix flag to actually fix files\n")
    else:
        print("🔧 FIX MODE - Files will be modified!\n")

    caption_files = sorted(data_dir.glob('*.txt'))

    print(f"Processing {len(caption_files)} caption files...\n")

    total_removed = 0
    files_changed = 0

    for filepath in caption_files:
        result = fix_caption_file(filepath, dry_run)

        if result['changed']:
            files_changed += 1
            total_removed += result['removed_count']

            if dry_run:
                print(f"Would fix {filepath.name}: remove {result['removed_count']} hex codes")

    print("\n" + "=" * 80)
    print(f"📊 SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(caption_files)}")
    print(f"Files with uncaptioned hex codes: {files_changed}")
    print(f"Total hex codes to remove: {total_removed}")

    if dry_run:
        print(f"\n⚠️  DRY RUN - No files were modified")
        print(f"   Run with --fix to apply changes:")
        print(f"   python scripts/fix_caption_hex_codes.py {data_dir} --fix")
    else:
        print(f"\n✅ Fixed {files_changed} files!")
        print(f"   Removed {total_removed} uncaptioned hex codes")

    print()

if __name__ == "__main__":
    main()
