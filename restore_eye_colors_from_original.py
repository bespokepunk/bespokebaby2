#!/usr/bin/env python3
"""
Restore Eye Colors from Original Captions

Extract eye colors from original training captions and restore them to V4 captions.
"""

import re
from pathlib import Path

V4_DIR = Path("improved_samples_v4")
ORIGINAL_DIR = Path("runpod_package/training_data")
OUTPUT_DIR = Path("improved_samples_v5_auto")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_eye_color(caption):
    """Extract eye color from caption"""
    patterns = [
        r'(dual colored eyes[^,]*)',
        r'(deep blue eyes)',
        r'(light brown eyes)',
        r'(dark brown eyes)',
        r'(medium brown eyes)',
        r'(light honey brown eyes)',
        r'(light medium brownred eyes)',
        r'(dark red brown eyes)',
        r'(brown eyes)',
        r'(blue eyes)',
        r'(green eyes)',
        r'(hazel eyes)',
        r'(gray eyes)',
        r'(grey eyes)',
        r'(black eyes)',
    ]

    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            return match.group(1)

    return None

def has_eye_color(caption):
    """Check if caption already has eye color"""
    patterns = [
        r'\bbrown eyes\b', r'\bblue eyes\b', r'\bgreen eyes\b',
        r'\bhazel eyes\b', r'\bgray eyes\b', r'\bgrey eyes\b',
        r'\bblack eyes\b', r'\bdual colored eyes\b',
        r'\bdeep blue eyes\b', r'\bdark brown eyes\b',
        r'\blight brown eyes\b', r'\bmedium brown eyes\b'
    ]

    return any(re.search(pattern, caption, re.IGNORECASE) for pattern in patterns)

def add_eye_color_to_caption(caption, eye_color):
    """Add eye color to caption in the right place"""
    # Try to insert after expression
    if 'neutral expression' in caption:
        caption = caption.replace('neutral expression', f'neutral expression, {eye_color}')
    elif 'slight smile' in caption:
        caption = caption.replace('slight smile', f'slight smile, {eye_color}')
    elif ', eyes,' in caption:
        # Replace bare "eyes"
        caption = caption.replace(', eyes,', f', {eye_color},')
    else:
        # Insert before skin tone
        caption = re.sub(r'(,\s*(?:light|medium|dark|tan)\s+(?:light\s+)?(?:skin|green skin))',
                       f', {eye_color}\\1', caption)

    return caption

def main():
    restored_count = 0
    still_missing_count = 0
    already_has_count = 0
    still_missing_files = []

    print("🔍 Restoring eye colors from original captions...")
    print()

    for v4_file in sorted(V4_DIR.glob("*.txt")):
        # Read V4 caption
        with open(v4_file, 'r') as f:
            v4_caption = f.read().strip()

        # Check if V4 already has eye color
        if has_eye_color(v4_caption):
            already_has_count += 1
            output_caption = v4_caption
        else:
            # Try to get from original
            original_file = ORIGINAL_DIR / v4_file.name
            if original_file.exists():
                with open(original_file, 'r') as f:
                    original_caption = f.read().strip()

                eye_color = extract_eye_color(original_caption)
                if eye_color:
                    output_caption = add_eye_color_to_caption(v4_caption, eye_color)
                    restored_count += 1
                    print(f"✅ {v4_file.name}: Restored '{eye_color}'")
                else:
                    output_caption = v4_caption
                    still_missing_count += 1
                    still_missing_files.append(v4_file.name)
                    print(f"⚠️  {v4_file.name}: Still missing (not in original)")
            else:
                output_caption = v4_caption
                still_missing_count += 1
                still_missing_files.append(v4_file.name)
                print(f"⚠️  {v4_file.name}: Original not found")

        # Save to V5
        output_file = OUTPUT_DIR / v4_file.name
        with open(output_file, 'w') as f:
            f.write(output_caption)

    print()
    print("=" * 70)
    print("📊 EYE COLOR RESTORATION REPORT")
    print("=" * 70)
    print(f"Already had eye colors: {already_has_count}")
    print(f"Restored from originals: {restored_count}")
    print(f"Still missing (need manual): {still_missing_count}")
    print(f"Total captions: {len(list(V4_DIR.glob('*.txt')))}")
    print()
    if still_missing_files:
        print(f"📋 Files still needing eye colors ({len(still_missing_files)}):")
        for filename in still_missing_files[:20]:
            print(f"   - {filename}")
        if len(still_missing_files) > 20:
            print(f"   ... and {len(still_missing_files) - 20} more")
    print()
    print(f"📁 Output: {OUTPUT_DIR}/")
    print("=" * 70)

if __name__ == "__main__":
    main()
