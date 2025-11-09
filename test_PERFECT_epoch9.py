#!/usr/bin/env python3
"""Test PERFECT epoch 9."""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
BASE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/PERFECT"

TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown eyes, tan skin, green background"),
]

print("="*70)
print("Testing PERFECT Epoch 9")
print("="*70)

lora_path = f"{BASE_DIR}/bespoke_punks_PERFECT-000009.safetensors"

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None,
)
pipe.load_lora_weights(lora_path)
pipe = pipe.to("mps")

output_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_PERFECT_epoch9"
os.makedirs(output_dir, exist_ok=True)

for name, prompt in TEST_PROMPTS:
    print(f"Generating: {name}")

    image = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth",
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    output_path = f"{output_dir}/{name}_512.png"
    image.save(output_path)
    print(f"  ✓ Saved: {output_path}")

print("\nDONE!")
