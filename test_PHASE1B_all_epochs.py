#!/usr/bin/env python3
"""
Test All Phase 1B Epochs (1-8)
Compare simplified captions vs CAPTION_FIX baseline

Phase 1B Changes:
- Simplified captions (removed micro-details)
- 512px resolution (proven optimal)
- 8 epochs training

This script tests all epochs to find the optimal one.
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import numpy as np
import os
from pathlib import Path
import json

# Paths
LORA_DIR = Path("lora_checkpoints/phase1b")
OUTPUT_BASE_DIR = Path("test_outputs_PHASE1B")
OUTPUT_BASE_DIR.mkdir(exist_ok=True)

# Test prompts using CAPTION_FIX format (no hex codes, simplified descriptions)
TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, tan skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("blue_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, blue eyes, light skin, red solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("green_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, black hair, green eyes, medium skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("afro_hair", "pixel art, 24x24, portrait of bespoke punk lady, large voluminous brown afro hair, brown eyes, dark skin, orange solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("sunglasses", "pixel art, 24x24, portrait of bespoke punk lad, blonde hair, wearing black rectangular sunglasses covering eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("earrings", "pixel art, 24x24, portrait of bespoke punk lady, red hair, wearing golden circular earrings, blue eyes, light skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("cap", "pixel art, 24x24, portrait of bespoke punk lad, black hair, wearing red baseball cap, brown eyes, dark skin, gray solid background, sharp pixel edges, hard color borders, retro pixel art style"),
]

def count_unique_colors(image_24):
    """Count unique RGB colors in 24x24 image"""
    arr = np.array(image_24)
    pixels = arr.reshape(-1, 3)
    unique = np.unique(pixels, axis=0)
    return len(unique)

def test_epoch(epoch_num):
    """Test a single epoch with all prompts"""
    lora_path = LORA_DIR / f"phase1b_epoch{epoch_num}.safetensors"
    output_dir = OUTPUT_BASE_DIR / f"epoch_{epoch_num}"
    output_dir.mkdir(exist_ok=True)

    print("=" * 100)
    print(f"TESTING PHASE 1B EPOCH {epoch_num}")
    print("=" * 100)
    print(f"LoRA: {lora_path}")
    print(f"Output: {output_dir}")
    print()

    # Load SD 1.5 pipeline
    print("Loading SD 1.5 pipeline...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
    )

    # Load LoRA
    print(f"Loading LoRA for Epoch {epoch_num}...")
    pipe.load_lora_weights(str(lora_path))

    # Move to device
    if torch.backends.mps.is_available():
        print("Using MPS (Apple Silicon)")
        device = "mps"
        pipe = pipe.to("mps")
    elif torch.cuda.is_available():
        print("Using CUDA")
        device = "cuda"
        pipe = pipe.to("cuda")
    else:
        print("Using CPU (will be slow)")
        device = "cpu"

    print("✓ Pipeline ready!")
    print()

    # Track results
    results = {
        'epoch': epoch_num,
        'lora_path': str(lora_path),
        'generations': []
    }

    color_counts = []

    # Generate test images
    for name, prompt in TEST_PROMPTS:
        print(f"Generating: {name}")
        print(f"  Prompt: {prompt[:80]}...")

        # Generate 512x512
        generator = torch.Generator(device=device).manual_seed(42)
        image_512 = pipe(
            prompt=prompt,
            negative_prompt="blurry, smooth, gradients, antialiased, photography, realistic, 3d render",
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
            generator=generator,
        ).images[0]

        # Save 512x512
        output_512 = output_dir / f"{name}_512.png"
        image_512.save(output_512)

        # Downscale to 24x24
        image_24 = image_512.resize((24, 24), Image.NEAREST)
        output_24 = output_dir / f"{name}_24x24.png"
        image_24.save(output_24)

        # Count colors
        unique_colors = count_unique_colors(image_24)
        color_counts.append(unique_colors)

        print(f"  ✓ Generated! Unique colors: {unique_colors}")
        print()

        results['generations'].append({
            'name': name,
            'prompt': prompt,
            'unique_colors': unique_colors,
            'output_512': str(output_512),
            'output_24': str(output_24),
        })

    # Calculate statistics
    avg_colors = sum(color_counts) / len(color_counts)
    min_colors = min(color_counts)
    max_colors = max(color_counts)

    results['statistics'] = {
        'avg_unique_colors': avg_colors,
        'min_colors': min_colors,
        'max_colors': max_colors,
        'all_color_counts': color_counts,
    }

    print("-" * 100)
    print(f"EPOCH {epoch_num} SUMMARY:")
    print(f"  Average unique colors: {avg_colors:.1f}")
    print(f"  Range: {min_colors} - {max_colors}")
    print("-" * 100)
    print()

    # Save results JSON
    results_file = output_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Clean up
    del pipe
    torch.mps.empty_cache() if device == "mps" else None

    return results

# Main execution
if __name__ == "__main__":
    print("=" * 100)
    print("PHASE 1B COMPREHENSIVE TESTING")
    print("=" * 100)
    print()
    print("Testing all 8 epochs to find optimal checkpoint")
    print()
    print("Changes from CAPTION_FIX:")
    print("  - Simplified captions (removed micro-details like 'thin temples behind ears')")
    print("  - Still 512px resolution")
    print("  - Still SD 1.5")
    print()
    print("Goal: See if simplified captions improve quality vs CAPTION_FIX Epoch 8 (216.6 colors)")
    print("=" * 100)
    print()

    all_results = []

    for epoch in range(1, 9):
        try:
            result = test_epoch(epoch)
            all_results.append(result)
        except Exception as e:
            print(f"❌ Error testing epoch {epoch}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Final summary
    print("\n" + "=" * 100)
    print("PHASE 1B FINAL SUMMARY - ALL EPOCHS")
    print("=" * 100)
    print()
    print(f"{'Epoch':<10} {'Avg Colors':<15} {'Min':<10} {'Max':<10} {'Status':<20}")
    print("-" * 100)

    best_epoch = None
    best_avg = float('inf')

    for result in all_results:
        epoch = result['epoch']
        stats = result['statistics']
        avg = stats['avg_unique_colors']
        min_c = stats['min_colors']
        max_c = stats['max_colors']

        # Determine status
        if avg < 216.6:
            status = "✅ BETTER than CAPTION_FIX"
        elif avg < 230:
            status = "⚠️  Close to CAPTION_FIX"
        else:
            status = "❌ Worse than CAPTION_FIX"

        print(f"{epoch:<10} {avg:<15.1f} {min_c:<10} {max_c:<10} {status:<20}")

        if avg < best_avg:
            best_avg = avg
            best_epoch = epoch

    print("-" * 100)
    print()
    print(f"🏆 BEST EPOCH: {best_epoch} ({best_avg:.1f} avg colors)")
    print(f"📊 CAPTION_FIX Baseline: Epoch 8 (216.6 avg colors)")

    if best_avg < 216.6:
        improvement = ((216.6 - best_avg) / 216.6) * 100
        print(f"✅ Phase 1B is {improvement:.1f}% BETTER than CAPTION_FIX!")
    else:
        degradation = ((best_avg - 216.6) / 216.6) * 100
        print(f"❌ Phase 1B is {degradation:.1f}% WORSE than CAPTION_FIX")

    print()
    print("=" * 100)
    print()

    # Save final summary
    summary_file = OUTPUT_BASE_DIR / "PHASE1B_SUMMARY.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'all_results': all_results,
            'best_epoch': best_epoch,
            'best_avg_colors': best_avg,
            'baseline_caption_fix': 216.6,
        }, f, indent=2)

    print(f"✓ Full results saved to: {OUTPUT_BASE_DIR}/")
    print(f"✓ Summary saved to: {summary_file}")
    print()
