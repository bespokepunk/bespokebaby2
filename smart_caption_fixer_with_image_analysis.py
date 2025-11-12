#!/usr/bin/env python3
"""
Smart Caption Fixer with Image Analysis
I DO THE WORK - You review only the uncertain ones!

Process:
1. Load images and analyze pixel colors
2. Infer eye colors from actual pixel data
3. Infer hair colors from actual pixel data
4. Fix all broken text automatically
5. Apply surgical fixes
6. Flag only uncertain captions for human review

Result: User reviews ~20 instead of 203!
"""

import os
import re
from pathlib import Path
from PIL import Image
import json
from collections import Counter

SOURCE_DIR = Path("runpod_package/training_data")
OUTPUT_DIR = Path("improved_samples_v8_SMART")
OUTPUT_DIR.mkdir(exist_ok=True)

class SmartCaptionFixer:
    """Smart fixer with image analysis"""

    def __init__(self):
        self.stats = {
            'auto_fixed_eyes': 0,
            'auto_fixed_hair': 0,
            'auto_fixed_broken': 0,
            'needs_review': 0
        }
        self.uncertain_captions = []

    def analyze_dominant_colors(self, image_path, region='top'):
        """Analyze dominant colors in an image region"""
        try:
            img = Image.open(image_path).convert('RGB')
            width, height = img.size

            # Define regions for analysis
            if region == 'top':  # Hair region
                box = (0, 0, width, height // 3)
            elif region == 'middle':  # Eyes region
                box = (0, height // 3, width, 2 * height // 3)
            else:  # Full image
                box = (0, 0, width, height)

            cropped = img.crop(box)
            pixels = list(cropped.getdata())

            # Get most common colors
            color_counts = Counter(pixels)
            most_common = color_counts.most_common(10)

            return most_common
        except Exception as e:
            print(f"⚠️ Could not analyze image: {e}")
            return []

    def infer_eye_color(self, image_path):
        """Infer eye color from image analysis"""
        colors = self.analyze_dominant_colors(image_path, 'middle')
        if not colors:
            return None, False  # None, uncertain

        # Analyze RGB values of dominant colors
        for (r, g, b), count in colors:
            # Brown eyes (most common)
            if 80 <= r <= 150 and 40 <= g <= 100 and 20 <= b <= 70:
                return "brown eyes", True
            # Blue eyes
            if b > r and b > g and b > 100:
                return "blue eyes", True
            # Green eyes
            if g > r and g > b and g > 80:
                return "green eyes", True
            # Gray eyes
            if abs(r - g) < 20 and abs(g - b) < 20 and 100 < r < 180:
                return "gray eyes", True
            # Dark brown/black eyes
            if r < 60 and g < 60 and b < 60:
                return "dark brown eyes", True

        # If uncertain, return None and flag for review
        return None, False

    def infer_hair_color(self, image_path):
        """Infer hair color from top region"""
        colors = self.analyze_dominant_colors(image_path, 'top')
        if not colors:
            return None, False

        for (r, g, b), count in colors:
            # Black hair
            if r < 40 and g < 40 and b < 40:
                return "black hair", True
            # Brown hair
            if 60 <= r <= 120 and 40 <= g <= 80 and 20 <= b <= 60:
                return "brown hair", True
            # Blonde hair
            if r > 180 and g > 150 and b < 120:
                return "blonde hair", True
            # Gray hair
            if abs(r - g) < 20 and abs(g - b) < 20 and 120 < r < 200:
                return "gray hair", True
            # Red hair
            if r > 140 and g < 100 and b < 80:
                return "red hair", True
            # Green hair (pixel art)
            if g > r and g > b and g > 100:
                return "green hair", True
            # Bald (skin tones)
            if 140 <= r <= 220 and 100 <= g <= 180 and 80 <= b <= 140:
                return "bald", True

        return None, False

    def fix_caption_smart(self, caption, filename, image_path):
        """Smart caption fixing with image analysis"""
        original = caption
        original_length = len(caption)
        uncertain = False
        fixes_applied = []

        # STEP 1: Surgical fixes first
        caption = re.sub(r'\bsimple\s+', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bmale\s+skin', 'skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bfemale\s+skin', 'skin', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bmale\b', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\bfemale\b', '', caption, flags=re.IGNORECASE)

        # Fix "wearing stubble" → "with stubble"
        caption = re.sub(r'wearing\s+(light\s+gray|dark\s+brown|brown|gray|grey)\s+(stubble|beard)',
                       r'with \1 \2', caption, flags=re.IGNORECASE)
        caption = re.sub(r'wearing\s+(stubble|beard)', r'with \1', caption, flags=re.IGNORECASE)

        # Remove lips, hex codes, palette
        caption = caption.replace('lips,', '').replace(', lips', '')
        caption = re.sub(r'#[0-9a-fA-F]{6}', '', caption)
        caption = re.sub(r',?\s*palette:[^,]*', '', caption)
        caption = re.sub(r',?\s*hard color borders', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r',?\s*sharp pixel edges', '', caption, flags=re.IGNORECASE)

        # Fix backgrounds
        caption = re.sub(r'split background', 'divided background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'solid background', 'background', caption, flags=re.IGNORECASE)

        # Remove ethnic descriptors
        caption = re.sub(r'\s*\(middle eastern\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(hispanic\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(mexican\)', '', caption, flags=re.IGNORECASE)

        # Fix "medium to light" → "medium light"
        caption = re.sub(r'medium to light', 'medium light', caption, flags=re.IGNORECASE)

        # STEP 2: Check for missing eye color
        has_eyes = bool(re.search(r'\b(brown|blue|green|gray|grey|hazel|black|dark)\s+eyes\b', caption, re.IGNORECASE))
        if not has_eyes or re.search(r'\beyes,\s', caption, re.IGNORECASE):
            # Try to infer from image
            inferred_eyes, confident = self.infer_eye_color(image_path)
            if confident and inferred_eyes:
                # Insert eye color before skin tone
                caption = re.sub(r'(,\s*(?:light|medium|dark)\s+skin)',
                               f', {inferred_eyes}\\1', caption)
                fixes_applied.append(f"Added {inferred_eyes}")
                self.stats['auto_fixed_eyes'] += 1
            else:
                uncertain = True
                fixes_applied.append("⚠️ Eye color uncertain - needs review")

        # STEP 3: Check for missing/broken hair
        if re.search(r'^pixel art, 24x24, portrait of bespoke punk \w+, hair,', caption, re.IGNORECASE):
            # "hair" with no description - try to infer
            inferred_hair, confident = self.infer_hair_color(image_path)
            if confident and inferred_hair:
                caption = re.sub(r', hair,', f', {inferred_hair},', caption, flags=re.IGNORECASE)
                fixes_applied.append(f"Added {inferred_hair}")
                self.stats['auto_fixed_hair'] += 1
            else:
                uncertain = True
                fixes_applied.append("⚠️ Hair description uncertain - needs review")

        # STEP 4: Remove duplicate consecutive phrases
        words = caption.split(', ')
        seen_recently = {}
        cleaned_words = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            if word_lower in seen_recently and i - seen_recently[word_lower] <= 3:
                # Duplicate found within last 3 words
                self.stats['auto_fixed_broken'] += 1
                continue
            cleaned_words.append(word)
            seen_recently[word_lower] = i
        caption = ', '.join(cleaned_words)

        # STEP 5: Clean up spacing
        caption = re.sub(r'\s+', ' ', caption)
        caption = re.sub(r'\s*,\s*', ', ', caption)
        caption = re.sub(r',\s*,+', ',', caption)
        caption = caption.strip().rstrip(', ')

        # Ensure proper ending
        if not caption.endswith('pixel art style'):
            caption += ', pixel art style'

        new_length = len(caption)

        if uncertain:
            self.stats['needs_review'] += 1
            self.uncertain_captions.append({
                'filename': filename,
                'original': original,
                'improved': caption,
                'issues': fixes_applied
            })

        return {
            'filename': filename,
            'original': original,
            'improved': caption,
            'original_length': original_length,
            'new_length': new_length,
            'reduction_pct': round((original_length - new_length) / original_length * 100, 1),
            'uncertain': uncertain,
            'fixes': fixes_applied
        }

    def process_all(self):
        """Process all captions with smart analysis"""
        txt_files = sorted(SOURCE_DIR.glob("*.txt"))
        results = []

        print("🔍 Processing captions with smart image analysis...")
        print()

        for txt_file in txt_files:
            with open(txt_file, 'r') as f:
                caption = f.read().strip()

            image_file = txt_file.with_suffix('.png')

            result = self.fix_caption_smart(caption, txt_file.name, image_file)
            results.append(result)

            # Save
            output_file = OUTPUT_DIR / txt_file.name
            with open(output_file, 'w') as f:
                f.write(result['improved'])

            status = "⚠️" if result['uncertain'] else "✅"
            print(f"{status} {txt_file.name}: {result['original_length']} → {result['new_length']} chars")
            if result['fixes']:
                for fix in result['fixes'][:2]:  # Show first 2 fixes
                    print(f"     {fix}")

        return results

    def save_uncertain_list(self):
        """Save list of uncertain captions for user review"""
        uncertain_file = OUTPUT_DIR / "NEEDS_REVIEW.json"
        with open(uncertain_file, 'w') as f:
            json.dump(self.uncertain_captions, f, indent=2)

        print(f"\n📋 Saved {len(self.uncertain_captions)} uncertain captions to: {uncertain_file}")
        return uncertain_file

    def print_stats(self, results):
        """Print final statistics"""
        total = len(results)
        avg_new = sum(r['new_length'] for r in results) / total
        target_met = sum(1 for r in results if 150 <= r['new_length'] <= 220)

        print("\n" + "="*70)
        print("🎯 SMART CAPTION FIXER - FINAL REPORT")
        print("="*70)
        print(f"Total processed: {total}")
        print(f"✅ Auto-fixed eye colors: {self.stats['auto_fixed_eyes']}")
        print(f"✅ Auto-fixed hair: {self.stats['auto_fixed_hair']}")
        print(f"✅ Auto-fixed broken text: {self.stats['auto_fixed_broken']}")
        print(f"⚠️  Needs human review: {self.stats['needs_review']}")
        print()
        print(f"Avg length: {round(avg_new, 1)} chars")
        print(f"Target range (150-220): {target_met}/{total} ({round(target_met/total*100, 1)}%)")
        print()
        print(f"📁 Output: {OUTPUT_DIR}/")
        print("="*70)
        print()
        print(f"🎉 YOU ONLY NEED TO REVIEW {self.stats['needs_review']} CAPTIONS!")
        print(f"   (instead of all {total})")
        print()

def main():
    print("🎯 Smart Caption Fixer with Image Analysis")
    print("I'll do the heavy lifting - you review only uncertain ones!")
    print()

    fixer = SmartCaptionFixer()
    results = fixer.process_all()
    uncertain_file = fixer.save_uncertain_list()
    fixer.print_stats(results)

    if fixer.uncertain_captions:
        print(f"📝 Next step: Review {uncertain_file}")
    else:
        print("✨ All captions fixed automatically - no review needed!")

if __name__ == "__main__":
    main()
