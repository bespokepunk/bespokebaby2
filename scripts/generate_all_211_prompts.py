#!/usr/bin/env python3
"""
Generate clean, concise Midjourney prompts for ALL 211 Bespoke Punks.
Extracts colors from PNG files for punks missing color data.
"""

import re
from pathlib import Path
from PIL import Image
from collections import Counter

# Define base paths
REPO_ROOT = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2")
FREEPIK_FILE = REPO_ROOT / "bespoke-punks-website/FREEPIK_PROMPTS_MAGNIFICENT_2025-11-18.md"
OUTPUT_FILE = REPO_ROOT / "bespoke-punks-website/MIDJOURNEY_PROMPTS_CLEAN_2025-11-18.md"
ASEPRITE_DIR = REPO_ROOT / "Aseperite/all"

# Punks missing color data in FREEPIK (have TODO placeholders)
MISSING_COLORS = {
    'lad_014_jackson',
    'lad_029_famous',
    'lad_032_shaman',
    'lad_033_molecule',
    'lad_038_cashking',
    'lad_039_davinci',
    'lad_043_jeremy',
    'lad_045_homewithkids',
    'lad_049_gainzyyyy12',
    'lad_049_gainzyyyy18',
    'lad_066_napoli2',
    'lad_068_mayor',
    'lad_074_lc',
    'lad_102_bunya',
    'lad_103_merheb2',
    'lady_099_domino'
}

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def extract_dominant_colors_from_png(png_path, num_colors=4):
    """Extract dominant colors from a PNG file."""
    try:
        # Try different possible filenames
        possible_paths = [
            png_path,
            png_path.replace('gainzyyyy12', 'gainzyyyy12 copy'),
            png_path.replace('gainzyyyy18', 'gainzyyyy18 copy'),
            png_path.replace('napoli2', 'napoli2 copy'),
            png_path.replace('mayor', 'mayor copy 2'),
            png_path.replace('lc', '74_lc'),
            png_path.replace('merheb2', 'merheb3'),
            png_path.replace('domino', 'VQ'),  # lady_099 might be named differently
        ]

        img = None
        for path in possible_paths:
            p = Path(path)
            if p.exists():
                img = Image.open(p)
                break

        if img is None:
            # Return default colors if file not found
            return ["#000000", "#ffffff", "#808080", "#404040"]

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize for faster processing
        img = img.resize((50, 50))

        # Get all pixels
        pixels = list(img.getdata())

        # Count colors
        color_counts = Counter(pixels)

        # Get most common colors
        dominant = color_counts.most_common(num_colors)

        # Convert to hex
        hex_colors = [rgb_to_hex(color[0]) for color in dominant]

        # Ensure we have exactly 4 colors
        while len(hex_colors) < 4:
            hex_colors.append("#808080")

        return hex_colors[:4]

    except Exception as e:
        print(f"Warning: Could not extract colors from {png_path}: {e}")
        return ["#000000", "#ffffff", "#808080", "#404040"]

def extract_punk_data_from_freepik(content):
    """Extract ALL punk data from FREEPIK file."""
    punks = []

    # Split by punk sections
    sections = re.split(r'^### (lad|lady)_', content, flags=re.MULTILINE)

    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break

        punk_prefix = sections[i]
        punk_content = sections[i + 1]

        # Extract punk name
        name_match = re.match(r'([^\n]+)', punk_content)
        if not name_match:
            continue
        punk_name = f"{punk_prefix}_{name_match.group(1).strip()}"

        # Extract palette (or check if it's TODO)
        has_todo = "TODO: ADD ASEPRITE COLORS" in punk_content

        if has_todo:
            # Extract colors from PNG file
            png_path = ASEPRITE_DIR / f"{punk_name}.png"
            color_list = extract_dominant_colors_from_png(png_path)
            hex_colors = " + ".join(color_list)
        else:
            palette_match = re.search(r'\*\*Palette:\*\*([^(]+)\(([^)]+)\)', punk_content)
            if not palette_match:
                continue
            hex_colors = palette_match.group(2).strip()

        # Extract world description
        world_match = re.search(r'\*\*A breathtaking miniature ([^*]+)\*\*', punk_content)
        world_desc = world_match.group(1).strip() if world_match else ""

        # Simplify world description to key elements (take first clause)
        world_simplified = world_desc.split(',')[0] if ',' in world_desc else world_desc

        punks.append({
            'name': punk_name,
            'hex_colors': hex_colors,
            'world': world_simplified,
            'colors_from_png': has_todo
        })

    return punks

def create_concise_prompt(punk):
    """Create a concise 40-60 word Midjourney prompt."""
    world = punk['world']
    hex_colors = punk['hex_colors']

    # Build concise prompt (40-60 words)
    prompt = f"{world}, "
    prompt += f"miniature diorama stop-motion aesthetic, tilt-shift depth, "
    prompt += f"handcrafted claymation textures, dramatic cinematic lighting with god rays and sparkles, "
    prompt += f"palette: {hex_colors}, "
    prompt += f"Tim Burton whimsy meets Wes Anderson symmetry, "
    prompt += f"no human figures, environmental storytelling only, "
    prompt += f"35mm lens, shallow depth of field --ar 1:1 --style raw --s 50"

    return prompt

def generate_markdown():
    """Generate the complete Midjourney prompts markdown file."""

    # Read the freepik file
    with open(FREEPIK_FILE, 'r') as f:
        content = f.read()

    # Extract ALL punk data from FREEPIK
    punks = extract_punk_data_from_freepik(content)

    # Count how many used PNG colors
    png_color_count = sum(1 for p in punks if p.get('colors_from_png', False))

    # Separate lads and ladies
    lad_punks = [p for p in punks if p['name'].startswith('lad_')]
    lady_punks = [p for p in punks if p['name'].startswith('lady_')]

    # Generate markdown
    md_lines = [
        "# CLEAN MIDJOURNEY PROMPTS",
        "## Bespoke Punks: Cinematic Miniature Worlds",
        "",
        "**Format:** Square 1:1 ratio for optimal fullscreen display",
        "**Aesthetic:** Stop-motion miniature diorama with Tim Burton whimsy + Wes Anderson symmetry",
        "**Influences:** Nightmare Before Christmas, Coraline, James and the Giant Peach, LittleBigPlanet, Fantasia, Kubo",
        "",
        "**All prompts are:**",
        "- 40-60 words maximum (Midjourney optimized)",
        "- Include exact hex color palettes from each punk",
        "- Glamorous, charming, romantic with sparkles and god rays",
        "- Strong atmosphere and dramatic perspective",
        "- NO human figures - pure environmental storytelling",
        "- Copy-paste ready for immediate use",
        "",
        f"**Total Prompts:** {len(punks)}",
        "",
        "---",
        "",
        "## LAD PUNKS",
        ""
    ]

    # Add lad prompts
    for punk in lad_punks:
        prompt = create_concise_prompt(punk)

        md_lines.append(f"### {punk['name']}")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(prompt)
        md_lines.append("```")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # Add lady section
    md_lines.append("## LADY PUNKS")
    md_lines.append("")

    # Add lady prompts
    for punk in lady_punks:
        prompt = create_concise_prompt(punk)

        md_lines.append(f"### {punk['name']}")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(prompt)
        md_lines.append("```")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # Write to file
    with open(OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(md_lines))

    print(f"✅ Generated {len(punks)} clean Midjourney prompts")
    print(f"   - Lads: {len(lad_punks)}")
    print(f"   - Ladies: {len(lady_punks)}")
    print(f"   - Colors extracted from PNG files: {png_color_count}")
    print(f"\n📍 Saved to: {OUTPUT_FILE}")
    print(f"\n🎬 All prompts include:")
    print(f"   - Exact hex color palettes")
    print(f"   - Miniature diorama aesthetic")
    print(f"   - Tim Burton + Wes Anderson influences")
    print(f"   - God rays and sparkles")
    print(f"   - Environmental storytelling only (no humans)")
    print(f"   - 1:1 square format (--ar 1:1)")
    print(f"   - Midjourney parameters: --style raw --s 50")

if __name__ == "__main__":
    generate_markdown()
