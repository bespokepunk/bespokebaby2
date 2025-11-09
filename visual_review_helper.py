#!/usr/bin/env python3
"""
Visual image review helper - displays images for manual review
"""
from pathlib import Path
from PIL import Image
import sys

from comprehensive_accurate_data import ACCURATE_DATA

def get_remaining_images():
    """Get images that haven't been documented yet"""
    images_dir = Path("FORTRAINING6/bespokepunks")
    all_images = sorted([p.stem for p in images_dir.glob("*.png")])
    documented = set(ACCURATE_DATA.keys())
    remaining = [name for name in all_images if name not in documented]
    return remaining

def display_image_info(image_name, index, total):
    """Display an image and its info"""
    img_path = Path(f"FORTRAINING6/bespokepunks/{image_name}.png")

    if not img_path.exists():
        print(f"❌ Image not found: {img_path}")
        return

    img = Image.open(img_path)

    print("\n" + "="*70)
    print(f"Image {index}/{total}: {image_name}")
    print("="*70)
    print(f"Path: {img_path}")
    print(f"Size: {img.size}")

    # Sample some corner pixels to show bg color
    import numpy as np
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    corners = {
        'Top-left': img_array[0, 0][:3],
        'Top-right': img_array[0, w-1][:3],
        'Bottom-left': img_array[h-1, 0][:3],
        'Bottom-right': img_array[h-1, w-1][:3]
    }

    print("\nCorner pixels (RGB):")
    for pos, rgb in corners.items():
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        print(f"  {pos}: RGB{tuple(rgb)} = {hex_color}")

    # Show the image
    print("\nOpening image for visual inspection...")
    img.show()

    # Return template
    img_type = "lady" if image_name.startswith("lady_") else "lad"

    if img_type == "lady":
        template = f"""
    '{image_name}': {{
        'bg': '', 'bg_pattern': 'solid',
        'hair': '', 'eyes': '',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': '', 'lips': ''
    }},"""
    else:
        template = f"""
    '{image_name}': {{
        'bg': '', 'bg_pattern': 'solid',
        'hair': '', 'eyes': '',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': '', 'facial_hair': ''
    }},"""

    print("\nTemplate to fill:")
    print(template)
    print("="*70)

def main():
    remaining = get_remaining_images()

    if not remaining:
        print("🎉 All images have been documented!")
        return

    print(f"\n📊 Remaining images to review: {len(remaining)}")

    # Ask how many to review
    try:
        if len(sys.argv) > 1:
            n = int(sys.argv[1])
        else:
            n = 5  # Default to 5
    except ValueError:
        n = 5

    batch = remaining[:n]
    print(f"\nReviewing next {len(batch)} images...\n")

    for i, image_name in enumerate(batch, 1):
        display_image_info(image_name, i, len(batch))

        if i < len(batch):
            input("\n Press Enter to continue to next image... ")

    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("1. Copy the filled templates above")
    print("2. Add them to comprehensive_accurate_data.py")
    print("3. Run this script again: python3 visual_review_helper.py [number]")
    print("="*70)

if __name__ == "__main__":
    main()
