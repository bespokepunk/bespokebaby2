# 🚀 CivitAI Training Configuration - Bespoke Punks V3

## Base Model Selection

**Model**: Nova Pixels XL v2.0
**Link**: https://civitai.com/models/1856313/nova-pixels-xl
**Type**: Illustrious checkpoint (pixel art specialized)
**Updated**: September 2025 (most recent)

---

## Training Configuration

### Basic Settings

```yaml
Training Type: LoRA
Base Model: Nova Pixels XL v2.0
Model Name: "Bespoke_Punks_V3_PixelArt_24x24"

# CRITICAL SETTINGS
Resolution: 24x24  # NATIVE PIXEL ART RESOLUTION
Enable Buckets: NO  # Force 24x24, no resizing
Flip Augmentation: NO  # Don't flip punks
Color Augmentation: NO  # Preserve exact colors

# LoRA Settings
LoRA Rank (Network Dim): 32
Network Alpha: 16
LoRA Type: Standard

# Training Parameters
Epochs: 3
Save Every N Epochs: 1  # Save all 3 epochs
Batch Size: 4
Learning Rate: 1e-4
LR Scheduler: cosine
Optimizer: AdamW8bit

# Advanced
Mixed Precision: fp16
Gradient Accumulation Steps: 1
Max Token Length: 225
Clip Skip: 2
```

---

## Dataset Information

**Total Images**: 204
**Format**: PNG (24x24 native)
**Captions**: .txt files (same name as images)
**Trigger Word**: "pixel art, 24x24, portrait of bespoke punk"

**Caption Format Example**:
```
pixel art, 24x24, portrait of bespoke punk, bright green solid background (#6ae745), white/grey with green tones hair, covered by black sunglasses eyes, pale grey skin, black sunglasses, black suit/tie, sharp pixel edges, hard color borders
```

---

## Upload Instructions for CivitAI

### Step 1: Package Dataset

Run the packaging script (created below) or manually:

```bash
# The script will create: bespoke_punks_v3_training.zip
python3 package_for_civitai_v3.py
```

**What's included**:
- 204 PNG images (24x24)
- 203 TXT caption files
- Total size: ~500KB

### Step 2: Upload to CivitAI

1. Go to: https://civitai.com/models/train
2. Click "New Training"
3. Select **"LoRA"** training type
4. **CRITICAL**: Select "Nova Pixels XL v2.0" as base model
5. Upload `bespoke_punks_v3_training.zip`

### Step 3: Configure Training

**On CivitAI Training Page**:

1. **Basic Info**:
   - Model Name: `Bespoke_Punks_V3_PixelArt_24x24`
   - Description: "24x24 pixel art LoRA for Bespoke Punks style"
   - Tags: pixel art, portraits, crypto punks, 24x24

2. **Training Settings**:
   - Resolution: **24** (CRITICAL - set to 24x24)
   - LoRA Rank: **32**
   - Network Alpha: **16**
   - Epochs: **3**
   - Batch Size: **4**
   - Learning Rate: **0.0001** (1e-4)
   - LR Scheduler: **cosine**
   - Optimizer: **AdamW8bit**

3. **Advanced Settings**:
   - Enable Buckets: **NO** ✅
   - Flip Augmentation: **NO** ✅
   - Color Augmentation: **NO** ✅
   - Save Every N Epochs: **1** ✅
   - Clip Skip: **2**

4. **Important Checkboxes**:
   - ❌ Don't enable auto-tagging
   - ❌ Don't enable any augmentation
   - ✅ Save every epoch
   - ✅ Keep all checkpoints

### Step 4: Start Training

1. Review settings one more time
2. Click "Start Training"
3. Cost should be ~$5-6
4. Training time: ~6-8 hours

---

## What to Expect

### Training Progress

**Epoch 1** (2-3 hours):
- Model learns basic Bespoke Punk structure
- Colors, basic shapes
- Might be blurry/imperfect

**Epoch 2** (2-3 hours):
- Should show major improvement
- Sharp edges emerging
- Better color accuracy
- **Likely the winner** (based on V1/V2 results)

**Epoch 3** (2-3 hours):
- Refinement
- May be best for complex features
- Could overfit

### Download Checkpoints

When training completes, download ALL 3 epoch checkpoints:
- `Bespoke_Punks_V3_PixelArt_24x24-000001.safetensors` (Epoch 1)
- `Bespoke_Punks_V3_PixelArt_24x24-000002.safetensors` (Epoch 2)
- `Bespoke_Punks_V3_PixelArt_24x24-000003.safetensors` (Epoch 3)

---

## Testing After Training

### Test Prompts

**Test 1: Simple Solid Background**
```
pixel art, 24x24, portrait of bespoke punk, bright green solid background, black hair, blue eyes, light skin, sharp pixel edges
```

**Test 2: Checkered Pattern** (This was hard before!)
```
pixel art, 24x24, portrait of bespoke punk, brown and yellow checkered pattern background, brown hair, brown eyes, tan skin, mustache, sharp pixel edges
```

**Test 3: Gradient Background**
```
pixel art, 24x24, portrait of bespoke punk, pixelated blue gradient background with stepped color transitions, dark brown hair, tan skin, beard, sharp pixel edges
```

**Test 4: Accessories**
```
pixel art, 24x24, portrait of bespoke punk, red solid background, black hair, purple sunglasses, gold earrings, silver necklace, pale skin, sharp pixel edges
```

### Test Settings

```yaml
Model: Nova Pixels XL v2.0 + Bespoke_Punks_V3 LoRA
LoRA Weight: 1.0
Steps: 30
CFG Scale: 7.5
Sampler: Euler
Scheduler: Normal
Resolution: 24x24  # Generate at native resolution
Seed: 12345 (fixed for comparison)
```

### Success Criteria

For each epoch, generate all 4 test prompts and check:

| Criteria | Target | How to Check |
|----------|--------|--------------|
| **Sharp Edges** | 90%+ | Visual inspection - are edges crisp? |
| **Color Count** | 35-50 colors | Count unique colors in output |
| **Pattern Accuracy** | Visible checkerboard | Can you see the checkered pattern? |
| **Gradient Quality** | Stepped, not smooth | Are gradients pixelated? |
| **Overall Match** | 85%+ to originals | Side-by-side comparison |

**If Epoch 2 hits 85%+**: ✅ SUCCESS - we're done with LoRA!
**If 70-85%**: Good progress, might add ControlNet
**If <70%**: Investigate what's wrong, possibly retrain with adjustments

---

## Post-Training: ControlNet Decision

### When to Add ControlNet

**YES, train ControlNet if**:
- LoRA gets 70-85% match (good but not perfect)
- Edges are better but still slightly soft
- Structure is close but needs enforcement

**NO, skip ControlNet if**:
- LoRA alone hits 85%+ match (we're done!)
- Edges are already sharp
- Results look nearly identical to originals

### ControlNet Training (If Needed)

**Dataset**: 204 edge maps (already created in `FORTRAINING6/bespokepunks_edges/`)

**Settings**:
```yaml
Type: Canny ControlNet
Base: Nova Pixels XL v2.0 (same as LoRA)
Resolution: 24x24
Epochs: 3
Learning Rate: 1e-5
Batch Size: 2
Cost: ~$3-4
Time: ~4-6 hours
```

**Usage**:
```python
# At inference, use both:
# 1. Bespoke Punks V3 LoRA (weight: 1.0)
# 2. Bespoke Punks ControlNet (weight: 0.8-1.0)
# 3. Edge map input (extracted from prompt description)
```

This enforces pixel structure while LoRA handles style/colors.

---

## Troubleshooting

### If Training Fails

**Resolution not 24x24**:
- CivitAI might auto-adjust
- Check training logs
- If it trained at 512x512, we need to specify 24 in custom config

**Bucketing enabled**:
- This will resize images
- Make sure it's disabled
- Critical for native 24x24 training

**Out of memory**:
- Reduce batch size to 2 or 1
- Should not happen at 24x24 (very small)

### If Results Are Still Blurry

**Try these adjustments**:
1. Increase LoRA rank to 64 (stronger)
2. Add ControlNet for edge enforcement
3. Try different base (SD 1.5 PixNite instead)
4. Nuclear option: Fine-tune entire model

---

## Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| CivitAI LoRA Training | $5-6 | 3 epochs, 24x24 resolution |
| ControlNet (optional) | $3-4 | Only if needed |
| **Total** | **$5-10** | Depends on ControlNet need |

---

## Timeline

**Today (Saturday)**:
- ✅ Package dataset
- ✅ Upload to CivitAI
- ✅ Start training
- ⏳ Training runs overnight

**Tomorrow (Sunday)**:
- ⏳ Training completes (morning/afternoon)
- ✅ Download 3 epoch checkpoints
- ✅ Test all 3 epochs
- ✅ Identify winner

**Monday**:
- ✅ If >85% match: Package for production, DONE!
- ✅ If 70-85%: Set up ControlNet training
- ⏳ ControlNet trains overnight (if needed)

**Tuesday**:
- ✅ Test LoRA + ControlNet combo
- ✅ Final evaluation
- ✅ Deploy to production

---

## Next Immediate Action

Run the packaging script to create the upload file:

```bash
python3 package_for_civitai_v3.py
```

Then follow upload instructions above!

Expected file: `bespoke_punks_v3_training.zip` (~500KB)
