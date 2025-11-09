#!/usr/bin/env python3
"""
Update all captions for pixel art base model training
- Add "pixel art" trigger
- Simplify structure (base handles style)
- Fix gradient terminology
- Remove redundant phrases
"""

from pathlib import Path
import shutil

def update_caption(old_caption):
    """Transform old caption to new pixel art base format"""

    # Start with pixel art trigger
    new = "pixel art, 24x24, portrait of bespoke punk, "

    # Remove old prefix if exists
    old = old_caption.replace("bespoke, ", "")
    old = old.replace("24x24 pixel art portrait, ", "")
    old = old.replace("24x24 pixel grid portrait, ", "")

    # Fix gradient backgrounds
    if "gradient background" in old and "pixelated" not in old:
        old = old.replace("gradient background", "pixelated gradient background with stepped color transitions")

    # Remove problematic phrases
    old = old.replace("pure pixel art with no gradients or anti-aliasing", "sharp pixel edges, hard color borders")
    old = old.replace("no gradients or anti-aliasing", "sharp pixel edges, hard color borders")
    old = old.replace("pure pixel art", "")

    # Remove "symbolic punk style" (redundant)
    old = old.replace("symbolic punk style, ", "")
    old = old.replace("symbolic punk style", "")

    # Clean up coordinate specs (keep them but simplify)
    # These are still valuable for training

    # Add the rest of the caption
    new += old.strip()

    # Clean up double spaces and commas
    new = new.replace("  ", " ")
    new = new.replace(", ,", ",")
    new = new.replace(",,", ",")

    # Ensure it ends with sharp pixel edges
    if "sharp pixel edges" not in new:
        new += ", sharp pixel edges, hard color borders"

    return new.strip()

def main():
    print("📝 UPDATING CAPTIONS FOR PIXEL ART BASE MODEL")
    print("="*80)

    caption_dir = Path("FORTRAINING6/bespokepunks")
    backup_dir = Path("FORTRAINING6/bespokepunks_captions_backup")
    backup_dir.mkdir(exist_ok=True)

    print(f"\n📁 Caption directory: {caption_dir}/")
    print(f"📁 Backup directory: {backup_dir}/")
    print()

    count = 0
    updated = []

    for txt_path in sorted(caption_dir.glob("*.txt")):
        # Backup original
        backup_path = backup_dir / txt_path.name
        shutil.copy(txt_path, backup_path)

        # Read old caption
        with open(txt_path, 'r') as f:
            old_caption = f.read().strip()

        # Update caption
        new_caption = update_caption(old_caption)

        # Write new caption
        with open(txt_path, 'w') as f:
            f.write(new_caption)

        count += 1
        updated.append({
            'file': txt_path.name,
            'old': old_caption[:80] + "..." if len(old_caption) > 80 else old_caption,
            'new': new_caption[:80] + "..." if len(new_caption) > 80 else new_caption
        })

        print(f"✅ {count:3d}. {txt_path.name}")

    print()
    print("="*80)
    print(f"✅ Updated {count} captions")
    print(f"📁 Originals backed up to: {backup_dir}/")
    print()
    print("Sample updates:")
    for item in updated[:3]:
        print(f"\n📄 {item['file']}")
        print(f"  OLD: {item['old']}")
        print(f"  NEW: {item['new']}")

    print()
    print("Next steps:")
    print("  1. Review updated captions")
    print("  2. Package for training with edge maps")
    print("  3. Upload to CivitAI training")

if __name__ == "__main__":
    main()
