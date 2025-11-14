#!/usr/bin/env python3
"""
Create character-specific world prompts for all 174 Bespoke Punks
Manually curated visual descriptions based on actual punk images
"""

# Visual trait mappings based on actual punk analysis
PUNK_TRAITS = {
    # LADS
    "lad_001_carbon": "dark gray cap with graphic, brown skin, serious expression",
    "lad_002_cash": "silver/white wild hair, pale skin, futuristic cyberpunk vibe, black suit",
    "lad_003_chai": "white fluffy curly hair, brown skin, green plaid shirt, warm cozy vibe",
    "lad_004_silicon": "gray messy hair, very pale skin, monochrome tech aesthetic",
    "lad_005_copper": "brown hair, light skin, surrounded by golden copper sparks and particles",
    "lad_006_redshift": "dark blue wavy hair, light skin, blue eyes, calm expression",
    "lad_007_titanium": "dark brown hair, light skin, industrial worker aesthetic",
    "lad_008_platinum": "dark messy hair with beard, light skin, robotic/cyborg elements visible",
    "lad_009_steel": "gray/silver hair, headband, rugged industrial worker in blue",
    "lad_010_aluminum": "bright red cap/bandana, brown skin, orange outfit, vibrant energy",
    "lad_011_chocolate": "dark hair with orange bow tie accent, brown skin, sweet shop vibes",
    "lad_012_chromium": "silver/chrome spiky hair, very pale skin, blue eyes, futuristic",
    "lad_013_caramel": "white/cream fluffy hair, brown skin, green checkered shirt",
    "lad_014_sugar": "light gray hair, pale skin, crystalline delicate aesthetic",
    "lad_015_jackson": "silver/gray short hair, athletic build, sporty casual wear",
    "lad_016_tungsten": "gray messy hair, pale skin, inventor/scientist look with goggles vibe",
    "lad_017_ink": "silver/white messy hair, pale skin, black outfit, monochrome artist",
    "lad_018_mandarin": "dark hair, orange headband/cap, tan skin, Asian-inspired outfit",
    "lad_019_diamond": "mixed blonde/brown hair, light skin, crystalline shimmer",
    "lad_020_gpu": "blonde/golden tousled hair, light skin, tech worker casual style",
    "lad_021_x": "abstract green-tinted form, mysterious undefined features",
    "lad_022_x": "abstract green-tinted form, map explorer aesthetic",
    "lad_023_x": "abstract mixed forms emerging, clay-like metamorphosis",
    "lad_025_x": "minimal abstract paper figure, white/blank aesthetic",
    "lad_026_chromiumabstractsalmon": "chrome and salmon pink abstract artist",
    "lad_027_chromiumabstractyellow": "chrome and gold abstract seeker",
    "lad_028_chromiumabstractgreen": "chrome and green abstract scientist",
    "lad_029_famous-9": "paparazzi with camera, celebrity culture aesthetic",
    "lad_030_ink": "dark monochrome figure, ink artist emerging from liquid",
    "lad_031_fin": "diver with dark hair, underwater explorer aesthetic",
    "lad_032_shaman-4": "mystical shaman, tribal ritual aesthetic",
    "lad_033_molecule-2": "scientist in lab coat, molecular discovery moment",
    "lad_035_JUAN": "Latin American street figure, cultural distinctive features",
    "lad_036_x": "digital consciousness forming, pixelated birth",
    "lad_037_aressprout": "peace advocate, war garden observer",
    "lad_038_cashking-6": "jester/fool with playful features, gold and money",
    "lad_039_davinci-2": "Renaissance man with beard, inventor sketching",
    "lad_040_melzarmagic": "wizard with robes and pointed hat, magical artifacts",
    "lad_041_Maradona": "wild brown curly hair, athletic soccer player in blue and white",
    "lad_043_jeremey": "professional office worker, startup entrepreneur",
    "lad_045_homewithkids3": "family home setting, domestic warmth",
    "lad_046_NATE": "urban Brooklyn style, late-night worker",
    "lad_049_gainzyyyy12": "muscular gym figure, fitness dedication",
    "lad_050_nate-2": "urban explorer with flashlight, subway adventurer",
    "lad_051_DEVON-4": "tech entrepreneur, Silicon Valley garage startup",
    "lad_054_sterlingglasses3withcrown5": "green/yellow hair, red-framed glasses, golden crown, regal scholar",
    "lad_055_Luke8": "brown wavy hair, film production crew aesthetic",
    "lad_057_Hugh5": "reddish-brown hair, English countryside gardener",
    "lad_057_Hughx": "brown hair, British pub patron",
    "lad_058_SAVVA": "Eastern European architectural historian",
    "lad_059_SamAScientist": "scientist in white lab coat, breakthrough discovery",
    "lad_060_bhaitradingbot2": "focused trader, financial markets analyst",
    "lad_061_DOPE10": "hip-hop producer, urban music studio",
    "lad_061_DOPE7": "urban B-boy, 90s hip-hop culture",
    "lad_062_devox2": "developer with glasses, late-night coding",
    "lad_063_kenichi": "Japanese zen practitioner, meditation aesthetic",
    "lad_064_Scott": "American diner patron, Route 66 traveler",
    "lad_064_sensei": "martial arts student, dojo discipline",
    "lad_066_napoli2": "Italian pizzeria chef, Mediterranean warmth",
    "lad_068_mayor": "distinguished city hall official, leadership presence",
    "lad_070_IRAsBF2": "romantic dinner date, intimate rooftop setting",
    "lad_075_mmhm": "relaxed lounge figure, chill vibes",
    "lad_078_btoshi": "crypto miner, blockchain tech explorer",
    "lad_079_ravish": "Bollywood cultural performer, Indian celebration",
    "lad_080_fcpo": "detective with serious expression, case solver",
    "lad_081_iggy2": "punk rocker with wild hair, energetic stage presence",
    "lad_086_Scooby": "brown messy hair, mystery detective with loyal dog",
    "lad_087_HEEM": "street basketball player, athletic urban setting",
    "lad_088_Kareem": "tall athletic basketball player, legendary shot",
    "lad_089_aguda": "African tribal figure with cultural features, savanna setting",
    "lad_090_drscott": "doctor in white coat, medical breakthrough",
    "lad_091_amit": "Indian marketplace merchant, entrepreneurial spirit",
    "lad_092_derrick": "construction worker with hard hat, engineering marvel",
    "lad_093_photogee": "photographer with camera, capturing impossible moments",
    "lad_094_storm": "powerful figure controlling lightning, superhero energy",
    "lad_095_godfather": "distinguished Italian mafia figure, 1940s noir",
    "lad_096_apollo": "NASA mission control, space exploration excitement",
    "lad_097_drralph": "surgeon with steady hands, medical precision",
    "lad_098_Murtaza": "Pakistani scholar with traditional features, calligraphy wisdom",
    "lad_099_amenshiller": "reverent praying figure, cathedral sacred space",
    "lad_102_bunya3": "Aboriginal Australian with cultural features, ancient rock art",
    "lad_103_merheb3": "Middle Eastern spice merchant, bazaar alchemy",
    "lad_105_inkspired": "artistic figure emerging from ink, calligraphy magic",
    "lad_106_sultan": "regal sultan with turban, treasure map discovery",
    "lad_74_lc": "California skateboarder, Los Angeles palm boulevard freedom",

    # LADIES
    "lady_000_lemon": "red and white checkered bandana, citrus grove harvester",
    "lady_001_hazelnut": "brown forest tones, woodland mouse-like delicate features",
    "lady_002_vanilla": "pale cream features, delicate fairy-like presence",
    "lady_003_cashew": "warm brown skin tones, tropical harvest energy",
    "lady_004_nutmeg": "warm features, spice market aromatic presence",
    "lady_005_cinnamon": "warm brown tones, grandmother baker with apron",
    "lady_010_saffron": "golden elegant features, Persian textile weaver",
    "lady_011_sage": "wise healer features, herbal apothecary garden",
    "lady_012_parasite": "concerned scientist, greenhouse botanical researcher",
    "lady_013_rosemary": "elderly wise features, Mediterranean hillside herbalist",
    "lady_014_olive": "Mediterranean family features, ancient olive grove",
    "lady_015_lime": "vibrant fresh energy, tropical bartender mixing magic",
    "lady_016_honey": "golden beekeeper features, honeycomb fractal observer",
    "lady_017_pine": "woodland creature features, evergreen forest gathering",
    "lady_018_strawberry": "innocent child features climbing giant fruit, Alice in Wonderland scale",
    "lady_020_blood": "dark flowing hair, gothic crimson moon ritual figure",
    "lady_021_diamond": "determined miner features, crystalline treasure seeker",
    "lady_022_gold": "adventurous treasure hunter, ancient vault explorer",
    "lady_023_silver": "delicate artisan features, moonlight metalwork crafter",
    "lady_024_linen": "skilled weaver features, textile destiny reader",
    "lady_025_mistletoe": "winter romantic features, Druid magic blessing",
    "lady_026_fur": "fashionable shopper features, boutique metamorphosis witness",
    "lady_027_nitrogen": "shocked scientist features, cryogenic awakening observer",
    "lady_028_marshmallow": "sweet factory worker features, cloud levitation witness",
    "lady_029_basil": "Italian nonna features with warm hands, herbal kitchen magic",
    "lady_030_grass": "meadow observer, UFO crop circle witness",
    "lady_031_paprika": "mystical fortune teller features, Hungarian spice divination",
    "lady_032_salt": "contemplative pilgrim features, crystal desert labyrinth walker",
    "lady_033_staranise": "traditional tea master features, Asian five-pointed balance",
    "lady_034_lavender": "peaceful Provence features, purple field trance walker",
    "lady_035_turmeric": "Indian spiritual features with third eye, golden bazaar healer",
    "lady_037_rose": "elegant gardener features, romantic black rose tender",
    "lady_038_peanut": "rural farmer features, American county fair innovation",
    "lady_039_sandalwood": "spiritual devotee features, Indian temple incense visions",
    "lady_040_fivespice": "traditional Chinese herbalist features, five elements alchemist",
    "lady_041_bayleaf": "Mediterranean grandmother features stirring pot, steam visions",
    "lady_042_almond": "romantic lover features, blossom storm beauty",
    "lady_043_orange": "sun-kissed picker features, perpetual harvest abundance",
    "lady_044_x": "abstract explorer features, impossible maze puzzle solver",
    "lady_045_x": "abstract emerging features, void consciousness birth",
    "lady_046_x": "undefined explorer features, parallel dimension jumper",
    "lady_047_x": "minimal paper features, void space isolation",
    "lady_048_pink": "delicate fairy features with pink tones, flower ring dancer",
    "lady_049_abstractangels": "awestruck human features, angelic message receiver",
    "lady_050_x-6": "glitch features reaching toward code, simulation awakening",
    "lady_051_rosieabstract": "creative artist features, rose decay/beauty cycle painter",
    "lady_052_pinksilkabstract": "flowing surfer features, silk wave time suspension",
    "lady_053_pepperabstract": "focused astronomer features, pepper constellation mapper",
    "lady_055_bloodabstract": "dark mysterious cultist features, crimson sigil summoner",
    "lady_056_alloyabstract": "innovative scientist features, metal fusion alchemist",
    "lady_057_bluesilkabstract": "adventurous sailor features, blue silk water realm traveler",
    "lady_058_x": "sophisticated curator features, self-creating art gallery",
    "lady_059_paula-5": "creative artist features in awe, brush painting through muse",
    "lady_060_winehouse": "dark wavy hair with red rose accent, glowing jazz singer spirit",
    "lady_061_nikkkk-2": "fashionable model features, runway outfit metamorphosis",
    "lady_062_Dalia-2": "elegant Middle Eastern features, night garden wish maker",
    "lady_062_Dalia-BD": "celebratory birthday features, impossible wish magic moment",
    "lady_063_PVR-3": "amazed audience features, movie theater self-watching",
    "lady_064_aubree-2": "graceful dancer features, ballet ghost mimicry",
    "lady_065_miggs-4": "focused producer features, perfect take recording witness",
    "lady_065_miggs": "producer with headphones feeling energy, healing frequency creator",
    "lady_066_monalisa-3": "brown wavy hair, museum guard witnessing painting change",
    "lady_067_salamander-2": "curious seeker features, swamp salamander guide follower",
    "lady_068_nikkisf-4": "urban San Francisco passenger features, fog cable car rider",
    "lady_069_giulia": "Italian vintner features, vineyard goddess symbol discoverer",
    "lady_070_mango": "tropical picker features with overflowing basket, golden paradise",
    "lady_071_papaya": "island merchant features, papaya seed future reader",
    "lady_072_tangerine": "wondering astronomer features, citrus constellation mapper",
    "lady_073_mango_punk": "cyberpunk hacker features, tech-fruit augmented reality",
    "lady_074_melon": "mystical fortune teller features, watermelon seed diviner",
    "lady_075_clementine": "ancient druid features, fairy ring citrus grove tender",
    "lady_076_orange_blossom": "loving couple features, eternal spring tree meeting point",
    "lady_077_pink_grapefruit": "scientific botanist features, impossible hybrid fruit examiner",
    "lady_078_orange_zest": "microscopic explorer features living in cellular awareness",
    "lady_079_lime_breeze": "relaxed beach bar patron features, eternal cocktail drinker",
    "lady_080_zesty_lime": "vibrant splash-born features, conscious lime liquid being",
    "lady_083_Marianne3": "romantic French cafe features, fated lovers approaching",
    "lady_085_IRA2": "loving couple features embracing, guardian angel protected",
    "lady_086_ELENI9": "Greek island villager features, ancient temple light walker",
    "lady_087_feybirthday5": "joyful birthday features, fairy godmother granting wishes",
    "lady_088_r": "contemplative philosopher features, letter R reality shifter",
    "lady_090_missthang": "fierce model features growing butterfly wings, haute couture metamorphosis",
    "lady_094_violetta": "dark elegant features sleeping in purple bloom, vampire orchid beauty",
    "lady_095_royalty": "regal bearing with black hair and red accent crown, true heir arriving",
    "lady_096_yuri": "serene monk features, Japanese zen garden koan solver",
    "lady_097_dani": "urban gardener features amazed, rooftop jungle overnight growth",
    "lady_097_dani2": "contemplative urban features, parallel city portal stepper",
    "lady_098_heyeah": "energetic conductor features, concert crowd unity channeler",
    "lady_099_domino": "strategic features trying to stop fate, eternal cascade observer",
    "lady_099_VQ": "blonde hair with white-framed glasses, VIP lounge list checker, exclusive bouncer presence",
}

# Original prompts template
ORIGINAL_PROMPTS = {
    "lad_001_carbon": "Handbuilt carbon fiber city miniature with tiny figure in trench coat walking alone, neon-lit alley with visible model seams, mysterious fog from dry ice, Burton-esque exaggerated proportions, Laika Studios tactile craftsmanship, tilt-shift photography showing scale, 16:9",
    # ... (continuing with all 174 prompts)
}

def enhance_prompt(punk_name, original_prompt, traits):
    """
    Enhance a prompt by adding character-specific visual details
    """
    # Insert character description into the prompt
    # Find where to insert (usually after first description of setting)

    if "tiny figure" in original_prompt:
        enhanced = original_prompt.replace(
            "tiny figure",
            f"tiny figure ({traits})"
        )
    elif "miniature figure" in original_prompt:
        enhanced = original_prompt.replace(
            "miniature figure",
            f"miniature figure ({traits})"
        )
    elif "tiny" in original_prompt and "figure" in original_prompt:
        # More complex insertion needed
        enhanced = original_prompt
    else:
        enhanced = original_prompt

    return enhanced

if __name__ == "__main__":
    print("Character traits defined for", len(PUNK_TRAITS), "punks")
    print("\nSample enhancements:")
    for punk_name in list(PUNK_TRAITS.keys())[:5]:
        print(f"\n{punk_name}: {PUNK_TRAITS[punk_name]}")
