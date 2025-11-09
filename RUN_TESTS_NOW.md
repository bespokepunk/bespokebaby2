# ✅ Everything is Set Up! Run Your Tests Now

All dependencies are installed and ready to go!

## 🚀 Quick Start (Easiest Way)

Just run this command:

```bash
./run_tests.sh
```

That's it! The script will:
1. Activate the virtual environment
2. Run tests on epochs 2, 5, 7, and 10
3. Generate 16 test images
4. Create comparison grids
5. Save everything to `test_outputs/`

**Time:** 10-20 minutes (first run will download SDXL base model ~7GB)

---

## 📊 What Will Happen

### First Run (Longer ~30-40 minutes)
- Downloads SDXL base model (~7GB) - happens once
- Tests all 4 epochs
- Generates 16 images

### Subsequent Runs (~10-20 minutes)
- SDXL already downloaded
- Just generates test images

---

## 📁 Results Location

After testing completes, you'll find:

```
test_outputs/
├── epoch_02/
│   ├── basic_test.png
│   ├── coordinate_test.png
│   ├── accessory_test.png
│   └── creative_test.png
├── epoch_05/
│   ├── basic_test.png
│   ├── coordinate_test.png
│   ├── accessory_test.png
│   └── creative_test.png
├── epoch_07/
│   └── ... (same structure)
├── epoch_10/
│   └── ... (same structure)
├── comparison_basic_test.png
├── comparison_coordinate_test.png
├── comparison_accessory_test.png
└── comparison_creative_test.png
```

---

## 🖥️ System Info

**What you have:**
- ✅ Python 3.13.3
- ✅ Apple Silicon (MPS)
- ✅ PyTorch 2.9.0
- ✅ diffusers, transformers, accelerate (all latest)
- ✅ Virtual environment: `venv_testing/`

**Your Mac will use:**
- MPS (Metal Performance Shaders) for GPU acceleration
- Optimized for M-series chips
- Expected: 30-60 seconds per image

---

## 🎯 Alternative: Manual Run

If you prefer to run manually:

```bash
# Activate virtual environment
source venv_testing/bin/activate

# Run test script
python3 test_civitai_models.py

# When done, deactivate
deactivate
```

---

## 💡 What to Expect

### During Testing:
```
🎨 Bespoke Punks LoRA Model Testing
============================================================
Loading base model: stabilityai/stable-diffusion-xl-base-1.0
Using device: mps

🧪 Testing Epoch 2: Bespoke_Punks_24x24_Pixel_Art-000002.safetensors
  Generating: basic_test...
    ✅ Saved: test_outputs/epoch_02/basic_test.png
  Generating: coordinate_test...
    ✅ Saved: test_outputs/epoch_02/coordinate_test.png
...
```

### When Complete:
```
============================================================
✅ Testing Complete!
📁 Results saved to: /Users/ilyssaevans/Documents/GitHub/bespokebaby2/test_outputs
============================================================

📊 Summary:
  Tested 4 epochs
  Generated 16 images
  Used 4 test prompts

🎯 Next Steps:
  1. Review images in test_outputs/
  2. Compare epoch_05, epoch_07, and epoch_10 folders
  3. Check comparison_*.png files for side-by-side views
  4. Choose the best performing epoch

💡 Note: Epoch 5 or 7 often performs better than the final epoch 10!
```

---

## ⚠️ If You See Errors

### "Out of memory"
Don't worry, the script will reduce resolution automatically. Just let it retry.

### "Model download failed"
Check your internet connection. The script will resume where it left off.

### "No module named..."
The virtual environment didn't activate. Try:
```bash
source venv_testing/bin/activate
python3 test_civitai_models.py
```

---

## 🎨 Ready to Start!

**Just run:**
```bash
./run_tests.sh
```

Then go grab a coffee for 10-20 minutes! ☕

When you come back, you'll have:
- 16 test images across 4 epochs
- 4 comparison grids
- Clear winner identified

**Let's see which epoch is best!** 🏆
