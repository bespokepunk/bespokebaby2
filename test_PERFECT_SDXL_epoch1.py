#!/usr/bin/env python3
"""
Test PERFECT SDXL Epoch 1
Trained with final perfect captions on RunPod!
"""

import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import os

# Paths
LORA_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_PERFECT-000001.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_PERFECT_SDXL_epoch1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test prompts using the final caption format
TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, tan skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("blue_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, blue eyes, light skin, red solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("green_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, black hair, green eyes, medium skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("afro_hair", "pixel art, 24x24, portrait of bespoke punk lady, large voluminous brown afro hair, brown eyes, dark skin, orange solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("sunglasses", "pixel art, 24x24, portrait of bespoke punk lad, blonde hair, wearing black stunner shades with white reflection, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("crown", "pixel art, 24x24, portrait of bespoke punk lady, red hair, wearing gold crown, blue eyes, light skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("hoodie", "pixel art, 24x24, portrait of bespoke punk lad, black hair, brown eyes, dark skin, wearing purple hoodie, gray solid background, sharp pixel edges, hard color borders, retro pixel art style"),
]

print("=" * 100)
print("TESTING PERFECT SDXL EPOCH 1 - FINAL CAPTIONS!")
print("=" * 100)
print(f"LoRA: {LORA_PATH}")
print(f"Output: {OUTPUT_DIR}")
print()
print("This was trained with:")
print("  ✓ Final perfect captions (strict template + full detail)")
print("  ✓ All hex colors verified")
print("  ✓ 10 epochs on RunPod")
print()
print("Testing epoch 1 first to see early learning...")
print("=" * 100)
print()

# Load SDXL pipeline
print("Loading SDXL pipeline...")
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
)

# Load LoRA
print(f"Loading LoRA from {LORA_PATH}...")
pipe.load_lora_weights(LORA_PATH)

# Move to GPU/MPS
if torch.backends.mps.is_available():
    print("Using MPS (Apple Silicon)")
    pipe = pipe.to("mps")
elif torch.cuda.is_available():
    print("Using CUDA")
    pipe = pipe.to("cuda")
else:
    print("Using CPU (will be slow)")

print("✓ Pipeline ready!")
print()

# Generate test images
for name, prompt in TEST_PROMPTS:
    print(f"Generating: {name}")
    print(f"  Prompt: {prompt[:80]}...")

    image = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth, gradients, antialiased, photography, realistic",
        num_inference_steps=30,
        guidance_scale=7.5,
        width=1024,
        height=1024,
    ).images[0]

    # Save 1024x1024
    output_path = os.path.join(OUTPUT_DIR, f"{name}_1024.png")
    image.save(output_path)

    # Save 24x24 (pixel art size)
    small = image.resize((24, 24), Image.NEAREST)
    small_path = os.path.join(OUTPUT_DIR, f"{name}_24.png")
    small.save(small_path)

    # Save 512x512 (medium size for review)
    medium = image.resize((512, 512), Image.LANCZOS)
    medium_path = os.path.join(OUTPUT_DIR, f"{name}_512.png")
    medium.save(medium_path)

    print(f"  ✓ Saved: {name}_[24/512/1024].png")
    print()

print("=" * 100)
print("✅ DONE!")
print("=" * 100)
print(f"\nResults in: {OUTPUT_DIR}")
print()
print("🎯 KEY TESTS:")
print("  1. Do brown eyes look brown?")
print("  2. Are traits appearing correctly (hair, accessories)?")
print("  3. Is pixel art style maintained?")
print("  4. Are backgrounds solid colors?")
print()
print("Next: If epoch 1 looks good, test higher epochs (5, 10) for comparison")
print()
