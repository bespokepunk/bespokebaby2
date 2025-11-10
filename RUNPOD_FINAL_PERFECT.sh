#!/bin/bash
set -e

echo "=============================================="
echo "BESPOKE PUNKS - FINAL PERFECT TRAINING"
echo "With corrected hex codes & accurate captions"
echo "=============================================="
echo ""

# CRITICAL: Set Hugging Face cache to /workspace (50GB) not /root (10GB)
export HF_HOME=/workspace/.cache/huggingface
export TRANSFORMERS_CACHE=/workspace/.cache/huggingface
export HF_DATASETS_CACHE=/workspace/.cache/huggingface
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

cd /workspace

# ====================
# STEP 1: SETUP KOHYA_SS
# ====================
echo "=== STEP 1: Installing Kohya SS ==="
if [ ! -d "kohya_ss" ]; then
    git clone --recurse-submodules https://github.com/bmaltais/kohya_ss.git
else
    echo "Kohya SS already exists, skipping clone"
fi

cd kohya_ss

# Ensure submodules are initialized
if [ ! -f "sd-scripts/train_network.py" ]; then
    git submodule update --init --recursive
fi

# ====================
# STEP 2: INSTALL DEPENDENCIES
# ====================
echo ""
echo "=== STEP 2: Installing Dependencies ==="

# Install from Kohya's requirements (has all correct versions)
pip install -r requirements.txt

# Add any additional packages that might be missing
pip install opencv-python 2>/dev/null || true
pip install wandb 2>/dev/null || true

echo "✓ All dependencies installed!"

# ====================
# STEP 3: EXTRACT TRAINING DATA
# ====================
echo ""
echo "=== STEP 3: Extracting Training Data ==="

cd /workspace

# Remove old training data if exists
if [ -d "training_data" ]; then
    echo "Removing old training_data directory..."
    rm -rf training_data
fi

# Check if zip file exists
if [ ! -f "civitai_v2_7_training.zip" ]; then
    echo "ERROR: civitai_v2_7_training.zip not found!"
    echo "Please upload it to /workspace/ first"
    echo ""
    echo "To create the zip file locally, run:"
    echo "  cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2"
    echo "  zip -r civitai_v2_7_training.zip civitai_v2_7_training/"
    exit 1
fi

# Unzip training data
echo "Unzipping training data..."
unzip -q civitai_v2_7_training.zip

# Check if we need to move files
if [ -d "civitai_v2_7_training" ]; then
    mv civitai_v2_7_training training_data
else
    echo "ERROR: Expected civitai_v2_7_training folder in zip"
    exit 1
fi

# ====================
# STEP 4: VERIFY TRAINING DATA
# ====================
echo ""
echo "=== STEP 4: Verifying Training Data ==="

IMAGE_COUNT=$(find /workspace/training_data -name "*.png" | wc -l)
CAPTION_COUNT=$(find /workspace/training_data -name "*.txt" | wc -l)

echo "Images found: ${IMAGE_COUNT}"
echo "Captions found: ${CAPTION_COUNT}"

if [ "$IMAGE_COUNT" -ne 203 ]; then
    echo "ERROR: Found ${IMAGE_COUNT} images (expected 203)"
    echo "Contents of /workspace/training_data:"
    ls -la /workspace/training_data | head -20
    exit 1
fi

if [ "$CAPTION_COUNT" -ne 203 ]; then
    echo "ERROR: Found ${CAPTION_COUNT} captions (expected 203)"
    exit 1
fi

echo "✓ Training data verified - 203 images + 203 captions!"

# Show sample captions
echo ""
echo "Sample caption (first 200 chars):"
head -c 200 /workspace/training_data/lad_001_carbon.txt
echo ""
echo ""

# Create output directory
mkdir -p /workspace/output

# ====================
# STEP 5: START TRAINING
# ====================
echo ""
echo "=== STEP 5: Starting Training ==="
echo "Resolution: 512x512 (images are 576x576, will be center-cropped)"
echo "Base Model: SDXL"
echo "Network Rank: 32"
echo "Epochs: 10 (saves every epoch)"
echo "Expected Duration: 2-3 hours on RTX 4090"
echo "Training started at: $(date)"
echo ""
echo "KEY FIX: This training uses CORRECTED hex codes!"
echo "  - Brown eyes now have brown hex codes (not background colors)"
echo "  - All regions sampled from actual pixels"
echo "  - Brown eyes should render correctly now!"
echo ""

cd /workspace/kohya_ss

python3 sd-scripts/train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="/workspace/training_data" \
  --resolution="512,512" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_punks_PERFECT" \
  --save_model_as=safetensors \
  --max_train_epochs=10 \
  --learning_rate=0.0001 \
  --unet_lr=0.0001 \
  --text_encoder_lr=0.00005 \
  --network_module=networks.lora \
  --network_dim=32 \
  --network_alpha=16 \
  --save_every_n_epochs=1 \
  --mixed_precision="fp16" \
  --cache_latents \
  --cache_latents_to_disk \
  --optimizer_type="AdamW8bit" \
  --caption_extension=".txt" \
  --lr_scheduler="cosine_with_restarts" \
  --lr_scheduler_num_cycles=3 \
  --min_snr_gamma=5 \
  --noise_offset=0.1 \
  --clip_skip=2 \
  --train_batch_size=4 \
  --gradient_checkpointing \
  --xformers \
  --seed=42

# ====================
# STEP 6: COMPLETE
# ====================
echo ""
echo "=============================================="
echo "✓ TRAINING COMPLETE!"
echo "=============================================="
echo "Completed at: $(date)"
echo ""
echo "Output models:"
ls -lh /workspace/output/*.safetensors 2>/dev/null || echo "No models found - training may have failed"
echo ""
echo "Models saved as: bespoke_punks_PERFECT-000001.safetensors through bespoke_punks_PERFECT-000010.safetensors"
echo ""
echo "TEST PROMPTS to verify brown eyes work:"
echo "  1. 'portrait of bespoke punk lad, dark brown eyes, medium skin'"
echo "  2. 'portrait of bespoke punk lady, brown eyes, pink lips'"
echo ""
echo "Download the .safetensors files to test!"
echo "Recommended: Test epoch 5, 8, and 10"
echo ""
