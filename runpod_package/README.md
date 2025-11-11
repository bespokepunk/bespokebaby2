# Bespoke Baby SD 1.5 LoRA Training Package
# Experiment: keep_tokens=3 (Background Color Fix)

Complete RunPod training package for Stable Diffusion 1.5 LoRA fine-tuning.

## Experiment Details

**Run Name:** SD15_KEEP_TOKENS_3_EXPERIMENT

**Hypothesis:** Increasing keep_tokens from 1 to 3 will fix background color accuracy issue

**Expected Results:**
- ✅ Green background by Epoch 3-4 (vs Epoch 7 previously)
- ✅ Quality score 8+/10 by Epoch 7
- ✅ No training oscillation

**Confidence:** 85% (highest priority recommendation from MLOps analysis)

---

## Quick Start

1. Upload this package to your RunPod instance
2. Extract: `unzip runpod_KEEP_TOKENS_3_EXPERIMENT.zip`
3. Navigate: `cd runpod_package`
4. Run: `bash start_training.sh`

That's it! The script handles everything automatically.

---

## What's Included

- **training_data/**: 203 pixel art images + final_corrected_lips_12hex_v1 captions (24x24, 512x512)
- **training_config.toml**: Updated configuration with keep_tokens=3
- **start_training.sh**: Automated training script
- **README.md**: This file

---

## Training Configuration

**KEY CHANGES from previous run:**
- **keep_tokens: 1 → 3** ← PRIMARY CHANGE (prevents dropping color keywords)
- **caption_dropout_rate: 0.0 → 0.05** ← NEW (adds variety)

**Architecture (KEPT - proven optimal):**
- Model: Stable Diffusion 1.5
- LoRA Rank (Network Dim): 32 (optimal for pixel art)
- Network Alpha: 16

**Hyperparameters:**
- Learning Rate: 1e-4
- Epochs: 10
- Batch Size: 1
- Gradient Accumulation: 4
- Mixed Precision: FP16
- Optimizer: AdamW8bit
- Scheduler: Cosine with restarts (3 cycles)

**Dataset:**
- Training Images: 203
- Caption Version: final_corrected_lips_12hex_v1 (12+ hex codes)
- Keep Tokens: **3** (ensures critical color keywords never dropped)
- Caption Dropout: **0.05** (5% dropout for variety)

---

## Output

Trained models will be saved to `/workspace/output/` as:
- `bespoke_baby_sd15_lora_keep_tokens_3-000001.safetensors` (Epoch 1)
- `bespoke_baby_sd15_lora_keep_tokens_3-000002.safetensors` (Epoch 2)
- ... up to Epoch 10

---

## Critical Checkpoint: Epoch 4 🎯

**IMPORTANT:** After Epoch 4 completes, check the background color:

✅ **If background is GREEN:** Continue to Epoch 10 - hypothesis validated!

❌ **If background is still WRONG:** Stop training - hypothesis failed, try alternative approach

Download Epoch 4 checkpoint and test with:
```bash
python quick_test_epoch.py bespoke_baby_sd15_lora_keep_tokens_3-000004.safetensors
```

---

## Testing Each Epoch

After each epoch completes, download the checkpoint and run:

```bash
python auto_test_epoch.py <checkpoint_path> --auto-score --auto-commit
```

This will:
1. Generate test images
2. Run quantitative metrics (color accuracy, style quality)
3. Auto-score and log to Supabase
4. Commit results to Git

---

## Requirements

- RunPod instance with GPU (RTX 3090/4090 or A100 recommended)
- CUDA 11.8+
- 24GB+ VRAM recommended
- Ubuntu 20.04/22.04

---

## Expected Training Time

- **Per Epoch:** ~10-12 minutes
- **Total (10 epochs):** ~2 hours

---

## Comparison Baselines

**SD15_FINAL_CORRECTED_CAPTIONS (Previous Run):**
- Best Epoch: 6 (7.3/10)
- Background: Wrong until Epoch 7
- Issue: Training oscillation

**SD15_PERFECT (Production Baseline):**
- Best Epoch: 7 (9/10)
- Production ready

**SD15_KEEP_TOKENS_3 (This Run):**
- Goal: Combine quality + accurate backgrounds
- Target: 8.5+/10 by Epoch 7

---

## Support

Training logs available at `/workspace/logs/`

For automated testing and analysis, see:
- `docs/NEXT_TRAINING_RUN_PLAN.md`
- `docs/DATASET_EXPANSION_STRATEGY.md`

---

## Next Steps After This Run

**If successful (8+/10):**
- Dataset expansion with 50-100 generated images
- Test conv_dim=8 for accessory detail

**If partially successful (7-7.9/10):**
- Longer training (15 epochs)
- Lower learning rate (5e-5)

**If unsuccessful (<7/10):**
- Root cause analysis
- Alternative approaches (simplify captions, increase keep_tokens to 5)

---

**Status:** 🚀 Ready for deployment
**Priority:** HIGH (85% confidence)
**Date Created:** 2025-11-10
