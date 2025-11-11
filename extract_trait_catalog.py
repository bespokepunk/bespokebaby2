#!/usr/bin/env python3
"""
Extract trait catalog from training captions
Build comprehensive list of all accessories, features, and traits the model knows
"""

import re
from pathlib import Path
from collections import defaultdict
import json

TRAINING_DIR = Path("runpod_package/training_data")

# Trait patterns to extract
TRAIT_PATTERNS = {
    'eyewear': [
        r'wearing (.+?) (?:sunglasses|glasses|shades)',
        r'wearing (.+?) rimmed (?:sunglasses|glasses)',
    ],
    'headwear': [
        r'wearing (.+?) (?:cap|hat|beanie|bandana|hoodie|hood)',
        r'wearing (.+?) hooded (?:cape|sweatshirt)',
    ],
    'jewelry': [
        r'wearing (.+?) (?:earring|necklace|chain)',
        r'wearing (.+?) stud earring',
        r'wearing (.+?) dangly earring',
    ],
    'hair_accessories': [
        r'wearing (.+?) (?:bow|flower crown|headband)',
        r'(.+?) bow in hair',
        r'wearing flower in hair',
    ],
    'facial_hair': [
        r'wearing (.+?) (?:beard|mustache|goatee)',
        r'full beard',
        r'soul patch',
        r'chin hair',
    ],
    'expression': [
        r'(neutral expression)',
        r'(slight smile)',
        r'(frown)',
        r'(buck teeth)',
    ],
    'clothing': [
        r'wearing (.+?) (?:suit|jacket|hoodie|shirt|blouse)',
        r'wearing (.+?) hooded sweatshirt',
    ],
}

def extract_traits_from_caption(caption):
    """Extract all traits from a single caption"""
    traits = defaultdict(list)

    for category, patterns in TRAIT_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, caption, re.IGNORECASE)
            for match in matches:
                trait = match.strip().lower()
                if trait and len(trait) > 2:  # Filter noise
                    traits[category].append(trait)

    return traits

def main():
    print("=" * 80)
    print("EXTRACTING TRAIT CATALOG FROM TRAINING DATA")
    print("=" * 80)
    print()

    # Collect all traits across all captions
    all_traits = defaultdict(set)
    trait_counts = defaultdict(lambda: defaultdict(int))

    caption_files = list(TRAINING_DIR.glob("*.txt"))
    print(f"Processing {len(caption_files)} caption files...")
    print()

    for caption_file in caption_files:
        with open(caption_file, 'r') as f:
            caption = f.read().strip()

        traits = extract_traits_from_caption(caption)

        for category, trait_list in traits.items():
            for trait in trait_list:
                all_traits[category].add(trait)
                trait_counts[category][trait] += 1

    # Display results
    print("=" * 80)
    print("TRAIT CATALOG")
    print("=" * 80)
    print()

    catalog = {}

    for category in sorted(all_traits.keys()):
        print(f"\n{category.upper()}: ({len(all_traits[category])} unique)")
        print("-" * 80)

        # Sort by frequency
        sorted_traits = sorted(
            trait_counts[category].items(),
            key=lambda x: x[1],
            reverse=True
        )

        catalog[category] = []

        for trait, count in sorted_traits:
            print(f"  {trait:<50} (appears {count}x)")
            catalog[category].append({
                'trait': trait,
                'count': count,
                'prompt_text': f'wearing {trait}' if category in ['eyewear', 'headwear', 'jewelry', 'clothing'] else trait
            })

    # Save to JSON
    output_file = Path("trait_catalog_extracted.json")
    with open(output_file, 'w') as f:
        json.dump(catalog, f, indent=2)

    print()
    print("=" * 80)
    print(f"✓ Trait catalog saved to: {output_file}")
    print("=" * 80)
    print()

    # Summary stats
    total_traits = sum(len(traits) for traits in all_traits.values())
    print(f"Total unique traits: {total_traits}")
    print(f"Categories: {len(all_traits)}")
    print()

    for category, traits in all_traits.items():
        print(f"  {category}: {len(traits)} traits")

    print()

if __name__ == "__main__":
    main()
