#!/usr/bin/env python3
"""
Efficiently review all 203 images and classify expressions.
Shows images and prompts for classification.
"""

import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def review_images():
    base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"
    png_files = sorted([f for f in os.listdir(base_dir) if f.endswith('.png')])

    classifications = {}

    print(f"Total images to review: {len(png_files)}")
    print("\nInstructions:")
    print("  's' = smile/grin")
    print("  'n' = neutral/straight face")
    print("  'q' = quit and save")
    print("\nShowing 9 images at a time...\n")

    i = 0
    while i < len(png_files):
        # Show 9 images in 3x3 grid
        fig, axes = plt.subplots(3, 3, figsize=(12, 12))
        fig.suptitle(f'Images {i+1}-{min(i+9, len(png_files))} of {len(png_files)}', fontsize=16)

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
            axes[row, col].imshow(img)
            axes[row, col].set_title(f"{idx+1}. {png_file.replace('.png', '')}", fontsize=8)
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
        print(f"\nBatch {i+1}-{i+len(batch_files)}:")
        for idx, png_file in enumerate(batch_files):
            while True:
                response = input(f"  {idx+1}. {png_file}: (s)mile or (n)eutral? ").strip().lower()
                if response == 's':
                    classifications[png_file.replace('.png', '.txt')] = 'smile'
                    break
                elif response == 'n':
                    classifications[png_file.replace('.png', '.txt')] = 'neutral'
                    break
                elif response == 'q':
                    plt.close()
                    return classifications
                else:
                    print("    Invalid input. Use 's', 'n', or 'q'")

        plt.close()
        i += len(batch_files)

    return classifications

if __name__ == "__main__":
    print("Starting expression review...")
    print("This will show images in batches of 9.\n")

    classifications = review_images()

    # Save classifications
    output_file = "/tmp/expression_classifications.txt"
    with open(output_file, 'w') as f:
        for txt_file, expression in sorted(classifications.items()):
            f.write(f"{txt_file}:{expression}\n")

    print(f"\n✓ Saved {len(classifications)} classifications to {output_file}")

    smile_count = sum(1 for e in classifications.values() if e == 'smile')
    neutral_count = sum(1 for e in classifications.values() if e == 'neutral')
    print(f"  Smiles: {smile_count}")
    print(f"  Neutral: {neutral_count}")
