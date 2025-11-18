#!/usr/bin/env python3
"""
Generate clean, concise Midjourney prompts for ALL 211 Bespoke Punks from FREEPIK file.
"""

import re
from pathlib import Path

# Define base paths
REPO_ROOT = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2")
FREEPIK_FILE = REPO_ROOT / "bespoke-punks-website/FREEPIK_PROMPTS_MAGNIFICENT_2025-11-18.md"
OUTPUT_FILE = REPO_ROOT / "bespoke-punks-website/MIDJOURNEY_PROMPTS_CLEAN_2025-11-18.md"

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

        # Extract palette
        palette_match = re.search(r'\*\*Palette:\*\*([^(]+)\(([^)]+)\)', punk_content)
        if not palette_match:
            # No palette found, skip
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
            'world': world_simplified
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
    print(f"\n📍 Saved to: {OUTPUT_FILE}")
    print(f"\n🎬 All prompts include:")
    print(f"   - Exact hex color palettes")
    print(f"   - Miniature diorama aesthetic")
    print(f"   - Tim Burton + Wes Anderson influences")
    print(f"   - God rays and sparkles")
    print(f"   - Environmental storytelling only (no humans)")
    print(f"   - 1:1 square format")

if __name__ == "__main__":
    generate_markdown()
