#!/usr/bin/env python3
"""
FINAL CAPTION REVIEW UI - Review all 203 world-class captions
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
CAPTIONS_DIR = "FINAL_WORLD_CLASS_CAPTIONS"
IMAGES_DIR = "runpod_package/training_data"
REVIEW_DATA = "final_caption_review_status.json"

class CaptionReviewer:
    def __init__(self):
        self.load_captions()
        self.load_review_status()
        self.current_index = 0

    def load_captions(self):
        """Load all images and their final captions"""
        self.items = []

        # Get all .txt files from FINAL_WORLD_CLASS_CAPTIONS
        txt_files = sorted(Path(CAPTIONS_DIR).glob("*.txt"))

        for txt_file in txt_files:
            # Image is in IMAGES_DIR with same name
            img_file = Path(IMAGES_DIR) / txt_file.with_suffix('.png').name

            if img_file.exists():
                with open(txt_file, 'r') as f:
                    caption = f.read().strip()

                self.items.append({
                    'filename': txt_file.name,
                    'image_path': str(img_file),
                    'txt_path': str(txt_file),
                    'caption': caption,
                    'char_count': len(caption)
                })

        print(f"✓ Loaded {len(self.items)} captions with images")

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
        current_char_count = len(current_caption)

        # Stats
        total = len(self.items)
        approved = sum(1 for s in self.status.values() if s['status'] == 'approved')
        modified = sum(1 for s in self.status.values() if s['status'] == 'modified')
        pending = total - approved - modified

        # Character count status
        char_status = "✅ Good" if 150 <= current_char_count <= 350 else "⚠️ Check length"

        info_text = f"""
**Caption {self.current_index + 1} of {total}**
**Filename:** {filename}
**Characters:** {current_char_count} {char_status}
**Status:** {status_info['status'].upper()}

**Progress:**
- ✅ Approved: {approved}
- ✏️ Modified: {modified}
- ⏳ Pending: {pending}

---
**Original Caption ({item['char_count']} chars):**
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
with gr.Blocks(title="Final Caption Review - All 203", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 FINAL CAPTION REVIEW - All 203 World-Class Captions")
    gr.Markdown("Review, edit, and approve your cleaned captions. All changes save automatically.")

    with gr.Row():
        with gr.Column(scale=1):
            # Image display
            image_display = gr.Image(label="Current Image", type="pil", height=400)

            # Info panel
            info_panel = gr.Markdown()

        with gr.Column(scale=1):
            # Caption editor
            caption_editor = gr.Textbox(
                label="Caption (Editable)",
                lines=8,
                placeholder="Edit caption here..."
            )

            # Feedback box
            feedback_box = gr.Textbox(
                label="Feedback / Notes (optional)",
                lines=3,
                placeholder="Add notes about this caption..."
            )

            gr.Markdown("### 🎯 Review Actions")
            # Action buttons
            with gr.Row():
                approve_btn = gr.Button("✅ Approve & Next", variant="primary", size="lg")
                save_modified_btn = gr.Button("✏️ Save Edit & Next", variant="secondary", size="lg")

            gr.Markdown("### 🧭 Navigation")
            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous")
                next_btn = gr.Button("➡️ Next")
                jump_pending_btn = gr.Button("⏭️ Jump to Pending")

            gr.Markdown("### 💾 Export")
            # Export button
            export_btn = gr.Button("📤 Export All Feedback", variant="stop")
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
    print("🎨 FINAL CAPTION REVIEW UI - All 203 Captions")
    print("=" * 80)
    print()
    print(f"✓ Loaded {len(reviewer.items)} captions from {CAPTIONS_DIR}")
    print()
    print("📊 Quick Stats:")
    total = len(reviewer.items)
    approved = sum(1 for s in reviewer.status.values() if s['status'] == 'approved')
    modified = sum(1 for s in reviewer.status.values() if s['status'] == 'modified')
    pending = total - approved - modified
    print(f"   ✅ Approved: {approved}")
    print(f"   ✏️  Modified: {modified}")
    print(f"   ⏳ Pending: {pending}")
    print()
    print("🚀 Starting Gradio interface...")
    print("   Username: admin")
    print("   Password: test123")
    print()

    # Get credentials from environment or use defaults
    username = os.getenv('GRADIO_USERNAME', 'admin')
    password = os.getenv('GRADIO_PASSWORD', 'test123')

    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        auth=(username, password),
        show_error=True,
        inbrowser=True
    )
