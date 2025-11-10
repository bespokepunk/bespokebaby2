#!/usr/bin/env python3
"""
CAPTION RECONCILIATION - ONE SOURCE OF TRUTH

This script ensures consistency between:
1. Supabase database (caption_reviews table)
2. SUPABASE_REVIEW.html display
3. Actual training .txt files used for SD 1.5

It identifies discrepancies and provides options to fix them.
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Training data location (ACTUAL files used for training)
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

def main():
    print("="*80)
    print("CAPTION RECONCILIATION - ENSURING ONE SOURCE OF TRUTH")
    print("="*80)
    print()

    # Connect to Supabase
    print("1. Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch all captions from Supabase
    print("2. Fetching all captions from Supabase...")
    response = supabase.table("caption_reviews").select("*").execute()
    supabase_data = {row['filename']: row for row in response.data}
    print(f"   ✓ Found {len(supabase_data)} records in Supabase")
    print()

    # Check all training files
    print("3. Checking training .txt files...")
    training_files = [f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')]
    print(f"   ✓ Found {len(training_files)} .txt files in training directory")
    print()

    # Compare
    print("4. Comparing Supabase vs Training Files...")
    print()

    mismatches = []
    missing_in_supabase = []
    missing_in_training = []

    for txt_file in training_files:
        filename = txt_file.replace('.txt', '.png')
        txt_path = os.path.join(TRAINING_DIR, txt_file)

        # Read training file
        with open(txt_path, 'r') as f:
            training_caption = f.read().strip()

        # Check Supabase
        if filename in supabase_data:
            supabase_record = supabase_data[filename]

            # Get the final caption from Supabase
            # Priority: final_caption_txt > user_corrections > ai_caption > current_caption
            if supabase_record.get('final_caption_txt'):
                supabase_caption = supabase_record['final_caption_txt']
                source = "final_caption_txt"
            elif supabase_record.get('user_corrections'):
                supabase_caption = supabase_record['user_corrections']
                source = "user_corrections"
            elif supabase_record.get('ai_caption'):
                supabase_caption = supabase_record['ai_caption']
                source = "ai_caption"
            else:
                supabase_caption = supabase_record.get('current_caption', '')
                source = "current_caption"

            # Compare
            if training_caption != supabase_caption:
                mismatches.append({
                    'filename': filename,
                    'supabase_caption': supabase_caption,
                    'supabase_source': source,
                    'training_caption': training_caption
                })
        else:
            missing_in_supabase.append(filename)

    # Check for files in Supabase but not in training
    for filename in supabase_data:
        txt_file = filename.replace('.png', '.txt')
        if txt_file not in training_files:
            missing_in_training.append(filename)

    # Report Results
    print("="*80)
    print("RECONCILIATION RESULTS")
    print("="*80)
    print()

    if not mismatches and not missing_in_supabase and not missing_in_training:
        print("✅ PERFECT! All captions are consistent!")
        print()
        print("Supabase database matches training files exactly.")
        print("You have ONE source of truth.")
        return

    # Report mismatches
    if mismatches:
        print(f"⚠️  FOUND {len(mismatches)} MISMATCHES:")
        print()
        for i, mismatch in enumerate(mismatches[:5], 1):  # Show first 5
            print(f"{i}. {mismatch['filename']}")
            print(f"   Supabase ({mismatch['supabase_source']}): {mismatch['supabase_caption'][:80]}...")
            print(f"   Training file: {mismatch['training_caption'][:80]}...")
            print()

        if len(mismatches) > 5:
            print(f"   ... and {len(mismatches) - 5} more mismatches")
            print()

    if missing_in_supabase:
        print(f"⚠️  FOUND {len(missing_in_supabase)} FILES IN TRAINING BUT NOT IN SUPABASE:")
        for filename in missing_in_supabase[:10]:
            print(f"   - {filename}")
        if len(missing_in_supabase) > 10:
            print(f"   ... and {len(missing_in_supabase) - 10} more")
        print()

    if missing_in_training:
        print(f"⚠️  FOUND {len(missing_in_training)} FILES IN SUPABASE BUT NOT IN TRAINING:")
        for filename in missing_in_training[:10]:
            print(f"   - {filename}")
        if len(missing_in_training) > 10:
            print(f"   ... and {len(missing_in_training) - 10} more")
        print()

    # Offer solutions
    print("="*80)
    print("RECOMMENDED ACTIONS:")
    print("="*80)
    print()

    if mismatches:
        print("1. MISMATCHES: Training files don't match Supabase")
        print("   Solution: Update training files from Supabase (most recent/reviewed)")
        print("   Command: python update_training_from_supabase.py")
        print()

    if missing_in_supabase:
        print("2. MISSING IN SUPABASE: Some training files not in database")
        print("   Solution: Import missing files to Supabase")
        print("   Command: python import_missing_to_supabase.py")
        print()

    if missing_in_training:
        print("3. MISSING IN TRAINING: Some Supabase records have no training file")
        print("   Solution: Generate missing .txt files from Supabase")
        print("   Command: python export_supabase_to_training.py")
        print()

    print("="*80)
    print()

    # Save detailed report
    report = {
        'summary': {
            'total_training_files': len(training_files),
            'total_supabase_records': len(supabase_data),
            'mismatches': len(mismatches),
            'missing_in_supabase': len(missing_in_supabase),
            'missing_in_training': len(missing_in_training),
        },
        'mismatches': mismatches,
        'missing_in_supabase': missing_in_supabase,
        'missing_in_training': missing_in_training,
    }

    report_path = 'caption_reconciliation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"📄 Detailed report saved to: {report_path}")
    print()

if __name__ == "__main__":
    main()
