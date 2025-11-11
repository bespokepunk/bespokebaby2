#!/usr/bin/env python3
"""
Phase 1A: Enhanced Caption Generator for Accessory Detail
Systematically improves captions with structural descriptions
"""

import os
import re
import shutil
from datetime import datetime

CAPTION_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"
BACKUP_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/caption_backups/phase1a_backup"
LOG_FILE = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/docs/PHASE1A_CAPTION_ENHANCEMENTS.md"

# Create backup directory
os.makedirs(BACKUP_DIR, exist_ok=True)

# Enhancement templates
ACCESSORY_ENHANCEMENTS = {
    # HATS
    r'\bwearing (\w+) hat\b': {
        'pattern': r'wearing (\w+) hat',
        'enhanced': lambda m: f'wearing {m.group(1)} structured baseball cap with curved front brim covering top of head down to hairline',
        'accessory_type': 'hat'
    },
    r'\bwearing (\w+) baseball cap\b': {
        'pattern': r'wearing (\w+) baseball cap',
        'enhanced': lambda m: f'wearing {m.group(1)} structured baseball cap with curved front brim and flat crown, cap sits on top of head covering hairline',
        'accessory_type': 'hat'
    },

    # SUNGLASSES
    r'\bwearing (\w+) (\w+) shades\b': {
        'pattern': r'wearing (\w+) (\w+) shades',
        'enhanced': lambda m: f'wearing {m.group(1)} rectangular {m.group(2)} sunglasses with thin {m.group(1)} plastic frames and thin temples behind ears, lenses completely cover eyes',
        'accessory_type': 'sunglasses'
    },
    r'\bwearing (\w+) sunglasses\b': {
        'pattern': r'wearing (\w+) sunglasses',
        'enhanced': lambda m: f'wearing {m.group(1)} rectangular sunglasses with thin plastic frames and thin temples behind ears, lenses completely cover eyes',
        'accessory_type': 'sunglasses'
    },

    # EARRINGS
    r'\bwearing (\w+) earring': {
        'pattern': r'wearing (\w+) earring',
        'enhanced': lambda m: f'wearing {m.group(1)} stud earring visible on side of head next to ear, small distinct point of color',
        'accessory_type': 'earring'
    },
    r'\b(\w+) earring\b': {
        'pattern': r'(?<!wearing )(\w+) earring',
        'enhanced': lambda m: f'{m.group(1)} stud earring visible on side of head next to ear, small distinct point of color',
        'accessory_type': 'earring'
    },

    # BOWS
    r'\bwearing (\w+) bow in hair\b': {
        'pattern': r'wearing (\w+) bow in hair',
        'enhanced': lambda m: f'wearing large {m.group(1)} ribbon bow positioned on top center of head clearly visible above hairline, traditional bow shape with two loops and center knot, {m.group(1)} color clearly distinct from hair',
        'accessory_type': 'bow'
    },
}

# Color distinctiveness enhancements
COLOR_ENHANCEMENTS = {
    r'\bbrown eyes.*?brown hair\b': 'dark brown eyes clearly distinct from lighter brown hair',
    r'\bbrown hair.*?brown eyes\b': 'lighter brown hair clearly distinct from dark brown eyes',
    r'\bblack hair.*?dark skin\b': 'jet black hair with hard edge against dark brown skin',
    r'\bdark skin.*?black hair\b': 'dark brown skin with hard edge against jet black hair',
    r'\bblonde hair.*?light skin\b': 'bright blonde hair clearly distinct from light peachy skin tone',
    r'\blight skin.*?blonde hair\b': 'light peachy skin tone clearly distinct from bright blonde hair',
}

# Track changes
changes_log = []

def backup_captions():
    """Create backup of all caption files before modification"""
    print("Creating backup of caption files...")
    for filename in os.listdir(CAPTION_DIR):
        if filename.endswith('.txt'):
            src = os.path.join(CAPTION_DIR, filename)
            dst = os.path.join(BACKUP_DIR, filename)
            shutil.copy2(src, dst)
    print(f"✓ Backup created at: {BACKUP_DIR}")

def enhance_caption(caption_text, filename):
    """Enhance a single caption with accessory detail and color distinctiveness"""
    original = caption_text
    enhanced = caption_text
    changes = []

    # Apply accessory enhancements
    for pattern_key, enhancement in ACCESSORY_ENHANCEMENTS.items():
        pattern = enhancement['pattern']
        if re.search(pattern, enhanced, re.IGNORECASE):
            new_text = re.sub(pattern, enhancement['enhanced'], enhanced, count=1, flags=re.IGNORECASE)
            if new_text != enhanced:
                changes.append(f"Enhanced {enhancement['accessory_type']}: {pattern}")
                enhanced = new_text

    # Apply color distinctiveness
    for pattern, replacement in COLOR_ENHANCEMENTS.items():
        if re.search(pattern, enhanced, re.IGNORECASE):
            # Check if already enhanced
            if 'clearly distinct' not in enhanced:
                new_text = re.sub(pattern, replacement, enhanced, count=1, flags=re.IGNORECASE)
                if new_text != enhanced:
                    changes.append(f"Added color distinctiveness")
                    enhanced = new_text

    # Add pixel art clarity keywords if not present
    if 'hard color borders' not in enhanced.lower():
        enhanced = enhanced.rstrip() + ', hard color borders, sharp pixel edges'
        changes.append("Added pixel art clarity keywords")

    if enhanced != original:
        changes_log.append({
            'file': filename,
            'changes': changes,
            'before': original,
            'after': enhanced
        })

    return enhanced

def process_all_captions():
    """Process all caption files"""
    total_files = 0
    enhanced_files = 0

    print("\n" + "=" * 100)
    print("PHASE 1A: CAPTION ENHANCEMENT - ACCESSORY DETAIL + COLOR DISTINCTIVENESS")
    print("=" * 100)
    print()

    for filename in sorted(os.listdir(CAPTION_DIR)):
        if not filename.endswith('.txt'):
            continue

        total_files += 1
        filepath = os.path.join(CAPTION_DIR, filename)

        # Read original caption
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read().strip()

        # Enhance caption
        enhanced = enhance_caption(original, filename)

        # Write enhanced caption if changed
        if enhanced != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(enhanced)
            enhanced_files += 1
            print(f"✓ Enhanced: {filename}")

    print()
    print("=" * 100)
    print(f"SUMMARY: Enhanced {enhanced_files} out of {total_files} captions")
    print("=" * 100)

    return enhanced_files, total_files

def write_enhancement_log():
    """Write detailed log of all changes"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("# Phase 1A Caption Enhancements\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Enhancements:** {len(changes_log)}\n\n")
        f.write("---\n\n")

        f.write("## Enhancement Strategy\n\n")
        f.write("### Accessory Detail Enhancements\n\n")
        f.write("1. **Hats:** Add brim type, crown shape, placement on head\n")
        f.write("2. **Sunglasses:** Add frame type, lens shape, temple position\n")
        f.write("3. **Earrings:** Add size, placement, distinctiveness\n")
        f.write("4. **Bows:** Add size, placement, shape, color distinction\n\n")

        f.write("### Color Distinctiveness\n\n")
        f.write("- Add 'clearly distinct' keywords for similar colors (brown eyes + brown hair)\n")
        f.write("- Add 'hard edge' keywords for feature boundaries\n")
        f.write("- Emphasize contrast between adjacent features\n\n")

        f.write("### Pixel Art Clarity\n\n")
        f.write("- Add 'hard color borders, sharp pixel edges' to all captions\n\n")

        f.write("---\n\n")
        f.write("## Detailed Changes\n\n")

        for i, change in enumerate(changes_log, 1):
            f.write(f"### {i}. {change['file']}\n\n")
            f.write("**Changes Applied:**\n")
            for c in change['changes']:
                f.write(f"- {c}\n")
            f.write("\n")
            f.write("**Before:**\n")
            f.write(f"```\n{change['before']}\n```\n\n")
            f.write("**After:**\n")
            f.write(f"```\n{change['after']}\n```\n\n")
            f.write("---\n\n")

    print(f"\n✓ Enhancement log saved to: {LOG_FILE}")

def main():
    print("=" * 100)
    print("PHASE 1A: CAPTION ENHANCEMENT FOR NEXT TRAINING RUN")
    print("=" * 100)
    print()
    print("Strategy:")
    print("  1. Backup all captions")
    print("  2. Enhance accessories with structural detail")
    print("  3. Add color distinctiveness keywords")
    print("  4. Add pixel art clarity keywords")
    print()
    print("Expected Impact:")
    print("  - 40-60% improvement in accessory rendering")
    print("  - 15-20% improvement in color distinctiveness")
    print("  - Better pixel-perfect boundaries")
    print()

    input("Press ENTER to continue...")
    print()

    # Step 1: Backup
    backup_captions()

    # Step 2: Process
    enhanced_count, total_count = process_all_captions()

    # Step 3: Log
    write_enhancement_log()

    print()
    print("=" * 100)
    print("✅ PHASE 1A COMPLETE!")
    print("=" * 100)
    print()
    print(f"Files enhanced: {enhanced_count}/{total_count}")
    print(f"Backup location: {BACKUP_DIR}")
    print(f"Log file: {LOG_FILE}")
    print()
    print("Next Steps:")
    print("  1. Review enhancement log to verify changes")
    print("  2. Spot-check 5-10 enhanced captions manually")
    print("  3. Proceed to Phase 1B (improved downscaling) or Phase 2 (256px training)")
    print()

if __name__ == "__main__":
    main()
