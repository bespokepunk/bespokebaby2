#!/usr/bin/env python3
"""Quick test of epoch 2 LoRA - generates a few test images."""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

# Configuration
MODEL_NAME = "runwayml/stable-diffusion-v1-5"
LORA_PATH = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/runpod_v2_7/bespoke_punks_v2_7-000002.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_epoch2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Quick test prompts
TEST_PROMPTS = [
    ("brown_eyes_test", "pixel art, 24x24, portrait of bespoke punk lady, brown eyes, light skin, blue background"),
    ("blue_eyes_test", "pixel art, 24x24, portrait of bespoke punk lad, blue eyes, tan skin, green background"),
    ("random_punk", "pixel art, 24x24, portrait of bespoke punk, random style"),
]

print("="*60)
print("QUICK EPOCH 2 TEST")
print("="*60)
print(f"Loading model: {MODEL_NAME}")
print(f"Loading LoRA: {os.path.basename(LORA_PATH)}")

# Load pipeline
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    safety_checker=None,
)
pipe.load_lora_weights(LORA_PATH)
pipe = pipe.to("mps")

print("\nGenerating test images...\n")

for name, prompt in TEST_PROMPTS:
    print(f"Testing: {name}")
    print(f"  Prompt: {prompt}")

    image = pipe(
        prompt=prompt,
        negative_prompt="blurry, smooth, gradients",
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
    print(f"  ✓ Saved: {small_path}")
    print()

print("="*60)
print("DONE!")
print("="*60)
print(f"\nCheck your images in: {OUTPUT_DIR}")
