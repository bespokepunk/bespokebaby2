#!/usr/bin/env python3
import csv

# Read CSV
csv_path = "Context 1106/Bespoke Punks - Sheet2.csv"

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
data_rows = rows[1:]

# Find and remove lady_063_PVR (not PVR-3)
removed = False
for i, row in enumerate(data_rows):
    if len(row) > 1 and row[1] == 'lady_063_PVR':
        print(f"Found lady_063_PVR at index {i}")
        print(f"Duplicate marker: '{row[0]}'")
        print(f"Removing this entry...")
        del data_rows[i]
        removed = True
        break

if removed:
    # Write updated CSV
    all_rows = [header] + data_rows
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    print(f"\n✅ Removed lady_063_PVR duplicate")
    print(f"✅ Total entries now: {len(data_rows)}")
    print(f"✅ lady_063_PVR-3 remains (matches actual image)")
else:
    print("Entry not found")
