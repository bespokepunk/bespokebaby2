#!/usr/bin/env python3
"""
Phase 1B: Simplified Caption Enhancement
Resolution: 512px (proven optimal)
Strategy: Minimal structural detail, NO micro-features

Key Principle: At 24x24 pixels, only describe what CAN physically exist
- ✅ "wearing sunglasses" (exists)
- ❌ "thin temples behind ears" (can't see at 24px)
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Backup directory
BACKUP_DIR = Path("caption_backups/phase1b_backup")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Training data directory
TRAINING_DATA_DIR = Path("runpod_package/training_data")

# Phase 1B Enhancement Rules: MINIMAL STRUCTURAL CLARITY
SIMPLIFICATION_RULES = {
    # Sunglasses: Remove ALL micro-details
    r'wearing (\w+) rectangular (\w+) sunglasses with thin (\w+) plastic frames and thin temples behind ears, lenses completely cover eyes(?: with white reflections)?':
        r'wearing \1 rectangular sunglasses covering eyes',

    r'wearing (\w+) rectangular stunner sunglasses with thin (\w+) plastic frames and thin temples behind ears, lenses completely cover eyes(?: with white reflections)?':
        r'wearing \1 rectangular sunglasses covering eyes',

    # Hats: Simplify to basic description
    r'wearing (\w+) structured baseball cap with curved front brim covering top of head down to hairline(?: with (?:white |black )?(?:small )?logo on front center)?':
        r'wearing \1 baseball cap',

    r'wearing (\w+) cap with curved brim':
        r'wearing \1 cap',

    # Earrings: Remove "drop" and "hanging" details
    r'wearing large circular golden yellow drop earrings hanging from earlobes':
        r'wearing golden circular earrings',

    r'wearing (\w+) circular (?:golden yellow )?(?:drop )?earrings(?: hanging from earlobes)?':
        r'wearing \1 circular earrings',

    # Bows: Simplify
    r'with (\w+) decorative bow attached to hair on (left|right) side of head near ear':
        r'with \1 bow in hair',

    # Eyes: Keep simple distinction
    r'dark brown eyes clearly distinct from lighter brown hair':
        r'dark brown eyes, lighter brown hair',

    # Remove redundant "hard color borders, sharp pixel edges" if already present
    r', hard color borders, sharp pixel edges, hard color borders, sharp pixel edges':
        r', hard color borders, sharp pixel edges',
}

# Ensure core pixel art description is present
PIXEL_ART_CORE = "hard color borders, sharp pixel edges"

def simplify_caption(caption_text):
    """Apply Phase 1B simplification rules"""

    simplified = caption_text.strip()

    # Apply all simplification rules
    for pattern, replacement in SIMPLIFICATION_RULES.items():
        simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)

    # Ensure pixel art core description is present (once)
    if PIXEL_ART_CORE not in simplified.lower():
        simplified = simplified.rstrip() + f', {PIXEL_ART_CORE}'

    return simplified

def process_all_captions():
    """Process all caption files with Phase 1B simplification"""

    print("="*70)
    print("PHASE 1B: SIMPLIFIED CAPTION ENHANCEMENT")
    print("="*70)
    print()
    print("Strategy: Minimal structural detail at 512px")
    print("  ✅ Keep: What exists (sunglasses, hat, earrings)")
    print("  ✅ Keep: Where it is (covering eyes, in hair)")
    print("  ✅ Keep: Basic shape (rectangular, circular)")
    print("  ❌ Remove: Micro-details (thin, thick, textures)")
    print()

    # Get all caption files
    caption_files = sorted(TRAINING_DATA_DIR.glob("*.txt"))

    if not caption_files:
        print(f"❌ No caption files found in {TRAINING_DATA_DIR}")
        return

    print(f"Found {len(caption_files)} caption files")
    print()

    # Track changes
    modified_count = 0
    changes_log = []

    for caption_path in caption_files:
        # Read original
        with open(caption_path, 'r') as f:
            original = f.read().strip()

        # Backup original
        backup_path = BACKUP_DIR / caption_path.name
        with open(backup_path, 'w') as f:
            f.write(original)

        # Apply simplification
        simplified = simplify_caption(original)

        # Only write if changed
        if simplified != original:
            with open(caption_path, 'w') as f:
                f.write(simplified)

            modified_count += 1

            # Log change
            changes_log.append({
                'file': caption_path.name,
                'before': original,
                'after': simplified
            })

            print(f"✓ {caption_path.name}")
            if len(original) > len(simplified):
                print(f"  Simplified: {len(original)} → {len(simplified)} chars ({len(original) - len(simplified)} chars removed)")

    print()
    print("="*70)
    print(f"PHASE 1B COMPLETE")
    print("="*70)
    print(f"Modified: {modified_count}/{len(caption_files)} files")
    print(f"Backup saved: {BACKUP_DIR}")
    print()

    # Save detailed log
    log_path = f"docs/PHASE1B_SIMPLIFIED_CAPTIONS_LOG.md"
    with open(log_path, 'w') as f:
        f.write(f"# Phase 1B: Simplified Caption Enhancement Log\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Strategy:** Minimal structural detail (512px resolution)\n")
        f.write(f"**Modified:** {modified_count}/{len(caption_files)} files\n\n")
        f.write(f"---\n\n")

        f.write(f"## Simplification Rules\n\n")
        f.write(f"**Core Principle:** Only describe features that exist at 24x24 pixels\n\n")
        f.write(f"| Feature | Phase 1A (Too Verbose) | Phase 1B (Simplified) |\n")
        f.write(f"|---------|----------------------|---------------------|\n")
        f.write(f"| Sunglasses | \"thin black plastic frames and thin temples behind ears\" | \"black rectangular sunglasses covering eyes\" |\n")
        f.write(f"| Hat | \"structured baseball cap with curved front brim covering top of head down to hairline\" | \"baseball cap\" |\n")
        f.write(f"| Earrings | \"large circular golden yellow drop earrings hanging from earlobes\" | \"golden circular earrings\" |\n")
        f.write(f"| Bow | \"decorative bow attached to hair on left side of head near ear\" | \"bow in hair\" |\n\n")

        f.write(f"---\n\n")
        f.write(f"## Changed Captions ({modified_count} files)\n\n")

        for change in changes_log:
            f.write(f"### {change['file']}\n\n")
            f.write(f"**Before (Phase 1A):**\n")
            f.write(f"```\n{change['before']}\n```\n\n")
            f.write(f"**After (Phase 1B):**\n")
            f.write(f"```\n{change['after']}\n```\n\n")
            f.write(f"---\n\n")

    print(f"✓ Detailed log saved: {log_path}")
    print()
    print("Ready for training:")
    print(f"  - Resolution: 512px (proven optimal)")
    print(f"  - Captions: Phase 1B simplified")
    print(f"  - Hex codes: Removed (from previous run)")
    print(f"  - Expected: Better than Phase 1A, comparable to CAPTION_FIX baseline")

if __name__ == "__main__":
    process_all_captions()
