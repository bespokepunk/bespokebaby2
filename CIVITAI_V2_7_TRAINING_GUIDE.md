# CivitAI V2.7 Training Guide - Brown Eyes Fix

## What You're Training

**V2.7 Enhanced Captions** with fixes for:
- Brown eyes (the critical fix - no more cyan!)
- Improved accessory detection (sunglasses, earrings, hats, beards, mustaches)
- Better hair styles (afro, braided, bun, ponytail, dreadlocks, slicked back)
- Gender detection from filename (lad/lady)

**Package Ready**: `bespoke_punks_v2_7_training.zip` (1.0MB, 204 images + captions)

---

## Why CivitAI (Not RunPod)?

**Your PRODUCTION models came from CivitAI:**
- Nov 8, 2025 training → 218MB LoRAs → **Worked perfectly**
- Bright, colorful, accurate pixel art

**RunPod V2.7 failed completely:**
- Nov 9, 2025 training → 72MB LoRAs → **Dark, muddy, terrible**
- Used SD 1.5 base model (wrong choice for pixel art)

**CivitAI uses better base models** (likely SDXL or Nova Pixels XL) which work much better for 24x24 pixel art.

---

## Step-by-Step CivitAI Training

### 1. Go to CivitAI Training

https://civitai.com/models/train

Click **"New Training"** or **"Train a New Model"**

### 2. Basic Settings

**Training Type**: LoRA

**Base Model**: You need to check what base model was used for V1/V2!
- Option 1: **Nova Pixels XL v2.0** (recommended for pixel art)
- Option 2: **SDXL 1.0** (if that's what V1 used)
- Option 3: Check your V1 training page to see exact base model

To find your V1 base model:
1. Go to https://civitai.com/user/models
2. Find "Bespoke Punks 24x24 Pixel Art" (your V1 training)
3. Look at training details to see the base model
4. **Use the SAME base model for V2.7**

**Model Name**: `Bespoke_Punks_V2_7_BrownEyes_Fixed`

**Description**: "V2.7 with brown eyes fix and enhanced captions (204 images)"

### 3. Upload Dataset

Upload: `bespoke_punks_v2_7_training.zip`

The zip contains:
- 204 PNG images (24x24 pixel art)
- 204 TXT caption files (V2.7 enhanced)
- Total size: 1.0MB

### 4. Training Configuration

**CRITICAL - Copy Your V1 Settings:**

Based on typical CivitAI pixel art training:

```
Resolution: 24 (for 24x24 native)
LoRA Rank: 32
Network Alpha: 16
Epochs: 10 (same as V1)
Save Every N Epochs: 1 (save all checkpoints)
Batch Size: 4
Learning Rate: 0.0001 (1e-4)
LR Scheduler: cosine
Optimizer: AdamW8bit
Mixed Precision: fp16
Clip Skip: 2 (if using SDXL/Nova Pixels)
```

**IMPORTANT CHECKBOXES:**
- ❌ Enable Buckets: **NO** (keep 24x24 native)
- ❌ Flip Augmentation: **NO** (don't flip punks)
- ❌ Color Augmentation: **NO** (preserve colors)
- ✅ Save Every N Epochs: **YES** (save all 10)

### 5. Start Training

**Estimated Cost**: $5-8
**Estimated Time**: 45-60 minutes
**Expected Output**: 10 epoch checkpoints (218MB each)

Click **"Start Training"**

---

## After Training Completes

### Download All Checkpoints

You'll get 10 checkpoints:
```
Bespoke_Punks_V2_7_BrownEyes_Fixed-000001.safetensors (Epoch 1)
Bespoke_Punks_V2_7_BrownEyes_Fixed-000002.safetensors (Epoch 2) ← Likely winner
Bespoke_Punks_V2_7_BrownEyes_Fixed-000003.safetensors (Epoch 3)
...
Bespoke_Punks_V2_7_BrownEyes_Fixed-000010.safetensors (Epoch 10)
```

Download them all to:
```
/Users/ilyssaevans/Documents/GitHub/bespokebaby2/models/civitai_v2_7/
```

### Test Brown Eyes Fix

**Critical Test Prompt** (the one that failed before):
```
pixel art, 24x24, portrait of bespoke punk lady, long afro blue hair, brown eyes,
light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style
```

**What to Check**:
- Are the eyes BROWN? (not cyan/blue)
- Are the colors bright and vibrant? (not dark/muddy)
- Is the pixel art sharp and clean?

Test with epochs 2, 5, and 10. Epoch 2 will likely be the winner (based on V1).

### Comparison Test

Generate the same prompt with:
1. **V1 PRODUCTION model** (old - has cyan eye bug)
2. **V2.7 Epoch 2** (new - should have brown eyes)

Side-by-side comparison to verify the brown eyes fix worked!

---

## Expected Results

**If V2.7 training succeeds:**
- Brown eyes will generate correctly (not cyan)
- Same bright, colorful quality as V1 PRODUCTION
- Better accessory detection (sunglasses, earrings)
- Improved hair style accuracy
- 218MB LoRA files (like V1)

**Success Criteria:**
- Brown eyes = actually brown ✅
- Quality matches V1 PRODUCTION ✅
- No dark/muddy outputs ✅

---

## Troubleshooting

**If results are still dark/muddy:**
- Check base model matches V1
- Check resolution is 24x24 (not auto-adjusted)
- Check bucketing is disabled

**If brown eyes still appear cyan:**
- Check captions in uploaded zip have "brown eyes"
- Try different epochs (2, 5, 8)
- May need to adjust caption format

**If training fails:**
- Verify zip file is valid
- Check you have enough credits
- Try uploading again

---

## Next Steps

1. **NOW**: Go to CivitAI and start V2.7 training
2. **~1 hour later**: Download all 10 checkpoints
3. **Test**: Run brown eyes test prompt with epoch 2, 5, 10
4. **Compare**: Side-by-side with V1 to see brown eyes fix
5. **Deploy**: Use best epoch as new PRODUCTION model

---

## Important Notes

- **Use the SAME base model as V1** (check V1 training page)
- **Keep all default settings that worked for V1**
- **Don't change resolution, bucketing, or augmentation**
- **Download ALL epochs** (not just final)
- **Test epoch 2 first** (historically the best)

The V2.7 training package is ready to upload!
File: `/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke_punks_v2_7_training.zip`

---

## Cost & Time

**Training**: $5-8, ~45-60 minutes
**Downloads**: Free, ~5 minutes (10 files × 218MB)
**Testing**: Free (local), ~15 minutes

**Total**: ~$6 and 1-2 hours start to finish

Good luck! The brown eyes fix should work once trained on CivitAI! 🎨
