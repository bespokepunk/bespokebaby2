#!/usr/bin/env python3
"""
Interactive Caption Review Interface
- View images with their final captions
- Edit captions directly
- Track approval/modification status
- Save feedback for regeneration
"""

import gradio as gr
import json
import os
from pathlib import Path
from PIL import Image

# Paths
TRAINING_DIR = "civitai_v2_7_training"
REVIEW_DATA = "caption_review_status.json"

class CaptionReviewer:
    def __init__(self):
        self.load_captions()
        self.load_review_status()
        self.current_index = 0

    def load_captions(self):
        """Load all images and their final captions"""
        self.items = []

        # Get all .txt files
        txt_files = sorted(Path(TRAINING_DIR).glob("*.txt"))

        for txt_file in txt_files:
            img_file = txt_file.with_suffix('.png')

            if img_file.exists():
                with open(txt_file, 'r') as f:
                    caption = f.read().strip()

                self.items.append({
                    'filename': img_file.name,
                    'image_path': str(img_file),
                    'txt_path': str(txt_file),
                    'caption': caption
                })

        print(f"✓ Loaded {len(self.items)} images with captions")

    def load_review_status(self):
        """Load review status from JSON file"""
        if os.path.exists(REVIEW_DATA):
            with open(REVIEW_DATA, 'r') as f:
                self.status = json.load(f)
        else:
            # Initialize with all items needing review
            self.status = {
                item['filename']: {
                    'status': 'pending',  # pending, approved, modified
                    'original_caption': item['caption'],
                    'modified_caption': None,
                    'feedback': ''
                }
                for item in self.items
            }
            self.save_review_status()

    def save_review_status(self):
        """Save review status to JSON file"""
        with open(REVIEW_DATA, 'w') as f:
            json.dump(self.status, f, indent=2)
        print(f"✓ Review status saved to {REVIEW_DATA}")

    def get_current_item(self):
        """Get current item for review"""
        if not self.items:
            return None, None, None, "No items to review"

        item = self.items[self.current_index]
        filename = item['filename']
        status_info = self.status[filename]

        # Load image
        image = Image.open(item['image_path'])

        # Get caption to display (modified if exists, else original)
        current_caption = status_info.get('modified_caption') or item['caption']

        # Stats
        total = len(self.items)
        approved = sum(1 for s in self.status.values() if s['status'] == 'approved')
        modified = sum(1 for s in self.status.values() if s['status'] == 'modified')
        pending = total - approved - modified

        info_text = f"""
**Image {self.current_index + 1} of {total}**
**Filename:** {filename}
**Status:** {status_info['status'].upper()}

**Progress:**
- ✅ Approved: {approved}
- ✏️ Modified: {modified}
- ⏳ Pending: {pending}

---
**Original Caption:**
{status_info['original_caption']}
        """

        return image, current_caption, status_info.get('feedback', ''), info_text

    def approve_caption(self):
        """Mark current caption as approved"""
        if not self.items:
            return self.get_current_item()

        filename = self.items[self.current_index]['filename']
        self.status[filename]['status'] = 'approved'
        self.save_review_status()

        # Move to next
        if self.current_index < len(self.items) - 1:
            self.current_index += 1

        return self.get_current_item()

    def save_modified_caption(self, modified_caption, feedback):
        """Save modified caption and feedback"""
        if not self.items:
            return self.get_current_item()

        item = self.items[self.current_index]
        filename = item['filename']

        # Update status
        self.status[filename]['status'] = 'modified'
        self.status[filename]['modified_caption'] = modified_caption
        self.status[filename]['feedback'] = feedback

        # Save modified caption to .txt file
        with open(item['txt_path'], 'w') as f:
            f.write(modified_caption)

        self.save_review_status()
        print(f"✓ Modified caption saved for {filename}")

        # Move to next
        if self.current_index < len(self.items) - 1:
            self.current_index += 1

        return self.get_current_item()

    def go_to_previous(self):
        """Go to previous item"""
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_item()

    def go_to_next(self):
        """Go to next item"""
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
        return self.get_current_item()

    def jump_to_pending(self):
        """Jump to next pending item"""
        for i in range(len(self.items)):
            filename = self.items[i]['filename']
            if self.status[filename]['status'] == 'pending':
                self.current_index = i
                break
        return self.get_current_item()

    def export_feedback(self):
        """Export all feedback for regeneration"""
        feedback_items = []

        for filename, status in self.status.items():
            if status['status'] == 'modified' and status.get('feedback'):
                feedback_items.append({
                    'filename': filename,
                    'original': status['original_caption'],
                    'modified': status['modified_caption'],
                    'feedback': status['feedback']
                })

        with open('caption_feedback_for_regeneration.json', 'w') as f:
            json.dump(feedback_items, f, indent=2)

        return f"✅ Exported {len(feedback_items)} feedback items to caption_feedback_for_regeneration.json"


# Create reviewer instance
reviewer = CaptionReviewer()


# Build Gradio Interface
with gr.Blocks(title="Caption Review Interface", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📝 Final Caption Review & Editor")
    gr.Markdown("Review your final captions, make edits, and track your progress.")

    with gr.Row():
        with gr.Column(scale=1):
            # Image display
            image_display = gr.Image(label="Current Image", type="pil")

            # Info panel
            info_panel = gr.Markdown()

        with gr.Column(scale=1):
            # Caption editor
            caption_editor = gr.Textbox(
                label="Caption",
                lines=8,
                placeholder="Edit caption here..."
            )

            # Feedback box
            feedback_box = gr.Textbox(
                label="Feedback / Notes (optional)",
                lines=3,
                placeholder="Add notes about why you changed this caption..."
            )

            # Action buttons
            with gr.Row():
                approve_btn = gr.Button("✅ Approve", variant="primary")
                save_modified_btn = gr.Button("💾 Save Modified", variant="secondary")

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous")
                next_btn = gr.Button("➡️ Next")
                jump_pending_btn = gr.Button("⏭️ Jump to Pending")

            # Export button
            export_btn = gr.Button("📤 Export Feedback for Regeneration", variant="stop")
            export_status = gr.Textbox(label="Export Status", interactive=False)

    # Event handlers
    def on_approve():
        return reviewer.approve_caption()

    def on_save_modified(caption, feedback):
        return reviewer.save_modified_caption(caption, feedback)

    def on_previous():
        return reviewer.go_to_previous()

    def on_next():
        return reviewer.go_to_next()

    def on_jump_pending():
        return reviewer.jump_to_pending()

    def on_export():
        return reviewer.export_feedback()

    # Wire up buttons
    approve_btn.click(
        fn=on_approve,
        outputs=[image_display, caption_editor, feedback_box, info_panel]
    )

    save_modified_btn.click(
        fn=on_save_modified,
        inputs=[caption_editor, feedback_box],
        outputs=[image_display, caption_editor, feedback_box, info_panel]
    )

    prev_btn.click(
        fn=on_previous,
        outputs=[image_display, caption_editor, feedback_box, info_panel]
    )

    next_btn.click(
        fn=on_next,
        outputs=[image_display, caption_editor, feedback_box, info_panel]
    )

    jump_pending_btn.click(
        fn=on_jump_pending,
        outputs=[image_display, caption_editor, feedback_box, info_panel]
    )

    export_btn.click(
        fn=on_export,
        outputs=[export_status]
    )

    # Load first item on startup
    demo.load(
        fn=reviewer.get_current_item,
        outputs=[image_display, caption_editor, feedback_box, info_panel]
    )


if __name__ == "__main__":
    print("=" * 80)
    print("CAPTION REVIEW INTERFACE")
    print("=" * 80)
    print()
    print("Starting Gradio interface...")
    print("Open the URL in your browser to start reviewing captions.")
    print()

    demo.launch(share=False, inbrowser=True)
