#!/usr/bin/env python3
"""Quick test of epoch 3 LoRA."""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_PATH = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7/bespoke_punks_v2_7-000003.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_epoch3"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEST_PROMPTS = [
    ("brown_eyes_test", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("blue_eyes_test", "pixel art, 24x24, portrait of bespoke punk lad, blue eyes, tan skin, green background"),
]

print("EPOCH 3 TEST")
print("="*60)

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None,
)
pipe.load_lora_weights(LORA_PATH)
pipe = pipe.to("mps")

for name, prompt in TEST_PROMPTS:
    print(f"Testing: {name}")
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
    print(f"  ✓ Saved: {output_path}")

print("\nDONE! Check: " + OUTPUT_DIR)
