#!/bin/bash

echo "=== V2.7 RunPod Training - SDXL Base Model ==="
echo "Training with 204 images + V2.7 enhanced captions"
echo "Using SDXL (NOT SD 1.5) to match CivitAI success"
echo ""

cd /workspace/kohya_ss
source venv/bin/activate

echo "Checking critical packages:"
pip list | grep -E "torch|diffusers|transformers|accelerate|safetensors"

echo ""
echo "=== Starting V2.7 SDXL Training ==="
echo "Expected duration: ~2-3 hours for 10 epochs"
echo ""

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
echo "=== Training Complete ==="
echo "Models saved to: /workspace/output/"
echo "Download all 10 epoch .safetensors files"
echo ""
echo "Expected files:"
echo "  bespoke_punks_v2_7_sdxl-000001.safetensors (Epoch 1)"
echo "  bespoke_punks_v2_7_sdxl-000002.safetensors (Epoch 2)"
echo "  ..."
echo "  bespoke_punks_v2_7_sdxl-000010.safetensors (Epoch 10)"
