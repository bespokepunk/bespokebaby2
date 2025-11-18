#!/usr/bin/env python3
"""
Script to insert all remaining missing punk prompts into FREEPIK_PROMPTS.md
"""

import re

# Define all prompts that need to be inserted with their anchor points
prompts_to_insert = [
    # After lad_028
    ("lad_029_famous-9", "lad_028", """### lad_029_famous-9
**Style: Claymation**
Miniature clay street corner diorama bathed in vibrant royal blue with multicolored rainbow visor creating neon energy, scattered orange collar accents and urban textures, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating bold street atmosphere, dream-logic scale where visor fragment is prism tower, liminal space between fame and sidewalk, shadow puppet theater depth with layered building shadows, folkloric tale of the street legend, mythological shadow play across blue walls, ancient legend told in rainbow light, ethereal ghostly neon pulse, small-scale urban fame magic with visible clay texture, handbuilt street style aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift electric, 16:9
"""),

    # After lad_029_famous-9 (will be inserted dynamically)
    ("lad_029_famous4", "lad_029_famous-9", """### lad_029_famous4
**Style: Claymation**
Miniature clay street corner diorama bathed in warm golden tan background with vibrant neon green visor creating retro street energy, scattered orange collar accents, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating bold 80s atmosphere, dream-logic scale where visor is neon monument, liminal space between fame and fortune, shadow puppet theater depth with layered urban shadows, folkloric tale of the icon, mythological shadow play across tan walls, ancient legend told in green light, ethereal ghostly neon glow, small-scale fame magic with visible clay texture, handbuilt retro aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift iconic, 16:9
"""),

    # After lad_031
    ("lad_032_shaman-4", "lad_031", """### lad_032_shaman-4
**Style: Miniature diorama stop-motion**
Miniature mystical chamber diorama bathed in soft grey twilight with lavender purple shades and deep red ceremonial accents, scattered ritual objects and smoky purple wisps, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating sacred mystery, dream-logic scale where incense smoke is spirit cloud, liminal space between worlds and wisdom, shadow puppet theater depth with layered shadow ceremonies, folkloric tale of the spirit walker, mythological shadow play across temple stone, ancient legend whispered in purple mist, ethereal ghostly ritual glow, small-scale shamanic magic with visible handbuilt textures, handcrafted sacred aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift mystical, 16:9
"""),

    # After lad_032_shaman-4
    ("lad_033_molecule-2", "lad_032_shaman-4", """### lad_033_molecule-2
**Style: Papercraft diorama**
Minimalist paper laboratory diorama bathed in soft grey twilight with clean lines and scientific precision, scattered geometric paper molecules and structural diagrams, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating analytical serenity, dream-logic scale where molecule is architectural sculpture, liminal space between science and art, shadow puppet theater depth with layered geometric formulas, folkloric tale of the builder, mythological shadow play in molecular realm, ancient legend coded in structure, ethereal ghostly lab glow, small-scale scientific magic with visible paper folds, handbuilt minimalist aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift precise, 16:9
"""),

    # After lad_034
    ("lad_035_JUAN", "lad_034", """### lad_035_JUAN
**Style: Claymation**
Miniature clay plaza diorama bathed in vibrant mint green atmosphere with warm terracotta skin tones and navy blue accents, scattered clay architectural elements creating casual urban energy, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating friendly street magic, dream-logic scale where streetlamp is beacon tower, liminal space between neighborhood and adventure, shadow puppet theater depth with layered plaza shadows, folkloric tale of the good neighbor, mythological shadow play across green walls, ancient legend shared in mint light, ethereal ghostly warm glow, small-scale community magic with visible clay texture, handbuilt friendly aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift welcoming, 16:9
"""),

    # After lad_037
    ("lad_038_cashking-6", "lad_037", """### lad_038_cashking-6
**Style: Pixel art environment**
Miniature pixel art vault diorama bathed in soft grey blue with bold black and orange accents creating financial district energy, geometric 8-bit currency patterns and digital wealth symbols, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with pixelated edges blurring into monetary mystery, dream-logic scale where coin is golden monument, liminal space between wealth and wisdom, shadow puppet theater depth with layered pixel finances, folkloric tale of the money master, mythological shadow play in digital vault, ancient legend minted in grey light, ethereal ghostly prosperity glow, small-scale wealth magic with visible pixel grid, handbuilt financial aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift prosperous, 16:9
"""),

    # After lad_038_cashking-6
    ("lad_039_davinci-2", "lad_038_cashking-6", """### lad_039_davinci-2
**Style: Papercraft diorama**
Miniature paper museum diorama bathed in warm golden tan twilight with deep blue ocean sky creating Renaissance atmosphere, scattered paper artworks and sketches in layered earth tones, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating artistic contemplation, dream-logic scale where single sketch is fresco wall, liminal space between vision and creation, shadow puppet theater depth with layered easel shadows, folkloric tale of the master artist, mythological shadow play across studio walls, ancient legend painted in golden light, ethereal ghostly creative glow, small-scale Renaissance magic with visible paper folds, handbuilt artistic aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift masterful, 16:9
"""),

    # After lad_040
    ("lad_041_Maradona", "lad_040", """### lad_041_Maradona
**Style: Claymation**
Miniature clay soccer field diorama bathed in bright blue sky with emerald green grass and white checkered details, scattered clay soccer equipment creating athletic magic, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating stadium energy, dream-logic scale where soccer ball is legendary orb, liminal space between game and glory, shadow puppet theater depth with layered field shadows, folkloric tale of the foot artist, mythological shadow play across pitch, ancient legend dribbled in blue light, ethereal ghostly championship glow, small-scale athletic legend magic with visible clay texture, handbuilt sports aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift legendary, 16:9
"""),

    # After lad_042
    ("lad_043_jeremey", "lad_042", """### lad_043_jeremey
**Style: Miniature diorama stop-motion**
Miniature sunset apartment diorama bathed in layered horizontal stripes of grey blue, cream, peach, and orange creating 70s retro atmosphere, scattered geometric shapes and vintage elements, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating nostalgic warmth, dream-logic scale where single stripe is entire horizon, liminal space between decades and dreams, shadow puppet theater depth with layered sunset bands, folkloric tale of the time traveler, mythological shadow play in retro realm, ancient legend painted in sunset bands, ethereal ghostly vintage glow, small-scale 70s magic with visible handbuilt textures, handcrafted groovy aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift nostalgic, 16:9
"""),

    # After lad_044
    ("lad_045_homewithkids3", "lad_044", """### lad_045_homewithkids3
**Style: Pixel art environment**
Miniature pixel art nursery diorama bathed in warm dusty rose background with cream hat accents and pastel yellow details, geometric 8-bit toy patterns creating innocent atmosphere, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with pixelated edges blurring into childhood mystery, dream-logic scale where toy block is castle tower, liminal space between play and peace, shadow puppet theater depth with layered pixel toys, folkloric tale of the gentle soul, mythological shadow play in nursery realm, ancient legend cradled in rose light, ethereal ghostly lullaby glow, small-scale wholesome magic with visible pixel grid, handbuilt innocent aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift gentle, 16:9
"""),

    # After lad_045_homewithkids3
    ("lad_046_NATE", "lad_045_homewithkids3", """### lad_046_NATE
**Style: Claymation**
Miniature clay street diorama bathed in deep burgundy red with dark navy blue and white accents creating bold urban energy, scattered checkered patterns and vintage textures, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating classic street magic, dream-logic scale where checkerboard is city plaza, liminal space between heritage and hustle, shadow puppet theater depth with layered urban shadows, folkloric tale of the street wise, mythological shadow play across red walls, ancient legend told in burgundy light, ethereal ghostly classic glow, small-scale vintage urban magic with visible clay texture, handbuilt timeless aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift classic, 16:9
"""),
]

# Read the current file
with open('bespoke-punks-website/FREEPIK_PROMPTS.md', 'r') as f:
    content = f.read()

# Insert prompts in order
for punk_name, after_punk, prompt_text in prompts_to_insert:
    # Find the anchor punk entry
    pattern = rf'(### {re.escape(after_punk)}\n\*\*Style:.*?tilt-shift.*?, 16:9\n)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_point = match.end()
        content = content[:insert_point] + '\n' + prompt_text + content[insert_point:]
        print(f"✓ Inserted {punk_name} after {after_punk}")
    else:
        print(f"✗ Could not find anchor {after_punk} for {punk_name}")

# Write back the modified content
with open('bespoke-punks-website/FREEPIK_PROMPTS.md', 'w') as f:
    f.write(content)

print("\nFirst batch complete! Now run the second batch script...")
