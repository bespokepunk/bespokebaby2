#!/usr/bin/env python3
"""Quick test of FIXED epochs 5-8 (trained with wrong captions)."""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
BASE_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7_FIXED"

TEST_PROMPT = "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"

print("Testing FIXED Epochs 5-8 (trained with WRONG captions)")
print("="*70)

for epoch in [5, 6, 7, 8]:
    lora_path = f"{BASE_DIR}/bespoke_punks_v2_7_FIXED-{epoch:06d}.safetensors"

    if not os.path.exists(lora_path):
        print(f"Epoch {epoch}: FILE NOT FOUND")
        continue

    print(f"\nEpoch {epoch}: Loading...")

    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)
    pipe = pipe.to("mps")

    image = pipe(
        prompt=TEST_PROMPT,
        negative_prompt="blurry, smooth",
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    output_dir = f"/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_FIXED_epoch{epoch}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/brown_eyes_test_512.png"
    image.save(output_path)

    print(f"  ✓ Saved to {output_path}")

    del pipe
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

print("\n" + "="*70)
print("DONE! Check test_outputs_FIXED_epoch* folders")
print("\nNote: These used WRONG captions (my bad auto-fix)")
print("Brown eyes likely still won't work.")
