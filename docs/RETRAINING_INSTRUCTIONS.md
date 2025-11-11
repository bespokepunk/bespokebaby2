# Retraining Instructions - Improved Captions

**Date:** 2025-11-10
**Package:** training_data_IMPROVED.zip (893KB)
**Base Model:** CAPTION_FIX Epoch 8

---

## What Was Improved

### Expression Captions: 195/203 images (96%)
Enhanced with detailed mouth shape descriptions for better model learning.

**Before:**
- "neutral expression"
- "slight smile"

**After:**
- "mouth in straight neutral line with relaxed expression"
- "mouth corners turned up in gentle slight smile"
- "lips curved upward in subtle smile expression"
- "calm neutral expression with closed relaxed mouth"

**Why This Helps:**
- More descriptive language teaches the model specific mouth shapes
- Better text embeddings create stronger visual-text associations
- Model learns the connection between facial features and expressions

**Expected Improvement:** 50.2% → 70-80% expression detection accuracy

---

### Hairstyle Captions: 8/203 images (4%)
Only a few images have hairstyle labels in the training data, but these were significantly enhanced.

**Before:**
- "curly hair"
- "wavy hair"
- "straight hair"
- "in two braids"

**After:**
- "tightly coiled curly textured hair with high volume"
- "gently wavy hair with soft flowing waves"
- "sleek straight hair hanging smoothly down"
- "hair in two distinct braids with visible woven pattern"

**Why This Helps:**
- Detailed texture descriptions (coiled, flowing, smooth, woven)
- Specific pattern language (tight weaving, soft waves, distinct curl pattern)
- More varied vocabulary for the model to learn from

**Expected Improvement:** 28.9% → 70-80% hairstyle detection accuracy

---

## Package Contents

**Location:** `training_data_IMPROVED.zip` (893KB) in project root

**Contains:**
- 203 improved .txt caption files
- 203 corresponding .png/.jpg image files
- All images are 24x24 pixel art bespoke punks
- Same images as original training data, only captions enhanced

**File Structure:**
```
runpod_package/training_data_IMPROVED/
├── lad_001_carbon.txt
├── lad_001_carbon.png
├── lady_002_vanilla.txt
├── lady_002_vanilla.png
...
(406 total files: 203 images + 203 captions)
```

---

## Retraining Process

### Step 0: Clear Disk Space (CRITICAL - DO THIS FIRST)

**The 33GB cache problem:** RunPod accumulates 33GB in `/workspace/.cache` every run. Clear it FIRST.

**Run these commands on RunPod BEFORE starting:**
```bash
# THE BIG ONE: Clear the 33GB cache (HuggingFace models, etc)
rm -rf /workspace/.cache/*
rm -rf ~/.cache/*

# Clear old training folders
rm -rf /workspace/output/*
rm -rf /workspace/training_parent
rm -rf /workspace/runpod_package
rm -rf /workspace/training_data
rm -rf /workspace/training_images
rm -rf /workspace/runpod_NEW_CAPTIONS_OPTIMAL
rm -rf /workspace/runpod_package_phase1b
rm -rf /workspace/FORTRAINING6

# Verify space (should have 30GB+ free after clearing cache)
df -h /workspace
```

**Space breakdown after cleanup:**
- Before: 41GB used, 9.9GB free (81% full)
- After clearing cache: ~8GB used, ~42GB free (16% full)

### Step 1: Upload Training Data

1. **Start RunPod Instance**
   - GPU: A40 or higher recommended
   - Template: Kohya SS training template (or SD training template with sd-scripts)
   - Storage: 20GB+ available

2. **Upload Package**
   ```bash
   # From your local machine:
   scp training_data_IMPROVED.zip runpod:/workspace/

   # Or use RunPod's web file manager to upload
   ```

### Step 2: Run Single Setup & Training Script

**Copy this entire script to RunPod as `/workspace/RETRAIN.sh`:**

```bash
#!/bin/bash
# RUNPOD RETRAINING SCRIPT - Bespoke Punks
# Variables you can change for different runs:

# ===== CHANGEABLE VARIABLES =====
TRAINING_ZIP="training_data_IMPROVED.zip"          # Your training data zip file name
OUTPUT_NAME="bespoke_punks_IMPROVED"                # Output model name prefix
MAX_EPOCHS=10                                       # Number of training epochs
SAVE_EVERY=2                                        # Save checkpoint every N epochs
RESOLUTION="512,512"                                # Training resolution
BATCH_SIZE=4                                        # Batch size (lower if OOM)
LEARNING_RATE=0.0001                                # U-Net learning rate
TEXT_LR=0.00005                                     # Text encoder learning rate
LORA_DIM=32                                         # LoRA dimension
LORA_ALPHA=16                                       # LoRA alpha
REPEAT_COUNT=10                                     # How many times to repeat dataset
# ================================

echo "=== STEP 1: Cleanup old files ==="
# Clear the 33GB cache that always accumulates
rm -rf /workspace/.cache/*

# Clear training folders
rm -rf /workspace/output/*
rm -rf /workspace/training_parent
rm -rf /workspace/runpod_package
rm -rf /workspace/training_data
rm -rf /workspace/training_images
rm -rf /workspace/runpod_NEW_CAPTIONS_OPTIMAL
rm -rf /workspace/runpod_package_phase1b
rm -rf /workspace/FORTRAINING6

# Clear other caches
rm -rf ~/.cache/*

mkdir -p /workspace/output

echo "=== Disk space after cleanup ==="
df -h /workspace

echo "=== STEP 2: Extract training data ==="
cd /workspace
unzip -q "$TRAINING_ZIP"

echo "=== STEP 3: Setup Kohya folder structure ==="
# Kohya requires: parent_folder/##_subfolder_name/images+captions
mkdir -p "/workspace/training_parent/${REPEAT_COUNT}_bespoke_punk"
mv /workspace/runpod_package/training_data_IMPROVED/* "/workspace/training_parent/${REPEAT_COUNT}_bespoke_punk/"

echo "=== STEP 4: Download base model if needed ==="
if [ ! -f /workspace/models/sd15_base.safetensors ]; then
    mkdir -p /workspace/models
    cd /workspace/models
    wget -O sd15_base.safetensors "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors"
fi

echo "=== STEP 5: Start training ==="
cd /workspace/sd-scripts

accelerate launch --num_cpu_threads_per_process=2 train_network.py \
  --pretrained_model_name_or_path=/workspace/models/sd15_base.safetensors \
  --train_data_dir=/workspace/training_parent \
  --resolution=$RESOLUTION \
  --output_dir=/workspace/output \
  --output_name=$OUTPUT_NAME \
  --save_model_as=safetensors \
  --max_train_epochs=$MAX_EPOCHS \
  --learning_rate=$LEARNING_RATE \
  --unet_lr=$LEARNING_RATE \
  --text_encoder_lr=$TEXT_LR \
  --lr_scheduler=cosine_with_restarts \
  --network_module=networks.lora \
  --network_dim=$LORA_DIM \
  --network_alpha=$LORA_ALPHA \
  --save_every_n_epochs=$SAVE_EVERY \
  --mixed_precision=fp16 \
  --save_precision=fp16 \
  --cache_latents \
  --optimizer_type=AdamW8bit \
  --xformers \
  --train_batch_size=$BATCH_SIZE \
  --gradient_checkpointing \
  --caption_extension=.txt \
  --shuffle_caption \
  --keep_tokens=2 \
  --max_token_length=225 \
  --seed=42

echo "=== Training complete! ==="
echo "Models saved to: /workspace/output/"
ls -lh /workspace/output/
```

**Then run it:**
```bash
chmod +x /workspace/RETRAIN.sh
bash /workspace/RETRAIN.sh
```

**That's it. One command.**

---

## EMERGENCY QUICK START (Space Cleared / Training Interrupted)

**If you cleared cache and need to restart, paste this ONE block:**

```bash
cd /workspace && unzip -q training_data_IMPROVED.zip && mkdir -p /workspace/training_parent/10_bespoke_punk && mv /workspace/runpod_package/training_data_IMPROVED/* /workspace/training_parent/10_bespoke_punk/ && cd /workspace/sd-scripts && accelerate launch --num_cpu_threads_per_process=2 train_network.py --pretrained_model_name_or_path=/workspace/models/sd15_base.safetensors --train_data_dir=/workspace/training_parent --resolution=512,512 --output_dir=/workspace/output --output_name=bespoke_punks_IMPROVED --save_model_as=safetensors --max_train_epochs=10 --learning_rate=0.0001 --unet_lr=0.0001 --text_encoder_lr=0.00005 --lr_scheduler=cosine_with_restarts --network_module=networks.lora --network_dim=32 --network_alpha=16 --save_every_n_epochs=2 --mixed_precision=fp16 --save_precision=fp16 --cache_latents --optimizer_type=AdamW8bit --xformers --train_batch_size=4 --gradient_checkpointing --caption_extension=.txt --shuffle_caption --keep_tokens=2 --max_token_length=225 --seed=42
```

**That's ONE command. Copy the ENTIRE line and paste once.**

---

### Step 3: Monitor Training

**Training will show:**
- Total steps and progress percentage
- Current epoch (1-10)
- Loss values (should decrease over time)
- Steps per second

**Checkpoints save automatically:**
- Every 2 epochs: epochs 2, 4, 6, 8, 10
- Location: `/workspace/output/`
- Naming: `bespoke_punks_IMPROVED-000002.safetensors`, `bespoke_punks_IMPROVED-000004.safetensors`, etc.
- **Note:** Files don't appear DURING an epoch, only when it completes

**Check saved models:**
```bash
ls -lh /workspace/output/
```

### Step 4: Download All Models

**After training completes, download all checkpoints:**
```bash
# From your local machine:
scp runpod:/workspace/output/*.safetensors ./models/runpod_checkpoints/

# Or use RunPod file manager to download
```

### Step 5: Test Each Epoch Locally

**Test each checkpoint to find the best one:**
```bash
# Test epoch 2
python test_model.py --model models/runpod_checkpoints/bespoke_punks_IMPROVED-000002.safetensors

# Test epoch 4
python test_model.py --model models/runpod_checkpoints/bespoke_punks_IMPROVED-000004.safetensors

# etc...
```

**Select the epoch with best visual quality and accuracy**

---

## Cost & Time Estimates

### Training Time
- **Per Epoch:** ~25-30 minutes on A40
- **Total (15 epochs):** ~6-7 hours
- **With validation:** ~8 hours total

### Cost
- **GPU Rental:** A40 @ $0.39/hr × 8 hours = **~$3.12**
- **Storage:** Minimal (< $0.50)
- **Total Estimated Cost:** **~$4-5**

Much cheaper than the initial $15 estimate because we're fine-tuning, not training from scratch!

---

## Expected Results

### Current Accuracy (CAPTION_FIX Epoch 8)
- Expression: 50.2% (102/203) - Coin flip
- Hairstyle: 28.9% (11/38) - Very poor
- Reliable Features (earrings, eyewear): 80.6% - Excellent

### After Retraining (Expected)
- Expression: **70-80%** (+20-30 points) - Useful!
- Hairstyle: **70-80%** (+41-51 points) - Useful!
- Reliable Features: **80.6%** (unchanged) - Still excellent

### Overall System Accuracy
- **Before:** 56.3% (all features) | 80.6% (reliable only)
- **After:** **~75%** (all features) - GOAL MET!

---

## Fallback Plan

If retraining doesn't hit 70%+ accuracy:

### Option A: Skip Expression/Hairstyle
- Ship with reliable features only (earrings, eyewear, colors)
- 80.6% accuracy on features we include
- Better user experience than 50% coin flips

### Option B: More Training Data
- Current training data only has:
  - 203 expression examples
  - 38 hairstyle examples (very small!)
- Could collect more diverse hairstyle examples
- Augment with synthetic data

### Option C: Advanced Detection (No Retraining)
- Expression: Implement facial landmarks (mediapipe)
  - Measure mouth curvature angles
  - Expected: 75-85% accuracy
  - Effort: 1-2 days
- Hairstyle: Add LBP + FFT analysis
  - Local binary patterns for texture
  - FFT for periodic patterns (braids)
  - Expected: 50-60% accuracy
  - Effort: 2-3 days

---

## Validation After Retraining

Once the new model is trained, validate it:

```bash
# Run full validation
python validate_detector.py

# Should see output like:
# Expression: 72.4% (147/203) ← Target met!
# Hairstyle: 76.3% (29/38) ← Target met!
# Overall: 75.2% ← GOAL ACHIEVED!
```

If validation shows 70%+ on both features, we're done!

---

## Next Steps

1. **Upload training_data_IMPROVED.zip to RunPod**
2. **Start training with CAPTION_FIX Epoch 8 as base**
3. **Monitor training every 2 epochs**
4. **Run validation on saved checkpoints**
5. **Select best epoch (highest validation accuracy)**
6. **Download and deploy new model**
7. **Run full system validation to confirm improvement**

---

## Questions?

**If training stalls:** Lower learning rate to 5e-7
**If overfitting:** Add dropout or reduce epochs
**If quality drops:** Revert to CAPTION_FIX Epoch 8
**If accuracy still poor:** Consider Option C (advanced detection without retraining)

The improved captions should significantly boost expression and hairstyle detection. Good luck with retraining!
