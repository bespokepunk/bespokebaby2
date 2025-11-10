#!/usr/bin/env python3
"""
Interactive visual review tool for classifying smiles.
Shows 9 images at a time, user marks which ones are smiling.
"""

import os
import json
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def review_images():
    """Show images in batches of 9 and collect classifications."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"
    png_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.png')])

    classifications = {}  # filename -> 'smile' or 'neutral'

    print(f"Total images to review: {len(png_files)}")
    print("\nInstructions:")
    print("  After viewing each batch of 9 images, enter the numbers (1-9) that are SMILING")
    print("  Examples:")
    print("    '1,3,5' - images 1, 3, and 5 are smiling")
    print("    '2 4 7' - images 2, 4, and 7 are smiling")
    print("    'none' or '' - no images are smiling (all neutral)")
    print("    'all' - all images are smiling")
    print("    'q' - save progress and quit")
    print("\nShowing 9 images at a time...\n")

    i = 0
    while i < len(png_files):
        # Show 9 images in 3x3 grid
        fig, axes = plt.subplots(3, 3, figsize=(15, 15))
        fig.suptitle(f'Images {i+1}-{min(i+9, len(png_files))} of {len(png_files)}', fontsize=16, fontweight='bold')

        batch_files = []
        for idx in range(9):
            if i + idx >= len(png_files):
                break

            png_file = png_files[i + idx]
            batch_files.append(png_file)

            img_path = os.path.join(base_dir, png_file)
            img = mpimg.imread(img_path)

            row = idx // 3
            col = idx % 3
            axes[row, col].imshow(img, interpolation='nearest')
            axes[row, col].set_title(f"{idx+1}. {png_file.replace('.png', '')}", fontsize=10, fontweight='bold')
            axes[row, col].axis('off')

        # Hide unused subplots
        for idx in range(len(batch_files), 9):
            row = idx // 3
            col = idx % 3
            axes[row, col].axis('off')

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

        # Get input for which are smiling
        print(f"\nBatch {i+1}-{i+len(batch_files)} ({len(batch_files)} images):")
        while True:
            response = input(f"  Which ones are SMILING? (e.g., '1,3,5' or 'none' or 'all' or 'q' to quit): ").strip().lower()

            if response == 'q':
                plt.close()
                return classifications

            smiling_indices = set()

            if response in ['none', '']:
                # All neutral
                pass
            elif response == 'all':
                # All smiling
                smiling_indices = set(range(len(batch_files)))
            else:
                # Parse the input
                try:
                    # Split by comma, space, or both
                    parts = response.replace(',', ' ').split()
                    for part in parts:
                        idx = int(part) - 1  # Convert to 0-indexed
                        if 0 <= idx < len(batch_files):
                            smiling_indices.add(idx)
                        else:
                            print(f"    Warning: {part} is out of range, ignoring")
                except ValueError:
                    print("    Invalid input. Try again (e.g., '1,3,5' or 'none')")
                    continue

            # Store classifications
            for idx, png_file in enumerate(batch_files):
                txt_file = png_file.replace('.png', '.txt')
                if idx in smiling_indices:
                    classifications[txt_file] = 'smile'
                    print(f"    ✓ {idx+1}. {png_file.replace('.png', '')} → SMILE")
                else:
                    classifications[txt_file] = 'neutral'

            break

        plt.close()
        i += len(batch_files)

        # Save progress after each batch
        with open('/tmp/smile_classifications_progress.json', 'w') as f:
            json.dump(classifications, f, indent=2)
        print(f"\n  Progress saved ({len(classifications)}/{len(png_files)} classified)")
        print()

    return classifications

def apply_classifications(classifications):
    """Apply the classifications to the caption files."""
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

    print("\n" + "=" * 80)
    print("Applying classifications to caption files...")
    print("=" * 80)

    changes = 0
    for txt_file, expression in classifications.items():
        caption_path = os.path.join(base_dir, txt_file)

        if not os.path.exists(caption_path):
            continue

        with open(caption_path, 'r') as f:
            caption = f.read()

        if expression == 'smile':
            # Change neutral to smile
            if 'neutral expression' in caption:
                updated_caption = caption.replace('neutral expression', 'slight smile')
                with open(caption_path, 'w') as f:
                    f.write(updated_caption)
                changes += 1
                print(f"✓ {txt_file}: neutral → slight smile")
        # If 'neutral', keep it as is (already neutral)

    print("\n" + "=" * 80)
    print(f"Applied {changes} classifications (neutral → smile)")

    # Count final distribution
    smile_count = sum(1 for e in classifications.values() if e == 'smile')
    neutral_count = sum(1 for e in classifications.values() if e == 'neutral')

    print(f"\nFinal distribution:")
    print(f"  Slight smile: {smile_count} ({100*smile_count/len(classifications):.1f}%)")
    print(f"  Neutral: {neutral_count} ({100*neutral_count/len(classifications):.1f}%)")
    print("=" * 80)

def main():
    """Main function."""
    print("=" * 80)
    print("INTERACTIVE SMILE CLASSIFIER")
    print("=" * 80)
    print()

    # Check for existing progress
    if os.path.exists('/tmp/smile_classifications_progress.json'):
        response = input("Found existing progress. Resume from where you left off? (y/n): ").strip().lower()
        if response == 'y':
            with open('/tmp/smile_classifications_progress.json', 'r') as f:
                classifications = json.load(f)
            print(f"Loaded {len(classifications)} existing classifications")
            print()
        else:
            classifications = {}
    else:
        classifications = {}

    # Review images
    classifications = review_images()

    if not classifications:
        print("\nNo classifications collected. Exiting.")
        return

    # Save final classifications
    output_file = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/smile_classifications_FINAL.json"
    with open(output_file, 'w') as f:
        json.dump(classifications, f, indent=2)
    print(f"\n✓ Saved {len(classifications)} classifications to {output_file}")

    # Apply to caption files
    apply_classifications(classifications)

if __name__ == "__main__":
    main()
