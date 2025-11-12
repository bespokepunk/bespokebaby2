#!/usr/bin/env python3
"""
V7 FINAL - World Class Captions
Balanced approach: Fix specific issues WITHOUT over-simplifying

Based on user feedback:
1. ADD facial hair color consistently  
2. REMOVE: "simple", "male/female", "wearing" for facial hair, "lips"
3. KEEP detail level ~180 chars like SD15_PERFECT
4. NO duplicates, NO broken text
5. Consistent structure

Target: 150-220 characters with ALL key information
"""

import os
import re
from pathlib import Path
import json

SOURCE_DIR = Path("runpod_package/training_data")
OUTPUT_DIR = Path("improved_samples_v7_FINAL")
OUTPUT_DIR.mkdir(exist_ok=True)

class FinalCaptionSimplifier:
    """V7 FINAL: Surgical fixes with precision"""
    
    def __init__(self):
        self.stats = {
            'processed': 0,
            'removed_simple': 0,
            'removed_male_female': 0,
            'fixed_facial_hair': 0,
            'removed_duplicates': 0
        }
    
    def simplify_caption(self, caption, filename):
        """Apply surgical fixes while preserving detail"""
        original = caption
        original_length = len(caption)
        
        # STEP 1: Remove "simple"
        if 'simple' in caption.lower():
            caption = re.sub(r'\bsimple\s+', '', caption, flags=re.IGNORECASE)
            self.stats['removed_simple'] += 1
        
        # STEP 2: Remove "male", "female"
        if 'male' in caption.lower() or 'female' in caption.lower():
            caption = re.sub(r'\bmale\s+skin', 'skin', caption, flags=re.IGNORECASE)
            caption = re.sub(r'\bfemale\s+skin', 'skin', caption, flags=re.IGNORECASE)
            caption = re.sub(r'\bmale\b', '', caption, flags=re.IGNORECASE)
            caption = re.sub(r'\bfemale\b', '', caption, flags=re.IGNORECASE)
            self.stats['removed_male_female'] += 1
        
        # STEP 3: Fix "wearing stubble/beard" → "with [color] stubble/beard"
        if re.search(r'wearing\s+(stubble|beard)', caption, re.IGNORECASE):
            # Try to find color
            caption = re.sub(r'wearing\s+(light\s+gray|dark\s+brown|brown|gray|grey)\s+(stubble|beard)', 
                           r'with \1 \2', caption, flags=re.IGNORECASE)
            caption = re.sub(r'wearing\s+(stubble|beard)', r'with \1', caption, flags=re.IGNORECASE)
            self.stats['fixed_facial_hair'] += 1
        
        # STEP 4: Remove "lips"
        caption = caption.replace('lips,', '').replace(', lips', '')
        
        # STEP 5: Remove hex codes
        caption = re.sub(r'#[0-9a-fA-F]{6}', '', caption)
        caption = re.sub(r'\s*\(#[0-9a-fA-F]{6}\)', '', caption)
        
        # STEP 6: Remove "palette:"
        caption = re.sub(r',?\s*palette:[^,]*', '', caption)
        
        # STEP 7: Remove redundant style markers
        caption = re.sub(r',?\s*hard color borders', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r',?\s*sharp pixel edges', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r',?\s*retro pixel art style', '', caption, flags=re.IGNORECASE)
        
        # STEP 8: Fix "split background" → "divided background"
        caption = re.sub(r'split background', 'divided background', caption, flags=re.IGNORECASE)
        caption = re.sub(r'solid background', 'background', caption, flags=re.IGNORECASE)
        
        # STEP 9: Remove ethnic/geographic descriptors in parentheses
        caption = re.sub(r'\s*\(middle eastern\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(hispanic\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(mexican\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(italian[^)]*\)', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'\s*\(from [^)]+\)', '', caption, flags=re.IGNORECASE)
        
        # STEP 10: Fix "medium to light" → "medium light"
        caption = re.sub(r'medium to light', 'medium light', caption, flags=re.IGNORECASE)
        
        # STEP 11: Simplify common verbose patterns
        caption = re.sub(r'on top of a plain', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'wearing a\s+', '', caption, flags=re.IGNORECASE)
        caption = re.sub(r'with a\s+', 'with ', caption, flags=re.IGNORECASE)
        
        # STEP 12: Clean up spacing and punctuation
        caption = re.sub(r'\s+', ' ', caption)
        caption = re.sub(r'\s*,\s*', ', ', caption)
        caption = re.sub(r',\s*,+', ',', caption)
        caption = caption.strip()
        
        # STEP 13: Remove duplicate consecutive phrases
        words = caption.split(', ')
        seen_recently = set()
        cleaned_words = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            # Only check last 3 words to avoid removing legitimate duplicates far apart
            if word_lower not in seen_recently:
                cleaned_words.append(word)
                seen_recently.add(word_lower)
                # Keep sliding window of last 3
                if len(seen_recently) > 3:
                    # Remove oldest
                    if i >= 3:
                        seen_recently.discard(words[i-3].lower())
            else:
                self.stats['removed_duplicates'] += 1
        caption = ', '.join(cleaned_words)
        
        # STEP 14: Ensure proper ending
        caption = caption.rstrip(', ')
        if not caption.endswith('pixel art style'):
            caption += ', pixel art style'
        caption = caption.replace(', pixel art style, pixel art style', ', pixel art style')
        
        new_length = len(caption)
        reduction = original_length - new_length
        reduction_pct = (reduction / original_length * 100) if original_length > 0 else 0
        
        self.stats['processed'] += 1
        
        return {
            'filename': filename,
            'original': original,
            'improved': caption,
            'original_length': original_length,
            'new_length': new_length,
            'reduction': reduction,
            'reduction_pct': round(reduction_pct, 1),
            'target_met': 150 <= new_length <= 220
        }
    
    def process_all(self):
        """Process all captions"""
        txt_files = sorted(SOURCE_DIR.glob("*.txt"))
        results = []
        
        for txt_file in txt_files:
            with open(txt_file, 'r') as f:
                caption = f.read().strip()
            
            result = self.simplify_caption(caption, txt_file.name)
            results.append(result)
            
            # Save
            output_file = OUTPUT_DIR / txt_file.name
            with open(output_file, 'w') as f:
                f.write(result['improved'])
            
            status = "✅" if result['target_met'] else "📊"
            print(f"{status} {txt_file.name}: {result['original_length']} → {result['new_length']} chars ({result['reduction_pct']}%)")
        
        return results
    
    def print_stats(self, results):
        """Print final statistics"""
        total = len(results)
        avg_original = sum(r['original_length'] for r in results) / total
        avg_new = sum(r['new_length'] for r in results) / total
        avg_reduction = sum(r['reduction_pct'] for r in results) / total
        target_met = sum(1 for r in results if r['target_met'])
        
        print("\n" + "="*70)
        print("📊 V7 FINAL - WORLD CLASS CAPTIONS")
        print("="*70)
        print(f"Total processed: {self.stats['processed']}")
        print(f"Removed 'simple': {self.stats['removed_simple']}")
        print(f"Removed 'male/female': {self.stats['removed_male_female']}")
        print(f"Fixed facial hair: {self.stats['fixed_facial_hair']}")
        print(f"Removed duplicates: {self.stats['removed_duplicates']}")
        print()
        print(f"Avg length: {round(avg_original, 1)} → {round(avg_new, 1)} chars")
        print(f"Avg reduction: {round(avg_reduction, 1)}%")
        print(f"Target range (150-220): {target_met}/{total} ({round(target_met/total*100, 1)}%)")
        print()
        print(f"📁 Output: {OUTPUT_DIR}/")
        print("="*70)

def main():
    print("🎯 V7 FINAL - World Class Quality Captions")
    print("Surgical fixes while preserving detail")
    print("Target: 150-220 characters\n")
    
    simplifier = FinalCaptionSimplifier()
    results = simplifier.process_all()
    simplifier.print_stats(results)
    
    print("\n✨ Complete! Ready for review.")

if __name__ == "__main__":
    main()
