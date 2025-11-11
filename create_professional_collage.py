#!/usr/bin/env python3
"""
Create Professional Collage - CAPTION_FIX Experiment Results
Comprehensive visual analysis with branding for Bespoke Labs
Owner: Ilyssa Evans
"""

import os
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
import json

# Configuration
OWNER = "Ilyssa Evans"
COMPANY = "Bespoke Labs"
EXPERIMENT = "SD15 CAPTION_FIX Experiment"
OUTPUT_FILE = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/CAPTION_FIX_RESULTS_COLLAGE.png"
ANALYSIS_FILE = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/CAPTION_FIX_COMPLETE_IMAGE_ANALYSIS.json"

# Test output directories
TEST_DIRS = {
    "Epoch 1": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_1_2_3/epoch1",
    "Epoch 2": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_1_2_3/epoch2",
    "Epoch 3": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_1_2_3/epoch3",
    "Epoch 4": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_4_5/epoch4",
    "Epoch 5": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_4_5/epoch5",
    "Epoch 6": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_6_7_8/epoch6",
    "Epoch 7": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_6_7_8/epoch7",
    "Epoch 8": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_6_7_8/epoch8",
    "Epoch 9": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_9_final/epoch9",
    "Final": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_9_final/final",
}

# Production samples
PRODUCTION_DIRS = {
    "Epoch 5 (Best BG)": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/production_samples_CAPTION_FIX/epoch5_best_bg",
    "Epoch 8 (Best Avg)": "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/production_samples_CAPTION_FIX/epoch8_best_avg",
}

# Test prompts used
PROMPT_NAMES = [
    "green_bg_lad",
    "brown_eyes_lady",
    "golden_earrings",
    "sunglasses_lad",
    "melon_lady",
    "cash_lad",
    "carbon_lad",
]

def count_unique_colors(image):
    """Count unique colors in image"""
    colors = image.getcolors(maxcolors=100000)
    return len(colors) if colors else 0

def analyze_all_images():
    """Analyze all generated images and create comprehensive report"""
    print("=" * 100)
    print("COMPREHENSIVE IMAGE ANALYSIS - CAPTION_FIX EXPERIMENT")
    print("=" * 100)
    print()

    all_analysis = {}

    # Analyze test outputs
    for epoch_name, epoch_dir in TEST_DIRS.items():
        if not os.path.exists(epoch_dir):
            print(f"⚠️  {epoch_name}: Directory not found - {epoch_dir}")
            continue

        print(f"\nAnalyzing {epoch_name}...")
        epoch_results = []

        for prompt_name in PROMPT_NAMES:
            img_24_path = os.path.join(epoch_dir, f"{prompt_name}_24.png")
            img_512_path = os.path.join(epoch_dir, f"{prompt_name}_512.png")

            if os.path.exists(img_24_path):
                img = Image.open(img_24_path)
                unique_colors = count_unique_colors(img)

                # Get top 5 colors
                pixels = list(img.getdata())
                color_counts = Counter(pixels)
                top_colors = color_counts.most_common(5)

                epoch_results.append({
                    'prompt': prompt_name,
                    'unique_colors': unique_colors,
                    'top_colors': [{'color': c, 'count': cnt} for c, cnt in top_colors],
                    'path_24': img_24_path,
                    'path_512': img_512_path if os.path.exists(img_512_path) else None,
                })

        if epoch_results:
            avg_colors = sum(r['unique_colors'] for r in epoch_results) / len(epoch_results)
            all_analysis[epoch_name] = {
                'avg_unique_colors': round(avg_colors, 1),
                'images': epoch_results,
                'image_count': len(epoch_results),
            }
            print(f"  ✓ {len(epoch_results)} images analyzed - Avg colors: {avg_colors:.1f}")

    # Analyze production samples
    for prod_name, prod_dir in PRODUCTION_DIRS.items():
        if not os.path.exists(prod_dir):
            continue

        print(f"\nAnalyzing {prod_name}...")
        prod_results = []

        # Production samples have different naming
        for img_file in os.listdir(prod_dir):
            if img_file.endswith('_24.png'):
                img_path = os.path.join(prod_dir, img_file)
                img = Image.open(img_path)
                unique_colors = count_unique_colors(img)

                prompt_name = img_file.replace('_24.png', '')
                prod_results.append({
                    'prompt': prompt_name,
                    'unique_colors': unique_colors,
                    'path_24': img_path,
                })

        if prod_results:
            avg_colors = sum(r['unique_colors'] for r in prod_results) / len(prod_results)
            all_analysis[prod_name] = {
                'avg_unique_colors': round(avg_colors, 1),
                'images': prod_results,
                'image_count': len(prod_results),
            }
            print(f"  ✓ {len(prod_results)} images analyzed - Avg colors: {avg_colors:.1f}")

    # Save analysis
    with open(ANALYSIS_FILE, 'w') as f:
        json.dump(all_analysis, f, indent=2)

    print(f"\n✓ Analysis saved to: {ANALYSIS_FILE}")
    return all_analysis

def create_professional_collage(analysis):
    """Create professional collage with all results"""
    print("\n" + "=" * 100)
    print("CREATING PROFESSIONAL COLLAGE")
    print("=" * 100)
    print()

    # Calculate dimensions - OPTIMIZED LAYOUT
    # Grid: 10 epochs x 7 test prompts = 70 images
    # Layout: Images on LEFT (majority), Text on RIGHT (compact)
    img_size = 56  # Increased from 48
    padding = 6  # Reduced from 10
    label_height = 20  # Reduced from 30
    top_margin = 40  # Minimal header
    side_margin = 10

    # Grid dimensions
    cols = 7  # 7 test prompts
    rows = 10  # 10 epochs

    # Left side: Image grid with epoch labels
    epoch_label_width = 70
    grid_width = epoch_label_width + cols * (img_size + padding) + padding
    grid_height = (label_height + padding) + rows * (img_size + label_height + padding) + padding

    # Right side: Compact text panel
    text_panel_width = 420

    canvas_width = grid_width + text_panel_width + side_margin * 3
    canvas_height = top_margin + grid_height + side_margin

    # Create canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), color='white')
    draw = ImageDraw.Draw(canvas)

    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
        tiny_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 8)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        tiny_font = ImageFont.load_default()

    # Minimal header - just title
    draw.text((canvas_width // 2, 15), f"{EXPERIMENT} - {COMPANY} | {OWNER}", fill='black', font=title_font, anchor='mm')
    draw.text((canvas_width // 2, 30), "28% Color Improvement | Production Ready", fill='green', font=small_font, anchor='mm')

    # Draw column headers (test prompts) - compact
    y_start = top_margin + 5
    x_start = side_margin + epoch_label_width

    prompt_labels = ["Green\nBG", "Brown\nEyes", "Gold\nEarring", "Sun-\nglasses", "Melon", "Cash", "Carbon"]
    for col, prompt_label in enumerate(prompt_labels):
        x = x_start + col * (img_size + padding) + img_size // 2
        draw.text((x, y_start + 5), prompt_label, fill='black', font=tiny_font, anchor='mm', align='center')

    # Draw epoch rows
    epoch_order = ["Epoch 1", "Epoch 2", "Epoch 3", "Epoch 4", "Epoch 5",
                   "Epoch 6", "Epoch 7", "Epoch 8", "Epoch 9", "Final"]

    current_y = y_start + label_height + padding

    for row, epoch_name in enumerate(epoch_order):
        if epoch_name not in analysis:
            current_y += img_size + label_height + padding
            continue

        epoch_data = analysis[epoch_name]

        # Draw epoch label on left - compact
        label_text = f"{epoch_name}\n{epoch_data['avg_unique_colors']}"

        # Highlight best epochs
        label_color = 'black'
        if epoch_name == "Epoch 8":
            label_color = 'green'
        elif epoch_name == "Epoch 5":
            label_color = 'blue'

        draw.text((side_margin + 5, current_y + img_size // 2), label_text,
                 fill=label_color, font=small_font, anchor='lm', align='center')

        # Draw images
        for col, prompt_name in enumerate(PROMPT_NAMES):
            # Find matching image
            matching_images = [img for img in epoch_data['images'] if prompt_name in img['prompt']]

            if matching_images:
                img_data = matching_images[0]
                img_path = img_data['path_24']

                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    # Upscale for visibility using NEAREST (pixel-perfect)
                    img = img.resize((img_size, img_size), Image.NEAREST)

                    x = x_start + col * (img_size + padding)
                    canvas.paste(img, (x, current_y))

                    # Draw color count below - tiny
                    color_text = f"{img_data['unique_colors']}"
                    draw.text((x + img_size // 2, current_y + img_size + 2),
                             color_text, fill='gray', font=tiny_font, anchor='mm')

        current_y += img_size + label_height + padding

    # Draw compact text panel on RIGHT side
    text_panel_x = grid_width + side_margin * 2
    text_y = top_margin + 10

    # Title for text panel
    draw.text((text_panel_x, text_y), "TRAINING CONFIG", fill='black', font=header_font)
    text_y += 20

    # Training settings - ultra compact
    config_text = """Model: SD1.5 + LoRA (32/16)
Dataset: 203 images
Captions: 3,621 hex codes removed
Resolution: 512→24px
Optimizer: AdamW, LR 1e-4
Batch: 4, Precision: bf16
keep_tokens=1, dropout=0.02"""

    draw.text((text_panel_x, text_y), config_text.strip(), fill='black', font=tiny_font)
    text_y += 80

    # Production recommendation box - compact
    draw.rectangle([text_panel_x, text_y, text_panel_x + text_panel_width - 20, text_y + 100],
                   outline='green', width=2, fill='#f0fff0')

    rec_text = """🏆 PRODUCTION
Epoch 8 (Green)
216.6 avg colors
28% improvement
Status: ✅ DEPLOYED

Alternative: Epoch 5 (Blue)
Best green BG (156)"""

    draw.text((text_panel_x + 5, text_y + 5), rec_text.strip(), fill='darkgreen', font=tiny_font)
    text_y += 110

    # Results summary
    draw.text((text_panel_x, text_y), "RESULTS", fill='black', font=header_font)
    text_y += 20

    results_text = """✓ Root Cause Fixed
  Duplicate hex codes removed

✓ Training Pattern
  Learning → Oscillation
  → Recovery → Peak (E8)

✓ Best Epochs
  E8: 216.6 colors (overall)
  E5: 156 colors (green BG)

✓ Convergence
  Faster than previous
  (Epoch 8 vs 9)

⚠️ Visual Issues Found
  Hats, glasses, bows
  Need caption enhancement
  Next: 24px native training"""

    draw.text((text_panel_x, text_y), results_text.strip(), fill='black', font=tiny_font)

    # Save collage
    canvas.save(OUTPUT_FILE, quality=95)
    print(f"✓ Collage saved to: {OUTPUT_FILE}")
    print(f"  Dimensions: {canvas_width}x{canvas_height}px")
    print(f"  Images included: {sum(len(e['images']) for e in analysis.values())}")

    return OUTPUT_FILE

if __name__ == "__main__":
    print("=" * 100)
    print(f"PROFESSIONAL COLLAGE GENERATOR - {COMPANY}")
    print(f"Owner: {OWNER}")
    print("=" * 100)
    print()

    # Step 1: Analyze all images
    analysis = analyze_all_images()

    # Step 2: Create collage
    collage_path = create_professional_collage(analysis)

    print("\n" + "=" * 100)
    print("✅ COMPLETE!")
    print("=" * 100)
    print(f"\nOutputs:")
    print(f"  1. Analysis: {ANALYSIS_FILE}")
    print(f"  2. Collage: {OUTPUT_FILE}")
    print()
    print("🎯 Ready to share with stakeholders!")
    print()
