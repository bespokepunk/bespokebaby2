# 256px Training Experiment - FAILED

**Date:** 2025-11-10
**Status:** ❌ ABANDONED - Results significantly worse than baseline

---

## Results

| Metric | 512px Epoch 8 (Baseline) | 256px Epochs 1-3 | Difference |
|--------|-------------------------|------------------|------------|
| Average Colors | 216.6 | 395.7 - 449.7 | +83% to +108% WORSE |

**Conclusion:** 256px training with enhanced captions FAILED catastrophically.

---

## What Went Wrong

### Issue #1: Overcomplicated Captions (Phase 1A)
- Enhanced captions added micro-details that don't exist at 24x24 resolution
- Example: "thin black plastic frames and thin temples behind ears" - these details can't physically render at 24px
- Model tried to render impossible details → noise/artifacts → more colors

### Issue #2: Resolution Theory Was Wrong
**Hypothesis:** 256px → 24px (10.6x downscale) would be cleaner than 512px → 24px (21.3x)

**Reality:** BACKWARDS
- 512px: Model learns high-detail features, SD1.5 downscales cleanly to 24px
- 256px: Model learns medium-detail, still downscales 10.6x, loses fidelity
- Lower resolution training is WORSE for pixel art generation

---

## Recommendation

**✅ STICK WITH 512px EPOCH 8** (Current best: 216.6 avg colors)

- Do NOT deploy 256px checkpoints
- Do NOT continue with Phase 1A enhanced captions
- Current 512px Epoch 8 remains the best model

---

## Cost

- **RunPod training:** ~$3-5 (8 epochs, ~30 min on A100)
- **Result:** Wasted experiment, but valuable learning

---

## Lessons Learned

1. ❌ Lower resolution training does NOT help pixel art
2. ❌ Verbose caption enhancements add noise at tiny resolutions
3. ✅ Original 512px approach with simple captions was correct
4. ✅ Sometimes the first solution is the best solution

---

## Next Steps

**Option A:** Use 512px Epoch 8 as-is (216.6 colors, 40% clean images)
**Option B:** Try Phase 3 (dataset expansion, hyperparameter tuning)
**Option C:** Accept current quality and move to production

**Recommended:** Option A or C - current model is decent, further improvements may not be worth cost
