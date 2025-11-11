#!/usr/bin/env python3
"""
Audit caption files for hex code issues

Finds:
1. Duplicate hex codes used for different features
2. Uncaptioned hex codes (after "retro pixel art style")
3. Features sharing the same hex code

Usage:
    python scripts/audit_caption_hex_codes.py runpod_package/training_data
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

def extract_labeled_hex_codes(caption: str) -> dict:
    """Extract hex codes with their labels (e.g., 'hair (#ff66cc)')"""
    # Pattern: word/phrase followed by hex code in parens
    pattern = r'(\w+(?:\s+\w+)*)\s*\(#([0-9a-fA-F]{6})\)'
    matches = re.findall(pattern, caption)

    labeled = {}
    for label, hex_code in matches:
        hex_code = hex_code.lower()
        if label not in labeled:
            labeled[label] = []
        labeled[label].append(f"#{hex_code}")

    return labeled

def extract_uncaptioned_hex_codes(caption: str) -> list:
    """Extract hex codes after 'retro pixel art style' (uncaptioned)"""
    # Find everything after "retro pixel art style"
    match = re.search(r'retro pixel art style,?\s*(.*)$', caption, re.IGNORECASE)
    if not match:
        return []

    tail = match.group(1)

    # Find all hex codes in the tail
    hex_pattern = r'#([0-9a-fA-F]{6})'
    hex_codes = [f"#{h.lower()}" for h in re.findall(hex_pattern, tail)]

    return hex_codes

def audit_caption_file(filepath: Path) -> dict:
    """Audit a single caption file"""
    with open(filepath, 'r') as f:
        caption = f.read().strip()

    labeled = extract_labeled_hex_codes(caption)
    uncaptioned = extract_uncaptioned_hex_codes(caption)

    # Check for duplicate hex codes across features
    hex_to_features = defaultdict(list)
    for feature, hex_codes in labeled.items():
        for hex_code in hex_codes:
            hex_to_features[hex_code].append(feature)

    duplicates = {hex_code: features for hex_code, features in hex_to_features.items()
                  if len(features) > 1}

    return {
        'filepath': str(filepath),
        'labeled': labeled,
        'uncaptioned': uncaptioned,
        'duplicates': duplicates,
        'has_issues': len(duplicates) > 0 or len(uncaptioned) > 0
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    caption_files = sorted(data_dir.glob('*.txt'))

    print(f"🔍 Auditing {len(caption_files)} caption files...\n")

    issues_found = 0
    duplicate_issues = 0
    uncaptioned_issues = 0

    all_duplicates = defaultdict(list)

    for filepath in caption_files:
        result = audit_caption_file(filepath)

        if result['has_issues']:
            issues_found += 1

            if result['duplicates']:
                duplicate_issues += 1
                print(f"❌ {filepath.name}:")
                for hex_code, features in result['duplicates'].items():
                    print(f"   {hex_code} used for: {', '.join(features)}")
                    all_duplicates[hex_code].append(filepath.name)

            if result['uncaptioned']:
                uncaptioned_issues += 1
                print(f"⚠️  {filepath.name}: {len(result['uncaptioned'])} uncaptioned hex codes")
                print(f"   {', '.join(result['uncaptioned'][:5])}{'...' if len(result['uncaptioned']) > 5 else ''}")

            print()

    print("=" * 80)
    print(f"📊 AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total files: {len(caption_files)}")
    print(f"Files with issues: {issues_found}")
    print(f"Files with duplicate hex codes: {duplicate_issues}")
    print(f"Files with uncaptioned hex codes: {uncaptioned_issues}")
    print()

    if all_duplicates:
        print("🔥 MOST COMMON DUPLICATE HEX CODES:")
        sorted_dups = sorted(all_duplicates.items(), key=lambda x: len(x[1]), reverse=True)
        for hex_code, files in sorted_dups[:10]:
            print(f"   {hex_code}: appears in {len(files)} files")
        print()

    print(f"✅ Clean files: {len(caption_files) - issues_found}")
    print()

    if issues_found > 0:
        print("⚠️  RECOMMENDATION: Run fix_caption_hex_codes.py to automatically fix these issues")
    else:
        print("🎉 All captions are clean!")

if __name__ == "__main__":
    main()
