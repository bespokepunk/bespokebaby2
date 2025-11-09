#!/usr/bin/env python3
"""
Interactive tool to review images and generate accurate caption data
"""
from pathlib import Path
from PIL import Image
import json

# Import existing data
from comprehensive_accurate_data import ACCURATE_DATA

def get_all_image_names():
    """Get all image names sorted"""
    images_dir = Path("FORTRAINING6/bespokepunks")
    return sorted([p.stem for p in images_dir.glob("*.png")])

def get_remaining_images():
    """Get images that haven't been documented yet"""
    all_images = get_all_image_names()
    documented = set(ACCURATE_DATA.keys())
    remaining = [name for name in all_images if name not in documented]
    return remaining

def show_review_status():
    """Show current review status"""
    all_images = get_all_image_names()
    remaining = get_remaining_images()

    print("\n" + "="*60)
    print("CAPTION REVIEW STATUS")
    print("="*60)
    print(f"Total images: {len(all_images)}")
    print(f"Documented: {len(ACCURATE_DATA)}")
    print(f"Remaining: {len(remaining)}")
    print(f"Progress: {len(ACCURATE_DATA)/len(all_images)*100:.1f}%")
    print("="*60 + "\n")

def get_next_batch(n=20):
    """Get next n images to review"""
    remaining = get_remaining_images()
    return remaining[:n]

def print_template_for_batch(batch):
    """Print Python dict template for a batch of images"""
    print("\n# Copy this into comprehensive_accurate_data.py:\n")

    for name in batch:
        img_type = "lady" if name.startswith("lady_") else "lad"

        if img_type == "lady":
            template = f"""    '{name}': {{
        'bg': '', 'bg_pattern': 'solid',  # solid/checkered/split/gradient
        'hair': '', 'eyes': '',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': '', 'lips': ''
    }},"""
        else:
            template = f"""    '{name}': {{
        'bg': '', 'bg_pattern': 'solid',  # solid/checkered/split/gradient
        'hair': '', 'eyes': '',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': '', 'facial_hair': ''
    }},"""

        print(template)

def list_next_images_to_review(n=20):
    """List the next images that need review"""
    batch = get_next_batch(n)

    print(f"\nNext {len(batch)} images to review:")
    print("-" * 60)
    for i, name in enumerate(batch, 1):
        img_path = f"FORTRAINING6/bespokepunks/{name}.png"
        print(f"{i:3}. {name}")
        print(f"     Path: {img_path}")
    print("-" * 60)

    return batch

def main():
    show_review_status()

    # Get next batch to review
    batch_size = 20
    batch = list_next_images_to_review(batch_size)

    if batch:
        print(f"\n\nTemplates for next {len(batch)} images:")
        print_template_for_batch(batch)

        print("\n\nTO CONTINUE:")
        print("1. Open each image from the list above")
        print("2. Fill in the template with accurate observations")
        print("3. Add the filled templates to comprehensive_accurate_data.py")
        print("4. Run this script again to get the next batch")
    else:
        print("\n🎉 All images have been documented!")

if __name__ == "__main__":
    main()
