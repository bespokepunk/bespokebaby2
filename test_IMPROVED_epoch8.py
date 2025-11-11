#!/usr/bin/env python3
"""Test IMPROVED model Epoch 8 - 80% complete"""

import torch
from diffusers import StableDiffusionPipeline
import os

MODEL_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_IMPROVED-000008.safetensors"
BASE_MODEL = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = "test_outputs/IMPROVED_epoch8"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("TESTING: IMPROVED Model - Epoch 8 (80% trained)")
print("=" * 80)

pipe = StableDiffusionPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    safety_checker=None
).to("mps")

pipe.load_lora_weights(MODEL_PATH)
print("✓ Model loaded\n")

test_prompts = [
    {"name": "expression_smile", "prompt": "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, mouth corners turned up in gentle slight smile, green background"},
    {"name": "expression_neutral", "prompt": "pixel art, 24x24, portrait of bespoke punk lad, brown hair, mouth in straight neutral line with relaxed expression, blue background"},
    {"name": "hair_curly_detailed", "prompt": "pixel art, 24x24, portrait of bespoke punk lady, tightly coiled curly textured hair with high volume, slight smile, green background"},
    {"name": "hair_straight_detailed", "prompt": "pixel art, 24x24, portrait of bespoke punk lad, sleek straight hair hanging smoothly down, slight smile, purple background"},
    {"name": "hair_braids_detailed", "prompt": "pixel art, 24x24, portrait of bespoke punk lady, hair in two distinct braids with visible woven pattern, neutral expression, green background"},
    {"name": "combined_curly_smile", "prompt": "pixel art, 24x24, portrait of bespoke punk lady, tightly coiled curly textured hair with high volume, mouth corners turned up in gentle slight smile, green background"},
    {"name": "baseline_simple_smile", "prompt": "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, slight smile, green background"},
    {"name": "baseline_simple_curly", "prompt": "pixel art, 24x24, portrait of bespoke punk lady, curly hair, slight smile, purple background"},
]

for i, test in enumerate(test_prompts, 1):
    print(f"\n[{i}/{len(test_prompts)}] {test['name']}")
    image = pipe(test['prompt'], num_inference_steps=30, guidance_scale=7.5, height=512, width=512).images[0]
    output_path = f"{OUTPUT_DIR}/{i:02d}_{test['name']}.png"
    image.save(output_path)
    print(f"✓ Saved: {output_path}")

print("\n" + "=" * 80)
print("EPOCH 8 COMPLETE")
