#!/usr/bin/env python3
"""
📝 Caption Review & Cleanup Tool - Fresh Start Edition

Shows ONLY the final captions used in the last training run.
Historical feedback is preserved in the database but not shown.
Fresh slate for new review cycle.
"""

import gradio as gr
import os
from pathlib import Path
from PIL import Image
import psycopg2
from psycopg2.extras import RealDictCursor

# TRAINING DATA - The actual files used in last training
TRAINING_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data"

# SUPABASE CONNECTION
SUPABASE_URL = "postgresql://postgres.qwvncbcphuyobijakdsr:Ilyssa2025@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

class CaptionReviewer:
    def __init__(self, training_dir, db_url):
        self.training_dir = Path(training_dir)
        self.db_url = db_url
        self.current_index = 0

        # Ensure fresh_review table exists
        self.setup_database()

        # Load all caption files from disk (source of truth)
        self.load_from_training_data()
        print(f"📝 Loaded {len(self.records)} caption files from training data")

    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            return None

    def setup_database(self):
        """Create fresh_review table if it doesn't exist"""
        conn = self.get_db_connection()
        if not conn:
            print("⚠️ Skipping database setup - no connection")
            return

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS caption_fresh_review (
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL UNIQUE,
                        original_caption TEXT,
                        final_used_caption TEXT,
                        new_feedback TEXT,
                        review_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                conn.commit()
                print("✅ Database table ready: caption_fresh_review")
        except Exception as e:
            print(f"⚠️ Database setup failed: {e}")
        finally:
            conn.close()

    def load_from_training_data(self):
        """Load all caption files from the actual training directory - FRESH SLATE"""
        self.records = []

        # Get all .txt files from training directory
        txt_files = sorted(self.training_dir.glob("*.txt"))

        # Load any existing feedback from NEW table (not old table)
        existing_feedback = {}
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT filename, new_feedback FROM caption_fresh_review")
                    for row in cur.fetchall():
                        existing_feedback[row['filename']] = row.get('new_feedback', '')
            except Exception as e:
                print(f"⚠️ Could not load existing feedback: {e}")
            finally:
                conn.close()

        # Load training captions from disk
        for txt_file in txt_files:
            # Read the actual caption used in training
            try:
                with open(txt_file, 'r') as f:
                    caption = f.read().strip()

                # Check if corresponding image exists
                image_file = txt_file.with_suffix('.png')
                if not image_file.exists():
                    continue

                filename = txt_file.name.replace('.txt', '.png')

                self.records.append({
                    'filename': filename,
                    'final_used_caption': caption,
                    'new_feedback': existing_feedback.get(filename, ''),  # Only load NEW feedback, not old
                    'review_status': 'pending'
                })
            except Exception as e:
                print(f"⚠️ Error loading {txt_file.name}: {e}")

        print(f"✅ Loaded {len(self.records)} captions from training data")
        print(f"📝 Found {len(existing_feedback)} existing NEW reviews (old feedback NOT loaded)")

    def save_feedback(self, filename, feedback, status='reviewed'):
        """Save NEW feedback to database (separate from historical feedback)"""
        conn = self.get_db_connection()
        if not conn:
            print("⚠️ Cannot save feedback - no database connection")
            return

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO caption_fresh_review
                        (filename, final_used_caption, new_feedback, review_status, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (filename)
                    DO UPDATE SET
                        new_feedback = EXCLUDED.new_feedback,
                        review_status = EXCLUDED.review_status,
                        updated_at = NOW()
                """, (filename, self.records[self.current_index]['final_used_caption'], feedback, status))
                conn.commit()
                print(f"💾 Saved feedback for: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save feedback: {e}")
        finally:
            conn.close()

    def get_current_data(self):
        """Get current image and caption from training data"""
        if not self.records:
            return None, "", "", "No records found", 0, len(self.records)

        record = self.records[self.current_index]
        filename = record['filename']
        caption = record['final_used_caption']
        feedback = record.get('new_feedback', '')
        status = record.get('review_status', 'pending')

        # Load image from disk
        image_path = self.training_dir / filename
        if image_path.exists():
            image = Image.open(image_path)
            # Scale up for better viewing
            image = image.resize((480, 480), Image.NEAREST)
        else:
            image = None
            print(f"⚠️ Image not found: {filename}")

        progress = f"Image {self.current_index + 1} of {len(self.records)} | Status: {status}"

        return image, caption, feedback, filename, self.current_index + 1, len(self.records)

    def next_image(self, current_feedback, current_filename):
        """Save current feedback and move to next"""
        if self.records and current_filename:
            self.save_feedback(current_filename, current_feedback, 'reviewed')

        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def previous_image(self, current_feedback, current_filename):
        """Save current feedback and move to previous"""
        if self.records and current_filename:
            self.save_feedback(current_filename, current_feedback, 'reviewed')

        if self.current_index > 0:
            self.current_index -= 1

        return self.get_current_data()

    def jump_to_image(self, index, current_feedback, current_filename):
        """Save current feedback and jump to specific index"""
        if self.records and current_filename:
            self.save_feedback(current_filename, current_feedback, 'reviewed')

        if 0 < index <= len(self.records):
            self.current_index = index - 1

        return self.get_current_data()

    def save_current(self, current_feedback, current_filename):
        """Save current feedback without moving"""
        if self.records and current_filename:
            self.save_feedback(current_filename, current_feedback, 'reviewed')
        return self.get_current_data()

# Create reviewer
print("🚀 Initializing Caption Reviewer...")
reviewer = CaptionReviewer(TRAINING_DIR, SUPABASE_URL)

# Create Gradio interface
with gr.Blocks(title="Caption Review Tool - Fresh Start", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📝 Caption Review & Cleanup Tool - FRESH START")
    gr.Markdown("""
    ## 🎯 This tool shows ONLY the final captions used in your last training run

    ### What's Different:
    - ✅ **Historical feedback PRESERVED** in database `caption_reviews` table (not deleted!)
    - ✅ **100% FRESH SLATE** - feedback fields are BLANK (old corrections not shown)
    - ✅ **New database table** `caption_fresh_review` - separate from old `caption_reviews`
    - ✅ **New column** `new_feedback` - your fresh corrections go here
    - ✅ **Source of truth** - loads directly from `training_data/` files used in last training

    ---

    ## What to Look For & Fix:

    ### ❌ REMOVE These Unnecessary Tokens:
    - ❌ Remove "lips" - model adds lips automatically
    - ❌ Remove "hard color borders, sharp pixel edges" - redundant style markers
    - ❌ Simplify "mouth in straight neutral line" → just "neutral expression"
    - ❌ Remove "male/female" from skin tone (e.g., "medium male skin" → "medium skin")

    ### ✅ KEEP & FIX These Important Features:
    - ✅ Hair color/style (verify it matches the image!)
    - ✅ Eye color (brown, blue, green, black, gray, hazel)
    - ✅ Skin tone (light, medium, tan, dark)
    - ✅ Accessories (glasses, earrings, hats, chains, etc.)
    - ✅ Expression: ONLY "neutral expression" or "slight smile" (verify!)
    - ✅ Background description (verify color accuracy!)
    - ✅ Clothing description (verify color/style!)

    ### 🔧 Common Fixes Needed:
    1. **Expression mismatch** - Many say "neutral" but show a smile
    2. **Missing hair description** - "hair, wearing hat" should be "brown hair, wearing hat"
    3. **Background color** - Verify it matches the actual image
    4. **Redundant text** - Remove duplicated phrases
    5. **Incomplete descriptions** - Fix broken sentences

    ### ✨ Final Format Should Be:
    `pixel art, 24x24, portrait of bespoke punk [lady/lad], [hair color] hair, [accessories], [eye color] eyes, [expression], [skin tone] skin, [background], pixel art style`

    **Example Good Caption:**
    `pixel art, 24x24, portrait of bespoke punk lad, brown hair, wearing gray baseball cap, dark brown eyes, neutral expression, medium skin, blue background, pixel art style`
    """)

    with gr.Row():
        with gr.Column(scale=1):
            image_display = gr.Image(label="Current Image (scaled up from 24x24)", type="pil")
            filename_display = gr.Textbox(label="Filename", interactive=False)
            progress_display = gr.Textbox(label="Progress", interactive=False)

        with gr.Column(scale=2):
            final_caption = gr.Textbox(
                label="📄 Final Caption Used in Last Training (read-only)",
                lines=6,
                interactive=False,
                show_copy_button=True
            )

            feedback_editor = gr.Textbox(
                label="✏️ Your NEW Feedback/Corrections (edit here)",
                lines=6,
                placeholder="Enter your corrections, notes, or the corrected caption here...",
                info="This will be saved separately from historical feedback"
            )

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous", variant="secondary", size="lg")
                save_btn = gr.Button("💾 Save Feedback", variant="primary", size="lg")
                next_btn = gr.Button("➡️ Next", variant="secondary", size="lg")

            with gr.Row():
                jump_input = gr.Number(label="Jump to image #", precision=0, minimum=1)
                jump_btn = gr.Button("🎯 Jump", variant="secondary")

    gr.Markdown("""
    ---
    ### 💡 Tips:
    - **Save frequently** - Feedback is saved to database automatically
    - **Historical data preserved** - Your previous feedback is safe in the old table
    - **Fresh perspective** - Review these captions with fresh eyes
    - **Copy helpful** - Use copy button to grab caption and edit in feedback box
    """)

    # Hidden state for current filename
    current_filename = gr.Textbox(visible=False, label="Current Filename")

    # Load initial image
    def load_initial():
        image, caption, feedback, filename, current, total = reviewer.get_current_data()
        return image, caption, feedback, filename, f"{current}/{total}", filename

    # Button actions
    def on_next(feedback, filename):
        image, caption, new_feedback, new_filename, progress, _ = reviewer.next_image(feedback, filename)
        return image, caption, new_feedback, new_filename, progress, new_filename

    def on_previous(feedback, filename):
        image, caption, new_feedback, new_filename, progress, _ = reviewer.previous_image(feedback, filename)
        return image, caption, new_feedback, new_filename, progress, new_filename

    def on_save(feedback, filename):
        image, caption, new_feedback, new_filename, progress, _ = reviewer.save_current(feedback, filename)
        return image, caption, new_feedback, new_filename, progress, new_filename

    def on_jump(index, feedback, filename):
        image, caption, new_feedback, new_filename, progress, _ = reviewer.jump_to_image(index, feedback, filename)
        return image, caption, new_feedback, new_filename, progress, new_filename

    # Wire up buttons
    next_btn.click(
        on_next,
        inputs=[feedback_editor, current_filename],
        outputs=[image_display, final_caption, feedback_editor, filename_display, progress_display, current_filename]
    )

    prev_btn.click(
        on_previous,
        inputs=[feedback_editor, current_filename],
        outputs=[image_display, final_caption, feedback_editor, filename_display, progress_display, current_filename]
    )

    save_btn.click(
        on_save,
        inputs=[feedback_editor, current_filename],
        outputs=[image_display, final_caption, feedback_editor, filename_display, progress_display, current_filename]
    )

    jump_btn.click(
        on_jump,
        inputs=[jump_input, feedback_editor, current_filename],
        outputs=[image_display, final_caption, feedback_editor, filename_display, progress_display, current_filename]
    )

    # Load initial image on startup
    demo.load(
        load_initial,
        outputs=[image_display, final_caption, feedback_editor, filename_display, progress_display, current_filename]
    )

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 LAUNCHING CAPTION REVIEW & CLEANUP TOOL - FRESH START")
    print("=" * 70)
    print()
    print(f"📁 Training directory: {TRAINING_DIR}")
    print(f"📊 Total captions to review: {len(reviewer.records)}")
    print()
    print("📌 The app will open in your browser automatically")
    print("📌 URL: http://127.0.0.1:7862")
    print()
    print("🔐 Credentials:")
    print("   Username: admin")
    print("   Password: test123")
    print()
    print("To stop the server: Press Ctrl+C")
    print("=" * 70)
    print()

    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7862,
        auth=("admin", "test123"),
        show_error=True
    )
