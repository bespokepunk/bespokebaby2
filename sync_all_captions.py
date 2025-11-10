#!/usr/bin/env python3
"""
Sync ALL caption files from sd15_training_512/ to all other directories and Supabase
"""

import os
import shutil
from supabase import create_client
from tqdm import tqdm

# Supabase credentials
SUPABASE_URL = "https://qwvncbcphuyobijakdsr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3dm5jYmNwaHV5b2JpamFrZHNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3MTA4NDgsImV4cCI6MjA3ODI4Njg0OH0.cE00n2favc7IK7fOwzCyDfTJK0tMntftb9gi_xfjpQ4"

# Source directory
SOURCE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

# All destination directories to sync to
DEST_DIRS = [
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks/bespokepunks_training",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks_captions_backup",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunktext",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunktextimages",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_training_data/10_bespokepunks",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_training_data_512/10_bespokepunks",
    "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/training_v2_package",
]

def get_all_caption_files():
    """Get all .txt files from source directory"""
    files = []
    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith('.txt'):
            files.append(filename)
    return sorted(files)

def sync_to_directories(caption_files):
    """Copy all caption files to all destination directories"""
    print(f"\n📁 Syncing {len(caption_files)} files to {len(DEST_DIRS)} directories...")

    total_copied = 0
    for dest_dir in DEST_DIRS:
        if not os.path.exists(dest_dir):
            print(f"  ⚠️  Skipping {dest_dir} (doesn't exist)")
            continue

        for txt_file in caption_files:
            source_path = os.path.join(SOURCE_DIR, txt_file)
            dest_path = os.path.join(dest_dir, txt_file)

            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                total_copied += 1

    print(f"  ✅ Copied {total_copied} files across all directories")

def sync_to_supabase(caption_files):
    """Update Supabase database with all captions"""
    print(f"\n💾 Syncing {len(caption_files)} captions to Supabase...")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    updated = 0
    for txt_file in tqdm(caption_files, desc="  Updating"):
        source_path = os.path.join(SOURCE_DIR, txt_file)
        filename = txt_file.replace('.txt', '.png')

        if os.path.exists(source_path):
            with open(source_path, 'r') as f:
                clean_caption = f.read().strip()

            try:
                supabase.table("caption_reviews").update({
                    "final_caption_txt": clean_caption
                }).eq("filename", filename).execute()
                updated += 1
            except Exception as e:
                print(f"    ❌ Error updating {filename}: {e}")

    print(f"  ✅ Updated {updated} records in Supabase")

def main():
    print("🚀 Starting comprehensive caption sync process...")

    caption_files = get_all_caption_files()
    print(f"   Source: {SOURCE_DIR}")
    print(f"   Files to sync: {len(caption_files)}")

    # Sync to all directories
    sync_to_directories(caption_files)

    # Sync to Supabase
    sync_to_supabase(caption_files)

    print("\n✨ All caption syncing complete!")

if __name__ == "__main__":
    main()
