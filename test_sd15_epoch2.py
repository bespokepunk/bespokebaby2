#!/usr/bin/env python3
"""
Test Bespoke Baby SD 1.5 LoRA - Epoch 2
"""
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path

print("=" * 60)
print("Testing Bespoke Baby SD 1.5 LoRA - Epoch 2")
print("=" * 60)

# Setup
lora_path = "/Users/ilyssaevans/Downloads/bespoke_baby_sd15-000002.safetensors"
output_dir = Path("test_outputs_sd15_epoch2")
output_dir.mkdir(exist_ok=True)

print(f"\nLoRA: {lora_path}")
print(f"Output: {output_dir}/")

# Load base SD 1.5 model
print("\nLoading SD 1.5 base model...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    safety_checker=None,
    requires_safety_checker=False
)

# Move to device
if torch.cuda.is_available():
    pipe = pipe.to("cuda")
elif torch.backends.mps.is_available():
    pipe = pipe.to("mps")

print("✓ Model loaded")

# Load LoRA
print(f"\nLoading LoRA from {lora_path}...")
pipe.load_lora_weights(lora_path)
print("✓ LoRA loaded")

# Same test prompts
test_prompts = [
    {
        "prompt": "portrait of bespoke punk, green solid background, black hair, blue eyes, light skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "01_bespoke_punk_green_bg"
    },
    {
        "prompt": "portrait of bespoke baby, pink solid background, brown hair, brown eyes, medium skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "02_bespoke_baby_pink_bg"
    },
    {
        "prompt": "portrait of bespoke punk lad, blue solid background, blonde hair, green eyes, tan skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "03_lad_blue_bg"
    },
    {
        "prompt": "portrait of bespoke punk lady, purple solid background, red hair, hazel eyes, pale skin",
        "negative": "full body, legs, multiple people, text, watermark",
        "name": "04_lady_purple_bg"
    },
]

gen_params = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512,
}

print(f"\nGenerating {len(test_prompts)} test images...")
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
print("Epoch 2 Testing Complete!")
print("=" * 60)
print(f"\nCompare epoch 1 vs epoch 2 outputs")
