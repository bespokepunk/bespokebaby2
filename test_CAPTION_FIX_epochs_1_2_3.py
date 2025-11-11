#!/usr/bin/env python3
"""
Test CAPTION_FIX Experiment - Epochs 1, 2, 3
Testing the fix where ALL hex codes were removed from captions

Expected improvements:
- Green background should appear by Epoch 5-7 (vs Epoch 9 in keep_tokens=3)
- No color bleeding (duplicate hex codes eliminated)
- Unique colors < 250 (vs 300-500 previously)
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
from collections import Counter

MODEL_NAME = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs_CAPTION_FIX_epochs_9_final"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LORA_PATHS = {
    "epoch9": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora_keep_tokens_3-000009 (1).safetensors",
    "final": "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora_keep_tokens_3 (1).safetensors",
}

# Test prompts based on cleaned captions (no hex codes, just descriptive text)
TEST_PROMPTS = [
    # Critical test: Green background (key metric - when does it appear?)
    ("green_bg_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium male skin tone, bright green background, sharp pixel edges, hard color borders, retro pixel art style"),

    # Test color accuracy
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    # Test accessories
    ("golden_earrings", "pixel art, 24x24, portrait of bespoke punk lady, black hair, wearing golden earrings, brown eyes, light skin, gray solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    # Test complex features
    ("sunglasses_lad", "pixel art, 24x24, portrait of bespoke punk lad, blonde hair, wearing black stunner shades with white reflection, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style"),

    # Test from actual training data (lady_074_melon.txt)
    ("melon_lady", "pixel art, 24x24, portrait of bespoke punk lady, hair, wearing white baseball cap, wearing big dark brown rimmed sunglasses with blue reflection, white diamond earring, lips, neutral expression, skin, bright green background, blue jacket with white hoodie underneath it with lifeguard cross on it"),

    # Test from actual training data (lad_002_cash.txt)
    ("cash_lad", "pixel art, 24x24, portrait of bespoke punk lad, bright lime green yellow green hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style, wearing black stunner shades with white reflections, dark eyes, lips, neutral expression, light pale green skin tone, split background, wearing classic vintage revolutionary war era dark grey suit with light grey and white undergarments"),

    # Test from actual training data (lad_001_carbon.txt)
    ("carbon_lad", "pixel art, 24x24, portrait of bespoke punk lad, hair, wearing gray hat with multicolored (red gold and white) logo in the center, lips, neutral expression, dark brown eyes, medium male skin tone, checkered brick background, medium grey shirt"),
]

def count_unique_colors(image):
    """Count unique colors in an image"""
    colors = image.getcolors(maxcolors=100000)
    return len(colors) if colors else 0

def analyze_image(image, name):
    """Analyze image metrics"""
    small = image.resize((24, 24), Image.NEAREST)
    unique_colors = count_unique_colors(small)

    # Get most common colors
    pixels = list(small.getdata())
    color_counts = Counter(pixels)
    top_colors = color_counts.most_common(5)

    return {
        'name': name,
        'unique_colors': unique_colors,
        'top_colors': top_colors,
    }

print("=" * 100)
print("TESTING CAPTION_FIX EXPERIMENT - EPOCH 9 & FINAL")
print("=" * 100)
print(f"Output: {OUTPUT_DIR}")
print()
print("🎯 HYPOTHESIS VALIDATION:")
print("  - Root cause: Duplicate hex codes in captions (e.g., hair #03dc73 AND bg #03dc73)")
print("  - Fix: Removed ALL 3,621 hex codes, kept descriptive color text")
print("  - Expected: Green background by Epoch 5-7 (vs Epoch 9 in keep_tokens=3)")
print("  - Expected: Unique colors < 250 (vs 300-500 previously)")
print()
print("=" * 100)
print()

all_results = {}

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

    epoch_results = []

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

        # Analyze
        metrics = analyze_image(image, name)
        epoch_results.append(metrics)

        print(f"    ✓ Saved: {name}_[24/512].png - {metrics['unique_colors']} colors")

    all_results[epoch_name] = epoch_results
    print(f"\n✓ {epoch_name.upper()} complete!\n")

    # Clean up
    del pipe
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

print("=" * 100)
print("📊 EPOCH COMPARISON")
print("=" * 100)
print()

for epoch_name in LORA_PATHS.keys():
    results = all_results[epoch_name]
    avg_colors = sum(r['unique_colors'] for r in results) / len(results)

    print(f"{epoch_name.upper()}:")
    print(f"  Average unique colors: {avg_colors:.1f}")

    # Check for green background test
    green_bg = [r for r in results if 'green_bg' in r['name']]
    if green_bg:
        print(f"  Green BG test: {green_bg[0]['unique_colors']} colors")

    print()

print("=" * 100)
print("✅ ALL EPOCHS TESTED!")
print("=" * 100)
print(f"\nResults in: {OUTPUT_DIR}/")
print()
print("Folders created:")
print(f"  - {OUTPUT_DIR}/epoch9/")
print(f"  - {OUTPUT_DIR}/final/")
print()
print("🔍 KEY VALIDATION CHECKS:")
print("  1. Green background test - does it show correct color?")
print("  2. Unique colors - are we < 250? (vs 300-500 in previous runs)")
print("  3. Color bleeding - do different features have distinct colors?")
print("  4. Pixel art style - clean, blocky, retro style?")
print()
print("📈 COMPARE AGAINST:")
print("  - keep_tokens=3: Epoch 1-2 baseline (wrong bg)")
print("  - keep_tokens=3: Epoch 9 (green bg finally appeared, 301 colors)")
print("  - Expected: Caption fix should show green bg earlier (Epoch 5-7)")
print()
