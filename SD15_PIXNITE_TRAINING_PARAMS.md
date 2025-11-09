# 🎯 SD 1.5 PixNite Training Parameters (Option 2)

## CivitAI Training Setup

### Step 1: Upload Same Data
- Use the SAME zip file: `bespoke_punks_v3_training.zip`
- Already has 203 images + captions
- Ready to go!

---

## Step 2: Base Model Selection

**Click**: Custom (5th option)
**Search for**: "PixNite" or "PixNite 1.5"
**Select**: **PixNite 1.5 - Pure Pixel Art**
- Link: https://civitai.com/models/294183/pixnite-15-pure-pixel-art

---

## Step 3: Training Parameters

### CRITICAL SETTINGS:

| Setting | Value | Notes |
|---------|-------|-------|
| **Base Model** | PixNite 1.5 - Pure Pixel Art | Custom model |
| **Resolution** | **64** or **128** | Try 64 first, if rejected use 128 |
| **Epochs** | **3** | Same as before |
| **Train Batch Size** | **4** | Same |
| **Network Dim (LoRA Rank)** | **32** | Same |
| **Network Alpha** | **16** | Same |
| **Learning Rate (Unet LR)** | **0.0001** | Same |
| **Text Encoder LR** | **0.00005** | Same |
| **Clip Skip** | **1** | ⚠️ SD 1.5 uses 1, NOT 2 |
| **LR Scheduler** | **cosine_with_restarts** | Same |
| **Optimizer** | **AdamW8Bit** | Same |
| **Enable Bucket** | **OFF** ❌ | Critical! |
| **Flip Augmentation** | **OFF** ❌ | Critical! |
| **Shuffle Tags** | **OFF** ❌ | We have captions |

### Other Settings (Leave as default):
- Num Repeats: 1
- Keep Tokens: 0
- Min SNR Gamma: 5
- Noise Offset: 0.1
- LR Scheduler Cycles: 3

---

## Step 4: Trigger Word

**Set to**: `pixel art` (same as before)

---

## Expected Results

**Cost**: ~$2-3 (cheaper than SDXL)
**Time**: ~20-30 minutes
**File size**: Smaller than SDXL LoRA

**Why this should work better:**
- ✅ PixNite designed for "pure pixel art"
- ✅ "Minimum number of colors"
- ✅ SD 1.5 = simpler, might follow our data better
- ✅ Not sprite-focused (unlike Nova Pixels XL)
- ✅ May allow lower resolution (64 vs 512)

---

## Quick Checklist:

1. [ ] Upload: `bespoke_punks_v3_training.zip`
2. [ ] Set trigger word: `pixel art`
3. [ ] Base Model: Custom → **PixNite 1.5 - Pure Pixel Art**
4. [ ] Resolution: **64** (try this first) or **128**
5. [ ] Clip Skip: **1** (not 2!)
6. [ ] Enable Bucket: **OFF**
7. [ ] Flip Augmentation: **OFF**
8. [ ] Network Dim: **32**
9. [ ] Network Alpha: **16**
10. [ ] Epochs: **3**
11. [ ] Start Training!

---

## If Resolution 64 is Rejected:

Try these in order:
1. **64** (ideal for pixel art)
2. **128** (still small)
3. **256** (compromise)
4. **512** (fallback)

The smaller the better for pixel art!

---

## After Training:

Download all 3 epochs:
- PixNite_BespokePunks-000001.safetensors (Epoch 1)
- PixNite_BespokePunks-000002.safetensors (Epoch 2)
- PixNite_BespokePunks-000003.safetensors (Epoch 3)

Test with prompts:
```
pixel art, 24x24, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin
```

Should generate: **Heads only, not full body sprites!**
