#!/bin/bash

# 🚀 Bespoke Punk SDXL Training - Quick Start Script
# Run this on your RunPod instance

set -e  # Exit on error

echo "🎨 BESPOKE PUNK SDXL TRAINING"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "runpod_training.py" ]; then
    echo "❌ Error: runpod_training.py not found!"
    echo "Please run this script from the bespokebaby2 directory"
    exit 1
fi

# Check if dataset exists
if [ ! -d "FORTRAINING6/all" ] || [ ! -d "FORTRAINING6/oldtext" ]; then
    echo "❌ Error: Training dataset not found!"
    echo "Expected: FORTRAINING6/all (images) and FORTRAINING6/oldtext (captions)"
    exit 1
fi

# Count images and captions
IMAGE_COUNT=$(ls FORTRAINING6/all/*.png 2>/dev/null | wc -l)
CAPTION_COUNT=$(ls FORTRAINING6/oldtext/*.txt 2>/dev/null | wc -l)

echo "📦 Dataset Check:"
echo "   Images: $IMAGE_COUNT"
echo "   Captions: $CAPTION_COUNT"
echo ""

if [ "$IMAGE_COUNT" -eq 0 ] || [ "$CAPTION_COUNT" -eq 0 ]; then
    echo "❌ Error: No images or captions found!"
    exit 1
fi

if [ "$IMAGE_COUNT" -ne "$CAPTION_COUNT" ]; then
    echo "⚠️  Warning: Image and caption counts don't match!"
    echo "   This may cause issues during training."
fi

# Check Python and dependencies
echo "🔍 Checking dependencies..."
python -c "import torch; print(f'✅ PyTorch {torch.__version__}')" || {
    echo "❌ PyTorch not found! Run: pip install -r requirements_runpod.txt"
    exit 1
}

python -c "import diffusers; print(f'✅ Diffusers {diffusers.__version__}')" || {
    echo "❌ Diffusers not found! Run: pip install -r requirements_runpod.txt"
    exit 1
}

# Check GPU
echo ""
echo "🎮 GPU Check:"
python -c "import torch; print(f'   CUDA Available: {torch.cuda.is_available()}'); print(f'   GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}'); print(f'   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB' if torch.cuda.is_available() else '')" || {
    echo "⚠️  Warning: Could not detect GPU"
}

echo ""
echo "🚀 Starting training..."
echo ""

# Recommended settings for most GPUs (RTX 4090 / A40 / A6000)
python runpod_training.py \
  --images_dir ./FORTRAINING6/all \
  --captions_dir ./FORTRAINING6/oldtext \
  --output_dir ./models/bespoke_punk_sdxl \
  --base_model stabilityai/stable-diffusion-xl-base-1.0 \
  --resolution 512 \
  --train_batch_size 4 \
  --num_train_epochs 120 \
  --learning_rate 0.00008 \
  --lora_rank 16 \
  --lora_alpha 16 \
  --mixed_precision fp16 \
  --gradient_accumulation_steps 1 \
  --save_steps 500 \
  --validation_steps 100 \
  --wandb_project bespoke-punk-sdxl \
  --wandb_api_key 495752e0ee6cde7b8d27088c713f941780d902a1 \
  --seed 42

echo ""
echo "🎉 Training complete!"
echo "📁 Model saved to: ./models/bespoke_punk_sdxl/final_model"
echo ""
echo "Next steps:"
echo "1. Test your model"
echo "2. Download the model"
echo "3. Don't forget to stop your RunPod instance!"
