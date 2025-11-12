#!/usr/bin/env python3
"""
Sample Review UI - Side-by-side caption comparison
Review AI-improved captions with visual diff and manual editing
"""

import gradio as gr
import json
from pathlib import Path
from PIL import Image
import difflib
import psycopg2
from psycopg2.extras import RealDictCursor

TRAINING_DIR = Path("runpod_package/training_data")
IMPROVED_DIR = Path("improved_samples")
REPORT_FILE = IMPROVED_DIR / "simplification_report.json"
SUPABASE_URL = "postgresql://postgres.qwvncbcphuyobijakdsr:Ilyssa2025@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

class SampleReviewer:
    def __init__(self):
        self.load_report()
        self.current_index = 0
        self.decisions = {}  # Track user decisions
        self.setup_database()
        self.load_existing_feedback_from_db()

    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(SUPABASE_URL)
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            return None

    def setup_database(self):
        """Ensure caption_fresh_review table exists (already created, just checking)"""
        conn = self.get_db_connection()
        if not conn:
            print("⚠️ Skipping database setup - no connection")
            return

        try:
            with conn.cursor() as cur:
                # Table already exists, just verify
                cur.execute("SELECT COUNT(*) FROM caption_fresh_review")
                count = cur.fetchone()[0]
                print(f"✅ Database table ready: caption_fresh_review ({count} existing rows)")
        except Exception as e:
            print(f"⚠️ Database check failed: {e}")
        finally:
            conn.close()

    def load_existing_feedback_from_db(self):
        """Load any existing feedback from database"""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Use actual column names: new_feedback, review_status (not user_feedback, user_status)
                cur.execute("SELECT filename, new_feedback, review_status FROM caption_fresh_review")
                for row in cur.fetchall():
                    self.decisions[row['filename']] = {
                        'feedback': row['new_feedback'] or '',
                        'status': row['review_status'] or 'pending'
                    }
            print(f"✅ Loaded {len(self.decisions)} existing feedback entries from database")
        except Exception as e:
            print(f"⚠️ Could not load existing feedback: {e}")
        finally:
            conn.close()

    def load_report(self):
        """Load the simplification report"""
        with open(REPORT_FILE, 'r') as f:
            report = json.load(f)
        self.samples = report['samples']
        self.summary = report['summary']
        print(f"✅ Loaded {len(self.samples)} samples for review")

    def get_diff_html(self, original, improved):
        """Generate HTML diff highlighting"""
        # Split into words for better diff
        orig_words = original.split()
        imp_words = improved.split()

        # Generate diff
        diff = difflib.SequenceMatcher(None, orig_words, imp_words)

        html_parts = []
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            if tag == 'equal':
                html_parts.append(' '.join(orig_words[i1:i2]))
            elif tag == 'delete':
                deleted = ' '.join(orig_words[i1:i2])
                html_parts.append(f'<span style="background-color: #ffcccc; text-decoration: line-through;">{deleted}</span>')
            elif tag == 'insert':
                inserted = ' '.join(imp_words[j1:j2])
                html_parts.append(f'<span style="background-color: #ccffcc; font-weight: bold;">{inserted}</span>')
            elif tag == 'replace':
                deleted = ' '.join(orig_words[i1:i2])
                inserted = ' '.join(imp_words[j1:j2])
                html_parts.append(f'<span style="background-color: #ffcccc; text-decoration: line-through;">{deleted}</span>')
                html_parts.append(f'<span style="background-color: #ccffcc; font-weight: bold;">{inserted}</span>')

        return ' '.join(html_parts)

    def get_changes_markdown(self, changes, original_length, new_length, target_met):
        """Format changes as markdown"""
        lines = ["### Changes Applied:\n"]

        for i, change in enumerate(changes, 1):
            lines.append(f"{i}. {change}")

        lines.append(f"\n### Metrics:")
        lines.append(f"- Original: **{original_length} chars**")
        lines.append(f"- Improved: **{new_length} chars**")
        lines.append(f"- Reduction: **{original_length - new_length} chars ({round((original_length - new_length) / original_length * 100, 1)}%)**")
        lines.append(f"- Target (150-180): **{'✅ MET' if target_met else '⚠️ NOT MET'}**")

        return "\n".join(lines)

    def get_current_data(self):
        """Get current sample data"""
        if not self.samples:
            return None, "", "", "", "", "", 0, len(self.samples)

        sample = self.samples[self.current_index]
        filename = sample['filename']
        original = sample['original']
        improved = sample['improved']
        changes = sample['changes']
        original_length = sample['original_length']
        new_length = sample['new_length']
        target_met = sample['target_met']

        # Load image
        image_path = TRAINING_DIR / filename.replace('.txt', '.png')
        if image_path.exists():
            image = Image.open(image_path)
            image = image.resize((360, 360), Image.NEAREST)  # Compact size
        else:
            image = None

        # Generate diff HTML
        diff_html = self.get_diff_html(original, improved)

        # Format changes
        changes_md = self.get_changes_markdown(changes, original_length, new_length, target_met)

        # Get current decision
        current_decision = self.decisions.get(filename, {'status': 'pending', 'feedback': ''})

        progress = f"Sample {self.current_index + 1} of {len(self.samples)}"

        return (
            image,
            filename,
            original,
            improved,
            diff_html,
            changes_md,
            current_decision['feedback'],
            current_decision['status'],
            progress,
            self.current_index + 1
        )

    def save_to_database(self, filename, feedback, status):
        """Save feedback to Supabase database"""
        conn = self.get_db_connection()
        if not conn:
            print(f"⚠️ Cannot save to database - no connection")
            return

        try:
            # Get original and improved captions for this sample
            sample = next((s for s in self.samples if s['filename'] == filename), None)
            if not sample:
                print(f"⚠️ Sample not found: {filename}")
                return

            with conn.cursor() as cur:
                # Use actual column names: final_used_caption, new_feedback, review_status
                cur.execute("""
                    INSERT INTO caption_fresh_review
                        (filename, original_caption, final_used_caption, new_feedback, review_status, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (filename)
                    DO UPDATE SET
                        new_feedback = EXCLUDED.new_feedback,
                        review_status = EXCLUDED.review_status,
                        updated_at = NOW()
                """, (filename, sample['original'], sample['improved'], feedback, status))
                conn.commit()
                print(f"💾 Saved to Supabase: {filename} - {status}")
        except Exception as e:
            print(f"⚠️ Failed to save to database: {e}")
        finally:
            conn.close()

    def next_sample(self, current_filename, feedback, status):
        """Save current feedback and move to next"""
        if current_filename:
            self.decisions[current_filename] = {
                'status': status,
                'feedback': feedback
            }
            # Save to database immediately
            self.save_to_database(current_filename, feedback, status)

        if self.current_index < len(self.samples) - 1:
            self.current_index += 1

        return self.get_current_data()

    def previous_sample(self, current_filename, feedback, status):
        """Save current feedback and move to previous"""
        if current_filename:
            self.decisions[current_filename] = {
                'status': status,
                'feedback': feedback
            }
            # Save to database immediately
            self.save_to_database(current_filename, feedback, status)

        if self.current_index > 0:
            self.current_index -= 1

        return self.get_current_data()

    def quick_approve(self, current_filename):
        """Quick approve AI suggestion"""
        feedback = 'AI version looks good'
        status = 'ai_approved'
        self.decisions[current_filename] = {
            'status': status,
            'feedback': feedback
        }
        # Save to database immediately
        self.save_to_database(current_filename, feedback, status)
        return status, feedback

    def quick_reject(self, current_filename):
        """Quick reject - keep original"""
        feedback = 'Keep original caption'
        status = 'keep_original'
        self.decisions[current_filename] = {
            'status': status,
            'feedback': feedback
        }
        # Save to database immediately
        self.save_to_database(current_filename, feedback, status)
        return status, feedback

    def save_feedback(self, current_filename, feedback):
        """Save custom feedback"""
        status = 'has_feedback'
        self.decisions[current_filename] = {
            'status': status,
            'feedback': feedback
        }
        # Save to database immediately
        self.save_to_database(current_filename, feedback, status)
        return status, feedback

    def export_decisions(self):
        """Export all feedback as JSON for AI processing"""
        output_file = Path("user_feedback_on_samples.json")

        # Compile feedback with original and improved captions
        feedback_data = []
        for sample in self.samples:
            filename = sample['filename']
            decision = self.decisions.get(filename, {'status': 'pending', 'feedback': ''})

            feedback_data.append({
                'filename': filename,
                'original_caption': sample['original'],
                'ai_improved_caption': sample['improved'],
                'user_status': decision['status'],
                'user_feedback': decision['feedback'],
                'original_length': sample['original_length'],
                'ai_improved_length': sample['new_length']
            })

        # Save as JSON
        with open(output_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)

        # Count statuses
        ai_approved = sum(1 for d in self.decisions.values() if d['status'] == 'ai_approved')
        keep_original = sum(1 for d in self.decisions.values() if d['status'] == 'keep_original')
        has_feedback = sum(1 for d in self.decisions.values() if d['status'] == 'has_feedback')
        pending = len(self.samples) - len(self.decisions)

        summary = f"""
✅ Feedback Export Complete!

Saved to: {output_file}

Summary:
- ✅ AI Approved: {ai_approved}
- ❌ Keep Original: {keep_original}
- 📝 Custom Feedback: {has_feedback}
- ⏳ Pending: {pending}
- 📊 Total: {len(self.samples)}

Next Step: Run intelligent feedback processor to generate final captions
"""
        return summary

# Initialize reviewer
reviewer = SampleReviewer()

# Create Gradio interface with compact CSS
custom_css = """
.compact-container {
    max-width: 100%;
    padding: 10px;
}
.compact-header {
    margin-bottom: 10px;
    padding: 10px;
    background: #f0f0f0;
    border-radius: 5px;
}
.compact-header h1 {
    margin: 0;
    font-size: 1.5rem;
}
.compact-header p {
    margin: 5px 0;
    font-size: 0.9rem;
}
textarea {
    font-size: 0.85rem !important;
    line-height: 1.3 !important;
}
"""

with gr.Blocks(title="Caption Sample Review", theme=gr.themes.Soft(), css=custom_css) as demo:
    with gr.Row(elem_classes="compact-header"):
        gr.HTML(f"""
        <div>
            <h1>📊 Caption Review - All 203 Captions</h1>
            <p><b>Total:</b> {reviewer.summary['total_samples']} | <b>Avg reduction:</b> {reviewer.summary['avg_reduction_pct']}% | <b>Target met:</b> {reviewer.summary['target_met_count']}/{reviewer.summary['total_samples']}</p>
        </div>
        """)

    with gr.Row():
        # LEFT: Image and navigation
        with gr.Column(scale=1):
            image_display = gr.Image(label="24x24 Punk (scaled up)", type="pil")
            filename_display = gr.Textbox(label="Filename", interactive=False)
            progress_display = gr.Textbox(label="Progress", interactive=False)
            status_display = gr.Textbox(label="Decision Status", interactive=False)

            with gr.Row():
                prev_btn = gr.Button("⬅️ Previous", variant="secondary", size="lg")
                next_btn = gr.Button("➡️ Next", variant="secondary", size="lg")

        # RIGHT: Captions and decisions
        with gr.Column(scale=2):
            with gr.Accordion("📄 Original Caption", open=False):
                original_caption = gr.Textbox(
                    label="",
                    lines=2,
                    interactive=False,
                    show_copy_button=True
                )

            with gr.Accordion("🤖 AI-Improved Caption", open=True):
                ai_improved_caption = gr.Textbox(
                    label="",
                    lines=2,
                    interactive=False,
                    show_copy_button=True
                )

            with gr.Accordion("🔍 Diff Highlighting", open=False):
                diff_display = gr.HTML(label="")

            with gr.Accordion("📊 Changes & Metrics", open=False):
                changes_display = gr.Markdown(label="")

            feedback_box = gr.Textbox(
                label="✏️ Your Feedback (NOT the final caption - just notes/corrections)",
                lines=2,
                placeholder="Examples: 'looks good', 'too long', 'missing brown hair color', 'keep original', 'remove background description', 'AI version looks good'..."
            )

            with gr.Row():
                quick_approve_btn = gr.Button("✅ AI Looks Good", variant="primary", size="lg")
                quick_reject_btn = gr.Button("❌ Keep Original", variant="secondary", size="lg")
                save_feedback_btn = gr.Button("💾 Save My Feedback", variant="stop", size="lg")

    with gr.Row():
        export_btn = gr.Button("📦 Export All Feedback (for AI processing)", variant="primary", size="lg")
        export_status = gr.Textbox(label="Export Status", lines=6, interactive=False)

    gr.Markdown("""
    ---
    ### 📝 Workflow:
    1. **Review samples** - See original vs AI-improved
    2. **Leave feedback** - Quick approve/reject or write notes
    3. **Export feedback** - Save all your feedback
    4. **AI processes** - Intelligently applies your feedback to generate final captions
    5. **Final validation** - Review and approve before training
    """)

    # Hidden state
    current_filename = gr.Textbox(visible=False)
    current_jump_index = gr.Number(visible=False)

    # Load initial
    def load_initial():
        return reviewer.get_current_data()

    # Navigation
    def on_next(filename, feedback, status):
        return reviewer.next_sample(filename, feedback, status)

    def on_previous(filename, feedback, status):
        return reviewer.previous_sample(filename, feedback, status)

    # Quick decisions
    def on_quick_approve(filename):
        status, feedback = reviewer.quick_approve(filename)
        return status, feedback

    def on_quick_reject(filename):
        status, feedback = reviewer.quick_reject(filename)
        return status, feedback

    def on_save_feedback(filename, feedback):
        status, feedback_text = reviewer.save_feedback(filename, feedback)
        return status, feedback_text

    def on_export():
        return reviewer.export_decisions()

    # Wire up buttons
    next_btn.click(
        on_next,
        inputs=[current_filename, feedback_box, status_display],
        outputs=[image_display, current_filename, original_caption, ai_improved_caption,
                 diff_display, changes_display, feedback_box, status_display, progress_display, current_jump_index]
    )

    prev_btn.click(
        on_previous,
        inputs=[current_filename, feedback_box, status_display],
        outputs=[image_display, current_filename, original_caption, ai_improved_caption,
                 diff_display, changes_display, feedback_box, status_display, progress_display, current_jump_index]
    )

    quick_approve_btn.click(
        on_quick_approve,
        inputs=[current_filename],
        outputs=[status_display, feedback_box]
    )

    quick_reject_btn.click(
        on_quick_reject,
        inputs=[current_filename],
        outputs=[status_display, feedback_box]
    )

    save_feedback_btn.click(
        on_save_feedback,
        inputs=[current_filename, feedback_box],
        outputs=[status_display, feedback_box]
    )

    export_btn.click(
        on_export,
        outputs=[export_status]
    )

    # Load initial on startup
    demo.load(
        load_initial,
        outputs=[image_display, current_filename, original_caption, ai_improved_caption,
                 diff_display, changes_display, feedback_box, status_display, progress_display, current_jump_index]
    )

if __name__ == "__main__":
    print("="*70)
    print("🚀 LAUNCHING SAMPLE REVIEW UI")
    print("="*70)
    print()
    print(f"📊 Samples to review: {len(reviewer.samples)}")
    print(f"📁 Training data: {TRAINING_DIR}")
    print(f"📁 Improved samples: {IMPROVED_DIR}")
    print()
    print("📌 URL: http://127.0.0.1:7863")
    print()
    print("To stop: Press Ctrl+C")
    print("="*70)
    print()

    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7863,
        show_error=True
    )
