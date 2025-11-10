#!/bin/bash
# RunPod GPU Disk Cleanup Script
# Run this on RunPod BEFORE starting training to free up space

echo "============================================"
echo "RunPod Disk Cleanup"
echo "============================================"
echo ""

echo "Current disk usage:"
df -h /workspace
echo ""

# Remove old training outputs
echo "[1/7] Removing old training outputs..."
rm -rf /workspace/output/*
rm -rf /workspace/output_*
echo "Cleared output directories"

# Remove old models
echo "[2/7] Removing old model files..."
rm -rf /workspace/models/*
rm -f /workspace/*.safetensors
rm -f /workspace/*.ckpt
rm -f /workspace/*.pt
echo "Cleared old models"

# Remove old logs
echo "[3/7] Removing old logs..."
rm -rf /workspace/logs/*
rm -rf /workspace/log_*
echo "Cleared logs"

# Clean pip cache
echo "[4/7] Cleaning pip cache..."
pip cache purge
echo "Cleared pip cache"

# Clean conda cache if it exists
echo "[5/7] Cleaning conda cache (if exists)..."
conda clean --all -y 2>/dev/null || echo "Conda not found, skipping"

# Remove old training data from previous runs
echo "[6/7] Removing old training data..."
rm -rf /workspace/training_data_old
rm -rf /workspace/training_images_old
rm -rf /workspace/reg_data
echo "Cleared old training data"

# Clean apt cache
echo "[7/7] Cleaning apt cache..."
apt-get clean
rm -rf /var/lib/apt/lists/*
echo "Cleared apt cache"

echo ""
echo "============================================"
echo "Cleanup complete!"
echo "New disk usage:"
df -h /workspace
echo "============================================"
