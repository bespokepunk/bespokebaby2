#!/usr/bin/env python3
"""
Generate synthetic training data for classification model

Uses Epoch 4 SD model to generate 1000+ bespoke punks with known labels.
Creates balanced dataset for training expression & hairstyle classifier.
"""

import torch
from diffusers import StableDiffusionPipeline
import os
import json
from itertools import product

# Configuration
MODEL_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_IMPROVED-000004.safetensors"  # Epoch 4 (best quality)
BASE_MODEL = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = "synthetic_training_data"
TEST_MODE = True  # Set to True for 50-image test batch, False for full 720 images
IMAGES_PER_COMBINATION = 1 if TEST_MODE else 3  # 1 variant in test mode, 3 in full mode

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/images", exist_ok=True)

print("=" * 80)
print("SYNTHETIC TRAINING DATA GENERATOR")
print("=" * 80)
print(f"Model: Epoch 4 (best pixel art quality)")
print(f"Mode: {'TEST (50 images)' if TEST_MODE else 'FULL (720 images)'}")
print(f"Output: {OUTPUT_DIR}/")
print()

if TEST_MODE:
    print("⚠️  TEST MODE ENABLED")
    print("   Generating small batch for validation")
    print("   After validation, set TEST_MODE=False for full generation")
    print()

# Load model
print("Loading Stable Diffusion + LoRA...")
pipe = StableDiffusionPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    safety_checker=None
).to("mps")

pipe.load_lora_weights(MODEL_PATH)
print("✓ Model loaded\n")

# Define generation parameters
# We'll generate balanced dataset across all combinations

EXPRESSIONS = [
    {"label": "neutral", "prompt": "mouth in straight neutral line with relaxed expression"},
    {"label": "slight_smile", "prompt": "mouth corners turned up in gentle slight smile"},
]

HAIRSTYLES = [
    {"label": "straight", "prompt": "sleek straight hair hanging smoothly down"},
    {"label": "curly", "prompt": "tightly coiled curly textured hair with high volume"},
    {"label": "wavy", "prompt": "soft wavy hair with gentle flowing curves"},
]

GENDERS = ["lady", "lad"]

BACKGROUNDS = ["green", "blue", "purple", "yellow"]

HAIR_COLORS = [
    "blonde", "brown", "black", "red", "gray"
]

# Calculate total images
total_combinations = (
    len(EXPRESSIONS) *
    len(HAIRSTYLES) *
    len(GENDERS) *
    len(BACKGROUNDS) *
    len(HAIR_COLORS) *
    IMAGES_PER_COMBINATION
)

print(f"Generating {total_combinations} synthetic images:")
print(f"  - {len(EXPRESSIONS)} expressions")
print(f"  - {len(HAIRSTYLES)} hairstyles")
print(f"  - {len(GENDERS)} genders")
print(f"  - {len(BACKGROUNDS)} backgrounds")
print(f"  - {len(HAIR_COLORS)} hair colors")
print(f"  - {IMAGES_PER_COMBINATION} variants each")
print()

# Generate all combinations
labels_data = []
count = 0
max_images = 50 if TEST_MODE else 999999  # Limit to 50 in test mode

for expression in EXPRESSIONS:
    for hairstyle in HAIRSTYLES:
        for gender in GENDERS:
            for bg_color in BACKGROUNDS:
                for hair_color in HAIR_COLORS:
                    for variant in range(IMAGES_PER_COMBINATION):
                        if count >= max_images:
                            break
                        count += 1

                        # Construct prompt
                        prompt = (
                            f"pixel art, 24x24, portrait of bespoke punk {gender}, "
                            f"{hair_color} {hairstyle['prompt']}, "
                            f"{expression['prompt']}, "
                            f"{bg_color} background"
                        )

                        # Generate image
                        print(f"[{count}/{total_combinations}] {expression['label']}, {hairstyle['label']}, {hair_color}, {bg_color}")

                        image = pipe(
                            prompt,
                            num_inference_steps=30,
                            guidance_scale=7.5,
                            height=512,
                            width=512,
                            generator=torch.Generator("mps").manual_seed(count)  # Different seed each time
                        ).images[0]

                        # Save image
                        filename = f"synthetic_{count:05d}.png"
                        image_path = f"{OUTPUT_DIR}/images/{filename}"
                        image.save(image_path)

                        # Record labels
                        labels_data.append({
                            "filename": filename,
                            "expression": expression['label'],
                            "hairstyle": hairstyle['label'],
                            "gender": gender,
                            "background_color": bg_color,
                            "hair_color": hair_color,
                            "prompt": prompt
                        })

                        # Save labels incrementally (in case of crash)
                        if count % 50 == 0:
                            with open(f"{OUTPUT_DIR}/labels.json", 'w') as f:
                                json.dump(labels_data, f, indent=2)
                            print(f"  ✓ Checkpoint saved ({count}/{total_combinations})")

# Final save
with open(f"{OUTPUT_DIR}/labels.json", 'w') as f:
    json.dump(labels_data, f, indent=2)

print("\n" + "=" * 80)
print("GENERATION COMPLETE")
print("=" * 80)
print(f"Generated {count} images")
print(f"Images: {OUTPUT_DIR}/images/")
print(f"Labels: {OUTPUT_DIR}/labels.json")

if TEST_MODE:
    print("\n⚠️  TEST MODE - Small batch generated")
    print("\nNext steps:")
    print("  1. Run: python validate_synthetic_data.py")
    print("  2. If validation passes (>70% accuracy):")
    print("     - Set TEST_MODE=False in this script")
    print("     - Re-run to generate full 720 images")
    print("  3. If validation fails:")
    print("     - Try Epoch 6 model instead")
    print("     - Or simplify prompts")
else:
    print("\nNext step: python train_classifier.py")
