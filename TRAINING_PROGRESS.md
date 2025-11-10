# Bespoke Baby LoRA Training - Progress Documentation

**Last Updated:** 2025-11-10
**Status:** SDXL Training In Progress on RunPod

---

## Critical Decision: SD 1.5 → SDXL

### SD 1.5 Training Results (COMPLETE FAILURE)
- **Trained:** 10 epochs, all completed successfully
- **Problem:** ALL epochs (1-9) generated realistic baby photographs instead of pixel art
- **Root Cause:** SD 1.5 base model has too strong photorealistic bias
- **Conclusion:** LoRA cannot override base model bias for style learning

### SDXL Training (CURRENT)
- **Decision Made:** Switch to SDXL base model immediately
- **Rationale:**
  - SDXL designed for better style learning
  - User has proven working SDXL scripts (RUNPOD_FINAL_PERFECT.sh)
  - Captions already correct (start with "pixel art, 24x24")
  - No caption modifications needed

---

## Current Training Configuration

### Files
- **Package:** `bespoke_baby_runpod_training.zip` (SDXL version)
- **Script:** `runpod_package/start_training.sh` (SDXL)
- **Training Data:** 203 images (24x24 pixel art) + 203 captions

### SDXL Training Parameters

```bash
python3 sd-scripts/sdxl_train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="/workspace/training_data" \
  --resolution="1024,1024" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_baby_sdxl" \
  --save_model_as=safetensors \
  --max_train_epochs=10 \
  --learning_rate=0.0001 \
  --unet_lr=0.0001 \
  --text_encoder_lr=0.00005 \
  --network_module=networks.lora \
  --network_dim=128 \
  --network_alpha=64 \
  --save_every_n_epochs=1 \
  --mixed_precision="bf16" \
  --cache_latents \
  --cache_latents_to_disk \
  --optimizer_type="AdamW8bit" \
  --caption_extension=".txt" \
  --lr_scheduler="cosine_with_restarts" \
  --lr_scheduler_num_cycles=3 \
  --min_snr_gamma=5 \
  --noise_offset=0.1 \
  --train_batch_size=2 \
  --gradient_checkpointing \
  --xformers \
  --seed=42
```

### Key Configuration Differences

| Parameter | SD 1.5 (Failed) | SDXL (Current) |
|-----------|-----------------|----------------|
| Base Model | runwayml/stable-diffusion-v1-5 | stabilityai/stable-diffusion-xl-base-1.0 |
| Resolution | 512,512 | 1024,1024 |
| Network Dim (Rank) | 32 | 128 |
| Network Alpha | 16 | 64 |
| Mixed Precision | fp16 | bf16 |
| Batch Size | 4 | 2 |
| Training Script | train_network.py | sdxl_train_network.py |

### Training Math
- **Images:** 203
- **Repeat Count:** 10 (subdirectory: `10_bespoke_baby/`)
- **Total Samples:** 2030 per epoch
- **Batch Size:** 2
- **Steps per Epoch:** 1015
- **Total Steps:** 10150 (10 epochs)
- **Saves:** Every epoch (10 checkpoints total)

---

## Architecture (What Works)

### Proven Working Approach
Based on `RUNPOD_FINAL_PERFECT.sh` - the ONLY approach that worked:

1. **Cache Management (CRITICAL)**
   ```bash
   export HF_HOME=/workspace/.cache/huggingface
   export TRANSFORMERS_CACHE=/workspace/.cache/huggingface
   export HF_DATASETS_CACHE=/workspace/.cache/huggingface
   ```
   - Uses /workspace (50GB) NOT /root (10GB)
   - Prevents disk space errors

2. **Directory Structure**
   ```
   /workspace/
   ├── training_data/
   │   └── 10_bespoke_baby/          # Repeat count in directory name
   │       ├── lad_001_carbon.png
   │       ├── lad_001_carbon.txt
   │       └── ... (203 images + 203 captions)
   └── output/
       ├── bespoke_baby_sdxl-000001.safetensors
       ├── bespoke_baby_sdxl-000002.safetensors
       └── ... (up to epoch 10)
   ```

3. **CLI Arguments (NOT .toml files)**
   - Direct command-line arguments only
   - No training_config.toml
   - Avoids format/parsing errors

4. **Dependencies**
   - Use Kohya's requirements.txt
   - Has all correct versions pre-configured

---

## What Didn't Work (Never Do Again)

### 1. TOML Configuration Files
- **Problem:** `resolution = 512` interpreted as integer
- **Error:** `AttributeError: 'int' object has no attribute 'split'`
- **Solution:** Use CLI arguments only

### 2. Flat Directory Structure
- **Problem:** Training data in flat `/workspace/training_data/`
- **Error:** "No data found"
- **Solution:** Must use subdirectory with repeat count

### 3. Wrong Cache Location
- **Problem:** HF cache in /root (10GB partition)
- **Error:** Disk at 105% utilization
- **Solution:** Redirect to /workspace (50GB)

### 4. SD 1.5 for Style Learning
- **Problem:** Base model photorealistic bias too strong
- **Result:** Generated realistic babies instead of pixel art
- **Solution:** Use SDXL for style learning

---

## Caption Format (CORRECT - Do Not Change)

All 203 captions follow this proven format:

```
pixel art, 24x24, portrait of bespoke punk [lad/lady], [hair description],
[facial features], [skin tone], [background], [clothing], palette: [hex colors],
sharp pixel edges, hard color borders, retro pixel art style, [additional colors]
```

**Example:**
```
pixel art, 24x24, portrait of bespoke punk lady, long textured curly multicolored
brown hair with yellow accessory (#a0b1a6), wearing dark red maroon rimmed glasses,
wearing white diamond earring (#27181f), light green pale green eyes (#4f2526),
lips (#94584b), medium dark skin tone (#94584b), grey background (#a0b1a6),
grey turtleneck (#3e373e), palette: #a0b1a6, #4f2526, #94584b, #3e373e, #27181f,
sharp pixel edges, hard color borders, retro pixel art style
```

**Key Points:**
- Always starts with "pixel art, 24x24"
- Includes "bespoke punk", "bespoke baby", "bespoke punk lad", or "bespoke punk lady"
- Includes hex color codes
- Emphasizes pixel art style characteristics

---

## Current RunPod Session

### Setup Commands Used
```bash
cd /workspace
unzip -q bespoke_baby_runpod_training.zip
chmod +x runpod_package/start_training.sh
bash runpod_package/start_training.sh
```

### Current Status (as of 2025-11-10 10:44)
- ✓ Models downloaded successfully
- ✓ Latents cached (203/203) in 4:35
- ✓ LoRA network created (dim=128, alpha=64)
- ✓ Text Encoder 1 LoRA created
- ✓ Text Encoder 2 LoRA created
- ✓ Total: 264 LoRA modules for text encoders
- ⏳ **CURRENT:** Creating LoRA for U-Net (in progress)
- **NEXT:** Training will start (10150 steps)

### Expected Timeline
- LoRA setup: ~5-7 minutes (current phase)
- Training: ~2-4 hours total (depends on GPU)
- Saves checkpoint every epoch

---

## Failed Experiments Log

### Experiment 1: SD 1.5 Training
- **Date:** Prior to 2025-11-10
- **Configuration:** See table above
- **Results:**
  - Epoch 1: Realistic baby photos ❌
  - Epoch 2: Realistic baby photos ❌
  - Epoch 3: Realistic baby photos ❌
  - Epoch 4: Realistic baby photos ❌
  - Epochs 5-9: All realistic baby photos ❌
- **Conclusion:** SD 1.5 fundamentally wrong for pixel art style

---

## Next Steps

### During Training
1. Monitor training progress (should see step counter 0/10150)
2. Watch for loss values (should decrease over time)
3. Let it complete all 10 epochs (~2-4 hours)

### After Training Completes
1. Download all 10 epoch checkpoints from `/workspace/output/`
2. Test each epoch with same prompts used for SD 1.5
3. Compare quality across epochs
4. Select best performing epoch

### Testing Protocol
Use consistent test prompts:
```python
test_prompts = [
    "portrait of bespoke punk, green solid background, black hair, blue eyes, light skin",
    "portrait of bespoke baby, pink solid background, brown hair, brown eyes, medium skin",
    "portrait of bespoke punk lad, blue solid background, blonde hair, green eyes, tan skin",
    "portrait of bespoke punk lady, purple solid background, red hair, hazel eyes, pale skin",
]
```

Generate with:
- Steps: 30
- Guidance: 7.5
- Size: 1024x1024 (SDXL native)
- Model: SDXL base + LoRA

---

## Critical Reminders

1. **NEVER use SD 1.5** - proven to fail for pixel art style
2. **NEVER use .toml files** - use CLI arguments only
3. **NEVER use flat directory** - must have repeat count subdirectory
4. **NEVER cache to /root** - always use /workspace
5. **ALWAYS verify 203 images/captions** before training
6. **ALWAYS keep "pixel art, 24x24" at start** of captions
7. **ALWAYS use proven SDXL settings** from this document

---

## Reference Files

### Working Scripts in Repo
- `RUNPOD_FINAL_PERFECT.sh` - Proven SDXL training (original reference)
- `runpod_v2_7_sdxl_train.sh` - Another working SDXL example
- `runpod_package/start_training.sh` - Current SDXL script (active)

### Training Data Location
- Local: `runpod_package/training_data/` (203 PNG + 203 TXT)
- RunPod: `/workspace/training_data/10_bespoke_baby/`

### Output Location
- RunPod: `/workspace/output/bespoke_baby_sdxl-NNNNNN.safetensors`

---

## Troubleshooting Reference

### If Training Fails
1. Check disk space: `df -h /workspace`
2. Verify image count: `find /workspace/training_data -name "*.png" | wc -l` (expect 203)
3. Verify caption count: `find /workspace/training_data -name "*.txt" | wc -l` (expect 203)
4. Check logs for specific error
5. Refer to this document for correct settings

### Common Errors and Solutions
| Error | Cause | Solution |
|-------|-------|----------|
| "No data found" | Wrong directory structure | Use `10_bespoke_baby/` subdirectory |
| Disk at 105% | Cache in /root | Set HF_HOME to /workspace |
| 406 latents | Two subdirectories | Use only one subdirectory |
| AttributeError: 'int' | TOML format error | Use CLI arguments only |

---

**END OF DOCUMENTATION**
