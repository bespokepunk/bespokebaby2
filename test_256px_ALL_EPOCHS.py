#!/usr/bin/env python3
"""
256px Training - Complete Analysis Pipeline
Tests all 8 epochs + compares with 512px Epoch 8 baseline
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageDraw, ImageFont
import os
import json
from collections import Counter
from datetime import datetime

# Test prompts (same as CAPTION_FIX for direct comparison)
TEST_PROMPTS = [
    ("green_bg_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium male skin tone, bright green background, hard color borders, sharp pixel edges"),
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, dark brown eyes clearly distinct from lighter brown hair, pale female skin tone, gray background, hard color borders, sharp pixel edges"),
    ("golden_earrings", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, pale female skin tone, wearing large circular golden yellow drop earrings hanging from earlobes, teal blue background, hard color borders, sharp pixel edges"),
    ("sunglasses_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair behind sunglasses, brown eyes completely covered by sunglasses, medium male skin tone, wearing black rectangular stunner sunglasses with thin black plastic frames and thin temples behind ears, lenses completely cover eyes with white reflections, teal blue background, hard color borders, sharp pixel edges"),
    ("melon_lady", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, brown eyes, light brown female skin tone, wearing large circular golden yellow drop earrings hanging from earlobes, soft green background, hard color borders, sharp pixel edges"),
    ("cash_lad", "pixel art, 24x24, portrait of bespoke punk lad, gray wavy hair, brown eyes, pale male skin tone, teal blue background, hard color borders, sharp pixel edges"),
    ("carbon_lad", "pixel art, 24x24, portrait of bespoke punk lad, black hair, brown eyes, pale male skin tone, wearing gray structured baseball cap with curved front brim covering top of head down to hairline with white small logo on front center, gray background, hard color borders, sharp pixel edges"),
]

EPOCHS = list(range(1, 9))  # 1-8

# 512px Epoch 8 baseline for comparison
BASELINE_512PX_EPOCH8 = {
    "green_bg_lad": 199,
    "brown_eyes_lady": 261,
    "golden_earrings": 199,
    "sunglasses_lad": 208,
    "melon_lady": 237,
    "cash_lad": 209,
    "carbon_lad": 203,
    "average": 216.6
}

def count_unique_colors(img):
    """Count unique colors in PIL Image"""
    colors = img.getcolors(maxcolors=1000000)
    return len(colors) if colors else 0

def test_epoch(epoch_num, lora_path):
    """Test one epoch with all prompts"""
    print(f"\n{'='*60}")
    print(f"EPOCH {epoch_num}")
    print(f"{'='*60}\n")

    # Detect device
    if torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
    elif torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
    else:
        device = "cpu"
        dtype = torch.float32

    # Load pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=dtype,
        safety_checker=None
    ).to(device)

    # Load LoRA
    pipe.load_lora_weights(lora_path)

    output_dir = f"test_outputs_256px_epoch{epoch_num}"
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for prompt_name, prompt in TEST_PROMPTS:
        print(f"  {prompt_name}...", end=" ", flush=True)

        # Generate 24x24
        img = pipe(
            prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            width=24,
            height=24
        ).images[0]

        # Count colors
        colors = count_unique_colors(img)

        # Save
        save_path = os.path.join(output_dir, f"{prompt_name}_epoch{epoch_num}.png")
        img.save(save_path)

        # Compare with baseline
        baseline = BASELINE_512PX_EPOCH8.get(prompt_name, 0)
        diff = colors - baseline
        diff_pct = ((colors - baseline) / baseline * 100) if baseline > 0 else 0

        results.append({
            "prompt": prompt_name,
            "colors": colors,
            "baseline_512px": baseline,
            "diff": diff,
            "diff_pct": diff_pct
        })

        status = "✓" if colors <= baseline else "✗"
        print(f"{status} {colors} colors (baseline: {baseline}, {diff:+d}, {diff_pct:+.0f}%)")

    # Summary
    avg_colors = sum(r["colors"] for r in results) / len(results)
    avg_diff = avg_colors - BASELINE_512PX_EPOCH8["average"]
    avg_diff_pct = (avg_diff / BASELINE_512PX_EPOCH8["average"]) * 100

    print(f"\n  Average: {avg_colors:.1f} colors")
    print(f"  Baseline: {BASELINE_512PX_EPOCH8['average']:.1f} colors")
    print(f"  Difference: {avg_diff:+.1f} ({avg_diff_pct:+.1f}%)")

    # Cleanup
    del pipe
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    elif torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return results, avg_colors

def create_results_collage(all_results):
    """Create visual comparison collage"""
    print("\nCreating results collage...")

    # Load all images
    images = {}
    for epoch in EPOCHS:
        for prompt_name, _ in TEST_PROMPTS:
            img_path = f"test_outputs_256px_epoch{epoch}/{prompt_name}_epoch{epoch}.png"
            if os.path.exists(img_path):
                images[(epoch, prompt_name)] = Image.open(img_path)

    # Create collage (8 epochs × 7 prompts)
    scale = 20  # Scale up 24x24 to visible size
    img_w, img_h = 24 * scale, 24 * scale
    padding = 10
    label_h = 30

    grid_w = len(TEST_PROMPTS)
    grid_h = len(EPOCHS)

    collage_w = grid_w * (img_w + padding) + padding
    collage_h = label_h + grid_h * (img_h + label_h + padding) + padding

    collage = Image.new('RGB', (collage_w, collage_h), 'white')
    draw = ImageDraw.Draw(collage)

    # Try to load a font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except:
        font = ImageFont.load_default()
        font_small = font

    # Column headers (prompts)
    for col, (prompt_name, _) in enumerate(TEST_PROMPTS):
        x = padding + col * (img_w + padding)
        draw.text((x + 10, 5), prompt_name.replace("_", " "), fill='black', font=font_small)

    # Rows (epochs with images + color counts)
    for row, epoch in enumerate(EPOCHS):
        y_base = label_h + row * (img_h + label_h + padding) + padding

        # Epoch label
        draw.text((5, y_base + img_h // 2), f"E{epoch}", fill='black', font=font)

        # Images + color counts
        for col, (prompt_name, _) in enumerate(TEST_PROMPTS):
            x = padding + col * (img_w + padding)

            if (epoch, prompt_name) in images:
                img = images[(epoch, prompt_name)]
                img_scaled = img.resize((img_w, img_h), Image.NEAREST)
                collage.paste(img_scaled, (x, y_base))

                # Color count label
                colors = count_unique_colors(img)
                baseline = BASELINE_512PX_EPOCH8.get(prompt_name, 0)

                # Color code: green if better, red if worse
                color = 'green' if colors <= baseline else 'red'
                draw.text((x + 5, y_base + img_h + 2),
                         f"{colors}", fill=color, font=font_small)

    # Add legend
    legend_y = collage_h - 25
    draw.text((10, legend_y),
             f"Green = Better than 512px baseline | Red = Worse | Baseline Avg: {BASELINE_512PX_EPOCH8['average']:.1f} colors",
             fill='black', font=font_small)

    # Save
    collage_path = "RESULTS_256PX_VS_512PX_COLLAGE.png"
    collage.save(collage_path)
    print(f"  ✓ Saved: {collage_path}")

    return collage_path

def generate_report(all_results):
    """Generate comprehensive markdown report"""
    print("\nGenerating analysis report...")

    report = []
    report.append("# 256px Training Results - Complete Analysis")
    report.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Training:** SD1.5 LoRA @ 256x256 (8 epochs)")
    report.append(f"**Baseline:** 512px Epoch 8 (216.6 avg colors)")
    report.append("\n---\n")

    # Summary table
    report.append("## Epoch Summary\n")
    report.append("| Epoch | Avg Colors | vs Baseline | Change | Status |")
    report.append("|-------|-----------|-------------|--------|--------|")

    baseline_avg = BASELINE_512PX_EPOCH8["average"]
    best_epoch = None
    best_avg = float('inf')

    for epoch in EPOCHS:
        if epoch in all_results:
            _, avg = all_results[epoch]
            diff = avg - baseline_avg
            diff_pct = (diff / baseline_avg) * 100
            status = "✅ Better" if avg < baseline_avg else "❌ Worse"

            report.append(f"| {epoch} | {avg:.1f} | {baseline_avg:.1f} | {diff:+.1f} ({diff_pct:+.1f}%) | {status} |")

            if avg < best_avg:
                best_avg = avg
                best_epoch = epoch

    report.append(f"\n**Best Epoch:** {best_epoch} ({best_avg:.1f} avg colors, {((best_avg - baseline_avg) / baseline_avg * 100):+.1f}% vs baseline)")
    report.append("\n---\n")

    # Per-prompt breakdown
    report.append("## Per-Prompt Analysis\n")

    for prompt_name, _ in TEST_PROMPTS:
        report.append(f"\n### {prompt_name.replace('_', ' ').title()}\n")
        report.append(f"**Baseline (512px E8):** {BASELINE_512PX_EPOCH8.get(prompt_name, 'N/A')} colors\n")
        report.append("| Epoch | Colors | vs Baseline | Status |")
        report.append("|-------|--------|-------------|--------|")

        for epoch in EPOCHS:
            if epoch in all_results:
                results, _ = all_results[epoch]
                prompt_result = next((r for r in results if r["prompt"] == prompt_name), None)
                if prompt_result:
                    colors = prompt_result["colors"]
                    diff = prompt_result["diff"]
                    diff_pct = prompt_result["diff_pct"]
                    status = "✅" if colors <= BASELINE_512PX_EPOCH8.get(prompt_name, float('inf')) else "❌"
                    report.append(f"| {epoch} | {colors} | {diff:+d} ({diff_pct:+.0f}%) | {status} |")

    # Key findings
    report.append("\n---\n")
    report.append("## Key Findings\n")

    # Check if ANY epoch beat baseline
    any_better = any(all_results[e][1] < baseline_avg for e in EPOCHS if e in all_results)

    if any_better:
        report.append(f"- ✅ **SUCCESS:** Epoch {best_epoch} achieved {best_avg:.1f} avg colors ({((best_avg - baseline_avg) / baseline_avg * 100):+.1f}% vs 512px baseline)")
        report.append(f"- **Improvement:** 256px training with enhanced captions shows measurable quality improvement")
    else:
        report.append(f"- ❌ **ISSUE:** No epoch beat 512px baseline ({baseline_avg:.1f} colors)")
        report.append(f"- **Best 256px result:** Epoch {best_epoch} with {best_avg:.1f} colors ({((best_avg - baseline_avg) / baseline_avg * 100):+.1f}% worse)")
        report.append(f"- **Recommendation:** 256px may need further tuning, or 512px is optimal")

    # Training observations
    report.append("\n### Training Pattern Analysis\n")
    if len(all_results) >= 3:
        epoch_avgs = [all_results[e][1] for e in sorted(all_results.keys())]
        early_avg = sum(epoch_avgs[:3]) / 3
        late_avg = sum(epoch_avgs[-3:]) / 3

        if late_avg < early_avg:
            report.append(f"- Training improved over time (early: {early_avg:.1f} → late: {late_avg:.1f} colors)")
        else:
            report.append(f"- Training degraded over time (early: {early_avg:.1f} → late: {late_avg:.1f} colors)")

    report.append("\n---\n")
    report.append("## Next Steps\n")

    if any_better:
        report.append(f"1. **Deploy Epoch {best_epoch}** to production")
        report.append("2. Run visual quality audit on Epoch {best_epoch}")
        report.append("3. Compare side-by-side with 512px Epoch 8")
        report.append("4. Make final production decision")
    else:
        report.append("1. Investigate why 256px underperformed")
        report.append("2. Consider: caption quality, resolution mismatch, or hyperparameters")
        report.append("3. Option A: Stick with 512px Epoch 8 (current best)")
        report.append("4. Option B: Try Phase 3 improvements")

    # Save report
    report_path = "docs/256PX_TRAINING_COMPLETE_REPORT.md"
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))

    print(f"  ✓ Saved: {report_path}")
    return report_path

def main():
    print("="*60)
    print("256PX TRAINING - COMPLETE ANALYSIS")
    print("="*60)
    print(f"Testing 8 epochs against 512px baseline")
    print(f"Baseline: {BASELINE_512PX_EPOCH8['average']:.1f} avg colors")
    print("="*60)

    all_results = {}
    checkpoint_dir = "lora_checkpoints/256px_training"

    for epoch in EPOCHS:
        lora_path = f"{checkpoint_dir}/bespoke_baby_sd15_lora_256px-{epoch:06d}.safetensors"

        if not os.path.exists(lora_path):
            print(f"\n⚠️  Epoch {epoch} checkpoint not found: {lora_path}")
            continue

        results, avg = test_epoch(epoch, lora_path)
        all_results[epoch] = (results, avg)

    # Create visual collage
    collage_path = create_results_collage(all_results)

    # Generate report
    report_path = generate_report(all_results)

    # Final summary
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

    baseline_avg = BASELINE_512PX_EPOCH8["average"]
    best_epoch = min(all_results.keys(), key=lambda e: all_results[e][1])
    best_avg = all_results[best_epoch][1]

    print(f"\nBest Epoch: {best_epoch}")
    print(f"Best Average: {best_avg:.1f} colors")
    print(f"Baseline: {baseline_avg:.1f} colors")
    print(f"Difference: {best_avg - baseline_avg:+.1f} ({((best_avg - baseline_avg) / baseline_avg * 100):+.1f}%)")

    if best_avg < baseline_avg:
        print(f"\n✅ SUCCESS! 256px Epoch {best_epoch} beats 512px baseline!")
    else:
        print(f"\n❌ No improvement. 512px Epoch 8 remains best.")

    print(f"\nOutputs:")
    print(f"  - Visual collage: {collage_path}")
    print(f"  - Full report: {report_path}")
    print(f"  - Test images: test_outputs_256px_epoch*/")

if __name__ == "__main__":
    main()
