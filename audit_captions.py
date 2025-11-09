#!/usr/bin/env python3
"""
Audit and improve Bespoke Punks captions for training accuracy.
Reviews images against CSV traits and generates enhanced captions.
"""

import csv
from pathlib import Path
from PIL import Image
import json

# Paths
CSV_PATH = "Context 1106/Bespoke Punks - Accurate Captions.csv"
IMAGES_DIR = Path("FORTRAINING6/bespokepunks")
OUTPUT_DIR = Path("caption_audit")
OUTPUT_DIR.mkdir(exist_ok=True)

def read_csv_data():
    """Read CSV and return punk data."""
    punks = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            punks.append(row)
    return punks

def analyze_image(image_path):
    """Analyze image for visual verification."""
    img = Image.open(image_path)
    width, height = img.size

    # Get background colors (top-left corner area)
    bg_colors = set()
    for x in range(min(5, width)):
        for y in range(min(5, height)):
            bg_colors.add(img.getpixel((x, y)))

    return {
        'size': (width, height),
        'bg_color_count': len(bg_colors),
        'is_likely_checkered': len(bg_colors) > 1
    }

def build_enhanced_caption(punk_data, img_analysis):
    """Build enhanced caption with all relevant details."""
    parts = []

    # Always start with base
    parts.append("bespoke")
    parts.append("24x24 pixel art portrait")

    # Background - CRITICAL: Include pattern type
    bg = punk_data['Background']
    bg_hex = punk_data['Background_Hex']
    bg_pattern = punk_data['Background_Pattern']

    if bg_pattern == 'checkered':
        parts.append(f"{bg} checkered pattern background ({bg_hex})")
    elif bg_pattern == 'gradient':
        parts.append(f"{bg} gradient background ({bg_hex})")
    elif bg_pattern == 'solid':
        parts.append(f"{bg} solid background ({bg_hex})")
    else:
        parts.append(f"{bg} background ({bg_hex})")

    # Hair (if present)
    hair = punk_data['Hair'].strip()
    if hair:
        parts.append(f"{hair} hair")

    # Eyes
    eyes = punk_data['Eyes'].strip()
    if eyes:
        if 'covered by' in eyes.lower():
            parts.append(f"{eyes}")
        else:
            parts.append(f"{eyes} eyes")

    # Skin tone
    skin = punk_data['Skin_Tone'].strip()
    if skin:
        parts.append(f"{skin} skin")

    # Headwear
    headwear = punk_data['Headwear'].strip()
    if headwear:
        parts.append(f"wearing {headwear}")

    # Facial hair
    facial_hair = punk_data['Facial_Hair'].strip()
    if facial_hair:
        parts.append(f"{facial_hair}")

    # Accessories
    accessories = punk_data['Accessories'].strip()
    if accessories and 'sunglasses' in accessories.lower() and 'covered by' not in eyes.lower():
        parts.append(f"{accessories}")
    elif accessories and 'sunglasses' not in accessories.lower():
        parts.append(f"{accessories}")

    # Clothing
    clothing = punk_data['Clothing'].strip()
    if clothing:
        parts.append(f"{clothing}")

    # Lips (for females)
    lips = punk_data['Lips'].strip()
    if lips:
        parts.append(f"{lips} lips")

    # Join with proper formatting
    caption = ", ".join(parts)

    # Add pixel art style reminder
    caption += ", pure pixel art with no gradients or anti-aliasing"

    return caption

def audit_all_punks():
    """Audit all punks and generate report."""
    punks = read_csv_data()

    report = []
    issues = []
    enhanced_captions = {}

    print(f"🔍 Auditing {len(punks)} punks...")
    print("=" * 80)

    for i, punk in enumerate(punks, 1):
        name = punk['Name']
        image_path = IMAGES_DIR / f"{name}.png"
        caption_path = IMAGES_DIR / f"{name}.txt"

        if not image_path.exists():
            issues.append(f"❌ {name}: Image file missing")
            continue

        if not caption_path.exists():
            issues.append(f"⚠️  {name}: Caption file missing")

        # Analyze image
        img_analysis = analyze_image(image_path)

        # Check for pattern discrepancies
        bg_pattern = punk['Background_Pattern']
        if bg_pattern == 'checkered' and not img_analysis['is_likely_checkered']:
            issues.append(f"⚠️  {name}: CSV says 'checkered' but image appears solid")
        elif bg_pattern == 'solid' and img_analysis['is_likely_checkered']:
            issues.append(f"⚠️  {name}: CSV says 'solid' but image appears checkered")

        # Build enhanced caption
        enhanced_caption = build_enhanced_caption(punk, img_analysis)
        enhanced_captions[name] = enhanced_caption

        # Read current caption
        current_caption = ""
        if caption_path.exists():
            with open(caption_path, 'r', encoding='utf-8') as f:
                current_caption = f.read().strip()

        # Compare
        if current_caption != enhanced_caption:
            report.append({
                'name': name,
                'current': current_caption,
                'enhanced': enhanced_caption,
                'diff': 'DIFFERENT'
            })

        if i % 20 == 0:
            print(f"  Processed {i}/{len(punks)} punks...")

    print("=" * 80)
    print(f"✅ Audit complete!\n")

    # Save report
    with open(OUTPUT_DIR / 'audit_report.txt', 'w', encoding='utf-8') as f:
        f.write("BESPOKE PUNKS CAPTION AUDIT REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total punks audited: {len(punks)}\n")
        f.write(f"Issues found: {len(issues)}\n")
        f.write(f"Captions needing update: {len(report)}\n\n")

        if issues:
            f.write("ISSUES FOUND:\n")
            f.write("-" * 80 + "\n")
            for issue in issues:
                f.write(f"{issue}\n")
            f.write("\n")

        if report:
            f.write("CAPTION UPDATES:\n")
            f.write("-" * 80 + "\n")
            for item in report[:10]:  # Show first 10
                f.write(f"\n{item['name']}:\n")
                f.write(f"  CURRENT:  {item['current']}\n")
                f.write(f"  ENHANCED: {item['enhanced']}\n")
            if len(report) > 10:
                f.write(f"\n... and {len(report) - 10} more\n")

    # Save enhanced captions as JSON
    with open(OUTPUT_DIR / 'enhanced_captions.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_captions, f, indent=2, ensure_ascii=False)

    print(f"📊 Issues found: {len(issues)}")
    print(f"📝 Captions needing update: {len(report)}")
    print(f"\n📁 Reports saved to: {OUTPUT_DIR}/")
    print(f"   - audit_report.txt")
    print(f"   - enhanced_captions.json")

    if issues:
        print("\n⚠️  ISSUES:")
        for issue in issues[:10]:
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more (see audit_report.txt)")

    return enhanced_captions, issues, report

if __name__ == "__main__":
    enhanced_captions, issues, report = audit_all_punks()

    print(f"\n✨ Enhanced captions ready for review!")
    print(f"   Use enhanced_captions.json to update caption files.")
