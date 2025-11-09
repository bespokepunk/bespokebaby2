#!/usr/bin/env python3
"""
Test V3 Epoch 1 to see if we can get proper Bespoke Punk heads
Try different prompts to coerce it into head-only portraits
"""

from diffusers import StableDiffusionXLPipeline
import torch
from PIL import Image
from pathlib import Path

# Configuration
LORA_PATH = "/Users/ilyssaevans/Downloads/BespokePunks3-000001.safetensors"
BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"  # Fallback if Nova Pixels not available locally
OUTPUT_DIR = Path("v3_epoch1_tests")
OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

# Test prompts - try to force HEAD ONLY
TEST_PROMPTS = [
    # Emphasize "head only", "face only"
    {
        "name": "test1_head_only",
        "prompt": "pixel art, 24x24, close-up face portrait of bespoke punk, head only, no body, green solid background, black hair, blue eyes, light skin, sharp pixel edges",
        "negative": "full body, torso, shoulders, character sprite, game sprite, standing, walking"
    },
    {
        "name": "test2_profile_face",
        "prompt": "pixel art, 24x24, profile face only portrait of bespoke punk, just the head, red checkered background, brown hair, brown eyes, tan skin, mustache, sharp pixel edges",
        "negative": "body, legs, arms, full character, sprite, torso"
    },
    {
        "name": "test3_headshot",
        "prompt": "pixel art, 24x24, headshot portrait of bespoke punk, face crop, blue gradient background, blonde hair, green eyes, pale skin, sunglasses, sharp pixel edges",
        "negative": "body parts, full body, character sprite, game character"
    },
    {
        "name": "test4_simple",
        "prompt": "pixel art, 24x24, portrait of bespoke punk, purple solid background, black hair, brown eyes, light skin",
        "negative": "body, torso, full character"
    }
]

def generate_test(prompt_config):
    """Generate a test image with given prompt"""
    print(f"\n🎨 Generating: {prompt_config['name']}")
    print(f"   Prompt: {prompt_config['prompt'][:80]}...")

    try:
        # Load base model
        pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32
        ).to(DEVICE)

        # Load LoRA
        pipe.load_lora_weights(LORA_PATH)

        # Generate
        image = pipe(
            prompt=prompt_config['prompt'],
            negative_prompt=prompt_config.get('negative', ''),
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512
        ).images[0]

        # Save full size
        output_path = OUTPUT_DIR / f"{prompt_config['name']}_512.png"
        image.save(output_path)
        print(f"   ✅ Saved: {output_path}")

        # Downscale to 24x24 (nearest neighbor)
        img_24 = image.resize((24, 24), Image.Resampling.NEAREST)
        output_path_24 = OUTPUT_DIR / f"{prompt_config['name']}_24.png"
        img_24.save(output_path_24)
        print(f"   ✅ Saved: {output_path_24}")

        return image, img_24

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None

def main():
    print("🧪 TESTING V3 EPOCH 1")
    print("="*80)
    print(f"\nLoRA: {LORA_PATH}")
    print(f"Device: {DEVICE}")
    print(f"Output: {OUTPUT_DIR}/")
    print()
    print("Trying different prompts to force HEAD-ONLY portraits...")
    print("(Not full body character sprites)")
    print()

    for prompt_config in TEST_PROMPTS:
        generate_test(prompt_config)

    print()
    print("="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)
    print()
    print(f"📁 Check outputs in: {OUTPUT_DIR}/")
    print()
    print("What to look for:")
    print("  ✅ GOOD: Just heads/faces (like Bespoke Punks)")
    print("  ❌ BAD: Full body sprites/characters")
    print()
    print("If results show full bodies:")
    print("  → Nova Pixels XL is wrong base model")
    print("  → Need to try SD 1.5 PixNite or Kohya with different base")

if __name__ == "__main__":
    main()
