#!/usr/bin/env python3
"""
COMPREHENSIVE VALIDATION - Check all 203 captions for quality
"""

import re
from pathlib import Path

SOURCE = Path("FINAL_WORLD_CLASS_CAPTIONS")

def validate_caption(cap, filename):
    """Check caption for issues, return list of problems"""
    issues = []

    # Check for unwanted words
    if re.search(r'\bsimple\s+', cap, flags=re.I):
        issues.append("❌ contains 'simple'")
    if re.search(r'\bmale\b', cap, flags=re.I):
        issues.append("❌ contains 'male'")
    if re.search(r'\bfemale\b', cap, flags=re.I):
        issues.append("❌ contains 'female'")
    if re.search(r'\bhispanic\b', cap, flags=re.I):
        issues.append("❌ contains 'hispanic'")
    if re.search(r'\blips\b', cap, flags=re.I):
        issues.append("❌ contains 'lips'")

    # Check for "wearing" with facial hair (should be "with")
    if re.search(r'wearing\s+(?:stubble|beard|mustache|goatee)', cap, flags=re.I):
        issues.append("❌ 'wearing' + facial hair")

    # Check for duplicate eye colors
    eye_pattern = r'\b(?:brown|blue|green|gray|grey|hazel|black|dark)\s+eyes\b'
    eye_count = len(re.findall(eye_pattern, cap, flags=re.I))
    if eye_count > 1:
        issues.append(f"❌ {eye_count} eye colors")

    # Check for broken "eyes," (no color)
    if ', eyes,' in cap.lower() or cap.lower().endswith(', eyes'):
        issues.append("❌ broken 'eyes' (no color)")

    # Check has eye color
    has_eyes = bool(re.search(eye_pattern, cap, flags=re.I))
    if not has_eyes:
        issues.append("⚠️ missing eye color")

    # Check ends with "pixel art style"
    if not cap.endswith('pixel art style'):
        issues.append("❌ wrong ending")

    # Check for artifacts
    if 'hard color borders' in cap.lower():
        issues.append("❌ 'hard color borders'")
    if 'sharp pixel edges' in cap.lower():
        issues.append("❌ 'sharp pixel edges'")

    # Check character length
    if len(cap) < 100:
        issues.append(f"⚠️ very short ({len(cap)} chars)")
    elif len(cap) > 500:
        issues.append(f"⚠️ very long ({len(cap)} chars)")

    return issues

print("🔍 COMPREHENSIVE VALIDATION OF ALL 203 CAPTIONS\n")
print("=" * 80)

total_files = 0
total_issues = 0
critical_issues = []
warnings = []

for txt_file in sorted(SOURCE.glob("*.txt")):
    with open(txt_file, 'r') as f:
        caption = f.read().strip()

    issues = validate_caption(caption, txt_file.name)
    total_files += 1

    if issues:
        total_issues += 1
        # Separate critical issues from warnings
        critical = [i for i in issues if i.startswith("❌")]
        warn = [i for i in issues if i.startswith("⚠️")]

        if critical:
            critical_issues.append((txt_file.name, critical, caption))
            print(f"\n🔴 {txt_file.name} ({len(caption)} chars)")
            for issue in critical:
                print(f"   {issue}")
        elif warn:
            warnings.append((txt_file.name, warn, caption))

print("\n" + "=" * 80)
print(f"\n📊 VALIDATION SUMMARY:")
print(f"   Total files checked: {total_files}")
print(f"   Files with critical issues: {len(critical_issues)}")
print(f"   Files with warnings only: {len(warnings)}")
print(f"   Clean files: {total_files - len(critical_issues) - len(warnings)}")

if critical_issues:
    print(f"\n🔴 CRITICAL ISSUES FOUND IN {len(critical_issues)} FILES:")
    for name, issues, cap in critical_issues[:15]:  # Show first 15
        print(f"\n{name}:")
        for issue in issues:
            print(f"  {issue}")
        print(f"  Caption: {cap[:100]}...")

if warnings and not critical_issues:
    print(f"\n⚠️  WARNINGS IN {len(warnings)} FILES (non-critical):")
    for name, warns, cap in warnings[:10]:  # Show first 10
        print(f"\n{name}:")
        for warn in warns:
            print(f"  {warn}")

if not critical_issues and not warnings:
    print("\n✅ ALL CAPTIONS PASSED VALIDATION!")
    print("🎉 Ready for training!")
