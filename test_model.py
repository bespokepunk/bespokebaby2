#!/usr/bin/env python3
"""
Test your trained Bespoke Punk SDXL model
"""

import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path
import argparse
from datetime import datetime

def test_model(
    model_path="./models/bespoke_punk_sdxl/final_model",
    output_dir="./test_outputs",
    num_images=5,
    steps=30,
    guidance_scale=7.5
):
    """Test the trained model with sample prompts"""

    print("🎨 BESPOKE PUNK MODEL TESTING")
    print("=" * 80)

    # Check if model exists
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ Model not found at: {model_path}")
        print("Available models:")
        models_dir = Path("./models")
        if models_dir.exists():
            for model in models_dir.glob("*/final_model"):
                print(f"   - {model}")
        return

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Setup device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Using device: {device}")

    # Load base model
    print(f"\n📥 Loading base SDXL model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
        variant="fp16" if device == "cuda" else None
    )

    # Load LoRA weights
    print(f"📥 Loading your trained LoRA from: {model_path}")
    pipe.load_lora_weights(model_path)
    pipe = pipe.to(device)

    print("✅ Model loaded successfully!")

    # Test prompts
    test_prompts = [
        "TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing",
        "TOK bespoke, 24x24 pixel art, male, orange solid background, black hair, brown eyes, tan skin, right-facing",
        "TOK bespoke punk, 24x24 pixel grid, female, pink background, blonde hair, green eyes, glasses, light skin, right-facing",
        "TOK bespoke, 24x24 pixel art portrait, male, teal background, red hair, blue eyes, beard, light skin, right-facing",
        "TOK bespoke punk style, 24x24 pixel grid, female, yellow background, black hair, brown eyes, earrings, tan skin, right-facing",
    ]

    print(f"\n🎨 Generating {num_images} test images...")
    print(f"   Steps: {steps}")
    print(f"   Guidance: {guidance_scale}")
    print()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, prompt in enumerate(test_prompts[:num_images], 1):
        print(f"\n[{i}/{num_images}] {prompt[:80]}...")

        try:
            image = pipe(
                prompt,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                height=512,
                width=512
            ).images[0]

            # Save image
            output_file = output_dir / f"test_{timestamp}_{i:02d}.png"
            image.save(output_file)

            # Also save prompt
            prompt_file = output_dir / f"test_{timestamp}_{i:02d}.txt"
            with open(prompt_file, 'w') as f:
                f.write(prompt)

            print(f"✅ Saved: {output_file}")

        except Exception as e:
            print(f"❌ Error generating image {i}: {e}")

    print(f"\n🎉 Testing complete!")
    print(f"📁 Images saved to: {output_dir}")
    print(f"\nReview the images to assess model quality.")
    print(f"Look for:")
    print(f"  - Clean pixel art style")
    print(f"  - Correct colors (hair, eyes, background)")
    print(f"  - Proper features (right-facing profile)")
    print(f"  - Sharp edges (no blur/anti-aliasing)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test trained Bespoke Punk model")

    parser.add_argument("--model_path", type=str,
                        default="./models/bespoke_punk_sdxl/final_model",
                        help="Path to trained model")
    parser.add_argument("--output_dir", type=str,
                        default="./test_outputs",
                        help="Output directory for test images")
    parser.add_argument("--num_images", type=int, default=5,
                        help="Number of test images to generate")
    parser.add_argument("--steps", type=int, default=30,
                        help="Inference steps")
    parser.add_argument("--guidance_scale", type=float, default=7.5,
                        help="Guidance scale")

    args = parser.parse_args()

    test_model(
        model_path=args.model_path,
        output_dir=args.output_dir,
        num_images=args.num_images,
        steps=args.steps,
        guidance_scale=args.guidance_scale
    )
