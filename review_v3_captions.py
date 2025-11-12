#!/usr/bin/env python3
"""
📝 V3 Caption Review Tool

Review the V3-improved captions before finalizing them for training.
Side-by-side comparison: original vs V3 improved
"""

import gradio as gr
import os
from pathlib import Path
from PIL import Image
import json

# Directories
TRAINING_DIR = Path("/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data")
V3_DIR = Path("improved_samples_v3")
IMAGES_DIR = TRAINING_DIR  # Images are in training_data

class V3CaptionReviewer:
    def __init__(self):
        self.current_index = 0
        self.load_captions()
        self.feedback = {}  # Store feedback in memory for now

    def load_captions(self):
        """Load original and V3 captions"""
        self.records = []

        # Get all txt files from V3 directory
        v3_files = sorted(V3_DIR.glob("*.txt"))

        for v3_file in v3_files:
            filename = v3_file.name
            image_filename = filename.replace('.txt', '.png')

            # Read V3 caption
            with open(v3_file, 'r') as f:
                v3_caption = f.read().strip()

            # Read original caption
            original_file = TRAINING_DIR / filename
            if original_file.exists():
                with open(original_file, 'r') as f:
                    original_caption = f.read().strip()
            else:
                original_caption = "Original not found"

            # Check if image exists
            image_path = IMAGES_DIR / image_filename
            if not image_path.exists():
                continue

            self.records.append({
                'filename': image_filename,
                'original': original_caption,
                'v3': v3_caption,
                'original_length': len(original_caption),
                'v3_length': len(v3_caption),
                'reduction': len(original_caption) - len(v3_caption),
                'reduction_pct': round((len(original_caption) - len(v3_caption)) / len(original_caption) * 100, 1) if len(original_caption) > 0 else 0
            })

        print(f"✅ Loaded {len(self.records)} V3 captions for review")

    def get_current_data(self):
        """Get current record"""
        if not self.records:
            return None, "", "", "", "", 0, len(self.records), ""

        record = self.records[self.current_index]

        # Load image
        image_path = IMAGES_DIR / record['filename']
        if image_path.exists():
            image = Image.open(image_path)
            image = image.resize((480, 480), Image.NEAREST)
        else:
            image = None

        # Get feedback for this file
        feedback = self.feedback.get(record['filename'], '')

        # Stats
        stats = f"""
📊 **Stats:**
- Original: {record['original_length']} chars
- V3: {record['v3_length']} chars
- Reduction: {record['reduction']} chars ({record['reduction_pct']}%)
- Target: 150-220 chars ({'✅' if 150 <= record['v3_length'] <= 220 else '❌'})
"""

        progress = f"Image {self.current_index + 1} of {len(self.records)}"

        return (
            image,
            record['original'],
            record['v3'],
            record['filename'],
            feedback,
            self.current_index + 1,
            len(self.records),
            stats
        )

    def save_feedback(self, filename, feedback):
        """Save feedback to memory"""
        self.feedback[filename] = feedback
        print(f"💾 Saved feedback for: {filename}")

    def next_image(self, current_feedback, current_filename):
        """Save and move to next"""
        if current_filename:
            self.save_feedback(current_filename, current_feedback)

        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def previous_image(self, current_feedback, current_filename):
        """Save and move to previous"""
        if current_filename:
            self.save_feedback(current_filename, current_feedback)

        if self.current_index > 0:
            self.current_index -= 1

        return self.get_current_data()

    def jump_to_image(self, index, current_feedback, current_filename):
        """Jump to specific index"""
        if current_filename:
            self.save_feedback(current_filename, current_feedback)

        if 0 < index <= len(self.records):
            self.current_index = index - 1

        return self.get_current_data()

    def approve_current(self, current_feedback, current_filename):
        """Quick approve and move to next"""
        if current_filename:
            # Use custom feedback if provided, otherwise use default approve message
            feedback_to_save = current_feedback.strip() if current_feedback.strip() else "✅ APPROVED - V3 caption is good"
            self.save_feedback(current_filename, feedback_to_save)

        # Auto-advance to next image
        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def reject_current(self, current_feedback, current_filename):
        """Quick reject and move to next"""
        if current_filename:
            # Append reject marker to custom feedback if provided
            if current_feedback.strip():
                feedback_to_save = f"❌ NEEDS WORK - {current_feedback.strip()}"
            else:
                feedback_to_save = "❌ NEEDS WORK - See notes below"
            self.save_feedback(current_filename, feedback_to_save)

        # Auto-advance to next image
        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def save_and_next(self, current_feedback, current_filename):
        """Save custom feedback and move to next"""
        if current_filename and current_feedback.strip():
            self.save_feedback(current_filename, current_feedback.strip())

        # Auto-advance to next image
        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def export_feedback(self):
        """Export feedback to JSON"""
        output_file = V3_DIR / "review_feedback.json"
        with open(output_file, 'w') as f:
            json.dump(self.feedback, f, indent=2)
        print(f"📤 Exported feedback to: {output_file}")
        return f"✅ Exported {len(self.feedback)} reviews to {output_file}"

# Create reviewer
print("🚀 Initializing V3 Caption Reviewer...")
reviewer = V3CaptionReviewer()

# Create Gradio interface
with gr.Blocks(title="V3 Caption Review", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📝 V3 Caption Review Tool")
    gr.Markdown("""
    ## Review V3-improved captions before finalizing for training

    **What to check:**
    - ✅ All features are accurate (hair, eyes, skin, clothing, background)
    - ✅ No broken text or nonsense phrases
    - ✅ Expression matches image (neutral vs slight smile)
    - ✅ Caption length is reasonable (150-220 chars ideal)
    - ✅ No unnecessary tokens ("lips", "male/female", redundant style markers)

    **Actions:**
    - **Approve** if V3 caption is good
    - **Reject** if it needs work, then add notes in feedback box
    - **Navigate** through all 203 captions
    - **Export** your feedback when done
    """)

    with gr.Row():
        with gr.Column(scale=1):
            image_display = gr.Image(label="Image (24x24 scaled up)", type="pil")
            filename_display = gr.Textbox(label="Filename", interactive=False)
            progress_display = gr.Textbox(label="Progress", interactive=False)
            stats_display = gr.Markdown()

        with gr.Column(scale=2):
            original_caption = gr.Textbox(
                label="📄 Original Caption",
                lines=4,
                interactive=False,
                show_copy_button=True
            )

            v3_caption = gr.Textbox(
                label="✨ V3 Improved Caption",
                lines=4,
                interactive=False,
                show_copy_button=True
            )

            feedback_box = gr.Textbox(
                label="✏️ Your Feedback/Notes",
                lines=3,
                placeholder="Add notes, corrections, or leave blank if approved..."
            )

            with gr.Row():
                approve_btn = gr.Button("✅ Approve & Next", variant="primary", size="lg")
                reject_btn = gr.Button("❌ Needs Work & Next", variant="stop", size="lg")

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous", variant="secondary")
                save_next_btn = gr.Button("💾 Save & Next", variant="primary")
                next_btn = gr.Button("➡️ Next", variant="secondary")

            with gr.Row():
                jump_input = gr.Number(label="Jump to #", precision=0, minimum=1)
                jump_btn = gr.Button("🎯 Jump")

            export_btn = gr.Button("📤 Export All Feedback", variant="secondary", size="lg")
            export_status = gr.Textbox(label="Export Status", interactive=False)

    # Hidden state
    current_filename = gr.Textbox(visible=False)

    # Load initial
    def load_initial():
        return reviewer.get_current_data()

    # Actions
    def on_next(feedback, filename):
        return reviewer.next_image(feedback, filename)

    def on_previous(feedback, filename):
        return reviewer.previous_image(feedback, filename)

    def on_jump(index, feedback, filename):
        return reviewer.jump_to_image(index, feedback, filename)

    def on_approve(feedback, filename):
        return reviewer.approve_current(feedback, filename)

    def on_reject(feedback, filename):
        return reviewer.reject_current(feedback, filename)

    def on_save_and_next(feedback, filename):
        return reviewer.save_and_next(feedback, filename)

    def on_export():
        return reviewer.export_feedback()

    # Wire up
    outputs = [image_display, original_caption, v3_caption, filename_display,
               feedback_box, jump_input, progress_display, stats_display]

    next_btn.click(on_next, inputs=[feedback_box, filename_display], outputs=outputs)
    prev_btn.click(on_previous, inputs=[feedback_box, filename_display], outputs=outputs)
    jump_btn.click(on_jump, inputs=[jump_input, feedback_box, filename_display], outputs=outputs)
    approve_btn.click(on_approve, inputs=[feedback_box, filename_display], outputs=outputs)
    reject_btn.click(on_reject, inputs=[feedback_box, filename_display], outputs=outputs)
    save_next_btn.click(on_save_and_next, inputs=[feedback_box, filename_display], outputs=outputs)
    export_btn.click(on_export, outputs=[export_status])

    demo.load(load_initial, outputs=outputs)

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 LAUNCHING V3 CAPTION REVIEW TOOL")
    print("=" * 70)
    print(f"📁 V3 captions directory: {V3_DIR}")
    print(f"📊 Total captions to review: {len(reviewer.records)}")
    print()
    print("📌 URL: http://127.0.0.1:7864")
    print("=" * 70)

    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7864,
        show_error=True
    )
