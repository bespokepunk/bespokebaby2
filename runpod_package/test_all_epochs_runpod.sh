#!/bin/bash
# RunPod SDXL LoRA Testing - Complete Setup & Execution
# Run this on RunPod to test all SDXL epoch checkpoints
set -e

echo "=========================================="
echo "RunPod SDXL LoRA Testing - Full Setup"
echo "=========================================="
echo ""

# 1. Check training completed
echo "[1/5] Checking training outputs..."
cd /workspace

if [ ! -d "output" ]; then
    echo "ERROR: /workspace/output directory not found!"
    echo "Training may not have completed or directory was moved."
    exit 1
fi

checkpoint_count=$(find output -name "bespoke_baby_sdxl-*.safetensors" | wc -l)
echo "Found $checkpoint_count checkpoint files"

if [ "$checkpoint_count" -eq 0 ]; then
    echo "ERROR: No checkpoint files found!"
    exit 1
fi

echo "✓ Training output found"
echo ""

# List all checkpoints
echo "Available checkpoints:"
ls -lh output/bespoke_baby_sdxl-*.safetensors
echo ""

# 2. Install dependencies
echo "[2/5] Installing testing dependencies..."
pip install -q diffusers transformers accelerate safetensors peft 2>&1 | grep -v "already satisfied" || true
echo "✓ Dependencies ready"
echo ""

# 3. Create test script
echo "[3/5] Creating test script..."
cat > /workspace/test_sdxl_epochs.py << 'PYTHON_SCRIPT_END'
#!/usr/bin/env python3
"""
RunPod SDXL LoRA Testing Script - All Epochs
Optimized for CUDA GPU (fast generation)
"""
import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path
import time

print("=" * 70)
print("RunPod SDXL LoRA Testing - All Epochs")
print("=" * 70)
print()

# Which epochs to test (1-10)
epochs_to_test = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Test prompts - same as SD 1.5 for comparison
test_prompts = [
    {
        "prompt": "pixel art, 24x24, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render, blurry",
        "name": "01_bespoke_punk_green_bg"
    },
    {
        "prompt": "pixel art, 24x24, portrait of bespoke baby, pink solid background, brown hair, brown eyes, medium skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render, blurry",
        "name": "02_bespoke_baby_pink_bg"
    },
    {
        "prompt": "pixel art, 24x24, portrait of bespoke punk lad, blue solid background, blonde hair, green eyes, tan skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render, blurry",
        "name": "03_lad_blue_bg"
    },
    {
        "prompt": "pixel art, 24x24, portrait of bespoke punk lady, purple solid background, red hair, hazel eyes, pale skin",
        "negative": "full body, legs, multiple people, text, watermark, realistic, photographic, 3d render, blurry",
        "name": "04_lady_purple_bg"
    },
]

# SDXL generation parameters
gen_params = {
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 1024,  # SDXL native resolution
    "height": 1024,
}

# Load SDXL base model once
print("Loading SDXL base model (this may take a minute)...")
start_time = time.time()

pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16"
)

if torch.cuda.is_available():
    pipe = pipe.to("cuda")
    print(f"✓ Using CUDA GPU: {torch.cuda.get_device_name(0)}")
else:
    print("⚠ WARNING: CUDA not available, this will be very slow!")
    pipe = pipe.to("cpu")

load_time = time.time() - start_time
print(f"✓ Base model loaded in {load_time:.1f}s")
print()

# Test each epoch
total_start = time.time()

for epoch_num in epochs_to_test:
    epoch_start = time.time()

    print("=" * 70)
    print(f"Testing Epoch {epoch_num}/10")
    print("=" * 70)

    # LoRA path (epoch 10 is saved as final without number)
    if epoch_num == 10:
        lora_path = f"/workspace/output/bespoke_baby_sdxl.safetensors"
    else:
        lora_path = f"/workspace/output/bespoke_baby_sdxl-{epoch_num:06d}.safetensors"

    output_dir = Path(f"/workspace/test_outputs_sdxl_epoch{epoch_num}")
    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"LoRA: {lora_path}")
    print(f"Output: {output_dir}/")
    print()

    # Check if LoRA exists
    if not Path(lora_path).exists():
        print(f"⚠ Skipping - LoRA file not found")
        print()
        continue

    # Load LoRA
    try:
        pipe.load_lora_weights(lora_path)
        print("✓ LoRA loaded")
    except Exception as e:
        print(f"✗ Error loading LoRA: {e}")
        print()
        continue

    print()

    # Generate test images
    for i, test in enumerate(test_prompts, 1):
        img_start = time.time()
        print(f"[{i}/{len(test_prompts)}] Generating: {test['name']}")

        try:
            image = pipe(
                prompt=test["prompt"],
                negative_prompt=test["negative"],
                **gen_params
            ).images[0]

            output_path = output_dir / f"{test['name']}.png"
            image.save(output_path)

            img_time = time.time() - img_start
            print(f"  ✓ Saved in {img_time:.1f}s")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    epoch_time = time.time() - epoch_start
    print()
    print(f"✓ Epoch {epoch_num} complete in {epoch_time:.1f}s")
    print()

total_time = time.time() - total_start

print("=" * 70)
print("All Epochs Tested!")
print("=" * 70)
print()
print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
print()
print("Output directories:")
for epoch_num in epochs_to_test:
    output_dir = Path(f"/workspace/test_outputs_sdxl_epoch{epoch_num}")
    if output_dir.exists():
        img_count = len(list(output_dir.glob("*.png")))
        print(f"  - {output_dir}/ ({img_count} images)")
print()
print("Expected behavior:")
print("  ✓ Should produce PIXEL ART (not realistic photos)")
print("  ✓ Should look like 24x24 pixel art style")
print("  ✓ Compare with SD 1.5 results (realistic babies = failure)")
PYTHON_SCRIPT_END

chmod +x /workspace/test_sdxl_epochs.py
echo "✓ Test script created"
echo ""

# 4. Run testing
echo "[4/5] Running tests on all epochs..."
echo "This will take ~5-10 minutes with GPU"
echo ""
python3 /workspace/test_sdxl_epochs.py
echo ""

# 5. Package results
echo "[5/5] Packaging results..."
if [ -d "/workspace/test_outputs_sdxl_epoch1" ]; then
    cd /workspace
    zip -r -q sdxl_test_results.zip test_outputs_sdxl_epoch*

    file_size=$(du -h sdxl_test_results.zip | cut -f1)
    echo "✓ Results packaged: sdxl_test_results.zip ($file_size)"
    echo ""
    echo "=========================================="
    echo "TESTING COMPLETE!"
    echo "=========================================="
    echo ""
    echo "Download this file:"
    echo "  /workspace/sdxl_test_results.zip"
    echo ""
    echo "Contains test images for all 10 epochs"
    echo "(4 images per epoch = 40 total images)"
    echo ""
else
    echo "⚠ No test outputs found - check for errors above"
fi
