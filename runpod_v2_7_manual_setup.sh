#!/bin/bash
set -e  # Exit on any error

# CRITICAL: Set Hugging Face cache to use /workspace (50GB) instead of /root (10GB)
export HF_HOME=/workspace/.cache/huggingface
export TRANSFORMERS_CACHE=/workspace/.cache/huggingface
export HF_DATASETS_CACHE=/workspace/.cache/huggingface

echo "==================================================="
echo "RunPod V2.7 SDXL Training - Manual Setup"
echo "==================================================="
echo ""

# 1. Clone and setup Kohya SS manually
echo "=== Step 1/3: Installing Kohya SS ==="
cd /workspace

if [ ! -d "kohya_ss" ]; then
    echo "Cloning Kohya SS repository..."
    git clone --recurse-submodules https://github.com/bmaltais/kohya_ss.git
fi

cd kohya_ss

# Initialize submodules if needed
if [ ! -f "sd-scripts/train_network.py" ]; then
    echo "Initializing sd-scripts submodule..."
    git submodule update --init --recursive
fi

# 2. Verify training data
echo ""
echo "=== Step 2/3: Verifying Training Data ==="
if [ ! -d "/workspace/training_data" ]; then
    echo "ERROR: Training data not found!"
    echo "Run: cd /workspace && unzip bespoke_punks_v2_7_training.zip"
    exit 1
fi

IMAGE_COUNT=$(find /workspace/training_data -name "*.png" | wc -l)
CAPTION_COUNT=$(find /workspace/training_data -name "*.txt" | wc -l)

echo "Found ${IMAGE_COUNT} images and ${CAPTION_COUNT} captions"

if [ "$IMAGE_COUNT" -lt 200 ] || [ "$CAPTION_COUNT" -lt 200 ]; then
    echo "ERROR: Insufficient training data!"
    exit 1
fi

echo "Training data verified! ✓"

# 3. Create output directory
mkdir -p /workspace/output

# 4. Install dependencies and start training
echo ""
echo "=== Step 3/3: Installing Dependencies & Starting Training ==="
echo "Resolution: 24x24 (native pixel art)"
echo "Base Model: SDXL"
echo "Epochs: 10"
echo "Expected Duration: 2-3 hours"
echo ""

# Fix numpy version FIRST
pip install --upgrade "numpy<2.0"

# Install core dependencies (torch already installed, skip to avoid conflicts)
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install xformers compatible with PyTorch 2.x
pip install xformers
pip install bitsandbytes
pip install transformers==4.38.0
pip install diffusers[torch]==0.25.0
pip install accelerate==0.25.0
pip install safetensors==0.4.2
pip install huggingface-hub==0.20.1
pip install tensorboard
pip install einops
pip install ftfy
pip install imagesize
pip install toml
pip install pytorch-lightning==1.9.0
pip install lion-pytorch
pip install lycoris_lora==2.2.0.post3
pip install prodigyopt

echo ""
echo "=== Dependencies Installed, Starting Training ==="
echo "Training started at: $(date)"
echo ""

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
ls -lh /workspace/output/*.safetensors
echo ""
