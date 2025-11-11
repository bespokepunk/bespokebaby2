#!/usr/bin/env python3
"""
Test 256px training - Epochs 1-3 (while 4-8 finish training)
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
from collections import Counter

# Test prompts (same as CAPTION_FIX for comparison)
TEST_PROMPTS = [
    ("green_bg_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium male skin tone, bright green background, hard color borders, sharp pixel edges"),
    ("brown_eyes_lady", "pixel art, 24x24, portrait of bespoke punk lady, dark brown eyes clearly distinct from lighter brown hair, pale female skin tone, gray background, hard color borders, sharp pixel edges"),
    ("golden_earrings", "pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, pale female skin tone, wearing large circular golden yellow drop earrings hanging from earlobes, teal blue background, hard color borders, sharp pixel edges"),
    ("sunglasses_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair behind sunglasses, brown eyes completely covered by sunglasses, medium male skin tone, wearing black rectangular stunner sunglasses with thin black plastic frames and thin temples behind ears, lenses completely cover eyes with white reflections, teal blue background, hard color borders, sharp pixel edges"),
    ("melon_lady", "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, brown eyes, light brown female skin tone, wearing large circular golden yellow drop earrings hanging from earlobes, soft green background, hard color borders, sharp pixel edges"),
    ("cash_lad", "pixel art, 24x24, portrait of bespoke punk lad, gray wavy hair, brown eyes, pale male skin tone, teal blue background, hard color borders, sharp pixel edges"),
    ("carbon_lad", "pixel art, 24x24, portrait of bespoke punk lad, black hair, brown eyes, pale male skin tone, wearing gray structured baseball cap with curved front brim covering top of head down to hairline with white small logo on front center, gray background, hard color borders, sharp pixel edges"),
]

EPOCHS = [1, 2, 3]

def count_unique_colors(img):
    """Count unique colors in PIL Image"""
    colors = img.getcolors(maxcolors=1000000)
    return len(colors) if colors else 0

def test_epoch(epoch_num, lora_path):
    """Test one epoch with all prompts"""
    print(f"\n{'='*60}")
    print(f"TESTING EPOCH {epoch_num}")
    print(f"{'='*60}\n")

    # Detect device (MPS for Mac, CUDA for GPU, CPU fallback)
    if torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
    elif torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
    else:
        device = "cpu"
        dtype = torch.float32

    print(f"Using device: {device}")

    # Load pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=dtype,
        safety_checker=None
    ).to(device)

    # Load LoRA
    pipe.load_lora_weights(lora_path)

    output_dir = f"test_outputs_256px_epoch{epoch_num}"
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for prompt_name, prompt in TEST_PROMPTS:
        print(f"  Testing: {prompt_name}...")

        # Generate 24x24
        img = pipe(
            prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            width=24,
            height=24
        ).images[0]

        # Count colors
        colors = count_unique_colors(img)

        # Save
        save_path = os.path.join(output_dir, f"{prompt_name}_epoch{epoch_num}.png")
        img.save(save_path)

        results.append((prompt_name, colors))
        print(f"    ✓ {colors} colors")

    # Summary
    avg_colors = sum(c for _, c in results) / len(results)
    print(f"\n  Epoch {epoch_num} Average: {avg_colors:.1f} colors")

    # Cleanup
    del pipe
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    elif torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return results, avg_colors

def main():
    print("="*60)
    print("256PX TRAINING TEST - EPOCHS 1-3")
    print("="*60)

    all_results = {}

    for epoch in EPOCHS:
        lora_path = f"/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora_256px-{epoch:06d}.safetensors"

        if not os.path.exists(lora_path):
            print(f"\nSkipping Epoch {epoch} (file not found)")
            continue

        results, avg = test_epoch(epoch, lora_path)
        all_results[epoch] = (results, avg)

    # Final summary
    print("\n" + "="*60)
    print("SUMMARY - 256PX EPOCHS 1-3")
    print("="*60)

    for epoch in EPOCHS:
        if epoch in all_results:
            _, avg = all_results[epoch]
            print(f"Epoch {epoch}: {avg:.1f} avg colors")

    # Compare with 512px Epoch 8 baseline
    print("\n" + "="*60)
    print("COMPARISON WITH 512PX EPOCH 8")
    print("="*60)
    print("512px Epoch 8 baseline: 216.6 avg colors")
    print("Target: <220 colors (cleaner than baseline)")
    print("\nLook for:")
    print("  ✓ Fewer stray pixels")
    print("  ✓ Cleaner accessories (hats, sunglasses)")
    print("  ✓ Better eye rendering")
    print("  ✓ Distinct feature colors")

    print("\nTest complete! Check outputs in test_outputs_256px_epoch1-3/")

if __name__ == "__main__":
    main()
