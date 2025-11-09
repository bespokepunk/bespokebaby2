#!/bin/bash
set -e

echo "=============================================="
echo "BESPOKE PUNKS V2.7 - SIMPLE RUNPOD TRAINING"
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
# STEP 2: INSTALL DEPENDENCIES FROM KOHYA'S REQUIREMENTS
# ====================
echo ""
echo "=== STEP 2: Installing Dependencies from Kohya's requirements.txt ==="

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
if [ ! -f "bespoke_punks_v2_7_CORRECT.zip" ]; then
    echo "ERROR: bespoke_punks_v2_7_CORRECT.zip not found!"
    echo "Please upload it to /workspace/ first"
    exit 1
fi

# Unzip directly to training_data
echo "Unzipping training data..."
mkdir -p training_data
unzip -q bespoke_punks_v2_7_CORRECT.zip -d training_data

# ====================
# STEP 4: VERIFY TRAINING DATA
# ====================
echo ""
echo "=== STEP 4: Verifying Training Data ==="

IMAGE_COUNT=$(find /workspace/training_data -name "*.png" | wc -l)
CAPTION_COUNT=$(find /workspace/training_data -name "*.txt" | wc -l)

echo "Images found: ${IMAGE_COUNT}"
echo "Captions found: ${CAPTION_COUNT}"

if [ "$IMAGE_COUNT" -lt 200 ]; then
    echo "ERROR: Only found ${IMAGE_COUNT} images (expected 200+)"
    echo "Contents of /workspace/training_data:"
    ls -la /workspace/training_data | head -20
    exit 1
fi

if [ "$CAPTION_COUNT" -lt 200 ]; then
    echo "ERROR: Only found ${CAPTION_COUNT} captions (expected 200+)"
    exit 1
fi

echo "✓ Training data verified!"

# Show sample files
echo ""
echo "Sample training files:"
ls /workspace/training_data/*.png | head -5
ls /workspace/training_data/*.txt | head -5

# Create output directory
mkdir -p /workspace/output

# ====================
# STEP 5: START TRAINING
# ====================
echo ""
echo "=== STEP 5: Starting Training ==="
echo "Resolution: 24x24 (native pixel art)"
echo "Base Model: SDXL"
echo "Epochs: 10"
echo "Expected Duration: 2-3 hours on RTX 4090"
echo "Training started at: $(date)"
echo ""

cd /workspace/kohya_ss

python3 sd-scripts/train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="/workspace/training_data" \
  --resolution="24,24" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_punks_v2_7" \
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
  --optimizer_type="AdamW8bit" \
  --caption_extension=".txt" \
  --lr_scheduler="cosine_with_restarts" \
  --lr_scheduler_num_cycles=3 \
  --min_snr_gamma=5 \
  --noise_offset=0.1 \
  --clip_skip=2 \
  --train_batch_size=4 \
  --gradient_checkpointing \
  --xformers

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
echo "Download these .safetensors files to use your trained model!"
