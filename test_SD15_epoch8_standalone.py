#!/usr/bin/env python3
"""
Test SD 1.5 Epoch 8 (standalone test since batch test crashed)
"""

import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path

# Config
LORA_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000008.safetensors"
OUTPUT_DIR = "test_outputs_SD15_epoch8"

# Test prompts
TEST_PROMPTS = [
    {
        "name": "brown_eyes_test",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "negative": "blurry, smooth, gradients, antialiased, photography, realistic, 3d render"
    },
    {
        "name": "earrings_test",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, wearing golden earrings, blue eyes, light skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "negative": "blurry, smooth, gradients, antialiased, photography, realistic, 3d render"
    },
    {
        "name": "sunglasses_test",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, black afro hair, wearing black stunner shades, brown eyes, dark skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "negative": "blurry, smooth, gradients, antialiased, photography, realistic, 3d render"
    },
    {
        "name": "full_accessories",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, red hair, wearing red bow in hair, wearing silver necklace, wearing golden earrings, green eyes, medium skin, pink solid background, sharp pixel edges, hard color borders, retro pixel art style",
        "negative": "blurry, smooth, gradients, antialiased, photography, realistic, 3d render"
    }
]

def main():
    print("="*80)
    print("TESTING SD 1.5 EPOCH 8 (STANDALONE)")
    print("="*80)
    print()

    # Check if LoRA exists
    if not Path(LORA_PATH).exists():
        print(f"❌ Error: Epoch 8 LoRA not found: {LORA_PATH}")
        print("   Please download epoch 8 from RunPod")
        return

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    # Detect device
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(f"Device: {device}")
    print()

    # Load pipeline
    print("Loading SD 1.5 with Epoch 8 LoRA...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        safety_checker=None,
    )
    pipe.load_lora_weights(LORA_PATH)
    pipe = pipe.to(device)
    print("✓ Loaded!")
    print()

    # Generate test images
    for i, test in enumerate(TEST_PROMPTS, 1):
        print(f"[{i}/4] Generating: {test['name']}")
        print(f"    Prompt: {test['prompt'][:60]}...")

        image = pipe(
            prompt=test['prompt'],
            negative_prompt=test['negative'],
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
            generator=torch.Generator(device=device).manual_seed(42)
        ).images[0]

        # Save
        output_file = output_path / f"epoch8_{test['name']}.png"
        image.save(output_file)
        print(f"    ✓ Saved: {output_file}")
        print()

    print("="*80)
    print("✅ EPOCH 8 TESTING COMPLETE!")
    print("="*80)
    print()
    print(f"📁 Output directory: {OUTPUT_DIR}/")
    print()
    print("Review images to check:")
    print("  - Brown eyes render correctly (not blue)")
    print("  - All accessories visible (earrings, bow, necklace, sunglasses)")
    print("  - Clean bespoke punk pixel art style")
    print()

if __name__ == "__main__":
    main()
