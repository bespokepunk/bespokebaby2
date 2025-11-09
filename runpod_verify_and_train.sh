#!/bin/bash

echo "=== Verifying Installation ==="
cd /workspace/kohya_ss
source venv/bin/activate

echo "Checking critical packages:"
pip list | grep -E "torch|diffusers|transformers|accelerate|safetensors"

echo ""
echo "=== Starting V2.7 Training ==="
echo "Training with 204 images + V2.7 enhanced captions"
echo "Expected duration: ~30-60 minutes for 5 epochs"
echo ""

python sd-scripts/train_network.py \
  --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
  --train_data_dir="/workspace/FORTRAINING6/bespokepunks" \
  --resolution="24,24" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_punks_v2_7" \
  --save_model_as=safetensors \
  --max_train_epochs=5 \
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
  --clip_skip=1 \
  --xformers

echo ""
echo "=== Training Complete ==="
echo "Model saved to: /workspace/output/bespoke_punks_v2_7.safetensors"
echo "Download the .safetensors file to test locally"
