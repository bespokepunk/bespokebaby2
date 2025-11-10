#!/usr/bin/env python3
"""
Test Bespoke Baby SDXL LoRA - Epoch 1
First epoch from SDXL training (should produce pixel art unlike SD 1.5)
"""
import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path

print("=" * 60)
print("Testing SDXL Epoch 1 - Pixel Art LoRA")
print("=" * 60)
print()

# Test prompts - same as SD 1.5 for comparison
test_prompts = [
    {
        "prompt": "portrait of bespoke punk, green solid background, black hair, blue eyes, light skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render",
        "name": "01_bespoke_punk_green_bg"
    },
    {
        "prompt": "portrait of bespoke baby, pink solid background, brown hair, brown eyes, medium skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render",
        "name": "02_bespoke_baby_pink_bg"
    },
    {
        "prompt": "portrait of bespoke punk lad, blue solid background, blonde hair, green eyes, tan skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render",
        "name": "03_lad_blue_bg"
    },
    {
        "prompt": "portrait of bespoke punk lady, purple solid background, red hair, hazel eyes, pale skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render",
        "name": "04_lady_purple_bg"
    },
]

# SDXL generation parameters (reduced for MPS memory constraints)
gen_params = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 512,  # Reduced from 1024 for memory
    "height": 512,
}

# LoRA path
lora_path = "/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000001.safetensors"
output_dir = Path("test_outputs_sdxl_epoch1")
output_dir.mkdir(exist_ok=True)

print(f"Loading SDXL base model...")
print()

# Load SDXL base model
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    use_safetensors=True,
    variant="fp16" if torch.cuda.is_available() else None
)

# Move to appropriate device
if torch.cuda.is_available():
    pipe = pipe.to("cuda")
    print("✓ Using CUDA")
elif torch.backends.mps.is_available():
    pipe = pipe.to("mps")
    print("✓ Using MPS (Apple Silicon)")
    # Enable memory optimizations for MPS
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    print("  Memory optimizations enabled (attention + VAE slicing)")
else:
    print("✓ Using CPU (slow)")

print()

# Load LoRA
print(f"Loading LoRA: {lora_path}")
try:
    pipe.load_lora_weights(lora_path)
    print("✓ LoRA loaded successfully")
except Exception as e:
    print(f"✗ Error loading LoRA: {e}")
    exit(1)

print()
print("=" * 60)
print("Generating Test Images")
print("=" * 60)
print()

# Generate images
for i, test in enumerate(test_prompts, 1):
    print(f"[{i}/{len(test_prompts)}] {test['name']}")
    print(f"  Prompt: {test['prompt'][:60]}...")

    try:
        image = pipe(
            prompt=test["prompt"],
            negative_prompt=test["negative"],
            **gen_params
        ).images[0]

        output_path = output_dir / f"{test['name']}.png"
        image.save(output_path)
        print(f"  ✓ Saved to {output_path}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    print()

print("=" * 60)
print("SDXL Epoch 1 Testing Complete!")
print("=" * 60)
print()
print(f"Output directory: {output_dir}/")
print()
print("Compare these with SD 1.5 results:")
print("  - SD 1.5: test_outputs_sd15_epoch1/ (realistic babies)")
print("  - SDXL:   test_outputs_sdxl_epoch1/ (should be pixel art)")
