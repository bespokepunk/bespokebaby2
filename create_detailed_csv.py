#!/usr/bin/env python3
import csv
from pathlib import Path
from PIL import Image
import numpy as np
from collections import Counter

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex string"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color_name(rgb):
    """Get descriptive color name from RGB"""
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])

    # Define color thresholds
    if r < 30 and g < 30 and b < 30:
        return "Black"
    elif r > 225 and g > 225 and b > 225:
        return "White"
    elif r > 200 and g < 100 and b < 100:
        return "Red"
    elif r > 200 and g > 100 and g < 180 and b < 100:
        return "Orange"
    elif r > 200 and g > 200 and b < 100:
        return "Yellow"
    elif r < 100 and g > 150 and b < 100:
        return "Green"
    elif r < 100 and g < 150 and b > 200:
        return "Blue"
    elif r > 150 and g < 100 and b > 150:
        return "Purple"
    elif r > 200 and g > 100 and b > 150:
        return "Pink"
    elif r > 180 and g > 150 and b > 200:
        return "Lavender"
    elif r > 150 and g > 100 and b < 80:
        return "Brown"
    elif 80 < r < 150 and 80 < g < 150 and 80 < b < 150:
        return "Grey"
    elif r > 100 and g > 50 and b < 50 and r > g:
        return "Burgundy"
    elif r < 150 and g > 100 and b > 150:
        return "Teal"
    elif r > 150 and g > 150 and b < 150:
        return "Beige"
    else:
        return f"RGB({r},{g},{b})"

def analyze_background(img_array):
    """Analyze background with detailed color info"""
    h, w = img_array.shape[:2]

    # Sample corners and edges
    corners = [
        img_array[0, 0],
        img_array[0, w-1],
        img_array[h-1, 0],
        img_array[h-1, w-1]
    ]

    # Get unique colors in corners
    corner_colors = []
    for corner in corners:
        if len(corner) >= 3:
            corner_colors.append(tuple(corner[:3]))

    unique_colors = list(set(corner_colors))

    if len(unique_colors) == 1:
        # Solid background
        color = unique_colors[0]
        hex_val = rgb_to_hex(color)
        name = get_color_name(color)
        return f"{name} {hex_val}", "solid"
    else:
        # Gradient or patterned
        color_names = [get_color_name(c) for c in unique_colors]
        hex_vals = [rgb_to_hex(c) for c in unique_colors]

        # Check if it's a gradient by sampling the edge
        top_edge = img_array[0, :, :3]
        unique_edge_colors = len(np.unique(top_edge.reshape(-1, 3), axis=0))

        if unique_edge_colors > 2:
            pattern_type = "gradient"
        else:
            pattern_type = "pattern"

        desc = " to ".join([f"{n} {h}" for n, h in zip(color_names[:3], hex_vals[:3])])
        return desc, pattern_type

def get_dominant_colors(region, n=3):
    """Get top N dominant colors from region"""
    if region.size == 0:
        return []

    pixels = region.reshape(-1, region.shape[-1])
    if pixels.shape[1] >= 3:
        pixels = pixels[:, :3]

    pixel_tuples = [tuple(p) for p in pixels]
    counter = Counter(pixel_tuples)
    most_common = counter.most_common(n)

    return [(rgb, count) for rgb, count in most_common]

def analyze_hair(img_array):
    """Analyze hair with detailed description"""
    h, w = img_array.shape[:2]

    # Sample hair region (top 40% of image, avoiding edges)
    hair_region = img_array[0:int(h*0.4), int(w*0.2):int(w*0.8), :3]

    dominant = get_dominant_colors(hair_region, n=3)

    if not dominant:
        return "", ""

    # Filter out background/skin colors
    hair_colors = []
    for rgb, count in dominant:
        r, g, b = rgb
        # Skip very light (skin) or colors that appear in background
        if not (r > 200 and g > 150 and b > 130):  # Not skin tone
            color_name = get_color_name(rgb)
            hex_val = rgb_to_hex(rgb)
            hair_colors.append((color_name, hex_val, count))

    if len(hair_colors) == 0:
        return "", ""
    elif len(hair_colors) == 1:
        return f"{hair_colors[0][0]} {hair_colors[0][1]}", hair_colors[0][0]
    else:
        # Multiple colors - checkered, split, or gradient
        desc = " and ".join([f"{c[0]} {c[1]}" for c in hair_colors[:2]])
        colors = " and ".join([c[0] for c in hair_colors[:2]])
        return desc, colors

def analyze_eyes(img_array):
    """Analyze eye color"""
    h, w = img_array.shape[:2]

    # Sample eye region (around middle, standard eye positions)
    eye_y = int(h * 0.5)
    eye_region = img_array[eye_y-2:eye_y+2, int(w*0.25):int(w*0.75), :3]

    dominant = get_dominant_colors(eye_region, n=5)

    # Filter out black (pupils), skin, and background
    eye_colors = []
    for rgb, count in dominant:
        r, g, b = rgb
        if not (r < 50 and g < 50 and b < 50):  # Not black
            if not (r > 180 and g > 130):  # Not skin
                color_name = get_color_name(rgb)
                hex_val = rgb_to_hex(rgb)
                eye_colors.append((color_name, hex_val))

    if eye_colors:
        return f"{eye_colors[0][0]} {eye_colors[0][1]}", eye_colors[0][0]
    return "", ""

def detect_headwear(img_array, filename):
    """Detect specific headwear types"""
    h, w = img_array.shape[:2]

    # Sample top region
    top_region = img_array[0:int(h*0.3), :, :3]

    # Check for distinctive shapes/colors
    headwear_types = []

    # Check filename for hints
    if 'chef' in filename.lower() or 'Dalia' in filename:
        dominant = get_dominant_colors(top_region, n=3)
        if dominant:
            color = get_color_name(dominant[0][0])
            hex_val = rgb_to_hex(dominant[0][0])
            return f"{color} chef hat {hex_val}", f"{color} chef hat"

    if 'crown' in filename.lower() or 'sterling' in filename.lower():
        dominant = get_dominant_colors(top_region, n=3)
        colors_desc = []
        for rgb, _ in dominant[:2]:
            color = get_color_name(rgb)
            hex_val = rgb_to_hex(rgb)
            colors_desc.append(f"{color} {hex_val}")
        return f"{' and '.join(colors_desc)} crown", "crown"

    if 'cap' in filename.lower() or 'hat' in filename.lower() or 'nitrogen' in filename:
        dominant = get_dominant_colors(top_region, n=2)
        if dominant:
            color = get_color_name(dominant[0][0])
            hex_val = rgb_to_hex(dominant[0][0])
            return f"{color} cap {hex_val}", f"{color} cap"

    # Check for distinctive white on top (chef hat pattern)
    white_pixels = np.sum((top_region[:, :, 0] > 200) & (top_region[:, :, 1] > 200) & (top_region[:, :, 2] > 200))
    if white_pixels > (top_region.shape[0] * top_region.shape[1] * 0.3):
        return "White chef hat #FFFFFF", "White chef hat"

    return "", ""

def detect_accessories(img_array, filename):
    """Detect accessories like glasses, bows, earrings, bear ears"""
    accessories = []
    h, w = img_array.shape[:2]

    # Check filename for hints
    if 'bear' in filename.lower() or 'Dalia' in filename:
        accessories.append("bear ears")
    if 'cat' in filename.lower():
        accessories.append("cat ears")
    if 'glasses' in filename.lower() or 'sunglasses' in filename.lower():
        # Try to detect glasses color
        mid_region = img_array[int(h*0.4):int(h*0.6), :, :3]
        dominant = get_dominant_colors(mid_region, n=5)
        for rgb, _ in dominant:
            color = get_color_name(rgb)
            if color in ["Red", "Brown", "Black", "Grey"]:
                accessories.append(f"{color.lower()} glasses")
                break
        if not any('glasses' in a for a in accessories):
            accessories.append("glasses")

    if 'bow' in filename.lower() or 'Dalia' in filename:
        # Detect bow color from side regions
        side_region = img_array[:, :int(w*0.2), :3]
        dominant = get_dominant_colors(side_region, n=3)
        if dominant:
            color = get_color_name(dominant[0][0])
            if color not in ["Black", "White"]:  # Likely not hair or background
                accessories.append(f"{color.lower()} bows")

    return ", ".join(accessories)

def analyze_image_detailed(image_path):
    """Comprehensive image analysis"""
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        filename = image_path.stem

        # Analyze each component
        bg_detailed, bg_type = analyze_background(img_array)
        hair_detailed, hair_simple = analyze_hair(img_array)
        eyes_detailed, eyes_simple = analyze_eyes(img_array)
        headwear_detailed, headwear_simple = detect_headwear(img_array, filename)
        accessories = detect_accessories(img_array, filename)

        # Generate training caption
        caption_parts = []
        caption_parts.append(f"24x24 pixel art portrait")
        caption_parts.append(f"background: {bg_detailed}")
        if hair_detailed:
            caption_parts.append(f"hair: {hair_detailed}")
        if eyes_detailed:
            caption_parts.append(f"eyes: {eyes_detailed}")
        if headwear_detailed:
            caption_parts.append(f"wearing {headwear_detailed}")
        if accessories:
            caption_parts.append(f"accessories: {accessories}")

        training_caption = ", ".join(caption_parts)

        return {
            'background_detailed': bg_detailed,
            'background_type': bg_type,
            'hair_detailed': hair_detailed,
            'hair_simple': hair_simple,
            'eyes_detailed': eyes_detailed,
            'eyes_simple': eyes_simple,
            'headwear_detailed': headwear_detailed,
            'headwear_simple': headwear_simple,
            'accessories': accessories,
            'training_caption': training_caption
        }
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
        return None

def main():
    images_dir = "FORTRAINING6/bespokepunks"
    output_csv = "Context 1106/Bespoke Punks - Detailed Captions.csv"

    print("Analyzing images for detailed attributes...")
    image_files = sorted(Path(images_dir).glob("*.png"))

    # Create CSV
    fieldnames = [
        'Name',
        'Type',
        'Background_Detailed',
        'Background_Type',
        'Hair_Detailed',
        'Hair_Simple',
        'Eyes_Detailed',
        'Eyes_Simple',
        'Headwear_Detailed',
        'Headwear_Simple',
        'Accessories',
        'Training_Caption'
    ]

    rows = []

    for i, img_path in enumerate(image_files, 1):
        name = img_path.stem
        print(f"  [{i}/{len(image_files)}] Analyzing {name}...")

        # Determine type
        if name.startswith('lady_'):
            type_val = "Female"
        elif name.startswith('lad_'):
            type_val = "Male"
        else:
            type_val = ""

        # Analyze image
        attrs = analyze_image_detailed(img_path)

        if attrs:
            row = {
                'Name': name,
                'Type': type_val,
                'Background_Detailed': attrs['background_detailed'],
                'Background_Type': attrs['background_type'],
                'Hair_Detailed': attrs['hair_detailed'],
                'Hair_Simple': attrs['hair_simple'],
                'Eyes_Detailed': attrs['eyes_detailed'],
                'Eyes_Simple': attrs['eyes_simple'],
                'Headwear_Detailed': attrs['headwear_detailed'],
                'Headwear_Simple': attrs['headwear_simple'],
                'Accessories': attrs['accessories'],
                'Training_Caption': attrs['training_caption']
            }
            rows.append(row)

    # Write CSV
    print(f"\nWriting detailed CSV with {len(rows)} entries...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Done! Created {output_csv}")
    print(f"   Total entries: {len(rows)}")

if __name__ == "__main__":
    main()
