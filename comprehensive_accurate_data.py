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

    # LADS 001-020
    'lad_001_carbon': {
        'bg': 'brick/checkered red-brown', 'bg_pattern': 'checkered',
        'hair': 'brown', 'eyes': 'brown',
        'headwear': 'dark grey hat with gold badge',
        'accessories': '', 'clothing': '',
        'skin': 'tan', 'facial_hair': ''
    },
    'lad_002_cash': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'white/grey with green tones', 'eyes': 'covered by black sunglasses',
        'headwear': '',
        'accessories': 'black sunglasses', 'clothing': 'black suit/tie',
        'skin': 'pale grey', 'facial_hair': ''
    },
    'lad_003_chai': {
        'bg': 'tan/brown', 'bg_pattern': 'checkered',
        'hair': 'white/cream fluffy', 'eyes': 'brown',
        'headwear': 'brown hat with white band',
        'accessories': '', 'clothing': 'green and white checkered top',
        'skin': 'brown', 'facial_hair': ''
    },
    'lad_004_silicon': {
        'bg': 'grey', 'bg_pattern': 'checkered',
        'hair': 'grey', 'eyes': 'grey',
        'headwear': '',
        'accessories': 'grey tie', 'clothing': 'grey suit with tie',
        'skin': 'pale grey', 'facial_hair': ''
    },
    'lad_005_copper': {
        'bg': 'brown and yellow', 'bg_pattern': 'checkered',
        'hair': 'brown', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': 'brown mustache'
    },
    'lad_006_redshift': {
        'bg': 'brown/mauve', 'bg_pattern': 'checkered',
        'hair': 'dark blue/navy', 'eyes': 'blue',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'peach/light', 'facial_hair': ''
    },
    'lad_007_titanium': {
        'bg': 'dark grey', 'bg_pattern': 'checkered',
        'hair': 'black', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': '5 o\'clock shadow'
    },
    'lad_008_platinum': {
        'bg': 'multi-colored gradient (cyan, red, orange, blue)', 'bg_pattern': 'gradient',
        'hair': 'black', 'eyes': 'grey/multi',
        'headwear': '',
        'accessories': 'face crack/scar, scruff', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': 'scruff'
    },
    'lad_009_steel': {
        'bg': 'blue', 'bg_pattern': 'checkered',
        'hair': 'black/grey with blue tones', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'glasses, tie, scruff', 'clothing': 'suit with tie',
        'skin': 'light/grey', 'facial_hair': 'scruff'
    },
    'lad_010_aluminum': {
        'bg': 'cyan/light blue', 'bg_pattern': 'solid',
        'hair': 'red (under hat)', 'eyes': 'brown',
        'headwear': 'red hat/cap',
        'accessories': 'glasses, scruff', 'clothing': 'orange top',
        'skin': 'light/pink', 'facial_hair': 'scruff'
    },
    'lad_011_chocolate': {
        'bg': 'cream to coral gradient', 'bg_pattern': 'gradient',
        'hair': 'black/grey', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'brown checkered collar',
        'skin': 'tan/brown', 'facial_hair': 'beard'
    },
    'lad_012_chromium': {
        'bg': 'light grey/eggshell', 'bg_pattern': 'gradient',
        'hair': 'ash grey/brown', 'eyes': 'blue',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'pale/pink', 'facial_hair': 'scruff'
    },
    'lad_013_caramel': {
        'bg': 'multi-colored split (blue, white, red)', 'bg_pattern': 'split',
        'hair': 'black', 'eyes': 'black',
        'headwear': '',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'olive/tan', 'facial_hair': ''
    },
    'lad_014_sugar': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'brown/red', 'eyes': 'blue',
        'headwear': '',
        'accessories': '', 'clothing': 'white checkered collar',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_015_jackson': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'white/grey fluffy (zombie-like)', 'eyes': 'covered by black sunglasses',
        'headwear': '',
        'accessories': 'black sunglasses', 'clothing': 'grey/black suit',
        'skin': 'pale grey/white', 'facial_hair': ''
    },
    'lad_016_tungsten': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'grey/white pixelated/blocky', 'eyes': 'covered by black sunglasses',
        'headwear': '',
        'accessories': 'black sunglasses', 'clothing': 'grey pixelated pattern',
        'skin': 'pale grey with pixelated/checkered pattern', 'facial_hair': ''
    },
    'lad_017_ink': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'white/grey checkered pixelated', 'eyes': 'covered by black sunglasses',
        'headwear': '',
        'accessories': 'black sunglasses', 'clothing': 'black suit',
        'skin': 'pale grey/white', 'facial_hair': ''
    },
    'lad_018_mandarin': {
        'bg': 'light green/sage', 'bg_pattern': 'solid',
        'hair': 'dark grey/black', 'eyes': 'grey',
        'headwear': 'grey helmet/cap',
        'accessories': '', 'clothing': 'dark blue with colorful checkered pattern (cyan, yellow, red, blue)',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_019_diamond': {
        'bg': 'bright green/turquoise', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'cyan and white checkered collar',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_020_gpu': {
        'bg': 'sage/grey-green', 'bg_pattern': 'solid',
        'hair': 'blonde/tan wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'black and white checkered collar',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_021_x': {
        'bg': 'bright green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'dark grey/black', 'eyes': 'brown',
        'headwear': 'dark helmet with white X logo',
        'accessories': '', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_022_x': {
        'bg': 'bright green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'black/tan', 'eyes': 'brown/tan',
        'headwear': 'white headband',
        'accessories': 'gold necklace', 'clothing': '',
        'skin': 'tan/brown', 'facial_hair': ''
    },
    'lad_023_x': {
        'bg': 'cyan/turquoise striped/gradient', 'bg_pattern': 'striped',
        'hair': 'grey pixelated/checkered', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_024_x': {
        'bg': 'purple', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'dark purple/brown',
        'headwear': 'dark helmet with light purple X logo',
        'accessories': '', 'clothing': 'white and light purple checkered collar',
        'skin': 'tan/brown', 'facial_hair': 'beard'
    },
    'lad_025_x': {
        'bg': 'light purple/grey', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'brown',
        'headwear': 'dark helmet with orange X logo',
        'accessories': '', 'clothing': 'white and light blue checkered collar',
        'skin': 'tan/brown', 'facial_hair': 'beard'
    },

    # LADIES 010-019
    'lady_010_saffron': {
        'bg': 'dark green', 'bg_pattern': 'solid',
        'hair': 'blonde/tan braided', 'eyes': 'green',
        'headwear': '',
        'accessories': 'gold earrings', 'clothing': 'magenta/pink top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_011_sage': {
        'bg': 'blue-grey', 'bg_pattern': 'solid',
        'hair': 'brown wavy long', 'eyes': 'green',
        'headwear': '',
        'accessories': 'white earring', 'clothing': 'coral/salmon top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_012_parasite': {
        'bg': 'cyan to pink gradient with pink splatter effects', 'bg_pattern': 'gradient',
        'hair': 'black', 'eyes': 'light grey/blue (zombie-like)',
        'headwear': '',
        'accessories': '', 'clothing': 'white top',
        'skin': 'pale white/blue (zombie-like)', 'lips': ''
    },
    'lady_013_rosemary': {
        'bg': 'light purple to peach gradient', 'bg_pattern': 'gradient',
        'hair': 'brown wavy long', 'eyes': 'green',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'tan/light brown', 'lips': 'pink'
    },
    'lady_014_olive': {
        'bg': 'dark purple', 'bg_pattern': 'solid',
        'hair': 'blonde/tan braided', 'eyes': 'covered by brown visor/sunglasses',
        'headwear': '',
        'accessories': 'brown visor/sunglasses', 'clothing': 'magenta/pink top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_015_lime': {
        'bg': 'bright yellow-green/lime', 'bg_pattern': 'solid',
        'hair': 'black short', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white and grey checkered collar',
        'skin': 'light/pink', 'lips': 'pink'
    },
    'lady_016_honey': {
        'bg': 'tan/orange gradient', 'bg_pattern': 'gradient',
        'hair': 'white/grey wavy', 'eyes': 'green',
        'headwear': 'brown glasses/visor',
        'accessories': 'brown glasses', 'clothing': 'blue top',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_017_pine': {
        'bg': 'yellow-green/sage', 'bg_pattern': 'solid',
        'hair': 'brown wavy long', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'blue and tan checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_018_strawberry': {
        'bg': 'dark green', 'bg_pattern': 'solid',
        'hair': 'red/burgundy wavy', 'eyes': 'olive/yellow-green',
        'headwear': '',
        'accessories': '', 'clothing': 'yellow and green checkered collar',
        'skin': 'light/pink', 'lips': 'red'
    },
    'lady_019_banana': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'mint green/turquoise large', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'yellow and orange checkered collar',
        'skin': 'light/pink', 'lips': 'red'
    },
    'lady_020_blood': {
        'bg': 'pink to magenta gradient', 'bg_pattern': 'gradient',
        'hair': 'black with blue/grey checkered pattern', 'eyes': 'black',
        'headwear': '',
        'accessories': '', 'clothing': 'white and magenta checkered collar',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_021_diamond': {
        'bg': 'light cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'brown/burgundy wavy with red checkered pattern', 'eyes': 'teal/green',
        'headwear': '',
        'accessories': 'white earring', 'clothing': 'cyan and white checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_022_gold': {
        'bg': 'dark grey', 'bg_pattern': 'solid',
        'hair': 'brown wavy with orange and white bow/accessory', 'eyes': 'green',
        'headwear': '',
        'accessories': 'orange and white hair bow', 'clothing': 'white checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_023_silver': {
        'bg': 'light grey to beige gradient', 'bg_pattern': 'gradient',
        'hair': 'brown wavy with blue/purple/cyan hair accessory', 'eyes': 'green',
        'headwear': '',
        'accessories': 'colorful hair bow (blue/purple/cyan)', 'clothing': 'light blue checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_024_linen': {
        'bg': 'cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'brown wavy with yellow/gold checkered bow', 'eyes': 'green',
        'headwear': '',
        'accessories': 'yellow/gold checkered bow', 'clothing': 'purple checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_025_mistletoe': {
        'bg': 'dark blue/navy', 'bg_pattern': 'solid',
        'hair': 'brown wavy with red and white checkered bow', 'eyes': 'green',
        'headwear': '',
        'accessories': 'red and white checkered bow', 'clothing': 'green checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_027_nitrogen': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'black wavy', 'eyes': 'green',
        'headwear': '',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_028_marshmallow': {
        'bg': 'pink', 'bg_pattern': 'solid',
        'hair': 'black/grey checkered pixelated', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_029_basil': {
        'bg': 'green split/gradient', 'bg_pattern': 'split',
        'hair': 'brown short', 'eyes': 'covered by brown/tan visor',
        'headwear': '',
        'accessories': 'brown/tan visor/sunglasses', 'clothing': 'purple checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_030_grass': {
        'bg': 'tan/peach to orange/yellow split', 'bg_pattern': 'split',
        'hair': 'brown checkered/pixelated long', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'red and white checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_031_paprika': {
        'bg': 'light beige/white', 'bg_pattern': 'solid',
        'hair': 'red/burgundy wavy large', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'grey checkered collar',
        'skin': 'pale/white', 'lips': 'pink'
    },
    'lady_032_salt': {
        'bg': 'red', 'bg_pattern': 'solid',
        'hair': 'white/grey wavy with red and white checkered bow', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'red and white checkered bow', 'clothing': 'tan/beige checkered collar',
        'skin': 'light/pink', 'lips': 'red'
    },
    'lady_033_staranise': {
        'bg': 'light pink', 'bg_pattern': 'solid',
        'hair': 'brown checkered/pixelated wavy', 'eyes': 'green/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'burgundy/wine top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_034_lavender': {
        'bg': 'light pink/peach', 'bg_pattern': 'solid',
        'hair': 'brown wavy with blue/grey checkered bow', 'eyes': 'purple/burgundy',
        'headwear': '',
        'accessories': 'blue/grey checkered bow', 'clothing': 'grey checkered collar',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_035_turmeric': {
        'bg': 'light peach/tan', 'bg_pattern': 'solid',
        'hair': 'brown/tan checkered wavy with blue/teal checkered hat', 'eyes': 'burgundy',
        'headwear': 'blue/teal checkered wide-brim hat',
        'accessories': '', 'clothing': '',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_036_boisenberry': {
        'bg': 'purple/magenta', 'bg_pattern': 'solid',
        'hair': 'red/pink/burgundy wavy large pixelated', 'eyes': 'olive/yellow-green',
        'headwear': '',
        'accessories': 'teal/green accessory', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_037_rose': {
        'bg': 'pink', 'bg_pattern': 'solid',
        'hair': 'brown wavy pigtails with bows', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'yellow earring/accessory', 'clothing': 'tan/cream checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_038_peanut': {
        'bg': 'light cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'brown/burgundy wavy', 'eyes': 'purple',
        'headwear': '',
        'accessories': '', 'clothing': 'pink and yellow checkered collar',
        'skin': 'light/pink', 'lips': 'red'
    },
    'lady_039_sandalwood': {
        'bg': 'light purple', 'bg_pattern': 'solid',
        'hair': 'red/pink/burgundy wavy large pixelated', 'eyes': 'covered by purple visor',
        'headwear': '',
        'accessories': 'purple visor/sunglasses', 'clothing': 'teal/green checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_040_fivespice': {
        'bg': 'yellow', 'bg_pattern': 'solid',
        'hair': 'black/brown with purple checkered highlights', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'purple and orange/yellow checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_041_bayleaf': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'red/pink/burgundy wavy large pixelated', 'eyes': 'olive/yellow-green',
        'headwear': '',
        'accessories': 'cigarette holder (white/orange)', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_042_almond': {
        'bg': 'pink', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'cream/tan checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_043_orange': {
        'bg': 'magenta to green split/gradient', 'bg_pattern': 'split',
        'hair': 'black/dark pixelated', 'eyes': 'brown',
        'headwear': 'yellow/gold pixelated crown/headband with cyan/magenta accents',
        'accessories': 'green splatter/effects', 'clothing': '',
        'skin': 'light/pink', 'lips': 'pink'
    },
    'lady_044_x': {
        'bg': 'magenta to green split/gradient', 'bg_pattern': 'split',
        'hair': 'black/dark pixelated', 'eyes': 'brown',
        'headwear': 'colorful pixelated crown (white/grey/purple/cyan/magenta)',
        'accessories': '', 'clothing': '',
        'skin': 'light/pink', 'lips': 'pink'
    },
    'lady_045_x': {
        'bg': 'green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'black/grey pixelated short', 'eyes': 'burgundy/purple',
        'headwear': '',
        'accessories': '', 'clothing': 'yellow checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_046_x': {
        'bg': 'green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'brown short pixelated', 'eyes': 'olive/brown',
        'headwear': '',
        'accessories': 'orange/yellow accessory', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_047_x': {
        'bg': 'green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'black short', 'eyes': 'covered by tan visor',
        'headwear': '',
        'accessories': 'tan visor/sunglasses', 'clothing': 'pink/purple top',
        'skin': 'light/pink', 'lips': 'red'
    },
    'lady_048_pink': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'blonde/tan pixelated curly large', 'eyes': 'blue',
        'headwear': '',
        'accessories': '', 'clothing': 'purple/mauve checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_049_abstractangels': {
        'bg': 'green gradient/striped', 'bg_pattern': 'striped',
        'hair': 'black wavy', 'eyes': 'teal/cyan',
        'headwear': '',
        'accessories': 'white pixelated angel wings, purple cross/halo', 'clothing': '',
        'skin': 'light', 'lips': 'red'
    },
    'lady_050_x-6': {
        'bg': 'magenta to green split/gradient', 'bg_pattern': 'split',
        'hair': 'black/grey pixelated short', 'eyes': 'brown',
        'headwear': 'gold/tan visor',
        'accessories': 'white pixelated effects, green/white cross', 'clothing': 'white/cream checkered collar',
        'skin': 'light/tan', 'lips': 'pink'
    },
    'lady_051_rosieabstract': {
        'bg': 'green striped/checkered', 'bg_pattern': 'checkered',
        'hair': 'brown short with orange/white/yellow checkered bow/crown', 'eyes': 'grey/purple',
        'headwear': 'orange/white/yellow checkered bow/crown',
        'accessories': '', 'clothing': 'light cyan/white checkered collar',
        'skin': 'light/tan', 'lips': 'orange'
    },
    'lady_052_pinksilkabstract': {
        'bg': 'purple to orange gradient', 'bg_pattern': 'gradient',
        'hair': 'brown short with white/pink tiara', 'eyes': 'brown/tan',
        'headwear': 'white/pink tiara/crown',
        'accessories': '', 'clothing': 'light blue/white checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_053_pepperabstract': {
        'bg': 'green to black split', 'bg_pattern': 'split',
        'hair': 'black and white split (Cruella style)', 'eyes': 'green',
        'headwear': '',
        'accessories': '', 'clothing': 'red/pink checkered collar',
        'skin': 'pale white', 'lips': 'red'
    },
    'lady_054_hazelnutabstract-3': {
        'bg': 'green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'brown wavy with blue bow/accessory', 'eyes': 'green',
        'headwear': '',
        'accessories': 'blue bow/accessory', 'clothing': 'cream/tan checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_055_bloodabstract': {
        'bg': 'green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'black with blue/grey checkered pattern and yellow/white crown', 'eyes': 'purple',
        'headwear': 'yellow/white crown/tiara',
        'accessories': '', 'clothing': 'light purple/white checkered collar',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_056_alloyabstract': {
        'bg': 'pink to purple to blue gradient', 'bg_pattern': 'gradient',
        'hair': 'brown/tan pixelated short', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_057_bluesilkabstract': {
        'bg': 'purple to cyan gradient', 'bg_pattern': 'gradient',
        'hair': 'brown short with white/pink tiara', 'eyes': 'covered by black sunglasses',
        'headwear': 'white/pink tiara/crown',
        'accessories': 'black sunglasses', 'clothing': 'light blue/white checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_058_x': {
        'bg': 'cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'black/grey pixelated wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'pink top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_059_paula-5': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'brown checkered/pixelated wavy', 'eyes': 'purple/grey',
        'headwear': 'grey/white visor',
        'accessories': 'grey/white visor', 'clothing': 'blue checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_060_winehouse': {
        'bg': 'light purple', 'bg_pattern': 'solid',
        'hair': 'black pixelated wavy with white/grey/red accessories', 'eyes': 'olive/tan',
        'headwear': '',
        'accessories': 'red flower/bow, white pixelated effects', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_061_nikkkk-2': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'brown wavy long', 'eyes': 'cyan/teal',
        'headwear': 'light cyan/mint pixelated hat/headband',
        'accessories': 'white/green cross', 'clothing': 'grey/dark checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_063_PVR-3': {
        'bg': 'orange', 'bg_pattern': 'solid',
        'hair': 'black large afro', 'eyes': 'covered by tan visor',
        'headwear': '',
        'accessories': 'tan visor/sunglasses', 'clothing': 'magenta/burgundy top',
        'skin': 'light/tan', 'lips': 'pink'
    },
    'lady_064_aubree-2': {
        'bg': 'magenta/pink', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'green',
        'headwear': '',
        'accessories': '', 'clothing': 'purple and white checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_065_miggs-4': {
        'bg': 'purple striped/gradient', 'bg_pattern': 'striped',
        'hair': 'blonde/tan pixelated curly large checkered', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'yellow and pink checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_066_monalisa-3': {
        'bg': 'green gradient/pixelated', 'bg_pattern': 'gradient',
        'hair': 'brown wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'tan/yellow', 'lips': ''
    },
    'lady_067_salamander-2': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'white/cream large fluffy', 'eyes': 'purple',
        'headwear': '',
        'accessories': '', 'clothing': 'tan/brown checkered shawl/collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_068_nikkisf-4': {
        'bg': 'tan/peach', 'bg_pattern': 'solid',
        'hair': 'black pixelated wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'tan/brown checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_069_giulia': {
        'bg': 'yellow/tan', 'bg_pattern': 'solid',
        'hair': 'brown with yellow/green/cyan pixelated accessories', 'eyes': 'covered by blue visor',
        'headwear': '',
        'accessories': 'blue visor, yellow/green/cyan pixelated hair decorations', 'clothing': 'green/blue checkered collar',
        'skin': 'tan/brown', 'lips': ''
    },
    'lady_070_mango': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'pink pixelated large', 'eyes': 'purple',
        'headwear': '',
        'accessories': '', 'clothing': 'light blue/white checkered collar',
        'skin': 'pale white', 'lips': ''
    },
    'lady_071_papaya': {
        'bg': 'tan/brown', 'bg_pattern': 'solid',
        'hair': 'black pixelated short', 'eyes': 'grey',
        'headwear': '',
        'accessories': 'white earrings', 'clothing': '',
        'skin': 'light/tan', 'lips': 'pink'
    },
    'lady_072_tangerine': {
        'bg': 'dark blue', 'bg_pattern': 'solid',
        'hair': 'orange/red gradient pixelated large wavy', 'eyes': 'grey/purple',
        'headwear': '',
        'accessories': 'yellow earring', 'clothing': '',
        'skin': 'light', 'lips': 'red'
    },
    'lady_073_mango_punk': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'yellow/orange pixelated large with burgundy bow', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': 'burgundy/red bow, cigarette holder', 'clothing': '',
        'skin': 'pale white', 'lips': ''
    },
    'lady_074_melon': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'tan/peach checkered pixelated', 'eyes': 'cyan/teal',
        'headwear': 'tan/peach checkered wide-brim hat',
        'accessories': '', 'clothing': 'red cross/medical symbol',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_075_clementine': {
        'bg': 'cyan checkered', 'bg_pattern': 'checkered',
        'hair': 'red/magenta pixelated large with grey bows', 'eyes': 'green',
        'headwear': '',
        'accessories': 'grey bows', 'clothing': 'black and white checkered collar',
        'skin': 'pale white', 'lips': 'pink'
    },
    'lady_076_orange_blossom': {
        'bg': 'tan/beige', 'bg_pattern': 'solid',
        'hair': 'brown checkered/pixelated wavy with brown crown', 'eyes': 'brown',
        'headwear': 'brown pixelated crown',
        'accessories': '', 'clothing': 'red top',
        'skin': 'light/tan', 'lips': 'pink'
    },
    'lady_077_pink_grapefruit': {
        'bg': 'grey to pink split', 'bg_pattern': 'split',
        'hair': 'blue/teal pixelated large', 'eyes': 'olive/tan',
        'headwear': '',
        'accessories': '', 'clothing': 'red and white checkered collar',
        'skin': 'light/tan', 'lips': 'pink'
    },
    'lady_078_orange_zest': {
        'bg': 'tan/brown', 'bg_pattern': 'solid',
        'hair': 'black/brown/blue pixelated', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_079_lime_breeze': {
        'bg': 'yellow gradient/striped', 'bg_pattern': 'gradient',
        'hair': 'brown pixelated short', 'eyes': 'brown',
        'headwear': 'orange headband',
        'accessories': 'grey/white pixelated wings/effects', 'clothing': 'brown checkered collar',
        'skin': 'tan', 'lips': 'pink'
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

    # Additional LADs batch 1
    'lad_023_x-2': {
        'bg': 'cyan/turquoise striped/gradient', 'bg_pattern': 'striped',
        'hair': 'grey pixelated/checkered', 'eyes': 'brown',
        'headwear': 'green and white checkered crown/headband',
        'accessories': '', 'clothing': 'black suit/tie',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_023_x-3': {
        'bg': 'cyan/turquoise striped/gradient', 'bg_pattern': 'striped',
        'hair': 'grey pixelated/checkered', 'eyes': 'brown',
        'headwear': 'colorful pixelated crown (green, red/magenta, orange, blue)',
        'accessories': '', 'clothing': 'black suit/tie',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_023_x-4': {
        'bg': 'cyan/turquoise striped/gradient', 'bg_pattern': 'striped',
        'hair': 'grey pixelated/checkered', 'eyes': 'brown',
        'headwear': 'green pixelated crown/headband',
        'accessories': '', 'clothing': 'black suit/tie',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_026_chromiumabstractsalmon': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'dark grey/black spiky pixelated', 'eyes': 'blue/cyan',
        'headwear': '',
        'accessories': '', 'clothing': 'pink/salmon top',
        'skin': 'pale grey/white', 'facial_hair': ''
    },
    'lad_027_chromiumabstractyellow': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'dark grey/black spiky pixelated', 'eyes': 'blue/cyan',
        'headwear': '',
        'accessories': '', 'clothing': 'yellow/tan top',
        'skin': 'pale grey/white', 'facial_hair': ''
    },
    'lad_028_chromiumabstractgreen': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'dark grey/black spiky pixelated', 'eyes': 'blue/cyan',
        'headwear': '',
        'accessories': '', 'clothing': 'grey/green top',
        'skin': 'pale grey/white', 'facial_hair': ''
    },
    'lad_029_famous-9': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'brown/black pixelated', 'eyes': 'covered by colorful visor/glasses',
        'headwear': '',
        'accessories': 'colorful pixelated visor/glasses (green, yellow, orange, magenta)', 'clothing': 'orange top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_029_famous4': {
        'bg': 'yellow/tan gradient', 'bg_pattern': 'gradient',
        'hair': 'brown/black pixelated', 'eyes': 'green pixelated',
        'headwear': '',
        'accessories': 'cigarette holder', 'clothing': 'orange top',
        'skin': 'light', 'facial_hair': 'black mustache'
    },
    'lad_030_ink': {
        'bg': 'dark grey', 'bg_pattern': 'solid',
        'hair': 'black afro', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'red top with dark grey/black vest',
        'skin': 'dark/brown', 'facial_hair': 'grey scruff'
    },
    'lad_031_fin': {
        'bg': 'green gradient (dark to bright)', 'bg_pattern': 'gradient',
        'hair': 'black/dark brown', 'eyes': 'brown',
        'headwear': 'grey headband/visor',
        'accessories': '', 'clothing': 'burgundy/red top',
        'skin': 'light/pink', 'facial_hair': ''
    },

    # Additional LADs batch 2
    'lad_032_shaman-4': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black with streaks', 'eyes': 'covered by purple visor',
        'headwear': '',
        'accessories': 'purple visor/glasses', 'clothing': 'green and white and red checkered collar',
        'skin': 'light', 'facial_hair': 'grey scruff'
    },
    'lad_033_molecule-2': {
        'bg': 'grey/beige', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'dark blue/navy collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_035_JUAN': {
        'bg': 'bright green', 'bg_pattern': 'solid',
        'hair': 'black/brown', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white collar with dark blue suit',
        'skin': 'light/tan', 'facial_hair': 'black mustache'
    },
    'lad_036_x': {
        'bg': 'bright green/turquoise', 'bg_pattern': 'solid',
        'hair': 'white/cream large fluffy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_037_aressprout': {
        'bg': 'sage/grey-green', 'bg_pattern': 'solid',
        'hair': 'brown checkered/pixelated large', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_038_cashking-6': {
        'bg': 'blue-grey', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'white pixelated',
        'headwear': '',
        'accessories': '', 'clothing': 'colorful checkered collar (red, yellow, orange)',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_039_davinci-2': {
        'bg': 'tan/brown', 'bg_pattern': 'solid',
        'hair': 'black pixelated large', 'eyes': 'blue',
        'headwear': '',
        'accessories': 'pixelated effects around face', 'clothing': '',
        'skin': 'light/tan', 'facial_hair': ''
    },
    'lad_040_melzarmagic': {
        'bg': 'tan/brown', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'brown',
        'headwear': 'grey headband',
        'accessories': '', 'clothing': 'white and grey checkered collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_041_Maradona': {
        'bg': 'teal and blue and green striped', 'bg_pattern': 'striped',
        'hair': 'brown long curly', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white and blue checkered collar',
        'skin': 'light/tan', 'facial_hair': ''
    },
    'lad_043_jeremey': {
        'bg': 'gradient striped (blue, grey, orange, peach)', 'bg_pattern': 'gradient',
        'hair': 'brown/black', 'eyes': 'blue',
        'headwear': '',
        'accessories': '', 'clothing': 'grey and brown checkered collar',
        'skin': 'light/tan', 'facial_hair': ''
    },
    'lad_045_homewithkids3': {
        'bg': 'burgundy/red', 'bg_pattern': 'solid',
        'hair': 'cream/tan', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'colorful checkered collar (yellow, grey, pink, cyan)',
        'skin': 'light', 'facial_hair': 'brown beard'
    },
    'lad_046_NATE': {
        'bg': 'burgundy/red', 'bg_pattern': 'solid',
        'hair': 'dark blue/navy', 'eyes': 'grey/cyan',
        'headwear': '',
        'accessories': '', 'clothing': 'tan/beige checkered collar',
        'skin': 'light', 'facial_hair': 'grey scruff'
    },
    'lad_050_nate': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'blue and grey checkered collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_050_nate-2': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'brown', 'eyes': 'brown',
        'headwear': 'yellow and cyan checkered crown',
        'accessories': '', 'clothing': 'blue and grey checkered collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_051_DEVON-2': {
        'bg': 'burgundy/mauve', 'bg_pattern': 'solid',
        'hair': 'brown long', 'eyes': 'grey/cyan',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': 'brown beard'
    },
    'lad_051_DEVON-4': {
        'bg': 'purple', 'bg_pattern': 'solid',
        'hair': 'brown long', 'eyes': 'grey/cyan',
        'headwear': 'colorful pixelated crown (purple, yellow, cyan)',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': 'brown beard'
    },
    'lad_054_sterling': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'tan/brown messy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': 'brown beard'
    },
    'lad_054_sterlingglasses': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'tan/brown messy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': 'black glasses', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': 'brown beard'
    },
    'lad_054_sterlingglasses3withcrown5': {
        'bg': 'magenta/pink', 'bg_pattern': 'solid',
        'hair': 'tan/brown messy with green checkered crown', 'eyes': 'cyan/teal',
        'headwear': 'green checkered crown',
        'accessories': 'dark red/burgundy glasses, purple and yellow pixelated effects', 'clothing': '',
        'skin': 'light/pink', 'facial_hair': 'brown beard'
    },
    'lad_055_Luke': {
        'bg': 'cyan/turquoise gradient pixelated', 'bg_pattern': 'gradient',
        'hair': 'tan/blonde pixelated wavy', 'eyes': 'green',
        'headwear': '',
        'accessories': 'black cigarette holder', 'clothing': 'grey top',
        'skin': 'light', 'facial_hair': ''
    },

    # Additional LADs batch 3
    'lad_055_Luke10': {
        'bg': 'gradient pixelated (purple, cyan, green)', 'bg_pattern': 'gradient',
        'hair': 'tan/blonde pixelated wavy', 'eyes': 'green',
        'headwear': 'colorful pixelated crown (white, purple)',
        'accessories': '', 'clothing': 'grey top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_055_Luke3': {
        'bg': 'purple gradient', 'bg_pattern': 'gradient',
        'hair': 'tan/blonde pixelated wavy', 'eyes': 'green',
        'headwear': 'black hat',
        'accessories': '', 'clothing': 'grey top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_055_Luke6': {
        'bg': 'gradient pixelated (blue, cyan, green)', 'bg_pattern': 'gradient',
        'hair': 'tan/blonde pixelated wavy', 'eyes': 'purple/magenta pixelated',
        'headwear': 'purple pixelated hat/crown',
        'accessories': '', 'clothing': 'grey top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_055_Luke8': {
        'bg': 'gradient pixelated (purple, cyan, green)', 'bg_pattern': 'gradient',
        'hair': 'tan/blonde pixelated wavy', 'eyes': 'green',
        'headwear': 'orange pixelated mask/headwear',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_057_Hugh': {
        'bg': 'dark grey/black', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'green',
        'headwear': '',
        'accessories': '', 'clothing': 'dark blue/navy collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_057_Hugh5': {
        'bg': 'green, white, red split (Italian flag)', 'bg_pattern': 'split',
        'hair': 'brown wavy', 'eyes': 'white pixelated',
        'headwear': '',
        'accessories': '', 'clothing': 'dark blue/navy collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_058_SAVVA': {
        'bg': 'blue-grey', 'bg_pattern': 'solid',
        'hair': 'grey/tan pixelated', 'eyes': 'green',
        'headwear': '',
        'accessories': 'grey scruff', 'clothing': 'dark blue/navy collar',
        'skin': 'light', 'facial_hair': 'grey scruff'
    },
    'lad_059_SamAScientist': {
        'bg': 'cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'dark grey/black spiky pixelated', 'eyes': 'covered by blue visor',
        'headwear': '',
        'accessories': 'blue visor/glasses', 'clothing': 'white top',
        'skin': 'pale grey/white', 'facial_hair': ''
    },
    'lad_060_bhaitradingbot2': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'tan/yellow top',
        'skin': 'dark/brown', 'facial_hair': ''
    },
    'lad_061_DOPE7': {
        'bg': 'green', 'bg_pattern': 'solid',
        'hair': 'dark brown/burgundy', 'eyes': 'white pixelated',
        'headwear': '',
        'accessories': '', 'clothing': 'blue checkered collar',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_062_devox2': {
        'bg': 'burgundy/red', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'green/cyan',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': 'black beard'
    },
    'lad_063_kenichi': {
        'bg': 'red', 'bg_pattern': 'solid',
        'hair': 'black pixelated spiky', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white collar',
        'skin': 'light/tan', 'facial_hair': ''
    },
    'lad_064_Scott': {
        'bg': 'blue-grey', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white and grey checkered collar',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_064_sensei': {
        'bg': 'light grey/beige', 'bg_pattern': 'solid',
        'hair': 'grey', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'cyan/blue checkered collar',
        'skin': 'light/tan', 'facial_hair': ''
    },
    'lad_066_napoli2': {
        'bg': 'red', 'bg_pattern': 'solid',
        'hair': 'grey/dark checkered hat', 'eyes': 'covered by sunglasses',
        'headwear': 'grey/dark checkered fedora/hat',
        'accessories': 'gold earring', 'clothing': 'checkered collar (brown, grey, tan)',
        'skin': 'light', 'facial_hair': 'brown mustache'
    },
    'lad_068_mayor': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'brown afro large', 'eyes': 'covered by colorful visor',
        'headwear': '',
        'accessories': 'colorful pixelated visor/glasses (purple, blue, cyan)', 'clothing': '',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_070_IRAsBF2': {
        'bg': 'light grey', 'bg_pattern': 'solid',
        'hair': 'dark blue/black', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'gold earrings', 'clothing': 'colorful checkered collar (brown, blue, burgundy)',
        'skin': 'light/tan', 'facial_hair': ''
    },
    'lad_075_mmhm': {
        'bg': 'light purple', 'bg_pattern': 'solid',
        'hair': 'blonde/tan pixelated large wavy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': 'green pixelated flower/accessory', 'clothing': 'tan/brown top',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_078_btoshi': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'brown',
        'headwear': 'black hat with grey pixelated effects',
        'accessories': '', 'clothing': 'white collar',
        'skin': 'dark/brown', 'facial_hair': ''
    },
    'lad_079_ravish': {
        'bg': 'beige and red split', 'bg_pattern': 'split',
        'hair': 'black wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'tan/brown', 'facial_hair': ''
    },

    # Additional LADs batch 4 (final)
    'lad_080_fcpo': {
        'bg': 'orange', 'bg_pattern': 'solid',
        'hair': 'grey pixelated', 'eyes': 'blue/cyan',
        'headwear': '',
        'accessories': '', 'clothing': 'purple/lavender top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_081_iggy2': {
        'bg': 'tan/beige', 'bg_pattern': 'solid',
        'hair': 'grey/blue pixelated with visor', 'eyes': 'covered by visor',
        'headwear': '',
        'accessories': 'grey pixelated visor/headband, colorful checkered collar (green, cyan, yellow, red, magenta)', 'clothing': '',
        'skin': 'tan/brown', 'facial_hair': ''
    },
    'lad_086_Scooby': {
        'bg': 'blue-grey', 'bg_pattern': 'solid',
        'hair': 'brown curly', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'tan/brown top',
        'skin': 'light/pink', 'facial_hair': ''
    },
    'lad_087_HEEM': {
        'bg': 'tan/beige', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'brown',
        'headwear': 'colorful checkered hat/cap (grey, blue, cyan, orange)',
        'accessories': '', 'clothing': 'white and grey checkered collar',
        'skin': 'dark/brown', 'facial_hair': ''
    },
    'lad_088_Kareem': {
        'bg': 'dark grey', 'bg_pattern': 'solid',
        'hair': 'grey pixelated', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'white top',
        'skin': 'grey/pale', 'facial_hair': ''
    },
    'lad_089_aguda': {
        'bg': 'dark grey/black', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'white top',
        'skin': 'dark grey/black', 'facial_hair': ''
    },
    'lad_090_drscott': {
        'bg': 'orange', 'bg_pattern': 'solid',
        'hair': 'tan/brown pixelated', 'eyes': 'green',
        'headwear': '',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_091_amit': {
        'bg': 'light blue/lavender', 'bg_pattern': 'solid',
        'hair': 'grey/blue pixelated', 'eyes': 'pink/magenta pixelated',
        'headwear': '',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'brown/tan', 'facial_hair': ''
    },
    'lad_092_derrick': {
        'bg': 'blue-grey', 'bg_pattern': 'solid',
        'hair': 'tan/blonde pixelated curly', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'grey top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_093_photogee': {
        'bg': 'dark grey/black', 'bg_pattern': 'solid',
        'hair': 'black/grey', 'eyes': 'pink/magenta pixelated',
        'headwear': 'grey/white pixelated hat',
        'accessories': '', 'clothing': '',
        'skin': 'dark grey', 'facial_hair': ''
    },
    'lad_094_storm': {
        'bg': 'cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'orange/yellow',
        'headwear': '',
        'accessories': '', 'clothing': 'cyan checkered collar',
        'skin': 'dark/brown', 'facial_hair': ''
    },
    'lad_095_godfather': {
        'bg': 'dark grey', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'blue',
        'headwear': '',
        'accessories': '', 'clothing': 'white collar',
        'skin': 'brown/tan', 'facial_hair': ''
    },
    'lad_096_apollo': {
        'bg': 'cyan/turquoise', 'bg_pattern': 'solid',
        'hair': 'black large afro pixelated', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'colorful pixelated headband (white, blue, red, orange)', 'clothing': 'white and red checkered collar',
        'skin': 'dark/brown', 'facial_hair': ''
    },
    'lad_097_drralph': {
        'bg': 'light beige/white', 'bg_pattern': 'solid',
        'hair': 'brown curly', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'brown top',
        'skin': 'light', 'facial_hair': ''
    },
    'lad_098_Murtaza': {
        'bg': 'sage/grey-green', 'bg_pattern': 'solid',
        'hair': 'black', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'dark blue/navy top',
        'skin': 'tan/brown', 'facial_hair': ''
    },
    'lad_099_amenshiller': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black/brown', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white top',
        'skin': 'dark/brown', 'facial_hair': ''
    },
    'lad_102_bunya': {
        'bg': 'dark blue/navy', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': 'brown beard'
    },
    'lad_102_bunya2': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'facial_hair': 'brown beard'
    },
    'lad_102_bunya3': {
        'bg': 'dark blue/navy', 'bg_pattern': 'solid',
        'hair': 'brown wavy', 'eyes': 'covered by grey visor',
        'headwear': '',
        'accessories': 'grey visor/sunglasses', 'clothing': '',
        'skin': 'light', 'facial_hair': 'brown beard'
    },
    'lad_103_merheb': {
        'bg': 'light grey/beige', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'yellow/gold visor/headband', 'clothing': 'tan/brown checkered collar',
        'skin': 'dark/brown', 'facial_hair': 'black beard'
    },
    'lad_103_merheb2': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'brown/black', 'eyes': 'brown',
        'headwear': '',
        'accessories': 'yellow/gold visor/headband', 'clothing': 'tan/brown checkered collar',
        'skin': 'dark/brown', 'facial_hair': 'black beard'
    },
    'lad_74_lc': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black/grey', 'eyes': 'grey',
        'headwear': '',
        'accessories': '', 'clothing': 'white top',
        'skin': 'grey/dark', 'facial_hair': ''
    },

    # Additional LADIES batch
    'lady_059_paula-6': {
        'bg': 'green striped/gradient', 'bg_pattern': 'striped',
        'hair': 'brown checkered/pixelated wavy', 'eyes': 'covered by grey visor',
        'headwear': '',
        'accessories': 'grey/dark visor/sunglasses', 'clothing': 'blue and yellow checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_065_miggs': {
        'bg': 'purple and pink striped/gradient', 'bg_pattern': 'striped',
        'hair': 'green pixelated large checkered', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': '', 'clothing': 'blue top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_080_zesty_lime': {
        'bg': 'grey', 'bg_pattern': 'solid',
        'hair': 'black wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_085_IRA2': {
        'bg': 'red', 'bg_pattern': 'solid',
        'hair': 'blonde/tan wavy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': 'white pixelated wings/effects, gold necklace', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_086_ELENI9': {
        'bg': 'tan/beige', 'bg_pattern': 'solid',
        'hair': 'black/brown wavy', 'eyes': 'blue',
        'headwear': '',
        'accessories': 'pink veil/headscarf pixelated', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_087_feybirthday5': {
        'bg': 'beige with pixelated elements', 'bg_pattern': 'solid',
        'hair': 'black/brown wavy', 'eyes': 'grey',
        'headwear': '',
        'accessories': 'pixelated colorful elements (yellow, blue, green, brown, magenta)', 'clothing': 'purple top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_088_r': {
        'bg': 'orange', 'bg_pattern': 'solid',
        'hair': 'brown checkered/pixelated wavy', 'eyes': 'cyan/teal',
        'headwear': '',
        'accessories': 'burgundy/dark red visor/glasses', 'clothing': 'white and blue/red checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_090_missthang': {
        'bg': 'light grey/beige', 'bg_pattern': 'solid',
        'hair': 'black/brown wavy', 'eyes': 'green',
        'headwear': '',
        'accessories': 'yellow earrings', 'clothing': 'blue checkered collar',
        'skin': 'light/tan', 'lips': 'pink'
    },
    'lady_094_violetta': {
        'bg': 'split (beige, burgundy, green, grey-blue)', 'bg_pattern': 'split',
        'hair': 'black wavy long', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white and yellow checkered collar',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_095_royalty': {
        'bg': 'grey and beige split with pixelated elements', 'bg_pattern': 'split',
        'hair': 'brown wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'pink top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_096_yuri': {
        'bg': 'grey/mauve', 'bg_pattern': 'solid',
        'hair': 'purple pixelated large', 'eyes': 'yellow/cream pixelated',
        'headwear': '',
        'accessories': 'magenta pixelated accessory', 'clothing': 'white and red checkered collar',
        'skin': 'pale/white', 'lips': 'pink'
    },
    'lady_097_dani': {
        'bg': 'light purple', 'bg_pattern': 'solid',
        'hair': 'black/grey pixelated wavy', 'eyes': 'brown',
        'headwear': '',
        'accessories': '', 'clothing': 'white and brown checkered collar',
        'skin': 'tan/brown', 'lips': 'pink'
    },
    'lady_097_dani2': {
        'bg': 'sage/grey-green', 'bg_pattern': 'solid',
        'hair': 'brown pixelated wavy', 'eyes': 'grey',
        'headwear': '',
        'accessories': 'orange/yellow accessory, grey/white earrings', 'clothing': 'grey top',
        'skin': 'brown/tan', 'lips': 'pink'
    },
    'lady_098_heyeah': {
        'bg': 'purple', 'bg_pattern': 'solid',
        'hair': 'brown wavy long', 'eyes': 'covered by black sunglasses',
        'headwear': '',
        'accessories': 'black sunglasses', 'clothing': 'grey top',
        'skin': 'light', 'lips': 'pink'
    },
    'lady_099_VQ': {
        'bg': 'blue', 'bg_pattern': 'solid',
        'hair': 'yellow/blonde pixelated large wavy', 'eyes': 'covered by white glasses',
        'headwear': '',
        'accessories': 'white pixelated glasses/visor', 'clothing': '',
        'skin': 'light', 'lips': 'pink'
    },
}

# I'll continue adding more as I review them...
# This is just the starter template

if __name__ == "__main__":
    print(f"Currently documented: {len(ACCURATE_DATA)} images")
    print(f"Remaining: {193 - len(ACCURATE_DATA)} images")
