#!/bin/bash
# RunPod Complete Disk Cleanup - Run BEFORE new training
# Single script to clear ALL old data and free maximum space

echo "=========================================="
echo "RunPod Complete Disk Cleanup"
echo "=========================================="
df -h /workspace | tail -1
echo ""

# Kill any stuck processes first
echo "[1/6] Killing stuck training processes..."
pkill -9 -f "train_network" 2>/dev/null || true
pkill -9 -f "accelerate" 2>/dev/null || true

# Remove ALL old training outputs and checkpoints
echo "[2/6] Removing old checkpoints and outputs..."
rm -rf /workspace/output/* 2>/dev/null
rm -rf /workspace/output_* 2>/dev/null
rm -rf /workspace/*.safetensors 2>/dev/null
rm -rf /workspace/*.ckpt 2>/dev/null
rm -rf /workspace/logs/* 2>/dev/null

# Clean model caches (HuggingFace can get huge)
echo "[3/6] Cleaning model caches..."
rm -rf ~/.cache/huggingface/hub/* 2>/dev/null
rm -rf /workspace/.cache/* 2>/dev/null

# Remove old training data (will be replaced)
echo "[4/6] Removing old training data..."
rm -rf /workspace/training_data/* 2>/dev/null
rm -rf /workspace/training_data_old 2>/dev/null

# Clean pip and system caches
echo "[5/6] Cleaning pip/apt caches..."
pip cache purge 2>/dev/null || true
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* 2>/dev/null
rm -rf /tmp/* 2>/dev/null

# Clean Kohya SS old files
echo "[6/6] Cleaning Kohya SS..."
rm -rf /workspace/kohya_ss/sd-scripts/*.safetensors 2>/dev/null

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
df -h /workspace | tail -1
echo ""
echo "✅ Ready for new training run"
echo "Next: bash start_training.sh"
echo "=========================================="
