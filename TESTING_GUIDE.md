# Testing Your Bespoke Punks LoRA Models

Complete guide for testing your trained CivitAI models using multiple methods.

## 📦 What You Have

**Location:** `models/civitai_bespoke_punks_v1/`

- Epoch 1-10 checkpoints (11 files total)
- Each is 218MB
- Final model: `Bespoke_Punks_24x24_Pixel_Art.safetensors`

## 🎯 Recommended Testing Order

Test these epochs to find the best performer:
1. **Epoch 5** - Often the "sweet spot" before overfitting
2. **Epoch 7** - Mid-late training, good refinement
3. **Epoch 10** - Final model (may be over-trained)

💡 **Important:** The best model is often NOT the final epoch!

---

## Method 1: Python Script (Automated Comparison) ⚡

**Best for:** Quickly comparing multiple epochs with consistent settings.

### Setup

```bash
# Install dependencies
pip install diffusers transformers accelerate safetensors pillow torch

# For Apple Silicon (M1/M2/M3)
# torch is already optimized for MPS

# For NVIDIA GPUs
pip install xformers  # Optional but recommended
```

### Run Tests

```bash
python test_civitai_models.py
```

**What it does:**
- Tests epochs 2, 5, 7, and 10
- Generates 4 test images per epoch (16 total)
- Creates comparison grids automatically
- Saves everything to `test_outputs/`

**Output structure:**
```
test_outputs/
├── epoch_02/
│   ├── basic_test.png
│   ├── coordinate_test.png
│   ├── accessory_test.png
│   └── creative_test.png
├── epoch_05/
├── epoch_07/
├── epoch_10/
├── comparison_basic_test.png
├── comparison_coordinate_test.png
├── comparison_accessory_test.png
└── comparison_creative_test.png
```

**Estimated time:** 10-20 minutes depending on hardware

---

## Method 2: ComfyUI (Interactive Visual Testing) 🎨

**Best for:** Visual experimentation and fine-tuning.

### Setup ComfyUI

```bash
# Clone ComfyUI (if not already installed)
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Copy your models
mkdir -p models/loras
cp ../bespokebaby2/models/civitai_bespoke_punks_v1/*.safetensors models/loras/
```

### Launch ComfyUI

```bash
python main.py
```

Then open: http://127.0.0.1:8188

### ComfyUI Workflow

I've created a workflow file for you. Load it in ComfyUI:

**File:** `comfyui_bespoke_punks_workflow.json`

**Workflow includes:**
- SDXL base model loader
- LoRA loader (switch between epochs)
- Prompt inputs for testing
- Image output
- Batch processing option

### Quick ComfyUI Testing Steps

1. **Load the workflow:** File → Load → `comfyui_bespoke_punks_workflow.json`
2. **Select LoRA:** Choose epoch to test (e.g., epoch 5)
3. **Set LoRA strength:** Start with 1.0
4. **Enter prompt:**
   ```
   bespoke, 24x24 pixel art portrait, female, purple background, brown hair, blue eyes, right-facing
   ```
5. **Click "Queue Prompt"**
6. **Compare results:** Try different epochs with same prompt

---

## Method 3: Automatic1111 WebUI 🖼️

**Best for:** Full-featured UI with extensive options.

### Setup A1111

```bash
# Clone WebUI (if not already installed)
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# Copy your models
cp ../bespokebaby2/models/civitai_bespoke_punks_v1/*.safetensors models/Lora/

# Launch
./webui.sh  # Mac/Linux
# OR
webui-user.bat  # Windows
```

### A1111 Testing Steps

1. **Open WebUI:** http://127.0.0.1:7860
2. **Select base model:** SDXL 1.0
3. **Enable LoRA:**
   - Click "Show extra networks"
   - Go to "Lora" tab
   - Click on your epoch (e.g., epoch 5)
4. **Set prompt:**
   ```
   bespoke, 24x24 pixel art portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing
   Negative: blurry, low quality, 3d, photorealistic, smooth
   ```
5. **Settings:**
   - Sampling steps: 30
   - CFG Scale: 7.5
   - Width/Height: 512x512
   - Batch count: 1
6. **Generate**
7. **Switch LoRA:** Test different epochs with same settings

### A1111 Comparison Tips

- Use **X/Y/Z Plot** for automatic epoch comparison
- Set X axis: "LoRA"
- Values: `Bespoke_Punks_24x24_Pixel_Art-000005, Bespoke_Punks_24x24_Pixel_Art-000007, Bespoke_Punks_24x24_Pixel_Art`
- Generates grid automatically

---

## 🧪 Test Prompts to Use

### Basic Test
```
bespoke, 24x24 pixel art portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing
```

### Advanced Coordinate Test
```
bespoke, 24x24 pixel grid portrait, symbolic punk style, vibrant orange solid background, black hair starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12), brown iris eyes at (9,12) and (14,12), black nose dot at (11,13), pink lips spanning x=10-13 y=15-16, tan skin tone with jaw defined at y=19, blue collar at bottom edge y=20-22, right-facing, pure pixel art with no gradients or anti-aliasing
```

### Accessory Test
```
bespoke, 24x24 pixel art, male, glasses spanning x=7-16 y=11-13, black hair, green solid background, right-facing profile
```

### Creative Test (not in training set)
```
bespoke, 24x24 pixel art portrait, female, red background, blonde hair, green eyes, dark skin, wearing crown
```

---

## 📊 What to Look For When Comparing

### Quality Checklist

✅ **Pixel Art Style**
- Clean 24x24 pixel grid
- No anti-aliasing or gradients
- Sharp color boundaries

✅ **Prompt Following**
- Correct colors (background, hair, eyes, skin)
- Accurate coordinate placement (if specified)
- Accessories rendered correctly

✅ **Consistency**
- Right-facing profile maintained
- Proper feature placement (eyes, nose, mouth)
- Recognizable Bespoke Punk style

✅ **Generalization**
- Works with prompts NOT in training set
- Handles variations well
- Doesn't copy training images exactly

### Common Issues by Epoch

**Epoch 2:**
- ⚠️ Too early, basic shapes only
- Features may be undefined

**Epoch 5:**
- ✅ Often ideal - learned features without overfitting
- Good balance of accuracy and creativity

**Epoch 7:**
- ✅ Refined quality
- May start showing signs of overfitting

**Epoch 10:**
- ⚠️ May be over-trained
- Could be too specific to training set
- May lack creativity with new prompts

---

## 🎯 Decision Matrix

After testing, score each epoch (1-5 stars):

| Criteria | Epoch 5 | Epoch 7 | Epoch 10 |
|----------|---------|---------|----------|
| Pixel art quality | ⭐⭐⭐⭐⭐ | | |
| Prompt accuracy | ⭐⭐⭐⭐⭐ | | |
| Consistency | ⭐⭐⭐⭐ | | |
| Creativity | ⭐⭐⭐⭐⭐ | | |
| **Total** | **19/20** | | |

**Winner:** The epoch with highest total score

---

## 💾 After Choosing Your Best Model

Once you've identified the best epoch:

```bash
# Copy best model to easy-to-use location
cp models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000005.safetensors \
   models/bespoke_punks_BEST.safetensors

# Document your choice
echo "Best model: Epoch 5" > models/BEST_MODEL.txt
echo "Tested: 2025-11-08" >> models/BEST_MODEL.txt
echo "Reason: Best balance of quality and creativity" >> models/BEST_MODEL.txt
```

---

## 🚀 Quick Start Commands

**Method 1 - Python Script:**
```bash
python test_civitai_models.py
```

**Method 2 - ComfyUI:**
```bash
cd ComfyUI && python main.py
```

**Method 3 - Automatic1111:**
```bash
cd stable-diffusion-webui && ./webui.sh
```

---

## 📈 Performance Tips

### For Apple Silicon (M1/M2/M3)
- Use MPS backend (automatic in script)
- Enable attention slicing
- 512x512 resolution works well
- Expected: 30-60 seconds per image

### For NVIDIA GPUs
- Install xformers for speed boost
- Can use higher resolutions (768x768)
- Expected: 10-30 seconds per image

### For CPU (Not Recommended)
- Very slow (5-10 minutes per image)
- Use lower resolution (256x256)
- Consider using cloud GPU instead

---

## ❓ Troubleshooting

**"Out of memory" error:**
```python
# In test script, reduce resolution:
GEN_SETTINGS = {
    "width": 256,
    "height": 256,
    # ... other settings
}
```

**"Model not loading" error:**
- Check file paths are correct
- Verify .safetensors files aren't corrupted
- Ensure SDXL base model is downloaded

**"Poor quality results":**
- Try different CFG scale (5.0 - 10.0)
- Adjust LoRA strength (0.7 - 1.0)
- Increase inference steps (40-50)

---

## 📝 Documentation Template

After testing, document your findings:

```markdown
# Model Testing Results

**Date:** 2025-11-08
**Tested By:** [Your Name]

## Models Tested
- Epoch 5
- Epoch 7
- Epoch 10

## Test Results

### Epoch 5
- Quality: Excellent
- Prompt following: 9/10
- Notes: Best overall, good creativity

### Epoch 7
- Quality: Very Good
- Prompt following: 8/10
- Notes: Slightly over-trained

### Epoch 10
- Quality: Good
- Prompt following: 7/10
- Notes: Too specific to training data

## Final Decision
**Best Model:** Epoch 5
**Reason:** Best balance of quality, accuracy, and generalization
```

---

**Ready to test? Start with Method 1 (Python script) for automated comparison!**
