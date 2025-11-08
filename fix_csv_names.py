#!/usr/bin/env python3
import csv
from pathlib import Path
import shutil
from datetime import datetime

def main():
    # Paths
    csv_path = "Context 1106/Bespoke Punks - Sheet2.csv"
    images_dir = "FORTRAINING6/bespokepunks"

    # Read CSV
    print("Reading CSV...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    data_rows = rows[1:]

    # Get all image names
    print("Scanning images...")
    image_files = list(Path(images_dir).glob("*.png"))
    image_names = {img.stem for img in image_files}

    # Find CSV entries without matching images
    csv_entries = {}  # name -> row_index, row_data
    for i, row in enumerate(data_rows):
        if len(row) > 1 and row[1]:
            name = row[1]
            csv_entries[name] = {'index': i, 'row': row}

    missing_images = [name for name in csv_entries.keys() if name not in image_names]

    print(f"\nFound {len(missing_images)} CSV entries without matching images")

    # Create mapping based on number prefix
    # For entries like lady_052_holly1abstract -> lady_052_pinksilkabstract
    mapping = {}

    for csv_name in missing_images:
        # Extract the prefix (e.g., lady_052 or lad_029)
        parts = csv_name.split('_')
        if len(parts) >= 2:
            prefix = f"{parts[0]}_{parts[1]}"  # e.g., "lady_052"

            # Find images with the same prefix
            matching_images = [img for img in image_names if img.startswith(prefix)]

            # If exactly one match, create mapping
            if len(matching_images) == 1:
                mapping[csv_name] = matching_images[0]
            elif len(matching_images) > 1:
                # Multiple matches - need to be careful
                # Prefer exact numbered matches or variants
                for img in matching_images:
                    # Check if this image already has a CSV entry
                    if img not in csv_entries:
                        # This shouldn't happen since we added all images
                        mapping[csv_name] = img
                        break
                else:
                    # All matches already have CSV entries
                    # Check if any are marked as NEW (duplicates from our script)
                    for img in matching_images:
                        if csv_entries[img]['row'][0] == 'NEW':
                            mapping[csv_name] = img
                            break

    print("\n" + "="*80)
    print("PROPOSED CHANGES - PLEASE REVIEW CAREFULLY")
    print("="*80)

    changes = []
    removals = []

    for old_name, new_name in mapping.items():
        old_entry = csv_entries[old_name]
        old_row = old_entry['row']

        # Check if new name already exists in CSV
        if new_name in csv_entries:
            new_entry = csv_entries[new_name]
            new_row = new_entry['row']

            # Check if old entry has more data than new entry
            old_has_data = any(old_row[i].strip() for i in range(2, min(len(old_row), 16)) if i not in [9, 10, 11])  # Skip empty columns
            new_is_new = new_row[0] == 'NEW'

            if old_has_data and new_is_new:
                # Old entry has data, new entry is just from our script
                # We should rename old entry and remove new entry
                changes.append({
                    'action': 'RENAME',
                    'old_name': old_name,
                    'new_name': new_name,
                    'old_row': old_row,
                    'new_row': new_row,
                    'reason': 'Old entry has data, new is empty AUTO-GENERATED'
                })
                removals.append({
                    'action': 'REMOVE',
                    'name': new_name,
                    'row': new_row,
                    'reason': f'Duplicate of renamed {old_name} (was auto-generated)'
                })
            elif not old_has_data and new_is_new:
                # Both are empty, just remove the old one
                removals.append({
                    'action': 'REMOVE',
                    'name': old_name,
                    'row': old_row,
                    'reason': f'Renamed to {new_name} (both entries empty)'
                })
            else:
                # Complex case - flag for manual review
                print(f"\n⚠️  MANUAL REVIEW NEEDED:")
                print(f"   Old: {old_name}")
                print(f"   New: {new_name}")
                print(f"   Both have data or complex state")
        else:
            # New name doesn't exist, simple rename
            changes.append({
                'action': 'RENAME',
                'old_name': old_name,
                'new_name': new_name,
                'old_row': old_row,
                'reason': 'Simple rename to match image file'
            })

    # Display changes
    print(f"\n📝 RENAMES ({len(changes)}):")
    for change in changes:
        print(f"\n   {change['old_name']}")
        print(f"   → {change['new_name']}")
        print(f"   Reason: {change['reason']}")
        if 'old_row' in change and len(change['old_row']) > 6:
            has_data = any(change['old_row'][i].strip() for i in range(6, min(len(change['old_row']), 13)))
            if has_data:
                print(f"   ℹ️  Has existing data: Background={change['old_row'][6]}, Hair={change['old_row'][7]}, Eyes={change['old_row'][8]}")

    print(f"\n🗑️  REMOVALS ({len(removals)}):")
    for removal in removals:
        print(f"\n   ❌ {removal['name']}")
        print(f"   Reason: {removal['reason']}")

    # Check for any CSV entries without images that weren't mapped
    unmapped = [name for name in missing_images if name not in mapping]
    if unmapped:
        print(f"\n⚠️  UNMAPPED ENTRIES ({len(unmapped)}):")
        print("   These CSV entries have no matching images and no clear mapping:")
        for name in unmapped:
            print(f"      - {name}")

    print("\n" + "="*80)

    # Ask for confirmation
    if changes or removals:
        print(f"\nTotal changes: {len(changes)} renames, {len(removals)} removals")
        response = input("\n⚠️  Apply these changes? (yes/no): ").strip().lower()

        if response == 'yes':
            # Backup first
            backup_path = f"{csv_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(csv_path, backup_path)
            print(f"\n✅ Backup created: {backup_path}")

            # Apply changes
            print("\nApplying changes...")

            # Track indices to remove
            indices_to_remove = set()

            # Apply renames
            for change in changes:
                old_name = change['old_name']
                new_name = change['new_name']
                idx = csv_entries[old_name]['index']

                # Update the name in the row
                data_rows[idx][1] = new_name

                # If old row has data and we're replacing a NEW entry, preserve the data
                if 'new_row' in change and change['new_row'][0] == 'NEW':
                    # Keep the old row's data, just update the name
                    data_rows[idx][0] = ''  # Remove any duplicate marker from old entry

                print(f"   ✓ Renamed: {old_name} → {new_name}")

            # Apply removals
            for removal in removals:
                name = removal['name']
                if name in csv_entries:
                    idx = csv_entries[name]['index']
                    indices_to_remove.add(idx)

            # Remove rows (in reverse order to preserve indices)
            for idx in sorted(indices_to_remove, reverse=True):
                removed_name = data_rows[idx][1]
                del data_rows[idx]
                print(f"   ✓ Removed: {removed_name}")

            # Write updated CSV
            all_rows = [header] + data_rows
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(all_rows)

            print(f"\n✅ CSV updated successfully!")
            print(f"   Total entries: {len(data_rows)}")

            # Verify
            print("\n🔍 Verification:")
            updated_names = {row[1] for row in data_rows if len(row) > 1 and row[1]}
            missing_after = [name for name in updated_names if name not in image_names]
            if missing_after:
                print(f"   ⚠️  Still {len(missing_after)} entries without images:")
                for name in missing_after:
                    print(f"      - {name}")
            else:
                print(f"   ✅ All CSV entries now have matching images!")

        else:
            print("\n❌ Changes cancelled. CSV unchanged.")
    else:
        print("\n✅ No changes needed!")

if __name__ == "__main__":
    main()
