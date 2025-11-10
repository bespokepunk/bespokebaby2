#!/usr/bin/env python3
"""
Manually classify expressions for the 90 images.
Reviewing images and creating classification based on visual inspection.
"""

# Based on visual review of images, classify as:
# "smile" - has visible upward curve or happy expression
# "neutral" - straight mouth, serious, or minimal expression

expression_classifications = {
    # Reviewed batch 1
    "lad_001_carbon.txt": "neutral",  # straight mouth
    "lad_003_chai.txt": "neutral",    # straight small mouth
    "lad_004_silicon.txt": "neutral", # straight mouth
    "lad_006_redshift.txt": "neutral", # straight mouth
    "lad_007_titanium.txt": "neutral", # straight mouth
    "lad_008_platinum.txt": "neutral", # straight mouth, serious
    "lad_009_steel.txt": "neutral",   # straight mouth
    "lad_010_aluminum.txt": "neutral", # straight mouth
    "lad_011_chocolate.txt": "neutral", # straight mouth
    "lad_013_caramel.txt": "smile",   # visible smile/grin

    # Need to review remaining 80 images
    # Will do in batches
}

# List of files that need review
files_to_review = [
    "lad_014_sugar.txt",
    "lad_018_mandarin.txt",
    "lad_019_diamond.txt",
    "lad_020_gpu.txt",
    "lad_021_x.txt",
    "lad_022_x.txt",
    "lad_023_x-2.txt",
    "lad_023_x-3.txt",
    "lad_023_x-4.txt",
    "lad_023_x.txt",
    "lad_024_x.txt",
    "lad_025_x.txt",
    "lad_029_famous-9.txt",
    "lad_029_famous4.txt",
    "lad_030_ink.txt",
    "lad_031_fin.txt",
    "lad_032_shaman-4.txt",
    "lad_033_molecule-2.txt",
    "lad_035_JUAN.txt",
    "lad_036_x.txt",
    "lad_037_aressprout.txt",
    "lad_038_cashking-6.txt",
    "lad_040_melzarmagic.txt",
    "lad_041_Maradona.txt",
    "lad_043_jeremey.txt",
    "lad_045_homewithkids3.txt",
    "lad_046_NATE.txt",
    "lad_047_CYGAAR1.txt",
    "lad_049_gainzyyyy12.txt",
    "lad_049_gainzyyyy18.txt",
    "lad_050_nate-2.txt",
    "lad_050_nate.txt",
    "lad_051_DEVON-2.txt",
    "lad_051_DEVON-4.txt",
    "lad_054_sterling.txt",
    "lad_054_sterlingglasses.txt",
    "lad_054_sterlingglasses3withcrown5.txt",
    "lad_057_Hugh.txt",
    "lad_057_Hugh5.txt",
    "lad_058_SAVVA.txt",
    "lad_060_bhaitradingbot2.txt",
    "lad_061_DOPE10.txt",
    "lad_061_DOPE7.txt",
    "lad_061_DOPE9.txt",
    "lad_062_devox2.txt",
    "lad_063_kenichi.txt",
    "lad_064_Scott.txt",
    "lad_064_sensei.txt",
    "lad_066_napoli2.txt",
    "lad_068_mayor.txt",
    "lad_070_IRAsBF2.txt",
    "lad_075_mmhm.txt",
    "lad_078_btoshi.txt",
    "lad_079_ravish.txt",
    "lad_080_fcpo.txt",
    "lad_081_iggy2.txt",
    "lad_086_Scooby.txt",
    "lad_087_HEEM.txt",
    "lad_088_Kareem.txt",
    "lad_089_aguda.txt",
    "lad_090_drscott.txt",
    "lad_091_amit.txt",
    "lad_092_derrick.txt",
    "lad_093_photogee.txt",
    "lad_094_storm.txt",
    "lad_095_godfather.txt",
    "lad_096_apollo.txt",
    "lad_097_drralph.txt",
    "lad_098_Murtaza.txt",
    "lad_099_amenshiller.txt",
    "lad_102_bunya.txt",
    "lad_102_bunya2.txt",
    "lad_102_bunya3.txt",
    "lad_103_merheb.txt",
    "lad_103_merheb2.txt",
    "lad_103_merheb3.txt",
    "lad_105_inkspired.txt",
    "lad_106_sultan.txt",
    "lad_74_lc.txt",
    "lady_099_VQ.txt",
]

print(f"Classified: {len(expression_classifications)}")
print(f"Remaining to review: {len(files_to_review)}")
