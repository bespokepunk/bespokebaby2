#!/usr/bin/env python3
"""
Test nerijs/pixel-art-xl LoRA with SDXL
This should produce better true pixel art than FLUX
"""

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from pathlib import Path
from PIL import Image

# Test prompts - same as FLUX test
test_prompts = [
    {
        "name": "purple_female",
        "prompt": "TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing"
    },
    {
        "name": "orange_male",
        "prompt": "TOK bespoke punk, 24x24 pixel art, male, orange solid background, black hair, brown eyes, tan skin, right-facing"
    },
    {
        "name": "teal_redhead",
        "prompt": "TOK bespoke punk style, 24x24 pixel art portrait, male, teal background, red hair, blue eyes with glasses, light skin, right-facing"
    }
]

def test_pixel_art_xl():
    """Test pixel-art-xl LoRA"""

    print("=" * 80)
    print("🎨 TESTING PIXEL-ART-XL LoRA")
    print("=" * 80)
    print("Loading SDXL + pixel-art-xl LoRA...")
    print()

    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    if device == "cpu":
        print("⚠️  Warning: Running on CPU will be VERY slow!")
        print("   Consider running this on a GPU machine.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    # Load SDXL base model
    print("\n📥 Loading SDXL base model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
        variant="fp16" if device == "cuda" else None
    )

    # Load pixel-art-xl LoRA
    print("📥 Loading pixel-art-xl LoRA...")
    pipe.load_lora_weights("nerijs/pixel-art-xl")

    # Optimize
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to(device)

    # Enable memory optimizations
    if device == "cuda":
        pipe.enable_model_cpu_offload()
        pipe.enable_vae_slicing()

    print("✅ Models loaded!")

    # Create output directory
    output_dir = Path("./pixelart_xl_test_outputs")
    output_dir.mkdir(exist_ok=True)

    # Generate images
    for i, test in enumerate(test_prompts, 1):
        print(f"\n📸 Generating {i}/{len(test_prompts)}: {test['name']}")
        print(f"   Prompt: {test['prompt'][:80]}...")

        try:
            # Generate at higher resolution
            image = pipe(
                prompt=test['prompt'],
                num_inference_steps=25,
                guidance_scale=7.5,
                height=512,
                width=512
            ).images[0]

            # Save high-res version
            save_path_hires = output_dir / f"{test['name']}_hires.png"
            image.save(save_path_hires)
            print(f"   ✅ Saved high-res: {save_path_hires}")

            # Downscale 8x with Nearest Neighbor for pixel-perfect result
            # 512 / 8 = 64 pixels (close to 24x24, but cleaner)
            small_size = (64, 64)
            image_small = image.resize(small_size, Image.NEAREST)

            # Scale back up for viewing (but keep pixel boundaries)
            image_pixel_perfect = image_small.resize((512, 512), Image.NEAREST)

            save_path_pixel = output_dir / f"{test['name']}_pixel.png"
            image_pixel_perfect.save(save_path_pixel)
            print(f"   ✅ Saved pixel art: {save_path_pixel}")

            # Also save the tiny 64x64 version
            save_path_tiny = output_dir / f"{test['name']}_64x64.png"
            image_small.save(save_path_tiny)
            print(f"   ✅ Saved 64x64: {save_path_tiny}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE!")
    print(f"📁 Images saved to: {output_dir.absolute()}")
    print("=" * 80)
    print("\n💡 Files generated:")
    print("   *_hires.png    = Original 512x512 generation")
    print("   *_pixel.png    = Pixel-perfect version (64x64 → 512x512)")
    print("   *_64x64.png    = Actual low-res pixel art")
    print("\nCompare with FLUX results to see which is better!")

if __name__ == "__main__":
    test_pixel_art_xl()
