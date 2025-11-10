#!/usr/bin/env python3
"""
CAPTION MERGER V3 - FINAL TRAINING PREPARATION
Intelligently merges user corrections with AI captions and validates against actual images
"""

import json
import os
import re
from PIL import Image
import numpy as np
from collections import Counter
from pathlib import Path

# Paths
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training"
SUPABASE_EXPORT = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/supabase_export_complete.json"

# Color mapping
def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def describe_color_advanced(r, g, b):
    """Enhanced color description with more nuance"""
    r, g, b = int(r), int(g), int(b)

    # Very dark/black
    if r < 30 and g < 30 and b < 30:
        return "black"

    # Very light/white
    if r > 230 and g > 230 and b > 230:
        return "white"

    # Grays
    if abs(r - g) < 20 and abs(g - b) < 20:
        if r < 60:
            return "dark gray"
        elif r < 120:
            return "medium gray"
        elif r < 180:
            return "light gray"
        else:
            return "very light gray"

    # Browns (multiple shades)
    if r > g and g > b and r - b > 30:
        if r > 160:
            return "light brown"
        elif r > 100:
            return "brown"
        else:
            return "dark brown"

    # Tans/beiges
    if 150 < r < 240 and 120 < g < 220 and 80 < b < 180:
        if r > g > b and r - b < 80:
            return "tan"

    # Reds/oranges
    if r > 120 and r > g + 30:
        if g > 80 and b < 80:
            return "orange"
        elif g > 100:
            return "orange-red"
        else:
            return "red"

    # Yellows/golds
    if r > 180 and g > 150 and b < 120:
        if abs(r - g) < 40:
            return "yellow"
        else:
            return "golden"

    # Pinks
    if r > 180 and g < 180 and b > 100:
        return "pink"

    # Purples/magentas
    if r > 80 and b > 80 and r > g and b > g:
        if abs(r - b) < 40:
            return "purple"
        elif r > b:
            return "magenta"
        else:
            return "violet"

    # Blues
    if b > r + 25 and b > g + 15:
        if b > 180:
            return "bright blue"
        elif b > 120:
            return "blue"
        else:
            return "dark blue"

    # Cyans/aquas
    if b > 100 and g > 100:
        if abs(b - g) < 40:
            if b > 180:
                return "bright cyan"
            else:
                return "cyan"

    # Greens
    if g > r + 25 and g > b + 25:
        if g > 180:
            return "bright green"
        elif g > 120:
            return "green"
        else:
            return "dark green"

    return f"mixed-{r}-{g}-{b}"

def sample_image_regions(image_path):
    """Sample colors from specific regions of the 24x24 pixel image"""
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)

    # Define regions for 24x24 pixel art (0-indexed)
    regions = {
        'hair_top': arr[0:8, :],           # Top 8 rows
        'hair_left': arr[4:12, 0:8],       # Left side hair
        'hair_right': arr[4:12, 16:24],    # Right side hair
        'eyes_left': arr[9:13, 7:11],      # Left eye
        'eyes_right': arr[9:13, 13:17],    # Right eye
        'face_center': arr[10:16, 8:16],   # Face/skin
        'nose': arr[13:15, 11:13],         # Nose area
        'mouth': arr[15:17, 9:15],         # Mouth/lips
        'chin': arr[17:20, 9:15],          # Chin/facial hair area
        'accessories_top': arr[5:10, 2:22],# Head accessories (hats, headbands)
        'earrings_left': arr[12:16, 2:6],  # Left earring area
        'earrings_right': arr[12:16, 18:22],# Right earring area
        'background_top_left': arr[0:6, 0:6],
        'background_top_right': arr[0:6, 18:24],
        'background_bottom_left': arr[18:24, 0:6],
        'background_bottom_right': arr[18:24, 18:24],
        'clothing_top': arr[16:20, 6:18],  # Upper clothing
        'clothing_bottom': arr[20:24, 8:16], # Lower clothing
    }

    sampled = {}
    for region_name, pixels in regions.items():
        if len(pixels.shape) == 3:
            pixels = pixels.reshape(-1, 3)

        if len(pixels) == 0:
            continue

        color_counts = Counter(tuple(int(c) for c in p) for p in pixels)
        top_colors = []

        for (r, g, b), count in color_counts.most_common(5):
            top_colors.append({
                'hex': rgb_to_hex(r, g, b),
                'rgb': [r, g, b],
                'count': count,
                'percentage': round((count / len(pixels)) * 100, 2),
                'description': describe_color_advanced(r, g, b)
            })

        sampled[region_name] = top_colors

    return sampled

def detect_hair_shape(hair_regions):
    """Detect hair shape/style from pixel patterns"""
    hair_top = hair_regions.get('hair_top', [])
    hair_left = hair_regions.get('hair_left', [])
    hair_right = hair_regions.get('hair_right', [])

    styles = []

    # Check volume (afro)
    if hair_left and hair_right and hair_top:
        left_count = sum(c['count'] for c in hair_left if c['description'] != 'background')
        right_count = sum(c['count'] for c in hair_right if c['description'] != 'background')
        top_count = sum(c['count'] for c in hair_top if c['description'] != 'background')

        # Afro: significant volume on both sides and top
        if left_count > 20 and right_count > 20 and top_count > 300:
            styles.append("afro")

    # Check for long hair (extends down sides)
    if hair_left and hair_right:
        if len(hair_left) > 3 or len(hair_right) > 3:
            styles.append("long")

    # Check for asymmetric (side-swept, parted)
    if hair_left and hair_right:
        left_vol = sum(c['count'] for c in hair_left)
        right_vol = sum(c['count'] for c in hair_right)
        if abs(left_vol - right_vol) > 30:  # Significant difference
            styles.append("side-swept")

    # Default descriptions
    if not styles:
        if hair_top:
            if len(hair_top) > 2:
                styles.append("short")
            else:
                styles.append("cropped")

    return ", ".join(styles) if styles else "short"

def detect_background_pattern(bg_corners):
    """Detect if background is solid, gradient, checkered, or split"""
    if not bg_corners:
        return "solid", None

    # Get top colors from each corner
    tl = bg_corners.get('background_top_left', [{}])[0].get('hex')
    tr = bg_corners.get('background_top_right', [{}])[0].get('hex')
    bl = bg_corners.get('background_bottom_left', [{}])[0].get('hex')
    br = bg_corners.get('background_bottom_right', [{}])[0].get('hex')

    colors = [c for c in [tl, tr, bl, br] if c]
    unique_colors = set(colors)

    if len(unique_colors) == 1:
        return "solid", list(unique_colors)[0]
    elif len(unique_colors) == 2:
        # Check if split (half and half)
        if tl == tr and bl == br and tl != bl:
            return "split-horizontal", list(unique_colors)
        elif tl == bl and tr == br and tl != tr:
            return "split-vertical", list(unique_colors)
        else:
            return "gradient", list(unique_colors)
    else:
        return "checkered", list(unique_colors)

def parse_user_corrections(user_text):
    """Extract traits from user's natural language corrections"""
    traits = {}
    text_lower = user_text.lower()

    # Hair keywords
    hair_keywords = {
        'afro': ['afro'],
        'long': ['long', 'flowing', 'dangling'],
        'short': ['short', 'cropped', 'buzzed'],
        'curly': ['curly', 'wavy', 'curls'],
        'straight': ['straight', 'sleek'],
        'messy': ['messy', 'fluffy', 'wild'],
        'styled': ['styled', 'gelled', 'polished', 'shiny', 'slick'],
        'parted': ['parted', 'side swept', 'side-swept'],
        'mohawk': ['mohawk'],
        'ponytail': ['ponytail', 'pony tail'],
        'bald': ['bald', 'balding'],
    }

    for style, keywords in hair_keywords.items():
        if any(kw in text_lower for kw in keywords):
            traits.setdefault('hair_style', []).append(style)

    # Eye color extraction
    eye_patterns = [
        r'(dark brown|light brown|medium brown|brown|blue|green|hazel|gray|grey|red|purple|cyan) eyes',
        r'eyes.*?(dark brown|light brown|medium brown|brown|blue|green|hazel|gray|grey|red|purple|cyan)',
    ]
    for pattern in eye_patterns:
        match = re.search(pattern, text_lower)
        if match:
            traits['eye_color'] = match.group(1)
            break

    # Accessories
    if 'sunglasses' in text_lower or 'shades' in text_lower:
        traits['sunglasses'] = True
    if 'glasses' in text_lower and 'sunglasses' not in text_lower:
        traits['glasses'] = True
    if 'earring' in text_lower:
        traits['earrings'] = True
    if 'hat' in text_lower or 'cap' in text_lower:
        traits['headwear'] = True

    # Facial hair
    if 'stubble' in text_lower or 'scruff' in text_lower:
        traits['facial_hair'] = 'stubble'
    elif 'beard' in text_lower:
        traits['facial_hair'] = 'beard'
    elif 'mustache' in text_lower or 'moustache' in text_lower:
        traits['facial_hair'] = 'mustache'

    # Skin tone descriptors
    skin_patterns = [
        r'(light|medium|dark|pale|tan|brown) skin',
        r'(light|medium|dark|pale|tan|brown) skinned',
    ]
    for pattern in skin_patterns:
        match = re.search(pattern, text_lower)
        if match:
            traits['skin_tone'] = match.group(1)
            break

    # Special instructions
    if 'get lip color' in text_lower or 'lip color' in text_lower:
        traits['include_lips'] = True

    return traits

def merge_caption_intelligent(filename, user_corrections, ai_caption, current_caption, sampled_regions, full_palette):
    """Merge captions with intelligent priority rules"""

    # Determine gender from filename
    gender = "lad" if "lad_" in filename else "lady"

    # Parse user corrections
    user_traits = parse_user_corrections(user_corrections)

    # Start building merged caption parts
    parts = []
    parts.append("pixel art, 24x24")
    parts.append(f"portrait of bespoke punk {gender}")

    # HAIR - User description takes priority
    # Extract hair info from user corrections (preserve their exact phrasing)
    hair_desc_user = None
    user_lower = user_corrections.lower()

    # Try to extract hair description from user text
    hair_sentences = []
    for sentence in user_corrections.split('.'):
        if 'hair' in sentence.lower():
            hair_sentences.append(sentence.strip())

    if hair_sentences:
        # User mentioned hair - use their description
        hair_desc_user = ', '.join(hair_sentences)
        # Clean up and format
        hair_desc_user = hair_desc_user.replace('\n', ' ').strip()

    # Sample actual hair colors from image
    hair_colors_sampled = []
    for region in ['hair_top', 'hair_left', 'hair_right']:
        if sampled_regions.get(region):
            top_color = sampled_regions[region][0]
            if top_color['description'] not in ['black', 'white', 'light gray', 'dark gray']:  # Not background
                hair_colors_sampled.append({
                    'color': top_color['description'],
                    'hex': top_color['hex']
                })

    # Hair shape from image analysis
    hair_shape = detect_hair_shape(sampled_regions)

    # Construct hair description
    if hair_desc_user:
        # Use user's description but add sampled colors if not mentioned
        parts.append(hair_desc_user)
    elif hair_colors_sampled:
        hair_color = hair_colors_sampled[0]['color']
        parts.append(f"{hair_color} {hair_shape} hair")

    # HEADWEAR / ACCESSORIES (HEAD)
    if user_traits.get('headwear'):
        # Extract headwear description from user text
        for sentence in user_corrections.split('.'):
            if any(kw in sentence.lower() for kw in ['hat', 'cap', 'crown', 'headband', 'visor']):
                parts.append(sentence.strip())
                break

    # FACIAL HAIR
    if user_traits.get('facial_hair'):
        parts.append(f"wearing {user_traits['facial_hair']}")

    # SUNGLASSES / GLASSES
    if user_traits.get('sunglasses'):
        # Extract sunglasses description
        for sentence in user_corrections.split('.'):
            if 'sunglasses' in sentence.lower() or 'shades' in sentence.lower():
                parts.append(sentence.strip())
                break
    elif user_traits.get('glasses'):
        for sentence in user_corrections.split('.'):
            if 'glasses' in sentence.lower():
                parts.append(sentence.strip())
                break

    # EARRINGS
    if user_traits.get('earrings'):
        for sentence in user_corrections.split('.'):
            if 'earring' in sentence.lower():
                parts.append(sentence.strip())
                break

    # EYES - Only if not covered by sunglasses
    if not user_traits.get('sunglasses'):
        if user_traits.get('eye_color'):
            # User specified eye color
            parts.append(f"{user_traits['eye_color']} eyes")
        else:
            # Sample from image
            eyes_left = sampled_regions.get('eyes_left', [])
            eyes_right = sampled_regions.get('eyes_right', [])
            if eyes_left and eyes_right:
                eye_color_left = eyes_left[0]['description']
                eye_color_right = eyes_right[0]['description']
                if eye_color_left == eye_color_right:
                    parts.append(f"{eye_color_left} eyes")
                else:
                    parts.append(f"heterochromia eyes (left {eye_color_left}, right {eye_color_right})")

    # LIPS - For ladies or if user requested
    if gender == "lady" or user_traits.get('include_lips'):
        mouth_region = sampled_regions.get('mouth', [])
        if mouth_region:
            lip_color = mouth_region[0]
            if lip_color['description'] not in ['black', 'dark gray']:  # Not just outline
                parts.append(f"{lip_color['description']} lips ({lip_color['hex']})")

    # SKIN TONE
    if user_traits.get('skin_tone'):
        parts.append(f"{user_traits['skin_tone']} skin")
    else:
        # Sample from image
        face_region = sampled_regions.get('face_center', [])
        if face_region:
            skin_color = face_region[0]
            parts.append(f"{skin_color['description']} skin ({skin_color['hex']})")

    # BACKGROUND
    bg_pattern, bg_colors = detect_background_pattern(sampled_regions)
    if bg_pattern == "solid" and bg_colors:
        # Check if user mentioned background
        bg_user = None
        for sentence in user_corrections.split('.'):
            if 'background' in sentence.lower():
                bg_user = sentence.strip()
                break

        if bg_user:
            parts.append(bg_user)
        else:
            bg_rgb = hex_to_rgb(bg_colors)
            bg_desc = describe_color_advanced(*bg_rgb)
            parts.append(f"{bg_desc} solid background ({bg_colors})")
    elif bg_pattern in ["split-horizontal", "split-vertical", "checkered", "gradient"]:
        colors_desc = [describe_color_advanced(*hex_to_rgb(c)) for c in bg_colors[:3]]
        parts.append(f"{bg_pattern} background ({', '.join(colors_desc)})")

    # CLOTHING
    clothing_user = []
    for sentence in user_corrections.split('.'):
        if any(kw in sentence.lower() for kw in ['shirt', 'jacket', 'suit', 'coat', 'hoodie', 'dress', 'top']):
            clothing_user.append(sentence.strip())

    if clothing_user:
        parts.extend(clothing_user)
    else:
        # Sample from image
        clothing_regions = sampled_regions.get('clothing_top', [])
        if clothing_regions:
            clothing_colors = [c['description'] for c in clothing_regions[:2]]
            parts.append(f"{', '.join(clothing_colors)} clothing")

    # COLOR PALETTE - Top 5 colors from image
    top_5_palette = [c['hex'] for c in full_palette[:5]]
    parts.append(f"palette: {', '.join(top_5_palette)}")

    # STYLE SUFFIX
    parts.append("sharp pixel edges, hard color borders, retro pixel art style")

    # Join all parts
    merged_caption = ", ".join([p for p in parts if p])

    return merged_caption, user_traits

def main():
    print("="*100)
    print("CAPTION MERGER V3 - FINAL TRAINING PREPARATION")
    print("="*100)
    print()

    # Load Supabase export
    print("📥 Loading user corrections from Supabase...")
    with open(SUPABASE_EXPORT, 'r') as f:
        data = json.load(f)

    print(f"✓ Loaded {len(data)} records")
    print()

    # Process each image
    results = []
    validation_issues = []

    print("🔍 Processing images and merging captions...")
    for i, record in enumerate(data, 1):
        filename = record['filename']
        print(f"  [{i}/{len(data)}] {filename}")

        image_path = os.path.join(TRAINING_DIR, filename)
        if not os.path.exists(image_path):
            print(f"    ⚠️  Image not found: {image_path}")
            validation_issues.append({
                'filename': filename,
                'issue': 'image_not_found',
                'severity': 'high'
            })
            continue

        # Sample colors from image
        sampled_regions = sample_image_regions(image_path)

        # Merge caption
        merged_caption, user_traits = merge_caption_intelligent(
            filename=filename,
            user_corrections=record['user_corrections'],
            ai_caption=record['ai_comprehensive_caption'],
            current_caption=record['current_caption'],
            sampled_regions=sampled_regions,
            full_palette=record['full_palette_15']
        )

        results.append({
            'filename': filename,
            'user_corrections': record['user_corrections'],
            'current_caption': record['current_caption'],
            'ai_comprehensive_caption': record['ai_comprehensive_caption'],
            'merged_caption_v3': merged_caption,
            'sampled_trait_colors': sampled_regions,
            'user_traits_extracted': user_traits,
            'full_palette_15': record['full_palette_15']
        })

    print()
    print(f"✓ Processed {len(results)} images")
    print()

    # Save results
    output_file = 'merged_captions_v3.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"💾 Saved merged captions to: {output_file}")

    # Save validation issues
    if validation_issues:
        with open('validation_issues.json', 'w') as f:
            json.dump(validation_issues, f, indent=2)
        print(f"⚠️  Found {len(validation_issues)} validation issues - saved to validation_issues.json")

    print()
    print("✅ Caption merging complete!")
    print()
    print("Next steps:")
    print("  1. Review merged_captions_v3.json")
    print("  2. Update Supabase with merged captions")
    print("  3. Generate final review UI")

if __name__ == "__main__":
    main()
