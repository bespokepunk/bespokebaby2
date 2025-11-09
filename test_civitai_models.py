#!/usr/bin/env python3
"""
Test and compare CivitAI Bespoke Punks LoRA models across different epochs.

This script generates test images using different epoch checkpoints to help
you determine which trained model performs best.
"""

import os
from pathlib import Path
from diffusers import StableDiffusionXLPipeline, AutoPipelineForText2Image
import torch
from PIL import Image
import datetime

# Configuration
BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"  # Adjust if you used a different base
MODELS_DIR = Path("models/civitai_bespoke_punks_v1")
OUTPUT_DIR = Path("test_outputs")
DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

# Test prompts - covering different features
TEST_PROMPTS = [
    {
        "name": "basic_test",
        "prompt": "bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing",
        "negative": "blurry, low quality, 3d, photorealistic, smooth"
    },
    {
        "name": "coordinate_test",
        "prompt": "bespoke, 24x24 pixel grid portrait, symbolic punk style, vibrant orange solid background, black hair starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12), brown iris eyes at (9,12) and (14,12), black nose dot at (11,13), pink lips spanning x=10-13 y=15-16, tan skin tone with jaw defined at y=19, blue collar at bottom edge y=20-22, right-facing, pure pixel art with no gradients or anti-aliasing",
        "negative": "blurry, low quality, 3d, photorealistic, smooth, anti-aliasing"
    },
    {
        "name": "accessory_test",
        "prompt": "bespoke, 24x24 pixel art, male, glasses spanning x=7-16 y=11-13, black hair, green solid background, right-facing profile",
        "negative": "blurry, low quality, 3d, photorealistic"
    },
    {
        "name": "creative_test",
        "prompt": "bespoke, 24x24 pixel art portrait, female, red background, blonde hair, green eyes, dark skin, wearing sunglasses",
        "negative": "blurry, low quality, 3d, photorealistic, smooth"
    }
]

# Epochs to test (prioritize 5, 7, 10)
EPOCHS_TO_TEST = [2, 5, 7, 10]

# Generation settings
GEN_SETTINGS = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 512,  # Generate at higher res, can downscale later
    "height": 512,
    "num_images_per_prompt": 1
}


def get_model_path(epoch):
    """Get the path to a specific epoch model."""
    if epoch == 10:
        return MODELS_DIR / "Bespoke_Punks_24x24_Pixel_Art.safetensors"
    else:
        return MODELS_DIR / f"Bespoke_Punks_24x24_Pixel_Art-{epoch:06d}.safetensors"


def load_pipeline():
    """Load the base SDXL pipeline."""
    print(f"Loading base model: {BASE_MODEL}")
    print(f"Using device: {DEVICE}")

    if DEVICE == "mps":
        # MPS (Apple Silicon) optimizations
        pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        pipe = pipe.to("mps")
        # Enable attention slicing for memory efficiency
        pipe.enable_attention_slicing()
    elif DEVICE == "cuda":
        # CUDA optimizations
        pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        pipe = pipe.to("cuda")
        # Try to enable xformers if available
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except:
            print("xformers not available, using default attention")
    else:
        # CPU fallback
        pipe = StableDiffusionXLPipeline.from_pretrained(BASE_MODEL)

    return pipe


def test_epoch(pipe, epoch, test_prompt_data):
    """Test a specific epoch model with given prompts."""
    model_path = get_model_path(epoch)

    if not model_path.exists():
        print(f"⚠️  Model not found: {model_path}")
        return None

    print(f"\n🧪 Testing Epoch {epoch}: {model_path.name}")

    # Load LoRA weights
    pipe.load_lora_weights(str(model_path))

    results = []

    for prompt_data in test_prompt_data:
        prompt_name = prompt_data["name"]
        prompt = prompt_data["prompt"]
        negative_prompt = prompt_data.get("negative", "")

        print(f"  Generating: {prompt_name}...")

        # Generate image
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            **GEN_SETTINGS
        ).images[0]

        # Save image
        output_subdir = OUTPUT_DIR / f"epoch_{epoch:02d}"
        output_subdir.mkdir(parents=True, exist_ok=True)

        output_path = output_subdir / f"{prompt_name}.png"
        image.save(output_path)

        print(f"    ✅ Saved: {output_path}")

        results.append({
            "epoch": epoch,
            "prompt_name": prompt_name,
            "path": output_path,
            "image": image
        })

    # Unload LoRA weights for next test
    pipe.unload_lora_weights()

    return results


def create_comparison_grid(all_results):
    """Create a grid comparing all epochs and prompts."""
    print("\n📊 Creating comparison grid...")

    # Group by prompt
    prompts = sorted(set(r["prompt_name"] for r in all_results))
    epochs = sorted(set(r["epoch"] for r in all_results))

    for prompt_name in prompts:
        # Get all images for this prompt across epochs
        images = []
        for epoch in epochs:
            result = next((r for r in all_results if r["prompt_name"] == prompt_name and r["epoch"] == epoch), None)
            if result:
                images.append(result["image"])

        if not images:
            continue

        # Create horizontal comparison
        widths, heights = zip(*(img.size for img in images))
        total_width = sum(widths) + (len(images) - 1) * 10  # 10px spacing
        max_height = max(heights)

        comparison = Image.new('RGB', (total_width, max_height), (255, 255, 255))

        x_offset = 0
        for img in images:
            comparison.paste(img, (x_offset, 0))
            x_offset += img.width + 10

        # Save comparison
        comparison_path = OUTPUT_DIR / f"comparison_{prompt_name}.png"
        comparison.save(comparison_path)
        print(f"  ✅ Saved comparison: {comparison_path}")


def main():
    """Main testing workflow."""
    print("=" * 60)
    print("🎨 Bespoke Punks LoRA Model Testing")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load pipeline
    pipe = load_pipeline()

    # Test each epoch
    all_results = []

    for epoch in EPOCHS_TO_TEST:
        results = test_epoch(pipe, epoch, TEST_PROMPTS)
        if results:
            all_results.extend(results)

    # Create comparison grids
    if all_results:
        create_comparison_grid(all_results)

    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print(f"📁 Results saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)

    # Print summary
    print("\n📊 Summary:")
    print(f"  Tested {len(EPOCHS_TO_TEST)} epochs")
    print(f"  Generated {len(all_results)} images")
    print(f"  Used {len(TEST_PROMPTS)} test prompts")

    print("\n🎯 Next Steps:")
    print("  1. Review images in test_outputs/")
    print("  2. Compare epoch_05, epoch_07, and epoch_10 folders")
    print("  3. Check comparison_*.png files for side-by-side views")
    print("  4. Choose the best performing epoch")
    print("\n💡 Note: Epoch 5 or 7 often performs better than the final epoch 10!")


if __name__ == "__main__":
    main()
