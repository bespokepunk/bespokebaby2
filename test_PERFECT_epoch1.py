#!/usr/bin/env python3
"""Test PERFECT epoch 1 - trained with pixel-verified captions!"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_PATH = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/PERFECT/bespoke_punks_PERFECT-000001.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_PERFECT_epoch1"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown eyes, tan skin, green background"),
    ("blue_eyes", "pixel art, 24x24, portrait of bespoke punk lady, blue eyes, light skin"),
    ("cyan_eyes", "pixel art, 24x24, portrait of bespoke punk lad, cyan eyes, dark skin"),
    ("green_eyes", "pixel art, 24x24, portrait of bespoke punk lady, green eyes, tan skin"),
    ("red_eyes", "pixel art, 24x24, portrait of bespoke punk lad, red eyes, light skin"),
]

print("="*80)
print("TESTING PERFECT EPOCH 1 - PIXEL-VERIFIED CAPTIONS!")
print("="*80)
print("This was trained with 100% accurate captions")
print("Brown eyes should FINALLY work correctly!")
print("="*80)
print()

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None,
)
pipe.load_lora_weights(LORA_PATH)
pipe = pipe.to("mps")

for name, prompt in TEST_PROMPTS:
    print(f"Generating: {name}")
    print(f"  Prompt: {prompt}")

    image = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth, gradients",
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    output_path = os.path.join(OUTPUT_DIR, f"{name}_512.png")
    image.save(output_path)

    # Also save 24x24
    small = image.resize((24, 24), Image.NEAREST)
    small_path = os.path.join(OUTPUT_DIR, f"{name}_24.png")
    small.save(small_path)

    print(f"  ✓ Saved: {output_path}")
    print()

print("="*80)
print("DONE!")
print("="*80)
print(f"\nResults in: {OUTPUT_DIR}")
print("\n🎯 KEY TEST: Do the brown eyes ACTUALLY look brown this time?")
