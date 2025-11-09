#!/usr/bin/env python3
"""Test PERFECT epochs 2 and 3."""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
BASE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/PERFECT"

TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown eyes, tan skin, green background"),
    ("blue_eyes", "pixel art, 24x24, portrait of bespoke punk lady, blue eyes, light skin"),
    ("cyan_eyes", "pixel art, 24x24, portrait of bespoke punk lad, cyan eyes, dark skin"),
    ("green_eyes", "pixel art, 24x24, portrait of bespoke punk lady, green eyes, tan skin"),
]

print("="*70)
print("Testing PERFECT Epochs 2 & 3")
print("="*70)

for epoch in [2, 3]:
    print(f"\n{'='*70}")
    print(f"EPOCH {epoch}")
    print(f"{'='*70}")

    lora_path = f"{BASE_DIR}/bespoke_punks_PERFECT-{epoch:06d}.safetensors"

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)
    pipe = pipe.to("mps")

    output_dir = f"/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_PERFECT_epoch{epoch}"
    os.makedirs(output_dir, exist_ok=True)

    for name, prompt in TEST_PROMPTS:
        print(f"  Generating: {name}")

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
        print(f"    ✓ {output_path}")

    del pipe
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

print("\n" + "="*70)
print("DONE!")
print("="*70)
