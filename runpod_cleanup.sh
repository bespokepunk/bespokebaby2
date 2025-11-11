#!/bin/bash
# RunPod Disk Cleanup Script
# Run this ON the RunPod instance to free up space

echo "============================================"
echo "RUNPOD DISK CLEANUP"
echo "============================================"
echo ""

# Check current disk usage
echo "Current disk usage:"
df -h /workspace
echo ""

echo "Checking disk usage by directory..."
cd /workspace
du -sh * 2>/dev/null | sort -hr | head -20
echo ""

echo "============================================"
echo "SAFE CLEANUP OPTIONS"
echo "============================================"
echo ""

# Option 1: Old training checkpoints
echo "1. Old Training Checkpoints:"
if [ -d "/workspace/output" ]; then
    echo "   Found: /workspace/output"
    du -sh /workspace/output 2>/dev/null
    echo "   These are old .safetensors files from previous training runs"
    echo "   Safe to delete if you've already downloaded them"
fi
echo ""

# Option 2: Hugging Face cache
echo "2. Hugging Face Model Cache:"
if [ -d "$HOME/.cache/huggingface" ]; then
    echo "   Found: $HOME/.cache/huggingface"
    du -sh $HOME/.cache/huggingface 2>/dev/null
    echo "   Cached models (can be re-downloaded if needed)"
fi
echo ""

# Option 3: Pip cache
echo "3. Pip Cache:"
if [ -d "$HOME/.cache/pip" ]; then
    echo "   Found: $HOME/.cache/pip"
    du -sh $HOME/.cache/pip 2>/dev/null
    echo "   Python package cache (can be re-downloaded)"
fi
echo ""

# Option 4: Old training data
echo "4. Old Training Data:"
if [ -d "/workspace/training_data" ]; then
    echo "   Found: /workspace/training_data"
    du -sh /workspace/training_data 2>/dev/null
    echo "   Old training images/captions (if superseded by new ones)"
fi
echo ""

# Option 5: Temp files
echo "5. Temp Files:"
echo "   /tmp and other temporary directories"
du -sh /tmp 2>/dev/null
echo ""

echo "============================================"
echo "CLEANUP COMMANDS (run as needed)"
echo "============================================"
echo ""
echo "# Remove old training checkpoints (if already downloaded):"
echo "rm -rf /workspace/output/*.safetensors"
echo ""
echo "# Clear Hugging Face cache:"
echo "rm -rf \$HOME/.cache/huggingface/*"
echo ""
echo "# Clear pip cache:"
echo "pip cache purge"
echo ""
echo "# Clear temp files:"
echo "rm -rf /tmp/*"
echo ""
echo "# Remove old training data (BE CAREFUL - verify first!):"
echo "# rm -rf /workspace/training_data_OLD"
echo ""
echo "# Docker cleanup (if you have access):"
echo "# docker system prune -a -f"
echo ""

echo "============================================"
echo "INTERACTIVE CLEANUP"
echo "============================================"
echo ""

read -p "Do you want to run automatic cleanup now? (yes/no): " response

if [ "$response" = "yes" ] || [ "$response" = "y" ]; then
    echo ""
    echo "Starting cleanup..."

    # Clear pip cache
    echo "Clearing pip cache..."
    pip cache purge 2>/dev/null
    echo "✓ Pip cache cleared"

    # Clear temp files
    echo "Clearing /tmp..."
    rm -rf /tmp/* 2>/dev/null
    echo "✓ Temp files cleared"

    # Clear Hugging Face cache (aggressive - will re-download models)
    read -p "Clear Hugging Face cache? (models will re-download) (yes/no): " hf_response
    if [ "$hf_response" = "yes" ] || [ "$hf_response" = "y" ]; then
        echo "Clearing Hugging Face cache..."
        rm -rf $HOME/.cache/huggingface/* 2>/dev/null
        echo "✓ Hugging Face cache cleared"
    fi

    # Show results
    echo ""
    echo "============================================"
    echo "CLEANUP COMPLETE"
    echo "============================================"
    echo ""
    echo "New disk usage:"
    df -h /workspace

else
    echo "Cleanup cancelled. Use the commands above manually."
fi

echo ""
echo "Done!"
