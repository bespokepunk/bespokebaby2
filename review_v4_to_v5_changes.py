#!/usr/bin/env python3
"""
Review V4 → V5 Changes Only

Shows ONLY the captions that changed based on your feedback.
Side-by-side: V4 vs V5
SAVES TO SUPABASE!
"""

import gradio as gr
from pathlib import Path
from PIL import Image
import psycopg2
from psycopg2.extras import RealDictCursor

V4_DIR = Path("improved_samples_v4")
V5_DIR = Path("improved_samples_v5")
IMAGES_DIR = Path("runpod_package/training_data")

# SUPABASE CONNECTION
SUPABASE_URL = "postgresql://postgres.qwvncbcphuyobijakdsr:Ilyssa2025@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

class ChangeReviewer:
    def __init__(self):
        self.current_index = 0
        self.db_url = SUPABASE_URL
        self.setup_database()
        self.load_changed_captions()

    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            return None

    def setup_database(self):
        """Create v5_review table if it doesn't exist"""
        conn = self.get_db_connection()
        if not conn:
            print("⚠️ Skipping database setup - no connection")
            return

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS caption_v5_review (
                        id SERIAL PRIMARY KEY,
                        filename TEXT NOT NULL UNIQUE,
                        v4_caption TEXT,
                        v5_caption TEXT,
                        feedback TEXT,
                        review_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                conn.commit()
                print("✅ Database table ready: caption_v5_review")
        except Exception as e:
            print(f"⚠️ Database setup failed: {e}")
        finally:
            conn.close()

    def load_changed_captions(self):
        """Load only captions that changed from V4 to V5"""
        self.records = []

        # Load existing feedback from DB
        existing_feedback = {}
        conn = self.get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT filename, feedback, review_status FROM caption_v5_review")
                    for row in cur.fetchall():
                        existing_feedback[row['filename']] = {
                            'feedback': row.get('feedback', ''),
                            'status': row.get('review_status', 'pending')
                        }
            except Exception as e:
                print(f"⚠️ Could not load existing feedback: {e}")
            finally:
                conn.close()

        for v5_file in sorted(V5_DIR.glob("*.txt")):
            v4_file = V4_DIR / v5_file.name

            if not v4_file.exists():
                continue

            with open(v4_file, 'r') as f:
                v4_caption = f.read().strip()
            with open(v5_file, 'r') as f:
                v5_caption = f.read().strip()

            # Only include if changed
            if v4_caption != v5_caption:
                image_file = v5_file.name.replace('.txt', '.png')
                feedback_data = existing_feedback.get(image_file, {'feedback': '', 'status': 'pending'})
                self.records.append({
                    'filename': image_file,
                    'v4': v4_caption,
                    'v5': v5_caption,
                    'feedback': feedback_data['feedback'],
                    'status': feedback_data['status']
                })

        print(f"✅ Found {len(self.records)} changed captions to review")

    def save_feedback(self, filename, feedback, status='reviewed'):
        """Save feedback to Supabase"""
        conn = self.get_db_connection()
        if not conn:
            print("⚠️ Cannot save feedback - no database connection")
            return

        record = self.records[self.current_index]
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO caption_v5_review
                        (filename, v4_caption, v5_caption, feedback, review_status, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (filename)
                    DO UPDATE SET
                        feedback = EXCLUDED.feedback,
                        review_status = EXCLUDED.review_status,
                        updated_at = NOW()
                """, (filename, record['v4'], record['v5'], feedback, status))
                conn.commit()
                print(f"💾 Saved to Supabase: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save feedback: {e}")
        finally:
            conn.close()

    def get_current_data(self):
        """Get current record"""
        if not self.records:
            return None, "", "", "", "", 0, len(self.records)

        record = self.records[self.current_index]

        # Load image
        image_path = IMAGES_DIR / record['filename']
        if image_path.exists():
            image = Image.open(image_path)
            image = image.resize((480, 480), Image.NEAREST)
        else:
            image = None

        progress = f"Changed caption {self.current_index + 1} of {len(self.records)}"

        return (
            image,
            record['v4'],
            record['v5'],
            record['feedback'],
            record['filename'],
            self.current_index + 1,
            len(self.records)
        )

    def approve_current(self, current_feedback, current_filename):
        """Quick approve and move to next"""
        if current_filename:
            feedback_to_save = current_feedback.strip() if current_feedback.strip() else "✅ APPROVED - V5 caption looks good"
            self.save_feedback(current_filename, feedback_to_save, 'approved')

        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def reject_current(self, current_feedback, current_filename):
        """Quick reject and move to next"""
        if current_filename:
            if current_feedback.strip():
                feedback_to_save = f"❌ NEEDS WORK - {current_feedback.strip()}"
            else:
                feedback_to_save = "❌ NEEDS WORK - See notes"
            self.save_feedback(current_filename, feedback_to_save, 'needs_work')

        if self.current_index < len(self.records) - 1:
            self.current_index += 1

        return self.get_current_data()

    def next_image(self, current_feedback, current_filename):
        """Save and move to next"""
        if current_filename and current_feedback.strip():
            self.save_feedback(current_filename, current_feedback, 'reviewed')

        if self.current_index < len(self.records) - 1:
            self.current_index += 1
        return self.get_current_data()

    def previous_image(self, current_feedback, current_filename):
        """Save and move to previous"""
        if current_filename and current_feedback.strip():
            self.save_feedback(current_filename, current_feedback, 'reviewed')

        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_data()

    def jump_to_image(self, index, current_feedback, current_filename):
        """Save and jump to specific index"""
        if current_filename and current_feedback.strip():
            self.save_feedback(current_filename, current_feedback, 'reviewed')

        if 0 < index <= len(self.records):
            self.current_index = index - 1
        return self.get_current_data()

# Create reviewer
print("🚀 Initializing V4 → V5 Change Reviewer...")
reviewer = ChangeReviewer()

# Create UI
with gr.Blocks(title="V4 → V5 Changes Review", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📊 Review V4 → V5 Changes (SAVES TO SUPABASE!)")
    gr.Markdown(f"""
    ## {len(reviewer.records)} captions changed based on your feedback

    **✅ All feedback is saved to Supabase database: `caption_v5_review` table**

    **Changes applied:**
    - Fixed missing/incorrect eye colors
    - Fixed "medium to light" → "medium light"
    - Removed "pal" garbage text
    - Fixed background descriptions (solid vs divided vs gradient)
    - Removed duplicate words
    - Fixed "wearing stubble" → "with stubble/beard"
    - Removed parenthetical details
    - Fixed spacing and typos
    - Applied specific file fixes from your feedback

    **How to use:**
    - Click **✅ Looks Good & Next** if V5 is good (saves & auto-advances)
    - Click **❌ Needs Work & Next** if it needs fixes (saves & auto-advances)
    - Add notes in the feedback box before clicking buttons
    - All feedback is **automatically saved to Supabase!**
    """)

    with gr.Row():
        with gr.Column(scale=1):
            image_display = gr.Image(label="Image (24x24 scaled up)", type="pil")
            filename_display = gr.Textbox(label="Filename", interactive=False)
            progress_display = gr.Textbox(label="Progress", interactive=False)

        with gr.Column(scale=2):
            v4_caption = gr.Textbox(
                label="📄 V4 Caption (before)",
                lines=4,
                interactive=False,
                show_copy_button=True
            )

            v5_caption = gr.Textbox(
                label="✨ V5 Caption (after your feedback)",
                lines=4,
                interactive=False,
                show_copy_button=True
            )

            feedback_box = gr.Textbox(
                label="✏️ Your Feedback/Notes (saved to Supabase)",
                lines=3,
                placeholder="Add notes, corrections, or leave blank if approved..."
            )

            with gr.Row():
                approve_btn = gr.Button("✅ Looks Good & Next", variant="primary", size="lg")
                reject_btn = gr.Button("❌ Needs Work & Next", variant="stop", size="lg")

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous", variant="secondary")
                next_btn = gr.Button("➡️ Next", variant="secondary")

            with gr.Row():
                jump_input = gr.Number(label="Jump to #", precision=0, minimum=1)
                jump_btn = gr.Button("🎯 Jump")

    # Hidden state for current filename
    current_filename = gr.Textbox(visible=False, label="Current Filename")

    # Actions
    def load_initial():
        image, v4, v5, feedback, filename, current, total = reviewer.get_current_data()
        return image, v4, v5, feedback, filename, f"{current}/{total}", filename

    def on_approve(feedback, filename):
        return reviewer.approve_current(feedback, filename)

    def on_reject(feedback, filename):
        return reviewer.reject_current(feedback, filename)

    def on_next(feedback, filename):
        return reviewer.next_image(feedback, filename)

    def on_previous(feedback, filename):
        return reviewer.previous_image(feedback, filename)

    def on_jump(index, feedback, filename):
        return reviewer.jump_to_image(index, feedback, filename)

    # Wire up
    outputs = [image_display, v4_caption, v5_caption, feedback_box, filename_display,
               progress_display, current_filename]

    approve_btn.click(on_approve, inputs=[feedback_box, current_filename], outputs=outputs)
    reject_btn.click(on_reject, inputs=[feedback_box, current_filename], outputs=outputs)
    next_btn.click(on_next, inputs=[feedback_box, current_filename], outputs=outputs)
    prev_btn.click(on_previous, inputs=[feedback_box, current_filename], outputs=outputs)
    jump_btn.click(on_jump, inputs=[jump_input, feedback_box, current_filename], outputs=outputs)

    demo.load(load_initial, outputs=outputs)

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 LAUNCHING V4 → V5 CHANGE REVIEWER")
    print("=" * 70)
    print(f"📊 Changed captions to review: {len(reviewer.records)}")
    print()
    print("📌 URL: http://127.0.0.1:7866")
    print("=" * 70)

    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7866,
        show_error=True
    )
