#!/usr/bin/env python3
"""
Test IMPROVED model Epoch 2 - Enhanced Expression & Hairstyle Captions
Tests if improved caption descriptions boost detection accuracy
"""

import torch
from diffusers import StableDiffusionPipeline
import os

# Model path
MODEL_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_IMPROVED-000002.safetensors"
BASE_MODEL = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = "test_outputs/IMPROVED_epoch2"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("TESTING: IMPROVED Model - Epoch 2")
print("=" * 80)
print(f"Model: {MODEL_PATH}")
print(f"Base: {BASE_MODEL}")
print(f"Output: {OUTPUT_DIR}")
print()

# Load pipeline
print("Loading pipeline...")
pipe = StableDiffusionPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    safety_checker=None
).to("mps")

# Load LoRA weights
print(f"Loading LoRA: {MODEL_PATH}")
pipe.load_lora_weights(MODEL_PATH)
print("✓ Model loaded\n")

# Test prompts focusing on improved features
test_prompts = [
    # Expression tests (improved captions: "mouth corners turned up", "mouth in straight neutral line")
    {
        "name": "expression_smile",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, mouth corners turned up in gentle slight smile, green background",
        "test": "Testing improved smile description"
    },
    {
        "name": "expression_neutral",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, brown hair, mouth in straight neutral line with relaxed expression, blue background",
        "test": "Testing improved neutral expression description"
    },
    {
        "name": "expression_lips_curved",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, red hair, lips curved upward in subtle smile expression, purple background",
        "test": "Testing improved smile variation"
    },
    {
        "name": "expression_calm_closed_mouth",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, black hair, calm neutral expression with closed relaxed mouth, green background",
        "test": "Testing improved calm expression"
    },

    # Hairstyle tests (improved captions: detailed texture descriptions)
    {
        "name": "hair_curly_detailed",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, tightly coiled curly textured hair with high volume, slight smile, green background",
        "test": "Testing improved curly hair description"
    },
    {
        "name": "hair_wavy_detailed",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, gently wavy hair with soft flowing waves, neutral expression, blue background",
        "test": "Testing improved wavy hair description"
    },
    {
        "name": "hair_straight_detailed",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, sleek straight hair hanging smoothly down, slight smile, purple background",
        "test": "Testing improved straight hair description"
    },
    {
        "name": "hair_braids_detailed",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, hair in two distinct braids with visible woven pattern, neutral expression, green background",
        "test": "Testing improved braids description"
    },

    # Combined tests (expression + hairstyle)
    {
        "name": "combined_curly_smile",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, tightly coiled curly textured hair with high volume, mouth corners turned up in gentle slight smile, green background",
        "test": "Testing curly hair + smile"
    },
    {
        "name": "combined_straight_neutral",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, sleek straight hair hanging smoothly down, mouth in straight neutral line with relaxed expression, blue background",
        "test": "Testing straight hair + neutral expression"
    },
    {
        "name": "combined_braids_smile",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, hair in two distinct braids with visible woven pattern, lips curved upward in subtle smile expression, purple background",
        "test": "Testing braids + smile"
    },

    # Baseline tests (simple descriptions like training had before)
    {
        "name": "baseline_simple_smile",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, blonde hair, slight smile, green background",
        "test": "Baseline: simple smile (old caption style)"
    },
    {
        "name": "baseline_simple_neutral",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, brown hair, neutral expression, blue background",
        "test": "Baseline: simple neutral (old caption style)"
    },
    {
        "name": "baseline_simple_curly",
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, curly hair, slight smile, purple background",
        "test": "Baseline: simple curly (old caption style)"
    },
]

# Generate images
print("Generating test images...")
print("=" * 80)

for i, test in enumerate(test_prompts, 1):
    print(f"\n[{i}/{len(test_prompts)}] {test['name']}")
    print(f"Test: {test['test']}")
    print(f"Prompt: {test['prompt']}")

    image = pipe(
        test['prompt'],
        num_inference_steps=30,
        guidance_scale=7.5,
        height=512,
        width=512
    ).images[0]

    output_path = f"{OUTPUT_DIR}/{i:02d}_{test['name']}.png"
    image.save(output_path)
    print(f"✓ Saved: {output_path}")

print("\n" + "=" * 80)
print("GENERATION COMPLETE")
print("=" * 80)
print(f"\nAll images saved to: {OUTPUT_DIR}/")
print("\nNext steps:")
print("1. Visually inspect images for:")
print("   - Expression accuracy (smiles vs neutral)")
print("   - Hairstyle texture (curly, wavy, straight, braids)")
print("2. Compare detailed prompts vs baseline simple prompts")
print("3. Wait for epochs 4, 6, 8, 10 and compare improvements")
print("\nExpected improvements:")
print("- Expression: 50.2% → 70%+ (better mouth shape understanding)")
print("- Hairstyle: 28.9% → 70%+ (better texture understanding)")
