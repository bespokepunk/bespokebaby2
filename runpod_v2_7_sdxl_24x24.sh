#!/bin/bash

echo "=== V2.7 RunPod Training - 24x24 Native Resolution ==="
echo "CRITICAL FIX: Training at 24x24 (NOT 1024) to preserve pixel art style"
echo ""

cd /workspace/kohya_ss
source venv/bin/activate

echo "Verifying training data..."
ls -la /workspace/FORTRAINING6/bespokepunks/*.png | head -5
echo ""
echo "Image count: $(find /workspace/FORTRAINING6/bespokepunks -name "*.png" | wc -l)"
echo "Caption count: $(find /workspace/FORTRAINING6/bespokepunks -name "*.txt" | wc -l)"
echo ""

echo "=== Starting V2.7 SDXL Training at 24x24 Native Resolution ==="
echo "Expected duration: ~2-3 hours for 10 epochs"
echo ""

python sd-scripts/train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="/workspace/FORTRAINING6/bespokepunks" \
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
echo "Models saved to: /workspace/output/"
ls -lh /workspace/output/*.safetensors
