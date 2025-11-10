#!/usr/bin/env python3
"""
Quick Epoch Tester - Generate 1 sample image to check quality

Usage:
    python quick_test_epoch.py "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000001.safetensors"

Or edit LORA_PATH below and just run: python quick_test_epoch.py
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import sys
import os

# =============================================================================
# CONFIGURATION - Update this with your epoch file path
# =============================================================================

LORA_PATH = "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000001 (1).safetensors"

# Quick test prompt (using FINAL CORRECTED caption format)
TEST_PROMPT = "pixel art, 24x24, portrait of bespoke punk lady, pink hair (#ff66cc), crown, hoop earrings, eyes (#663300), lips (#cc6666), neutral expression, skin (#f0c090), solid green background (#00ff00)"

NEGATIVE_PROMPT = "blurry, smooth, gradients, antialiased, photography, realistic, 3d render, full body, character sprite"

# =============================================================================

def main():
    # Get LoRA path from command line or use default
    lora_path = sys.argv[1] if len(sys.argv) > 1 else LORA_PATH

    if not os.path.exists(lora_path):
        print(f"❌ ERROR: File not found: {lora_path}")
        print(f"\nUsage: python quick_test_epoch.py <path-to-lora.safetensors>")
        return

    # Extract epoch name from filename
    filename = os.path.basename(lora_path)
    epoch_name = filename.replace(".safetensors", "").replace(" ", "_")

    print("\n" + "="*80)
    print(f"🎨 QUICK EPOCH TEST: {epoch_name}")
    print("="*80)
    print(f"LoRA: {lora_path}")
    print(f"Size: {os.path.getsize(lora_path) / (1024*1024):.1f}MB")
    print(f"Prompt: {TEST_PROMPT[:60]}...")
    print("="*80 + "\n")

    # Load pipeline
    print("Loading SD 1.5 + LoRA...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.load_lora_weights(lora_path)

    # Move to MPS/CUDA
    if torch.backends.mps.is_available():
        pipe = pipe.to("mps")
        device = "MPS"
    elif torch.cuda.is_available():
        pipe = pipe.to("cuda")
        device = "CUDA"
    else:
        device = "CPU"

    print(f"✓ Pipeline ready on {device}\n")

    # Generate image
    print("Generating test image...")
    image = pipe(
        prompt=TEST_PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
        generator=torch.Generator().manual_seed(42),
    ).images[0]

    # Save outputs
    output_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/quick_tests"
    os.makedirs(output_dir, exist_ok=True)

    # Save 512x512
    output_512 = os.path.join(output_dir, f"{epoch_name}_test_512.png")
    image.save(output_512)
    print(f"✓ Saved 512x512: {output_512}")

    # Save 24x24
    image_24 = image.resize((24, 24), Image.Resampling.NEAREST)
    output_24 = os.path.join(output_dir, f"{epoch_name}_test_24.png")
    image_24.save(output_24)
    print(f"✓ Saved 24x24: {output_24}")

    # Open the output folder
    print(f"\n✅ DONE! Opening output folder...")
    os.system(f'open "{output_dir}"')

    print("\n" + "="*80)
    print("🎯 Quick visual check:")
    print("  - Is it pixel art style? (not photorealistic)")
    print("  - Are colors correct? (pink hair, green background)")
    print("  - Are accessories visible? (crown, earrings)")
    print("  - Is background solid? (not noisy/textured)")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
