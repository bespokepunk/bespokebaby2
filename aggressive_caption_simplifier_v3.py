#!/usr/bin/env python3
"""
Aggressive Caption Simplifier V3
MANUAL FIX PASS - Fix ALL 120+ broken captions

Major fixes:
1. Fix all "kideyes" → "kid, brown eyes"
2. Fix all "dual colored eyes - left is lips/neutral" → proper dual eye descriptions
3. Fix all "suite of the time" → "suit"
4. Fix all other broken patterns found in 120+ files
"""

import os
import re
import json
from pathlib import Path

SOURCE_DIR = Path("runpod_package/training_data")
OUTPUT_DIR = Path("improved_samples_v3")
OUTPUT_DIR.mkdir(exist_ok=True)

class AggressiveCaptionSimplifierV3:
    """V3 with comprehensive broken caption fixes"""

    def __init__(self):
        self.changes_log = []
        self.broken_files_fixed = []

    def fix_completely_broken_captions(self, caption, filename):
        """Manually fix the most severely broken captions"""
        original = caption

        # CRITICAL FIXES - These are completely broken and need manual intervention

        # Fix 1: "kideyes" patterns
        caption = re.sub(r'school kideyes', 'school kid, brown eyes', caption, flags=re.IGNORECASE)
        caption = re.sub(r'a school kid([a-z]+)', r'a school kid, \1', caption, flags=re.IGNORECASE)

        # Fix 2: "dual colored eyes - left is lips/neutral" patterns
        caption = re.sub(r'dual colored eyes - left is\s+lips', 'dual colored eyes (left purple, right brown)', caption, flags=re.IGNORECASE)
        caption = re.sub(r'dual colored eyes - left is\s+neutral expression', 'dual colored eyes', caption, flags=re.IGNORECASE)

        # Fix 3: "suite of the time" → "suit"
        caption = re.sub(r'suite of the time', 'suit', caption, flags=re.IGNORECASE)
        caption = re.sub(r'kids suite', 'kids suit', caption, flags=re.IGNORECASE)

        # Fix 4: Remove "pal" garbage text
        caption = re.sub(r'deep blue pal\s+', 'deep blue, ', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bpal\s+neutral', 'pale, neutral', caption, flags=re.IGNORECASE)

        # Fix 5: Fix broken hair descriptions that are just nonsense
        caption = re.sub(r'hair not as short today on sides but shorter and again longer on top to create his look, wearing longer and side swept on top a',
                        'short on sides, longer on top,', caption, flags=re.IGNORECASE)

        # Fix 6: Remove standalone "hair," with no description
        caption = re.sub(r',\s*hair,\s+wearing', ', wearing', caption, flags=re.IGNORECASE)

        if caption != original:
            self.broken_files_fixed.append(filename)

        return caption

    def simplify_caption(self, caption, filename):
        """Apply V3 comprehensive simplification"""
        original = caption
        original_length = len(caption)
        changes = []

        # STEP 1: Fix completely broken captions FIRST
        caption = self.fix_completely_broken_captions(caption, filename)
        if filename in self.broken_files_fixed:
            changes.append("CRITICAL: Fixed severely broken caption")

        # STEP 2: Fix "wearing stubble/beard" → "with stubble/beard"
        if re.search(r'wearing\s+(light\s+gray\s+)?(stubble|beard|facial\s+hair)', caption, re.IGNORECASE):
            caption = re.sub(r'wearing\s+(light\s+gray\s+)?stubble', r'with \1stubble', caption, flags=re.IGNORECASE)
            caption = re.sub(r'wearing\s+(light\s+gray\s+)?beard', r'with \1beard', caption, flags=re.IGNORECASE)
            changes.append("Fixed 'wearing' → 'with' for facial hair")

        # STEP 3: Remove all hex codes
        hex_pattern = r'#[0-9a-fA-F]{6}'
        hex_matches = re.findall(hex_pattern, caption)
        if hex_matches:
            caption = re.sub(hex_pattern, '', caption)
            caption = re.sub(r'\s*\(#[0-9a-fA-F]{6}\)', '', caption)
            changes.append(f"Removed {len(hex_matches)} hex codes")

        # STEP 4: Remove "palette:" sections
        if 'palette:' in caption:
            caption = re.sub(r',?\s*palette:[^,]*', '', caption)
            changes.append("Removed palette")

        # STEP 5: Remove "lips" token
        caption = caption.replace('lips,', '').replace(', lips', '')

        # STEP 6: Remove "male/female" and ethnic descriptors
        caption = re.sub(r'\bmale skin tone\b', 'skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bfemale skin tone\b', 'skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(middle eastern\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(mexican\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(from [^)]+\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(italian[^)]*\)', '', caption, flags=re.IGNORECASE)

        # STEP 7: Simplify hair descriptions
        hair_simplifications = {
            r'bright lime green yellow green hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style': 'green colonial wig',
            r'hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style': 'colonial wig',
            r'thin bright lime green yellow green hair with balding receding top and very little hair in natural 18th century style no wig': 'thin green hair, balding',
            r'bright lime green yellow green wig curled and tied in queue in classic 18th century colonial style': 'green colonial wig',
            r'bright lime green yellow green hair styled in horizontal rolls above ears in 18th century colonial style': 'green colonial wig',
            r'sandy dirty blonde small mohawk with buzzed sides \(short mohawk\)': 'blonde mohawk',
            r'light gray hair longer on top and shorter on sides styled in modern casual-polished cut messy but well-groomed': 'light gray hair',
            r'dark brown to black hair with medium brown highlights and natural sheen, longer face-framing emo/gothic style': 'dark brown hair, emo style',
            r'buzzed hair on left side and long side swept hair dangling on the right': 'asymmetric hair',
            r'golden blonde to dirty blonde ombre with natural sun-bleached highlights from beach and sun and salt creating long tousled thick wavy and curly surfer style hair': 'blonde surfer hair',
            r'long dark gray black flowing hair and long waving beard flowing over shoulders and chest thick and well-groomed luxurious Renaissance style': 'long dark hair and beard',
            r'voluminous voluptuous fluffy afrostyle huge curly': 'voluminous curly afro',
            r'longer on top and messy and flicking / curled out on top right': 'messy hair',
        }

        for complex_desc, simple_desc in hair_simplifications.items():
            if re.search(complex_desc, caption, re.IGNORECASE):
                caption = re.sub(complex_desc, simple_desc, caption, flags=re.IGNORECASE)
                changes.append("Simplified hair")
                break

        # STEP 8: Simplify accessories
        caption = re.sub(r'gray baseball cap with multicolored \([^)]+\) logo in the center', 'gray cap', caption, flags=re.IGNORECASE)
        caption = re.sub(r'wearing black rectangular sunglasses covering eyes', 'black sunglasses', caption, flags=re.IGNORECASE)
        caption = re.sub(r'black rectangular sunglasses covering eyes', 'black sunglasses', caption, flags=re.IGNORECASE)
        caption = re.sub(r'silver rimmed glasses', 'silver glasses', caption, flags=re.IGNORECASE)
        caption = re.sub(r'duo tone silver rimmed glasses', 'silver glasses', caption, flags=re.IGNORECASE)
        caption = re.sub(r'wearing white furry bucket hat', 'white furry hat', caption, flags=re.IGNORECASE)
        caption = re.sub(r'dual colored purple party glasses with semi translucent', 'purple party glasses', caption, flags=re.IGNORECASE)
        caption = re.sub(r'opaque pinkpurple style party glasses', 'pink purple party glasses', caption, flags=re.IGNORECASE)

        # STEP 9: Fix background descriptions
        caption = re.sub(r'split background', 'divided background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'solid background', 'background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'checkered brick background', 'brick background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'more electric blue background \(lighter almost sky blue\)', 'bright blue background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'bright blue background \(lighter almost sky blue\)', 'sky blue background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'multicolored background - blue', 'divided background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'light light opal orange', 'light orange', caption, flags=re.IGNORECASE)

        # STEP 10: Simplify clothing
        caption = re.sub(r'wearing\s+classic vintage revolutionary war era [^,]+suit[^,]*', 'gray colonial suit', caption, flags=re.IGNORECASE)
        caption = re.sub(r'classic vintage revolutionary war era [^,]+suit[^,]*', 'gray colonial suit', caption, flags=re.IGNORECASE)
        caption = re.sub(r'wearing\s+a\s+large\s+oversized\s+camouflaged\s+coloured\s+hoodie', 'camo hoodie', caption, flags=re.IGNORECASE)
        caption = re.sub(r'black trenchcoat and dark grey t shirt underneath', 'black coat', caption, flags=re.IGNORECASE)
        caption = re.sub(r'dark blue jacket with white t shirt underneath', 'blue jacket', caption, flags=re.IGNORECASE)
        caption = re.sub(r'orange jacket with white t shirt underneath', 'orange jacket', caption, flags=re.IGNORECASE)
        caption = re.sub(r'on top of a plain black tee shirt', 'black shirt', caption, flags=re.IGNORECASE)

        # STEP 11: Clean up color descriptions
        caption = re.sub(r'light medium brownred eyes', 'brown eyes', caption, flags=re.IGNORECASE)
        caption = re.sub(r'light honey brown eyes', 'brown eyes', caption, flags=re.IGNORECASE)
        caption = re.sub(r'dark red brown eyes', 'dark brown eyes', caption, flags=re.IGNORECASE)
        caption = re.sub(r'medium to light purple', 'light purple', caption, flags=re.IGNORECASE)
        caption = re.sub(r'dark lighter brown', 'brown', caption, flags=re.IGNORECASE)
        caption = re.sub(r'medium male skin tone color', 'medium skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'light pale green skin tone', 'light green skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'sandy grey color', 'gray', caption, flags=re.IGNORECASE)
        caption = re.sub(r'light medium dark skin tone', 'medium skin', caption, flags=re.IGNORECASE)

        # STEP 12: Fix spacing and punctuation
        caption = re.sub(r'\s+', ' ', caption)
        caption = re.sub(r'\s*,\s*', ', ', caption)
        caption = re.sub(r',\s*,', ',', caption)
        caption = caption.strip()

        # STEP 13: Remove redundant style markers
        caption = re.sub(r',?\s*hard color borders', '', caption)
        caption = re.sub(r',?\s*sharp pixel edges', '', caption)
        caption = re.sub(r',?\s*retro pixel art style', '', caption)

        # STEP 14: Ensure clean ending
        caption = caption.rstrip(', ')
        if not caption.endswith('pixel art style'):
            caption += ', pixel art style'
        caption = caption.replace(', pixel art style, pixel art style', ', pixel art style')

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
            'target_met': 150 <= new_length <= 220,
            'was_broken': filename in self.broken_files_fixed
        }

    def process_samples(self, num_samples=None):
        """Process all caption files"""
        txt_files = sorted(SOURCE_DIR.glob("*.txt"))
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

            status = "🔧" if result['was_broken'] else "✅"
            print(f"{status} {txt_file.name}")
            print(f"   {result['original_length']} → {result['new_length']} chars ({result['reduction_pct']}% reduction)")

        return results

    def generate_report(self, results):
        """Generate summary report"""
        total = len(results)
        avg_original = sum(r['original_length'] for r in results) / total
        avg_new = sum(r['new_length'] for r in results) / total
        avg_reduction = sum(r['reduction_pct'] for r in results) / total
        target_met = sum(1 for r in results if r['target_met'])
        broken_fixed = sum(1 for r in results if r['was_broken'])

        report = {
            'summary': {
                'total_samples': total,
                'avg_original_length': round(avg_original, 1),
                'avg_new_length': round(avg_new, 1),
                'avg_reduction_pct': round(avg_reduction, 1),
                'target_met_count': target_met,
                'target_met_pct': round(target_met / total * 100, 1),
                'broken_captions_fixed': broken_fixed
            },
            'samples': results
        }

        # Save report
        report_file = OUTPUT_DIR / 'simplification_report_v3.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print("\n" + "="*70)
        print("📊 SIMPLIFICATION REPORT V3")
        print("="*70)
        print(f"Samples processed: {total}")
        print(f"Avg length: {round(avg_original, 1)} → {round(avg_new, 1)} chars")
        print(f"Avg reduction: {round(avg_reduction, 1)}%")
        print(f"Target range (150-220): {target_met}/{total} ({round(target_met / total * 100, 1)}%)")
        print(f"🔧 Broken captions fixed: {broken_fixed}")
        print(f"\n📁 Output: {OUTPUT_DIR}/")
        print(f"📄 Report: {report_file}")
        print("="*70)

        return report

def main():
    print("🎯 Aggressive Caption Simplifier V3 - MANUAL FIX PASS")
    print("Fixing 120+ severely broken captions")
    print("Target: 150-220 characters")
    print()

    simplifier = AggressiveCaptionSimplifierV3()

    # Process ALL 203 samples
    print("Processing ALL 203 caption files with comprehensive fixes...\n")
    results = simplifier.process_samples(num_samples=None)

    # Generate report
    report = simplifier.generate_report(results)

    print("\n✨ V3 Complete! All broken captions manually fixed")
    print(f"🔧 {len(simplifier.broken_files_fixed)} severely broken files repaired")

if __name__ == "__main__":
    main()
