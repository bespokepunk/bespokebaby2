#!/usr/bin/env python3
"""
Validate V2 models with ACTUAL Bespoke Punk prompts from training data
"""

import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path

# Use REAL prompts from training captions
REAL_PUNK_PROMPTS = [
    {
        "name": "simple_punk",
        "prompt": "bespoke, 24x24 pixel art portrait, bright green solid background, black hair, blue eyes, white/pale skin",
        "negative": "blurry, low quality, 3d, photorealistic, smooth"
    },
    {
        "name": "with_accessories",
        "prompt": "bespoke, 24x24 pixel art portrait, purple/lavender solid background, long black hair, covered by purple sunglasses, light/peach skin, pink lips",
        "negative": "blurry, low quality, 3d, photorealistic, smooth"
    },
    {
        "name": "checkered_bg",
        "prompt": "bespoke, 24x24 pixel art portrait, brown and yellow checkered pattern background, brown hair, brown eyes, light skin, brown mustache",
        "negative": "blurry, low quality, 3d, photorealistic, smooth"
    },
    {
        "name": "gradient_bg",
        "prompt": "bespoke, 24x24 pixel art portrait, blue gradient background, dark brown hair, covered by black sunglasses, brown/dark skin, beard, white collar",
        "negative": "blurry, low quality, 3d, photorealistic, smooth"
    },
]

MODELS = {
    "V1_Epoch2": "models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000002.safetensors",
    "V2_Epoch1": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000001.safetensors",
    "V2_Epoch2": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2-000002.safetensors",
    "V2_Epoch3": "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2.safetensors",
}

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
OUTPUT_DIR = Path("bespoke_validation")
OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

print("🎨 BESPOKE PUNKS VALIDATION TEST")
print("=" * 80)
print(f"Device: {DEVICE}")
print(f"Testing: {len(REAL_PUNK_PROMPTS)} real punk prompts across {len(MODELS)} models")
print("=" * 80)

# Load base model
print(f"\n📦 Loading base model: {BASE_MODEL}")
pipe = StableDiffusionXLPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
    variant="fp16" if DEVICE != "cpu" else None,
)
pipe = pipe.to(DEVICE)

for model_name, lora_path in MODELS.items():
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {model_name}")
    print(f"{'='*80}")

    # Load LoRA
    pipe.unload_lora_weights()
    pipe.load_lora_weights(lora_path)

    model_dir = OUTPUT_DIR / model_name
    model_dir.mkdir(exist_ok=True)

    for test in REAL_PUNK_PROMPTS:
        print(f"\n  → {test['name']}")
        print(f"     Prompt: {test['prompt'][:60]}...")

        output_path = model_dir / f"{test['name']}.png"

        image = pipe(
            prompt=test["prompt"],
            negative_prompt=test["negative"],
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
        ).images[0]

        image.save(output_path)
        print(f"     ✅ Saved: {output_path}")

print("\n" + "=" * 80)
print("✅ VALIDATION COMPLETE!")
print(f"📁 Results: {OUTPUT_DIR}/")
print("\nCheck if the images look like actual Bespoke Punks!")
print("Compare all 4 model versions for each prompt type.")
print("=" * 80)
