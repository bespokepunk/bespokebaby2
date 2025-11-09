#!/usr/bin/env python3
"""
Analyze Bespoke Punks CSV to Build Trait Vocabulary

This script reads the manually curated CSV and extracts all unique traits
to build a comprehensive vocabulary for BLIP-2/LLaVA mapping.
"""

import csv
import json
from collections import defaultdict, Counter

def analyze_csv(csv_path):
    """Analyze CSV and extract trait vocabulary"""

    # Trait categories
    traits = {
        'hair': set(),
        'eyes': set(),
        'skin_tone': set(),
        'headwear': set(),
        'facial_hair': set(),
        'accessories': set(),
        'clothing': set(),
        'lips': set(),
        'background_patterns': set(),
        'background_colors': set()
    }

    # Detailed trait analysis
    trait_frequencies = defaultdict(Counter)

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Hair
            if row['Hair']:
                hair = row['Hair'].strip()
                if hair:
                    traits['hair'].add(hair)
                    trait_frequencies['hair'][hair] += 1

            # Eyes
            if row['Eyes']:
                eyes = row['Eyes'].strip()
                if eyes:
                    traits['eyes'].add(eyes)
                    trait_frequencies['eyes'][eyes] += 1

            # Skin Tone
            if row['Skin_Tone']:
                skin = row['Skin_Tone'].strip()
                if skin:
                    traits['skin_tone'].add(skin)
                    trait_frequencies['skin_tone'][skin] += 1

            # Headwear
            if row['Headwear']:
                headwear = row['Headwear'].strip()
                if headwear:
                    traits['headwear'].add(headwear)
                    trait_frequencies['headwear'][headwear] += 1

            # Facial Hair
            if row['Facial_Hair']:
                facial_hair = row['Facial_Hair'].strip()
                if facial_hair:
                    traits['facial_hair'].add(facial_hair)
                    trait_frequencies['facial_hair'][facial_hair] += 1

            # Accessories
            if row['Accessories']:
                accessories = row['Accessories'].strip()
                if accessories:
                    # Split multiple accessories
                    for acc in accessories.split(','):
                        acc = acc.strip()
                        if acc:
                            traits['accessories'].add(acc)
                            trait_frequencies['accessories'][acc] += 1

            # Clothing
            if row['Clothing']:
                clothing = row['Clothing'].strip()
                if clothing:
                    traits['clothing'].add(clothing)
                    trait_frequencies['clothing'][clothing] += 1

            # Lips
            if row['Lips']:
                lips = row['Lips'].strip()
                if lips:
                    traits['lips'].add(lips)
                    trait_frequencies['lips'][lips] += 1

            # Background Pattern
            if row['Background_Pattern']:
                pattern = row['Background_Pattern'].strip()
                if pattern:
                    traits['background_patterns'].add(pattern)
                    trait_frequencies['background_patterns'][pattern] += 1

            # Background Color/Description
            if row['Background']:
                bg = row['Background'].strip()
                if bg:
                    traits['background_colors'].add(bg)
                    trait_frequencies['background_colors'][bg] += 1

    return traits, trait_frequencies


def print_vocabulary_report(traits, trait_frequencies):
    """Print comprehensive vocabulary report"""

    print("=" * 80)
    print("BESPOKE PUNKS TRAIT VOCABULARY ANALYSIS")
    print("=" * 80)
    print()

    # Summary
    print("SUMMARY")
    print("-" * 80)
    total_traits = sum(len(v) for v in traits.values())
    print(f"Total Unique Traits: {total_traits}")
    print()

    for category, trait_set in sorted(traits.items()):
        print(f"{category.upper().replace('_', ' ')}: {len(trait_set)} unique values")
    print()

    # Detailed breakdown
    for category in sorted(traits.keys()):
        print("=" * 80)
        print(f"{category.upper().replace('_', ' ')}")
        print("=" * 80)

        if not traits[category]:
            print("  (no data)")
            print()
            continue

        # Sort by frequency
        sorted_traits = sorted(
            trait_frequencies[category].items(),
            key=lambda x: x[1],
            reverse=True
        )

        for trait, count in sorted_traits:
            print(f"  [{count:3d}x] {trait}")

        print()


def save_vocabulary_json(traits, output_path):
    """Save vocabulary as JSON for V3 integration"""

    # Convert sets to sorted lists
    vocab_dict = {
        category: sorted(list(trait_set))
        for category, trait_set in traits.items()
    }

    with open(output_path, 'w') as f:
        json.dump(vocab_dict, f, indent=2)

    print(f"✓ Vocabulary saved to: {output_path}")


def extract_trait_patterns(traits):
    """Extract common patterns for BLIP-2 mapping"""

    patterns = {
        'hair_descriptors': set(),
        'hair_colors': set(),
        'hair_styles': set(),
        'eyewear': set(),
        'headwear_types': set(),
        'accessories_types': set(),
        'clothing_types': set()
    }

    # Hair analysis
    for hair in traits['hair']:
        # Hair colors
        colors = ['black', 'brown', 'white', 'grey', 'gray', 'blonde', 'tan', 'red', 'blue', 'green', 'purple', 'pink', 'orange', 'yellow', 'cream']
        for color in colors:
            if color in hair.lower():
                patterns['hair_colors'].add(color)

        # Hair descriptors
        descriptors = ['pixelated', 'checkered', 'fluffy', 'spiky', 'wavy', 'curly', 'large', 'afro', 'long', 'short', 'streaks']
        for desc in descriptors:
            if desc in hair.lower():
                patterns['hair_descriptors'].add(desc)

    # Eyewear detection
    for acc in traits['accessories']:
        if any(word in acc.lower() for word in ['glasses', 'sunglasses', 'visor', 'goggles']):
            patterns['eyewear'].add(acc)

    # Headwear types
    for headwear in traits['headwear']:
        types = ['hat', 'cap', 'helmet', 'crown', 'headband', 'visor']
        for hw_type in types:
            if hw_type in headwear.lower():
                patterns['headwear_types'].add(hw_type)

    # Accessory types
    for acc in traits['accessories']:
        types = ['necklace', 'earrings', 'glasses', 'sunglasses', 'tie', 'visor', 'cigarette', 'scar', 'crack']
        for acc_type in types:
            if acc_type in acc.lower():
                patterns['accessories_types'].add(acc_type)

    # Clothing types
    for clothing in traits['clothing']:
        types = ['suit', 'collar', 'top', 'vest', 'tie']
        for c_type in types:
            if c_type in clothing.lower():
                patterns['clothing_types'].add(c_type)

    return patterns


def print_pattern_report(patterns):
    """Print pattern extraction report"""

    print("=" * 80)
    print("TRAIT PATTERN ANALYSIS (for BLIP-2 mapping)")
    print("=" * 80)
    print()

    for category, pattern_set in sorted(patterns.items()):
        print(f"{category.upper().replace('_', ' ')}:")
        for pattern in sorted(pattern_set):
            print(f"  - {pattern}")
        print()


if __name__ == "__main__":
    csv_path = "Context 1106/Bespoke Punks - Accurate Captions.csv"
    output_json = "bespoke_trait_vocabulary.json"

    print("Analyzing Bespoke Punks trait data...")
    print()

    # Analyze CSV
    traits, trait_frequencies = analyze_csv(csv_path)

    # Print reports
    print_vocabulary_report(traits, trait_frequencies)
    print_pattern_report(extract_trait_patterns(traits))

    # Save vocabulary
    save_vocabulary_json(traits, output_json)

    print()
    print("=" * 80)
    print("NEXT STEPS FOR V3 INTEGRATION")
    print("=" * 80)
    print()
    print("1. Use this vocabulary to map BLIP-2/LLaVA outputs to training terms")
    print("2. Build fuzzy matching system for vision model → trait vocabulary")
    print("3. Prioritize specific traits:")
    print("   - Headwear (distinguish hat/helmet/crown from hair)")
    print("   - Eyewear (detect sunglasses/visor/glasses)")
    print("   - Accessories (earrings, necklaces, ties)")
    print("   - Hair styles (pixelated, fluffy, spiky, etc.)")
    print()
