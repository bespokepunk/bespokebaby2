# SD 1.5 Training Setup for RunPod

## What's Ready

✅ **203 images** upscaled to 512x512 (nearest-neighbor, preserves pixel art)
✅ **203 captions** with your final perfect format
✅ **Training script** configured for SD 1.5 (not SDXL)
✅ **Packaged zip** for easy upload

---

## Why SD 1.5 Instead of SDXL?

**SDXL was making detailed pixel art portraits** (too realistic)
**SD 1.5 makes simple bespoke punk style** (clean, blocky, perfect)

Your best results came from SD 1.5 epoch 5 - simple, clean pixel art!

---

## Upload to RunPod

### Option 1: Upload Zip File

1. Upload `sd15_training_512.zip` to RunPod
2. In RunPod terminal:
```bash
cd /workspace
unzip sd15_training_512.zip -d training_data
```

### Option 2: Upload Folder Directly

Upload the entire `sd15_training_512/` folder to `/workspace/training_data` on RunPod

---

## Run Training

### Step 1: Upload Training Script

Upload `runpod_train_sd15.sh` to `/workspace/` on RunPod

### Step 2: Run Training

```bash
chmod +x /workspace/runpod_train_sd15.sh
bash /workspace/runpod_train_sd15.sh
```

---

## Training Configuration

- **Model:** Stable Diffusion 1.5
- **Resolution:** 512x512 (upscaled from 24x24)
- **Epochs:** 10 (saves every epoch)
- **Batch Size:** 4
- **LoRA Rank:** 32
- **Learning Rate:** 0.0001
- **Output:** `bespoke_punks_SD15_PERFECT-000001.safetensors` through `000010.safetensors`

---

## What to Expect

Based on previous SD 1.5 training:

- **Epoch 1-2:** Basic shapes, colors starting to work
- **Epoch 3-5:** Good bespoke punk style, clean pixel art
- **Epoch 5-7:** Best results (simple, blocky, accurate)
- **Epoch 8-10:** Might be slightly overtrained but test them

**Download and test epochs 5, 7, and 10** for comparison.

---

## Testing After Training

Download the `.safetensors` files and run:

```bash
python test_PERFECT_epoch5.py  # Already have this script
```

Or create new test scripts for epochs 7 and 10.

---

## Files Created

1. `sd15_training_512/` - 203 images (512x512) + captions
2. `sd15_training_512.zip` - Packaged for upload (868 KB)
3. `runpod_train_sd15.sh` - Training script for RunPod
4. `upscale_for_sd15_training.py` - Script used to create 512x512 images

---

## Important Notes

- ✅ Uses **SD 1.5** not SDXL
- ✅ Images upscaled with **nearest-neighbor** (no smoothing)
- ✅ Same **perfect captions** you created
- ✅ Training at **512x512** (not 1024x1024)
- ✅ All dependencies auto-installed by script

---

## Expected Training Time

On RunPod with GPU:
- ~10-15 minutes per epoch
- ~2-2.5 hours total for 10 epochs

---

## Next Steps

1. Upload `sd15_training_512.zip` to RunPod
2. Upload `runpod_train_sd15.sh` to RunPod
3. Run: `bash /workspace/runpod_train_sd15.sh`
4. Wait ~2 hours
5. Download epoch 5, 7, 10 `.safetensors` files
6. Test locally with your existing test scripts

---

**This should give you the clean bespoke punk style you want!**
