# 🎨 Bespoke Punk Production Workflow

**Complete pipeline**: User Photo → Bespoke Punk NFT

Uses **SD 1.5 Epoch 7 LoRA** (best accuracy with brown eyes and all accessories)

---

## 🎯 Quick Start

```bash
# Generate bespoke punk from user photo
python user_to_bespoke_punk_PRODUCTION.py user_photo.jpg

# Specify gender
python user_to_bespoke_punk_PRODUCTION.py user_photo.jpg --gender lad

# Custom output name
python user_to_bespoke_punk_PRODUCTION.py user_photo.jpg --output my_punk

# Reproducible generation (same seed = same result)
python user_to_bespoke_punk_PRODUCTION.py user_photo.jpg --seed 42
```

---

## 📋 What It Does

### Step 1: **Analyze Photo**
Extracts features from user's photo:
- Hair color (black, brown, blonde, red, blue, etc.)
- Eye color (brown, blue, green, black, gray)
- Skin tone (light, medium, dark)
- Background color (for solid background)

### Step 2: **Generate Prompt**
Creates training-format prompt matching **exact vocabulary** used in training:

```
pixel art, 24x24, portrait of bespoke punk lady,
brown hair, brown eyes, light skin, blue solid background,
sharp pixel edges, hard color borders, retro pixel art style
```

### Step 3: **Generate with Epoch 7 LoRA**
- Uses **SD 1.5** base model
- Applies **Epoch 7 LoRA** (proven best results)
- Generates at 512x512 resolution
- Uses same settings as training tests:
  - 30 inference steps
  - Guidance scale 7.5
  - Negative prompt: `blurry, smooth, gradients, antialiased, photography, realistic, 3d render`

### Step 4: **Create 24x24 NFT**
- Downscales to 24x24 using **nearest-neighbor** (preserves pixel art)
- Final NFT-ready image

---

## 📁 Outputs

For input `user_photo.jpg` with default output name:

```
output_512.png     # 512x512 full resolution
output_24x24.png   # 24x24 final NFT
```

---

## ⚙️ Requirements

### 1. Python Packages

```bash
pip install torch diffusers pillow numpy transformers accelerate
```

### 2. Epoch 7 LoRA

**Default path**: `/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000007.safetensors`

If your LoRA is elsewhere:
```bash
python user_to_bespoke_punk_PRODUCTION.py user_photo.jpg \
  --lora /path/to/bespoke_punks_SD15_PERFECT-000007.safetensors
```

### 3. SD 1.5 Base Model

Auto-downloaded on first run (~4GB)
- Model: `runwayml/stable-diffusion-v1-5`
- Cached in `~/.cache/huggingface/hub/`

---

## 🎨 Usage Examples

### Example 1: Simple Generation

```bash
python user_to_bespoke_punk_PRODUCTION.py photos/user1.jpg
```

Output:
```
======================================================================
BESPOKE PUNK GENERATION PIPELINE
======================================================================

Step 1: Analyzing user photo...
   Detected:
     Hair: brown
     Eyes: brown
     Skin: light

Step 2: Generating training-format prompt...
   Prompt: pixel art, 24x24, portrait of bespoke punk lady, brown hair, brown eyes, light skin, blue solid background, sharp pixel edges, hard color borders, retro pixel art style

Step 3: Generating with Epoch 7 LoRA...
   Loading SD 1.5 with Epoch 7 LoRA...
   Device: mps
   ✓ Loaded successfully!
   Generating bespoke punk...
   ✓ Generated 512x512 image

Step 4: Creating 24x24 NFT...
   ✓ 24x24 NFT created (12 colors)

======================================================================
✅ GENERATION COMPLETE!
======================================================================

💾 Saved:
   512x512: output_512.png
   24x24:   output_24x24.png
```

### Example 2: Male Punk (Lad)

```bash
python user_to_bespoke_punk_PRODUCTION.py photos/user2.jpg --gender lad --output male_punk
```

### Example 3: Reproducible Generation

```bash
# Generate with seed 42
python user_to_bespoke_punk_PRODUCTION.py user.jpg --seed 42 --output version1

# Later... generate again with same seed
python user_to_bespoke_punk_PRODUCTION.py user.jpg --seed 42 --output version2

# version1 and version2 will be identical!
```

---

## 🎯 Why Epoch 7?

Based on comprehensive testing of all 10 epochs:

### ✅ Epoch 7 Wins:
- **Brown eyes render correctly** (epochs 1-6 fail - render as blue)
- All jewelry/accessories visible (earrings, necklaces, bows)
- Clean bespoke punk aesthetic (not overtrained)
- Simple, blocky pixel art style
- Solid color backgrounds working

### ⚠️ Other Epochs:
- **Epochs 1-6**: Brown eyes fail, render as blue/mixed
- **Epoch 9**: Also good, slightly more refined
- **Epoch 10**: Risk of overtraining artifacts

---

## 🔧 Advanced: Customization

### Modify Background Colors

Edit the script to add custom background:

```python
# In user_to_bespoke_punk_PRODUCTION.py, line ~97
features = {
    'hair_color': extractor.detect_hair_color(),
    'eye_color': extractor.detect_eye_color(),
    'skin_tone': extractor.detect_skin_tone(),
    'background_color': 'purple',  # ← Change this!
}
```

Available backgrounds:
- blue, green, red, purple, orange, yellow
- pink, gray, brown, teal, cyan

### Add Accessories (Manual)

To add specific accessories like earrings or sunglasses, modify the prompt generation:

```python
# In generate() method, add after skin_tone:
prompt_parts.append("wearing golden earrings")
prompt_parts.append("wearing black stunner shades")
```

---

## 📊 Training Prompt Template

The exact template used during training:

```
pixel art, 24x24, portrait of bespoke punk [lady/lad],
[hair color + style],
[accessories if any],
[eye color],
[skin tone],
[background color] solid background,
sharp pixel edges,
hard color borders,
retro pixel art style
```

**Critical keywords** (do not remove):
- `pixel art`
- `24x24`
- `bespoke punk`
- `sharp pixel edges`
- `hard color borders`
- `retro pixel art style`

These trigger the trained LoRA weights!

---

## 🚀 Next Steps: Web Interface

To build a web UI for this pipeline:

### Option 1: Gradio (Quick & Easy)

```python
import gradio as gr

pipeline = UserToBespokePunkPipeline(lora_path)

def generate_punk(image, gender):
    result = pipeline.process(image, gender=gender)
    return result['image_512'], result['image_24'], result['prompt']

demo = gr.Interface(
    fn=generate_punk,
    inputs=[
        gr.Image(type="filepath", label="Upload Photo"),
        gr.Radio(["lady", "lad"], label="Gender", value="lady")
    ],
    outputs=[
        gr.Image(label="512x512"),
        gr.Image(label="24x24 NFT"),
        gr.Textbox(label="Generated Prompt")
    ],
    title="Bespoke Punk Generator",
    description="Upload your photo → Get your Bespoke Punk NFT!"
)

demo.launch()
```

### Option 2: Integrate with Existing Next.js App

See: `app/generate/page.tsx` for web interface integration

---

## 🔍 Troubleshooting

### Issue: "LoRA not found"
```
❌ Error: LoRA not found: /Users/.../bespoke_punks_SD15_PERFECT-000007.safetensors
```

**Solution**: Download epoch 7 from RunPod output, or specify correct path:
```bash
python user_to_bespoke_punk_PRODUCTION.py user.jpg --lora /path/to/epoch7.safetensors
```

### Issue: "Out of memory"
```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Solution**: Use CPU (slower but works):
```python
# Edit line ~198 in user_to_bespoke_punk_PRODUCTION.py
device = "cpu"  # Force CPU
```

### Issue: Brown eyes still blue
```
# Generated punk has blue eyes instead of brown
```

**Solution**: Verify you're using **epoch 7** (not earlier epochs):
```bash
# Check LoRA filename
ls -lh /Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-*
```

Should see: `bespoke_punks_SD15_PERFECT-000007.safetensors`

---

## 📝 API Reference

### UserToBespokePunkPipeline

```python
from user_to_bespoke_punk_PRODUCTION import UserToBespokePunkPipeline

# Initialize
pipeline = UserToBespokePunkPipeline(
    lora_path="/path/to/epoch7.safetensors"
)

# Generate
result = pipeline.process(
    user_image_path="photo.jpg",
    gender="lady",  # or "lad"
    seed=42  # optional, for reproducibility
)

# Result dict contains:
{
    'image_512': PIL.Image,      # 512x512 image
    'image_24': PIL.Image,       # 24x24 NFT
    'prompt': str,               # Generated prompt
    'features': {                # Extracted features
        'hair_color': str,
        'eye_color': str,
        'skin_tone': str,
        'background_color': str
    }
}
```

---

## 📦 File Structure

```
bespokebaby2/
├── user_to_bespoke_punk_PRODUCTION.py    # Main production script
├── PRODUCTION_WORKFLOW_README.md         # This file
├── test_SD15_epoch7.py                   # Epoch 7 validation tests
└── Downloads/
    └── bespoke_punks_SD15_PERFECT-000007.safetensors  # Epoch 7 LoRA
```

---

## ✅ Production Checklist

- [x] SD 1.5 base model installed
- [x] Epoch 7 LoRA downloaded
- [x] Python packages installed (`torch`, `diffusers`, `pillow`, `numpy`)
- [x] Test generation working
- [x] Brown eyes rendering correctly
- [x] Accessories visible (earrings, etc.)
- [ ] Web interface deployed (optional)
- [ ] Database integration for storing generated punks (optional)

---

## 🎉 Success Criteria

A successful bespoke punk generation has:

1. ✅ **Correct eye color** (brown eyes = brown, not blue)
2. ✅ **Visible accessories** (earrings, necklaces if specified)
3. ✅ **Clean pixel art style** (blocky, not smooth/detailed)
4. ✅ **Solid color background** (no gradients/patterns)
5. ✅ **12-15 colors** in final 24x24 NFT
6. ✅ **Accurate hair color** matching user photo

---

**Made with epoch 7 LoRA** 🎨
