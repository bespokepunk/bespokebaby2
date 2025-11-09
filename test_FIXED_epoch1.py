#!/usr/bin/env python3
"""Test FIXED epoch 1 - with corrected captions. Brown eyes should finally work!"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_PATH = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7_FIXED/bespoke_punks_v2_7_FIXED-000001.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_FIXED_epoch1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test prompts - focusing on the brown eyes fix
TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown eyes, tan skin, green background"),
    ("blue_eyes_test", "pixel art, 24x24, portrait of bespoke punk lad, blue eyes, light skin, orange background"),
    ("cyan_eyes_test", "pixel art, 24x24, portrait of bespoke punk lady, cyan eyes, tan skin, purple background"),
    ("green_eyes_test", "pixel art, 24x24, portrait of bespoke punk lady, green eyes, dark skin, pink background"),
    ("random_punk", "pixel art, 24x24, portrait of bespoke punk, random style"),
]

print("="*80)
print("TESTING FIXED EPOCH 1 - WITH CORRECTED CAPTIONS")
print("="*80)
print("This training used ACCURATE color labels.")
print("Brown eyes should now generate as BROWN (not cyan)!")
print("="*80)
print()

# Load pipeline
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None,
)
pipe.load_lora_weights(LORA_PATH)
pipe = pipe.to("mps")

print("Generating test images...\n")

for name, prompt in TEST_PROMPTS:
    print(f"Testing: {name}")
    print(f"  Prompt: {prompt}")

    image = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth, gradients, soft edges",
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    # Save full size
    output_path = os.path.join(OUTPUT_DIR, f"{name}_512.png")
    image.save(output_path)
    print(f"  ✓ Saved: {output_path}")

    # Save downscaled to 24x24
    small = image.resize((24, 24), Image.NEAREST)
    small_path = os.path.join(OUTPUT_DIR, f"{name}_24.png")
    small.save(small_path)
    print(f"  ✓ Saved 24x24: {small_path}")
    print()

print("="*80)
print("DONE!")
print("="*80)
print(f"\nCheck results in: {OUTPUT_DIR}")
print("\nKEY TEST: Look at brown_eyes_* images")
print("Are the eyes actually BROWN now? (Not cyan/blue)")
print("\nIf yes: The caption fix worked! 🎉")
print("If no: May need more epochs or training adjustment")
