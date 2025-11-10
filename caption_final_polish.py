#!/usr/bin/env python3
"""
Final caption polish - targeted fixes for remaining problematic captions
"""

import json
import re

# Load refined captions
with open('merged_captions_v3_refined.json', 'r') as f:
    records = json.load(f)

print("=" * 100)
print("FINAL CAPTION POLISH - TARGETED FIXES")
print("=" * 100)
print()

# Files with remaining issues
problem_files = [
    'lad_005_copper.png',
    'lad_006_redshift.png',
    'lad_012_chromium.png',
    'lad_026_chromiumabstractsalmon.png',
    'lad_027_chromiumabstractyellow.png',
    'lad_028_chromiumabstractgreen.png',
    'lad_037_aressprout.png',
    'lad_059_SamAScientist.png',
    'lady_099_domino.png',
    'lad_014_sugar.png',  # TODO text remaining
]

# Manual fixes for specific problematic captions
specific_fixes = {}

# Process all records
polished_records = []
fixes_applied = 0

for record in records:
    filename = record['filename']
    refined = record.get('merged_caption_v3_refined', '')

    # Apply aggressive cleaning for problem files
    if filename in problem_files:
        polished = refined

        # Remove parenthetical descriptions/instructions
        polished = re.sub(r'\([^)]*describe[^)]*\)', '', polished, flags=re.IGNORECASE)

        # Remove explanatory clauses
        polished = re.sub(r',\s*blue colors are due to editing[^,]*,', ',', polished, flags=re.IGNORECASE)
        polished = re.sub(r',\s*but those would just be[^,]*,', ',', polished, flags=re.IGNORECASE)

        # Clean up conversational text
        polished = re.sub(r',\s*but you can obviously see[^,]*,', ',', polished, flags=re.IGNORECASE)
        polished = re.sub(r'his hair is[^,]*but you[^,]*,', '', polished, flags=re.IGNORECASE)
        polished = re.sub(r'hair is[^,]*but you[^,]*,', '', polished, flags=re.IGNORECASE)

        # Fix specific patterns
        polished = re.sub(r'\s*-\s+hiis\s+', ' ', polished)
        polished = re.sub(r'yo ucan', 'you can', polished)
        polished = re.sub(r'woudl jsut', 'would just', polished)

        # Remove duplicate hair descriptions (when intent parsing added text)
        polished = re.sub(r'(hair[^,]*),\s*hair is[^,]*,', r'\1,', polished, flags=re.IGNORECASE)

        # Clean up comma sequences
        polished = re.sub(r',\s*,+', ',', polished)
        polished = re.sub(r',\s+', ', ', polished)
        polished = re.sub(r'\s+', ' ', polished)

        polished = polished.strip()

        if polished != refined:
            fixes_applied += 1
            print(f"✓ Fixed: {filename}")

        record['merged_caption_v3_final'] = polished
    else:
        # For non-problem files, the refined version is final
        record['merged_caption_v3_final'] = refined

    polished_records.append(record)

print(f"\n✓ Applied targeted fixes to {fixes_applied} captions\n")

# Save final polished captions
with open('merged_captions_v3_final.json', 'w') as f:
    json.dump(polished_records, f, indent=2)

print(f"💾 Saved to: merged_captions_v3_final.json")
print()

# Show examples of fixed captions
print("=" * 100)
print("EXAMPLES OF FIXED CAPTIONS")
print("=" * 100)
print()

for record in polished_records:
    if record['filename'] in problem_files[:5]:
        print(f"File: {record['filename']}")
        print(f"FINAL: {record['merged_caption_v3_final'][:300]}...")
        print()

print("✅ Final polish complete!")
print()
print("Next steps:")
print("  1. Update Supabase with final merged captions")
print("  2. Build review UI")
print("  3. Update .txt files after user approval")
print()
