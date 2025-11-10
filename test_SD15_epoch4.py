#!/usr/bin/env python3
"""
Test SD 1.5 PERFECT Epoch 4
Quick test of epoch 4
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000004.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_SD15_epoch4"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test prompts based on actual final captions
TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("golden_earrings", "pixel art, 24x24, portrait of bespoke punk lady, black hair, wearing golden earrings, brown eyes, light skin, gray solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("bow_in_hair", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, wearing red bow in hair, blue eyes, light skin, pink solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("sunglasses_lad", "pixel art, 24x24, portrait of bespoke punk lad, blonde hair, wearing black stunner shades with white reflection, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("afro_hair", "pixel art, 24x24, portrait of bespoke punk lady, large voluminous brown afro hair, brown eyes, dark skin, orange solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("necklace", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, wearing silver necklace with pendant, blue eyes, light skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("crown", "pixel art, 24x24, portrait of bespoke punk lady, red hair, wearing gold crown, green eyes, light skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),
]

print("=" * 100)
print("TESTING SD 1.5 PERFECT - EPOCH 4")
print("=" * 100)
print(f"LoRA: {LORA_PATH}")
print(f"Output: {OUTPUT_DIR}")
print()
print("=" * 100)
print()

# Load pipeline
print("Loading SD 1.5 with epoch 4 LoRA...")
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None,
)
pipe.load_lora_weights(LORA_PATH)

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

# Generate test images
for name, prompt in TEST_PROMPTS:
    print(f"Generating: {name}")

    image = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth, gradients, antialiased, photography, realistic, 3d render",
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    # Save 512x512
    output_512 = os.path.join(OUTPUT_DIR, f"{name}_512.png")
    image.save(output_512)

    # Save 24x24 (pixel art size)
    small = image.resize((24, 24), Image.NEAREST)
    output_24 = os.path.join(OUTPUT_DIR, f"{name}_24.png")
    small.save(output_24)

    print(f"  ✓ Saved: {name}_[24/512].png\n")

print("=" * 100)
print("✅ EPOCH 4 COMPLETE!")
print("=" * 100)
print(f"\nResults in: {OUTPUT_DIR}/")
print()
print("🎯 KEY TESTS:")
print("  1. Brown eyes - do they look brown?")
print("  2. Golden earrings - are they visible?")
print("  3. Bow in hair - is it there?")
print("  4. Necklace - visible?")
print("  5. Pixel art style - simple & blocky?")
print()
