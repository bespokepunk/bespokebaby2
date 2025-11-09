#!/usr/bin/env python3
"""
Quick test of V2.0 models vs V1.0 winner
"""

import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path

# Models to test
MODELS = {
    "V1.0 Epoch 2 (Winner)": "models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000002.safetensors",
    "V2.0 Epoch 1": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000001.safetensors",
    "V2.0 Epoch 2": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000002.safetensors",
    "V2.0 Epoch 3": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2.safetensors",
}

# Coordinate test prompt (the one that won in v1.0)
COORDINATE_TEST = {
    "prompt": "bespoke, 24x24 pixel art portrait, symbolic punk style, vibrant orange solid background, black hair starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12), brown iris eyes at (9,12) and (14,12), black nose dot at (11,13), pink lips spanning x=10-13 y=15-16, tan skin tone with jaw defined at y=19, blue collar at bottom edge y=20-22, right-facing, pure pixel art with no gradients or anti-aliasing",
    "negative": "blurry, low quality, 3d, photorealistic, smooth, anti-aliasing"
}

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
OUTPUT_DIR = Path("test_outputs_v2_comparison")
OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

print("🎨 V2.0 vs V1.0 Comparison Test")
print("=" * 80)
print(f"Device: {DEVICE}")
print(f"Testing: Coordinate accuracy prompt")
print("=" * 80)

# Load base model once
print(f"\n📦 Loading base model: {BASE_MODEL}")
pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
    variant="fp16" if DEVICE != "cpu" else None,
)
pipe = pipe.to(DEVICE)

for name, lora_path in MODELS.items():
    print(f"\n🧪 Testing: {name}")
    print(f"   LoRA: {lora_path}")

    # Load LoRA
    pipe.unload_lora_weights()
    pipe.load_lora_weights(lora_path)

    # Generate
    output_path = OUTPUT_DIR / f"{name.replace(' ', '_').replace('.', '_')}_coordinate.png"

    image = pipe(
        prompt=COORDINATE_TEST["prompt"],
        negative_prompt=COORDINATE_TEST["negative"],
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    image.save(output_path)
    print(f"   ✅ Saved: {output_path}")

print("\n" + "=" * 80)
print("✅ Testing Complete!")
print(f"📁 Results: {OUTPUT_DIR}/")
print("\nCompare the images to see if V2.0 improved coordinate accuracy!")
print("=" * 80)
