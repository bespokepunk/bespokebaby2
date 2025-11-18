#!/usr/bin/env python3
"""
Generate Midjourney world prompts based on actual punk character visual traits.
Analyzes PNG files to extract colors and create character-specific world prompts.
"""

import os
from PIL import Image
from collections import Counter
import colorsys

def get_dominant_colors(image_path, num_colors=5):
    """Extract dominant colors from a pixel art image."""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')

        # Get all pixels
        pixels = list(img.getdata())

        # Filter out very dark (close to black) and very light (close to white) pixels
        # as they're often outlines or highlights
        filtered_pixels = []
        for r, g, b in pixels:
            # Skip if too dark or too light
            brightness = (r + g + b) / 3
            if 30 < brightness < 225:
                filtered_pixels.append((r, g, b))

        if not filtered_pixels:
            filtered_pixels = pixels  # Fallback to all pixels

        # Count color frequency
        color_counts = Counter(filtered_pixels)

        # Get most common colors
        dominant = color_counts.most_common(num_colors)

        return [color for color, count in dominant]
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return []

def rgb_to_color_name(r, g, b):
    """Convert RGB to descriptive color name."""
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = h * 360
    s = s * 100
    v = v * 100

    # Value-based (brightness)
    if v < 20:
        return "deep black"
    elif v > 90 and s < 10:
        return "pure white"

    # Saturation-based (grey vs color)
    if s < 15:
        if v < 30:
            return "charcoal grey"
        elif v < 50:
            return "medium grey"
        elif v < 70:
            return "light grey"
        else:
            return "pale grey"

    # Hue-based (actual colors)
    if h < 15 or h > 345:
        if v > 70:
            return "coral pink" if s > 40 else "soft pink"
        else:
            return "crimson red" if s > 50 else "dusty rose"
    elif h < 35:
        return "vibrant orange" if s > 60 else "peach"
    elif h < 65:
        return "golden yellow" if s > 50 else "cream"
    elif h < 80:
        return "lime green" if s > 60 else "sage"
    elif h < 150:
        return "emerald green" if s > 50 else "mint green"
    elif h < 190:
        return "cyan blue" if s > 50 else "soft aqua"
    elif h < 250:
        return "royal blue" if s > 50 else "periwinkle"
    elif h < 290:
        return "deep purple" if v < 50 else "lavender"
    elif h < 330:
        return "magenta" if s > 50 else "mauve"
    else:
        return "rose pink"

def analyze_punk_traits(png_path):
    """Analyze a punk PNG and determine visual traits for world generation."""
    colors = get_dominant_colors(png_path, num_colors=5)

    if not colors:
        return {
            'colors': ['grey', 'neutral'],
            'vibe': 'mysterious',
            'aesthetic': 'abstract'
        }

    # Convert to color names
    color_names = [rgb_to_color_name(r, g, b) for r, g, b in colors]

    # Determine vibe based on color palette
    avg_brightness = sum(sum(c) / 3 for c in colors) / len(colors)

    # Check for specific color families
    has_green = any('green' in c.lower() or 'lime' in c.lower() for c in color_names)
    has_blue = any('blue' in c.lower() or 'cyan' in c.lower() for c in color_names)
    has_purple = any('purple' in c.lower() or 'lavender' in c.lower() or 'mauve' in c.lower() for c in color_names)
    has_red = any('red' in c.lower() or 'crimson' in c.lower() or 'coral' in c.lower() for c in color_names)
    has_orange = any('orange' in c.lower() or 'peach' in c.lower() for c in color_names)
    has_brown = any('brown' in c.lower() or 'tan' in c.lower() for c in color_names)

    # Determine aesthetic vibe
    if has_green and avg_brightness > 150:
        vibe = 'vibrant retro sci-fi'
        aesthetic = 'neon futuristic'
    elif has_purple:
        vibe = 'mystical dreamy'
        aesthetic = 'ethereal fantasy'
    elif has_blue and avg_brightness > 120:
        vibe = 'bright optimistic'
        aesthetic = 'clean modern'
    elif has_blue and avg_brightness < 100:
        vibe = 'moody contemplative'
        aesthetic = 'intimate introspective'
    elif has_orange or (has_red and avg_brightness > 100):
        vibe = 'warm energetic'
        aesthetic = 'vibrant retro'
    elif has_brown or avg_brightness < 100:
        vibe = 'earthy cozy'
        aesthetic = 'natural warm'
    else:
        vibe = 'neutral minimalist'
        aesthetic = 'clean zen'

    return {
        'colors': color_names[:3],  # Top 3 colors
        'vibe': vibe,
        'aesthetic': aesthetic,
        'brightness': 'bright' if avg_brightness > 140 else 'moody' if avg_brightness < 80 else 'balanced'
    }

def generate_world_prompt(punk_name, traits):
    """Generate a miniature diorama world prompt based on punk traits."""
    colors = ', '.join(traits['colors'])

    # World type based on aesthetic
    world_types = {
        'neon futuristic': 'retro arcade game room',
        'ethereal fantasy': 'enchanted crystal garden',
        'clean modern': 'minimalist design studio',
        'intimate introspective': 'cozy bedroom sanctuary',
        'vibrant retro': 'vintage record shop',
        'natural warm': 'artisan pottery workshop',
        'clean zen': 'peaceful meditation space'
    }

    world_location = world_types.get(traits['aesthetic'], 'mysterious chamber')

    # Atmosphere based on vibe
    atmosphere_map = {
        'vibrant retro sci-fi': 'electric neon glow',
        'mystical dreamy': 'soft ethereal twilight',
        'bright optimistic': 'fresh morning light',
        'moody contemplative': 'intimate shadow play',
        'warm energetic': 'golden hour warmth',
        'earthy cozy': 'warm amber twilight',
        'neutral minimalist': 'serene grey light'
    }

    atmosphere = atmosphere_map.get(traits['vibe'], 'mysterious ambiance')

    # Generate the full prompt
    prompt = f"""Miniature {world_location} diorama bathed in {colors} creating {atmosphere}, scattered handcrafted details and layered textures building {traits['aesthetic']} atmosphere, no photorealistic figures, abstract shapes only, no human figures or characters, pure atmospheric environment, pure environmental storytelling, no people or characters, tilt-shift depth creating {traits['vibe']} mystery, heavy tilt-shift blur making any figures completely abstract and out of focus, dream-logic scale where objects become monuments, liminal space between reality and imagination, shadow puppet theater depth with layered atmospheric silhouettes, folkloric tale whispered through the air, mythological shadow play across surfaces, ancient legend told in {traits['brightness']} tones, ethereal ghostly glow, small-scale magic with visible handbuilt textures, handcrafted {traits['aesthetic']} style, no realistic faces or characters, abstract atmospheric world only, tilt-shift atmospheric, 16:9"""

    return prompt.strip()

def main():
    """Process all punk PNGs and generate prompts."""
    aseprite_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Aseperite/all"
    output_file = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke-punks-website/MIDJOURNEY_PROMPTS_TRAIT_BASED_2025-11-18.md"

    # Get all PNG files
    png_files = sorted([f for f in os.listdir(aseprite_dir) if f.endswith('.png')])

    print(f"Found {len(png_files)} PNG files")

    # Open output file
    with open(output_file, 'w') as f:
        f.write("# Midjourney Prompts - Based on Actual Character Traits & Appearance\n\n")
        f.write("**CREATED:** 2025-11-18\n")
        f.write("**METHOD:** Analyzed actual punk PNG files for visual colors and traits\n")
        f.write("**FORMAT:** Miniature diorama stop-motion aesthetic, 16:9 landscape\n")
        f.write("**SETTINGS:** --ar 16:9 --style raw --s 50\n\n")
        f.write("Each prompt is based on the CHARACTER'S ACTUAL COLOR PALETTE AND VISUAL VIBE.\n\n")
        f.write("---\n\n")

        # Separate into lads and ladies
        lad_files = [f for f in png_files if f.startswith('lad_')]
        lady_files = [f for f in png_files if f.startswith('lady_')]

        # Process lads
        f.write("## LAD PUNKS\n\n")
        for png_file in lad_files:
            punk_name = png_file.replace('.png', '')
            png_path = os.path.join(aseprite_dir, png_file)

            print(f"Processing {punk_name}...")

            # Analyze traits
            traits = analyze_punk_traits(png_path)

            # Generate prompt
            prompt = generate_world_prompt(punk_name, traits)

            # Write to file
            f.write(f"### {punk_name}\n")
            f.write(f"**Colors:** {', '.join(traits['colors'])}\n")
            f.write(f"**Vibe:** {traits['vibe']}\n")
            f.write(f"**Prompt:** {prompt} --ar 16:9 --style raw --s 50\n\n")

        # Process ladies
        f.write("\n## LADY PUNKS\n\n")
        for png_file in lady_files:
            punk_name = png_file.replace('.png', '')
            png_path = os.path.join(aseprite_dir, png_file)

            print(f"Processing {punk_name}...")

            # Analyze traits
            traits = analyze_punk_traits(png_path)

            # Generate prompt
            prompt = generate_world_prompt(punk_name, traits)

            # Write to file
            f.write(f"### {punk_name}\n")
            f.write(f"**Colors:** {', '.join(traits['colors'])}\n")
            f.write(f"**Vibe:** {traits['vibe']}\n")
            f.write(f"**Prompt:** {prompt} --ar 16:9 --style raw --s 50\n\n")

    print(f"\n✅ Generated prompts for {len(png_files)} punks!")
    print(f"📄 Output: {output_file}")

if __name__ == "__main__":
    main()
