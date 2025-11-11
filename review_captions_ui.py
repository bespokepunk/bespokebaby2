#!/usr/bin/env python3
"""
Caption Review UI - Review and fix all training captions
Connected to Supabase as source of truth
"""

import gradio as gr
import os
from pathlib import Path
from PIL import Image
import psycopg2
from psycopg2.extras import RealDictCursor

TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data_IMPROVED"
SUPABASE_URL = "postgresql://postgres.qwvncbcphuyobijakdsr:Ilyssa2025@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

class CaptionReviewer:
    def __init__(self, training_dir, db_url):
        self.training_dir = Path(training_dir)
        self.db_url = db_url
        self.current_index = 0

        # Connect to Supabase and load records
        self.load_from_database()
        print(f"📝 Found {len(self.records)} records from Supabase")

    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)

    def load_from_database(self):
        """Load all caption records from Supabase"""
        conn = self.get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, filename, current_caption, user_corrections,
                           final_caption_txt, status
                    FROM caption_reviews
                    ORDER BY filename
                """)
                self.records = cur.fetchall()
        finally:
            conn.close()

    def get_image_path(self, filename):
        """Get the local image path for a filename"""
        return self.training_dir / filename

    def save_feedback(self, record_id, feedback):
        """Save feedback to Supabase"""
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE caption_reviews
                    SET user_corrections = %s,
                        status = 'edited',
                        updated_at = NOW()
                    WHERE id = %s
                """, (feedback, record_id))
                conn.commit()
                print(f"💾 Saved to Supabase: record {record_id}")
        finally:
            conn.close()

    def get_current_data(self):
        """Get current image, caption, and feedback from Supabase"""
        if not self.records:
            return None, "", "", "No records found", 0, len(self.records), None

        record = self.records[self.current_index]
        filename = record['filename']
        caption = record['current_caption'] or ""
        feedback = record['user_corrections'] or ""
        record_id = record['id']
        status = record['status'] or "pending"

        # Load image from local disk
        image_path = self.get_image_path(filename)
        if image_path.exists():
            image = Image.open(image_path)
            # Scale up image for better viewing (24x24 is tiny)
            image = image.resize((480, 480), Image.NEAREST)
        else:
            image = None
            print(f"⚠️ Image not found: {filename}")

        progress = f"Image {self.current_index + 1} of {len(self.records)} | Status: {status}"

        return image, caption, feedback, filename, self.current_index + 1, len(self.records), record_id

    def next_image(self, current_feedback, current_record_id):
        """Save current feedback to Supabase and move to next image"""
        # Save current feedback to Supabase
        if self.records and current_record_id:
            self.save_feedback(current_record_id, current_feedback)

        # Move to next
        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def previous_image(self, current_feedback, current_record_id):
        """Save current feedback to Supabase and move to previous image"""
        # Save current feedback to Supabase
        if self.records and current_record_id:
            self.save_feedback(current_record_id, current_feedback)

        # Move to previous
        if self.current_index > 0:
            self.current_index -= 1

        return self.get_current_data()

    def jump_to_image(self, index, current_feedback, current_record_id):
        """Save current feedback to Supabase and jump to specific index"""
        # Save current feedback to Supabase
        if self.records and current_record_id:
            self.save_feedback(current_record_id, current_feedback)

        # Jump to index
        if 0 < index <= len(self.records):
            self.current_index = index - 1

        return self.get_current_data()

    def save_current(self, current_feedback, current_record_id):
        """Save current feedback to Supabase without moving"""
        if self.records and current_record_id:
            self.save_feedback(current_record_id, current_feedback)
        return self.get_current_data()

# Create reviewer
reviewer = CaptionReviewer(TRAINING_DIR, SUPABASE_URL)

# Create Gradio interface
with gr.Blocks(title="Caption Review Tool") as demo:
    gr.Markdown("# 📝 Caption Review & Cleanup Tool")
    gr.Markdown("""
    ## What to Look For & Fix:

    ### ❌ REMOVE These Unnecessary Tokens:
    - ❌ Remove "lips" - model adds lips automatically
    - ❌ Remove "hard color borders, sharp pixel edges" - redundant style markers
    - ❌ Simplify "mouth in straight neutral line with relaxed expression" → just "neutral expression"
    - ❌ Remove "male/female" from skin tone descriptions (e.g., "medium male skin tone" → "medium skin")

    ### ✅ KEEP & FIX These Important Features:
    - ✅ Hair color/style (but verify it matches the image!)
    - ✅ Eye color (brown, blue, green, black, gray)
    - ✅ Skin tone (light, medium, tan, dark)
    - ✅ Accessories (glasses, earrings, hats, etc.)
    - ✅ Expression: ONLY use "neutral expression" or "slight smile" (verify which one matches!)
    - ✅ Background description (if visible, but verify accuracy!)

    ### 🔧 Common Fixes Needed:
    1. **Expression**: Many say "neutral expression" but the image has a smile - FIX THIS!
    2. **Hair description**: "hair, wearing hat" is wrong - should be "brown hair, wearing hat"
    3. **Background**: Verify color matches - don't just trust the caption!
    4. **Clothing**: Check if "shirt" color is accurate

    ### ✨ Final Format Should Be:
    `pixel art, 24x24, portrait of bespoke punk [lady/lad], [hair color] hair, [accessories], [eye color] eyes, [expression], [skin tone] skin, [background], pixel art style`

    **Example Good Caption:**
    `pixel art, 24x24, portrait of bespoke punk lad, brown hair, wearing gray baseball cap, dark brown eyes, neutral expression, medium skin, blue background, pixel art style`
    """)

    with gr.Row():
        with gr.Column(scale=1):
            image_display = gr.Image(label="Current Image", type="pil")
            filename_display = gr.Textbox(label="Filename", interactive=False)
            progress_display = gr.Textbox(label="Progress", interactive=False)

        with gr.Column(scale=2):
            original_caption = gr.Textbox(
                label="Original Caption (read-only)",
                lines=4,
                interactive=False,
                show_copy_button=True
            )

            feedback_editor = gr.Textbox(
                label="Your Feedback/Changes (edit here)",
                lines=6,
                placeholder="Enter your corrections or feedback here..."
            )

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous", variant="secondary")
                save_btn = gr.Button("💾 Save Feedback", variant="primary")
                next_btn = gr.Button("➡️ Next", variant="secondary")

            with gr.Row():
                jump_input = gr.Number(label="Jump to image #", precision=0, minimum=1)
                jump_btn = gr.Button("🎯 Jump", variant="secondary")

    # Hidden state to track total images and current record ID
    total_images = gr.Number(visible=False)
    current_record_id = gr.Number(visible=False, label="Current Record ID")

    # Load initial image
    def load_initial():
        image, caption, feedback, filename, current, total, record_id = reviewer.get_current_data()
        return image, caption, feedback, filename, f"{current}/{total}", total, record_id

    # Button actions
    def on_next(feedback, record_id):
        image, caption, new_feedback, filename, current, total, new_record_id = reviewer.next_image(feedback, record_id)
        return image, caption, new_feedback, filename, f"{current}/{total}", new_record_id

    def on_previous(feedback, record_id):
        image, caption, new_feedback, filename, current, total, new_record_id = reviewer.previous_image(feedback, record_id)
        return image, caption, new_feedback, filename, f"{current}/{total}", new_record_id

    def on_save(feedback, record_id):
        image, caption, new_feedback, filename, current, total, new_record_id = reviewer.save_current(feedback, record_id)
        return image, caption, new_feedback, filename, f"{current}/{total}", new_record_id

    def on_jump(index, feedback, record_id):
        image, caption, new_feedback, filename, current, total, new_record_id = reviewer.jump_to_image(index, feedback, record_id)
        return image, caption, new_feedback, filename, f"{current}/{total}", new_record_id

    # Wire up buttons
    next_btn.click(
        on_next,
        inputs=[feedback_editor, current_record_id],
        outputs=[image_display, original_caption, feedback_editor, filename_display, progress_display, current_record_id]
    )

    prev_btn.click(
        on_previous,
        inputs=[feedback_editor, current_record_id],
        outputs=[image_display, original_caption, feedback_editor, filename_display, progress_display, current_record_id]
    )

    save_btn.click(
        on_save,
        inputs=[feedback_editor, current_record_id],
        outputs=[image_display, original_caption, feedback_editor, filename_display, progress_display, current_record_id]
    )

    jump_btn.click(
        on_jump,
        inputs=[jump_input, feedback_editor, current_record_id],
        outputs=[image_display, original_caption, feedback_editor, filename_display, progress_display, current_record_id]
    )

    # Load initial image on startup
    demo.load(
        load_initial,
        outputs=[image_display, original_caption, feedback_editor, filename_display, progress_display, total_images, current_record_id]
    )

if __name__ == "__main__":
    print("🚀 Starting Caption Review UI...")
    print(f"📁 Training directory: {TRAINING_DIR}")
    demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
