#!/usr/bin/env python3
"""
Log Epoch Results to Supabase - Professional ML Pipeline Tracking

This script documents each epoch's performance in Supabase for:
- Progress tracking
- Model comparison
- Production readiness decisions
- Historical analysis

Usage:
    python log_epoch_to_supabase.py 3 7 7 7
    (epoch_number visual_quality style_match prompt_adherence)
"""

import sys
import os
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_HOST = "aws-1-us-east-2.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres.qwvncbcphuyobijakdsr"
DB_PASSWORD = os.getenv("DB_PASSWORD", "Ilyssa2025")

# Training run name
TRAINING_RUN_NAME = "SD15_FINAL_CORRECTED_CAPTIONS"

def log_epoch_result(epoch_num, visual_quality, style_match, prompt_adherence,
                     observations="", issues=None, strengths=None):
    """
    Log epoch test results to Supabase

    Args:
        epoch_num: Epoch number (1-10)
        visual_quality: Score 0-10
        style_match: Score 0-10
        prompt_adherence: Score 0-10
        observations: Text observations
        issues: List of issues found
        strengths: List of strengths
    """

    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Get training run ID
    cur.execute(
        "SELECT id FROM training_runs WHERE run_name = %s",
        (TRAINING_RUN_NAME,)
    )
    result = cur.fetchone()
    if not result:
        print(f"❌ Training run '{TRAINING_RUN_NAME}' not found!")
        return False

    training_run_id = result[0]

    # Determine verdict based on scores
    avg_score = (visual_quality + style_match + prompt_adherence) / 3
    if avg_score >= 8:
        verdict = "best"
    elif avg_score >= 7:
        verdict = "good"
    elif avg_score >= 5:
        verdict = "acceptable"
    else:
        verdict = "skip"

    # Checkpoint path
    checkpoint_path = f"/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-{epoch_num:06d}.safetensors"

    # Test image paths
    test_image_dir = f"/Users/ilyssaevans/Documents/GitHub/bespokebaby2/quick_tests/epoch_{epoch_num}"
    test_image_paths = [
        f"{test_image_dir}/bespoke_baby_sd15_lora-{epoch_num:06d}_test_512.png",
        f"{test_image_dir}/bespoke_baby_sd15_lora-{epoch_num:06d}_test_24.png"
    ]

    # Analyze issues from scores
    auto_issues = []
    if prompt_adherence < 7:
        auto_issues.append("wrong_background_color")
    if visual_quality < 7:
        auto_issues.append("color_accuracy_issues")

    all_issues = (issues or []) + auto_issues

    # Default strengths
    default_strengths = ["pixel_art_style_maintained", "not_photorealistic"]
    all_strengths = (strengths or []) + default_strengths

    # Insert or update epoch result
    cur.execute("""
        INSERT INTO epoch_results (
            training_run_id,
            epoch_number,
            checkpoint_path,
            checkpoint_file_size_mb,
            test_output_dir,
            num_test_images,
            visual_quality_score,
            style_match_score,
            prompt_adherence_score,
            has_wrong_backgrounds,
            has_wrong_colors,
            is_photorealistic,
            issues_detail,
            strengths_detail,
            verdict,
            production_ready,
            observations,
            test_image_paths,
            notes
        ) VALUES (
            %s, %s, %s, 36, %s, 2, %s, %s, %s,
            %s, %s, false, %s, %s, %s, false, %s, %s,
            'Tested with FINAL CORRECTED captions (12+ hex codes, lips, expressions)'
        )
        ON CONFLICT (training_run_id, epoch_number)
        DO UPDATE SET
            visual_quality_score = EXCLUDED.visual_quality_score,
            style_match_score = EXCLUDED.style_match_score,
            prompt_adherence_score = EXCLUDED.prompt_adherence_score,
            observations = EXCLUDED.observations,
            issues_detail = EXCLUDED.issues_detail,
            strengths_detail = EXCLUDED.strengths_detail,
            verdict = EXCLUDED.verdict,
            test_image_paths = EXCLUDED.test_image_paths
    """, (
        training_run_id,
        epoch_num,
        checkpoint_path,
        test_image_dir,
        visual_quality,
        style_match,
        prompt_adherence,
        prompt_adherence < 7,  # has_wrong_backgrounds
        visual_quality < 7,     # has_wrong_colors
        all_issues,
        all_strengths,
        verdict,
        observations,
        test_image_paths
    ))

    conn.commit()

    print(f"\n✅ Epoch {epoch_num} logged to Supabase!")
    print(f"   Scores: Visual={visual_quality}, Style={style_match}, Prompt={prompt_adherence}")
    print(f"   Average: {avg_score:.1f}/10")
    print(f"   Verdict: {verdict}")
    print(f"   Issues: {', '.join(all_issues) if all_issues else 'None'}")

    cur.close()
    conn.close()

    return True

def main():
    if len(sys.argv) < 5:
        print("Usage: python log_epoch_to_supabase.py <epoch> <visual> <style> <prompt> [observations]")
        print("\nExample:")
        print("  python log_epoch_to_supabase.py 3 7 7 7 'Two-toned hair, garbled crown, pink background'")
        print("\nScores: 0-10 (0=terrible, 10=perfect)")
        return

    epoch = int(sys.argv[1])
    visual = int(sys.argv[2])
    style = int(sys.argv[3])
    prompt = int(sys.argv[4])
    obs = sys.argv[5] if len(sys.argv) > 5 else ""

    log_epoch_result(epoch, visual, style, prompt, obs)

if __name__ == "__main__":
    main()
