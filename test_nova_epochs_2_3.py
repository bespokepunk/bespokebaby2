#!/usr/bin/env python3
"""
Test Nova Pixels XL Epochs 2 & 3
Epoch 2 looks MUCH better than Epoch 1 - let's test properly!
"""

from diffusers import StableDiffusionXLPipeline
import torch
from PIL import Image, ImageFilter
from pathlib import Path
import numpy as np

# Paths
EPOCH2_PATH = "/Users/ilyssaevans/Downloads/BespokePunks3-000002.safetensors"
EPOCH3_PATH = "/Users/ilyssaevans/Downloads/BespokePunks3.safetensors"
BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
OUTPUT_DIR = Path("nova_epochs_test")
OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

# Test prompts - based on real Bespoke Punks
TEST_PROMPTS = [
    {
        "name": "simple_green_bg",
        "prompt": "pixel art, 24x24, portrait of bespoke punk, bright green solid background, black hair, blue eyes, light skin, sharp pixel edges",
    },
    {
        "name": "checkered_pattern",
        "prompt": "pixel art, 24x24, portrait of bespoke punk, brown and yellow checkered pattern background, brown hair, brown eyes, tan skin, mustache, sharp pixel edges",
    },
    {
        "name": "gradient_bg",
        "prompt": "pixel art, 24x24, portrait of bespoke punk, pixelated blue gradient background with stepped color transitions, dark hair, tan skin, beard, sharp pixel edges",
    },
    {
        "name": "sunglasses",
        "prompt": "pixel art, 24x24, portrait of bespoke punk, purple solid background, black hair, covered by purple sunglasses, light skin, pink lips, sharp pixel edges",
    },
    {
        "name": "hat_accessory",
        "prompt": "pixel art, 24x24, portrait of bespoke punk, red solid background, brown hair, red cap, brown eyes, tan skin, sharp pixel edges",
    },
]

def quantize_40_colors(img):
    """Quantize to 40 colors to match originals better"""
    return img.quantize(colors=40, method=2, dither=0).convert('RGB')

def sharpen_edges(img):
    """Sharpen to enhance pixel edges"""
    return img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

def downscale_to_24x24(img_512):
    """Proper downscaling pipeline for pixel art"""
    # Method 1: Direct downscale with nearest neighbor
    img_24_direct = img_512.resize((24, 24), Image.Resampling.NEAREST)

    # Method 2: Quantize first, then downscale
    img_quant = quantize_40_colors(img_512)
    img_quant_sharp = sharpen_edges(img_quant)
    img_24_processed = img_quant_sharp.resize((24, 24), Image.Resampling.NEAREST)

    return img_24_direct, img_24_processed

def count_colors(img):
    """Count unique colors in image"""
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    unique = set(tuple(p) for p in pixels)
    return len(unique)

def test_epoch(lora_path, epoch_name):
    """Test a single epoch"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING {epoch_name}")
    print(f"{'='*80}")
    print(f"LoRA: {lora_path}")
    print()

    try:
        # Load pipeline
        print("Loading model...")
        pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32
        ).to(DEVICE)

        pipe.load_lora_weights(lora_path)
        print(f"✅ Loaded on {DEVICE}")
        print()

        # Test each prompt
        for i, prompt_config in enumerate(TEST_PROMPTS, 1):
            print(f"📸 {i}/{len(TEST_PROMPTS)}: {prompt_config['name']}")

            # Generate
            image_512 = pipe(
                prompt=prompt_config['prompt'],
                negative_prompt="full body, body, legs, character sprite, game sprite",
                num_inference_steps=30,
                guidance_scale=7.5,
                width=512,
                height=512
            ).images[0]

            # Save 512x512 version
            output_512 = OUTPUT_DIR / f"{epoch_name}_{prompt_config['name']}_512.png"
            image_512.save(output_512)

            # Downscale both ways
            img_24_direct, img_24_processed = downscale_to_24x24(image_512)

            # Save both 24x24 versions
            output_24_direct = OUTPUT_DIR / f"{epoch_name}_{prompt_config['name']}_24_direct.png"
            output_24_processed = OUTPUT_DIR / f"{epoch_name}_{prompt_config['name']}_24_processed.png"

            img_24_direct.save(output_24_direct)
            img_24_processed.save(output_24_processed)

            # Count colors
            colors_direct = count_colors(img_24_direct)
            colors_processed = count_colors(img_24_processed)

            print(f"   512x512: {output_512}")
            print(f"   24x24 (direct): {colors_direct} colors")
            print(f"   24x24 (processed): {colors_processed} colors")
            print()

        print(f"✅ {epoch_name} testing complete!")

    except Exception as e:
        print(f"❌ Error testing {epoch_name}: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🎨 TESTING NOVA PIXELS XL - EPOCHS 2 & 3")
    print("="*80)
    print(f"\nDevice: {DEVICE}")
    print(f"Output: {OUTPUT_DIR}/")
    print()
    print("Epoch 2 looked promising in CivitAI preview!")
    print("Testing if it learned proper Bespoke Punk heads...")
    print()

    # Test Epoch 2
    if Path(EPOCH2_PATH).exists():
        test_epoch(EPOCH2_PATH, "Epoch2")
    else:
        print(f"❌ Epoch 2 not found: {EPOCH2_PATH}")

    # Test Epoch 3
    if Path(EPOCH3_PATH).exists():
        test_epoch(EPOCH3_PATH, "Epoch3")
    else:
        print(f"❌ Epoch 3 not found: {EPOCH3_PATH}")

    print()
    print("="*80)
    print("✅ ALL TESTING COMPLETE")
    print("="*80)
    print()
    print(f"📁 Check results: {OUTPUT_DIR}/")
    print()
    print("Compare outputs to originals in:")
    print("  FORTRAINING6/bespokepunks/")
    print()
    print("Key questions:")
    print("  1. Are these HEADS/PORTRAITS (not full body)?")
    print("  2. Do they look like real Bespoke Punks?")
    print("  3. Are edges sharp or blurry?")
    print("  4. How many colors? (Target: 35-50)")
    print()
    print("If Epoch 2 or 3 is 80%+ match:")
    print("  → Ship it! No need for Kohya!")
    print("If still not good enough:")
    print("  → Proceed with Kohya at 24x24 native")

if __name__ == "__main__":
    main()
