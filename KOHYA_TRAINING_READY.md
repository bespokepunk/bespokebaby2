# Kohya Training Ready - 24x24 Native Resolution

## Status: Ready to Train

Kohya has been installed and configured with two training options:

### Option 1: SDXL (Recommended - Higher Quality)
**Config**: `kohya_config_sdxl_24x24.toml`

**Base Model**: stabilityai/stable-diffusion-xl-base-1.0
**Resolution**: 24x24 native
**Clip Skip**: 2
**Output**: `kohya_output_sdxl/`

**To Run**:
```bash
cd ~/Documents/GitHub/kohya_ss
source venv/bin/activate
python train_network.py --config_file=/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_config_sdxl_24x24.toml
```

### Option 2: SD 1.5 (Faster, Lighter)
**Config**: `kohya_config_sd15_24x24.toml`

**Base Model**: runwayml/stable-diffusion-v1-5
**Resolution**: 24x24 native
**Clip Skip**: 1
**Output**: `kohya_output_sd15/`

**To Run**:
```bash
cd ~/Documents/GitHub/kohya_ss
source venv/bin/activate
python train_network.py --config_file=/Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_config_sd15_24x24.toml
```

---

## Key Differences from Previous Attempts

### ❌ What FAILED (Nova Pixels XL + PixNite):
- **Base Models**: Both Nova Pixels XL and PixNite are SPRITE-FOCUSED
  - Trained on game characters with full bodies
  - Always generate torsos/bodies, not just heads
- **Result**: All epochs from both models showed bodies/torsos

### ✅ What's DIFFERENT (Kohya Approach):
1. **Standard Base Models**: Using vanilla SDXL / SD 1.5
   - NO sprite bias
   - NO pixel art assumptions
   - Clean slate for learning Bespoke Punk head style

2. **True 24x24 Native Training**:
   - CivitAI forced 512 minimum → blurry downscaling
   - Kohya allows TRUE 24x24 → pixel-perfect learning

3. **Complete Control**:
   - No bucketing (strict 24x24)
   - No augmentation (no flips/crops)
   - Exact color preservation

---

## Training Data

**Location**: `/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks/`

**Contents**:
- 203 PNG images (24x24 Bespoke Punk heads)
- 203 TXT captions
- Format: `pixel art, 24x24, portrait of bespoke punk, [description]`

---

## Expected Results

**Training Time** (on Mac M-series):
- SDXL: ~20-40 minutes (3 epochs)
- SD 1.5: ~10-20 minutes (3 epochs)

**Output Files**:
- `bespoke_punks_sdxl_24x24-000001.safetensors` (Epoch 1)
- `bespoke_punks_sdxl_24x24-000002.safetensors` (Epoch 2)
- `bespoke_punks_sdxl_24x24-000003.safetensors` (Epoch 3)
- Sample images generated during training

**What Success Looks Like**:
- Generates HEAD/PORTRAIT only (no bodies)
- 35-50 colors (matches originals)
- Sharp pixel edges (no blur)
- Recognizable Bespoke Punk style

---

## Next Steps

1. **Wait for Nova test to finish** (almost done)
2. **Analyze Nova results** (likely failed like PixNite)
3. **Start SDXL training first** (higher quality)
4. **If SDXL too slow**: Use SD 1.5 instead
5. **Test results**: Generate and compare to originals

---

## Troubleshooting

### If Training Fails

**"Cannot find pretrained model"**:
- Kohya will auto-download on first run
- Requires internet connection
- SDXL download: ~7GB, SD 1.5: ~4GB

**Out of Memory**:
- Edit config: `batch_size = 2` or `batch_size = 1`
- Enable: `gradient_checkpointing = true` (already enabled)

**Too Slow**:
- Switch to SD 1.5 config (much faster)
- Or reduce epochs to 2

**"Resolution too small" error**:
- This is Kohya's advantage - it SUPPORTS 24x24!
- If error persists, check config syntax

---

## Why This Should Work

1. **No Sprite Bias**: Standard models don't assume full bodies
2. **Native Resolution**: Training at actual target size (24x24)
3. **Pixel-Perfect**: No upscaling/downscaling artifacts
4. **Full Control**: Every parameter optimized for pixel art heads

This is the "nuclear option" - if Kohya at 24x24 native doesn't work, then the issue is with the training data itself, not the training method.
