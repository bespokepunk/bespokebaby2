#!/bin/bash
set -e  # Exit immediately on any error

echo "=============================================="
echo "BESPOKE PUNKS V2.7 - COMPLETE RUNPOD TRAINING"
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
# STEP 2: INSTALL ALL DEPENDENCIES
# ====================
echo ""
echo "=== STEP 2: Installing ALL Dependencies (No More Missing Packages!) ==="

# Core PyTorch and CUDA dependencies FIRST (they will install compatible numpy)
pip install torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cu121

# Transformers and Diffusers ecosystem
pip install transformers==4.38.0
pip install diffusers[torch]==0.25.0
pip install accelerate==0.25.0
pip install safetensors==0.4.2
pip install huggingface-hub==0.20.1

# Training optimizations
pip install xformers
pip install bitsandbytes==0.41.1
pip install lion-pytorch
pip install prodigyopt
pip install pytorch-lightning==2.0.0
pip install lycoris_lora

# Image processing and utilities (opencv will install numpy>=2, we'll handle this)
pip install opencv-python
pip install imagesize
pip install albumentations
pip install einops
pip install omegaconf
pip install pillow

# Text and tokenization
pip install ftfy
pip install sentencepiece
pip install tokenizers

# Monitoring and visualization
pip install tensorboard
pip install wandb
pip install tqdm

# Configuration and data handling
pip install toml
pip install pyyaml
pip install scipy

# Additional dependencies that might be needed
pip install protobuf
pip install regex
pip install requests
pip install packaging
pip install filelock
pip install sympy
pip install mpmath

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
if [ ! -f "bespoke_punks_v2_7_training.zip" ]; then
    echo "ERROR: bespoke_punks_v2_7_training.zip not found!"
    echo "Please upload it to /workspace/ first"
    exit 1
fi

# Unzip to temporary location
echo "Unzipping training data..."
unzip -q bespoke_punks_v2_7_training.zip

# Find where the files actually extracted to and move them
if [ -d "FORTRAINING6/bespokepunks" ]; then
    echo "Moving files from FORTRAINING6/bespokepunks/ to training_data/"
    mv FORTRAINING6/bespokepunks training_data
    rm -rf FORTRAINING6
elif [ -d "civitai_v2_7_training" ]; then
    echo "Moving files from civitai_v2_7_training/ to training_data/"
    mv civitai_v2_7_training training_data
else
    # Files might be directly in current directory
    mkdir -p training_data
    echo "Moving .png and .txt files to training_data/"
    find . -maxdepth 1 -name "*.png" -exec mv {} training_data/ \;
    find . -maxdepth 1 -name "*.txt" ! -name "*.md" -exec mv {} training_data/ \;
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
ls -lh /workspace/output/*.safetensors
echo ""
echo "Download these .safetensors files to use your trained model!"
