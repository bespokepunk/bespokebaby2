#!/usr/bin/env python3
"""
Advanced script to enhance Freepik prompts with precise color palettes and atmospheric details
"""

import os
import re
from pathlib import Path
from PIL import Image
from collections import Counter
import colorsys

# Paths
BASE_DIR = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2")
PROMPTS_FILE = BASE_DIR / "bespoke-punks-website/FREEPIK_PROMPTS.md"
ASEPRITE_DIR = BASE_DIR / "Aseperite/all"
OUTPUT_FILE = BASE_DIR / "bespoke-punks-website/FREEPIK_PROMPTS_ENHANCED_COMPLETE_2025-11-18.md"

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_color_name(rgb):
    """Get descriptive name for a color"""
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    h = h * 360  # Convert to degrees

    # Determine saturation level
    if s < 0.1:
        sat_desc = ""
    elif s < 0.3:
        sat_desc = "pale "
    elif s < 0.6:
        sat_desc = "soft "
    elif s < 0.8:
        sat_desc = "vibrant "
    else:
        sat_desc = "intense "

    # Determine value/brightness
    if v < 0.2:
        val_desc = "deep "
    elif v < 0.4:
        val_desc = "dark "
    elif v < 0.6:
        val_desc = ""
    elif v < 0.8:
        val_desc = "bright "
    else:
        val_desc = "luminous "

    # Determine hue
    if s < 0.1:
        if v < 0.3:
            return f"{val_desc}charcoal"
        elif v < 0.6:
            return f"{val_desc}grey"
        else:
            return f"{val_desc}pearl"

    if h < 15 or h >= 345:
        hue = "crimson"
    elif h < 30:
        hue = "vermillion"
    elif h < 45:
        hue = "amber"
    elif h < 60:
        hue = "golden"
    elif h < 75:
        hue = "chartreuse"
    elif h < 150:
        hue = "emerald"
    elif h < 165:
        hue = "cyan"
    elif h < 200:
        hue = "azure"
    elif h < 240:
        hue = "sapphire"
    elif h < 280:
        hue = "violet"
    elif h < 310:
        hue = "magenta"
    elif h < 345:
        hue = "rose"

    return f"{val_desc}{sat_desc}{hue}".strip()

def get_atmospheric_details(colors):
    """Generate atmospheric lighting and material descriptions"""
    if not colors:
        return {}

    # Analyze dominant colors
    dominant = colors[0]['rgb']
    secondary = colors[1]['rgb'] if len(colors) > 1 else dominant

    r, g, b = dominant
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

    # Generate lighting effects based on color temperature
    if h < 0.15 or h > 0.9:  # Warm reds/oranges
        lighting = "warm golden bokeh, sun-kissed lens flare"
        atmosphere = "twilight ember glow, floating amber particles"
        materials = "weathered brass, burnished copper, warm terracotta"
    elif h < 0.25:  # Yellows
        lighting = "honeyed shimmer, soft candlelight bokeh"
        atmosphere = "golden hour haze, suspended dust motes"
        materials = "aged parchment, polished gold, sun-bleached wood"
    elif h < 0.45:  # Greens
        lighting = "dappled forest light, emerald lens flare"
        atmosphere = "misty morning glow, floating leaf particles"
        materials = "moss-covered stone, jade crystal, weathered bronze"
    elif h < 0.65:  # Blues/Cyans
        lighting = "cool moonlight bokeh, ice crystal shimmer"
        atmosphere = "twilight mist, floating frost particles"
        materials = "frosted glass, chrome steel, deep ocean ceramic"
    elif h < 0.75:  # Purples
        lighting = "ethereal violet glow, mystical lens flare"
        atmosphere = "enchanted twilight, wisps of lavender smoke"
        materials = "iridescent silk, amethyst crystal, aged velvet"
    else:  # Magentas/Pinks
        lighting = "soft rose bokeh, pearlescent shimmer"
        atmosphere = "dreamy pink haze, floating petal particles"
        materials = "delicate porcelain, rose quartz, silk ribbons"

    # Add depth based on value
    if v < 0.4:
        lighting += ", dramatic chiaroscuro"
        atmosphere += ", deep shadow pools"
    elif v > 0.7:
        lighting += ", bright highlights"
        atmosphere += ", luminous aura"

    return {
        'lighting': lighting,
        'atmosphere': atmosphere,
        'materials': materials
    }

def get_color_palette_from_png(png_path):
    """Extract color palette from PNG file"""
    try:
        img = Image.open(png_path).convert('RGB')
        pixels = list(img.getdata())

        # Count color occurrences
        color_counts = Counter(pixels)

        # Get top colors (excluding pure black and white)
        colors = []
        for color, count in color_counts.most_common(20):
            # Skip pure black and pure white
            if color == (0, 0, 0) or color == (255, 255, 255):
                continue
            colors.append({
                'hex': rgb_to_hex(color),
                'rgb': color,
                'name': get_color_name(color),
                'count': count
            })
            if len(colors) >= 8:
                break

        return colors
    except Exception as e:
        print(f"Error reading {png_path}: {e}")
        return []

def enhance_prompt_with_colors(prompt_text, colors, punk_name):
    """Enhance a prompt with precise color palette and atmospheric details"""
    if not colors:
        return prompt_text

    # Get atmospheric details
    atmos = get_atmospheric_details(colors)

    # Get hex values and names
    hex_colors = [c['hex'] for c in colors]
    color_names = [c['name'] for c in colors[:3]]

    # Parse the prompt to find the style and first descriptive line
    lines = prompt_text.strip().split('\n')

    # Find style line
    style_line = ""
    style_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("**Style:"):
            style_line = line
            style_idx = i
            break

    # Find the main prompt (usually after style)
    main_prompt_idx = style_idx + 1 if style_idx >= 0 else 0
    while main_prompt_idx < len(lines) and not lines[main_prompt_idx].strip():
        main_prompt_idx += 1

    if main_prompt_idx >= len(lines):
        return prompt_text

    main_prompt = lines[main_prompt_idx]

    # Insert color information right at the start of the main description
    # Find the first comma or "with" to insert our palette

    # Extract the beginning part (before "bathed in")
    if "bathed in" in main_prompt:
        parts = main_prompt.split("bathed in", 1)
        prefix = parts[0].strip()

        # Create new color-rich description
        color_desc = f"bathed in precise palette of {hex_colors[0]}, {hex_colors[1]}, {hex_colors[2]}"
        if len(hex_colors) > 3:
            color_desc += f", {hex_colors[3]}"

        # Add atmospheric details
        enhanced_desc = f"{color_desc} with {atmos['lighting']}, {atmos['atmosphere']}, materials: {atmos['materials']}, {parts[1]}"

        enhanced_prompt = prefix + " " + enhanced_desc
    else:
        # Fallback: add at beginning
        enhanced_prompt = main_prompt + f" [COLOR PALETTE: {', '.join(hex_colors[:6])} | LIGHTING: {atmos['lighting']} | ATMOSPHERE: {atmos['atmosphere']} | MATERIALS: {atmos['materials']}]"

    # Reconstruct
    new_lines = lines[:main_prompt_idx] + [enhanced_prompt] + lines[main_prompt_idx+1:]

    return '\n'.join(new_lines)

def extract_punk_name_from_header(line):
    """Extract punk identifier from header line"""
    match = re.match(r'###\s+(lad(?:y)?_\d+_[\w\-]+)', line)
    if match:
        return match.group(1)
    return None

def process_prompts():
    """Main processing function"""
    print("=" * 80)
    print("FREEPIK ADVANCED PROMPT ENHANCER")
    print("=" * 80)

    # Get PNG files
    png_files = {}
    for file in ASEPRITE_DIR.glob("*.png"):
        punk_name = file.stem
        png_files[punk_name] = file

    print(f"\nFound {len(png_files)} PNG files for color extraction")

    # Read original prompts
    with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into sections by punk
    sections = re.split(r'(###\s+lad(?:y)?_\d+_[\w\-]+)', content)

    # Reconstruct with enhancements
    enhanced_content = []

    # Add header with instructions
    header = """# Freepik AI Image Generation Prompts for Bespoke Punks
## WORLD-CLASS ENHANCED EDITION (2025-11-18)

**ATMOSPHERIC MINIATURE WORLDS** - Brief mysterious glimpses into each punk's world. Miniature diorama stop-motion aesthetic with tilt-shift depth, handbuilt craftsmanship, and subtle enchanted atmosphere. Each world matches the exact colors, palette, and aesthetic vibe from their 24×24 pixel portrait.

**🎨 ENHANCED WITH PRECISE COLOR PALETTES** - Each prompt now includes:
- Exact hex color values extracted from the punk's artwork
- Atmospheric lighting details (bokeh, lens flare, shimmer, glow)
- Material textures (weathered, chrome, delicate, glossy)
- Environmental storytelling (floating particles, wisps, dappled light)

**Recommended Model: Flux 1.1** (Great aesthetics and prompt adherence)

Generate these as **16:9 wide cinematic images** using Freepik AI Image Generator.

Save each image as: `/public/punk-worlds/{punk_name}.jpg`

---

"""

    enhanced_content.append(header)

    stats = {
        'total': 0,
        'enhanced': 0,
        'marked_todo': 0
    }

    current_section = "## LAD PUNKS\n\n"

    # Process each punk section
    for i in range(1, len(sections), 2):
        if i >= len(sections):
            break

        header_line = sections[i]
        prompt_text = sections[i + 1] if i + 1 < len(sections) else ""

        punk_name = extract_punk_name_from_header(header_line)

        if not punk_name:
            enhanced_content.append(header_line)
            enhanced_content.append(prompt_text)
            continue

        stats['total'] += 1

        # Check for section headers
        if "## LAD PUNKS" in prompt_text or "## LADY PUNKS" in prompt_text:
            # Extract section header
            for line in prompt_text.split('\n'):
                if line.startswith("## "):
                    current_section = line + "\n\n"
                    break

        # Check if we have PNG for this punk
        has_png = punk_name in png_files

        if has_png:
            # Get color palette
            colors = get_color_palette_from_png(png_files[punk_name])

            if colors:
                # Enhance the prompt
                enhanced_prompt = enhance_prompt_with_colors(prompt_text, colors, punk_name)
                enhanced_content.append(header_line)
                enhanced_content.append(enhanced_prompt)
                stats['enhanced'] += 1
                print(f"✓ Enhanced: {punk_name} with {len(colors)} colors")
            else:
                # Has PNG but couldn't extract colors
                enhanced_content.append(header_line)
                enhanced_content.append(prompt_text)
                print(f"⚠ No colors: {punk_name}")
        else:
            # No files - mark as TODO
            enhanced_content.append(header_line)
            # Insert TODO marker right after the header
            enhanced_content.append(f"\n**[TODO: ENHANCE WHEN ASEPRITE FILE AVAILABLE]**\n{prompt_text}")
            stats['marked_todo'] += 1
            print(f"⊗ TODO: {punk_name}")

    # Write enhanced file
    final_content = ''.join(enhanced_content)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total punks: {stats['total']}")
    print(f"Enhanced with advanced details: {stats['enhanced']}")
    print(f"Marked TODO: {stats['marked_todo']}")
    print(f"\nOutput saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_prompts()
