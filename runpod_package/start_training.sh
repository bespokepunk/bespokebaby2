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
mkdir -p /workspace/training_data/10_bespoke_baby
cp -v training_data/*.png /workspace/training_data/10_bespoke_baby/ 2>&1 | grep -c ".png" || echo "0"
cp -v training_data/*.txt /workspace/training_data/10_bespoke_baby/ 2>&1 | grep -c ".txt" || echo "0"
IMAGE_COUNT=$(ls /workspace/training_data/10_bespoke_baby/*.png 2>/dev/null | wc -l)
CAPTION_COUNT=$(ls /workspace/training_data/10_bespoke_baby/*.txt 2>/dev/null | wc -l)
echo "Training data copied: $IMAGE_COUNT images, $CAPTION_COUNT captions"
if [ "$IMAGE_COUNT" != "203" ] || [ "$CAPTION_COUNT" != "203" ]; then
    echo "ERROR: Expected 203 images and 203 captions, got $IMAGE_COUNT images and $CAPTION_COUNT captions"
    exit 1
fi

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
echo "[5/6] Installing Python dependencies and downloading model..."
pip install --quiet --upgrade pip

# Uninstall ALL conflicting packages first
pip uninstall -y torch torchvision torchaudio xformers triton 2>/dev/null || true

# Install latest compatible versions from cu118
pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install --quiet -r requirements.txt
pip install --quiet xformers --index-url https://download.pytorch.org/whl/cu118
pip install --quiet bitsandbytes
pip install --quiet transformers
pip install --quiet diffusers[torch]
pip install --quiet accelerate
pip install --quiet huggingface-hub
pip install --quiet hf_transfer  # For fast HuggingFace downloads

# Create accelerate config to avoid warnings
mkdir -p ~/.cache/huggingface/accelerate
cat > ~/.cache/huggingface/accelerate/default_config.yaml << 'ACCEL_EOF'
compute_environment: LOCAL_MACHINE
distributed_type: 'NO'
downcast_bf16: 'no'
machine_rank: 0
main_training_function: main
mixed_precision: fp16
num_machines: 1
num_processes: 1
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
ACCEL_EOF

# Pre-download SD 1.5 model to avoid timeout during training
echo "Downloading Stable Diffusion 1.5 model..."
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('runwayml/stable-diffusion-v1-5', allow_patterns=['*.json', '*.txt', '*.safetensors', '*.bin', '*.model'])" || echo "Model download had issues, will retry during training"

# Copy config file
cp /workspace/runpod_package/training_config.toml /workspace/kohya_ss/sd-scripts/

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

cd /workspace/kohya_ss/sd-scripts

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
