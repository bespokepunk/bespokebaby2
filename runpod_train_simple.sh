#!/bin/bash
set -e

# CRITICAL: Set Hugging Face cache to /workspace (50GB) instead of /root (10GB)
export HF_HOME=/workspace/.cache/huggingface
export TRANSFORMERS_CACHE=/workspace/.cache/huggingface
export HF_DATASETS_CACHE=/workspace/.cache/huggingface

echo "=== V2.7 SDXL Training at 24x24 Native Resolution ==="
echo ""

cd /workspace/kohya_ss

echo "Verifying training data..."
echo "Image count: $(find /workspace/training_data -name "*.png" | wc -l)"
echo "Caption count: $(find /workspace/training_data -name "*.txt" | wc -l)"
echo ""

mkdir -p /workspace/output

echo "Installing missing dependencies..."
pip install opencv-python > /dev/null 2>&1

echo "Starting training at: $(date)"
echo "Expected duration: ~2-3 hours for 10 epochs"
echo ""

python sd-scripts/train_network.py \
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
echo "=== Training Complete ==="
echo "Completed at: $(date)"
ls -lh /workspace/output/*.safetensors
