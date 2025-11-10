#!/usr/bin/env python3
"""
Update Supabase final_caption_txt field from training files
This ensures Supabase has the correct training captions
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

def main():
    print("="*80)
    print("UPDATING SUPABASE FROM TRAINING FILES")
    print("="*80)
    print()

    # Connect to Supabase
    print("1. Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✓ Connected")
    print()

    # Get all training files
    print("2. Reading training files...")
    training_files = [f for f in os.listdir(TRAINING_DIR) if f.endswith('.txt')]
    print(f"   ✓ Found {len(training_files)} .txt files")
    print()

    # Update each record
    print("3. Updating Supabase records...")
    updated = 0
    errors = 0

    for txt_file in tqdm(training_files, desc="Updating"):
        filename = txt_file.replace('.txt', '.png')
        txt_path = os.path.join(TRAINING_DIR, txt_file)

        # Read training caption
        with open(txt_path, 'r') as f:
            training_caption = f.read().strip()

        try:
            # Update Supabase record
            supabase.table("caption_reviews").update({
                "final_caption_txt": training_caption
            }).eq("filename", filename).execute()

            updated += 1
        except Exception as e:
            print(f"   ✗ Error updating {filename}: {e}")
            errors += 1

    print()
    print("="*80)
    print("UPDATE COMPLETE")
    print("="*80)
    print()
    print(f"✅ Updated: {updated} records")
    if errors > 0:
        print(f"❌ Errors: {errors} records")
    print()
    print("Now Supabase final_caption_txt contains the training captions!")
    print()

if __name__ == "__main__":
    main()
