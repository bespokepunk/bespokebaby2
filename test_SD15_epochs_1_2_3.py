#!/usr/bin/env python3
"""
Test SD 1.5 PERFECT Epochs 1, 2, 3
With COMPLETE captions (including all jewelry & accessories!)
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_SD15_epochs_1_2_3"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LORA_PATHS = {
    "epoch1": "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000001.safetensors",
    "epoch2": "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000002.safetensors",
    "epoch3": "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000003.safetensors",
}

# Test prompts based on actual final captions
TEST_PROMPTS = [
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("brown_eyes_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("golden_earrings", "pixel art, 24x24, portrait of bespoke punk lady, black hair, wearing golden earrings, brown eyes, light skin, gray solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("bow_in_hair", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, wearing red bow in hair, blue eyes, light skin, pink solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("sunglasses_lad", "pixel art, 24x24, portrait of bespoke punk lad, blonde hair, wearing black stunner shades with white reflection, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("afro_hair", "pixel art, 24x24, portrait of bespoke punk lady, large voluminous brown afro hair, brown eyes, dark skin, orange solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("necklace", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, wearing silver necklace with pendant, blue eyes, light skin, purple solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    ("crown", "pixel art, 24x24, portrait of bespoke punk lady, red hair, wearing gold crown, green eyes, light skin, green solid background, sharp pixel edges, hard color borders, retro pixel art style"),
]

print("=" * 100)
print("TESTING SD 1.5 PERFECT - EPOCHS 1, 2, 3")
print("=" * 100)
print(f"Output: {OUTPUT_DIR}")
print()
print("Testing with COMPLETE captions including:")
print("  ✓ Earrings")
print("  ✓ Necklaces")
print("  ✓ Bows/ribbons")
print("  ✓ All jewelry & accessories")
print()
print("=" * 100)
print()

for epoch_name, lora_path in LORA_PATHS.items():
    print(f"\n{'=' * 100}")
    print(f"TESTING {epoch_name.upper()}")
    print(f"{'=' * 100}\n")

    # Create epoch folder
    epoch_dir = os.path.join(OUTPUT_DIR, epoch_name)
    os.makedirs(epoch_dir, exist_ok=True)

    # Load pipeline
    print(f"Loading SD 1.5 with {epoch_name} LoRA...")
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)

    # Move to GPU/MPS
    if torch.backends.mps.is_available():
        pipe = pipe.to("mps")
        device = "MPS"
    elif torch.cuda.is_available():
        pipe = pipe.to("cuda")
        device = "CUDA"
    else:
        device = "CPU"

    print(f"✓ Pipeline ready on {device}\n")

    # Generate test images
    for name, prompt in TEST_PROMPTS:
        print(f"  Generating: {name}")

        image = pipe(
            prompt=prompt,
            negative_prompt="blurry, smooth, gradients, antialiased, photography, realistic, 3d render",
            num_inference_steps=30,
            guidance_scale=7.5,
            width=512,
            height=512,
        ).images[0]

        # Save 512x512
        output_512 = os.path.join(epoch_dir, f"{name}_512.png")
        image.save(output_512)

        # Save 24x24 (pixel art size)
        small = image.resize((24, 24), Image.NEAREST)
        output_24 = os.path.join(epoch_dir, f"{name}_24.png")
        small.save(output_24)

        print(f"    ✓ Saved: {name}_[24/512].png")

    print(f"\n✓ {epoch_name.upper()} complete!\n")

    # Clean up
    del pipe
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

print("=" * 100)
print("✅ ALL EPOCHS TESTED!")
print("=" * 100)
print(f"\nResults in: {OUTPUT_DIR}/")
print()
print("Folders created:")
print(f"  - {OUTPUT_DIR}/epoch1/")
print(f"  - {OUTPUT_DIR}/epoch2/")
print(f"  - {OUTPUT_DIR}/epoch3/")
print()
print("🎯 KEY TESTS:")
print("  1. Brown eyes - do they look brown?")
print("  2. Golden earrings - are they visible?")
print("  3. Bow in hair - is it there?")
print("  4. Necklace - visible?")
print("  5. Pixel art style - simple & blocky like bespoke punks?")
print()
print("Compare epochs to see which looks best!")
print()
