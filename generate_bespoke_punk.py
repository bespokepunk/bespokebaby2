#!/usr/bin/env python3
"""
PRODUCTION PIPELINE: Generate True Bespoke Punk Pixel Art

This script generates authentic Bespoke Punk style pixel art by:
1. Using V2_Epoch3 LoRA (best validation results)
2. Generating at 512x512 with SDXL
3. Quantizing to 15 colors using k-means clustering
4. Downsampling to 24x24 for true pixel art

Usage:
    python generate_bespoke_punk.py --prompt "bespoke, 24x24 pixel art portrait, green background, black hair, blue eyes"
"""

import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path
import argparse

def quantize_to_pixel_art(img, n_colors=15):
    """
    Reduce image to n_colors using k-means clustering
    This removes anti-aliasing artifacts and creates true pixel art
    """
    arr = np.array(img)
    original_shape = arr.shape

    # Reshape to list of pixels
    pixels = arr.reshape(-1, 3)

    # Use k-means to find n dominant colors
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)

    # Replace each pixel with its cluster center
    quantized_pixels = kmeans.cluster_centers_[kmeans.labels_]
    quantized_pixels = np.round(quantized_pixels).astype(np.uint8)

    # Reshape back to image
    quantized_arr = quantized_pixels.reshape(original_shape)
    return Image.fromarray(quantized_arr)

def generate_bespoke_punk(prompt, negative_prompt=None, output_path="output.png",
                          generate_24x24=True, n_colors=15):
    """
    Generate a Bespoke Punk style image

    Args:
        prompt: Text description (should start with "bespoke, 24x24 pixel art portrait")
        negative_prompt: Things to avoid (default: anti-aliasing, blur, 3D)
        output_path: Where to save the result
        generate_24x24: Also create a 24x24 pixel version (default: True)
        n_colors: Number of colors for quantization (default: 15)
    """

    # Default negative prompt for pixel art
    if negative_prompt is None:
        negative_prompt = "blurry, low quality, 3d, photorealistic, smooth, anti-aliasing"

    # Model paths
    BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    LORA_PATH = "models/civitai_bespoke_punks_v2/Bespoke_Punks_24x24_Pixel_Art_V2.safetensors"

    DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"

    print(f"🎨 Generating Bespoke Punk...")
    print(f"   Device: {DEVICE}")
    print(f"   Prompt: {prompt}")

    # Load pipeline
    print(f"   Loading SDXL base model...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if DEVICE != "cpu" else torch.float32,
        variant="fp16" if DEVICE != "cpu" else None,
    )
    pipe = pipe.to(DEVICE)

    # Load LoRA
    print(f"   Loading V2_Epoch3 LoRA...")
    pipe.load_lora_weights(LORA_PATH)

    # Generate at 512x512
    print(f"   Generating 512x512 image...")
    image_512 = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
    ).images[0]

    # Quantize to remove anti-aliasing
    print(f"   Quantizing to {n_colors} colors...")
    quantized_512 = quantize_to_pixel_art(image_512, n_colors=n_colors)

    # Save 512x512 version
    output_path = Path(output_path)
    quantized_512.save(output_path)
    print(f"   ✅ Saved 512x512: {output_path}")

    # Generate 24x24 version if requested
    if generate_24x24:
        quantized_24 = quantized_512.resize((24, 24), Image.NEAREST)
        output_24 = output_path.parent / f"{output_path.stem}_24x24{output_path.suffix}"
        quantized_24.save(output_24)

        # Check final stats
        arr = np.array(quantized_24)
        final_colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        print(f"   ✅ Saved  24x24: {output_24} ({final_colors} colors)")

    print(f"   🎉 Done!")
    return quantized_512

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Bespoke Punk pixel art")
    parser.add_argument("--prompt", type=str, required=True, help="Image description")
    parser.add_argument("--negative", type=str, default=None, help="Negative prompt")
    parser.add_argument("--output", type=str, default="output.png", help="Output path")
    parser.add_argument("--colors", type=int, default=15, help="Number of colors (default: 15)")
    parser.add_argument("--no-24x24", action="store_true", help="Skip 24x24 version")

    args = parser.parse_args()

    generate_bespoke_punk(
        prompt=args.prompt,
        negative_prompt=args.negative,
        output_path=args.output,
        generate_24x24=not args.no_24x24,
        n_colors=args.colors
    )
