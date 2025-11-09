#!/bin/bash

echo "=================================================="
echo "RunPod V2.7 SDXL Training - Complete Setup"
echo "=================================================="
echo ""
echo "This script will:"
echo "1. Install Kohya SS training framework"
echo "2. Verify training data is present"
echo "3. Train V2.7 SDXL LoRA (10 epochs, ~2-3 hours)"
echo ""
echo "Expected output: 10 × ~228MB .safetensors files"
echo ""

# Exit on any error
set -e

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
if [ ! -d "/workspace/FORTRAINING6/bespokepunks" ]; then
    echo "ERROR: Training data not found!"
    echo "Expected location: /workspace/FORTRAINING6/bespokepunks"
    echo ""
    echo "Please upload your training data first:"
    echo "  - 204 PNG files (24x24 pixel art)"
    echo "  - 204 TXT caption files"
    echo ""
    exit 1
fi

IMAGE_COUNT=$(find /workspace/FORTRAINING6/bespokepunks -name "*.png" | wc -l)
CAPTION_COUNT=$(find /workspace/FORTRAINING6/bespokepunks -name "*.txt" | wc -l)

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

# 4. Start training
echo ""
echo "=== Step 4/4: Starting V2.7 SDXL Training ==="
echo "Duration: ~2-3 hours"
echo "GPU: A100 (40GB)"
echo "Model: SDXL Base 1.0"
echo ""
echo "Training started at: $(date)"
echo ""

source venv/bin/activate

python sd-scripts/train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="/workspace/FORTRAINING6/bespokepunks" \
  --resolution="1024,1024" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_punks_v2_7_sdxl" \
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
echo "=================================================="
echo "Training Complete!"
echo "=================================================="
echo "Completed at: $(date)"
echo ""
echo "Output models saved to: /workspace/output/"
echo ""
ls -lh /workspace/output/*.safetensors
echo ""
echo "Download these files to your local machine:"
echo "  scp root@POD_IP:/workspace/output/*.safetensors ~/Documents/GitHub/bespokebaby2/models/runpod_v2_7_sdxl/"
echo ""
echo "Expected: 10 files × ~228MB each"
echo ""
