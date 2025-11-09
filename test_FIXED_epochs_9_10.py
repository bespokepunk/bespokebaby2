#!/usr/bin/env python3
"""Test FIXED epochs 9 and 10 - final epochs from wrong caption training."""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
BASE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7_FIXED"

TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown eyes, tan skin, green background"),
    ("cyan_eyes", "pixel art, 24x24, portrait of bespoke punk lady, cyan eyes, dark skin"),
    ("green_eyes", "pixel art, 24x24, portrait of bespoke punk lad, green eyes"),
]

print("="*70)
print("Testing FIXED Epochs 9 & 10 (trained with WRONG captions)")
print("="*70)

for epoch in [9, 10]:
    print(f"\n{'='*70}")
    print(f"EPOCH {epoch}")
    print(f"{'='*70}")

    lora_path = f"{BASE_DIR}/bespoke_punks_v2_7_FIXED-{epoch:06d}.safetensors"

    if not os.path.exists(lora_path):
        print(f"FILE NOT FOUND: {lora_path}")
        continue

    print(f"Loading...")

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)
    pipe = pipe.to("mps")

    output_dir = f"/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_FIXED_epoch{epoch}"
    os.makedirs(output_dir, exist_ok=True)

    for name, prompt in TEST_PROMPTS:
        print(f"  Generating: {name}")

        image = pipe(
            prompt=prompt,
            negative_prompt="blurry, smooth, gradients",
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
        ).images[0]

        output_path = f"{output_dir}/{name}_512.png"
        image.save(output_path)
        print(f"    ✓ Saved: {output_path}")

    del pipe
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
print("\nNote: These used WRONG captions (my auto-fix mistake)")
print("Brown eyes likely still won't work - need PERFECT captions training")
