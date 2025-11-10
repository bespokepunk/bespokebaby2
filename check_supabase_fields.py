#!/usr/bin/env python3
"""
Check what fields exist in Supabase caption_reviews table
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get one record to see all fields
response = supabase.table("caption_reviews").select("*").limit(1).execute()

if response.data:
    record = response.data[0]
    print("="*80)
    print("SUPABASE RECORD FIELDS:")
    print("="*80)
    print()

    for key, value in record.items():
        value_preview = str(value)[:80] if value else "None"
        print(f"{key:25s}: {value_preview}")

    print()
    print("="*80)
    print("CHECKING FOR final_caption_txt:")
    print("="*80)
    print()

    if 'final_caption_txt' in record:
        print(f"✓ final_caption_txt EXISTS")
        print(f"  Content: {record['final_caption_txt']}")
    else:
        print(f"✗ final_caption_txt DOES NOT EXIST")

    print()
