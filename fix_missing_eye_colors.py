#!/usr/bin/env python3
"""
Fix Missing Eye Colors Tool

Quickly add missing eye colors to the 106 captions that need them.
Shows image + current caption, you input the eye color.
"""

import gradio as gr
from pathlib import Path
from PIL import Image
import json
import re

V4_DIR = Path("improved_samples_v4")
OUTPUT_DIR = Path("improved_samples_v5")
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR = Path("runpod_package/training_data")

class EyeColorFixer:
    def __init__(self):
        self.load_captions_missing_eyes()
        self.current_index = 0
        self.fixes = {}

    def load_captions_missing_eyes(self):
        """Load only captions that are missing eye colors"""
        self.records = []

        # Eye color patterns to check for
        eye_patterns = [
            r'\bbrown eyes\b', r'\bblue eyes\b', r'\bgreen eyes\b',
            r'\bhazel eyes\b', r'\bgray eyes\b', r'\bblack eyes\b',
            r'\bdark brown eyes\b', r'\blight brown eyes\b',
            r'\bmedium brown eyes\b', r'\bdeep blue eyes\b',
            r'\bdual colored eyes\b', r'\bgrey eyes\b'
        ]

        for txt_file in sorted(V4_DIR.glob("*.txt")):
            with open(txt_file, 'r') as f:
                caption = f.read().strip()

            # Check if eye color is missing or just has "eyes" with no color
            has_eye_color = any(re.search(pattern, caption, re.IGNORECASE) for pattern in eye_patterns)

            # Also catch cases like "eyes," where there's the word "eyes" but no color
            has_bare_eyes = re.search(r'\beyes\b(?!\s*\()', caption, re.IGNORECASE)

            if not has_eye_color or (has_bare_eyes and not has_eye_color):
                image_file = txt_file.name.replace('.txt', '.png')
                self.records.append({
                    'filename': txt_file.name,
                    'image_file': image_file,
                    'caption': caption,
                    'fixed': False
                })

        print(f"✅ Found {len(self.records)} captions missing eye colors")

    def get_current_data(self):
        """Get current record"""
        if not self.records:
            return None, "", "", "", 0, len(self.records)

        record = self.records[self.current_index]

        # Load image
        image_path = IMAGES_DIR / record['image_file']
        if image_path.exists():
            image = Image.open(image_path)
            image = image.resize((480, 480), Image.NEAREST)
        else:
            image = None

        progress = f"Image {self.current_index + 1} of {len(self.records)}"

        # Get any existing fix
        eye_color_input = self.fixes.get(record['filename'], '')

        return (
            image,
            record['caption'],
            eye_color_input,
            record['filename'],
            self.current_index + 1,
            len(self.records)
        )

    def add_eye_color(self, eye_color, caption):
        """Insert eye color into caption in the right place"""
        if not eye_color.strip():
            return caption

        eye_color = eye_color.strip()

        # Ensure it ends with "eyes"
        if not eye_color.endswith('eyes'):
            eye_color = f"{eye_color} eyes"

        # Find where to insert - after expression or after accessories/hair
        # Pattern: look for "neutral expression" or "slight smile" and insert after
        if 'neutral expression' in caption:
            caption = caption.replace('neutral expression', f'neutral expression, {eye_color}')
        elif 'slight smile' in caption:
            caption = caption.replace('slight smile', f'slight smile, {eye_color}')
        elif ', eyes,' in caption:
            # Replace bare "eyes" with colored eyes
            caption = caption.replace(', eyes,', f', {eye_color},')
        else:
            # Insert before skin tone
            caption = re.sub(r'(,\s*(?:light|medium|dark|tan)\s+(?:light\s+)?(?:skin|green skin))',
                           f', {eye_color}\\1', caption)

        return caption

    def save_fix(self, eye_color, filename):
        """Save the eye color fix"""
        if filename and eye_color.strip():
            self.fixes[filename] = eye_color.strip()
            print(f"💾 Saved eye color for {filename}: {eye_color}")

    def next_image(self, eye_color, filename):
        """Save and move to next"""
        self.save_fix(eye_color, filename)
        if self.current_index < len(self.records) - 1:
            self.current_index += 1
        return self.get_current_data()

    def previous_image(self, eye_color, filename):
        """Save and move to previous"""
        self.save_fix(eye_color, filename)
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_data()

    def export_fixes(self):
        """Export all fixes and generate V5 captions"""
        fixed_count = 0
        unchanged_count = 0

        # First, copy all V4 captions to V5
        for txt_file in V4_DIR.glob("*.txt"):
            with open(txt_file, 'r') as f:
                caption = f.read().strip()

            # Check if this file has a fix
            if txt_file.name in self.fixes:
                eye_color = self.fixes[txt_file.name]
                caption = self.add_eye_color(eye_color, caption)
                fixed_count += 1

            # Save to V5
            output_file = OUTPUT_DIR / txt_file.name
            with open(output_file, 'w') as f:
                f.write(caption)

        # Save fixes log
        fixes_file = OUTPUT_DIR / "eye_color_fixes.json"
        with open(fixes_file, 'w') as f:
            json.dump(self.fixes, f, indent=2)

        unchanged_count = len([r for r in self.records if r['filename'] not in self.fixes])

        message = f"""✅ Export Complete!

Fixed: {fixed_count} captions
Still missing: {unchanged_count} captions
Total V5 captions: {len(list(V4_DIR.glob('*.txt')))}

Output: {OUTPUT_DIR}/
Fixes log: {fixes_file}
"""
        print(message)
        return message

# Create fixer
print("🚀 Initializing Eye Color Fixer...")
fixer = EyeColorFixer()

# Create UI
with gr.Blocks(title="Fix Missing Eye Colors", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 👁️ Fix Missing Eye Colors")
    gr.Markdown(f"""
    ## {len(fixer.records)} captions are missing eye colors

    **Instructions:**
    1. Look at the image
    2. Determine the eye color
    3. Type it in the box (e.g., "brown", "deep blue", "dark brown", "dual colored (left purple, right brown)")
    4. Click "Save & Next" to move on

    Common eye colors: brown, dark brown, light brown, blue, deep blue, green, hazel, gray, black
    """)

    with gr.Row():
        with gr.Column(scale=1):
            image_display = gr.Image(label="Image (24x24 scaled up)", type="pil")
            progress_display = gr.Textbox(label="Progress", interactive=False)

        with gr.Column(scale=2):
            current_caption = gr.Textbox(
                label="📄 Current Caption (missing eye color)",
                lines=4,
                interactive=False
            )

            eye_color_input = gr.Textbox(
                label="👁️ Eye Color",
                lines=1,
                placeholder="Type eye color here (e.g., 'brown', 'deep blue', 'dark brown')...",
                info="Just the color - 'eyes' will be added automatically"
            )

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous", variant="secondary")
                save_next_btn = gr.Button("💾 Save & Next", variant="primary", size="lg")
                next_btn = gr.Button("⏭️ Skip", variant="secondary")

            export_btn = gr.Button("📤 Export All Fixes & Generate V5", variant="stop", size="lg")
            export_status = gr.Textbox(label="Export Status", lines=8, interactive=False)

    # Hidden state
    current_filename = gr.Textbox(visible=False)

    # Actions
    def load_initial():
        return fixer.get_current_data()

    def on_next(eye_color, filename):
        return fixer.next_image(eye_color, filename)

    def on_previous(eye_color, filename):
        return fixer.previous_image(eye_color, filename)

    def on_export():
        return fixer.export_fixes()

    # Wire up
    outputs = [image_display, current_caption, eye_color_input, current_filename,
               progress_display, gr.Number(visible=False)]

    save_next_btn.click(on_next, inputs=[eye_color_input, current_filename], outputs=outputs)
    next_btn.click(on_next, inputs=[eye_color_input, current_filename], outputs=outputs)
    prev_btn.click(on_previous, inputs=[eye_color_input, current_filename], outputs=outputs)
    export_btn.click(on_export, outputs=[export_status])

    demo.load(load_initial, outputs=outputs)

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 LAUNCHING EYE COLOR FIXER")
    print("=" * 70)
    print(f"📊 Captions needing eye colors: {len(fixer.records)}")
    print()
    print("📌 URL: http://127.0.0.1:7865")
    print("=" * 70)

    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7865,
        show_error=True
    )
