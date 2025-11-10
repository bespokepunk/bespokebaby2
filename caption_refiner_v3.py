#!/usr/bin/env python3
"""
Caption Refinement V3
Fixes instruction text, typos, adds missing hex codes, resolves TODOs
"""

import json
import re
from PIL import Image
import numpy as np
from collections import Counter

# Load merged captions
with open('merged_captions_v3.json', 'r') as f:
    records = json.load(f)

# Load gap analysis
with open('gap_analysis_report_v3.json', 'r') as f:
    gap_report = json.load(f)

print("=" * 100)
print("CAPTION REFINEMENT V3 - FIXING ISSUES")
print("=" * 100)
print()

def fix_typos(text):
    """Fix common typos while preserving intent"""
    typo_map = {
        r'\byo u\b': 'you',
        r'\bliek\b': 'like',
        r'\bteh\b': 'the',
        r'\badn\b': 'and',
        r'\benahnce\b': 'enhance',
        r'\bhaoirc\b': 'hair',
        r'\brbowns\b': 'browns',
        r'\brkeds\b': 'reds',
        r'\bwith\s+with\b': 'with',
        r'\bhiglights\b': 'highlights',
        r'\brefelction\b': 'reflection',
        r'\bblaksi\b': 'blackish',
        r'\buneanrth\b': 'underneath',
        r'\bts hirt\b': 't shirt',
        r'\bpgimented\b': 'pigmented',
        r'\bcoloured\b': 'colored',
        r'\boverszied\b': 'oversized',
        r'\bcamoflaouged\b': 'camouflaged',
        r'\bschoo lkid\b': 'school kid',
        r'\blogner\b': 'longer',
        r'\bbuzszzed\b': 'buzzed',
        r'\bmxed\b': 'mixed',
        r'\bblack\s+dark brown\b': 'black-brown',
        r'\bdark dark\b': 'very dark',
    }

    result = text
    for pattern, replacement in typo_map.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result

def describe_color_enhanced(rgb):
    """Enhanced color description"""
    r, g, b = rgb

    # Calculate properties
    brightness = (r + g + b) / 3
    saturation = (max(r,g,b) - min(r,g,b))

    # Determine base color
    if saturation < 20:
        # Grayscale
        if brightness > 200: return "white"
        elif brightness > 180: return "very light gray"
        elif brightness > 160: return "light gray"
        elif brightness > 120: return "medium gray"
        elif brightness > 80: return "dark gray"
        elif brightness > 40: return "very dark gray"
        else: return "black"

    # Color detection
    if r > g and r > b:
        # Red family
        if r > 200 and g < 100 and b < 100:
            return "bright red"
        elif r > g + 30 and r > b + 30:
            if brightness > 180: return "light red"
            elif brightness > 140: return "red"
            else: return "dark red"
        elif r > g + 15 and g > b:
            # Orange/brown
            if brightness > 180: return "light orange"
            elif brightness > 140: return "orange"
            elif brightness > 100: return "brown"
            else: return "dark brown"
        elif r > b + 20 and r > 120 and g > 80:
            # Pink
            if brightness > 200: return "light pink"
            elif brightness > 160: return "pink"
            else: return "dark pink"

    elif g > r and g > b:
        # Green family
        if g > 200 and r < 100 and b < 100:
            return "bright green"
        elif g > r + 30 and g > b + 30:
            if brightness > 180: return "light green"
            elif brightness > 140: return "green"
            else: return "dark green"
        elif g > b + 15 and r > b:
            # Yellow/olive
            if brightness > 200: return "light yellow"
            elif brightness > 160: return "yellow"
            elif brightness > 120: return "olive"
            else: return "dark olive"

    elif b > r and b > g:
        # Blue family
        if b > 200 and r < 100 and g < 100:
            return "bright blue"
        elif b > r + 30 and b > g + 30:
            if brightness > 180: return "light blue"
            elif brightness > 140: return "blue"
            else: return "dark blue"
        elif b > r + 15 and g > r:
            # Cyan
            if brightness > 180: return "bright cyan"
            elif brightness > 140: return "cyan"
            else: return "dark cyan"
        elif b > g + 15 and r > g:
            # Purple
            if brightness > 180: return "light purple"
            elif brightness > 140: return "purple"
            else: return "dark purple"

    # Mixed colors
    if abs(r - g) < 30 and abs(g - b) < 30:
        # Close to gray
        if brightness > 180: return "very light gray"
        elif brightness > 140: return "light gray"
        elif brightness > 100: return "medium gray"
        else: return "dark gray"

    # Fallback - describe by dominant property
    if brightness > 160:
        return f"light color"
    elif brightness < 80:
        return f"dark color"
    else:
        return f"medium color"

def get_dominant_color(region_colors):
    """Get the most dominant color from a region"""
    if not region_colors:
        return None

    # Sort by count/percentage
    sorted_colors = sorted(region_colors, key=lambda x: x.get('count', 0), reverse=True)
    return sorted_colors[0]

def parse_user_intent(user_text):
    """Parse user's natural language to extract intended descriptions"""
    user_lower = user_text.lower()
    intents = {}

    # Hair style parsing
    if 'george washington' in user_lower or 'founding father' in user_lower:
        intents['hair_description'] = "white-gray hair styled in classic 18th century founding father fashion, with side rolls and back tail typical of the revolutionary war era"
    elif 'sam altman' in user_lower:
        intents['hair_description'] = "light auburn-brown hair with a classic short sides and swept-back top, professional modern executive style"
    elif 'nikola tesla' in user_lower or 'tesla' in user_lower:
        intents['hair_description'] = "dark brown hair parted in the middle with natural wave, classic late 19th century intellectual style"
    elif 'surfer' in user_lower:
        intents['hair_style_note'] = "surfer"
    elif 'emo' in user_lower or 'gothic' in user_lower:
        intents['hair_description'] = "long dark hair with face-framing layers, emo/gothic style"

    # Background parsing
    if 'checkered' in user_lower or 'checkerboard' in user_lower:
        intents['background_pattern'] = 'checkered'
    elif 'split' in user_lower:
        if 'horizontal' in user_lower:
            intents['background_pattern'] = 'split-horizontal'
        elif 'vertical' in user_lower:
            intents['background_pattern'] = 'split-vertical'
        else:
            intents['background_pattern'] = 'split'
    elif 'gradient' in user_lower:
        intents['background_pattern'] = 'gradient'
    elif 'electricity' in user_lower or 'electric' in user_lower:
        intents['background_note'] = 'electric/lightning effect'

    # Clothing mentions
    if 'suit' in user_lower and 'tie' in user_lower:
        intents['clothing'] = 'suit and tie'
    elif 'hoodie' in user_lower:
        intents['clothing'] = 'hoodie'
    elif 'jacket' in user_lower or 'coat' in user_lower:
        intents['clothing'] = 'jacket'

    return intents

def refine_caption(record):
    """Refine a single caption"""
    filename = record['filename']
    user_corr = record.get('user_corrections', '')
    merged = record['merged_caption_v3']
    sampled = record.get('sampled_trait_colors', {})

    # Parse user intent
    user_intent = parse_user_intent(user_corr)

    # Fix typos first
    caption = fix_typos(merged)

    # Remove instruction phrases
    instruction_patterns = [
        r'Explain\s+[^,]+?\s+if you had to,?\s*',
        r'Imagine\s+describing\s+[^,]+?,?\s*',
        r'Imagine\s+[^,]+?\s+describe\s+[^,]+?\s+here\s+[^,]+?,?\s*',
        r'describe\s+[^,]+?\s+better\s+[^,)]*',
        r'\([^)]*describe[^)]*better[^)]*\)',
        r'\([^)]*better[^)]*\)',
        r'do that here[^,]*,?\s*',
        r'adjust for that[^,]*,?\s*',
        r',\s*-\s+hiis',  # Artifact from instruction removal
    ]

    for pattern in instruction_patterns:
        caption = re.sub(pattern, '', caption, flags=re.IGNORECASE)

    # Apply parsed intent for specific descriptions
    if 'hair_description' in user_intent:
        # Replace hair section with proper description
        hair_pattern = r'(portrait of bespoke punk (lad|lady),\s*)([^,]+?)(\s*hair[^,]*)(,)'
        if re.search(hair_pattern, caption):
            # Replace the hair portion
            caption = re.sub(
                hair_pattern,
                r'\1' + user_intent['hair_description'] + r'\4',
                caption
            )

    # Add missing hex codes for eyes if we have the data
    eyes_pattern = r'(\w+\s+\w*\s*eyes)(?!\s*\(#)'
    if re.search(eyes_pattern, caption):
        # Check if we have eye color data
        eyes_left = sampled.get('eyes_left', [])
        eyes_right = sampled.get('eyes_right', [])

        if eyes_left:
            eye_color = get_dominant_color(eyes_left)
            if eye_color:
                hex_code = eye_color['hex']
                # Replace "color eyes" with "color eyes (#hex)"
                caption = re.sub(
                    eyes_pattern,
                    r'\1 (' + hex_code + ')',
                    caption,
                    count=1
                )

    # Fix "get lip color" TODO items
    if 'get lip' in caption.lower():
        mouth_region = sampled.get('mouth', [])
        if mouth_region:
            lip_color = get_dominant_color(mouth_region)
            if lip_color:
                hex_code = lip_color['hex']
                rgb = lip_color['rgb']
                color_desc = describe_color_enhanced(rgb)
                # Replace the TODO with actual lip color
                caption = re.sub(
                    r'get\s+lips?\s+color[^,]*',
                    f'{color_desc} lips ({hex_code})',
                    caption,
                    flags=re.IGNORECASE
                )

    # Clean up multiple commas
    caption = re.sub(r',\s*,', ',', caption)

    # Clean up extra spaces
    caption = re.sub(r'\s+', ' ', caption)

    # Clean up comma-space before period/end
    caption = re.sub(r',\s*$', '', caption)

    # Trim
    caption = caption.strip()

    return caption

print("🔧 Refining 203 captions...\n")

refined_records = []
changes_count = 0

for idx, record in enumerate(records, 1):
    original = record['merged_caption_v3']
    refined = refine_caption(record)

    if refined != original:
        changes_count += 1
        print(f"  [{idx}/203] {record['filename']}")
        print(f"    CHANGED: Yes")

    # Create refined record
    refined_record = record.copy()
    refined_record['merged_caption_v3_refined'] = refined
    refined_record['refinement_applied'] = (refined != original)

    refined_records.append(refined_record)

print(f"\n✓ Refined {changes_count} captions\n")

# Save refined captions
with open('merged_captions_v3_refined.json', 'w') as f:
    json.dump(refined_records, f, indent=2)

print(f"💾 Saved to: merged_captions_v3_refined.json")
print()

# Show some before/after examples
print("=" * 100)
print("BEFORE/AFTER EXAMPLES")
print("=" * 100)
print()

examples_shown = 0
for record in refined_records:
    if record['refinement_applied'] and examples_shown < 5:
        print(f"File: {record['filename']}")
        print(f"BEFORE: {record['merged_caption_v3'][:200]}...")
        print(f"AFTER:  {record['merged_caption_v3_refined'][:200]}...")
        print()
        examples_shown += 1

print("✅ Caption refinement complete!")
print()
print("Next steps:")
print("  1. Review refined captions")
print("  2. Run gap analysis again to verify fixes")
print("  3. Update Supabase with refined captions")
print()
