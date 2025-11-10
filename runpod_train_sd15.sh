#!/bin/bash

echo "================================================"
echo "SD 1.5 LoRA Training - Bespoke Punks PERFECT"
echo "================================================"

# Install ALL dependencies for kohya_ss
echo "Installing all required dependencies..."
echo "This may take a few minutes..."

# Install everything kohya_ss needs in one go (don't exit on error for optional packages)
pip install -q --upgrade pip
pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -q xformers
pip install -q bitsandbytes
pip install -q accelerate transformers diffusers
pip install -q safetensors omegaconf pytorch_lightning einops
pip install -q hf_transfer huggingface-hub
pip install -q ftfy tensorboard altair toml voluptuous
pip install -q albumentations opencv-python imagesize timm
pip install -q lion-pytorch lycoris-lora dadaptation prodigyopt 2>/dev/null || echo "Optional optimizers skipped"

# Verify critical packages
echo "Verifying critical installations..."
python3 -c "import torch; print('✓ torch installed')" || { echo "ERROR: torch failed"; exit 1; }
python3 -c "import xformers; print('✓ xformers installed')" || { echo "ERROR: xformers failed"; exit 1; }
python3 -c "import bitsandbytes; print('✓ bitsandbytes installed')" || { echo "ERROR: bitsandbytes failed"; exit 1; }
python3 -c "import accelerate; print('✓ accelerate installed')" || { echo "ERROR: accelerate failed"; exit 1; }

echo "✓ All dependencies installed successfully!"

# Check GPU availability
echo "Checking GPU..."
nvidia-smi || { echo "WARNING: No GPU detected. Training will be slow!"; }

# Setup directories
echo "Setting up directories..."
mkdir -p /workspace/models
mkdir -p /workspace/output
mkdir -p /workspace/training_data
mkdir -p /workspace/reg_data

# Check if model exists, if not download it
MODEL_PATH="/workspace/models/sd15_base.safetensors"
if [ ! -f "$MODEL_PATH" ]; then
    echo "Model not found. Downloading SD 1.5 base model..."
    cd /workspace/models
    wget -q --show-progress https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors -O sd15_base.safetensors
    echo "Model downloaded successfully!"
else
    echo "Model found at $MODEL_PATH"
fi

# Check training data
TRAIN_COUNT=$(find /workspace/training_data -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) 2>/dev/null | wc -l)
echo "Found $TRAIN_COUNT training images"

if [ "$TRAIN_COUNT" -eq 0 ]; then
    echo "ERROR: No training images found in /workspace/training_data"
    echo "Please upload your images first!"
    exit 1
fi

# Check regularization data
REG_COUNT=$(find /workspace/reg_data -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) 2>/dev/null | wc -l)
echo "Found $REG_COUNT regularization images"

if [ "$REG_COUNT" -eq 0 ]; then
    echo "WARNING: No regularization images found. Training without reg data..."
    REG_ARG=""
else
    REG_ARG="--reg_data_dir=/workspace/reg_data"
fi

# Check kohya_ss installation
if [ ! -d "/workspace/kohya_ss" ]; then
    echo "ERROR: kohya_ss not found at /workspace/kohya_ss"
    echo "Please install kohya_ss first!"
    exit 1
fi

if [ ! -f "/workspace/kohya_ss/sd-scripts/train_network.py" ]; then
    echo "ERROR: Training script not found at /workspace/kohya_ss/sd-scripts/train_network.py"
    echo "Please check your kohya_ss installation!"
    exit 1
fi

# Navigate to kohya_ss directory
cd /workspace/kohya_ss

echo "================================================"
echo "Starting SD 1.5 training..."
echo "================================================"
echo "Configuration:"
echo "  - Model: SD 1.5 (not SDXL!)"
echo "  - Training images: $TRAIN_COUNT"
echo "  - Reg images: $REG_COUNT"
echo "  - Resolution: 512x512"
echo "  - Output: /workspace/output"
echo "  - Epochs: 10"
echo "  - Batch size: 4"
echo "================================================"

# Run training
set -e  # Exit on error for training
accelerate launch --num_cpu_threads_per_process=2 "./sd-scripts/train_network.py" \
    --pretrained_model_name_or_path="$MODEL_PATH" \
    --train_data_dir="/workspace/training_data" \
    $REG_ARG \
    --resolution="512,512" \
    --output_dir="/workspace/output" \
    --output_name="bespoke_punks_SD15_PERFECT" \
    --save_model_as=safetensors \
    --prior_loss_weight=1.0 \
    --max_train_epochs=10 \
    --learning_rate=0.0001 \
    --unet_lr=0.0001 \
    --text_encoder_lr=0.00005 \
    --lr_scheduler="cosine_with_restarts" \
    --lr_scheduler_num_cycles=3 \
    --network_module=networks.lora \
    --network_dim=32 \
    --network_alpha=16 \
    --save_every_n_epochs=1 \
    --mixed_precision="fp16" \
    --save_precision="fp16" \
    --cache_latents \
    --cache_latents_to_disk \
    --optimizer_type="AdamW8bit" \
    --max_data_loader_n_workers=1 \
    --bucket_reso_steps=64 \
    --xformers \
    --bucket_no_upscale \
    --noise_offset=0.1 \
    --multires_noise_iterations=6 \
    --multires_noise_discount=0.3 \
    --adaptive_noise_scale=0.00357 \
    --train_batch_size=4 \
    --gradient_checkpointing \
    --gradient_accumulation_steps=1 \
    --min_snr_gamma=5 \
    --caption_extension=".txt" \
    --shuffle_caption \
    --keep_tokens=2 \
    --max_token_length=225 \
    --seed=42

TRAINING_EXIT_CODE=$?

if [ $TRAINING_EXIT_CODE -eq 0 ]; then
    echo "================================================"
    echo "✓ Training completed successfully!"
    echo "================================================"
    echo "Output location: /workspace/output"
    echo ""
    echo "Generated files:"
    ls -lh /workspace/output/*.safetensors 2>/dev/null || echo "No .safetensors files found"
    echo ""
    echo "To download your LoRA, check /workspace/output/bespoke_punks_SD15_PERFECT*.safetensors"
else
    echo "================================================"
    echo "✗ Training failed with exit code $TRAINING_EXIT_CODE"
    echo "================================================"
    echo "Check the error messages above for details."
    exit $TRAINING_EXIT_CODE
fi
