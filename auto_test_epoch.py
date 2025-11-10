#!/usr/bin/env python3
"""
Automated Epoch Testing - Complete Phase 2 Integration

Single command to fully test an epoch with quantitative metrics and logging.

This script orchestrates:
1. Generate test images (quick_test_epoch.py)
2. Run quantitative metrics (measure_color_accuracy.py, measure_pixel_art_quality.py)
3. Log results to Supabase with both subjective and quantitative scores
4. Optionally commit to git

Usage:
    python auto_test_epoch.py /path/to/checkpoint.safetensors --auto-commit

    # Interactive mode (prompts for scores)
    python auto_test_epoch.py checkpoint.safetensors

    # Auto-score mode (uses quantitative metrics to suggest scores)
    python auto_test_epoch.py checkpoint.safetensors --auto-score

    # Full automation (auto-score + auto-commit)
    python auto_test_epoch.py checkpoint.safetensors --auto-score --auto-commit
"""

import sys
import os
import json
import subprocess
import re
from pathlib import Path

def extract_epoch_number(checkpoint_path: str) -> int:
    """Extract epoch number from checkpoint filename"""
    filename = os.path.basename(checkpoint_path)
    match = re.search(r'-(\d{6})', filename)
    if match:
        return int(match.group(1).lstrip('0') or '0')
    raise ValueError(f"Could not extract epoch number from: {filename}")

def run_quick_test(checkpoint_path: str) -> tuple:
    """
    Run quick_test_epoch.py to generate test images

    Returns: (epoch_number, test_512_path, test_24_path)
    """
    print("=" * 80)
    print("STEP 1: Generating Test Images")
    print("=" * 80)

    result = subprocess.run(
        ['python', 'quick_test_epoch.py', checkpoint_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Error generating images: {result.stderr}")
        sys.exit(1)

    # Extract epoch number and paths
    epoch_num = extract_epoch_number(checkpoint_path)

    repo_root = Path(__file__).parent
    test_dir = repo_root / 'quick_tests' / f'epoch_{epoch_num}'
    test_512 = test_dir / f'bespoke_baby_sd15_lora-{epoch_num:06d}_test_512.png'
    test_24 = test_dir / f'bespoke_baby_sd15_lora-{epoch_num:06d}_test_24.png'

    print(f"✅ Images generated:")
    print(f"   512px: {test_512}")
    print(f"   24px:  {test_24}")

    return epoch_num, str(test_512), str(test_24)

def run_color_metrics(test_24_path: str) -> dict:
    """Run measure_color_accuracy.py and return metrics"""
    print("\n" + "=" * 80)
    print("STEP 2: Measuring Color Accuracy")
    print("=" * 80)

    result = subprocess.run(
        ['python', 'scripts/measure_color_accuracy.py', test_24_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"⚠️ Warning: Color metrics failed: {result.stderr}")
        return {}

    # Load the generated JSON
    json_path = test_24_path.replace('.png', '_color_metrics.json')
    with open(json_path, 'r') as f:
        metrics = json.load(f)

    print(f"✅ Color Accuracy: {metrics.get('overall_color_accuracy', 0):.2f}/100")
    print(f"   Background: {metrics['background']['actual_dominant_color']} "
          f"(expected: {metrics['background']['expected_color']})")
    if metrics.get('hair', {}).get('is_two_toned'):
        print(f"   ⚠️ Hair two-toning detected")

    return metrics

def run_style_metrics(test_24_path: str) -> dict:
    """Run measure_pixel_art_quality.py and return metrics"""
    print("\n" + "=" * 80)
    print("STEP 3: Measuring Style Quality")
    print("=" * 80)

    result = subprocess.run(
        ['python', 'scripts/measure_pixel_art_quality.py', test_24_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"⚠️ Warning: Style metrics failed: {result.stderr}")
        return {}

    # Load the generated JSON
    json_path = test_24_path.replace('.png', '_style_metrics.json')
    with open(json_path, 'r') as f:
        metrics = json.load(f)

    print(f"✅ Style Quality: {metrics.get('overall_style_quality', 0):.2f}/100")
    print(f"   Pixel Art: {'✅ YES' if metrics.get('is_pixel_art') else '❌ NO'}")
    print(f"   Unique Colors: {metrics.get('color_palette', {}).get('unique_colors', 0)}")

    return metrics

def suggest_scores_from_metrics(color_metrics: dict, style_metrics: dict) -> tuple:
    """
    Suggest subjective scores based on quantitative metrics

    Returns: (visual, style, prompt)
    """
    # Visual quality: Based on color purity and palette quality
    color_purity = color_metrics.get('color_purity', {}).get('color_purity_score', 0)
    palette_quality = style_metrics.get('color_palette', {}).get('palette_quality_score', 0)
    unique_colors = style_metrics.get('color_palette', {}).get('unique_colors', 500)

    # Scale to 0-10
    # Good pixel art: 20-100 colors, high purity
    visual = 5  # baseline
    if unique_colors < 400:
        visual += 2
    if unique_colors < 300:
        visual += 1
    if color_purity > 50:
        visual += 1
    if palette_quality > 50:
        visual += 1
    visual = min(visual, 10)

    # Style match: Based on pixel art purity and edge sharpness
    pixel_art_purity = style_metrics.get('photorealism_detection', {}).get('pixel_art_purity', 0)
    is_pixel_art = style_metrics.get('is_pixel_art', False)

    style = 5  # baseline
    if pixel_art_purity > 30:
        style += 2
    if pixel_art_purity > 50:
        style += 1
    if is_pixel_art:
        style += 2
    style = min(style, 10)

    # Prompt adherence: Based on color accuracy
    bg_correct = color_metrics.get('background', {}).get('is_correct', False)
    hair_not_two_toned = not color_metrics.get('hair', {}).get('is_two_toned', False)
    overall_color_acc = color_metrics.get('overall_color_accuracy', 0)

    prompt = 5  # baseline
    if bg_correct:
        prompt += 3
    if hair_not_two_toned:
        prompt += 1
    if overall_color_acc > 50:
        prompt += 1
    prompt = min(prompt, 10)

    return visual, style, prompt

def get_subjective_scores(color_metrics: dict, style_metrics: dict, auto_score: bool = False) -> tuple:
    """
    Get subjective scores from user or auto-suggest

    Returns: (visual, style, prompt, observations)
    """
    print("\n" + "=" * 80)
    print("STEP 4: Subjective Scoring")
    print("=" * 80)

    # Suggest scores based on metrics
    suggested_visual, suggested_style, suggested_prompt = suggest_scores_from_metrics(
        color_metrics, style_metrics
    )

    print(f"\n📊 Suggested scores based on quantitative metrics:")
    print(f"   Visual Quality:    {suggested_visual}/10")
    print(f"   Style Match:       {suggested_style}/10")
    print(f"   Prompt Adherence:  {suggested_prompt}/10")
    print(f"   Average:           {(suggested_visual + suggested_style + suggested_prompt) / 3:.1f}/10")

    if auto_score:
        print(f"\n✅ Using auto-suggested scores (--auto-score enabled)")
        observations = "Auto-scored based on quantitative metrics"
        return suggested_visual, suggested_style, suggested_prompt, observations

    print(f"\nEnter scores (0-10), or press Enter to accept suggestion:")

    visual_input = input(f"Visual Quality [{suggested_visual}]: ").strip()
    visual = int(visual_input) if visual_input else suggested_visual

    style_input = input(f"Style Match [{suggested_style}]: ").strip()
    style = int(style_input) if style_input else suggested_style

    prompt_input = input(f"Prompt Adherence [{suggested_prompt}]: ").strip()
    prompt = int(prompt_input) if prompt_input else suggested_prompt

    observations = input("Observations: ").strip()

    return visual, style, prompt, observations

def log_to_supabase(epoch_num: int, visual: int, style: int, prompt: int,
                    observations: str, color_metrics: dict, style_metrics: dict):
    """Log results to Supabase with quantitative metrics"""
    print("\n" + "=" * 80)
    print("STEP 5: Logging to Supabase")
    print("=" * 80)

    # First log with existing script (subjective scores)
    result = subprocess.run(
        ['python', 'log_epoch_to_supabase.py', str(epoch_num),
         str(visual), str(style), str(prompt), observations],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Error logging to Supabase: {result.stderr}")
        return False

    print(result.stdout)

    # TODO: Update log_epoch_to_supabase.py to also store quantitative_metrics
    # For now, metrics are stored in JSON files alongside images

    return True

def git_commit(epoch_num: int, visual: int, style: int, prompt: int, observations: str):
    """Commit results to git"""
    print("\n" + "=" * 80)
    print("STEP 6: Git Commit")
    print("=" * 80)

    avg_score = (visual + style + prompt) / 3

    # Stage files
    subprocess.run(['git', 'add', f'quick_tests/epoch_{epoch_num}/'], check=True)

    # Create commit message
    commit_msg = f"""Test Epoch {epoch_num} - Auto-tested with quantitative metrics

Scores: {visual}/{style}/{prompt} (Visual/Style/Prompt) = {avg_score:.1f}/10

Observations: {observations}

Quantitative metrics stored in JSON files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)

    print(f"✅ Committed Epoch {epoch_num} results")

    # Optionally push
    push = input("Push to remote? (y/n): ").strip().lower()
    if push == 'y':
        subprocess.run(['git', 'push'], check=True)
        print("✅ Pushed to remote")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    checkpoint_path = sys.argv[1]
    auto_score = '--auto-score' in sys.argv
    auto_commit = '--auto-commit' in sys.argv

    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        sys.exit(1)

    print(f"\n🤖 AUTOMATED EPOCH TESTING")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Auto-score: {auto_score}")
    print(f"Auto-commit: {auto_commit}")

    # Step 1: Generate test images
    epoch_num, test_512, test_24 = run_quick_test(checkpoint_path)

    # Step 2: Run color metrics
    color_metrics = run_color_metrics(test_24)

    # Step 3: Run style metrics
    style_metrics = run_style_metrics(test_24)

    # Step 4: Get subjective scores
    visual, style, prompt, observations = get_subjective_scores(
        color_metrics, style_metrics, auto_score
    )

    # Step 5: Log to Supabase
    log_to_supabase(epoch_num, visual, style, prompt, observations,
                    color_metrics, style_metrics)

    # Step 6: Git commit
    if auto_commit:
        git_commit(epoch_num, visual, style, prompt, observations)
    else:
        commit = input("\nCommit to git? (y/n): ").strip().lower()
        if commit == 'y':
            git_commit(epoch_num, visual, style, prompt, observations)

    print("\n" + "=" * 80)
    print("✅ EPOCH TESTING COMPLETE")
    print("=" * 80)
    print(f"Epoch {epoch_num}: {visual}/{style}/{prompt} = {(visual + style + prompt) / 3:.1f}/10")
    print(f"Color Accuracy: {color_metrics.get('overall_color_accuracy', 0):.1f}/100")
    print(f"Style Quality: {style_metrics.get('overall_style_quality', 0):.1f}/100")

if __name__ == "__main__":
    main()
