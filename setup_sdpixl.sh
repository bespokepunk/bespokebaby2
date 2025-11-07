#!/bin/bash
# Setup SD-πXL for bespoke punk pixel art generation

echo "================================================================================"
echo "🔧 SETTING UP SD-πXL"
echo "================================================================================"

cd SD-piXL

# Install dependencies (without conda for simplicity)
echo ""
echo "📦 Installing dependencies..."
pip install torch torchvision torchaudio
pip install matplotlib accelerate omegaconf einops transformers scipy tensorboard openai-clip xformers opencv-python
pip install git+https://github.com/huggingface/diffusers
pip install -U scikit-learn peft

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "================================================================================"
echo "📝 USAGE"
echo "================================================================================"
echo ""
echo "To generate a 24x24 pixel art image:"
echo ""
echo "cd SD-piXL"
echo "accelerate launch main.py \\"
echo "  --config ../config_bespoke_24x24.yaml \\"
echo "  --size 24,24 \\"
echo "  --palette assets/palettes/bespoke_punk.hex \\"
echo "  -pt \"Your prompt here\" \\"
echo "  --download \\"
echo "  --verbose"
echo ""
echo "⚠️  Note: Generation takes ~1.5 hours per image on GPU!"
echo "⚠️  Requires 24GB VRAM (you have 44GB on RunPod ✅)"
echo ""
echo "================================================================================"
