#!/usr/bin/env python3
"""
Gap Analysis on REFINED captions
"""

import json
import re
from collections import Counter, defaultdict

# Load refined captions
with open('merged_captions_v3_refined.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("GAP ANALYSIS - REFINED CAPTIONS")
print("=" * 100)
print()

stats = defaultdict(int)
issues = []

def check_for_instructions(text):
    """Check if caption contains instructions/meta-text"""
    instruction_patterns = [
        r'describe.*better',
        r'do that here',
        r'adjust for',
        r'explain.*if you',
        r'imagine describing',
        r'\(.*describe.*\)',
        r'\(.*better.*\)',
        r'yo u(?!r)',
        r'liek',
        r'enahnce',
        r'due to editing',
        r'woudl jsut be',
        r'obviously see',
    ]
    found = []
    for pattern in instruction_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(pattern)
    return found

print("🔍 ANALYZING 203 REFINED CAPTIONS...\n")

for idx, record in enumerate(records, 1):
    filename = record['filename']
    refined = record.get('merged_caption_v3_refined', '')

    stats['total'] += 1

    # Check for instruction text
    instructions = check_for_instructions(refined)
    if instructions:
        issues.append({
            'filename': filename,
            'type': 'INSTRUCTION_TEXT',
            'patterns': instructions,
        })
        stats['has_instruction_text'] += 1

    # Check for typos
    typo_patterns = [r'\bhcolor\b', r'\byo ucan\b', r'\bwoudl\b', r'\bo nleft\b', r'\bbalck\b', r'\bhiis\b']
    for pattern in typo_patterns:
        if re.search(pattern, refined, re.IGNORECASE):
            stats['has_typos'] += 1
            break

    # Check for TODO text
    if 'get lip' in refined.lower():
        stats['has_todo_text'] += 1

    # Count hex codes
    hex_codes = re.findall(r'#[0-9a-fA-F]{6}', refined)
    if 'eyes' in refined.lower():
        if not re.search(rf'eyes\s*\(#[0-9a-fA-F]{{6}}\)', refined, re.IGNORECASE):
            stats['eyes_missing_hex'] += 1

print("=" * 100)
print("REFINED CAPTION STATISTICS")
print("=" * 100)
print()
print(f"Total images: {stats['total']}")
print()
print("REMAINING ISSUES:")
print(f"  Instruction text: {stats.get('has_instruction_text', 0)}")
print(f"  Typos: {stats.get('has_typos', 0)}")
print(f"  TODO text: {stats.get('has_todo_text', 0)}")
print(f"  Eyes missing hex: {stats.get('eyes_missing_hex', 0)}")
print()

print("IMPROVEMENT COMPARISON:")
print("  Before refinement:")
print("    - Instruction text: 14")
print("    - Typos: 12")
print("    - TODO text: 3")
print(f"  After refinement:")
print(f"    - Instruction text: {stats.get('has_instruction_text', 0)} ({((14-stats.get('has_instruction_text',0))/14*100):.0f}% fixed)")
print(f"    - Typos: {stats.get('has_typos', 0)} ({((12-stats.get('has_typos',0))/12*100):.0f}% fixed)")
print(f"    - TODO text: {stats.get('has_todo_text', 0)} ({((3-stats.get('has_todo_text',0))/3*100):.0f}% fixed)")
print()

if stats.get('has_instruction_text', 0) > 0:
    print("=" * 100)
    print(f"REMAINING INSTRUCTION TEXT ISSUES ({stats['has_instruction_text']} files)")
    print("=" * 100)
    print()
    for issue in issues[:10]:
        if issue['type'] == 'INSTRUCTION_TEXT':
            print(f"  {issue['filename']}: {issue['patterns']}")

print()
print("✅ Gap analysis complete on refined captions")
