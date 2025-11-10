#!/usr/bin/env python3
"""
Gap Analysis & Quality Validation
Identifies missing traits, inconsistencies, and quality issues in merged captions
"""

import json
import re
from collections import Counter, defaultdict

# Load merged captions
with open('merged_captions_v3.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("GAP ANALYSIS & QUALITY VALIDATION")
print("=" * 100)
print()

# Analysis results
issues = []
stats = defaultdict(int)
trait_coverage = defaultdict(int)
quality_flags = []

def check_trait_presence(caption, trait_keywords):
    """Check if trait is mentioned in caption"""
    caption_lower = caption.lower()
    return any(kw in caption_lower for kw in trait_keywords)

def extract_hex_codes(text):
    """Extract all hex codes from text"""
    return re.findall(r'#[0-9a-fA-F]{6}', text)

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
        r'yo u',  # typo detection
        r'liek',
        r'enahnce',
    ]
    found = []
    for pattern in instruction_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found.append(pattern)
    return found

# Trait keywords to check
trait_checks = {
    'hair_color': ['hair', 'afro', 'blonde', 'brown', 'black', 'red', 'bald', 'gray', 'grey'],
    'hair_style': ['afro', 'curly', 'wavy', 'straight', 'long', 'short', 'side-swept', 'parted', 'buzzed', 'mohawk', 'styled', 'slicked'],
    'eye_color': ['eyes', 'eye color'],
    'skin_tone': ['skin', 'skinned', 'skin tone'],
    'facial_hair': ['stubble', 'beard', 'mustache', 'moustache', 'goatee'],
    'accessories': ['sunglasses', 'glasses', 'earrings', 'earring', 'hat', 'crown', 'headwear'],
    'lips': ['lips', 'lip color', 'mouth'],
    'clothing': ['shirt', 'jacket', 'suit', 'hoodie', 'coat', 'wearing', 'outfit'],
    'background': ['background', 'backdrop'],
    'expression': ['smiling', 'smile', 'serious', 'neutral', 'happy', 'sad', 'frown']
}

print("🔍 ANALYZING 203 CAPTIONS...\n")

for idx, record in enumerate(records, 1):
    filename = record['filename']
    merged = record['merged_caption_v3']
    user_corr = record.get('user_corrections', '')

    stats['total'] += 1

    # Check trait coverage
    for trait, keywords in trait_checks.items():
        if check_trait_presence(merged, keywords):
            trait_coverage[trait] += 1

    # Check for instruction text in merged caption
    instructions = check_for_instructions(merged)
    if instructions:
        issues.append({
            'filename': filename,
            'type': 'INSTRUCTION_TEXT',
            'severity': 'HIGH',
            'description': f'Caption contains meta-instructions that should be replaced with actual descriptions',
            'patterns': instructions,
            'caption_snippet': merged[:150] + '...'
        })
        stats['has_instruction_text'] += 1

    # Check for obvious typos in merged caption
    typo_patterns = [r'yo u(?!r)', r'liek', r'teh', r'adn', r'enahnce', r'haoirc', r'rbowns', r'rkeds']
    for pattern in typo_patterns:
        if re.search(pattern, merged, re.IGNORECASE):
            issues.append({
                'filename': filename,
                'type': 'TYPO',
                'severity': 'MEDIUM',
                'description': f'Caption contains typo: "{pattern}"',
                'caption_snippet': merged[:150] + '...'
            })
            stats['has_typos'] += 1
            break

    # Check if user mentioned accessories that appear in merged caption
    user_lower = user_corr.lower()
    merged_lower = merged.lower()

    # Earrings check (user said: if I don't mention them, they don't exist)
    if 'earring' in merged_lower and 'earring' not in user_lower:
        issues.append({
            'filename': filename,
            'type': 'UNSOLICITED_TRAIT',
            'severity': 'HIGH',
            'description': 'Caption mentions earrings but user did not mention them',
            'note': 'Per user: "if i dont mentin them, the ydont exist"'
        })
        stats['unsolicited_earrings'] += 1

    # Check for missing hex codes on colors
    color_words = ['hair', 'eyes', 'skin', 'lips', 'background', 'shirt', 'jacket']
    for cw in color_words:
        # Find color mentions without hex codes
        pattern = rf'(\w+)\s+{cw}'
        matches = re.findall(pattern, merged_lower)
        for match in matches:
            # Check if it's a color word
            color_keywords = ['brown', 'blue', 'green', 'red', 'yellow', 'orange', 'pink', 'purple', 'gray', 'grey', 'black', 'white', 'cyan', 'tan', 'olive']
            if match in color_keywords:
                # Check if there's a hex nearby
                # Look for pattern like "brown eyes (#...)" or just "brown eyes"
                hex_pattern = rf'{match}\s+{cw}\s*\(#[0-9a-fA-F]{{6}}\)'
                if not re.search(hex_pattern, merged_lower):
                    # This color doesn't have a hex code
                    stats[f'missing_hex_{cw}'] += 1
                    break

    # Check hex code consistency with sampled colors
    hex_in_caption = extract_hex_codes(merged)
    sampled = record.get('sampled_trait_colors', {})

    if sampled:
        # Get all sampled hex codes
        sampled_hexes = set()
        for region_name, region_data in sampled.items():
            if isinstance(region_data, list):
                for color_info in region_data:
                    if isinstance(color_info, dict) and 'hex' in color_info:
                        sampled_hexes.add(color_info['hex'].lower())

        # Check if caption hexes match sampled
        for hex_code in hex_in_caption:
            if hex_code.lower() not in sampled_hexes:
                stats['hex_not_in_sample'] += 1
                break

    # Check if "get lip color" instruction remains
    if 'get lip color' in merged_lower or 'get lips' in merged_lower:
        issues.append({
            'filename': filename,
            'type': 'TODO_TEXT',
            'severity': 'HIGH',
            'description': 'Caption contains TODO instruction "get lip color"',
        })
        stats['has_todo_text'] += 1

    # Check for incomplete descriptions
    if '...' in merged or '(?' in merged:
        stats['incomplete_descriptions'] += 1

    # Check expression mention
    if not check_trait_presence(merged, trait_checks['expression']):
        stats['missing_expression'] += 1

print("=" * 100)
print("STATISTICS")
print("=" * 100)
print()
print(f"Total images processed: {stats['total']}")
print()
print("TRAIT COVERAGE:")
for trait, count in sorted(trait_coverage.items()):
    percentage = (count / stats['total']) * 100
    print(f"  {trait:20s}: {count:3d} / {stats['total']} ({percentage:.1f}%)")
print()

print("ISSUES FOUND:")
print(f"  Captions with instruction text: {stats.get('has_instruction_text', 0)}")
print(f"  Captions with typos: {stats.get('has_typos', 0)}")
print(f"  Unsolicited earrings: {stats.get('unsolicited_earrings', 0)}")
print(f"  TODO text remaining: {stats.get('has_todo_text', 0)}")
print(f"  Incomplete descriptions: {stats.get('incomplete_descriptions', 0)}")
print(f"  Missing expression: {stats.get('missing_expression', 0)}")
print()

print("MISSING HEX CODES:")
for key in sorted([k for k in stats.keys() if k.startswith('missing_hex_')]):
    trait = key.replace('missing_hex_', '')
    print(f"  {trait:20s}: {stats[key]} instances")
print()

# Sort issues by severity
issues_sorted = sorted(issues, key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x['severity'], 3))

print("=" * 100)
print(f"DETAILED ISSUES ({len(issues)} total)")
print("=" * 100)
print()

# Group by type
issues_by_type = defaultdict(list)
for issue in issues_sorted:
    issues_by_type[issue['type']].append(issue)

for issue_type, issue_list in sorted(issues_by_type.items()):
    print(f"\n🚨 {issue_type} ({len(issue_list)} instances)")
    print("-" * 100)

    # Show first 5 examples of each type
    for issue in issue_list[:5]:
        print(f"\n  File: {issue['filename']}")
        print(f"  Severity: {issue['severity']}")
        print(f"  Issue: {issue['description']}")
        if 'caption_snippet' in issue:
            print(f"  Snippet: {issue['caption_snippet']}")
        if 'patterns' in issue:
            print(f"  Patterns: {issue['patterns']}")
        if 'note' in issue:
            print(f"  Note: {issue['note']}")

    if len(issue_list) > 5:
        print(f"\n  ... and {len(issue_list) - 5} more instances")

# Save detailed report
report = {
    'summary': dict(stats),
    'trait_coverage': dict(trait_coverage),
    'issues': issues_sorted,
    'recommendations': []
}

# Generate recommendations
if stats.get('has_instruction_text', 0) > 0:
    report['recommendations'].append({
        'priority': 'HIGH',
        'issue': f"{stats['has_instruction_text']} captions contain instruction text",
        'action': 'Parse user descriptions and replace meta-instructions with actual trait descriptions'
    })

if stats.get('has_typos', 0) > 0:
    report['recommendations'].append({
        'priority': 'MEDIUM',
        'issue': f"{stats['has_typos']} captions contain typos from user input",
        'action': 'Auto-correct common typos while preserving user intent'
    })

if stats.get('unsolicited_earrings', 0) > 0:
    report['recommendations'].append({
        'priority': 'HIGH',
        'issue': f"{stats['unsolicited_earrings']} captions mention accessories user did not specify",
        'action': 'Remove traits not mentioned by user (per user requirement)'
    })

if stats.get('has_todo_text', 0) > 0:
    report['recommendations'].append({
        'priority': 'HIGH',
        'issue': f"{stats['has_todo_text']} captions contain TODO markers like 'get lip color'",
        'action': 'Sample actual lip colors from images and replace TODO text'
    })

if stats.get('missing_expression', 0) > 50:
    report['recommendations'].append({
        'priority': 'MEDIUM',
        'issue': f"{stats['missing_expression']} captions missing expression/emotion",
        'action': 'Analyze facial features to detect smiling, serious, neutral expressions'
    })

# Save report
with open('gap_analysis_report_v3.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\n" + "=" * 100)
print("RECOMMENDATIONS")
print("=" * 100)
print()

for rec in report['recommendations']:
    print(f"[{rec['priority']}] {rec['issue']}")
    print(f"  → {rec['action']}")
    print()

print(f"✅ Full report saved to: gap_analysis_report_v3.json")
print()
