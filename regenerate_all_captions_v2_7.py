#!/usr/bin/env python3
"""
Regenerate ALL training captions using V2.7 improved detection.

This will:
1. Analyze all images in FORTRAINING6/bespokepunks/
2. Use V2.7's improved eye detection, color mapping, etc.
3. Generate new caption files
4. Save them to FORTRAINING6/bespokepunktext/ for review
"""

import os
import sys
from pathlib import Path
from bespoke_punk_generator_v2_7 import EnhancedImageAnalyzer, EnhancedColorPaletteExtractor, EnhancedPromptGenerator

def regenerate_all_captions():
    """Regenerate all training captions with V2.7 improvements"""

    # Paths
    image_dir = Path("FORTRAINING6/bespokepunks")
    output_dir = Path("FORTRAINING6/bespokepunktext")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all PNG images
    image_files = sorted(list(image_dir.glob("*.png")))

    print(f"Found {len(image_files)} images to process")
    print(f"Output directory: {output_dir}")
    print("="*60)

    # Initialize prompt generator
    prompt_gen = EnhancedPromptGenerator()

    # Process each image
    successful = 0
    failed = 0

    for i, image_path in enumerate(image_files, 1):
        try:
            print(f"\n[{i}/{len(image_files)}] Processing: {image_path.name}")

            # Generate caption using V2.7
            result = prompt_gen.generate(str(image_path))
            prompt = result['prompt']

            # Extract just the caption part (remove "pixel art, 24x24, ")
            # Keep everything after the base prefix
            caption = prompt

            # Save to text file
            output_file = output_dir / f"{image_path.stem}.txt"
            output_file.write_text(caption)

            print(f"  ✓ Saved to: {output_file.name}")
            print(f"  Caption: {caption[:100]}...")

            successful += 1

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
            continue

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total images: {len(image_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nNew captions saved to: {output_dir}")
    print("\nNext steps:")
    print("1. Review the captions in FORTRAINING6/bespokepunktext/")
    print("2. Copy them to FORTRAINING6/bespokepunks/ when ready")
    print("3. Retrain the model")

if __name__ == "__main__":
    regenerate_all_captions()
