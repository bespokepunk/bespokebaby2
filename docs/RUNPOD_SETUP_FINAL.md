# RunPod Training Setup - FINAL WORKING VERSION

**Date:** 2025-11-11
**Status:** ✅ WORKING - Training successfully running

---

## Critical Lessons Learned

### What Went Wrong Previously:
1. **Line break issues**: Pasting multi-line commands into RunPod terminal splits them incorrectly
2. **Cache accumulation**: 33GB accumulates in `/workspace/.cache` every run
3. **Missing data extraction**: Cleared cache deleted extracted training files
4. **Path confusion**: Mixed up `/workspace/kohya_ss/sd-scripts` vs `/workspace/sd-scripts`
5. **Incomplete cleanup**: Didn't remove all old training folders

### What Finally Worked:
**Creating a script file with heredoc (`cat > file << 'EOF'`) instead of pasting multi-line commands**

---

## THE WORKING PROCESS (3 Steps)

### Step 1: Clear Space & Extract Data

```bash
cd /workspace
rm -rf /workspace/.cache/*
rm -rf ~/.cache/*
rm -rf /workspace/training_parent
rm -rf /workspace/runpod_package
unzip -q training_data_IMPROVED.zip
mkdir -p /workspace/training_parent/10_bespoke_punk
mv /workspace/runpod_package/training_data_IMPROVED/* /workspace/training_parent/10_bespoke_punk/
df -h /workspace
```

### Step 2: Create Training Script

```bash
cat > /workspace/GO.sh << 'EOF'
#!/bin/bash
cd /workspace/sd-scripts
accelerate launch --num_cpu_threads_per_process=2 train_network.py \
  --pretrained_model_name_or_path=/workspace/models/sd15_base.safetensors \
  --train_data_dir=/workspace/training_parent \
  --resolution=512,512 \
  --output_dir=/workspace/output \
  --output_name=bespoke_punks_IMPROVED \
  --save_model_as=safetensors \
  --max_train_epochs=10 \
  --learning_rate=0.0001 \
  --unet_lr=0.0001 \
  --text_encoder_lr=0.00005 \
  --lr_scheduler=cosine_with_restarts \
  --network_module=networks.lora \
  --network_dim=32 \
  --network_alpha=16 \
  --save_every_n_epochs=2 \
  --mixed_precision=fp16 \
  --save_precision=fp16 \
  --cache_latents \
  --optimizer_type=AdamW8bit \
  --xformers \
  --train_batch_size=4 \
  --gradient_checkpointing \
  --caption_extension=.txt \
  --shuffle_caption \
  --keep_tokens=2 \
  --max_token_length=225 \
  --seed=42
EOF
```

### Step 3: Run Training

```bash
chmod +x /workspace/GO.sh
bash /workspace/GO.sh
```

---

## Expected Output When Working

```
Using DreamBooth method.
prepare images.
found directory /workspace/training_parent/10_bespoke_punk contains 203 image files
2030 train images with repeating.
create LoRA network. base dim (rank): 32, alpha: 16.0
create LoRA for Text Encoder: 72 modules.
create LoRA for U-Net: 192 modules.
running training / 学習開始
  num train images * repeats: 2030
  num batches per epoch: 508
  num epochs: 10
  total optimization steps: 5080
epoch 1/10
steps:   1%|█▉
```

If you see "found directory contains 203 image files" and "steps: 1%", training is working.

---

## Variable Reference (Change These for Different Runs)

| Variable | Current Value | Purpose |
|----------|--------------|---------|
| `TRAINING_ZIP` | `training_data_IMPROVED.zip` | Training data filename |
| `REPEAT_COUNT` | `10` | Folder name prefix (10_bespoke_punk) |
| `OUTPUT_NAME` | `bespoke_punks_IMPROVED` | Model filename prefix |
| `MAX_EPOCHS` | `10` | Total epochs to train |
| `SAVE_EVERY` | `2` | Save checkpoint every N epochs |
| `RESOLUTION` | `512,512` | Training resolution |
| `BATCH_SIZE` | `4` | Batch size (lower if OOM) |
| `LEARNING_RATE` | `0.0001` | U-Net learning rate |
| `TEXT_LR` | `0.00005` | Text encoder LR |
| `LORA_DIM` | `32` | LoRA dimension |
| `LORA_ALPHA` | `16` | LoRA alpha |
| `KEEP_TOKENS` | `2` | Tokens not shuffled in captions |
| `SEED` | `42` | Random seed for reproducibility |

---

## File Locations on RunPod

| Path | Contents |
|------|----------|
| `/workspace/training_data_IMPROVED.zip` | Uploaded training data |
| `/workspace/runpod_package/training_data_IMPROVED/` | Extracted files (203 images + captions) |
| `/workspace/training_parent/10_bespoke_punk/` | Files moved here for Kohya structure |
| `/workspace/sd-scripts/train_network.py` | The actual training script |
| `/workspace/models/sd15_base.safetensors` | Base SD 1.5 model |
| `/workspace/output/` | Saved checkpoints (every 2 epochs) |
| `/workspace/GO.sh` | Training launch script |
| `/workspace/.cache/` | **33GB cache - MUST DELETE** |

---

## Checkpoint Saving

**Saves every 2 epochs:**
- Epoch 2: `bespoke_punks_IMPROVED-000002.safetensors`
- Epoch 4: `bespoke_punks_IMPROVED-000004.safetensors`
- Epoch 6: `bespoke_punks_IMPROVED-000006.safetensors`
- Epoch 8: `bespoke_punks_IMPROVED-000008.safetensors`
- Epoch 10: `bespoke_punks_IMPROVED-000010.safetensors`

**Check saved models:**
```bash
ls -lh /workspace/output/
```

---

## Training Time

- **Per Epoch:** ~25-30 minutes on A40
- **Total (10 epochs):** ~4-5 hours
- **With latent caching:** First epoch takes longer (caches latents), rest are faster

---

## Common Errors & Fixes

### Error: "cannot stat '/workspace/runpod_package/training_data_IMPROVED/*'"
**Cause:** Training data not extracted or cache was cleared after extraction
**Fix:** Run `unzip -q training_data_IMPROVED.zip` again

### Error: "resolution is required / resolution（解像度）指定は必須です"
**Cause:** Multi-line command split incorrectly, `--resolution` parameter not passed
**Fix:** Use the script method (GO.sh) instead of pasting commands directly

### Error: "No data found. Please verify arguments"
**Cause:** Wrong folder structure or files not in `10_bespoke_punk` subfolder
**Fix:** Verify files are at `/workspace/training_parent/10_bespoke_punk/`

### Error: "101% pod volume utilization"
**Cause:** 33GB cache accumulated in `/workspace/.cache`
**Fix:** `rm -rf /workspace/.cache/*` (saves 33GB immediately)

---

## After Training Completes

### Download Models
```bash
# From local machine:
scp runpod:/workspace/output/*.safetensors ./models/runpod_checkpoints/
```

### Test Each Epoch
Test all epochs locally to find best one:
```bash
python test_model.py --model models/runpod_checkpoints/bespoke_punks_IMPROVED-000002.safetensors
python test_model.py --model models/runpod_checkpoints/bespoke_punks_IMPROVED-000004.safetensors
# etc...
```

### Select Best Model
Based on:
1. Visual quality (no artifacts, clear features)
2. Expression accuracy (test with validation set)
3. Hairstyle accuracy (test with validation set)
4. Overall prompt following

---

## Complete All-in-One Script (Future Runs)

**For completely automated runs, use this:**

```bash
cat > /workspace/FULL_SETUP.sh << 'EOF'
#!/bin/bash
set -e  # Exit on error

echo "=== STEP 1: Clear space ==="
rm -rf /workspace/.cache/*
rm -rf ~/.cache/*
rm -rf /workspace/training_parent
rm -rf /workspace/runpod_package
rm -rf /workspace/output/*
mkdir -p /workspace/output

echo "=== STEP 2: Extract training data ==="
cd /workspace
unzip -q training_data_IMPROVED.zip

echo "=== STEP 3: Setup Kohya structure ==="
mkdir -p /workspace/training_parent/10_bespoke_punk
mv /workspace/runpod_package/training_data_IMPROVED/* /workspace/training_parent/10_bespoke_punk/

echo "=== STEP 4: Verify files ==="
FILE_COUNT=$(ls /workspace/training_parent/10_bespoke_punk/*.png /workspace/training_parent/10_bespoke_punk/*.jpg 2>/dev/null | wc -l)
echo "Found $FILE_COUNT image files"
if [ "$FILE_COUNT" -lt 200 ]; then
    echo "ERROR: Expected ~203 images, found only $FILE_COUNT"
    exit 1
fi

echo "=== STEP 5: Start training ==="
cd /workspace/sd-scripts
accelerate launch --num_cpu_threads_per_process=2 train_network.py \
  --pretrained_model_name_or_path=/workspace/models/sd15_base.safetensors \
  --train_data_dir=/workspace/training_parent \
  --resolution=512,512 \
  --output_dir=/workspace/output \
  --output_name=bespoke_punks_IMPROVED \
  --save_model_as=safetensors \
  --max_train_epochs=10 \
  --learning_rate=0.0001 \
  --unet_lr=0.0001 \
  --text_encoder_lr=0.00005 \
  --lr_scheduler=cosine_with_restarts \
  --network_module=networks.lora \
  --network_dim=32 \
  --network_alpha=16 \
  --save_every_n_epochs=2 \
  --mixed_precision=fp16 \
  --save_precision=fp16 \
  --cache_latents \
  --optimizer_type=AdamW8bit \
  --xformers \
  --train_batch_size=4 \
  --gradient_checkpointing \
  --caption_extension=.txt \
  --shuffle_caption \
  --keep_tokens=2 \
  --max_token_length=225 \
  --seed=42

echo "=== Training complete! ==="
ls -lh /workspace/output/
EOF

chmod +x /workspace/FULL_SETUP.sh
bash /workspace/FULL_SETUP.sh
```

---

## Historical Issues (Don't Repeat)

1. ❌ Tried `train_lora.py` - doesn't exist
2. ❌ Used wrong path `/workspace/kohya_ss/sd-scripts/` - correct is `/workspace/sd-scripts/`
3. ❌ Pasted multi-line commands - terminal splits them incorrectly
4. ❌ Forgot to re-extract after clearing cache - no training data
5. ❌ Cleared cache but didn't document it - repeated disk space issues
6. ❌ Provided "Quick Resume" command without checking if extraction needed
7. ✅ **Created GO.sh script with heredoc - THIS WORKS**

---

## Success Criteria

Training is working correctly when you see:
- ✅ "found directory /workspace/training_parent/10_bespoke_punk contains 203 image files"
- ✅ "2030 train images with repeating"
- ✅ "create LoRA for Text Encoder: 72 modules"
- ✅ "create LoRA for U-Net: 192 modules"
- ✅ "epoch 1/10"
- ✅ "steps: 1%|█▉"

If any of these are missing, something is wrong.

---

## Support

**If training fails:**
1. Check `/workspace/training_parent/10_bespoke_punk/` has 203 images
2. Verify `/workspace/sd-scripts/train_network.py` exists
3. Check disk space: `df -h /workspace` (need 5GB+ free)
4. Use the GO.sh script method, not direct paste

**Never repeat:**
- Pasting multi-line commands directly
- Forgetting to clear the 33GB cache
- Clearing cache without re-extracting training data
- Using wrong paths or guessing script locations

---

**Last Updated:** 2025-11-11 (VERIFIED WORKING)
