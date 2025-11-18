#!/usr/bin/env python3
"""
Script to insert missing punk prompts into FREEPIK_PROMPTS.md
"""

# New prompts to insert
new_prompts = {
    "lad_023_x-2": """### lad_023_x-2
**Style: Pixel art environment**
Miniature pixel art carnival diorama bathed in gradient turquoise and mint green twilight with grey hair wisps and multicolored crown jewels, geometric 8-bit festival patterns creating playful atmosphere, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with pixelated edges blurring into celebration mystery, dream-logic scale where single confetti is floating banner, liminal space between festivity and calm, shadow puppet theater depth with layered pixel decorations, folkloric tale of the joyful wanderer, mythological shadow play in festive realm, ancient legend celebrated in aqua light, ethereal ghostly party glow, small-scale carnival magic with visible pixel grid, handbuilt celebration aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift festive, 16:9
""",
    "lad_023_x-3": """### lad_023_x-3
**Style: Pixel art environment**
Miniature pixel art festival diorama bathed in gradient turquoise and mint green twilight with grey wisps and vibrant crown jewels in blue, pink, and yellow, geometric 8-bit celebration patterns creating joyful atmosphere, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with pixelated edges blurring into festive mystery, dream-logic scale where crown jewel is entire monument, liminal space between party and peace, shadow puppet theater depth with layered pixel ornaments, folkloric tale of the crowned one, mythological shadow play in celebration realm, ancient legend adorned in mint light, ethereal ghostly festive glow, small-scale jubilation magic with visible pixel grid, handbuilt party aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift joyful, 16:9
""",
    "lad_023_x-4": """### lad_023_x-4
**Style: Pixel art environment**
Miniature pixel art celebration diorama bathed in gradient turquoise and bright green twilight with grey textures and pure white crown accents, geometric 8-bit jubilee patterns creating pristine atmosphere, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth with pixelated edges blurring into ceremonial mystery, dream-logic scale where white crown is palace spire, liminal space between honor and play, shadow puppet theater depth with layered pixel regalia, folkloric tale of the noble spirit, mythological shadow play in aqua realm, ancient legend crowned in green light, ethereal ghostly ceremonial glow, small-scale regal magic with visible pixel grid, handbuilt celebration aesthetic, no realistic faces or characters, abstract atmospheric world only, tilt-shift noble, 16:9
""",
}

# Read the file
with open('bespoke-punks-website/FREEPIK_PROMPTS.md', 'r') as f:
    content = f.read()

# Find where to insert lad_023_x-2 (after lad_023_x)
import re

# Insert after lad_023_x
pattern = r'(### lad_023_x\n\*\*Style:.*?\ntilt-shift.*?, 16:9\n)'
match = re.search(pattern, content, re.DOTALL)
if match:
    insert_point = match.end()
    content = content[:insert_point] + '\n' + new_prompts["lad_023_x-2"] + content[insert_point:]
    print("Inserted lad_023_x-2")

# Insert lad_023_x-3 after lad_023_x-2
pattern = r'(### lad_023_x-2\n\*\*Style:.*?\ntilt-shift.*?, 16:9\n)'
match = re.search(pattern, content, re.DOTALL)
if match:
    insert_point = match.end()
    content = content[:insert_point] + '\n' + new_prompts["lad_023_x-3"] + content[insert_point:]
    print("Inserted lad_023_x-3")

# Insert lad_023_x-4 after lad_023_x-3
pattern = r'(### lad_023_x-3\n\*\*Style:.*?\ntilt-shift.*?, 16:9\n)'
match = re.search(pattern, content, re.DOTALL)
if match:
    insert_point = match.end()
    content = content[:insert_point] + '\n' + new_prompts["lad_023_x-4"] + content[insert_point:]
    print("Inserted lad_023_x-4")

# Write back
with open('bespoke-punks-website/FREEPIK_PROMPTS.md', 'w') as f:
    f.write(content)

print("Done inserting prompts!")
