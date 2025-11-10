# RunPod Cleanup + Training Commands

**Date:** 2025-11-10
**Purpose:** Clear disk space, then train with NEW captions + optimal parameters

---

## STEP 1: Clean Up RunPod Disk Space

### Check Current Disk Usage
```bash
df -h /workspace
df -h /root
```

### Clean Up Commands (Run on RunPod)

```bash
# Navigate to workspace
cd /workspace

# Remove old training outputs
rm -rf output/*
echo "✓ Cleared output directory"

# Remove old test outputs
rm -rf test_outputs_*
echo "✓ Cleared test outputs"

# Remove old training data directories (keep current one if needed)
rm -rf training_data/
echo "✓ Cleared old training data"

# Clean up model cache in /root/.cache
rm -rf /root/.cache/huggingface/hub/*
echo "✓ Cleared Hugging Face cache"

# Clean pip cache
pip cache purge
echo "✓ Cleared pip cache"

# Remove any old zip files
rm -rf *.zip
echo "✓ Cleared old zip files"

# Clean up any old kohya_ss if needed (ONLY if you want to reinstall fresh)
# rm -rf /workspace/kohya_ss
# echo "✓ Removed old kohya_ss"

# Remove old safetensors if they're backed up
rm -rf *.safetensors
echo "✓ Cleared old checkpoint files"

# Check space after cleanup
echo ""
echo "Disk space after cleanup:"
df -h /workspace
df -h /root
```

### Aggressive Cleanup (If Still Low on Space)

```bash
# Remove everything except models directory
cd /workspace
find . -maxdepth 1 -type d ! -name "." ! -name ".." ! -name "models" -exec rm -rf {} +
find . -maxdepth 1 -type f -delete
echo "✓ Aggressive cleanup complete"

# Verify
df -h /workspace
```

---

## STEP 2: Upload Training Package

### On Your Local Machine

**Package Location:**
```
/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_NEW_CAPTIONS_OPTIMAL.zip
```

**Size:** 917KB

**Upload Methods:**

**Option A: RunPod Web Interface**
1. Open RunPod web interface
2. Navigate to your pod
3. Click "File Browser" or similar
4. Click "Upload"
5. Select `runpod_NEW_CAPTIONS_OPTIMAL.zip`
6. Wait for upload to complete

**Option B: Command Line (if you have SSH access)**
```bash
# On your local machine
scp runpod_NEW_CAPTIONS_OPTIMAL.zip root@[RUNPOD_IP]:/workspace/
```

---

## STEP 3: Extract and Setup on RunPod

```bash
# Navigate to workspace
cd /workspace

# Extract the package
unzip -q runpod_NEW_CAPTIONS_OPTIMAL.zip
echo "✓ Package extracted"

# Verify contents
ls -lh runpod_NEW_CAPTIONS_OPTIMAL/
```

---

## STEP 4: Copy Training Data

```bash
# Create training data directory with repeat count
mkdir -p /workspace/training_data/10_bespoke_baby

# Copy images
cp runpod_NEW_CAPTIONS_OPTIMAL/training_data/*.png /workspace/training_data/10_bespoke_baby/
echo "✓ Images copied"

# Copy captions
cp runpod_NEW_CAPTIONS_OPTIMAL/training_data/*.txt /workspace/training_data/10_bespoke_baby/
echo "✓ Captions copied"

# Verify counts
IMAGE_COUNT=$(ls /workspace/training_data/10_bespoke_baby/*.png | wc -l)
CAPTION_COUNT=$(ls /workspace/training_data/10_bespoke_baby/*.txt | wc -l)
echo "Images: $IMAGE_COUNT (should be 203)"
echo "Captions: $CAPTION_COUNT (should be 203)"

# Verify caption format (should show 12+ hex codes)
echo ""
echo "Sample caption (verify it has NEW format with 12+ hex codes):"
echo "---"
cat /workspace/training_data/10_bespoke_baby/lad_001_carbon.txt
echo "---"
echo ""
echo "⚠️  IMPORTANT: Caption should have:"
echo "  - 12+ hex codes"
echo "  - Specific details (eye color, skin tone, accessories)"
echo "  - ~320 characters"
echo "  - If it looks generic (1-3 hex codes), STOP and check!"
```

---

## STEP 5: Install/Verify Kohya SS

### If Kohya SS NOT Installed

```bash
cd /workspace

# Clone Kohya SS
git clone https://github.com/kohya-ss/sd-scripts.git kohya_ss
cd kohya_ss

# Install requirements
pip install -r requirements.txt

echo "✓ Kohya SS installed"
```

### If Kohya SS Already Installed

```bash
# Just verify it exists
cd /workspace
if [ -d "kohya_ss" ]; then
    echo "✓ Kohya SS found"
    cd kohya_ss
    git pull  # Update to latest
    echo "✓ Kohya SS updated"
else
    echo "ERROR: Kohya SS not found! Install it first."
    exit 1
fi
```

---

## STEP 6: Run Training

```bash
cd /workspace/runpod_NEW_CAPTIONS_OPTIMAL

# Make script executable
chmod +x train_sd15_new_captions_optimal.sh

# Run training
bash train_sd15_new_captions_optimal.sh
```

**What Happens:**
1. Installs all dependencies
2. Verifies GPU
3. Downloads SD1.5 model (if needed)
4. Verifies training data (203 images, 203 captions)
5. Shows sample caption for verification
6. Starts training with optimal parameters
7. Saves checkpoint every epoch
8. Shows completion message with file locations

**Expected Time:** 2-4 hours depending on GPU
**Expected Cost:** ~$1-2

---

## STEP 7: Monitor Training

### Check Progress

```bash
# In another terminal/tab, monitor output directory
watch -n 30 ls -lh /workspace/output/

# Or check logs
tail -f /workspace/kohya_ss/logs/*
```

### What to Watch For

**Good Signs:**
- ✅ "Epoch 1/10" through "Epoch 10/10"
- ✅ Loss values decreasing
- ✅ Checkpoint files appearing in /workspace/output/
- ✅ No CUDA errors

**Bad Signs:**
- ❌ Disk full errors
- ❌ CUDA out of memory
- ❌ Training stops unexpectedly
- ❌ No checkpoint files created

---

## STEP 8: After Training Completes

### Download Checkpoints

```bash
# List all checkpoints
cd /workspace/output
ls -lh *.safetensors

# Expected files:
# bespoke_punks_SD15_NEW_CAPTIONS_OPTIMAL-000001.safetensors (36MB)
# bespoke_punks_SD15_NEW_CAPTIONS_OPTIMAL-000002.safetensors (36MB)
# ... (epochs 1-9)
# bespoke_punks_SD15_NEW_CAPTIONS_OPTIMAL.safetensors (36MB, final)
```

**Download all epoch files via RunPod web interface or:**
```bash
# Zip them for easier download
cd /workspace/output
zip -r SD15_NEW_CAPTIONS_all_epochs.zip *.safetensors
echo "✓ Created zip file for download"
ls -lh SD15_NEW_CAPTIONS_all_epochs.zip
```

---

## Training Configuration Summary

### What's Being Trained

**Model:** Stable Diffusion 1.5
**Purpose:** Test if NEW accurate captions work with optimal parameters

**Captions Used:** NEW accurate (Nov 10, 12:53 AM)
- 12+ hex codes per caption
- Specific details (eye color, skin tone, accessories)
- Accurate background descriptions
- ~320 characters average

**Parameters:** ALL optimal from SD15_PERFECT (9/10 success)
- network_dim: **32** ← PROVEN SUCCESSFUL
- network_alpha: 16
- resolution: 512x512
- batch_size: 4
- shuffle_caption: **TRUE** ← CRITICAL
- keep_tokens: **2** ← CRITICAL
- max_token_length: 225
- multires_noise_iterations: **6** ← CRITICAL
- multires_noise_discount: **0.3** ← CRITICAL
- adaptive_noise_scale: **0.00357** ← CRITICAL
- noise_offset: 0.1
- min_snr_gamma: 5
- mixed_precision: fp16
- optimizer: AdamW8bit
- lr_scheduler: cosine_with_restarts (3 cycles)
- learning_rate: 0.0001
- text_encoder_lr: 0.00005

### Expected Results

**If SUCCESS (8-10/10):**
- ✅ NEW accurate captions work!
- ✅ Production ready model
- ✅ Update Supabase with success

**If FAILURE (0-7/10):**
- ⚠️ Caption detail is the problem
- ⚠️ Try Option 3 (simplified captions)
- ⚠️ Update Supabase with findings

---

## Complete Command Sequence (Copy-Paste Ready)

```bash
#############################################
# STEP 1: CLEANUP
#############################################
cd /workspace
df -h /workspace /root

# Remove old files
rm -rf output/* test_outputs_* training_data/ *.zip *.safetensors
rm -rf /root/.cache/huggingface/hub/*
pip cache purge

echo "✓ Cleanup complete"
df -h /workspace /root

#############################################
# STEP 2: EXTRACT PACKAGE (after upload)
#############################################
cd /workspace
unzip -q runpod_NEW_CAPTIONS_OPTIMAL.zip

#############################################
# STEP 3: SETUP TRAINING DATA
#############################################
mkdir -p /workspace/training_data/10_bespoke_baby
cp runpod_NEW_CAPTIONS_OPTIMAL/training_data/*.png /workspace/training_data/10_bespoke_baby/
cp runpod_NEW_CAPTIONS_OPTIMAL/training_data/*.txt /workspace/training_data/10_bespoke_baby/

# Verify
ls /workspace/training_data/10_bespoke_baby/*.png | wc -l
ls /workspace/training_data/10_bespoke_baby/*.txt | wc -l
cat /workspace/training_data/10_bespoke_baby/lad_001_carbon.txt

#############################################
# STEP 4: INSTALL KOHYA (if needed)
#############################################
cd /workspace
if [ ! -d "kohya_ss" ]; then
    git clone https://github.com/kohya-ss/sd-scripts.git kohya_ss
    cd kohya_ss
    pip install -r requirements.txt
fi

#############################################
# STEP 5: RUN TRAINING
#############################################
cd /workspace/runpod_NEW_CAPTIONS_OPTIMAL
chmod +x train_sd15_new_captions_optimal.sh
bash train_sd15_new_captions_optimal.sh

#############################################
# After training, download checkpoints from:
# /workspace/output/*.safetensors
#############################################
```

---

## Troubleshooting

### Issue: Disk Full During Training

```bash
# Emergency cleanup
cd /workspace
rm -rf /root/.cache/huggingface/hub/*
pip cache purge
df -h /workspace /root
```

### Issue: CUDA Out of Memory

```bash
# Training will fail if GPU memory insufficient
# Check GPU memory:
nvidia-smi

# If OOM, reduce batch size in training script
# Edit line: --train_batch_size=4
# Change to: --train_batch_size=2 or --train_batch_size=1
```

### Issue: Kohya Not Found

```bash
cd /workspace
git clone https://github.com/kohya-ss/sd-scripts.git kohya_ss
cd kohya_ss
pip install -r requirements.txt
```

### Issue: Model Download Fails

```bash
# Manually download SD1.5 model
cd /workspace/models
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors -O sd15_base.safetensors
```

---

## Summary

1. ✅ Clean up RunPod disk space
2. ✅ Upload `runpod_NEW_CAPTIONS_OPTIMAL.zip`
3. ✅ Extract and setup training data
4. ✅ Install/verify Kohya SS
5. ✅ Run training (2-4 hours)
6. ✅ Download checkpoints
7. ✅ Test and compare to SD15_PERFECT

**Ready to go!** Start with cleanup commands above.
