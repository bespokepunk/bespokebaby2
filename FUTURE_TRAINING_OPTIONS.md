# 🔮 Future Training Options (If V3 Needs Improvement)

## Current V3 Approach (In Progress)

**Status**: Training on Nova Pixels XL v2.0 at 512x512
**Limitation**: CivitAI won't allow 24x24 native training
**Workaround**: Train at 512, downscale to 24x24 with proper quantization
**Expected Result**: 70-80% match to originals

---

## Post-Processing Plan for V3 (When Training Completes)

### Generation Pipeline:
1. **Generate** at 512x512 using Nova Pixels XL + Bespoke Punks V3 LoRA
2. **Downscale** to 24x24 using nearest neighbor (no blur)
3. **Quantize** to 35-40 colors (not 15!)
4. **Sharpen** to enhance pixel edges
5. **Optional**: Apply edge enhancement filter

### Python Script:
```python
from PIL import Image

def process_v3_output(img_512):
    # 1. Downscale with nearest neighbor (no interpolation)
    img_24 = img_512.resize((24, 24), Image.Resampling.NEAREST)

    # 2. Quantize to 40 colors (preserves detail)
    img_24 = img_24.quantize(colors=40, method=2, dither=0).convert('RGB')

    # 3. Optional: Sharpen edges
    img_24 = img_24.filter(ImageFilter.UnsharpMask(radius=1, percent=150))

    return img_24
```

**Expected Improvement**:
- Sharp edges from pixel art base: ✅
- Better color preservation: ✅
- Cleaner downscaling: ✅
- **Overall**: 70-80% match (vs current 60%)

---

## Option A: Kohya_ss (Native 24x24 Training)

**Why**: Full control over resolution, can train at true 24x24

### Setup:
- **Platform**: Local (your computer) or Google Colab
- **Tool**: Kohya_ss GUI or scripts
- **Repository**: https://github.com/bmaltais/kohya_ss

### Advantages:
- ✅ Train at ANY resolution (including 24x24!)
- ✅ Complete control over all settings
- ✅ Free if running locally
- ✅ Can use any base model

### Disadvantages:
- ❌ Requires powerful GPU (or Colab costs ~$10)
- ❌ More complex setup
- ❌ Longer learning curve

### Configuration for 24x24:
```yaml
# kohya config
pretrained_model_name_or_path: "Nova_Pixels_XL_v2.0.safetensors"
resolution: "24,24"  # Native pixel art resolution
train_batch_size: 4
learning_rate: 0.0001
max_train_epochs: 3
network_dim: 32
network_alpha: 16
no_token_padding: true
bucket_no_upscale: true
bucket_reso_steps: 1
enable_bucket: false  # Force 24x24, no bucketing
```

### Cost:
- **Local**: Free (requires RTX 3080+ or similar)
- **Google Colab**: $9.99/month for Colab Pro
- **RunPod**: ~$0.50/hour

### Expected Result:
- **85-90% match** to originals
- True pixel-perfect generation
- No resolution compromise

---

## Option B: SD 1.5 PixNite Base Model

**Why**: SD 1.5 may have lower resolution minimums, designed for pixel art

### Model Details:
- **Name**: PixNite 1.5 - Pure Pixel Art
- **Link**: https://civitai.com/models/294183/pixnite-15-pure-pixel-art
- **Description**: "Minimum number of colors, fewer single pixels"
- **Base**: Stable Diffusion 1.5

### Advantages:
- ✅ Designed specifically for pixel art
- ✅ SD 1.5 = cheaper/faster than SDXL
- ✅ Might allow lower resolution training
- ✅ Known for sharp edges

### Training on CivitAI:
1. Select "SD 1.5" as base type
2. Choose "Custom" → Search "PixNite"
3. Try resolution: 64, 128, or 256 (might allow lower than SDXL)
4. Same other settings (Epochs: 3, LoRA Rank: 32, etc.)

### Expected Cost:
- **~$2-3** (SD 1.5 is cheaper than SDXL)

### Expected Result:
- **75-85% match** to originals
- Faster inference
- Smaller model files

---

## Option C: Hybrid Approach (LoRA + ControlNet)

**Why**: If V3 LoRA alone gets 70-80%, add ControlNet to push to 85-90%

### What We Already Have:
- ✅ Edge maps extracted: `FORTRAINING6/bespokepunks_edges/` (204 images)
- ✅ Ready for ControlNet training

### ControlNet Training:
```yaml
Base: Nova Pixels XL v2.0 (same as LoRA)
Type: Canny Edge Detection
Resolution: 512x512 (or native to what LoRA used)
Epochs: 3
Learning Rate: 1e-5
Batch Size: 2
```

### Usage at Inference:
```python
# Use both together:
# 1. Bespoke Punks V3 LoRA (weight: 1.0) - handles colors/style
# 2. Bespoke Punks ControlNet (weight: 0.8) - enforces edges
# 3. Edge map extracted from prompt
```

### Cost:
- **$3-4** for ControlNet training
- **Total with LoRA**: $5-6

### Expected Result:
- **85-90% match** to originals
- Perfect edge structure
- Style from LoRA + structure from ControlNet

---

## Option D: Fine-Tune Entire Model (Nuclear Option)

**Why**: Complete control, no compromises

### Approach:
- Don't train LoRA
- Fine-tune entire base model on ONLY our 203 Bespoke Punks
- Model forgets everything else, learns ONLY Bespoke Punk style

### Platform Options:
1. **Kohya_ss**: Full fine-tuning mode
2. **Dreambooth**: Classic approach
3. **CivitAI**: May offer full fine-tuning (check)

### Requirements:
- Powerful GPU (A100 recommended)
- More training time (2-3 days)
- Higher cost

### Cost:
- **$50-100** depending on platform/GPU
- **Time**: 1-2 weeks including testing

### Expected Result:
- **95-99% match** to originals
- Pixel-perfect reproduction
- No compromise on any aspect

### File Size:
- **6GB** (vs 200MB for LoRA)
- Harder to distribute
- But ultimate quality

---

## Decision Tree

```
V3 LoRA (512 → 24x24 quantize) completes
│
├─ 85%+ match? ✅ DONE! Use V3 in production
│
├─ 70-85% match?
│  ├─ Add ControlNet → 85-90% match
│  └─ Or try Kohya 24x24 → 85-90% match
│
└─ <70% match?
   ├─ Try SD 1.5 PixNite → 75-85% match
   ├─ Or Kohya 24x24 → 85-90% match
   └─ Or Nuclear Option → 95-99% match
```

---

## Recommended Next Steps (If V3 Isn't Perfect)

### If V3 Gets 70-85%:
**→ Try Kohya at 24x24 first** (free if local, $10 if Colab)
- Most likely to jump to 85-90%
- Worth the effort before spending more

### If V3 Gets 60-70%:
**→ Try SD 1.5 PixNite** ($2-3)
- Different base model might help
- Cheaper to test
- If that fails, move to Kohya

### If Everything Fails:
**→ Nuclear Option** ($50-100)
- Guaranteed 95%+ match
- Worth it if this is for production/commercial use

---

## Tools & Resources

### Kohya_ss:
- **GitHub**: https://github.com/bmaltais/kohya_ss
- **Guide**: https://github.com/bmaltais/kohya_ss/wiki
- **Colab Notebook**: Search "Kohya Colab" on GitHub

### SD 1.5 PixNite:
- **CivitAI**: https://civitai.com/models/294183
- **Alternative**: Pixel Art Sprite Diffusion (SD 1.5)

### ControlNet:
- **Training Guide**: https://github.com/lllyasviel/ControlNet
- **Canny Edge Detection**: Best for pixel art structure

---

## Cost Comparison

| Approach | Cost | Time | Expected Match |
|----------|------|------|----------------|
| V3 (current) | $1-2 | 36 min | 70-80% |
| V3 + ControlNet | $4-6 | 1-2 days | 85-90% |
| Kohya 24x24 | $0-10 | 2-3 days | 85-90% |
| SD 1.5 PixNite | $2-3 | 1 day | 75-85% |
| Nuclear (fine-tune) | $50-100 | 1-2 weeks | 95-99% |

---

## Status Tracking

- [ ] V3 training on Nova Pixels XL (512 resolution) - **IN PROGRESS**
- [ ] Test V3 outputs and evaluate match percentage
- [ ] If <85%, decide next approach
- [ ] Document what works for future reference

---

**Current Priority**: Let V3 finish training (36 min), test it, then decide next steps based on results.
