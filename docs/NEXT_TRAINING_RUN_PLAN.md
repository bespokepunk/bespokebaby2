# Next Training Run Plan: SD15_KEEP_TOKENS_3_EXPERIMENT

## Executive Summary

**Primary Goal:** Validate hypothesis that keep_tokens=3 solves background color accuracy issue

**Expected Impact:** Green background by Epoch 3-4 (vs Epoch 7 previously), stable convergence to 8-9/10 quality

**Confidence:** 85% (highest priority recommendation from MLOps analysis)

---

## Training Configuration

**File:** `training_config_SD15_KEEP_TOKENS_3.toml`

### Key Parameters

| Parameter | Previous Value | New Value | Rationale |
|-----------|---------------|-----------|-----------|
| `keep_tokens` | 1 | **3** | Primary change - prevents dropping critical color keywords |
| `caption_dropout_rate` | 0.0 | **0.05** | Slight dropout for prompt variety |
| `network_dim` | 32 | **32** | KEEP - proven optimal for pixel art |
| `network_alpha` | 16 | **16** | KEEP - stable |
| `learning_rate` | 1e-4 | **1e-4** | KEEP - stable convergence |
| `max_train_epochs` | 10 | **10** | Same as previous |

### Dataset
- **Images:** 203 original images
- **Caption Version:** final_corrected_lips_12hex_v1 (12+ hex codes)
- **Resolution:** 512x512
- **Future expansion:** Add 203 generated images (see DATASET_EXPANSION_STRATEGY.md)

---

## Success Criteria

### Primary Objectives (MUST ACHIEVE)

✅ **1. Early Background Convergence**
- Green background appears by Epoch 3-4 (vs Epoch 7 previously)
- Background remains stable (no oscillation)

✅ **2. Quality Target**
- Quality score 8+/10 by Epoch 7
- No quality degradation while learning background color

✅ **3. Training Stability**
- No oscillation between correct background and wrong background
- Smooth convergence across all epochs

### Secondary Objectives (DESIRED)

⭐ **4. Production Ready**
- At least one epoch achieves 8.5+/10 (production ready)
- Comparable to SD15_PERFECT Epoch 7 (9/10 baseline)

⭐ **5. Accessory Quality**
- Crown, necklace clearly visible and accurate
- No accessory degradation vs SD15_FINAL_CORRECTED

⭐ **6. Color Accuracy**
- Quantitative color accuracy: 80%+ by Epoch 5
- Hair colors correct, no two-toning by Epoch 7

---

## Quality Checkpoints

### Epoch 1-2: Baseline
**Expected:**
- Pixel art style established
- Wrong background (pink/purple) - NORMAL
- Some two-toning in hair

**Test:** Run quick_test_epoch.py with auto_test_epoch.py automation

### Epoch 3-4: CRITICAL CHECKPOINT 🎯
**Expected:**
- **GREEN BACKGROUND SHOULD APPEAR** ← Primary validation point
- Quality may still be developing (7-7.5/10 acceptable)
- Background should be stable from here on

**Action if FAILED:**
- If background still wrong at Epoch 4, hypothesis is INVALID
- Stop training and re-analyze
- Consider alternative approaches (caption simplification, different tokenizer, etc.)

**Action if SUCCESS:**
- Continue training to Epoch 10
- Validates 85% confidence prediction
- Sets foundation for dataset expansion

### Epoch 5-7: Convergence
**Expected:**
- Green background stable
- Quality improving: 7.5-8.5/10
- Accessories becoming clearer
- Color accuracy improving

### Epoch 8-10: Production Quality
**Expected:**
- Quality plateau: 8-9/10
- Production-ready checkpoint identified
- Comparable to or better than SD15_PERFECT

---

## Testing Protocol

### Automated Testing (Every Epoch)

```bash
# Run automated test pipeline
python auto_test_epoch.py <checkpoint_path> --auto-score --auto-commit

# This will:
# 1. Generate test images (512px and 24px)
# 2. Run color accuracy metrics
# 3. Run style quality metrics
# 4. Auto-score: Visual/Style/Prompt
# 5. Log to Supabase
# 6. Git commit results
```

### Manual Review (Key Epochs: 1, 3, 5, 7, 10)

```bash
# Generate diverse test set
python test_epoch_diverse.py <checkpoint_path>

# Visual inspection:
# - Background color accuracy
# - Accessory clarity
# - Color palette cleanliness
# - Overall style consistency
```

### Comparison Analysis (After Epoch 10)

```bash
# Compare against baselines
python scripts/parameter_correlation_analysis.py --report

# Root cause analysis (if issues persist)
python scripts/root_cause_analyzer.py --training-run "SD15_KEEP_TOKENS_3_EXPERIMENT"

# Generate next hypotheses
python scripts/hypothesis_generator.py
```

---

## Decision Points

### After Epoch 4

**If background is GREEN ✅:**
- Continue to Epoch 10
- Begin planning dataset expansion with 203 generated images
- Prepare next experiment (e.g., conv_dim=8)

**If background is still WRONG ❌:**
- STOP training at Epoch 5
- Root cause analysis
- Alternative hypotheses:
  - Caption simplification (remove some hex codes)
  - Caption restructuring (reorder keywords)
  - Different tokenizer approach
  - Increase keep_tokens to 5

### After Epoch 10

**If quality 8+/10 achieved ✅:**
- Mark best epoch as production candidate
- Begin dataset expansion experiment
- Plan long-term improvements (accessories, variety, etc.)

**If quality <8/10 ❌:**
- Analyze gap vs SD15_PERFECT
- Test next hypotheses:
  - conv_dim=8 (accessory detail)
  - Dataset expansion (203 generated images)
  - Learning rate adjustment
  - Longer training (15 epochs)

---

## Comparison Baselines

### SD15_FINAL_CORRECTED_CAPTIONS (Previous Run)
- **Best Epoch:** 6 (7.3/10)
- **Background:** Wrong (purple) until Epoch 7
- **Epoch 7:** Green background but quality degraded (7.0/10)
- **Issue:** Training oscillation, couldn't maintain both

### SD15_PERFECT (Production Baseline)
- **Best Epoch:** 7 (9/10)
- **Quality:** Production ready
- **Dataset:** 203 OG images
- **Captions:** Simpler (fewer hex codes)
- **Target to beat**

### SD15_KEEP_TOKENS_3 (This Run)
- **Goal:** Combine SD15_PERFECT's quality with FINAL_CORRECTED's detailed captions
- **Target:** 8.5+/10 by Epoch 7-10
- **Key metric:** Green background by Epoch 3-4

---

## Upload Instructions

### RunPod Setup

```bash
# 1. Upload training config
scp training_config_SD15_KEEP_TOKENS_3.toml runpod:/workspace/

# 2. Verify dataset is in place
# - 203 images in /workspace/training_data/
# - final_corrected_lips_12hex_v1 captions (.txt files)

# 3. Start training
cd /workspace
python train_network.py --config training_config_SD15_KEEP_TOKENS_3.toml

# 4. Monitor progress
tail -f /workspace/logs/keep_tokens_3_experiment.log
```

### Expected Training Time
- **Per Epoch:** ~10-12 minutes (203 images, batch_size=1, gradient_accumulation=4)
- **Total (10 epochs):** ~2 hours
- **GPU:** RTX 4090 or similar

---

## Next Steps After This Run

### If Successful (8+/10 quality achieved):

1. **Dataset Expansion Experiment**
   - Review 203 generated images
   - Re-caption 50-100 best images
   - Test training with 203 OG + 50 generated = 253 images
   - Compare convergence speed and quality

2. **Accessory Detail Experiment**
   - Add conv_dim=8, conv_alpha=4
   - Test if accessories (crown, necklace) become clearer
   - Medium priority, 45% confidence

3. **Production Deployment**
   - Select best epoch checkpoint
   - Deploy to Gradio app
   - Begin generating final collection

### If Partially Successful (7-7.9/10 quality):

1. **Refinement Run**
   - Same config, longer training (15 epochs)
   - Or adjust learning_rate to 5e-5 (more stable)

2. **Dataset Expansion** (may help push over 8/10 threshold)

3. **Conv_dim experiment** (detail improvement)

### If Unsuccessful (<7/10 or wrong background persists):

1. **Root Cause Analysis**
   - Deep dive into why keep_tokens=3 didn't work
   - Analyze caption structure and tokenization

2. **Alternative Approaches**
   - Simplify captions (reduce hex codes to 6-8 core colors)
   - Test keep_tokens=5
   - Caption restructuring

3. **Baseline Return**
   - Consider using SD15_PERFECT approach (simpler captions)
   - Add detail incrementally

---

## MLOps Tracking

### Log to Supabase

All epochs will be automatically logged with:
- Visual quality score (1-10)
- Style match score (1-10)
- Prompt adherence score (1-10)
- Quantitative color accuracy (0-100)
- Quantitative style quality (0-100)
- Background color (hex code)
- Unique colors count
- Issues detected
- Observations

### Parameters to Track

```json
{
  "run_name": "SD15_KEEP_TOKENS_3_EXPERIMENT",
  "architecture": {
    "network_dim": 32,
    "network_alpha": 16,
    "conv_dim": 0
  },
  "hyperparameters": {
    "learning_rate": 1e-4,
    "lr_scheduler": "cosine_with_restarts",
    "max_train_epochs": 10,
    "optimizer_type": "AdamW8bit"
  },
  "data": {
    "num_images": 203,
    "caption_version": "final_corrected_lips_12hex_v1",
    "keep_tokens": 3,
    "caption_dropout_rate": 0.05
  },
  "augmentation": {
    "noise_offset": 0.05
  }
}
```

---

## Files Ready for Upload

✅ `training_config_SD15_KEEP_TOKENS_3.toml` - Main training config
✅ `docs/DATASET_EXPANSION_STRATEGY.md` - Future dataset expansion plan
✅ `docs/NEXT_TRAINING_RUN_PLAN.md` - This document
✅ `auto_test_epoch.py` - Automated testing pipeline
✅ `scripts/measure_color_accuracy.py` - Quantitative color metrics
✅ `scripts/measure_pixel_art_quality.py` - Quantitative style metrics
✅ `log_epoch_to_supabase.py` - Database logging

**Status:** 🚀 Ready to start training

**Next Action:** Upload config to RunPod and start training run
