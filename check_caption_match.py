#!/usr/bin/env python3
"""
Check if final_caption in Supabase matches training files
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get one specific record
response = supabase.table("caption_reviews").select("*").eq("filename", "lad_001_carbon.png").execute()

if response.data:
    record = response.data[0]

    print("="*80)
    print("CHECKING: lad_001_carbon.png")
    print("="*80)
    print()

    # Supabase captions
    print("SUPABASE final_caption:")
    print(record.get('final_caption', 'None'))
    print()

    print("SUPABASE user_corrections:")
    print(record.get('user_corrections', 'None'))
    print()

    # Training file
    txt_file = os.path.join(TRAINING_DIR, "lad_001_carbon.txt")
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            training_caption = f.read().strip()

        print("TRAINING FILE caption:")
        print(training_caption)
        print()

        # Compare
        final_caption = record.get('final_caption', '')
        if final_caption == training_caption:
            print("✅ MATCH: final_caption matches training file!")
        else:
            print("❌ MISMATCH: final_caption does NOT match training file")
            print()
            print("Differences:")
            print(f"  Supabase length: {len(final_caption)}")
            print(f"  Training length: {len(training_caption)}")
