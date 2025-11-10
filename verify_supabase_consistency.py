#!/usr/bin/env python3
"""
Verify Supabase consistency after update
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

def main():
    print("="*80)
    print("VERIFYING SUPABASE CONSISTENCY")
    print("="*80)
    print()

    # Connect to Supabase
    print("1. Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✓ Connected")
    print()

    # Fetch all records
    print("2. Fetching all caption_reviews from Supabase...")
    response = supabase.table("caption_reviews").select("filename, final_caption_txt").execute()
    supabase_records = {r['filename']: r['final_caption_txt'] for r in response.data}
    print(f"   ✓ Found {len(supabase_records)} records")
    print()

    # Get local files
    print("3. Reading local training files...")
    local_files = {}
    for txt_file in os.listdir(TRAINING_DIR):
        if txt_file.endswith('.txt'):
            png_file = txt_file.replace('.txt', '.png')
            with open(os.path.join(TRAINING_DIR, txt_file), 'r') as f:
                local_files[png_file] = f.read().strip()
    print(f"   ✓ Found {len(local_files)} local files")
    print()

    # Compare
    print("4. Comparing local vs Supabase...")
    matches = 0
    mismatches = 0
    missing_in_supabase = []
    missing_locally = []

    for filename, local_caption in local_files.items():
        if filename not in supabase_records:
            missing_in_supabase.append(filename)
        elif supabase_records[filename] == local_caption:
            matches += 1
        else:
            mismatches += 1

    for filename in supabase_records:
        if filename not in local_files:
            missing_locally.append(filename)

    print()
    print("="*80)
    print("VERIFICATION RESULTS")
    print("="*80)
    print()
    print(f"✅ Matches: {matches} files")
    print(f"⚠️  Mismatches: {mismatches} files")
    print(f"⚠️  Missing in Supabase: {len(missing_in_supabase)} files")
    print(f"⚠️  Missing locally: {len(missing_locally)} files")
    print()

    # Check for key features
    print("5. Checking for corrected features in Supabase...")
    smile_count = 0
    neutral_count = 0
    has_lips = 0
    has_expression = 0

    for filename, caption in supabase_records.items():
        if 'lips (' in caption:
            has_lips += 1
        if 'slight smile' in caption:
            smile_count += 1
            has_expression += 1
        elif 'neutral expression' in caption:
            neutral_count += 1
            has_expression += 1

    print()
    print(f"   Lips with hex colors: {has_lips}/{len(supabase_records)} ✓")
    print(f"   Expression classification: {has_expression}/{len(supabase_records)} ✓")
    print(f"   - Slight smile: {smile_count} ({100*smile_count/len(supabase_records):.1f}%)")
    print(f"   - Neutral: {neutral_count} ({100*neutral_count/len(supabase_records):.1f}%)")
    print()

    if matches == len(local_files) and mismatches == 0:
        print("="*80)
        print("✅ PERFECT CONSISTENCY!")
        print("   Supabase is fully synced with local training data")
        print("="*80)
    else:
        print("="*80)
        print("⚠️  INCONSISTENCIES FOUND")
        print("   Some records may need attention")
        print("="*80)

if __name__ == "__main__":
    main()
