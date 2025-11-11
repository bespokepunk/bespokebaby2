#!/usr/bin/env python3
"""
CRITICAL: Validate synthetic data matches assigned labels

Before training classifier, verify that generated images actually have the
features they're labeled with. If Epoch 4 model generates "smile" prompts
but produces neutral faces, training will fail.
"""

import json
import os
from enhanced_feature_extraction_module import EnhancedFeatureExtractor

SYNTHETIC_DATA_DIR = "synthetic_training_data"
MIN_ACCURACY_THRESHOLD = 70.0  # Must be 70%+ accurate to proceed

def validate_synthetic_data():
    """
    Use current detector to check if synthetic images match their labels
    """
    print("=" * 80)
    print("SYNTHETIC DATA VALIDATION")
    print("=" * 80)
    print("Checking if generated images match assigned labels...")
    print()

    # Load labels
    labels_file = f"{SYNTHETIC_DATA_DIR}/labels.json"
    if not os.path.exists(labels_file):
        print(f"ERROR: {labels_file} not found")
        print("Run generate_synthetic_training_data.py first")
        return False

    with open(labels_file, 'r') as f:
        data = json.load(f)

    print(f"Found {len(data)} labeled images\n")

    # Validate each image
    expression_correct = 0
    expression_total = 0
    hairstyle_correct = 0
    hairstyle_total = 0

    mismatches = {
        'expression': [],
        'hairstyle': []
    }

    for i, item in enumerate(data):
        img_path = f"{SYNTHETIC_DATA_DIR}/images/{item['filename']}"

        if not os.path.exists(img_path):
            print(f"  ⚠ Missing: {item['filename']}")
            continue

        # Extract features using current detector
        extractor = EnhancedFeatureExtractor(img_path)
        detected = extractor.extract_all_features()

        # Check expression
        expected_expr = item['expression']
        detected_expr = detected['expression']

        expression_total += 1
        if expected_expr == detected_expr:
            expression_correct += 1
        else:
            mismatches['expression'].append({
                'file': item['filename'],
                'expected': expected_expr,
                'detected': detected_expr,
                'prompt': item['prompt']
            })

        # Check hairstyle (if present in detected features)
        if 'hairstyle' in detected and 'hairstyle' in item:
            expected_hair = item['hairstyle']
            detected_hair = detected['hairstyle']

            hairstyle_total += 1
            if expected_hair == detected_hair:
                hairstyle_correct += 1
            else:
                mismatches['hairstyle'].append({
                    'file': item['filename'],
                    'expected': expected_hair,
                    'detected': detected_hair,
                    'prompt': item['prompt']
                })

        # Progress
        if (i + 1) % 10 == 0:
            print(f"  Validated {i + 1}/{len(data)} images...")

    print()
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()

    # Expression accuracy
    expr_accuracy = (100.0 * expression_correct / expression_total) if expression_total > 0 else 0
    print(f"📊 EXPRESSION ACCURACY: {expression_correct}/{expression_total} ({expr_accuracy:.1f}%)")

    if expr_accuracy < MIN_ACCURACY_THRESHOLD:
        print(f"   ❌ BELOW THRESHOLD ({MIN_ACCURACY_THRESHOLD}%)")
        print("   Top mismatches:")
        for m in mismatches['expression'][:5]:
            print(f"      - {m['file']}: expected '{m['expected']}', got '{m['detected']}'")
    else:
        print(f"   ✅ ABOVE THRESHOLD")

    print()

    # Hairstyle accuracy
    if hairstyle_total > 0:
        hair_accuracy = 100.0 * hairstyle_correct / hairstyle_total
        print(f"📊 HAIRSTYLE ACCURACY: {hairstyle_correct}/{hairstyle_total} ({hair_accuracy:.1f}%)")

        if hair_accuracy < MIN_ACCURACY_THRESHOLD:
            print(f"   ❌ BELOW THRESHOLD ({MIN_ACCURACY_THRESHOLD}%)")
            print("   Top mismatches:")
            for m in mismatches['hairstyle'][:5]:
                print(f"      - {m['file']}: expected '{m['expected']}', got '{m['detected']}'")
        else:
            print(f"   ✅ ABOVE THRESHOLD")
    else:
        print("📊 HAIRSTYLE: Not validated (no hairstyle detection in current detector)")
        hair_accuracy = 0

    print()
    print("=" * 80)

    # Overall decision
    avg_accuracy = (expr_accuracy + hair_accuracy) / 2 if hairstyle_total > 0 else expr_accuracy

    print(f"AVERAGE ACCURACY: {avg_accuracy:.1f}%")
    print()

    if avg_accuracy >= MIN_ACCURACY_THRESHOLD:
        print("✅ VALIDATION PASSED")
        print("   Synthetic data is accurate enough to train classifier.")
        print("   Proceed with: python train_classifier.py")
        print()

        # Save validation report
        report = {
            'expression_accuracy': expr_accuracy,
            'expression_correct': expression_correct,
            'expression_total': expression_total,
            'hairstyle_accuracy': hair_accuracy if hairstyle_total > 0 else None,
            'hairstyle_correct': hairstyle_correct,
            'hairstyle_total': hairstyle_total,
            'average_accuracy': avg_accuracy,
            'passed': True,
            'mismatches': mismatches
        }

        with open(f"{SYNTHETIC_DATA_DIR}/validation_report.json", 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Validation report saved: {SYNTHETIC_DATA_DIR}/validation_report.json")
        return True

    else:
        print("❌ VALIDATION FAILED")
        print(f"   Synthetic data only {avg_accuracy:.1f}% accurate.")
        print("   Generated images don't match their labels reliably.")
        print()
        print("OPTIONS:")
        print("  1. Try different epoch (Epoch 6 instead of 4)")
        print("  2. Simplify prompts (remove detailed descriptions)")
        print("  3. Abandon synthetic data approach")
        print("  4. Manually review/fix mislabeled images")
        print()

        # Save failure report
        report = {
            'expression_accuracy': expr_accuracy,
            'expression_correct': expression_correct,
            'expression_total': expression_total,
            'hairstyle_accuracy': hair_accuracy if hairstyle_total > 0 else None,
            'hairstyle_correct': hairstyle_correct,
            'hairstyle_total': hairstyle_total,
            'average_accuracy': avg_accuracy,
            'passed': False,
            'mismatches': mismatches
        }

        with open(f"{SYNTHETIC_DATA_DIR}/validation_report.json", 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Failure report saved: {SYNTHETIC_DATA_DIR}/validation_report.json")
        return False

if __name__ == "__main__":
    success = validate_synthetic_data()
    exit(0 if success else 1)
