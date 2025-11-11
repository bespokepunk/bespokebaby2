#!/usr/bin/env python3
"""
CAPTION IMPROVEMENT SCRIPT FOR RETRAINING

Improves hairstyle and expression captions with more detailed descriptions.
This will help the model learn better feature associations.

Usage:
    python improve_captions_for_retraining.py

Creates improved versions in: runpod_package/training_data_IMPROVED/
"""

import os
import re
from pathlib import Path
import shutil

def improve_hairstyle_description(caption, hairstyle_type):
    """
    Enhance hairstyle descriptions with more specific language

    Args:
        caption: Original caption text
        hairstyle_type: 'curly', 'wavy', 'straight', 'braids', or None

    Returns:
        Enhanced caption with better hairstyle description
    """
    if not hairstyle_type:
        return caption

    # Improved descriptions for each hairstyle type
    improvements = {
        'curly': {
            'basic': 'curly hair',
            'enhanced': [
                'tightly coiled curly textured hair with high volume',
                'bouncy curly hair with distinct curl pattern',
                'kinky curly hair with dense coils',
                'loose curly hair with flowing ringlets'
            ]
        },
        'wavy': {
            'basic': 'wavy hair',
            'enhanced': [
                'gently wavy hair with soft flowing waves',
                'loosely wavy hair with natural wave pattern',
                'textured wavy hair with medium wave depth',
                'flowing wavy hair with visible wave crests'
            ]
        },
        'straight': {
            'basic': 'straight hair',
            'enhanced': [
                'sleek straight hair hanging smoothly down',
                'smooth straight hair with even texture',
                'straight hair with no waves or curls',
                'pin-straight hair lying flat'
            ]
        },
        'braids': {
            'basic': 'braids',
            'enhanced': [
                'hair in two distinct braids with visible woven pattern',
                'braided hair with alternating interlaced strands',
                'hair styled in parallel braids showing braid structure',
                'braided hairstyle with tight weaving pattern'
            ]
        }
    }

    if hairstyle_type not in improvements:
        return caption

    # Try to find and replace basic description
    basic = improvements[hairstyle_type]['basic']
    enhanced_options = improvements[hairstyle_type]['enhanced']

    # Use first enhanced option (could randomize for variety)
    enhanced = enhanced_options[0]

    # Replace in caption - handle various patterns
    caption_lower = caption.lower()

    # For braids, match the full pattern like "in two braids", "completely in two braids", etc.
    if hairstyle_type == 'braids':
        # Match patterns like "in two braids", "completely in two braids", "hair in braids"
        patterns = [
            r'(hair\s+)?completely\s+in\s+two\s+braids',
            r'in\s+two\s+braids',
            r'in\s+braids',
            r'braided\s+hair'
        ]
        for pattern_str in patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            if pattern.search(caption):
                caption = pattern.sub(enhanced, caption, count=1)
                return caption

    # For other hairstyles, do simple replacement
    if basic in caption_lower:
        pattern = re.compile(re.escape(basic), re.IGNORECASE)
        caption = pattern.sub(enhanced, caption, count=1)

    return caption


def improve_expression_description(caption, expression_type):
    """
    Enhance expression descriptions with mouth shape details

    Args:
        caption: Original caption text
        expression_type: 'slight_smile', 'neutral', or None

    Returns:
        Enhanced caption with better expression description
    """
    if not expression_type:
        return caption

    improvements = {
        'slight_smile': {
            'basic': ['slight smile', 'smile'],
            'enhanced': [
                'mouth corners turned up in gentle slight smile',
                'lips curved upward in subtle smile expression',
                'slight upward curve of mouth showing warm smile',
                'soft smile with mouth corners lifted slightly'
            ]
        },
        'neutral': {
            'basic': ['neutral expression', 'neutral'],
            'enhanced': [
                'mouth in straight neutral line with relaxed expression',
                'neutral facial expression with closed relaxed mouth',
                'mouth resting in neutral horizontal position',
                'calm neutral expression with straight mouth line'
            ]
        }
    }

    if expression_type not in improvements:
        return caption

    basic_patterns = improvements[expression_type]['basic']
    enhanced_options = improvements[expression_type]['enhanced']

    # Use first enhanced option
    enhanced = enhanced_options[0]

    # Replace any matching basic pattern
    caption_lower = caption.lower()
    for basic in basic_patterns:
        if basic in caption_lower:
            pattern = re.compile(re.escape(basic), re.IGNORECASE)
            caption = pattern.sub(enhanced, caption, count=1)
            break

    return caption


def detect_hairstyle_from_caption(caption):
    """Detect hairstyle type from caption"""
    caption_lower = caption.lower()

    if 'braid' in caption_lower:
        return 'braids'
    elif 'curly' in caption_lower:
        return 'curly'
    elif 'wavy' in caption_lower:
        return 'wavy'
    elif 'straight' in caption_lower:
        return 'straight'

    return None


def detect_expression_from_caption(caption):
    """Detect expression type from caption"""
    caption_lower = caption.lower()

    if 'slight smile' in caption_lower or 'smile' in caption_lower:
        return 'slight_smile'
    elif 'neutral' in caption_lower:
        return 'neutral'

    return None


def process_training_data():
    """Process all training captions and create improved versions"""

    training_dir = Path("runpod_package/training_data")
    output_dir = Path("runpod_package/training_data_IMPROVED")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("CAPTION IMPROVEMENT FOR RETRAINING")
    print("="*70)
    print(f"Input:  {training_dir}")
    print(f"Output: {output_dir}")
    print()

    # Find all caption files
    caption_files = list(training_dir.glob("*.txt"))

    stats = {
        'total': 0,
        'hairstyle_improved': 0,
        'expression_improved': 0,
        'both_improved': 0,
        'unchanged': 0
    }

    for caption_path in caption_files:
        stats['total'] += 1

        # Read original caption
        original_caption = caption_path.read_text().strip()
        improved_caption = original_caption

        # Detect features
        hairstyle = detect_hairstyle_from_caption(original_caption)
        expression = detect_expression_from_caption(original_caption)

        hairstyle_changed = False
        expression_changed = False

        # Improve hairstyle description
        if hairstyle:
            new_caption = improve_hairstyle_description(improved_caption, hairstyle)
            if new_caption != improved_caption:
                hairstyle_changed = True
                stats['hairstyle_improved'] += 1
            improved_caption = new_caption

        # Improve expression description
        if expression:
            new_caption = improve_expression_description(improved_caption, expression)
            if new_caption != improved_caption:
                expression_changed = True
                stats['expression_improved'] += 1
            improved_caption = new_caption

        # Track stats
        if hairstyle_changed and expression_changed:
            stats['both_improved'] += 1
        elif not hairstyle_changed and not expression_changed:
            stats['unchanged'] += 1

        # Write improved caption
        output_path = output_dir / caption_path.name
        output_path.write_text(improved_caption)

        # Copy corresponding image
        image_path = caption_path.with_suffix('.png')
        if not image_path.exists():
            image_path = caption_path.with_suffix('.jpg')

        if image_path.exists():
            shutil.copy2(image_path, output_dir / image_path.name)

        # Show examples
        if stats['total'] <= 5 and (hairstyle_changed or expression_changed):
            print(f"\n📝 {caption_path.name}")
            if hairstyle_changed:
                print(f"   Hairstyle: {hairstyle}")
            if expression_changed:
                print(f"   Expression: {expression}")
            if len(improved_caption) < 200:
                print(f"   New: {improved_caption[:150]}...")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total captions processed: {stats['total']}")
    print(f"Hairstyle improved: {stats['hairstyle_improved']}")
    print(f"Expression improved: {stats['expression_improved']}")
    print(f"Both improved: {stats['both_improved']}")
    print(f"Unchanged: {stats['unchanged']}")
    print()
    print(f"✅ Improved training data ready in: {output_dir}")
    print()
    print("Next steps:")
    print("1. Review sample captions in training_data_IMPROVED/")
    print("2. Zip the folder: zip -r training_data_IMPROVED.zip runpod_package/training_data_IMPROVED")
    print("3. Upload to RunPod and retrain")
    print("="*70)


if __name__ == "__main__":
    process_training_data()
