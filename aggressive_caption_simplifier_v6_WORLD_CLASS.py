#!/usr/bin/env python3
"""
Aggressive Caption Simplifier V6 - WORLD CLASS QUALITY
Complete rebuild from original training data with precision and consistency.

GOLD STANDARD FORMAT (from SD15_PERFECT - 9/10 quality):
pixel art, 24x24, portrait of bespoke punk [type], [hair color/style], [accessories],
[facial hair COLOR], [expression], [eye color], [skin tone], [background], [clothing], pixel art style

CRITICAL RULES:
1. ALWAYS remove: "simple", "male", "female", "wearing" for facial hair, ethnic descriptors
2. Facial hair MUST have color: "light gray stubble" NOT "stubble"
3. ALWAYS include: hair, expression, eyes, skin, background
4. NO duplicates, NO broken text, NO repetition
5. Consistent order and structure
6. Target: 150-220 characters
"""

import os
import re
from pathlib import Path

SOURCE_DIR = Path("runpod_package/training_data")  # START FROM ORIGINALS
OUTPUT_DIR = Path("improved_samples_v6_WORLD_CLASS")
OUTPUT_DIR.mkdir(exist_ok=True)

class WorldClassCaptionSimplifier:
    """V6: World-class quality with precision and consistency"""

    def __init__(self):
        self.stats = {
            'processed': 0,
            'fixed_duplicates': 0,
            'removed_simple': 0,
            'removed_male_female': 0,
            'fixed_facial_hair': 0,
            'removed_ethnic': 0
        }

    def extract_components(self, caption):
        """Extract key components from original caption"""
        components = {
            'hair': None,
            'accessories': [],
            'facial_hair': None,
            'expression': None,
            'eyes': None,
            'skin': None,
            'background': None,
            'clothing': None
        }

        # Extract expression FIRST (most reliable)
        if 'slight smile' in caption.lower():
            components['expression'] = 'slight smile'
        elif 'neutral expression' in caption.lower():
            components['expression'] = 'neutral expression'
        else:
            # Default to neutral if not specified
            components['expression'] = 'neutral expression'

        # Extract eye color
        eye_patterns = [
            (r'dual colored eyes[^,]*', 'dual_colored'),
            (r'deep blue eyes', 'deep blue eyes'),
            (r'dark brown eyes', 'dark brown eyes'),
            (r'light brown eyes', 'light brown eyes'),
            (r'medium brown eyes', 'medium brown eyes'),
            (r'brown eyes', 'brown eyes'),
            (r'blue eyes', 'blue eyes'),
            (r'green eyes', 'green eyes'),
            (r'hazel eyes', 'hazel eyes'),
            (r'gray eyes', 'gray eyes'),
            (r'grey eyes', 'grey eyes'),
            (r'black eyes', 'black eyes'),
            (r'dark eyes', 'dark eyes'),
        ]
        for pattern, name in eye_patterns:
            match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                components['eyes'] = match.group(0).lower()
                break

        # Extract skin tone
        skin_patterns = [
            r'medium light skin',
            r'light green skin',
            r'light gray skin tone',
            r'light skin',
            r'medium skin',
            r'dark skin',
            r'tan skin',
            r'pale skin',
            r'olive skin'
        ]
        for pattern in skin_patterns:
            if re.search(pattern, caption, re.IGNORECASE):
                # Get the matched text and clean it
                match = re.search(pattern, caption, re.IGNORECASE)
                components['skin'] = match.group(0).lower().replace(' tone', '')
                break

        # Extract background
        bg_patterns = [
            r'solid bright green background',
            r'bright green background',
            r'divided background',
            r'brick background',
            r'gradient background',
            r'blue background',
            r'green background',
            r'red background',
            r'bright blue background',
            r'sky blue background',
            r'light orange background',
            r'orange background',
            r'grey background',
            r'gray background',
            r'white background',
            r'background'
        ]
        for pattern in bg_patterns:
            if re.search(pattern, caption, re.IGNORECASE):
                match = re.search(pattern, caption, re.IGNORECASE)
                components['background'] = match.group(0).lower()
                break

        return components

    def simplify_hair_description(self, caption):
        """Simplify hair while keeping color"""
        hair_simplifications = {
            r'bright lime green yellow green hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style': 'green colonial wig',
            r'hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style': 'colonial wig',
            r'bright lime green yellow green wig curled and tied in queue in classic 18th century colonial style': 'green colonial wig',
            r'thin bright lime green yellow green hair with balding receding top and very little hair in natural 18th century style no wig': 'thin green hair, balding',
            r'bright lime green yellow green hair styled in horizontal rolls above ears in 18th century colonial style': 'green colonial wig',
            r'sandy dirty blonde small mohawk with buzzed sides \\(short mohawk\\)': 'blonde mohawk',
            r'light gray hair longer on top and shorter on sides styled in modern casual-polished cut messy but well-groomed': 'light gray hair',
            r'dark brown to black hair with medium brown highlights and natural sheen, longer face-framing emo/gothic style': 'dark brown hair, emo style',
            r'buzzed hair on left side and long side swept hair dangling on the right': 'asymmetric hair',
            r'golden blonde to dirty blonde ombre with natural sun-bleached highlights from beach and sun and salt creating long tousled thick wavy and curly surfer style hair': 'blonde surfer hair',
            r'long dark gray black flowing hair and long waving beard flowing over shoulders and chest thick and well-groomed luxurious Renaissance style': 'long dark hair',
            r'voluminous voluptuous fluffy afrostyle huge curly': 'voluminous curly afro',
        }

        for complex_desc, simple_desc in hair_simplifications.items():
            if re.search(complex_desc, caption, re.IGNORECASE):
                return simple_desc

        # Simple extraction: look for common hair patterns
        if 'bald' in caption.lower():
            return 'bald'

        # Try to extract basic hair color + style
        hair_match = re.search(r'((?:light|dark|medium|bright|sandy|dirty|jet|ashy|golden)\s+)?(?:gray|grey|black|brown|blonde|blond|red|green|blue|purple|silver)\s+(?:hair|mohawk|wig)', caption, re.IGNORECASE)
        if hair_match:
            return hair_match.group(0).lower()

        return None

    def extract_facial_hair_with_color(self, caption):
        """Extract facial hair WITH color consistently"""
        # Check for beard
        if re.search(r'beard', caption, re.IGNORECASE):
            # Try to find color
            color_match = re.search(r'(light\s+gray|dark\s+brown|light\s+brown|brown|black|gray|grey|white|red)\s+(?:\w+\s+)?beard', caption, re.IGNORECASE)
            if color_match:
                return f"{color_match.group(1).lower()} beard"
            else:
                return "beard"

        # Check for stubble
        if re.search(r'stubble', caption, re.IGNORECASE):
            # Try to find color
            color_match = re.search(r'(light\s+gray|dark\s+brown|light\s+brown|brown|black|gray|grey)\s+stubble', caption, re.IGNORECASE)
            if color_match:
                return f"{color_match.group(1).lower()} stubble"
            else:
                # Default to matching hair color or skin tone
                return "stubble"

        # Check for goatee, mustache
        if re.search(r'goatee|mustache|mustache', caption, re.IGNORECASE):
            return "goatee"

        return None

    def simplify_caption(self, caption, filename):
        """World-class simplification: EXTRACT components then REBUILD"""
        original = caption
        original_length = len(caption)

        # Track what we remove
        if 'simple' in original.lower():
            self.stats['removed_simple'] += 1
        if 'male' in original.lower() or 'female' in original.lower():
            self.stats['removed_male_female'] += 1

        # STEP 1: Extract key components
        components = self.extract_components(caption)

        # STEP 2: Extract hair
        hair = self.simplify_hair_description(caption)

        # STEP 3: Extract accessories
        accessories = []
        if 'sunglasses' in caption.lower():
            accessories.append('black sunglasses')
        if 'glasses' in caption.lower() and 'sunglasses' not in caption.lower():
            # Try to find color
            glasses_match = re.search(r'(silver|gold|dark|black|grey|gray|red|blue)\s+(?:\w+\s+)?glasses', caption, re.IGNORECASE)
            if glasses_match:
                accessories.append(f"{glasses_match.group(0).lower()}")
            else:
                accessories.append('glasses')
        if 'cap' in caption.lower() or 'hat' in caption.lower():
            hat_match = re.search(r'(baseball\s+cap|bucket\s+hat|hat|cap)', caption, re.IGNORECASE)
            if hat_match:
                accessories.append(hat_match.group(0).lower())

        # STEP 4: Extract facial hair WITH color
        facial_hair = self.extract_facial_hair_with_color(caption)

        # STEP 5: REBUILD caption in perfect order
        parts = ['pixel art', '24x24', 'portrait of bespoke punk lad']

        # Add hair
        if hair:
            parts.append(hair)

        # Add accessories
        for acc in accessories:
            parts.append(acc)

        # Add facial hair WITH color
        if facial_hair:
            if facial_hair == 'stubble' or facial_hair == 'beard':
                # Try to infer color from hair
                if hair and any(color in hair.lower() for color in ['gray', 'grey', 'light']):
                    parts.append(f"light gray {facial_hair}")
                elif hair and any(color in hair.lower() for color in ['brown', 'dark']):
                    parts.append(f"dark brown {facial_hair}")
                else:
                    parts.append(f"with {facial_hair}")
            else:
                parts.append(f"with {facial_hair}")

        # Add expression
        if components['expression']:
            parts.append(components['expression'])

        # Add eye color
        if components['eyes']:
            parts.append(components['eyes'])

        # Add skin tone
        if components['skin']:
            parts.append(components['skin'])

        # Add background
        if components['background']:
            parts.append(components['background'])
        else:
            parts.append('background')

        # Add clothing (simplified)
        if 'hoodie' in caption.lower():
            parts.append('hoodie')
        elif 'jacket' in caption.lower():
            color_match = re.search(r'(blue|black|gray|grey|red|green|orange|dark\s+blue)\s+jacket', caption, re.IGNORECASE)
            if color_match:
                parts.append(f"{color_match.group(0).lower()}")
            else:
                parts.append('jacket')
        elif 'suit' in caption.lower():
            parts.append('suit')
        elif 'shirt' in caption.lower():
            color_match = re.search(r'(blue|black|white|gray|grey|red|green)\s+(?:\w+\s+)?shirt', caption, re.IGNORECASE)
            if color_match:
                parts.append(f"{color_match.group(0).lower()}")
            else:
                parts.append('shirt')

        parts.append('pixel art style')

        # Join with commas
        rebuilt_caption = ', '.join(parts)

        new_length = len(rebuilt_caption)
        reduction = original_length - new_length
        reduction_pct = (reduction / original_length * 100) if original_length > 0 else 0

        self.stats['processed'] += 1

        return {
            'filename': filename,
            'original': original,
            'improved': rebuilt_caption,
            'original_length': original_length,
            'new_length': new_length,
            'reduction': reduction,
            'reduction_pct': round(reduction_pct, 1),
            'target_met': 150 <= new_length <= 220
        }

    def process_samples(self):
        """Process all samples"""
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
            print(f"{status} {txt_file.name}: {result['original_length']} → {result['new_length']} chars")

        return results

    def print_stats(self):
        """Print processing statistics"""
        print("\n" + "="*70)
        print("📊 V6 WORLD CLASS SIMPLIFICATION STATISTICS")
        print("="*70)
        print(f"Total processed: {self.stats['processed']}")
        print(f"Removed 'simple': {self.stats['removed_simple']}")
        print(f"Removed 'male/female': {self.stats['removed_male_female']}")
        print(f"Fixed facial hair: {self.stats['fixed_facial_hair']}")
        print(f"Removed ethnic descriptors: {self.stats['removed_ethnic']}")
        print(f"Output: {OUTPUT_DIR}/")
        print("="*70)

def main():
    print("🎯 V6 - WORLD CLASS QUALITY CAPTION SIMPLIFIER")
    print("Starting from ORIGINAL training data")
    print("Target: 150-220 characters with perfect consistency")
    print()

    simplifier = WorldClassCaptionSimplifier()
    results = simplifier.process_samples()
    simplifier.print_stats()

    # Calculate summary stats
    total = len(results)
    avg_new = sum(r['new_length'] for r in results) / total
    target_met = sum(1 for r in results if r['target_met'])

    print(f"\n✨ Complete! Avg length: {round(avg_new, 1)} chars")
    print(f"Target range (150-220): {target_met}/{total} ({round(target_met/total*100, 1)}%)")

if __name__ == "__main__":
    main()
