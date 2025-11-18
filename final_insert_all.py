#!/usr/bin/env python3
"""
Final comprehensive script to insert ALL remaining 52 punk prompts
Uses the prompts generated earlier in the conversation
"""

import re

# All remaining prompts with full text
ALL_PROMPTS = {
    "lad_029_famous-9": ("""### lad_029_famous-9
**Style: Claymation**
Miniature clay street corner diorama bathed in vibrant royal blue with multicolored rainbow visor creating neon energy, scattered orange collar accents and urban textures, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating bold street atmosphere, dream-logic scale where visor fragment is prism tower, liminal space between fame and sidewalk, shadow puppet theater depth with layered building shadows, folkloric tale of the street legend, mythological shadow play across blue walls, ancient legend told in rainbow light, ethereal ghostly neon pulse, small-scale urban fame magic with visible clay texture, handbuilt street style aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift electric, 16:9
""", "lad_029_famous"),

    "lad_029_famous4": ("""### lad_029_famous4
**Style: Claymation**
Miniature clay street corner diorama bathed in warm golden tan background with vibrant neon green visor creating retro street energy, scattered orange collar accents, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating bold 80s atmosphere, dream-logic scale where visor is neon monument, liminal space between fame and fortune, shadow puppet theater depth with layered urban shadows, folkloric tale of the icon, mythological shadow play across tan walls, ancient legend told in green light, ethereal ghostly neon glow, small-scale fame magic with visible clay texture, handbuilt retro aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift iconic, 16:9
""", "lad_029_famous-9"),

    "lad_032_shaman-4": ("""### lad_032_shaman-4
**Style: Miniature diorama stop-motion**
Miniature mystical chamber diorama bathed in soft grey twilight with lavender purple shades and deep red ceremonial accents, scattered ritual objects and smoky purple wisps, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating sacred mystery, dream-logic scale where incense smoke is spirit cloud, liminal space between worlds and wisdom, shadow puppet theater depth with layered shadow ceremonies, folkloric tale of the spirit walker, mythological shadow play across temple stone, ancient legend whispered in purple mist, ethereal ghostly ritual glow, small-scale shamanic magic with visible handbuilt textures, handcrafted sacred aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift mystical, 16:9
""", "lad_032_shaman"),

    "lad_033_molecule-2": ("""### lad_033_molecule-2
**Style: Papercraft diorama**
Minimalist paper laboratory diorama bathed in soft grey twilight with clean lines and scientific precision, scattered geometric paper molecules and structural diagrams, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating analytical serenity, dream-logic scale where molecule is architectural sculpture, liminal space between science and art, shadow puppet theater depth with layered geometric formulas, folkloric tale of the builder, mythological shadow play in molecular realm, ancient legend coded in structure, ethereal ghostly lab glow, small-scale scientific magic with visible paper folds, handbuilt minimalist aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift precise, 16:9
""", "lad_033_molecule"),
}

# Read file
with open('bespoke-punks-website/FREEPIK_PROMPTS.md', 'r') as f:
    content = f.read()

# Insert each prompt after its anchor
count = 0
for punk_name, (prompt_text, anchor) in ALL_PROMPTS.items():
    pattern = rf'(### {re.escape(anchor)}\n\*\*Style:.*?tilt-shift.*?, 16:9\n)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_point = match.end()
        content = content[:insert_point] + '\n' + prompt_text + content[insert_point:]
        print(f"✓ {count+1}/4: Inserted {punk_name}")
        count += 1
    else:
        print(f"✗ Could not find anchor '{anchor}' for {punk_name}")

# Write back
with open('bespoke-punks-website/FREEPIK_PROMPTS.md', 'w') as f:
    f.write(content)

print(f"\nInserted {count}/4 prompts in this batch")
print("Note: Due to size limits, need to run multiple batches")
