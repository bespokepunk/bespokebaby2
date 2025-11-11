#!/usr/bin/env python3
"""
Generate Sample Images from Best CAPTION_FIX Checkpoints
Epochs 5 and 8 - Production Quality Assessment
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/production_samples_CAPTION_FIX"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Best checkpoints identified from testing
BEST_LORAS = {
    "epoch5_best_bg": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora_keep_tokens_3-000005 (1).safetensors",
    "epoch8_best_avg": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora_keep_tokens_3-000008 (1).safetensors",
    "epoch9_visual_check": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora_keep_tokens_3-000009 (1).safetensors",
}

# Diverse test prompts to evaluate production quality
TEST_PROMPTS = [
    ("green_bg_verification", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium male skin tone, bright green background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lady_brown_eyes", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lad_sunglasses", "pixel art, 24x24, portrait of bespoke punk lad, blonde hair, wearing black stunner shades with white reflection, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lady_gold_earrings", "pixel art, 24x24, portrait of bespoke punk lady, black hair, wearing golden earrings, brown eyes, light skin, gray solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lady_red_hair", "pixel art, 24x24, portrait of bespoke punk lady, vibrant red hair, green eyes, light skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lad_afro", "pixel art, 24x24, portrait of bespoke punk lad, large voluminous brown afro hair, brown eyes, dark skin, orange solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lady_blonde_bow", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, wearing red bow in hair, blue eyes, light skin, pink solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("lad_green_hair", "pixel art, 24x24, portrait of bespoke punk lad, bright green hair, dark eyes, medium skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),
]

print("=" * 100)
print("GENERATING PRODUCTION SAMPLES - CAPTION_FIX BEST CHECKPOINTS")
print("=" * 100)
print(f"Output: {OUTPUT_DIR}")
print()
print("Best Checkpoints:")
print("  - Epoch 5: Best green background (156 colors)")
print("  - Epoch 8: Best overall average (216.6 colors)")
print("  - Epoch 9: Visual quality check (user noted better coloring)")
print()
print("=" * 100)
print()

for checkpoint_name, lora_path in BEST_LORAS.items():
    print(f"\n{'=' * 100}")
    print(f"GENERATING: {checkpoint_name.upper()}")
    print(f"{'=' * 100}\n")

    # Create checkpoint folder
    checkpoint_dir = os.path.join(OUTPUT_DIR, checkpoint_name)
    os.makedirs(checkpoint_dir, exist_ok=True)

    # Load pipeline
    print(f"Loading SD 1.5 with {checkpoint_name} LoRA...")
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)

    # Move to GPU/MPS
    if torch.backends.mps.is_available():
        pipe = pipe.to("mps")
        device = "MPS"
    elif torch.cuda.is_available():
        pipe = pipe.to("cuda")
        device = "CUDA"
    else:
        device = "CPU"

    print(f"✓ Pipeline ready on {device}\n")

    # Generate samples
    for name, prompt in TEST_PROMPTS:
        print(f"  Generating: {name}")

        image = pipe(
            prompt=prompt,
            negative_prompt="blurry, smooth, gradients, antialiased, photography, realistic, 3d render",
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
        ).images[0]

        # Save 512x512
        output_512 = os.path.join(checkpoint_dir, f"{name}_512.png")
        image.save(output_512)

        # Save 24x24 (pixel art size)
        small = image.resize((24, 24), Image.NEAREST)
        output_24 = os.path.join(checkpoint_dir, f"{name}_24.png")
        small.save(output_24)

        print(f"    ✓ Saved: {name}_[24/512].png")

    print(f"\n✓ {checkpoint_name.upper()} samples complete!\n")

    # Clean up
    del pipe
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

print("=" * 100)
print("✅ PRODUCTION SAMPLES GENERATED!")
print("=" * 100)
print(f"\nSamples saved to: {OUTPUT_DIR}/")
print()
print("Folders:")
print(f"  - {OUTPUT_DIR}/epoch5_best_bg/")
print(f"  - {OUTPUT_DIR}/epoch8_best_avg/")
print(f"  - {OUTPUT_DIR}/epoch9_visual_check/")
print()
print("🎯 USE THESE FOR:")
print("  1. Visual quality assessment")
print("  2. Color accuracy verification")
print("  3. Production deployment decision")
print("  4. Comparison with previous experiments")
print()
