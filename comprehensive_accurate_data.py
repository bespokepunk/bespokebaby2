#!/usr/bin/env python3
"""
Comprehensive accurate caption data from visual review
Building complete dataset for all 193 images
"""

# Complete accurate visual observations for all images
ACCURATE_DATA = {
    # LADIES 000-009
    'lady_000_lemon': {
        'bg': 'yellow', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'blue',
        'headwear': 'red and white checkered bandana',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'light', 'lips': 'orange'
    },
    'lady_001_hazelnut': {
        'bg': 'dark green', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'green',
        'headwear': 'pink bow',
        'accessories': 'teal earrings, yellow necklace', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_002_vanilla': {
        'bg': 'light blue', 'bg_pattern': 'solid',
        'hair': 'blonde wavy', 'eyes': 'green-grey',
        'headwear': '',
        'accessories': 'earrings, necklace', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_003_cashew': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black with gold checkered hair accessory', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'gold earrings, white collar', 'clothing': '',
        'skin': 'light', 'lips': 'red'
    },
    'lady_004_nutmeg': {
        'bg': 'peach/orange', 'bg_pattern': 'solid',
        'hair': 'black with gold accent', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'gold earrings', 'clothing': '',
        'skin': 'dark', 'lips': 'pink'
    },
    'lady_005_cinnamon': {
        'bg': 'brown', 'bg_pattern': 'solid',
        'hair': 'light brown/auburn wavy', 'eyes': 'green',
        'headwear': '',
        'accessories': 'gold necklace', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_006_pepper': {
        'bg': 'black and white split', 'bg_pattern': 'split',
        'hair': 'black and white split (Cruella style)', 'eyes': 'green',
        'headwear': '',
        'accessories': 'gold earrings', 'clothing': '',
        'skin': 'pale white', 'lips': 'red'
    },
    'lady_007_alloy': {
        'bg': 'purple', 'bg_pattern': 'solid',
        'hair': 'light brown/blonde short', 'eyes': 'blue/cyan',
        'headwear': '',
        'accessories': 'ocular implant (right eye)', 'clothing': 'burgundy top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_008_pinksilk': {
        'bg': 'pink', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'brown',
        'headwear': 'white tiara/crown',
        'accessories': 'earrings, necklace, cigarette holder', 'clothing': 'light blue dress',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_009_bluesilk': {
        'bg': 'cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'covered by sunglasses',
        'headwear': 'white tiara/crown, black sunglasses',
        'accessories': 'earrings, necklace', 'clothing': 'light blue dress',
        'skin': 'light', 'lips': 'pink'
    },

    # LADS 001-014
    'lad_001_carbon': {
        'bg': 'brick/checkered red-brown', 'bg_pattern': 'checkered',
        'hair': 'brown', 'eyes': 'brown',
        'headwear': 'dark grey hat with gold badge',
        'accessories': '', 'clothing': '',
        'skin': 'tan', 'facial_hair': ''
    },

    # SPECIFIC CASES
    'lady_026_fur': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'green',
        'headwear': 'brown bear/cat ears',
        'accessories': '', 'clothing': 'grey/green top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_062_Dalia-BD': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'brown',
        'headwear': 'white bear ears',
        'accessories': 'red bows (side)', 'clothing': 'red top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_062_Dalia-2': {
        'bg': 'pink', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'brown',
        'headwear': 'brown bear ears',
        'accessories': 'red bows (side)', 'clothing': 'red top',
        'skin': 'light', 'lips': 'pink'
    },
}

# I'll continue adding more as I review them...
# This is just the starter template

if __name__ == "__main__":
    print(f"Currently documented: {len(ACCURATE_DATA)} images")
    print(f"Remaining: {193 - len(ACCURATE_DATA)} images")
