#!/usr/bin/env python3
"""
Test Bespoke Baby SD 1.5 LoRA - Epoch 3
"""
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path

print("=" * 60)
print("Testing Bespoke Baby SD 1.5 LoRA - Epoch 3")
print("=" * 60)

lora_path = "/Users/ilyssaevans/Downloads/bespoke_baby_sd15-000003.safetensors"
output_dir = Path("test_outputs_sd15_epoch3")
output_dir.mkdir(exist_ok=True)

print(f"\nLoRA: {lora_path}")
print(f"Output: {output_dir}/")

# Load model
print("\nLoading SD 1.5...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    safety_checker=None,
    requires_safety_checker=False
)

if torch.cuda.is_available():
    pipe = pipe.to("cuda")
elif torch.backends.mps.is_available():
    pipe = pipe.to("mps")

print("✓ Model loaded")

# Load LoRA
print(f"\nLoading LoRA...")
pipe.load_lora_weights(lora_path)
print("✓ LoRA loaded")

# Test with explicit pixel art prompts
test_prompts = [
    {
        "prompt": "pixel art portrait, bespoke punk, green solid background, blocky pixelated style, 24x24 pixel art",
        "negative": "realistic, photorealistic, smooth, blurry, 3d render, photograph, full body",
        "name": "01_pixel_punk"
    },
    {
        "prompt": "pixel art portrait, bespoke baby, pink solid background, blocky pixelated style, 24x24 pixel art",
        "negative": "realistic, photorealistic, smooth, blurry, 3d render, photograph, full body",
        "name": "02_pixel_baby"
    },
]

gen_params = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512,
}

print(f"\nGenerating {len(test_prompts)} images with EXPLICIT pixel art prompts...")
print("-" * 60)

for i, test in enumerate(test_prompts, 1):
    print(f"\n[{i}/{len(test_prompts)}] {test['name']}")

    try:
        image = pipe(
            prompt=test["prompt"],
            negative_prompt=test["negative"],
            **gen_params
        ).images[0]

        output_path = output_dir / f"{test['name']}.png"
        image.save(output_path)
        print(f"✓ Saved: {output_path}")

    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Epoch 3 Complete")
print("=" * 60)
