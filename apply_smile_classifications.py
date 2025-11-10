#!/usr/bin/env python3
"""Apply user's smile classifications."""

import os

# Files that should be marked as "slight smile"
smile_files = [
    "lad_003_chai.txt",
    "lad_007_titanium.txt",
    "lad_009_steel.txt",
    "lad_010_aluminum.txt",
    "lad_011_chocolate.txt",
    "lad_012_chromium.txt",
    "lad_013_caramel.txt",
    "lad_014_sugar.txt",
    "lad_020_gpu.txt",
    "lad_021_x.txt",
    "lad_024_x.txt",
    "lad_025_x.txt",
    "lad_026_chromiumabstractsalmon.txt",
    "lad_027_chromiumabstractyellow.txt",
    "lad_028_chromiumabstractgreen.txt",
    "lad_033_molecule-2.txt",
    "lad_036_x.txt",
    "lad_040_melzarmagic.txt",
    "lad_041_Maradona.txt",
    "lad_046_NATE.txt",
    "lad_050_nate-2.txt",
    "lad_050_nate.txt",
    "lad_051_DEVON-2.txt",
    "lad_051_DEVON-4.txt",
    "lad_054_sterling.txt",
    "lad_054_sterlingglasses.txt",
    "lad_054_sterlingglasses3withcrown5.txt",
    "lad_057_Hugh.txt",
    "lad_057_Hugh5.txt",
    "lad_059_SamAScientist.txt",
    "lad_061_DOPE10.txt",
    "lad_061_DOPE7.txt",
    "lad_061_DOPE9.txt",
    "lad_062_devox2.txt",
    "lad_064_Scott.txt",
    "lad_064_sensei.txt",
    "lad_074_lc.txt",
    "lad_079_ravish.txt",
    "lad_080_fcpo.txt",
    "lad_081_iggy2.txt",
    "lad_087_HEEM.txt",
    "lad_090_drscott.txt",
    "lad_091_amit.txt",
    "lad_092_derrick.txt",
    "lad_094_storm.txt",
    "lad_096_apollo.txt",
    "lad_097_drralph.txt",
    "lad_098_Murtaza.txt",
    "lad_102_bunya.txt",
    "lad_102_bunya2.txt",
    "lad_102_bunya3.txt",
    "lad_105_inkspired.txt",
    "lady_001_hazelnut.txt",
    "lady_002_vanilla.txt",
    "lady_008_pinksilk.txt",
    "lady_009_bluesilk.txt",
    "lady_010_saffron.txt",
    "lady_011_sage.txt",
    "lady_013_rosemary.txt",
    "lady_015_lime.txt",
    "lady_016_honey.txt",
    "lady_017_pine.txt",
    "lady_018_strawberry.txt",
    "lady_019_banana.txt",
    "lady_021_diamond.txt",
    "lady_022_gold.txt",
    "lady_023_silver.txt",
    "lady_024_linen.txt",
    "lady_025_mistletoe.txt",
    "lady_026_fur.txt",
    "lady_027_nitrogen.txt",
    "lady_028_marshmallow.txt",
    "lady_029_basil.txt",
    "lady_030_grass.txt",
    "lady_032_salt.txt",
    "lady_033_staranise.txt",
    "lady_034_lavender.txt",
    "lady_035_turmeric.txt",
    "lady_036_boisenberry.txt",
    "lady_037_rose.txt",
    "lady_038_peanut.txt",
    "lady_039_sandalwood.txt",
    "lady_040_fivespice.txt",
    "lady_042_almond.txt",
    "lady_043_orange.txt",
    "lady_044_x.txt",
    "lady_045_x.txt",
    "lady_046_x.txt",
    "lady_047_x.txt",
    "lady_048_pink.txt",
    "lady_049_abstractangels.txt",
    "lady_052_pinksilkabstract.txt",
    "lady_054_hazelnutabstract-3.txt",
    "lady_057_bluesilkabstract.txt",
    "lady_058_x.txt",
    "lady_059_paula-5.txt",
    "lady_059_paula-6.txt",
    "lady_060_winehouse.txt",
    "lady_062_Dalia-2.txt",
    "lady_062_Dalia-BD.txt",
    "lady_063_PVR-3.txt",
    "lady_064_aubree-2.txt",
    "lady_067_salamander-2.txt",
    "lady_068_nikkisf-4.txt",
    "lady_070_mango.txt",
    "lady_078_orange_zest.txt",
    "lady_083_Marianne3.txt",
    "lady_086_ELENI9.txt",
    "lady_087_feybirthday5.txt",
    "lady_088_r.txt",
    "lady_090_missthang.txt",
    "lady_097_dani.txt",
    "lady_097_dani2.txt",
    "lady_099_VQ.txt",
]

base_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

print(f"Applying smile classifications to {len(smile_files)} files...\n")
print("=" * 80)

updated = 0
errors = 0

for filename in smile_files:
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filename}")
        errors += 1
        continue

    with open(filepath, 'r') as f:
        content = f.read()

    if 'neutral expression' in content:
        new_content = content.replace('neutral expression', 'slight smile')
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"✓ {filename}")
        updated += 1
    else:
        print(f"⚠️  {filename} - no 'neutral expression' found")
        errors += 1

print("\n" + "=" * 80)
print(f"✓ Updated: {updated} files")
print(f"✗ Errors: {errors} files")
print("=" * 80)

# Count final distribution
all_files = [f for f in os.listdir(base_dir) if f.endswith('.txt')]
smile_count = 0
neutral_count = 0

for filename in all_files:
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()
        if 'slight smile' in content:
            smile_count += 1
        elif 'neutral expression' in content:
            neutral_count += 1

print(f"\nFinal Distribution:")
print(f"  Total files: {len(all_files)}")
print(f"  😊 Slight smile: {smile_count} ({100*smile_count/len(all_files):.1f}%)")
print(f"  😐 Neutral: {neutral_count} ({100*neutral_count/len(all_files):.1f}%)")
print("=" * 80)
