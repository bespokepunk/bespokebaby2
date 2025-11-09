#!/bin/bash
set -e  # Exit on any error

# CRITICAL: Set Hugging Face cache to use /workspace (50GB) instead of /root (10GB)
export HF_HOME=/workspace/.cache/huggingface
export TRANSFORMERS_CACHE=/workspace/.cache/huggingface
export HF_DATASETS_CACHE=/workspace/.cache/huggingface

echo "=== Installing Dependencies ==="

# Fix numpy version conflict FIRST
pip install --upgrade "numpy<2.0"

# Install from Kohya's requirements file (has everything we need)
cd /workspace/kohya_ss
pip install -r requirements.txt

echo ""
echo "=== Dependencies Installed ==="
echo ""

# Create output directory
mkdir -p /workspace/output

echo "=== Starting Training ==="
echo "Resolution: 24x24 (native pixel art)"
echo "Base Model: SDXL"
echo "Epochs: 10"
echo "Expected Duration: 2-3 hours"
echo ""

# Run training
python3 sd-scripts/train_network.py --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" --train_data_dir="/workspace/training_data" --resolution="24,24" --output_dir="/workspace/output" --output_name="bespoke_punks_v2_7_sdxl_24x24" --save_model_as=safetensors --max_train_epochs=10 --learning_rate=0.0001 --unet_lr=0.0001 --text_encoder_lr=0.00005 --network_module=networks.lora --network_dim=32 --network_alpha=16 --save_every_n_epochs=1 --mixed_precision="fp16" --cache_latents --optimizer_type="AdamW8bit" --caption_extension=".txt" --lr_scheduler="cosine_with_restarts" --lr_scheduler_num_cycles=3 --min_snr_gamma=5 --noise_offset=0.1 --clip_skip=2 --train_batch_size=4 --gradient_checkpointing --xformers

echo ""
echo "=== Training Complete ==="
echo "Models saved to: /workspace/output/"
ls -lh /workspace/output/*.safetensors
