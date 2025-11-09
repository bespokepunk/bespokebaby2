#!/usr/bin/env python3
"""
Generate ACTUAL 24x24 Bespoke Punks and compare against real training images
"""

import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path
from PIL import Image
import numpy as np

# Test with simple prompts that match training data
TEST_PROMPTS = [
    {
        "name": "simple_green",
        "prompt": "bespoke, 24x24 pixel art portrait, bright green solid background, black hair, blue eyes, white/pale skin",
        "negative": "blurry, low quality, 3d, photorealistic, smooth, anti-aliasing"
    },
    {
        "name": "purple_sunglasses",
        "prompt": "bespoke, 24x24 pixel art portrait, purple/lavender solid background, long black hair, covered by purple sunglasses, light/peach skin, pink lips",
        "negative": "blurry, low quality, 3d, photorealistic, smooth, anti-aliasing"
    },
]

MODELS = {
    "V1_Epoch2": "models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000002.safetensors",
    "V2_Epoch3": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2.safetensors",
}

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
OUTPUT_DIR = Path("true_24x24_validation")
OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

print("🎯 TRUE 24x24 BESPOKE PUNK VALIDATION")
print("=" * 80)
print(f"Device: {DEVICE}")
print("Generating ACTUAL 24x24 images (not upscaled)")
print("=" * 80)

# Load base model
print(f"\n📦 Loading base model: {BASE_MODEL}")
pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
    variant="fp16" if DEVICE != "cpu" else None,
)
pipe = pipe.to(DEVICE)

# Also load some real training images for comparison
print("\n📸 Loading real Bespoke Punks for comparison...")
real_punks = []
training_dir = Path("FORTRAINING6/bespokepunks")
for img_path in list(training_dir.glob("*.png"))[:5]:
    if "ALL" not in img_path.name:
        img = Image.open(img_path)
        real_punks.append({
            "name": img_path.stem,
            "image": img,
            "size": img.size
        })
        print(f"  Real punk: {img_path.name} - Size: {img.size}")

for model_name, lora_path in MODELS.items():
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {model_name}")
    print(f"{'='*80}")

    # Load LoRA
    pipe.unload_lora_weights()
    pipe.load_lora_weights(lora_path)

    model_dir = OUTPUT_DIR / model_name
    model_dir.mkdir(exist_ok=True)

    for test in TEST_PROMPTS:
        print(f"\n  → {test['name']}")

        # Generate at 512x512 first (SDXL requirement)
        print(f"     Generating 512x512...")
        image_512 = pipe(
            prompt=test["prompt"],
            negative_prompt=test["negative"],
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
        ).images[0]

        # Downsample to 24x24 using NEAREST (no anti-aliasing)
        print(f"     Downsampling to 24x24 (NEAREST)...")
        image_24 = image_512.resize((24, 24), Image.NEAREST)

        # Save both versions
        output_512 = model_dir / f"{test['name']}_512.png"
        output_24 = model_dir / f"{test['name']}_24.png"

        image_512.save(output_512)
        image_24.save(output_24)

        # Analyze 24x24 version
        arr = np.array(image_24)
        unique_colors = len(np.unique(arr.reshape(-1, arr.shape[2]), axis=0))

        print(f"     ✅ 512x512: {output_512}")
        print(f"     ✅  24x24: {output_24}")
        print(f"     📊 Unique colors: {unique_colors}")
        print(f"     📐 Shape: {arr.shape}")

print("\n" + "=" * 80)
print("✅ VALIDATION COMPLETE!")
print(f"📁 Results: {OUTPUT_DIR}/")
print("\nNow compare the 24x24 images against real Bespoke Punks!")
print("=" * 80)
