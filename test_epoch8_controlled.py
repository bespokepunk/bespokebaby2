#!/usr/bin/env python3
"""
SCIENTIFIC VALIDATION OF EPOCH 8
Tests: Quality, Control, Predictability, Reproducibility

This script runs controlled experiments to validate Epoch 8 model performance.
"""

import torch
from diffusers import StableDiffusionPipeline
import os
from datetime import datetime

# Configuration
MODEL_PATH = "lora_checkpoints/caption_fix/caption_fix_epoch8.safetensors"
BASE_MODEL = "runwayml/stable-diffusion-v1-5"
OUTPUT_DIR = f"epoch8_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("EPOCH 8 SCIENTIFIC VALIDATION")
print("=" * 80)
print(f"Model: {MODEL_PATH}")
print(f"Output: {OUTPUT_DIR}/")
print()

# Load model
print("Loading Stable Diffusion + Epoch 8 LoRA...")
pipe = StableDiffusionPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    safety_checker=None
).to("mps")

pipe.load_lora_weights(MODEL_PATH)
print("✓ Model loaded\n")

# ============================================================================
# TEST 1: REPRODUCIBILITY - Same seed should produce identical results
# ============================================================================

print("=" * 80)
print("TEST 1: REPRODUCIBILITY")
print("=" * 80)
print("Testing if same seed produces identical outputs...\n")

test_prompt = "pixel art, 24x24, portrait of bespoke punk lady, brown hair, green eyes, neutral expression, blue background"
test_seed = 42

print(f"Prompt: {test_prompt}")
print(f"Seed: {test_seed}\n")

# Generate twice with same seed
for attempt in [1, 2]:
    print(f"Attempt {attempt}...")
    image = pipe(
        test_prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        height=512,
        width=512,
        generator=torch.Generator("mps").manual_seed(test_seed)
    ).images[0]

    image.save(f"{OUTPUT_DIR}/reproducibility_attempt{attempt}.png")
    print(f"  ✓ Saved")

print("\n✅ Check {OUTPUT_DIR}/ - both images should be IDENTICAL\n")

# ============================================================================
# TEST 2: FEATURE CONTROL - Can we control specific features?
# ============================================================================

print("=" * 80)
print("TEST 2: FEATURE CONTROL")
print("=" * 80)
print("Testing ability to control individual features...\n")

# Test different hair colors (most reliable feature)
hair_tests = [
    ("blonde", "Blonde lady with blue background"),
    ("brown", "Brown-haired lady with blue background"),
    ("black", "Black-haired lady with blue background"),
    ("red", "Red-haired lady with blue background"),
]

for hair_color, description in hair_tests:
    prompt = f"pixel art, 24x24, portrait of bespoke punk lady, {hair_color} hair, green eyes, blue background"
    print(f"Testing: {description}")
    print(f"  Prompt: {prompt}")

    image = pipe(
        prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        height=512,
        width=512,
        generator=torch.Generator("mps").manual_seed(123)
    ).images[0]

    filename = f"control_hair_{hair_color}.png"
    image.save(f"{OUTPUT_DIR}/{filename}")
    print(f"  ✓ Saved: {filename}\n")

# Test different backgrounds (also reliable)
bg_tests = [
    ("blue", "Lady on blue background"),
    ("green", "Lady on green background"),
    ("purple", "Lady on purple background"),
]

for bg_color, description in bg_tests:
    prompt = f"pixel art, 24x24, portrait of bespoke punk lady, brown hair, green eyes, {bg_color} background"
    print(f"Testing: {description}")
    print(f"  Prompt: {prompt}")

    image = pipe(
        prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        height=512,
        width=512,
        generator=torch.Generator("mps").manual_seed(456)
    ).images[0]

    filename = f"control_background_{bg_color}.png"
    image.save(f"{OUTPUT_DIR}/{filename}")
    print(f"  ✓ Saved: {filename}\n")

print("✅ Review {OUTPUT_DIR}/ to verify feature control\n")

# ============================================================================
# TEST 3: QUALITY - Visual pixel art quality assessment
# ============================================================================

print("=" * 80)
print("TEST 3: QUALITY ASSESSMENT")
print("=" * 80)
print("Generating diverse samples for quality review...\n")

quality_tests = [
    ("lady, blonde hair, blue eyes, green background", "quality_lady_1"),
    ("lad, brown hair, brown eyes, blue background", "quality_lad_1"),
    ("lady, black hair, green eyes, purple background", "quality_lady_2"),
    ("lad, gray hair, brown eyes, green background", "quality_lad_2"),
]

for i, (features, filename) in enumerate(quality_tests, 1):
    prompt = f"pixel art, 24x24, portrait of bespoke punk {features}"
    print(f"Sample {i}: {features}")

    image = pipe(
        prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        height=512,
        width=512,
        generator=torch.Generator("mps").manual_seed(100 + i)
    ).images[0]

    image.save(f"{OUTPUT_DIR}/{filename}.png")
    print(f"  ✓ Saved: {filename}.png\n")

print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
print(f"\nResults saved to: {OUTPUT_DIR}/")
print("\nNEXT STEPS:")
print("1. Review reproducibility images - should be identical")
print("2. Check feature control - hair/background colors should match prompts")
print("3. Assess quality samples - clean pixel art, production-ready?")
print("\nIf all tests pass → Epoch 8 is production-ready! 🚀")
print()
