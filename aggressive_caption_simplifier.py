#!/usr/bin/env python3
"""
Aggressive Caption Simplifier
Targets 150-180 characters following SD15_PERFECT's proven 9/10 quality pattern
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

TRAINING_DIR = Path("runpod_package/training_data")
OUTPUT_DIR = Path("improved_samples")
OUTPUT_DIR.mkdir(exist_ok=True)

class AggressiveCaptionSimplifier:
    """Simplifies captions to match successful OLD format (150-180 chars)"""

    def __init__(self):
        self.changes_log = []

    def simplify_caption(self, caption, filename):
        """Apply aggressive simplification rules"""
        original = caption
        original_length = len(caption)
        changes = []

        # RULE 1: Remove all hex codes (any #XXXXXX pattern)
        hex_pattern = r'#[0-9a-fA-F]{6}'
        hex_matches = re.findall(hex_pattern, caption)
        if hex_matches:
            caption = re.sub(hex_pattern, '', caption)
            changes.append(f"Removed {len(hex_matches)} hex codes: {', '.join(hex_matches[:3])}...")

        # RULE 2: Remove parenthetical hex codes like "(#XXXXXX)"
        paren_hex_pattern = r'\s*\(#[0-9a-fA-F]{6}\)'
        paren_matches = re.findall(paren_hex_pattern, caption)
        if paren_matches:
            caption = re.sub(paren_hex_pattern, '', caption)
            changes.append(f"Removed {len(paren_matches)} parenthetical hex codes")

        # RULE 3: Remove "palette:" sections
        if 'palette:' in caption:
            caption = re.sub(r',?\s*palette:[^,]*', '', caption)
            changes.append("Removed palette section")

        # RULE 4: Remove "lips" token
        if 'lips,' in caption or ', lips' in caption:
            caption = caption.replace('lips,', '').replace(', lips', '')
            changes.append("Removed 'lips' token (model adds automatically)")

        # RULE 5: Remove "male/female" from skin tone
        caption = re.sub(r'\bmale skin tone\b', 'skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bfemale skin tone\b', 'skin', caption, flags=re.IGNORECASE)
        if 'male skin' in original.lower() or 'female skin' in original.lower():
            changes.append("Removed 'male/female' from skin tone (redundant)")

        # RULE 6: Simplify overly detailed hair descriptions
        hair_simplifications = {
            r'bright lime green yellow green hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style': 'green hair in ponytail',
            r'hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style': 'hair in ponytail',
            r'long textured curly multicolored brown hair': 'curly brown hair',
            r'voluminous voluptuous fluffy afrostyle huge curly': 'voluminous curly',
            r'longer on top and messy and flicking / curled out on top right': 'messy hair',
            r'thin bright lime green yellow green hair with balding receding top and very little hair in natural 18th century style no wig': 'thin green hair, balding',
            r'bright lime green yellow green wig curled and tied in queue in classic 18th century colonial style': 'green wig in colonial style',
        }

        for complex_desc, simple_desc in hair_simplifications.items():
            if re.search(complex_desc, caption, re.IGNORECASE):
                caption = re.sub(complex_desc, simple_desc, caption, flags=re.IGNORECASE)
                changes.append(f"Simplified hair description")
                break

        # RULE 7: ULTRA-AGGRESSIVE accessory/clothing simplification
        # Remove ALL detailed clothing descriptions
        clothing_patterns = [
            (r'wearing classic vintage revolutionary war era [^,]+suit[^,]*', 'gray suit'),
            (r'wearing a large oversized camouflaged coloured hoodie', 'camo hoodie'),
            (r'wearing [^,]*collared shirt[^,]*', 'shirt'),
            (r'wearing [^,]*hoodie[^,]*', 'hoodie'),
            (r'wearing [^,]*jacket[^,]*', 'jacket'),
            (r'wearing [^,]*suit[^,]*', 'suit'),
            (r', medium grey shirt', ', gray shirt'),
            (r', dark grey shirt', ', gray shirt'),
        ]

        for pattern, replacement in clothing_patterns:
            if re.search(pattern, caption, re.IGNORECASE):
                caption = re.sub(pattern, replacement, caption, flags=re.IGNORECASE)
                changes.append(f"Ultra-simplified clothing description")

        # Simplify accessories
        accessory_simplifications = {
            r'wearing gray baseball cap with multicolored [^,]+': 'gray cap',
            r'gray baseball cap with multicolored [^,]+': 'gray cap',
            r'wearing black rectangular sunglasses[^,]*': 'black sunglasses',
            r'black rectangular sunglasses[^,]*': 'black sunglasses',
            r'wearing dual colored purple party glasses[^,]*': 'purple party glasses',
            r'wearing white furry bucket hat': 'white hat',
        }

        for complex_desc, simple_desc in accessory_simplifications.items():
            if re.search(complex_desc, caption, re.IGNORECASE):
                caption = re.sub(complex_desc, simple_desc, caption, flags=re.IGNORECASE)
                changes.append(f"Simplified accessory description")

        # RULE 8: Simplify skin tone descriptions
        skin_simplifications = {
            r'medium male skin tone color': 'medium skin',
            r'light pale green skin tone': 'light green skin',
            r'light light opal orange': 'light orange',
            r'medium dark blue eyes': 'dark blue eyes',
            r'light medium brownred eyes': 'light brown eyes',
        }

        for complex_desc, simple_desc in skin_simplifications.items():
            if re.search(complex_desc, caption, re.IGNORECASE):
                caption = re.sub(complex_desc, simple_desc, caption, flags=re.IGNORECASE)
                changes.append(f"Simplified color description")

        # RULE 9: Remove vague/useless descriptors
        # Remove standalone "hair," without description
        if re.search(r',\s*hair,', caption):
            caption = re.sub(r',\s*hair,', ',', caption)
            changes.append("Removed standalone 'hair' (no descriptor)")

        # Simplify background descriptions
        caption = re.sub(r'checkered brick background', 'brick background', caption)
        caption = re.sub(r'split background', 'gradient background', caption)
        caption = re.sub(r'solid background', 'background', caption)
        caption = re.sub(r'light light ', 'light ', caption)  # Double light

        # RULE 10: Fix spacing issues
        caption = re.sub(r'\s+', ' ', caption)  # Multiple spaces to single
        caption = re.sub(r'\s*,\s*', ', ', caption)  # Normalize commas
        caption = re.sub(r',\s*,', ',', caption)  # Remove double commas
        caption = caption.strip()

        # RULE 11: Remove redundant style markers and ensure clean ending
        # Remove ALL style redundancy
        caption = re.sub(r',?\s*hard color borders', '', caption)
        caption = re.sub(r',?\s*sharp pixel edges', '', caption)
        caption = re.sub(r',?\s*retro pixel art style', '', caption)

        # Clean up and add single style marker at end
        caption = caption.rstrip(', ') + ', pixel art style'
        changes.append("Removed redundant style markers, using only 'pixel art style'")

        # Calculate metrics
        new_length = len(caption)
        reduction = original_length - new_length
        reduction_pct = (reduction / original_length * 100) if original_length > 0 else 0

        return {
            'filename': filename,
            'original': original,
            'improved': caption,
            'original_length': original_length,
            'new_length': new_length,
            'reduction': reduction,
            'reduction_pct': round(reduction_pct, 1),
            'changes': changes,
            'target_met': 150 <= new_length <= 180
        }

    def process_samples(self, num_samples=None):
        """Process N caption files (None = all files)"""
        txt_files = sorted(TRAINING_DIR.glob("*.txt"))
        if num_samples:
            txt_files = txt_files[:num_samples]

        results = []
        for txt_file in txt_files:
            with open(txt_file, 'r') as f:
                caption = f.read().strip()

            result = self.simplify_caption(caption, txt_file.name)
            results.append(result)

            # Save improved caption
            output_file = OUTPUT_DIR / txt_file.name
            with open(output_file, 'w') as f:
                f.write(result['improved'])

            print(f"✅ {txt_file.name}")
            print(f"   {result['original_length']} → {result['new_length']} chars ({result['reduction_pct']}% reduction)")
            if result['changes']:
                print(f"   Changes: {len(result['changes'])}")

        return results

    def generate_report(self, results):
        """Generate summary report"""
        total = len(results)
        avg_original = sum(r['original_length'] for r in results) / total
        avg_new = sum(r['new_length'] for r in results) / total
        avg_reduction = sum(r['reduction_pct'] for r in results) / total
        target_met = sum(1 for r in results if r['target_met'])

        report = {
            'summary': {
                'total_samples': total,
                'avg_original_length': round(avg_original, 1),
                'avg_new_length': round(avg_new, 1),
                'avg_reduction_pct': round(avg_reduction, 1),
                'target_met_count': target_met,
                'target_met_pct': round(target_met / total * 100, 1)
            },
            'samples': results
        }

        # Save report
        report_file = OUTPUT_DIR / 'simplification_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print("\n" + "="*70)
        print("📊 SIMPLIFICATION REPORT")
        print("="*70)
        print(f"Samples processed: {total}")
        print(f"Avg length: {round(avg_original, 1)} → {round(avg_new, 1)} chars")
        print(f"Avg reduction: {round(avg_reduction, 1)}%")
        print(f"Target range (150-180): {target_met}/{total} ({round(target_met / total * 100, 1)}%)")
        print(f"\n📁 Output: {OUTPUT_DIR}/")
        print(f"📄 Report: {report_file}")
        print("="*70)

        return report

def main():
    print("🎯 Aggressive Caption Simplifier")
    print("Target: 150-180 characters (SD15_PERFECT proven format)")
    print()

    simplifier = AggressiveCaptionSimplifier()

    # Process ALL 203 samples
    print("Processing ALL 203 caption files...\n")
    results = simplifier.process_samples(num_samples=None)  # None = all files

    # Generate report
    report = simplifier.generate_report(results)

    print("\n✨ Done! All improved captions saved to improved_samples/ directory")
    print("📋 Next: Use sample_review_ui.py to review all 203 side-by-side")

if __name__ == "__main__":
    main()
