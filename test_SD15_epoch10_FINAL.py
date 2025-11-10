#!/usr/bin/env python3
"""
Test SD 1.5 PERFECT Epoch 10 - FINAL
Complete captions with all jewelry & accessories
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_SD15_epoch10_FINAL"
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
print("TESTING SD 1.5 PERFECT - EPOCH 10 FINAL")
print("=" * 100)
print(f"LoRA: {LORA_PATH}")
print(f"Output: {OUTPUT_DIR}")
print()
print("This is the FINAL epoch - may show overtraining!")
print("Compare with epochs 5-7 to find the best balance.")
print()
print("=" * 100)
print()

# Load pipeline
print("Loading SD 1.5 with epoch 10 FINAL LoRA...")
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
print("✅ EPOCH 10 FINAL COMPLETE!")
print("=" * 100)
print(f"\nResults in: {OUTPUT_DIR}/")
print()
print("🎯 NEXT STEPS:")
print("  1. Compare ALL epochs (1-10)")
print("  2. Look for the best balance of:")
print("     - Accurate traits (brown eyes, earrings, etc.)")
print("     - Simple bespoke punk style (not too detailed)")
print("     - Clean pixel art aesthetic")
print()
print("  3. Typical best epochs: 5, 6, or 7")
print("  4. Epochs 8-10 may be overtrained (too much detail/artifacts)")
print()
