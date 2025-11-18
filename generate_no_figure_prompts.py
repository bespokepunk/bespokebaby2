#!/usr/bin/env python3
"""
Generate all 211 punk world prompts with NO FIGURES - pure environmental storytelling.
Based on the exact structure the user provided.
"""

import os
from PIL import Image
from collections import Counter

def get_dominant_colors(image_path):
    """Extract dominant colors from pixel art."""
    try:
        img = Image.open(image_path).convert('RGB')
        pixels = list(img.getdata())

        # Filter out very dark/light pixels
        filtered = [p for p in pixels if 30 < sum(p)/3 < 225]
        if not filtered:
            filtered = pixels

        color_counts = Counter(filtered)
        dominant = color_counts.most_common(5)
        return [color for color, count in dominant]
    except:
        return []

def color_to_desc(r, g, b):
    """Convert RGB to descriptive color."""
    avg = (r + g + b) / 3

    if g > r and g > b and g > 150:
        return "bright lime green" if g > 200 else "emerald green"
    elif r > g and r > b:
        return "crimson red" if r > 180 else "dusty rose"
    elif b > r and b > g:
        return "royal blue" if b > 180 else "soft purple"
    elif r > 180 and g > 180:
        return "golden yellow" if r > g else "warm peach"
    elif avg < 80:
        return "deep charcoal"
    elif avg > 200:
        return "pristine white"
    else:
        return "soft grey"

# World location templates based on vibe
WORLD_TYPES = [
    ("retro arcade", "neon gaming", "geometric pixel screens and glowing arcade cabinets"),
    ("cozy tea house", "warm contemplative", "scattered teacups and steam wisps frozen mid-curl"),
    ("minimalist loft", "serene zen", "geometric paper furniture in clean modern lines"),
    ("vintage record shop", "nostalgic retro", "scattered vinyl records and warm wood shelves"),
    ("rooftop garden", "urban sanctuary", "clay planters and weathered brick textures"),
    ("artisan pottery studio", "creative warm", "pottery tools and clay vessels with golden dust particles"),
    ("bedroom recording studio", "intimate creative", "music equipment and soft fabric textures"),
    ("basketball court", "athletic energetic", "sports equipment and chalk dust creating fresh morning atmosphere"),
    ("80s gym", "vibrant retro", "geometric exercise equipment in primary color blocks"),
    ("pop art gallery", "bold graphic", "geometric artworks and sculptural shapes in primary colors"),
    ("nighttime city rooftop", "urban mysterious", "geometric skyline and neon light reflections"),
    ("japanese zen garden", "peaceful contemplative", "scattered stones and paper bonsai trees"),
    ("vintage library", "scholarly quiet", "leather-bound books and elegant writing instruments"),
    ("nautical cafe", "charming coastal", "striped awnings and maritime decor with floating sakura petals"),
    ("disco lounge", "retro glamorous", "golden disco balls floating throughout space creating shimmering light"),
]

def generate_prompt(punk_name, png_path):
    """Generate a NO FIGURES prompt."""

    # Get colors
    colors = get_dominant_colors(png_path)
    if not colors:
        color_desc = "mysterious twilight atmosphere"
    else:
        c1 = color_to_desc(*colors[0])
        c2 = color_to_desc(*colors[1]) if len(colors) > 1 else c1
        color_desc = f"{c1} with {c2} accents"

    # Pick world type (rotate through list)
    idx = hash(punk_name) % len(WORLD_TYPES)
    world_type, vibe, objects = WORLD_TYPES[idx]

    # Generate prompt following EXACT structure
    prompt = f"""Miniature {world_type} diorama bathed in {color_desc}, {objects} creating {vibe} atmosphere, atmospheric haze with layered textures and handcrafted details, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating magical mystery, heavy tilt-shift blur making any distant elements completely abstract and out of focus, dream-logic scale where objects become monuments, liminal space between reality and imagination, shadow puppet theater depth with layered atmospheric silhouettes, folkloric tale whispered through the air, mythological shadow play across surfaces, ancient legend told in atmospheric tones, ethereal ghostly glow, small-scale magic with visible handbuilt textures, abstract heavily stylized abstract only, no realism, no realistic faces or characters, abstract atmospheric world only, tilt-shift atmospheric, 16:9"""

    return prompt.strip()

def main():
    aseprite_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Aseperite/all"
    output_file = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/FREEPIK_PROMPTS_NO_FIGURES_COMPLETE.md"

    png_files = sorted([f for f in os.listdir(aseprite_dir) if f.endswith('.png')])

    with open(output_file, 'w') as f:
        f.write("# Freepik AI Image Generation Prompts - NO FIGURES VERSION\n\n")
        f.write("**Pure Environmental Storytelling - Compelling, Charming, Magnetic Worlds**\n\n")
        f.write("Every prompt emphasizes NO HUMAN FIGURES multiple times.\n")
        f.write("Format: 16:9 landscape, Miniature diorama stop-motion aesthetic\n\n")
        f.write("---\n\n")

        # Lads
        f.write("## LAD PUNKS\n\n")
        lad_files = [f for f in png_files if f.startswith('lad_')]
        for png_file in lad_files:
            punk_name = png_file.replace('.png', '')
            png_path = os.path.join(aseprite_dir, png_file)

            prompt = generate_prompt(punk_name, png_path)

            f.write(f"### {punk_name}\n")
            f.write(f"{prompt}\n\n")

        # Ladies
        f.write("\n## LADY PUNKS\n\n")
        lady_files = [f for f in png_files if f.startswith('lady_')]
        for png_file in lady_files:
            punk_name = png_file.replace('.png', '')
            png_path = os.path.join(aseprite_dir, png_file)

            prompt = generate_prompt(punk_name, png_path)

            f.write(f"### {punk_name}\n")
            f.write(f"{prompt}\n\n")

    print(f"✅ Generated {len(png_files)} prompts!")
    print(f"📄 Output: {output_file}")

if __name__ == "__main__":
    main()
