#!/usr/bin/env python3
"""
Extract edges from all Bespoke Punks for ControlNet training
Uses PIL-based edge detection instead of OpenCV
"""

import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

def extract_edges(img_path, output_path):
    """Extract edges from image using PIL filters"""
    # Read image
    img = Image.open(img_path).convert('RGB')

    # Convert to grayscale
    gray = img.convert('L')

    # Apply edge detection (combination of filters)
    # Find edges using FIND_EDGES filter
    edges = gray.filter(ImageFilter.FIND_EDGES)

    # Enhance edges
    edges = edges.point(lambda p: 255 if p > 50 else 0)

    # Invert (white edges on black background)
    edges = Image.eval(edges, lambda p: 255 - p)

    # Save
    edges.save(output_path)

    return edges

def main():
    print("🔍 EXTRACTING CANNY EDGES FOR CONTROLNET")
    print("="*80)

    input_dir = Path("FORTRAINING6/bespokepunks")
    output_dir = Path("FORTRAINING6/bespokepunks_edges")
    output_dir.mkdir(exist_ok=True)

    print(f"\n📁 Input:  {input_dir}/")
    print(f"📁 Output: {output_dir}/")
    print()

    count = 0
    failed = 0

    for img_path in sorted(input_dir.glob("*.png")):
        output_path = output_dir / img_path.name

        edges = extract_edges(img_path, output_path)

        if edges is not None:
            count += 1
            print(f"✅ {count:3d}. {img_path.name}")
        else:
            failed += 1
            print(f"❌ Failed: {img_path.name}")

    print()
    print("="*80)
    print(f"✅ Successfully extracted edges: {count} images")
    if failed > 0:
        print(f"❌ Failed: {failed} images")
    print(f"\n📁 Output directory: {output_dir}/")
    print()
    print("Next steps:")
    print("  1. Visually inspect edge maps")
    print("  2. Package with original images for ControlNet training")
    print("  3. Upload to training platform")

if __name__ == "__main__":
    main()
