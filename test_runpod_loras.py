"""
Test RunPod-trained LoRAs at 512×512 and downscale to 24×24
"""

from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import os

# Paths
CHECKPOINT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/Context 1106"
OUTPUT_DIR = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_test_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test checkpoints
checkpoints = [
    "bespoke_punks_sd15_512-000001.safetensors",  # Epoch 1
    "bespoke_punks_sd15_512-000002.safetensors",  # Epoch 2
    "bespoke_punks_sd15_512.safetensors",         # Epoch 3 (final)
]

# Test prompts (variety of styles from training data)
test_prompts = [
    "pixel art, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin, sharp pixel edges",
    "pixel art, portrait of bespoke punk, red solid background, brown hair, brown eyes, tan skin, sharp pixel edges",
    "pixel art, portrait of bespoke punk, blue solid background, blonde hair, green eyes, pale skin, sharp pixel edges",
    "pixel art, portrait of bespoke punk, yellow solid background, white hair, purple eyes, dark skin, sharp pixel edges",
]

print("=" * 80)
print("Testing RunPod-Trained Bespoke Punks LoRAs (512×512 → 24×24)")
print("=" * 80)
print()

# Load base model
print("Loading SD 1.5 base model...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    safety_checker=None
)
pipe = pipe.to("mps")  # Use Mac GPU
print("✓ Base model loaded\n")

# Test each checkpoint
for checkpoint_name in checkpoints:
    checkpoint_path = os.path.join(CHECKPOINT_DIR, checkpoint_name)

    if not os.path.exists(checkpoint_path):
        print(f"⚠️  Skipping {checkpoint_name} - file not found")
        continue

    epoch_num = "epoch1" if "000001" in checkpoint_name else "epoch2" if "000002" in checkpoint_name else "epoch3"
    print(f"{'='*80}")
    print(f"Testing: {checkpoint_name} ({epoch_num.upper()})")
    print(f"{'='*80}")

    # Load LoRA weights
    print(f"Loading LoRA weights from {checkpoint_name}...")
    pipe.load_lora_weights(CHECKPOINT_DIR, weight_name=checkpoint_name)
    print("✓ LoRA loaded\n")

    # Generate images for each test prompt
    for i, prompt in enumerate(test_prompts, 1):
        print(f"  [{i}/{len(test_prompts)}] Generating: {prompt[:60]}...")

        # Generate at 512×512
        image_512 = pipe(
            prompt=prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            height=512,
            width=512,
        ).images[0]

        # Save 512×512 version
        output_512 = os.path.join(OUTPUT_DIR, f"{epoch_num}_prompt{i}_512x512.png")
        image_512.save(output_512)
        print(f"      ✓ Saved 512×512: {output_512}")

        # Downscale to 24×24 using different methods
        methods = {
            "NEAREST": Image.NEAREST,
            "LANCZOS": Image.LANCZOS,
            "BILINEAR": Image.BILINEAR,
        }

        for method_name, method in methods.items():
            image_24 = image_512.resize((24, 24), method)
            output_24 = os.path.join(OUTPUT_DIR, f"{epoch_num}_prompt{i}_24x24_{method_name}.png")
            image_24.save(output_24)
            print(f"      ✓ Saved 24×24 ({method_name}): {output_24}")

        print()

    # Unload LoRA before loading next one
    pipe.unload_lora_weights()
    print(f"✓ Completed testing {checkpoint_name}\n")

print("=" * 80)
print("✅ ALL TESTS COMPLETE!")
print("=" * 80)
print(f"\nResults saved to: {OUTPUT_DIR}")
print("\nGenerated files:")
print("  - 3 epochs × 4 prompts = 12 images at 512×512")
print("  - 12 images × 3 downscale methods = 36 images at 24×24")
print("  - Total: 48 images")
print("\nNext steps:")
print("  1. Review 512×512 images to see which epoch looks best")
print("  2. Compare 24×24 versions to original Bespoke Punks")
print("  3. Choose best epoch + downscale method for production")
