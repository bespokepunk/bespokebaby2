# Phase 1B Training Experiment - Log

**Date:** 2025-11-10
**Status:** 🧪 TESTING IN PROGRESS
**Hypothesis:** Simplified captions (removing micro-details) will improve quality vs CAPTION_FIX

---

## Executive Summary

Phase 1B tests whether **simplifying captions** improves LoRA quality compared to CAPTION_FIX baseline (216.6 avg colors, Epoch 8).

**Key Changes from CAPTION_FIX:**
- ✂️ Simplified captions: Removed micro-details that don't exist at 24x24 scale
- ✅ Kept: 512px resolution, SD 1.5 architecture, 8 epochs
- ✅ Kept: Core color system (no hex codes in captions)

---

## Background: Why Phase 1B?

### The 256px Disaster (Phase 2)
- **Result:** 395-450 colors (83-108% WORSE than baseline)
- **Root Causes:**
  1. ❌ Phase 1A captions too verbose (describing features invisible at 24x24)
  2. ❌ 256px resolution theory backwards (lower res = worse, not better)

### User Feedback
> "u dont think we can do better still ? wh yr u giving up?"

This pivotal feedback led to Phase 1B: fix the caption complexity, keep proven resolution.

---

## Caption Simplification Examples

### Before (Phase 1A - OVERCOMPLICATED):
```
wearing black rectangular stunner sunglasses with thin black plastic frames
and thin temples behind ears, lenses completely cover eyes with white reflections
```
**Character count:** 139

### After (Phase 1B - SIMPLIFIED):
```
wearing black rectangular sunglasses covering eyes
```
**Character count:** 48 (65% reduction)

### More Examples:

| Feature | Phase 1A (Complex) | Phase 1B (Simple) |
|---------|-------------------|-------------------|
| **Hat** | "wearing red structured baseball cap with curved front brim covering top of head down to hairline with white small logo on front center" | "wearing red baseball cap" |
| **Earrings** | "wearing large circular golden yellow drop earrings hanging from earlobes" | "wearing golden circular earrings" |
| **Hair** | "bright lime green yellow green hair tied back in queue ponytail with side wings fluffed out in 18th century colonial style" | "bright lime green hair in ponytail" |

**Philosophy:** Describe what the MODEL needs to learn, not what exists in 512px training images. At 24x24, "thin temples" is 0.5 pixels!

---

## Training Configuration

### Hardware & Environment
- **Platform:** RunPod GPU Cloud
- **GPU:** A100 (40GB)
- **Training Time:** ~8-12 hours
- **Framework:** kohya_ss / sd-scripts

### Model Architecture
```toml
[model_arguments]
pretrained_model_name_or_path = "runwayml/stable-diffusion-v1-5"
v2 = false

[network_arguments]
network_module = "networks.lora"
network_dim = 32
network_alpha = 16
```

### Training Hyperparameters
```toml
[training_arguments]
max_train_epochs = 8
train_batch_size = 4
gradient_accumulation_steps = 1
mixed_precision = "bf16"
xformers = true

# Optimizer
optimizer_type = "AdamW"  # Not AdamW8bit (bitsandbytes issues)
learning_rate = 1e-4
unet_lr = 1e-4
text_encoder_lr = 5e-5
lr_scheduler = "cosine_with_restarts"
lr_warmup_steps = 100
lr_scheduler_num_cycles = 3

# Dataset
resolution = "512,512"  # PROVEN OPTIMAL
shuffle_caption = true
keep_tokens = 1  # Reverted from 3 (faster convergence)
caption_dropout_rate = 0.02  # Reduced from 0.05
max_token_length = 225

# Regularization
min_snr_gamma = 5.0
noise_offset = 0.05
```

### Dataset
- **Images:** 203 training pairs
- **Caption Format:** Simplified (no hex codes, reduced verbosity)
- **Captions Modified:** 11/203 files (accessories, hair styles)
- **Resolution:** 512x512 (with DreamBooth bucketing)

---

## Testing Methodology

### Test Script
`test_PHASE1B_all_epochs.py` - Comprehensive evaluation of all 8 epochs

### Test Prompts (8 variations)
1. **Brown eyes lady** - Basic portrait
2. **Brown eyes lad** - Basic portrait (male)
3. **Blue eyes lady** - Color variation
4. **Green eyes lad** - Rare color
5. **Afro hair** - Complex hair texture
6. **Sunglasses** - Critical accessory (CAPTION_FIX struggled)
7. **Earrings** - Subtle accessory
8. **Baseball cap** - Head covering

### Success Metrics
- **Primary:** Average unique colors in 24x24 outputs (lower = better)
- **Baseline:** CAPTION_FIX Epoch 8 = 216.6 colors
- **Target:** < 216.6 colors (improvement over baseline)
- **Secondary:** Visual quality, accessory accuracy, background cleanliness

---

## Hypothesis & Predictions

### Hypothesis
**Simplified captions will allow the model to focus on learnable features at 24x24 scale, reducing noise and improving pixel art quality.**

### Predictions

**Optimistic Scenario:**
- 🎯 Best epoch: 5-7 (similar to CAPTION_FIX)
- 🎯 Average colors: 190-210 (5-12% better than CAPTION_FIX)
- 🎯 Cleaner accessories (less hallucination of micro-details)

**Realistic Scenario:**
- 🎯 Best epoch: 6-8
- 🎯 Average colors: 210-220 (comparable to CAPTION_FIX)
- 🎯 Similar quality, less overfitting to verbose text

**Pessimistic Scenario:**
- ❌ Best epoch: 8+ (late convergence)
- ❌ Average colors: 220-240 (5-10% worse)
- ❌ Simplified captions removed useful signal

---

## Results

### Testing Status
- [x] All 8 epochs downloaded
- [x] Checkpoints organized
- [x] Test script created
- [ ] Testing in progress...
- [ ] Results analysis
- [ ] Comparison with CAPTION_FIX
- [ ] Production decision

### Epoch Results

| Epoch | Avg Colors | Min | Max | Status | Notes |
|-------|-----------|-----|-----|--------|-------|
| 1 | TBD | TBD | TBD | Testing... | Early learning |
| 2 | TBD | TBD | TBD | Pending | |
| 3 | TBD | TBD | TBD | Pending | |
| 4 | TBD | TBD | TBD | Pending | |
| 5 | TBD | TBD | TBD | Pending | Sweet spot? |
| 6 | TBD | TBD | TBD | Pending | |
| 7 | TBD | TBD | TBD | Pending | |
| 8 | TBD | TBD | TBD | Pending | Final epoch |

**Baseline for Comparison:**
- CAPTION_FIX Epoch 8: **216.6 avg colors** (current production)

---

## Analysis Framework

### Questions to Answer

1. **Did simplification help?**
   - Phase 1B best epoch < 216.6 colors? → Success
   - Phase 1B best epoch > 230 colors? → Failed hypothesis

2. **Which epoch is optimal?**
   - Compare convergence speed vs CAPTION_FIX
   - Does simplification change optimal epoch number?

3. **Quality improvements?**
   - Are accessories more accurate?
   - Are backgrounds cleaner?
   - Less color noise?

4. **What did we learn?**
   - Caption complexity impact quantified
   - Optimal verbosity level for 24x24 pixel art
   - Feature description best practices

---

## Decision Tree

```
IF Phase 1B Best < 216.6:
  → Use Phase 1B for production
  → Document optimal caption simplification rules
  → Apply learnings to future training

ELIF Phase 1B Best ≈ 216.6 (±5):
  → A/B test both in production
  → Let user feedback decide
  → Build adaptive epoch system (Option B)

ELSE Phase 1B Best > 225:
  → Stick with CAPTION_FIX Epoch 8
  → Hypothesis rejected: Complexity helps model learning
  → Explore other improvements (Phase 1C?)
```

---

## Next Steps

### Immediate (After Testing)
1. [ ] Analyze results vs CAPTION_FIX baseline
2. [ ] Visual quality audit (manual inspection)
3. [ ] Document findings in final report
4. [ ] Update production if Phase 1B wins
5. [ ] Update Supabase with Phase 1B captions

### Short-Term (This Week)
1. [ ] Build adaptive epoch selection system
2. [ ] Systematic testing of ALL epochs (CAPTION_FIX + Phase 1B)
3. [ ] User feedback collection integration
4. [ ] Production deployment

### Long-Term (Next Month)
1. [ ] Phase 1C: Further caption optimization (if needed)
2. [ ] Multi-epoch ensemble generation
3. [ ] Fine-grained parameter tuning per epoch
4. [ ] Community feedback analysis

---

## Related Documents

- `CAPTION_FIX_FINAL_REPORT.md` - Baseline experiment (216.6 colors)
- `256PX_EXPERIMENT_FAILURE_SUMMARY.md` - Why we're doing Phase 1B
- `PHASE1B_SIMPLIFIED_CAPTIONS_LOG.md` - Caption changes made
- `ADAPTIVE_EPOCH_SYSTEM_DESIGN.md` - Future routing system

---

## Training Artifacts

### Package
- **File:** `runpod_package_phase1b.zip` (2.4 MB)
- **Contents:** 203 images + 203 simplified captions + config.toml
- **Structure:** DreamBooth format (`training_data/1_bespoke_baby/`)

### Checkpoints (Downloaded)
```
lora_checkpoints/phase1b/
  phase1b_epoch1.safetensors  (36 MB)
  phase1b_epoch2.safetensors  (36 MB)
  phase1b_epoch3.safetensors  (36 MB)
  phase1b_epoch4.safetensors  (36 MB)
  phase1b_epoch5.safetensors  (36 MB)
  phase1b_epoch6.safetensors  (36 MB)
  phase1b_epoch7.safetensors  (36 MB)
  phase1b_epoch8.safetensors  (36 MB)
```

### Test Outputs
```
test_outputs_PHASE1B/
  epoch_1/
    brown_eyes_lady_512.png
    brown_eyes_lady_24x24.png
    ... (8 prompts)
    results.json
  epoch_2/
    ...
  ... (8 epochs)
  PHASE1B_SUMMARY.json
```

---

## Conclusion

Phase 1B represents a **hypothesis-driven refinement** based on the 256px failure analysis. By simplifying captions to match what's learnable at 24x24 scale, we expect cleaner convergence and better quality.

**Testing in progress. Results to be documented upon completion.**

---

**Last Updated:** 2025-11-10 (Testing initiated)
**Status:** 🧪 Awaiting results...
