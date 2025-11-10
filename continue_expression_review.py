#!/usr/bin/env python3
"""
Continue expression review from where we left off.
Reads existing classifications and continues from the next image.
"""

import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def load_existing_classifications():
    """Load existing classifications from MASTER file"""
    classifications = {}
    master_file = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/MASTER_EXPRESSION_CLASSIFICATION.txt"

    if os.path.exists(master_file):
        with open(master_file, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        txt_file = parts[0].strip()
                        expression = parts[1].strip()
                        # Convert txt filename to png filename
                        png_file = txt_file.replace('.txt', '.png')
                        classifications[png_file] = expression

    return classifications

def review_images():
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"
    all_png_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.png')])

    # Load existing classifications
    existing = load_existing_classifications()

    # Filter to only unclassified images
    png_files = [f for f in all_png_files if f not in existing]

    print(f"Total images: {len(all_png_files)}")
    print(f"Already classified: {len(existing)}")
    print(f"Remaining to review: {len(png_files)}")
    print("\nInstructions:")
    print("  's' = smile/grin")
    print("  'n' = neutral/straight face")
    print("  'q' = quit and save")
    print("\nShowing 9 images at a time...\n")

    classifications = {}

    i = 0
    while i < len(png_files):
        # Show 9 images in 3x3 grid
        fig, axes = plt.subplots(3, 3, figsize=(15, 15))
        fig.suptitle(f'Images {len(existing)+i+1}-{len(existing)+min(i+9, len(png_files))} of {len(all_png_files)}', fontsize=16)

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
            axes[row, col].set_title(f"{idx+1}. {png_file.replace('.png', '')}", fontsize=10)
            axes[row, col].axis('off')

        # Hide unused subplots
        for idx in range(len(batch_files), 9):
            row = idx // 3
            col = idx % 3
            axes[row, col].axis('off')

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

        # Get classifications for this batch
        print(f"\nBatch (images {len(existing)+i+1} to {len(existing)+i+len(batch_files)}):")
        for idx, png_file in enumerate(batch_files):
            while True:
                response = input(f"  {idx+1}. {png_file.replace('.png', '')}: (s)mile or (n)eutral? ").strip().lower()
                if response == 's':
                    classifications[png_file] = 'smile'
                    print(f"    ✓ Marked as smile")
                    break
                elif response == 'n':
                    classifications[png_file] = 'neutral'
                    print(f"    ✓ Marked as neutral")
                    break
                elif response == 'q':
                    plt.close()
                    return classifications, existing
                else:
                    print("    Invalid input. Use 's', 'n', or 'q'")

        plt.close()
        i += len(batch_files)

    return classifications, existing

if __name__ == "__main__":
    print("Continuing expression review from where we left off...\n")

    new_classifications, existing = review_images()

    # Combine with existing
    all_classifications = existing.copy()
    for png_file, expression in new_classifications.items():
        txt_file = png_file.replace('.png', '.txt')
        all_classifications[png_file] = expression

    # Save updated MASTER file
    master_file = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/MASTER_EXPRESSION_CLASSIFICATION.txt"
    with open(master_file, 'w') as f:
        f.write("# Master Expression Classification for All 203 Images\n")
        f.write("# Based on visual review of 24x24 pixel art\n")
        f.write("# Format: filename:expression (smile or neutral)\n\n")

        # Write in order
        for png_file in sorted(all_classifications.keys()):
            txt_file = png_file.replace('.png', '.txt')
            expression = all_classifications[png_file]
            f.write(f"{txt_file}:{expression}\n")

    print(f"\n✓ Saved classifications to {master_file}")
    print(f"  Total classified: {len(all_classifications)}")

    smile_count = sum(1 for e in all_classifications.values() if e == 'smile')
    neutral_count = sum(1 for e in all_classifications.values() if e == 'neutral')
    print(f"  Smiles: {smile_count}")
    print(f"  Neutral: {neutral_count}")
