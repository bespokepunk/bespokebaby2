#!/bin/bash
# Disk Cleanup Commands for bespokebaby2 repo
# Run these to free up space before RunPod upload

cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2

echo "Starting disk cleanup..."
echo "Current disk usage:"
df -h .

# Remove old RunPod files
echo "Removing old RunPod files..."
rm -f RUNPOD_COMPLETE*
rm -f RUNPOD_FINAL*
rm -f RUNPOD_SIMPLE*
rm -f runpod_train_sd*.sh
rm -f runpod_train_v2*.sh
rm -f runpod_train.sh
rm -f runpod_v2_7_*.sh
rm -f sd15_training_51*.sh

# Remove old bespoke_punks model files
echo "Removing old model safetensor files..."
rm -f bespoke_punks_*.safetensors

# Remove old civitai training configs
echo "Removing old civitai training files..."
rm -f civitai_v2_7_trai*.sh

# Remove old training output directories (if they exist in workspace)
# DO NOT run these if you need to keep any models from these folders
# Uncomment if you're sure you don't need them:
# rm -rf output/
# rm -rf output_PERFECT/
# rm -rf models/
# rm -rf reg_data/
# rm -rf training_data/
# rm -rf training_images/

# Remove kohya_ss clone (if you don't need it locally - RunPod will clone it)
# Uncomment if you're sure:
# rm -rf kohya_ss/

# Remove old FORTRAINING6 if it's a duplicate
# Uncomment if you're sure:
# rm -rf FORTRAINING6/

echo ""
echo "Cleanup complete!"
echo "New disk usage:"
df -h .

echo ""
echo "To remove large training artifacts, uncomment the lines in this script"
echo "for: output/, output_PERFECT/, models/, kohya_ss/, FORTRAINING6/"
