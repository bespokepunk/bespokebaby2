#!/usr/bin/env python3
"""
VALIDATION SCRIPT - Test Enhanced Detector Against Training Data Ground Truth

Compares detected features vs caption ground truth for all 203 training images.
Outputs accuracy metrics to identify where detection is failing.
"""

import os
import re
from pathlib import Path
from enhanced_feature_extraction_module import EnhancedFeatureExtractor
from collections import defaultdict

# ============================================================================
# GROUND TRUTH PARSERS
# ============================================================================

def parse_caption_features(caption_text):
    """
    Parse caption file to extract ground truth features
    Returns dict with expected features
    """
    features = {
        'eyewear': 'none',
        'earrings': False,
        'earring_type': 'none',
        'expression': 'neutral',
        'hairstyle': None,
    }

    caption_lower = caption_text.lower()

    # Eyewear
    if 'sunglasses' in caption_lower:
        features['eyewear'] = 'sunglasses'
    elif 'glasses' in caption_lower:
        features['eyewear'] = 'glasses'

    # Earrings
    if 'earring' in caption_lower:
        features['earrings'] = True

        if 'hoop' in caption_lower:
            features['earring_type'] = 'hoop'
        elif 'stud' in caption_lower or 'dangly' in caption_lower or 'chunky' in caption_lower:
            features['earring_type'] = 'stud'

    # Expression
    if 'slight smile' in caption_lower or 'smile' in caption_lower:
        features['expression'] = 'slight_smile'
    else:
        features['expression'] = 'neutral'

    # Hairstyle
    if 'braid' in caption_lower:
        features['hairstyle'] = 'braids'
    elif 'curly' in caption_lower:
        features['hairstyle'] = 'curly'
    elif 'wavy' in caption_lower:
        features['hairstyle'] = 'wavy'
    elif 'straight' in caption_lower:
        features['hairstyle'] = 'straight'

    return features


# ============================================================================
# VALIDATION
# ============================================================================

def validate_detector():
    """
    Test detector on all training images and compare vs ground truth
    """

    training_dir = Path("runpod_package/training_data")

    if not training_dir.exists():
        print(f"❌ Training directory not found: {training_dir}")
        return

    # Find all image files
    image_files = list(training_dir.glob("*.png")) + list(training_dir.glob("*.jpg"))

    print("="*70)
    print("ENHANCED DETECTOR VALIDATION")
    print("="*70)
    print(f"Testing on {len(image_files)} training images...")
    print()

    # Track results
    results = {
        'eyewear': {'correct': 0, 'total': 0, 'failures': []},
        'earrings': {'correct': 0, 'total': 0, 'failures': []},
        'earring_type': {'correct': 0, 'total': 0, 'failures': []},
        'expression': {'correct': 0, 'total': 0, 'failures': []},
        'hairstyle': {'correct': 0, 'total': 0, 'failures': []},
    }

    errors = []

    for img_path in image_files:
        # Load caption
        caption_path = img_path.with_suffix('.txt')

        if not caption_path.exists():
            continue

        caption_text = caption_path.read_text()
        ground_truth = parse_caption_features(caption_text)

        # Run detector
        try:
            extractor = EnhancedFeatureExtractor(str(img_path))
            detected = extractor.extract_all_features()

            # Compare eyewear
            if ground_truth['eyewear'] != 'none':
                results['eyewear']['total'] += 1
                if detected['eyewear'] == ground_truth['eyewear']:
                    results['eyewear']['correct'] += 1
                else:
                    results['eyewear']['failures'].append({
                        'file': img_path.name,
                        'expected': ground_truth['eyewear'],
                        'detected': detected['eyewear']
                    })

            # Compare earrings
            if ground_truth['earrings']:
                results['earrings']['total'] += 1
                if detected['earrings']:
                    results['earrings']['correct'] += 1
                else:
                    results['earrings']['failures'].append({
                        'file': img_path.name,
                        'expected': 'earrings present',
                        'detected': 'no earrings'
                    })

                # Compare earring type (only if both detected earrings)
                if detected['earrings']:
                    results['earring_type']['total'] += 1
                    if detected['earring_type'] == ground_truth['earring_type']:
                        results['earring_type']['correct'] += 1
                    else:
                        results['earring_type']['failures'].append({
                            'file': img_path.name,
                            'expected': ground_truth['earring_type'],
                            'detected': detected['earring_type']
                        })

            # Compare expression
            results['expression']['total'] += 1
            if detected['expression'] == ground_truth['expression']:
                results['expression']['correct'] += 1
            else:
                results['expression']['failures'].append({
                    'file': img_path.name,
                    'expected': ground_truth['expression'],
                    'detected': detected['expression']
                })

            # Compare hairstyle (if ground truth has it)
            if ground_truth['hairstyle']:
                results['hairstyle']['total'] += 1
                if detected['hairstyle'] == ground_truth['hairstyle']:
                    results['hairstyle']['correct'] += 1
                else:
                    results['hairstyle']['failures'].append({
                        'file': img_path.name,
                        'expected': ground_truth['hairstyle'],
                        'detected': detected['hairstyle'] if detected['hairstyle'] else 'none detected'
                    })

        except Exception as e:
            errors.append(f"{img_path.name}: {str(e)}")

    # ========================================================================
    # PRINT RESULTS
    # ========================================================================

    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    print()

    for feature, data in results.items():
        if data['total'] == 0:
            continue

        accuracy = (data['correct'] / data['total']) * 100

        print(f"📊 {feature.upper()}")
        print(f"   Accuracy: {data['correct']}/{data['total']} ({accuracy:.1f}%)")

        if accuracy < 100 and len(data['failures']) > 0:
            print(f"   ❌ Failed on {len(data['failures'])} images:")
            for failure in data['failures'][:5]:  # Show first 5
                print(f"      - {failure['file']}: expected '{failure['expected']}', got '{failure['detected']}'")
            if len(data['failures']) > 5:
                print(f"      ... and {len(data['failures']) - 5} more")
        print()

    # Overall summary
    total_tests = sum(r['total'] for r in results.values())
    total_correct = sum(r['correct'] for r in results.values())
    overall_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0

    print("="*70)
    print(f"OVERALL ACCURACY: {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
    print("="*70)

    if errors:
        print(f"\n⚠️  {len(errors)} errors encountered:")
        for error in errors[:10]:
            print(f"   {error}")

    return results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = validate_detector()
