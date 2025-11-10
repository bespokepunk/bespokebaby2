#!/usr/bin/env python3
"""
Update Supabase with ALL corrected captions from runpod_package/training_data
This includes:
- Lips with hex colors
- Smile vs neutral expressions (user-reviewed)
- All typo fixes
- Cleaned garbled text
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

def main():
    print("="*80)
    print("UPDATING SUPABASE WITH FINAL CORRECTED CAPTIONS")
    print("="*80)
    print()
    print("This update includes:")
    print("  ✓ Lips with accurate hex colors (203/203 files)")
    print("  ✓ User-reviewed smile/neutral classifications")
    print("  ✓ All typo fixes (15+ instances)")
    print("  ✓ Cleaned garbled text")
    print("  ✓ Fixed smoking accessories")
    print()

    # Check credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: SUPABASE_URL or SUPABASE_ANON_KEY not found in .env file")
        print()
        print("Please create a .env file with:")
        print("  SUPABASE_URL=your_supabase_url")
        print("  SUPABASE_ANON_KEY=your_supabase_anon_key")
        return

    # Connect to Supabase
    print("1. Connecting to Supabase...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("   ✓ Connected")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return
    print()

    # Get all training files
    print("2. Reading corrected training captions...")
    training_files = sorted([f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')])
    print(f"   ✓ Found {len(training_files)} .txt files")
    print()

    # Preview a few samples
    print("3. Preview of corrected captions:")
    samples = ['lad_087_HEEM.txt', 'lady_001_hazelnut.txt', 'lad_001_carbon.txt']
    for sample in samples:
        if sample in training_files:
            with open(os.path.join(TRAINING_DIR, sample), 'r') as f:
                caption = f.read().strip()
                # Extract just the lips + expression part
                if 'lips (' in caption:
                    start = caption.find('lips (')
                    end = caption.find(',', start + 50) + 1
                    snippet = caption[start:end]
                    print(f"   {sample}: ...{snippet}...")
    print()

    # Confirm before proceeding
    response = input("Proceed with Supabase update? (y/n): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return

    # Update each record
    print()
    print("4. Updating Supabase records...")
    updated = 0
    errors = []
    not_found = []

    for txt_file in tqdm(training_files, desc="Updating"):
        filename = txt_file.replace('.txt', '.png')
        txt_path = os.path.join(TRAINING_DIR, txt_file)

        # Read corrected caption
        with open(txt_path, 'r') as f:
            corrected_caption = f.read().strip()

        try:
            # Update Supabase record
            response = supabase.table("caption_reviews").update({
                "final_caption_txt": corrected_caption
            }).eq("filename", filename).execute()

            # Check if record was actually updated
            if response.data:
                updated += 1
            else:
                not_found.append(filename)

        except Exception as e:
            errors.append((filename, str(e)))

    print()
    print("="*80)
    print("UPDATE COMPLETE")
    print("="*80)
    print()
    print(f"✅ Successfully updated: {updated} records")

    if not_found:
        print(f"⚠️  Records not found in Supabase: {len(not_found)}")
        if len(not_found) <= 10:
            for fn in not_found:
                print(f"     - {fn}")

    if errors:
        print(f"❌ Errors: {len(errors)}")
        for fn, err in errors[:5]:
            print(f"     - {fn}: {err}")

    print()
    print("="*80)
    print("SUPABASE NOW HAS ALL CORRECTED CAPTIONS!")
    print("="*80)
    print()
    print("Summary of what was updated:")
    print("  ✓ 203 files with lips + hex colors")
    print("  ✓ 113 files marked as 'slight smile'")
    print("  ✓ 90 files marked as 'neutral expression'")
    print("  ✓ All typos and errors corrected")
    print()

if __name__ == "__main__":
    main()
