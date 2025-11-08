#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict

def main():
    # Paths
    csv_path = "Context 1106/Bespoke Punks - Sheet2.csv"
    images_dir = "FORTRAINING6/bespokepunks"

    # Read CSV and get all names
    print("Reading CSV...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    csv_names = set()
    csv_names_list = []
    for row in rows[1:]:  # Skip header
        if len(row) > 1 and row[1]:  # Check Name column
            name = row[1]
            csv_names.add(name)
            csv_names_list.append(name)

    # Get all PNG files from images directory
    print("Scanning image directory...")
    image_files = list(Path(images_dir).glob("*.png"))
    image_names = set()
    image_names_list = []
    for img_path in image_files:
        name = img_path.stem  # filename without extension
        image_names.add(name)
        image_names_list.append(name)

    # Find discrepancies
    images_not_in_csv = sorted(image_names - csv_names)
    csv_not_in_images = sorted(csv_names - image_names)

    # Check for duplicates
    csv_duplicates = [name for name in csv_names_list if csv_names_list.count(name) > 1]
    csv_duplicates = sorted(set(csv_duplicates))

    image_duplicates = [name for name in image_names_list if image_names_list.count(name) > 1]
    image_duplicates = sorted(set(image_duplicates))

    # Categorize by type
    def categorize_names(names):
        ladies = [n for n in names if n.startswith('lady_')]
        lads = [n for n in names if n.startswith('lad_')]
        other = [n for n in names if not n.startswith('lady_') and not n.startswith('lad_')]
        return ladies, lads, other

    print("\n" + "="*80)
    print("RECONCILIATION REPORT: FORTRAINING6 Images vs CSV")
    print("="*80)

    print(f"\n📊 OVERALL COUNTS:")
    print(f"   Images in FORTRAINING6/bespokepunks: {len(image_names)}")
    print(f"   Entries in CSV: {len(csv_names)}")
    print(f"   Difference: {abs(len(image_names) - len(csv_names))}")

    if len(image_names) == len(csv_names) and len(images_not_in_csv) == 0 and len(csv_not_in_images) == 0:
        print(f"\n✅ PERFECT MATCH! All images have corresponding CSV entries.")
    else:
        print(f"\n⚠️  DISCREPANCIES FOUND")

    # Report images without CSV entries
    if images_not_in_csv:
        ladies, lads, other = categorize_names(images_not_in_csv)
        print(f"\n❌ IMAGES WITHOUT CSV ENTRIES ({len(images_not_in_csv)} total):")
        if ladies:
            print(f"\n   Ladies ({len(ladies)}):")
            for name in ladies:
                print(f"      - {name}")
        if lads:
            print(f"\n   Lads ({len(lads)}):")
            for name in lads:
                print(f"      - {name}")
        if other:
            print(f"\n   Other ({len(other)}):")
            for name in other:
                print(f"      - {name}")
    else:
        print(f"\n✅ All images have CSV entries")

    # Report CSV entries without images
    if csv_not_in_images:
        ladies, lads, other = categorize_names(csv_not_in_images)
        print(f"\n❌ CSV ENTRIES WITHOUT IMAGES ({len(csv_not_in_images)} total):")
        if ladies:
            print(f"\n   Ladies ({len(ladies)}):")
            for name in ladies:
                print(f"      - {name}")
        if lads:
            print(f"\n   Lads ({len(lads)}):")
            for name in lads:
                print(f"      - {name}")
        if other:
            print(f"\n   Other ({len(other)}):")
            for name in other:
                print(f"      - {name}")
    else:
        print(f"\n✅ All CSV entries have corresponding images")

    # Report duplicates
    if csv_duplicates:
        print(f"\n⚠️  DUPLICATE NAMES IN CSV ({len(csv_duplicates)} names):")
        for name in csv_duplicates:
            count = csv_names_list.count(name)
            print(f"      - {name} (appears {count} times)")
    else:
        print(f"\n✅ No duplicate names in CSV")

    if image_duplicates:
        print(f"\n⚠️  DUPLICATE IMAGES ({len(image_duplicates)} names):")
        for name in image_duplicates:
            count = image_names_list.count(name)
            print(f"      - {name} (appears {count} times)")
    else:
        print(f"\n✅ No duplicate images")

    # Breakdown by category
    csv_ladies, csv_lads, csv_other = categorize_names(csv_names)
    img_ladies, img_lads, img_other = categorize_names(image_names)

    print(f"\n📋 BREAKDOWN BY TYPE:")
    print(f"\n   Ladies:")
    print(f"      CSV: {len(csv_ladies)}")
    print(f"      Images: {len(img_ladies)}")
    print(f"      Match: {'✅ Yes' if len(csv_ladies) == len(img_ladies) and len([n for n in csv_ladies if n not in img_ladies]) == 0 else '❌ No'}")

    print(f"\n   Lads:")
    print(f"      CSV: {len(csv_lads)}")
    print(f"      Images: {len(img_lads)}")
    print(f"      Match: {'✅ Yes' if len(csv_lads) == len(img_lads) and len([n for n in csv_lads if n not in img_lads]) == 0 else '❌ No'}")

    if csv_other or img_other:
        print(f"\n   Other:")
        print(f"      CSV: {len(csv_other)}")
        print(f"      Images: {len(img_other)}")

    # Check for naming pattern issues
    print(f"\n🔍 NAMING PATTERN ANALYSIS:")

    # Find variants (names with suffixes like -2, -3, etc.)
    variants_in_csv = [n for n in csv_names if '-' in n or any(c.isdigit() for c in n.split('_')[-1])]
    variants_in_images = [n for n in image_names if '-' in n or n.split('_')[-1][0].isdigit() if n.split('_')[-1]]

    print(f"   Variants/numbered entries in CSV: {len(variants_in_csv)}")
    print(f"   Variants/numbered entries in Images: {len(variants_in_images)}")

    print("\n" + "="*80)
    print("END OF REPORT")
    print("="*80)

    # Return summary for potential further action
    return {
        'total_images': len(image_names),
        'total_csv': len(csv_names),
        'images_not_in_csv': images_not_in_csv,
        'csv_not_in_images': csv_not_in_images,
        'perfect_match': len(image_names) == len(csv_names) and len(images_not_in_csv) == 0 and len(csv_not_in_images) == 0
    }

if __name__ == "__main__":
    result = main()
