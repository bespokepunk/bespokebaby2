#!/usr/bin/env python3
"""
Sync all 28 fixed caption files from sd15_training_512/ to all other directories and Supabase
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

# The 29 files that were fixed
FIXED_FILES = [
    # Sam Altman (5 files)
    "lad_012_chromium.txt",
    "lad_026_chromiumabstractsalmon.txt",
    "lad_027_chromiumabstractyellow.txt",
    "lad_028_chromiumabstractgreen.txt",
    "lad_059_SamAScientist.txt",
    # US Presidents (4 files)
    "lad_002_cash.txt",
    "lad_015_jackson.txt",
    "lad_016_tungsten.txt",
    "lad_017_ink.txt",
    # Leonardo da Vinci (1 file)
    "lad_039_davinci-2.txt",
    # Celebrities (2 files)
    "lady_033_staranise.txt",
    "lady_072_tangerine.txt",
    # Movie/TV characters (10 files)
    "lady_000_lemon.txt",
    "lady_006_pepper.txt",
    "lady_007_alloy.txt",
    "lady_008_pinksilk.txt",
    "lady_009_bluesilk.txt",
    "lady_051_rosieabstract.txt",
    "lady_052_pinksilkabstract.txt",
    "lady_053_pepperabstract.txt",
    "lady_056_alloyabstract.txt",
    "lady_057_bluesilkabstract.txt",
    # Mona Lisa & WifeJak (2 files)
    "lady_066_monalisa-3.txt",
    "lady_031_paprika.txt",
    # Luke surfer (5 files)
    "lad_055_Luke.txt",
    "lad_055_Luke3.txt",
    "lad_055_Luke6.txt",
    "lad_055_Luke8.txt",
    "lad_055_Luke10.txt",
]

def sync_to_directories():
    """Copy all fixed caption files to all destination directories"""
    print(f"\n📁 Syncing {len(FIXED_FILES)} files to {len(DEST_DIRS)} directories...")

    total_copied = 0
    for dest_dir in DEST_DIRS:
        if not os.path.exists(dest_dir):
            print(f"  ⚠️  Skipping {dest_dir} (doesn't exist)")
            continue

        for txt_file in FIXED_FILES:
            source_path = os.path.join(SOURCE_DIR, txt_file)
            dest_path = os.path.join(dest_dir, txt_file)

            if os.path.exists(source_path):
                shutil.copy2(source_path, dest_path)
                total_copied += 1

    print(f"  ✅ Copied {total_copied} files across all directories")

def sync_to_supabase():
    """Update Supabase database with all fixed captions"""
    print(f"\n💾 Syncing {len(FIXED_FILES)} captions to Supabase...")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    updated = 0
    for txt_file in tqdm(FIXED_FILES, desc="  Updating"):
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
    print("🚀 Starting caption sync process...")
    print(f"   Source: {SOURCE_DIR}")
    print(f"   Files to sync: {len(FIXED_FILES)}")

    # Sync to all directories
    sync_to_directories()

    # Sync to Supabase
    sync_to_supabase()

    print("\n✨ All caption syncing complete!")

if __name__ == "__main__":
    main()
