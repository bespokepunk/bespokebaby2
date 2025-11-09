#!/bin/bash
set -e  # Exit on any error

# CRITICAL: Set Hugging Face cache to use /workspace (50GB) instead of /root (10GB)
export HF_HOME=/workspace/.cache/huggingface
export TRANSFORMERS_CACHE=/workspace/.cache/huggingface
export HF_DATASETS_CACHE=/workspace/.cache/huggingface

echo "==================================================="
echo "RunPod V2.7 SDXL Training - Complete Setup"
echo "==================================================="
echo ""
echo "This script will:"
echo "1. Install Kohya SS training framework"
echo "2. Verify training data is present"
echo "3. Train V2.7 SDXL LoRA at 24x24 native resolution (10 epochs, ~2-3 hours)"
echo ""
echo "Expected output: 10 × ~228MB .safetensors files"
echo ""

# 1. Install Kohya SS
echo "=== Step 1/4: Installing Kohya SS ==="
cd /workspace
if [ ! -d "kohya_ss" ]; then
    echo "Cloning Kohya SS repository..."
    git clone https://github.com/bmaltais/kohya_ss.git
    cd kohya_ss
    echo "Running setup (this may take 5-10 minutes)..."
    bash setup.sh
else
    echo "Kohya SS already installed, skipping..."
    cd kohya_ss
fi

# 2. Verify training data
echo ""
echo "=== Step 2/4: Verifying Training Data ==="
if [ ! -d "/workspace/training_data" ]; then
    echo "ERROR: Training data not found!"
    echo "Expected location: /workspace/training_data"
    echo ""
    echo "Please unzip bespoke_punks_v2_7_training.zip first:"
    echo "  cd /workspace"
    echo "  unzip bespoke_punks_v2_7_training.zip"
    echo ""
    exit 1
fi

IMAGE_COUNT=$(find /workspace/training_data -name "*.png" | wc -l)
CAPTION_COUNT=$(find /workspace/training_data -name "*.txt" | wc -l)

echo "Found ${IMAGE_COUNT} images and ${CAPTION_COUNT} captions"

if [ "$IMAGE_COUNT" -lt 200 ] || [ "$CAPTION_COUNT" -lt 200 ]; then
    echo "ERROR: Insufficient training data!"
    echo "Expected: 204 images + 204 captions"
    exit 1
fi

echo "Training data verified! ✓"

# 3. Create output directory
echo ""
echo "=== Step 3/4: Creating Output Directory ==="
mkdir -p /workspace/output
echo "Output directory ready: /workspace/output"

# 4. Install dependencies and start training
echo ""
echo "=== Step 4/4: Installing Dependencies & Starting Training ==="
echo "Resolution: 24x24 (native pixel art)"
echo "Base Model: SDXL"
echo "Epochs: 10"
echo "Expected Duration: 2-3 hours"
echo ""
echo "Training started at: $(date)"
echo ""

# Fix numpy version conflict FIRST
pip install --upgrade "numpy<2.0"

# Install from Kohya's requirements file
cd /workspace/kohya_ss
pip install -r requirements.txt

echo ""
echo "=== Dependencies Installed, Starting Training ==="
echo ""

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run training
python3 sd-scripts/train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="/workspace/training_data" \
  --resolution="24,24" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_punks_v2_7_sdxl_24x24" \
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

echo ""
echo "==================================================="
echo "Training Complete!"
echo "==================================================="
echo "Completed at: $(date)"
echo ""
echo "Output models saved to: /workspace/output/"
echo ""
ls -lh /workspace/output/*.safetensors
echo ""
echo "Expected: 10 files × ~228MB each"
echo ""
