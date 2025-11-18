#!/usr/bin/env python3
"""
Generate clean, concise Midjourney prompts for ALL Bespoke Punks world images.
This version creates prompts for all PNG files, using FREEPIK data where available.
"""

import re
from pathlib import Path
from collections import defaultdict

# Define base paths
REPO_ROOT = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2")
FREEPIK_FILE = REPO_ROOT / "bespoke-punks-website/FREEPIK_PROMPTS_MAGNIFICENT_2025-11-18.md"
OUTPUT_FILE = REPO_ROOT / "bespoke-punks-website/MIDJOURNEY_PROMPTS_CLEAN_2025-11-18.md"
ASEPRITE_DIR = REPO_ROOT / "Aseperite/all"

# Thematic mappings based on punk names
THEME_MAP = {
    'carbon': 'twilight alleyway with shadows and forgotten stories',
    'cash': 'crystalline vault where fortune glows',
    'chai': 'cozy tea sanctuary with steam and warmth',
    'silicon': 'minimalist tech workspace',
    'copper': 'warm metallic workshop',
    'redshift': 'cosmic observatory with starlight',
    'titanium': 'sleek industrial space',
    'platinum': 'luxury gallery with prismatic light',
    'steel': 'morning training ground',
    'aluminum': 'retro neon gymnasium',
    'chocolate': 'cozy cafe with rich warmth',
    'chromium': 'reflective metallic chamber',
    'caramel': 'golden bakery paradise',
    'sugar': 'sweet confectionery wonderland',
    'jackson': 'moonlit dance floor',
    'tungsten': 'glowing industrial forge',
    'ink': 'mysterious calligraphy studio',
    'mandarin': 'serene asian garden',
    'diamond': 'crystalline palace',
    'gpu': 'cyberpunk data center',
    'famous': 'glamorous stage with spotlights',
    'fin': 'aquatic underwater realm',
    'shaman': 'mystical ritual chamber',
    'molecule': 'abstract scientific laboratory',
    'JUAN': 'vibrant soccer stadium',
    'aressprout': 'mythic training arena',
    'cashking': 'opulent treasure room',
    'davinci': 'renaissance artist studio',
    'melzarmagic': 'magical wizard sanctum',
    'Maradona': 'legendary football pitch',
    'jeremey': 'creative maker space',
    'homewithkids': 'warm family living room',
    'NATE': 'dynamic urban workspace',
    'gainzyyyy': 'fitness training zone',
    'nate': 'modern minimalist office',
    'DEVON': 'sophisticated lounge',
    'sterling': 'elegant gentleman study',
    'Luke': 'adventurous explorer space',
    'Hugh': 'classic library reading room',
    'SAVVA': 'mystical meditation chamber',
    'SamAScientist': 'scientific research lab',
    'bhaitradingbot': 'futuristic trading floor',
    'DOPE': 'street art urban gallery',
    'devox': 'tech developer workspace',
    'kenichi': 'samurai training dojo',
    'Scott': 'mountain climbing base',
    'sensei': 'peaceful zen temple',
    'napoli': 'italian coastal terrace',
    'mayor': 'grand city hall chamber',
    'IRAsBF': 'romantic garden gazebo',
    'lc': 'minimalist creative studio',
    'mmhm': 'cozy reading nook',
    'btoshi': 'digital currency vault',
    'ravish': 'glamorous fashion runway',
    'fcpo': 'peaceful meditation space',
    'iggy': 'punk rock music venue',
    'Scooby': 'mystery investigation room',
    'HEEM': 'basketball court',
    'Kareem': 'championship basketball arena',
    'aguda': 'tropical paradise retreat',
    'drscott': 'medical research facility',
    'amit': 'innovative tech lab',
    'derrick': 'basketball training court',
    'photogee': 'photography studio',
    'storm': 'dramatic weather observatory',
    'godfather': 'vintage italian restaurant',
    'apollo': 'space mission control',
    'drralph': 'botanical garden greenhouse',
    'Murtaza': 'elegant tea lounge',
    'amenshiller': 'mystical crypto temple',
    'bunya': 'australian outback campsite',
    'merheb': 'mediterranean villa terrace',
    'inkspired': 'tattoo artist studio',
    'sultan': 'arabian palace courtyard',
}

LADY_THEME_MAP = {
    'lemon': 'sunny citrus kitchen',
    'hazelnut': 'cozy autumn cafe',
    'vanilla': 'elegant pastry shop',
    'cashew': 'warm nutty bakery',
    'nutmeg': 'spice merchant stall',
    'cinnamon': 'aromatic spice kitchen',
    'pepper': 'vibrant market stall',
    'alloy': 'sleek metallic workspace',
    'pinksilk': 'luxurious fabric boutique',
    'bluesilk': 'serene textile studio',
    'saffron': 'golden spice bazaar',
    'sage': 'herbal apothecary',
    'parasite': 'dark mysterious laboratory',
    'rosemary': 'herb garden sanctuary',
    'olive': 'mediterranean grove',
    'lime': 'fresh citrus bar',
    'honey': 'golden bee garden',
    'pine': 'forest cabin retreat',
    'strawberry': 'berry patch paradise',
    'banana': 'tropical fruit market',
    'blood': 'gothic vampire chamber',
    'diamond': 'crystalline jewelry vault',
    'gold': 'treasure chamber',
    'silver': 'moonlit metallic gallery',
    'linen': 'vintage fabric shop',
    'mistletoe': 'winter holiday cottage',
    'fur': 'cozy winter lodge',
    'nitrogen': 'ice laboratory',
    'marshmallow': 'candy wonderland',
    'basil': 'italian herb garden',
    'grass': 'meadow picnic spot',
    'paprika': 'spicy market booth',
    'salt': 'ocean salt flats',
    'staranise': 'exotic spice collection',
    'lavender': 'purple flower field',
    'turmeric': 'golden spice market',
    'boisenberry': 'berry garden sanctuary',
    'rose': 'romantic rose garden',
    'peanut': 'cozy snack cafe',
    'sandalwood': 'incense meditation room',
    'fivespice': 'asian spice market',
    'bayleaf': 'herb drying room',
    'almond': 'orchard blossom grove',
    'orange': 'citrus grove sunset',
    'pink': 'pastel dream room',
    'abstractangels': 'ethereal cloud realm',
    'rosieabstract': 'abstract art gallery',
    'pinksilkabstract': 'flowing fabric dimension',
    'pepperabstract': 'spicy color explosion',
    'hazelnutabstract': 'geometric autumn space',
    'bloodabstract': 'crimson abstract void',
    'alloyabstract': 'metallic geometric realm',
    'bluesilkabstract': 'flowing blue dimension',
    'paula': 'vintage music lounge',
    'winehouse': 'soulful jazz club',
    'nikkkk': 'glamorous fashion studio',
    'Dalia': 'elegant flower shop',
    'PVR': 'cinematic movie theater',
    'aubree': 'artistic creative space',
    'miggs': 'street art studio',
    'monalisa': 'renaissance museum',
    'salamander': 'mystical creature habitat',
    'nikkisf': 'san francisco sunset view',
    'giulia': 'italian countryside villa',
    'mango': 'tropical fruit paradise',
    'papaya': 'exotic fruit garden',
    'tangerine': 'citrus sunset grove',
    'mango_punk': 'street art tropical space',
    'melon': 'watermelon patch',
    'clementine': 'orange grove morning',
    'orange_blossom': 'flowering citrus trees',
    'pink_grapefruit': 'pastel citrus garden',
    'orange_zest': 'bright citrus kitchen',
    'lime_breeze': 'tropical lime orchard',
    'zesty_lime': 'vibrant lime bar',
    'Marianne': 'parisian cafe terrace',
    'IRA': 'romantic cottage garden',
    'ELENI': 'greek island terrace',
    'feybirthday': 'magical birthday party',
    'missthang': 'glamorous runway',
    'violetta': 'purple flower conservatory',
    'royalty': 'regal throne room',
    'yuri': 'anime art studio',
    'dani': 'modern creative workspace',
    'heyeah': 'energetic dance studio',
    'VQ': 'sophisticated lounge',
    'domino': 'vintage game parlor',
}

def get_punk_theme(punk_name):
    """Get thematic description based on punk name."""
    # Remove punk prefix and extract base name
    name_part = punk_name.replace('lad_', '').replace('lady_', '')
    name_part = re.sub(r'^\d+_', '', name_part)  # Remove number prefix
    name_part = re.sub(r'-?\d+$', '', name_part)  # Remove trailing numbers
    name_part = name_part.replace(' copy', '').replace(' 2', '').strip()

    # Check lady themes first
    for key, theme in LADY_THEME_MAP.items():
        if key.lower() in name_part.lower():
            return theme

    # Check lad themes
    for key, theme in THEME_MAP.items():
        if key.lower() in name_part.lower():
            return theme

    # Default theme
    if 'lady' in punk_name:
        return 'enchanting miniature world with sparkling atmosphere'
    else:
        return 'captivating miniature space with dramatic lighting'

def extract_punk_data_from_freepik(content):
    """Extract punk data from FREEPIK file."""
    punks = {}

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

        hex_colors = palette_match.group(2).strip()

        # Extract world description
        world_match = re.search(r'\*\*A breathtaking miniature ([^*]+)\*\*', punk_content)
        world_desc = world_match.group(1).strip() if world_match else ""

        # Simplify world description to key elements
        world_simplified = world_desc.split(',')[0] if ',' in world_desc else world_desc

        punks[punk_name] = {
            'hex_colors': hex_colors,
            'world': world_simplified
        }

    return punks

def create_concise_prompt(punk_name, freepik_data=None):
    """Create a concise 40-60 word Midjourney prompt."""

    if freepik_data and punk_name in freepik_data:
        world = freepik_data[punk_name]['world']
        hex_colors = freepik_data[punk_name]['hex_colors']
    else:
        world = get_punk_theme(punk_name)
        hex_colors = "#000000 + #ffffff + #808080"  # Default colors

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

    # Extract punk data from FREEPIK
    freepik_data = extract_punk_data_from_freepik(content)

    # Get all PNG files
    png_files = sorted(ASEPRITE_DIR.glob("*.png"))
    punk_names = [f.stem for f in png_files]

    # Filter out "copy" files and "other/" subdirectory
    punk_names = [name for name in punk_names if ' copy' not in name.lower()]

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
        f"**Total Prompts:** {len(punk_names)}",
        "",
        "---",
        "",
        "## LAD PUNKS",
        ""
    ]

    # Separate lads and ladies
    lad_punks = [p for p in punk_names if p.startswith('lad_')]
    lady_punks = [p for p in punk_names if p.startswith('lady_')]

    # Add lad prompts
    for punk_name in lad_punks:
        prompt = create_concise_prompt(punk_name, freepik_data)

        md_lines.append(f"### {punk_name}")
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
    for punk_name in lady_punks:
        prompt = create_concise_prompt(punk_name, freepik_data)

        md_lines.append(f"### {punk_name}")
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

    print(f"Generated {len(punk_names)} Midjourney prompts")
    print(f"  - Lads: {len(lad_punks)}")
    print(f"  - Ladies: {len(lady_punks)}")
    print(f"  - Using FREEPIK data for: {len(freepik_data)} punks")
    print(f"  - Generated fallback themes for: {len(punk_names) - len([p for p in punk_names if p in freepik_data])} punks")
    print(f"\nSaved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_markdown()
