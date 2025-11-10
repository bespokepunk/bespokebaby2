#!/bin/bash
set -e

echo "============================================"
echo "Bespoke Baby SD 1.5 LoRA Training - RunPod"
echo "============================================"
echo ""

# Setup workspace directories
echo "[1/6] Setting up workspace directories..."
mkdir -p /workspace/training_data
mkdir -p /workspace/output
mkdir -p /workspace/logs

# Copy training data to workspace
echo "[2/6] Copying training data to workspace..."
cp -r training_data/* /workspace/training_data/
echo "Training data copied: $(ls /workspace/training_data/*.png | wc -l) images"

# Install system dependencies
echo "[3/6] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq git wget unzip

# Clone and setup Kohya SS if not exists
if [ ! -d "/workspace/kohya_ss" ]; then
    echo "[4/6] Cloning Kohya SS sd-scripts..."
    cd /workspace
    git clone https://github.com/kohya-ss/sd-scripts.git kohya_ss
    cd kohya_ss
else
    echo "[4/6] Kohya SS already exists, updating..."
    cd /workspace/kohya_ss
    git pull
fi

# Install Python dependencies
echo "[5/6] Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118
pip install --quiet -r requirements.txt
pip install --quiet xformers==0.0.22.post7
pip install --quiet bitsandbytes==0.41.1
pip install --quiet transformers==4.35.2
pip install --quiet diffusers[torch]==0.24.0
pip install --quiet accelerate==0.25.0

# Copy config file
cp /workspace/bespoke_baby_training/training_config.toml /workspace/kohya_ss/

# Start training
echo "[6/6] Starting LoRA training..."
echo ""
echo "Training Configuration:"
echo "  - Model: Stable Diffusion 1.5"
echo "  - Network Dim: 32"
echo "  - Network Alpha: 16"
echo "  - Learning Rate: 1e-4"
echo "  - Epochs: 10"
echo "  - Training Images: 203"
echo "  - Output: /workspace/output"
echo ""
echo "Training started at: $(date)"
echo "============================================"
echo ""

cd /workspace/kohya_ss

accelerate launch --num_cpu_threads_per_process=2 \
  train_network.py \
  --config_file=training_config.toml

echo ""
echo "============================================"
echo "Training completed at: $(date)"
echo "============================================"
echo ""
echo "Output files saved to: /workspace/output"
echo "Models can be found at:"
ls -lh /workspace/output/*.safetensors
echo ""
echo "Download your trained LoRA models from /workspace/output/"
echo "============================================"
