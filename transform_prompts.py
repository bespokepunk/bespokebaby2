#!/usr/bin/env python3
"""
Transform Bespoke Punks prompts into MAGNIFICENT, DREAMY, BREATHTAKING worlds
Inspired by: Wes Anderson, Coraline, James and the Giant Peach, Isle of Dogs,
Fantastic Mr. Fox, The Grand Budapest Hotel
"""

import re
import os
from PIL import Image
from collections import Counter

def extract_colors_from_png(png_path):
    """Extract dominant colors from PNG file"""
    try:
        img = Image.open(png_path)
        img = img.convert('RGB')
        pixels = list(img.getdata())

        # Get unique colors sorted by frequency
        color_counts = Counter(pixels)
        dominant_colors = color_counts.most_common(8)  # Get top 8 colors

        # Convert to hex
        hex_colors = ['#{:02x}{:02x}{:02x}'.format(r, g, b) for (r, g, b), count in dominant_colors]
        return hex_colors
    except Exception as e:
        return None

def create_magnificent_color_palette(colors):
    """Transform hex colors into poetic, evocative descriptions"""
    if not colors or len(colors) == 0:
        return ""

    color_descriptions = []

    for hex_color in colors[:6]:  # Use top 6 colors
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)

        # Brightness
        brightness = (r + g + b) / 3

        # Saturation
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        saturation = 0 if max_c == 0 else (max_c - min_c) / max_c

        # Create poetic descriptions
        if brightness > 240:
            color_descriptions.append("moonlit pearl")
        elif brightness > 220:
            color_descriptions.append("whispered silk")
        elif brightness < 20:
            color_descriptions.append("velvet shadow")
        elif brightness < 40:
            color_descriptions.append("charcoal mystery")
        elif r > g + 30 and r > b + 30:  # Reddish
            if brightness > 180:
                color_descriptions.append("sunset coral")
            elif brightness > 120:
                color_descriptions.append("terracotta warmth")
            elif saturation > 0.5:
                color_descriptions.append("crimson heart")
            else:
                color_descriptions.append("dusty rose")
        elif g > r + 30 and g > b + 30:  # Greenish
            if brightness > 180:
                color_descriptions.append("spring meadow")
            elif brightness > 120:
                color_descriptions.append("sage whisper")
            elif saturation > 0.5:
                color_descriptions.append("emerald depth")
            else:
                color_descriptions.append("moss patina")
        elif b > r + 30 and b > g + 30:  # Blueish
            if brightness > 180:
                color_descriptions.append("aquamarine mist")
            elif brightness > 120:
                color_descriptions.append("twilight indigo")
            elif saturation > 0.5:
                color_descriptions.append("cobalt dream")
            else:
                color_descriptions.append("slate whisper")
        elif r > 150 and g > 150 and b < 100:  # Yellow/gold
            if brightness > 200:
                color_descriptions.append("lemon sunlight")
            else:
                color_descriptions.append("honey gold")
        elif r > 100 and g < 80 and b > 100:  # Purple
            if brightness > 150:
                color_descriptions.append("lavender dusk")
            else:
                color_descriptions.append("plum velvet")
        elif abs(r - g) < 20 and abs(g - b) < 20:  # Neutral/grey
            if brightness > 180:
                color_descriptions.append("silver shimmer")
            elif brightness > 100:
                color_descriptions.append("pewter glow")
            else:
                color_descriptions.append("graphite shadow")
        else:
            # Default warm/cool
            if r + g > b * 1.5:
                color_descriptions.append("amber warmth")
            else:
                color_descriptions.append("slate cool")

    # Remove duplicates while preserving order
    seen = set()
    unique_descriptions = []
    for desc in color_descriptions:
        if desc not in seen:
            seen.add(desc)
            unique_descriptions.append(desc)

    hex_str = " + ".join(colors[:4])
    description_str = ", ".join(unique_descriptions[:4])

    return f"**Color Palette:** {description_str} ({hex_str})"

def transform_to_magnificent(name, style, original_prompt, color_info=""):
    """Transform a basic prompt into a magnificent, dreamy, breathtaking world"""

    # Base cinematic elements
    cinematic_lighting = [
        "god rays piercing through atmospheric dust",
        "rim light catching every handcrafted edge",
        "lens flare dancing like fireflies",
        "chiaroscuro shadows creating theatrical depth",
        "golden hour glow kissing miniature horizons",
        "ethereal backlight revealing translucent textures",
        "dappled light filtering through impossible leaves",
        "luminous haze swirling in tilt-shift focus",
        "prismatic rainbows refracting through dew drops",
        "volumetric light beams painting air visible"
    ]

    material_magic = [
        "felt textures with visible fiber details",
        "paper grain revealing hand-torn edges",
        "clay fingerprints frozen in time",
        "stitching imperfections adding soul",
        "wire armatures barely visible beneath surfaces",
        "brushstroke textures singing handmade hymns",
        "woodgrain patterns telling tree stories",
        "fabric weave catching microscopic light",
        "metal patina whispering age and wonder",
        "glass imperfections creating lens poetry"
    ]

    atmospheric_wonder = [
        "floating dust motes catching light like stars",
        "steam wisps curling in frozen choreography",
        "pollen clouds drifting in amber suspension",
        "gossamer threads connecting worlds",
        "particle effects suggesting magic",
        "fog tendrils embracing miniature landscapes",
        "bokeh orbs blooming in soft focus",
        "light bloom halos around impossible objects",
        "atmospheric haze creating dreamy distance",
        "ethereal glow suggesting parallel dimensions"
    ]

    # Wes Anderson symmetry elements
    anderson_composition = [
        "perfectly symmetrical composition",
        "centered framing with theatrical precision",
        "layered depth like a stage set",
        "pastel color harmony singing in perfect pitch",
        "meticulous arrangement suggesting obsessive care",
        "proscenium arch framing the miniature world",
        "geometrically balanced foreground and background",
        "doll house cross-section revealing intimate layers"
    ]

    # Choose random elements based on punk name (deterministic)
    import hashlib
    seed = int(hashlib.md5(name.encode()).hexdigest(), 16) % 10

    lighting = cinematic_lighting[seed % len(cinematic_lighting)]
    material = material_magic[(seed + 3) % len(material_magic)]
    atmosphere = atmospheric_wonder[(seed + 7) % len(atmospheric_wonder)]
    composition = anderson_composition[seed % len(anderson_composition)]

    # Extract core world concept from original
    # Try to identify the main environment type
    world_type = ""
    if "alley" in original_prompt or "street" in original_prompt or "urban" in original_prompt:
        world_type = "twilight alleyway where shadows tell stories"
    elif "bank" in original_prompt or "vault" in original_prompt or "cash" in original_prompt:
        world_type = "crystalline vault where fortune dreams in green light"
    elif "tea" in original_prompt or "café" in original_prompt:
        world_type = "intimate tea sanctuary where time steeps in warmth"
    elif "office" in original_prompt or "tech" in original_prompt:
        world_type = "minimalist workspace where innovation whispers"
    elif "workshop" in original_prompt or "forge" in original_prompt:
        world_type = "mystical forge where sparks birth constellations"
    elif "bedroom" in original_prompt:
        world_type = "dreamer's sanctuary where stars leak through curtains"
    elif "gallery" in original_prompt or "art" in original_prompt:
        world_type = "kaleidoscopic gallery where colors rebel"
    elif "field" in original_prompt or "sports" in original_prompt:
        world_type = "morning field where dedication glows golden"
    elif "gym" in original_prompt or "athletic" in original_prompt:
        world_type = "neon gymnasium where rhythm pulses electric"
    elif "lab" in original_prompt or "science" in original_prompt:
        world_type = "inventor's laboratory where light conquers darkness"
    elif "palace" in original_prompt or "ice" in original_prompt:
        world_type = "frost palace where winter dreams crystallize"
    elif "school" in original_prompt or "classroom" in original_prompt:
        world_type = "optimistic classroom where futures take shape"
    elif "bakery" in original_prompt or "sugar" in original_prompt:
        world_type = "enchanted bakery where sugar transforms into starlight"
    elif "city" in original_prompt or "building" in original_prompt:
        world_type = "pixel cityscape where futures glow neon"
    else:
        world_type = "liminal space where dreams crystallize into reality"

    # Build magnificent prompt
    magnificent = f"""**A breathtaking miniature {world_type}**, lovingly handcrafted with stop-motion soul and tilt-shift magic. """

    # Add color palette if available
    if color_info:
        magnificent += f"""{color_info} dancing across every surface like memories made visible. """
    else:
        magnificent += f"""**[TODO: ADD ASEPRITE COLORS]** """

    magnificent += f"""

**Cinematic Poetry:** {composition}, {lighting}, {material}, {atmosphere}. Every element staged with Wes Anderson precision meeting Laika Studios wonder.

**Material Soul:** Visible craft imperfections—thumbprint textures in clay, hand-stitched seams catching light, paper grain whispering handmade, wire armatures barely glimpsed beneath surfaces, paintbrush strokes singing their maker's devotion.

**Atmospheric Enchantment:** Dream-logic scale where small becomes infinite, time frozen mid-magic, shadows defying physics, parallel world hints shimmering at edges, folkloric whispers woven into air itself.

**Emotional Resonance:** Nostalgic melancholy meeting childlike wonder, theatrical elegance with indie heart, whimsical mystery wrapped in autumn warmth, the kind of beauty that makes you hold your breath.

**Technical Magic:** Miniature diorama perfection, tilt-shift depth of field blurring edges into bokeh dreams, 16:9 cinematic framing, practical effects aesthetic, no CGI slickness—only handbuilt wonder.

**CRUCIAL SAFETY:** No human figures or characters whatsoever, purely environmental storytelling, abstract atmospheric world only, no people or faces, pure scene/setting/mood.

**Format:** 16:9 wide cinematic, stop-motion miniature aesthetic, {style.lower()} craftsmanship"""

    return magnificent

# Main processing
def main():
    source_file = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/FREEPIK_PROMPTS_ENHANCED_ASEPRITE_2025-11-18.md'
    aseprite_dir = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Aseperite/all'
    output_file = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/FREEPIK_PROMPTS_MAGNIFICENT_2025-11-18.md'

    # Read source file
    with open(source_file, 'r') as f:
        content = f.read()

    # Extract all punk entries
    punk_pattern = r'### ((?:lad|lady)_\d+_[^\n]+)\n\*\*Style: ([^\n]+)\*\*\n(.*?)(?=\n### |\Z)'
    punks = re.findall(punk_pattern, content, re.DOTALL)

    print(f"Processing {len(punks)} punks...")

    # Build output
    output = f"""# MAGNIFICENT FREEPIK PROMPTS - Bespoke Punks Worlds
## BREATHTAKING MINIATURE DIORAMAS

**Every world is a cinematic masterpiece** - Stop-motion magic meets Wes Anderson precision. Each environment tells a story without characters, using only light, texture, color, and atmosphere to create worlds that make you gasp.

**Cinematic Influences:** The symmetrical beauty of The Grand Budapest Hotel, the handcrafted wonder of Fantastic Mr. Fox, the eerie enchantment of Coraline, the otherworldly magic of James and the Giant Peach, the miniature perfection of Isle of Dogs.

**Technical Requirements:**
- **Model:** Flux 1.1 (recommended for aesthetic excellence)
- **Format:** 16:9 wide cinematic
- **Style:** Miniature diorama, tilt-shift depth of field, stop-motion aesthetic
- **Safety:** NO human figures or characters - pure environmental storytelling only

**Save Path:** `/public/punk-worlds/{{punk_name}}.jpg`

---

## LAD PUNKS

"""

    lad_count = 0
    lady_count = 0
    processed = 0

    for name, style, original_prompt in punks:
        processed += 1
        print(f"Processing {processed}/{len(punks)}: {name}")

        # Check if lad or lady for section organization
        if name.startswith('lad_'):
            if lad_count == 0:
                pass  # Already have LAD PUNKS header
            lad_count += 1
        else:
            if lady_count == 0:
                output += "\n\n## LADY PUNKS\n\n"
            lady_count += 1

        # Try to get colors from Aseprite file
        color_info = ""
        png_path = os.path.join(aseprite_dir, f"{name}.png")
        if os.path.exists(png_path):
            colors = extract_colors_from_png(png_path)
            if colors:
                color_info = create_magnificent_color_palette(colors)

        # Transform the prompt
        magnificent_prompt = transform_to_magnificent(name, style, original_prompt, color_info)

        # Add to output
        output += f"### {name}\n"
        output += f"**Style:** {style}\n\n"
        output += magnificent_prompt
        output += "\n\n---\n\n"

    # Write output
    with open(output_file, 'w') as f:
        f.write(output)

    print(f"\n✨ MAGNIFICENCE COMPLETE! ✨")
    print(f"Processed: {processed} punks ({lad_count} lads, {lady_count} ladies)")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    main()
