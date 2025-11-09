"""
Test Epoch 1 Checkpoint from Kohya SD 1.5 Training
Generates sample Bespoke Punk images to evaluate training progress
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import os

# Configuration
CHECKPOINT_PATH = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_output_sd15/bespoke_punks_sd15_24x24-000001.safetensors"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/epoch1_test_outputs"
BASE_MODEL = "runwayml/stable-diffusion-v1-5"

# Test prompts
TEST_PROMPTS = [
    "pixel art, 24x24, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin, sharp pixel edges",
    "pixel art, 24x24, portrait of bespoke punk, red solid background, brown hair, brown eyes, tan skin, sharp pixel edges",
    "pixel art, 24x24, portrait of bespoke punk, checkered pattern background, blonde hair, green eyes, light skin, sharp pixel edges",
    "pixel art, 24x24, portrait of bespoke punk, blue solid background, purple hair, black skin, sharp pixel edges",
]

NEGATIVE_PROMPT = "full body, body, legs, character sprite, game sprite, blurry, smooth, antialiased"

print("Loading SD 1.5 base model...")
pipe = StableDiffusionPipeline.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    safety_checker=None
)

print(f"Loading LoRA checkpoint: {CHECKPOINT_PATH}")
pipe.load_lora_weights(CHECKPOINT_PATH)

# Use MPS (Apple Silicon) if available
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")
pipe = pipe.to(device)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\nGenerating {len(TEST_PROMPTS)} test images...")
print("=" * 60)

for idx, prompt in enumerate(TEST_PROMPTS, 1):
    print(f"\n[{idx}/{len(TEST_PROMPTS)}] Generating: {prompt[:60]}...")

    # Generate at 24x24
    image = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE_PROMPT,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=24,
        height=24,
        generator=torch.manual_seed(42)
    ).images[0]

    # Save original 24x24
    output_path_24 = os.path.join(OUTPUT_DIR, f"epoch1_test_{idx}_24x24.png")
    image.save(output_path_24)

    # Also save upscaled version for easier viewing
    upscaled = image.resize((240, 240), Image.NEAREST)
    output_path_upscaled = os.path.join(OUTPUT_DIR, f"epoch1_test_{idx}_upscaled.png")
    upscaled.save(output_path_upscaled)

    print(f"   ✓ Saved: {output_path_24}")
    print(f"   ✓ Saved: {output_path_upscaled} (10x upscaled)")

print("\n" + "=" * 60)
print(f"✅ All test images saved to: {OUTPUT_DIR}")
print("\nCheck the results to see if Epoch 1 is learning the Bespoke Punk style!")
