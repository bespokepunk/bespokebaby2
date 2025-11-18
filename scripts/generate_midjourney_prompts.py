#!/usr/bin/env python3
"""
Generate clean, concise Midjourney prompts for all Bespoke Punks world images.
"""

import re
from pathlib import Path

# Define base paths
REPO_ROOT = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2")
FREEPIK_FILE = REPO_ROOT / "bespoke-punks-website/FREEPIK_PROMPTS_MAGNIFICENT_2025-11-18.md"
OUTPUT_FILE = REPO_ROOT / "bespoke-punks-website/MIDJOURNEY_PROMPTS_CLEAN_2025-11-18.md"

def extract_punk_data(content):
    """Extract punk name, palette, and world description from content."""
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

        # Extract palette
        palette_match = re.search(r'\*\*Palette:\*\*([^(]+)\(([^)]+)\)', punk_content)
        if not palette_match:
            continue

        color_names = palette_match.group(1).strip()
        hex_colors = palette_match.group(2).strip()

        # Extract world description (the breathtaking line)
        world_match = re.search(r'\*\*A breathtaking miniature ([^*]+)\*\*', punk_content)
        world_desc = world_match.group(1).strip() if world_match else ""

        # Extract style
        style_match = re.search(r'\*\*Style:\*\*\s*(.+)', punk_content)
        style = style_match.group(1).strip() if style_match else "Miniature diorama"

        punks.append({
            'name': punk_name,
            'color_names': color_names,
            'hex_colors': hex_colors,
            'world': world_desc,
            'style': style
        })

    return punks

def create_concise_prompt(punk):
    """Create a concise 40-60 word Midjourney prompt."""

    # Extract core concept from world description
    world = punk['world']

    # Simplify to key elements
    world_simplified = world.split(',')[0] if ',' in world else world

    # Build concise prompt
    prompt = f"{world_simplified}, "
    prompt += f"miniature diorama stop-motion aesthetic, tilt-shift depth, "
    prompt += f"handcrafted claymation textures, dramatic cinematic lighting with god rays and sparkles, "
    prompt += f"palette: {punk['hex_colors']}, "
    prompt += f"Tim Burton whimsy meets Wes Anderson symmetry, "
    prompt += f"no human figures, environmental storytelling only, "
    prompt += f"35mm lens, shallow depth of field --ar 1:1 --style raw --s 50"

    return prompt

def generate_markdown():
    """Generate the complete Midjourney prompts markdown file."""

    # Read the freepik file
    with open(FREEPIK_FILE, 'r') as f:
        content = f.read()

    # Extract punk data
    punks = extract_punk_data(content)

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
        "- Include exact hex color palettes",
        "- Glamorous, charming, romantic with sparkles",
        "- NO human figures - pure environmental storytelling",
        "- Copy-paste ready for immediate use",
        "",
        "---",
        "",
        "## PROMPTS",
        ""
    ]

    # Add each punk prompt
    for punk in punks:
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

    print(f"Generated {len(punks)} Midjourney prompts")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_markdown()
