# 🚀 Option 3 Execution Plan: Pixel Art Base + 24x24 Training + ControlNet

## Timeline: 5 Days Total

### Day 1 (TODAY): Research & Setup
- ✅ Find pixel art base models
- ⏳ Download top 3 candidates
- ⏳ Test generation quality
- ⏳ Extract edge maps from all 203 punks
- ⏳ Update captions

### Day 2-3 (WEEKEND): Training
- Train LoRA on winning base model at 24x24
- Train ControlNet on edge maps
- Both can run in parallel

### Day 4 (MONDAY): Testing
- Generate test images with LoRA
- Generate with LoRA + ControlNet
- Compare to originals
- Evaluate success rate

### Day 5 (TUESDAY): Iterate or Deploy
- If 85%+ success: Package for production
- If 70-85%: Adjust and retrain
- If <70%: Move to nuclear option

---

## 📦 Pixel Art Base Model Candidates

### Top Candidates Found:

#### 1. **【SDXL】Pixel Art | Base** by Husky_AI
- **Type**: Full checkpoint (6.46 GB)
- **Updated**: March 2024
- **Trigger**: "pixel art"
- **Features**: Built-in pixel repair plugin
- **Link**: https://civitai.com/models/276298
- **Rating**: ⭐⭐⭐⭐⭐ (Strong reviews)

#### 2. **Pixel Art Diffusion XL - Sprite Shaper**
- **Type**: Checkpoint based on Husky's model
- **Updated**: 2024
- **Features**: Improved pixel shape quality, trained on more images
- **Link**: https://civitai.com/models/277680
- **Rating**: ⭐⭐⭐⭐

#### 3. **Nova Pixels XL v2.0**
- **Type**: Illustrious checkpoint
- **Updated**: September 2025 (NEWEST)
- **Features**: Specifically for sprite/pixel art
- **Link**: https://civitai.com/models/1856313
- **Rating**: ⭐⭐⭐⭐⭐ (Very recent, might be best)

### SD 1.5 Options (Cheaper to train):
- Searching now...

---

## 🎯 Training Strategy

### Phase 1: LoRA Training

**Base Model**: (TBD - will test all 3)

**Training Settings**:
```yaml
base_model: [Winner from tests]
training_type: LoRA
resolution: 24x24  # CRITICAL - native resolution
lora_rank: 32
network_alpha: 16
epochs: 3
learning_rate: 1e-4
batch_size: 4
optimizer: AdamW8bit
scheduler: cosine
save_every_n_epochs: 1

# Important flags
enable_bucket: false  # Force 24x24, no resizing
color_aug: false      # Don't mess with colors
flip_aug: false       # Don't flip punks
```

**Dataset**:
- 203 Bespoke Punks at native 24x24
- Updated captions (see below)
- No preprocessing (keep originals pure)

**Platform**: CivitAI Training (~$5)

---

### Phase 2: ControlNet Training

**Type**: Canny Edge Detection ControlNet

**Process**:
1. Extract edges from all 203 punks using Canny
2. Create pairs: (original_punk.png, edges.png)
3. Train ControlNet to enforce edge structure

**Training Settings**:
```yaml
controlnet_type: canny
resolution: 24x24
epochs: 3-5
learning_rate: 1e-5
batch_size: 2
```

**Platform**: Could use CivitAI or local (TBD)
**Cost**: ~$3-5

---

## 📝 Caption Updates

### Current Caption Format:
```
bespoke, 24x24 pixel art portrait, brick/checkered red-brown checkered pattern background (#c06148, #a76857), brown hair, brown eyes, tan skin, wearing dark grey hat with gold badge, pure pixel art with no gradients or anti-aliasing
```

### NEW Caption Format for Pixel Art Base:
```
pixel art, 24x24, portrait of bespoke punk, brick/checkered red-brown checkered pattern background (#c06148, #a76857), brown hair, brown eyes, tan skin, dark grey hat with gold badge, sharp pixel edges, hard color borders
```

**Key Changes**:
- ✅ Add "pixel art" trigger for base model
- ✅ Simpler structure (base model handles style)
- ✅ "sharp pixel edges, hard color borders" instead of "no anti-aliasing"
- ✅ "pixelated gradient" for gradient backgrounds
- ✅ Remove redundant "pure pixel art" (base knows this)

---

## 🔧 Edge Extraction Script

```python
#!/usr/bin/env python3
"""Extract Canny edges from all Bespoke Punks for ControlNet training"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image

def extract_edges(img_path, output_path):
    """Extract Canny edges from image"""
    # Read image
    img = cv2.imread(str(img_path))

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    # Low threshold for pixel art (want all edges)
    edges = cv2.Canny(gray, threshold1=30, threshold2=100)

    # Save
    cv2.imwrite(str(output_path), edges)

    return edges

def main():
    input_dir = Path("FORTRAINING6/bespokepunks")
    output_dir = Path("FORTRAINING6/bespokepunks_edges")
    output_dir.mkdir(exist_ok=True)

    for img_path in input_dir.glob("*.png"):
        output_path = output_dir / img_path.name
        extract_edges(img_path, output_path)
        print(f"✓ {img_path.name}")

    print(f"\n✅ Extracted edges for all images")
    print(f"📁 Output: {output_dir}/")

if __name__ == "__main__":
    main()
```

---

## 📊 Success Criteria

After training, generate 20 test punks and compare to originals:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Color Count** | 35-50 colors | Count unique colors |
| **Sharpness** | 90%+ sharp edges | Visual inspection + edge detection |
| **Pixel Accuracy** | 85%+ match | Side-by-side comparison |
| **Gradient Quality** | Stepped, not smooth | Check gradient backgrounds |
| **Overall Similarity** | 85-90% | User judgment + community feedback |

**If we hit 85%+**: SUCCESS - deploy to production
**If 70-85%**: Good progress, iterate on captions or add more ControlNet weight
**If <70%**: Move to nuclear option (full model fine-tune)

---

## 💰 Budget Breakdown

| Item | Cost | Notes |
|------|------|-------|
| Download base models | $0 | Free from CivitAI |
| Test generations | $0 | Local or free tier |
| LoRA training (24x24) | ~$4-6 | CivitAI training |
| ControlNet training | ~$3-5 | CivitAI or local |
| **TOTAL** | **$7-11** | Within $8-10 target |

---

## 🔄 Fallback Plans

### If Pixel Art Base Doesn't Help (unlikely):
- Switch to SD 1.5 + pixel art base (cheaper, faster)
- Or go straight to nuclear option

### If 24x24 Training Fails:
- Try 64x64 or 128x128 as compromise
- Use super-resolution for upscaling

### If ControlNet Isn't Needed:
- Great! Save $3-5
- Deploy with just LoRA

---

## 📅 Detailed Schedule

### TODAY (Saturday):
- [ ] Download Nova Pixels XL, Husky's Pixel Art Base, Sprite Shaper
- [ ] Test each with prompt: "pixel art, 24x24, portrait, green background, black hair"
- [ ] Pick winner based on:
  - Sharp edges (most important)
  - Color accuracy
  - No anti-aliasing
- [ ] Extract edge maps from all 203 punks
- [ ] Update all captions

### SUNDAY:
- [ ] Package training data (images + captions + edges)
- [ ] Upload to CivitAI
- [ ] Start LoRA training (24x24, 3 epochs)
- [ ] Start ControlNet training (parallel)

### MONDAY:
- [ ] Download trained models
- [ ] Test generation pipeline
- [ ] Generate 20 test punks
- [ ] Compare to originals
- [ ] Calculate success metrics

### TUESDAY:
- [ ] If successful: Package for production
- [ ] If needs work: Identify issues and retrain
- [ ] If failed: Discuss nuclear option

---

## ✅ Next Immediate Actions

1. **Download 3 base models** (30 min)
2. **Test generation quality** (1 hour)
3. **Extract edge maps** (script will run in 5 min)
4. **Update captions** (script will run in 10 min)

Then we're ready to train!

Ready to start downloading and testing the base models?
