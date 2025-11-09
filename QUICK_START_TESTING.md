# 🚀 Quick Start: Test Your Models in 5 Minutes

The fastest way to see your trained Bespoke Punks models in action!

## ✅ Prerequisites

You need ONE of these:
- Python 3.10+ (for automated testing)
- ComfyUI (for visual testing)
- Automatic1111 WebUI (for full-featured testing)

---

## 🎯 Fastest Method: Python Script

### 1. Install Dependencies (One-time)

```bash
pip install diffusers transformers accelerate safetensors pillow torch
```

### 2. Run Test Script

```bash
python test_civitai_models.py
```

### 3. Wait 10-20 Minutes

The script will:
- ✅ Test epochs 2, 5, 7, and 10
- ✅ Generate 16 test images
- ✅ Create comparison grids
- ✅ Save everything to `test_outputs/`

### 4. Review Results

```bash
open test_outputs/  # Mac
# OR
explorer test_outputs  # Windows
# OR
xdg-open test_outputs  # Linux
```

Look at:
- `comparison_*.png` - Side-by-side epoch comparisons
- Individual `epoch_XX/` folders for full images

### 5. Choose Winner

Based on quality, choose your best epoch (likely 5 or 7).

---

## 🎨 Visual Method: ComfyUI

### 1. Launch ComfyUI

```bash
cd /path/to/ComfyUI
python main.py
```

### 2. Open Workflow

1. Go to http://127.0.0.1:8188
2. Click **Load** button
3. Select: `bespokebaby2/comfyui_bespoke_punks_workflow.json`

### 3. Test Different Epochs

1. Click on **LoraLoader** node
2. Change model to test different epochs:
   - `Bespoke_Punks_24x24_Pixel_Art-000005.safetensors` (Epoch 5)
   - `Bespoke_Punks_24x24_Pixel_Art-000007.safetensors` (Epoch 7)
   - `Bespoke_Punks_24x24_Pixel_Art.safetensors` (Epoch 10)
3. Click **Queue Prompt**
4. Wait 30-60 seconds for result

### 4. Try Different Prompts

Edit the positive prompt in the workflow:

**Simple:**
```
bespoke, 24x24 pixel art portrait, female, red background, blonde hair, green eyes
```

**Detailed:**
```
bespoke, 24x24 pixel grid portrait, male, blue background, black hair, brown eyes, glasses, right-facing
```

---

## 📊 What to Look For

### Good Results ✅
- Clean 24x24 pixel grid appearance
- Accurate colors matching prompt
- Clear features (eyes, hair, etc.)
- Bespoke Punk style maintained

### Poor Results ❌
- Blurry or anti-aliased
- Wrong colors
- Doesn't follow prompt
- Looks 3D or photorealistic

---

## 🏆 Expected Winner

Based on typical training patterns:

**Epoch 5** usually wins because:
- Learned all features
- Not over-trained yet
- Good generalization
- Creative with new prompts

**Epoch 7** is often second best:
- More refined
- Slightly over-trained
- Still good quality

**Epoch 10** may disappoint:
- Too specific to training data
- Less creative
- May not generalize well

---

## 💡 Quick Tips

### If Results Look Bad
1. Check you're using SDXL base model (not SD 1.5)
2. Try CFG scale between 5-10
3. Use negative prompt: `blurry, 3d, photorealistic, smooth`
4. Ensure prompt includes "bespoke" trigger word

### If Memory Issues
Lower resolution:
- Try 256x256 instead of 512x512
- Use `enable_attention_slicing()` in script
- Close other applications

### Save Time
Only test epochs 5, 7, and 10 first. That's 90% likely to include your winner.

---

## 📋 Quick Comparison Template

After testing 2-3 epochs, fill this out:

```
Epoch 5: ⭐⭐⭐⭐⭐ (Excellent)
Epoch 7: ⭐⭐⭐⭐  (Very Good)
Epoch 10: ⭐⭐⭐    (Good)

Winner: Epoch 5
Reason: Best quality and follows prompts accurately
```

---

## ✨ Next Steps After Testing

1. **Copy best model:**
   ```bash
   cp models/civitai_bespoke_punks_v1/Bespoke_Punks_24x24_Pixel_Art-000005.safetensors \
      models/bespoke_punks_PRODUCTION.safetensors
   ```

2. **Document decision:**
   ```bash
   echo "Production Model: Epoch 5" > models/PRODUCTION_MODEL.txt
   echo "Date: $(date)" >> models/PRODUCTION_MODEL.txt
   ```

3. **Upload to CivitAI** (optional):
   - Share your best model with the community
   - Include test images as examples
   - Document which epoch performed best

---

## ❓ Troubleshooting

**"Model not found" error:**
- Check paths in script/workflow
- Verify files copied correctly to models folder

**"Out of memory" error:**
- Lower resolution (256x256)
- Close other apps
- Try CPU mode (slower but works)

**"Poor quality" results:**
- Verify using SDXL base (not SD 1.5)
- Check LoRA strength (should be 0.8-1.0)
- Try different CFG scale

**Script stuck/frozen:**
- First run downloads SDXL base (~7GB)
- This can take 10-30 minutes
- Watch terminal for progress

---

## 🎉 Success Looks Like

After 20 minutes of testing, you'll have:

✅ Clear winner epoch identified
✅ Test images proving quality
✅ Comparison grids for documentation
✅ Production-ready model selected
✅ Confidence in your training results

**You're ready to generate pixel art punks! 🎨**

---

**Need help?** Check the full guide: `TESTING_GUIDE.md`
