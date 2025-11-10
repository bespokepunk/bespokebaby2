#!/usr/bin/env python3
"""
Compare SD15_FINAL_CORRECTED_CAPTIONS Training vs SD15_PERFECT (Production)

This script tests new epochs from the current training run against the proven
production model (SD15_PERFECT Epoch 7) to see if detailed captions improve quality.

Usage:
  1. Download epoch checkpoints to /Users/ilyssaevans/Downloads/
  2. Update EPOCH_PATHS dict below with actual filenames
  3. Run: python test_SD15_FINAL_CORRECTED_vs_PERFECT.py
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = f"/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_FINAL_CORRECTED_vs_PERFECT_{TIMESTAMP}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Production baseline (SD15_PERFECT Epoch 7 - 9/10 quality)
BASELINE_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000007.safetensors"

# New training run epochs (update filenames as you download them)
# Example: bespoke_baby_sd15_lora-000001.safetensors
EPOCH_PATHS = {
    "epoch1": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000001 (1).safetensors",  # Epoch 1 ready!
    # Add more epochs as they finish training
    # "epoch2": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000002.safetensors",
    # "epoch3": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000003.safetensors",
}

# Test prompts - using NEW FINAL CORRECTED caption format
# These have 12+ hex codes, lips, expressions, all details
TEST_PROMPTS = [
    ("lady_pink_hair_crown",
     "pixel art, 24x24, portrait of bespoke punk lady, pink hair (#ff66cc), crown, hoop earrings, eyes (#663300), lips (#cc6666), neutral expression, skin (#f0c090), solid green background (#00ff00)"),

    ("lad_purple_hair_cap",
     "pixel art, 24x24, portrait of bespoke punk lad, purple hair (#9966ff), purple cap, eyes (#663300), lips (#cc9999), neutral expression, skin (#f0c090), solid blue background (#0066ff)"),

    ("lady_brown_afro",
     "pixel art, 24x24, portrait of bespoke punk lady, brown afro hair (#663300), hoop earrings, eyes (#663300), lips (#cc6666), slight smile, skin (#d0a070), solid orange background (#ff9900)"),

    ("lad_blonde_sunglasses",
     "pixel art, 24x24, portrait of bespoke punk lad, blonde hair (#ffcc66), black stunner shades with white reflection, lips (#cc9999), neutral expression, skin (#f0c090), solid blue background (#0066ff)"),

    ("lady_red_hair_bow",
     "pixel art, 24x24, portrait of bespoke punk lady, red hair (#ff3333), red bow in hair, stud earrings, eyes (#3399ff), lips (#ff6666), slight smile, skin (#ffccaa), solid pink background (#ff99cc)"),

    ("lad_green_hair_headband",
     "pixel art, 24x24, portrait of bespoke punk lad, green hair (#33cc33), green headband, eyes (#663300), lips (#cc9999), neutral expression, skin (#f0c090), solid yellow background (#ffcc00)"),
]

# ==============================================================================
# TESTING FUNCTION
# ==============================================================================

def test_lora(name, lora_path, output_subdir):
    """Test a LoRA model with all test prompts"""

    if not os.path.exists(lora_path):
        print(f"  ⚠️  File not found: {lora_path}")
        print(f"  ⏭️  Skipping {name}")
        return False

    print(f"\n{'=' * 100}")
    print(f"TESTING: {name}")
    print(f"LoRA: {lora_path}")
    print(f"File size: {os.path.getsize(lora_path) / (1024*1024):.1f}MB")
    print(f"{'=' * 100}\n")

    # Create output directory
    epoch_dir = os.path.join(OUTPUT_DIR, output_subdir)
    os.makedirs(epoch_dir, exist_ok=True)

    # Load pipeline
    print(f"Loading SD 1.5 with {name} LoRA...")
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)

    # Move to device
    if torch.backends.mps.is_available():
        pipe = pipe.to("mps")
        device = "MPS (Apple Silicon)"
    elif torch.cuda.is_available():
        pipe = pipe.to("cuda")
        device = "CUDA (NVIDIA GPU)"
    else:
        device = "CPU (Warning: very slow!)"

    print(f"✓ Pipeline ready on {device}\n")

    # Generate test images
    for prompt_name, prompt in TEST_PROMPTS:
        print(f"  Generating: {prompt_name}...")

        try:
            image = pipe(
                prompt=prompt,
                negative_prompt="blurry, smooth, gradients, antialiased, photography, realistic, 3d render, full body, character sprite",
                num_inference_steps=30,
                guidance_scale=7.5,
                width=512,
                height=512,
                generator=torch.Generator().manual_seed(42),  # Fixed seed for consistency
            ).images[0]

            # Save 512x512
            output_path = os.path.join(epoch_dir, f"{prompt_name}_512.png")
            image.save(output_path)
            print(f"    ✓ Saved: {output_path}")

            # Also save 24x24 downscaled version
            image_24 = image.resize((24, 24), Image.Resampling.NEAREST)
            output_path_24 = os.path.join(epoch_dir, f"{prompt_name}_24.png")
            image_24.save(output_path_24)

        except Exception as e:
            print(f"    ❌ Error: {e}")

    print(f"\n✓ {name} testing complete!")
    print(f"  Output: {epoch_dir}")

    # Cleanup
    del pipe
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    elif torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return True

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("SD15_FINAL_CORRECTED_CAPTIONS vs SD15_PERFECT Comparison Test")
    print("=" * 100)
    print(f"\nOutput Directory: {OUTPUT_DIR}")
    print(f"Baseline: SD15_PERFECT Epoch 7 (9/10 production model)")
    print(f"Test Subjects: SD15_FINAL_CORRECTED epochs")
    print(f"\nCaption Format: FINAL CORRECTED (12+ hex codes, lips, expressions)")
    print("\n" + "=" * 100)

    # Test baseline first
    print("\n📊 BASELINE TEST")
    baseline_success = test_lora(
        "SD15_PERFECT Epoch 7 (BASELINE - 9/10)",
        BASELINE_PATH,
        "baseline_PERFECT_epoch7"
    )

    if not baseline_success:
        print("\n❌ ERROR: Baseline model not found!")
        print(f"   Expected: {BASELINE_PATH}")
        print("\n   Cannot proceed without baseline for comparison.")
        exit(1)

    # Test new epochs
    print("\n\n📊 NEW TRAINING RUN TESTS")
    tested_count = 0
    skipped_count = 0

    for epoch_name, epoch_path in EPOCH_PATHS.items():
        success = test_lora(
            f"SD15_FINAL_CORRECTED {epoch_name.upper()}",
            epoch_path,
            f"new_training_{epoch_name}"
        )
        if success:
            tested_count += 1
        else:
            skipped_count += 1

    # Summary
    print("\n\n" + "=" * 100)
    print("TESTING COMPLETE")
    print("=" * 100)
    print(f"\nBaseline: 1 model tested")
    print(f"New Training: {tested_count} epochs tested, {skipped_count} skipped")
    print(f"\nAll results saved to: {OUTPUT_DIR}")
    print("\n📋 NEXT STEPS:")
    print("  1. Review images in the output directory")
    print("  2. Compare new epochs vs baseline (PERFECT Epoch 7)")
    print("  3. Score each epoch on visual quality, style match, prompt adherence (0-10)")
    print("  4. Update Supabase epoch_results table with findings")
    print("  5. Determine if detailed captions improved quality vs PERFECT's simpler captions")
    print("\n" + "=" * 100 + "\n")
