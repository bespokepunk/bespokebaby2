#!/usr/bin/env python3
"""
Transform Bespoke Punks prompts into MAGNIFICENT, DREAMY, BREATHTAKING worlds
Version 2: Extracts specific world details from original prompts
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
        color_counts = Counter(pixels)
        dominant_colors = color_counts.most_common(8)
        hex_colors = ['#{:02x}{:02x}{:02x}'.format(r, g, b) for (r, g, b), count in dominant_colors]
        return hex_colors
    except:
        return None

def create_poetic_color_name(r, g, b):
    """Create a single poetic color name"""
    brightness = (r + g + b) / 3
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    saturation = 0 if max_c == 0 else (max_c - min_c) / max_c

    # Create poetic descriptions
    if brightness > 240:
        return "moonlit pearl"
    elif brightness > 220:
        return "whispered silk"
    elif brightness < 20:
        return "velvet shadow"
    elif brightness < 40:
        return "charcoal mystery"
    elif r > g + 30 and r > b + 30:  # Reddish
        if brightness > 180:
            return "sunset coral"
        elif brightness > 120:
            return "terracotta warmth" if saturation < 0.5 else "crimson heart"
        else:
            return "dusty rose" if saturation < 0.5 else "ruby depth"
    elif g > r + 30 and g > b + 30:  # Greenish
        if brightness > 180:
            return "spring meadow"
        elif brightness > 120:
            return "sage whisper" if saturation < 0.5 else "emerald depth"
        else:
            return "moss patina" if saturation < 0.5 else "forest shadow"
    elif b > r + 30 and b > g + 30:  # Blueish
        if brightness > 180:
            return "aquamarine mist"
        elif brightness > 120:
            return "twilight indigo" if saturation < 0.5 else "cobalt dream"
        else:
            return "slate whisper" if saturation < 0.5 else "midnight depths"
    elif r > 150 and g > 150 and b < 100:  # Yellow/gold
        return "lemon sunlight" if brightness > 200 else "honey gold"
    elif r > 100 and g < 80 and b > 100:  # Purple
        return "lavender dusk" if brightness > 150 else "plum velvet"
    elif abs(r - g) < 20 and abs(g - b) < 20:  # Neutral/grey
        if brightness > 180:
            return "silver shimmer"
        elif brightness > 100:
            return "pewter glow"
        else:
            return "graphite shadow"
    else:
        return "amber warmth" if r + g > b * 1.5 else "slate cool"

def create_magnificent_color_palette(colors):
    """Transform hex colors into poetic descriptions"""
    if not colors or len(colors) == 0:
        return ""

    color_descriptions = []
    for hex_color in colors[:6]:
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        name = create_poetic_color_name(r, g, b)
        if name not in color_descriptions:
            color_descriptions.append(name)

    hex_str = " + ".join(colors[:4])
    description_str = ", ".join(color_descriptions[:4])
    return f"**Palette:** {description_str} ({hex_str})"

def extract_world_details(original_prompt):
    """Extract key atmospheric and world details from original prompt"""
    # Extract the core environment
    details = {}

    # Find key descriptive words
    if "alley" in original_prompt or "urban" in original_prompt:
        details['world'] = "twilight alleyway where shadows tell forgotten stories"
        details['objects'] = "cardboard boxes stacked like monuments, graffiti tags bleeding into shadows, abandoned coffee cups still steaming"
    elif "vault" in original_prompt or "bank" in original_prompt:
        details['world'] = "crystalline vault where fortune crystallizes into geometric dreams"
        details['objects'] = "scattered coins catching light like fallen stars, cash creating origami patterns, chrome safe doors barely ajar"
    elif "tea" in original_prompt:
        details['world'] = "intimate tea sanctuary where time steeps in ceramic warmth"
        details['objects'] = "porcelain teacups with steam frozen mid-curl, scattered tea leaves telling fortunes, honey jar glowing amber"
    elif "office" in original_prompt or "workspace" in original_prompt:
        details['world'] = "minimalist workspace where innovation whispers through clean lines"
        details['objects'] = "paper circuit diagrams floating like blueprints of dreams, single desk lamp painting dramatic shadows"
    elif "workshop" in original_prompt or "forge" in original_prompt:
        details['world'] = "mystical forge where sparks birth constellations"
        details['objects'] = "copper coils spiraling like industrial serpents, scattered tools casting geometric shadows, welding sparks frozen mid-flight"
    elif "bedroom" in original_prompt:
        details['world'] = "dreamer's sanctuary where stars leak through curtained windows"
        details['objects'] = "indie posters curling at edges, vinyl records stacked like time capsules, single moonbeam illuminating dust motes"
    elif "gallery" in original_prompt or "museum" in original_prompt:
        details['world'] = "kaleidoscopic gallery where colors rebel against reality"
        details['objects'] = "geometric art pieces floating in space, prismatic light refracting through impossible angles"
    elif "field" in original_prompt or "soccer" in original_prompt or "sports" in original_prompt:
        details['world'] = "morning field where dedication glows in dew-soaked grass"
        details['objects'] = "athletic equipment scattered like battle artifacts, white chalk lines glowing ethereal, water bottle catching sunrise"
    elif "gym" in original_prompt:
        details['world'] = "neon gymnasium where rhythm pulses through 80s energy"
        details['objects'] = "dumbbells like steel mountains, geometric exercise equipment in primary colors, neon strips painting electric dreams"
    elif "lab" in original_prompt or "science" in original_prompt:
        details['world'] = "inventor's laboratory where light conquers darkness through glass tubes"
        details['objects'] = "scientific equipment casting dramatic shadows, tungsten filament glowing like captured sunlight, beakers filled with possibility"
    elif "palace" in original_prompt or "throne" in original_prompt:
        details['world'] = "frost palace where winter dreams crystallize into architectural poetry"
        details['objects'] = "ice crystals forming geometric spires, frozen waterfalls catching prismatic light, crystal throne barely visible in mist"
    elif "school" in original_prompt or "classroom" in original_prompt:
        details['world'] = "optimistic classroom where futures take shape in graphite and hope"
        details['objects'] = "textbooks stacked like knowledge towers, pencils arranged in geometric precision, morning light streaming through windows"
    elif "bakery" in original_prompt or "sugar" in original_prompt:
        details['world'] = "enchanted bakery where sugar transforms into edible starlight"
        details['objects'] = "powdered sugar dusting surfaces like fresh snow, scattered sugar crystals catching light, steam rising in gentle spirals"
    elif "locker" in original_prompt:
        details['world'] = "electric locker room where athletic dreams pulse with neon promise"
        details['objects'] = "sneakers arranged like street monuments, lockers lined in perfect symmetry, sports equipment casting bold shadows"
    elif "cafe" in original_prompt or "lounge" in original_prompt:
        details['world'] = "soul cafe where sunset melts into velvet furniture"
        details['objects'] = "coffee cups creating concentric circles, checkered napkins in geometric perfection, smoke wisps frozen in golden hour"
    elif "street" in original_prompt or "corner" in original_prompt:
        details['world'] = "urban street corner where legends are written in neon and shadow"
        details['objects'] = "chain link fence catching golden light, scattered urban textures, rainbow visor fragments refracting mystery"
    elif "beach" in original_prompt or "ocean" in original_prompt:
        details['world'] = "liminal shoreline where ocean whispers meet sky in turquoise infinity"
        details['objects'] = "seashells arranged in spiral patterns, foam frozen mid-crash, single wave suspended in time"
    elif "city" in original_prompt or "building" in original_prompt:
        details['world'] = "pixel cityscape where digital futures glow in geometric rebellion"
        details['objects'] = "8-bit buildings stacked like circuit boards, streetlamps casting pixelated halos, neon signs bleeding color"
    elif "temple" in original_prompt or "garden" in original_prompt:
        details['world'] = "zen temple garden where discipline meets tranquility in paper precision"
        details['objects'] = "paper bonsai trees perfectly folded, stone path leading to nowhere and everywhere, single orange leaf suspended"
    elif "library" in original_prompt:
        details['world'] = "timeless library where knowledge towers reach toward infinity"
        details['objects'] = "books stacked in precarious poetry, reading lamp casting warm sphere of light, dust particles visible in golden beam"
    elif "stage" in original_prompt or "concert" in original_prompt:
        details['world'] = "glam rock stage where electric dreams explode into lime lightning"
        details['objects'] = "microphone stands like metal monuments, scattered guitar picks catching spotlight, amplifiers humming with potential"
    elif "hideout" in original_prompt or "ninja" in original_prompt:
        details['world'] = "tactical hideout where shadows teach the art of invisible motion"
        details['objects'] = "throwing stars arranged in constellation patterns, mask fragments, pink cherry blossom petals in stark contrast"
    elif "chamber" in original_prompt or "ritual" in original_prompt:
        details['world'] = "mystical chamber where incense smoke carries prayers to parallel dimensions"
        details['objects'] = "ritual objects arranged in sacred geometry, purple smoke tendrils frozen mid-spiral, candles casting dancing shadows"
    elif "plaza" in original_prompt:
        details['world'] = "neighborhood plaza where community breathes in terracotta warmth"
        details['objects'] = "architectural elements suggesting Mediterranean dreams, single streetlamp as beacon, scattered friendly details"
    elif "studio" in original_prompt or "art" in original_prompt:
        details['world'] = "creative studio where visions transform into geometric rebellion"
        details['objects'] = "scattered artworks in progress, palette knives catching light, paint tubes arranged like urban skyline"
    elif "nursery" in original_prompt or "family" in original_prompt:
        details['world'] = "gentle nursery where innocence glows in soft geometric patterns"
        details['objects'] = "toy blocks stacked in impossible physics, stuffed animals catching warm light, single mobile spinning slowly"
    elif "rooftop" in original_prompt:
        details['world'] = "sunset rooftop where day surrenders to dreaming in horizontal poetry"
        details['objects'] = "scattered sunset gradient creating layered atmosphere, single antenna reaching skyward, clouds painted in bands"
    elif "nightclub" in original_prompt or "club" in original_prompt:
        details['world'] = "cyberpunk nightclub where neon vertical stripes pulse with electric heartbeat"
        details['objects'] = "neon tubes creating vertical rhythm, scattered nightclub elements, chrome surfaces reflecting impossible colors"
    elif "kingdom" in original_prompt or "castle" in original_prompt:
        details['world'] = "noble kingdom where crown jewels catch light like captured constellations"
        details['objects'] = "golden crown ornaments, scattered royal symbols, throne barely visible in misty majesty"
    elif "apartment" in original_prompt:
        details['world'] = "minimalist apartment where stillness speaks louder than noise"
        details['objects'] = "coffee cup as meditation vessel, geometric furniture in clean lines, single plant suggesting life"
    elif "nature" in original_prompt or "forest" in original_prompt:
        details['world'] = "enchanted forest where every leaf tells ancient secrets"
        details['objects'] = "scattered natural textures, single sprout pushing through earth, dappled light creating shadow theater"
    else:
        details['world'] = "liminal space where reality softens into atmospheric poetry"
        details['objects'] = "scattered geometric shapes catching impossible light, shadows defying physics"

    return details

def get_cinematic_elements(name):
    """Get deterministic cinematic elements based on punk name"""
    import hashlib
    seed = int(hashlib.md5(name.encode()).hexdigest(), 16)

    lighting_options = [
        "god rays piercing atmospheric dust like divine fingers",
        "rim light kissing every handcrafted edge with golden reverence",
        "lens flare dancing across frame like imprisoned fireflies",
        "chiaroscuro shadows creating Caravaggio depth in miniature",
        "golden hour glow bathing everything in nostalgic amber",
        "ethereal backlight revealing translucent textures and hidden details",
        "dappled light filtering through leaves like stained glass",
        "luminous haze swirling in tilt-shift focal plane",
        "prismatic rainbows refracting through crystal dew drops",
        "volumetric light beams painting air itself visible and sacred"
    ]

    material_options = [
        "felt textures revealing every fiber's gentle imperfection",
        "paper grain showing hand-torn edges with fibrous honesty",
        "clay fingerprints frozen in time like maker's signature",
        "stitching with thread slightly loose, adding handmade soul",
        "wire armatures barely glimpsed beneath surface like skeletal truth",
        "brushstroke textures singing visible hymns to human touch",
        "woodgrain patterns telling tree ring stories of patience",
        "fabric weave catching microscopic light in textile poetry",
        "metal patina whispering oxidation's slow romance with time",
        "glass imperfections creating accidental lens poetry"
    ]

    atmosphere_options = [
        "floating dust motes catching light like indoor constellations",
        "steam wisps curling in frozen choreography of heat and air",
        "pollen clouds drifting in amber suspension, time holding breath",
        "gossamer threads connecting foreground to background like web of dreams",
        "particle effects suggesting just-departed magic still lingering",
        "fog tendrils embracing miniature landscape in gentle possession",
        "bokeh orbs blooming in soft focus like dreamy light bubbles",
        "light bloom halos surrounding objects as if blessed",
        "atmospheric haze creating romantic distance between viewer and world",
        "ethereal glow suggesting parallel dimension bleeding through"
    ]

    composition_options = [
        "**Wes Anderson symmetry:** Perfect bilateral composition, every element precisely balanced",
        "**Laika Studios depth:** Layered planes creating theatrical proscenium framing",
        "**Coraline mystery:** Off-kilter angles suggesting something wonderfully wrong",
        "**Grand Budapest elegance:** Ornate details in every corner, maximalist beauty",
        "**Fantastic Mr. Fox warmth:** Autumn-touched palette, handmade with visible love",
        "**Isle of Dogs precision:** Japanese aesthetic influence, minimal and profound",
        "**Kubo composition:** Sweeping dramatic framing, epic scope in miniature",
        "**ParaNorman staging:** Slightly askew, charming imperfection, indie heart"
    ]

    idx = seed % len(lighting_options)
    return {
        'lighting': lighting_options[idx],
        'material': material_options[(idx + 3) % len(material_options)],
        'atmosphere': atmosphere_options[(idx + 7) % len(atmosphere_options)],
        'composition': composition_options[idx % len(composition_options)]
    }

def transform_to_magnificent(name, style, original_prompt, color_info=""):
    """Transform into MAGNIFICENT prompt with specific world details"""

    # Extract world-specific details
    details = extract_world_details(original_prompt)
    world = details.get('world', 'liminal space between dreams and reality')
    objects = details.get('objects', 'scattered elements catching impossible light')

    # Get cinematic elements
    cinema = get_cinematic_elements(name)

    # Build the magnificent prompt
    output = f"**A breathtaking miniature {world}**, lovingly handcrafted with stop-motion soul and tilt-shift magic. "

    # Add color palette
    if color_info:
        output += f"{color_info} painting every surface with chromatic poetry. "
    else:
        output += "**[TODO: ADD ASEPRITE COLORS]** "

    # Composition and framing
    output += f"\n\n{cinema['composition']}. "

    # Specific world details and objects
    output += f"**World Details:** {objects}—each element positioned with obsessive care, telling stories through pure atmosphere.\n\n"

    # Lighting
    output += f"**Cinematic Lighting:** {cinema['lighting']}, creating mood through shadow and luminance, theatrical yet intimate.\n\n"

    # Material craft
    output += f"**Material Soul:** {cinema['material']}. Every surface whispers 'handmade'—thumbprint textures, imperfect stitching, the ghost of the artist's hand visible in clay and paper.\n\n"

    # Atmospheric magic
    output += f"**Atmospheric Enchantment:** {cinema['atmosphere']}. Dream-logic scale where tiny becomes monumental, physics suggestions rather than laws, folkloric whispers woven into very air.\n\n"

    # Emotional core
    output += "**Emotional Resonance:** Nostalgic melancholy kissing childlike wonder. Theatrical elegance with indie heart. Whimsical mystery wrapped in autumn warmth. The kind of beauty that makes you hold your breath and feel homesick for places you've never been.\n\n"

    # Technical specifications
    output += "**Technical Magic:** Miniature diorama perfection with visible craft, tilt-shift depth of field blurring edges into bokeh dreams, 16:9 cinematic letterbox framing, practical stop-motion aesthetic—no CGI slickness, only handbuilt wonder and visible love.\n\n"

    # Safety
    output += "**CRUCIAL SAFETY:** Absolutely no human figures, faces, or characters whatsoever. Pure environmental storytelling. Abstract atmospheric world only. No people or realistic characters—only mood, light, object, and space telling tales.\n\n"

    # Format
    output += f"**Format:** 16:9 wide cinematic letterbox • {style} craftsmanship • Stop-motion miniature aesthetic • Tilt-shift depth of field"

    return output

def main():
    source_file = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/FREEPIK_PROMPTS_ENHANCED_ASEPRITE_2025-11-18.md'
    aseprite_dir = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Aseperite/all'
    output_file = '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/FREEPIK_PROMPTS_MAGNIFICENT_2025-11-18.md'

    with open(source_file, 'r') as f:
        content = f.read()

    # Extract all punk entries
    punk_pattern = r'### ((?:lad|lady)_\d+_[^\n]+)\n\*\*Style: ([^\n]+)\*\*\n(.*?)(?=\n### |\Z)'
    punks = re.findall(punk_pattern, content, re.DOTALL)

    print(f"Processing {len(punks)} punks into MAGNIFICENT worlds...")

    # Build output
    output = f"""# MAGNIFICENT FREEPIK PROMPTS
## Bespoke Punks: Breathtaking Miniature Worlds

**Every world is a cinematic masterpiece** — Stop-motion magic meets Wes Anderson precision. Each environment tells profound stories without characters, using only light, texture, color, and atmosphere to create worlds that steal your breath and break your heart.

**Cinematic DNA:** The symmetrical beauty of *The Grand Budapest Hotel*, the handcrafted wonder of *Fantastic Mr. Fox*, the eerie enchantment of *Coraline*, the otherworldly magic of *James and the Giant Peach*, the miniature perfection of *Isle of Dogs*, the sweeping drama of *Kubo and the Two Strings*.

**Core Aesthetic:** Tilt-shift miniature dioramas with visible craft imperfections, theatrical lighting with emotional depth, folkloric atmosphere meeting indie sensibility, nostalgic melancholy wrapped in childlike wonder.

**Technical Requirements:**
- **Recommended Model:** Flux 1.1 (exceptional aesthetic adherence)
- **Format:** 16:9 wide cinematic letterbox
- **Style:** Miniature diorama, tilt-shift depth of field, stop-motion aesthetic with visible handcraft
- **Safety Requirement:** NO human figures, faces, or characters—pure environmental storytelling only
- **Save Path:** `/public/punk-worlds/{{punk_name}}.jpg`

---

## LAD PUNKS

"""

    lad_count = 0
    lady_count = 0

    for i, (name, style, original_prompt) in enumerate(punks):
        print(f"✨ {i+1}/{len(punks)}: {name}")

        # Section headers
        if name.startswith('lady_') and lady_count == 0:
            output += "\n\n---\n\n## LADY PUNKS\n\n"
            lady_count += 1
        elif name.startswith('lad_'):
            lad_count += 1

        # Get colors
        color_info = ""
        png_path = os.path.join(aseprite_dir, f"{name}.png")
        if os.path.exists(png_path):
            colors = extract_colors_from_png(png_path)
            if colors:
                color_info = create_magnificent_color_palette(colors)

        # Transform
        magnificent_prompt = transform_to_magnificent(name, style, original_prompt, color_info)

        # Add to output
        output += f"### {name}\n\n"
        output += f"**Style:** {style}\n\n"
        output += magnificent_prompt
        output += "\n\n---\n\n"

    # Write output
    with open(output_file, 'w') as f:
        f.write(output)

    print(f"\n🌟 MAGNIFICENCE COMPLETE! 🌟")
    print(f"📊 Processed: {len(punks)} punks ({lad_count} lads, {len(punks) - lad_count} ladies)")
    print(f"💾 Output: {output_file}")
    print(f"✨ Every prompt is now a miniature masterpiece! ✨")

if __name__ == "__main__":
    main()
