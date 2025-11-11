# RunPod Deployment - Phase 2 (256px Training) - READY 🚀

**Date:** 2025-11-10
**Status:** ✅ READY FOR DEPLOYMENT
**Owner:** Ilyssa Evans | Bespoke Labs

---

## ✅ What's Ready

### Dataset: 256px + Enhanced Captions
- ✅ **203 images** resized to 256x256 (high-quality Lanczos)
- ✅ **203 captions** enhanced with structural detail (Phase 1A)
- ✅ All backups created (512px images + config)
- ✅ Training config updated for 256px

### Location
**Package:** `/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/`
```
runpod_package/
├── training_config.toml  ✅ Updated for 256px
└── training_data/
    ├── *.png             ✅ 203 images @ 256x256
    └── *.txt             ✅ 203 enhanced captions
```

---

## 📋 RunPod Deployment Steps

### 1. Upload Package to RunPod

**Option A: Direct Upload (if RunPod supports it)**
```bash
# Zip the package
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2
zip -r runpod_package_256px.zip runpod_package/

# Upload via RunPod web interface
# Size: ~50-100 MB
```

**Option B: Use RunPod Storage (recommended for speed)**
```bash
# Upload to RunPod network storage
# Then extract on GPU instance
```

### 2. Start RunPod Instance

**GPU:** A100 (80GB VRAM) recommended
**Docker Image:** `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
**Disk Space:** 50 GB minimum
**Network Storage:** 20 GB recommended

### 3. Install Dependencies on RunPod

```bash
# SSH into RunPod instance
cd /workspace

# Install required packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install diffusers transformers accelerate safetensors
pip install xformers
pip install bitsandbytes
pip install toml

# Install training framework (sd-scripts or kohya_ss)
git clone https://github.com/kohya-ss/sd-scripts
cd sd-scripts
pip install -r requirements.txt
```

### 4. Upload Training Data

```bash
# Copy training package to /workspace
cd /workspace
unzip runpod_package_256px.zip

# Verify files
ls -lh runpod_package/training_data/*.png | head -5
cat runpod_package/training_config.toml | grep resolution
```

### 5. Start Training

```bash
cd /workspace/sd-scripts

# Run training
accelerate launch --num_cpu_threads_per_process=2 \
  train_network.py \
  --config_file=/workspace/runpod_package/training_config.toml

# Monitor logs
tail -f /workspace/logs/caption_fix_experiment.log
```

**Expected runtime:** 8-12 hours for 8 epochs

---

## 📊 Training Configuration (Final)

```toml
[general]
bucket_resolution = 256       # ✅ CHANGED from 512
min_bucket_reso = 256
max_bucket_reso = 512         # ✅ CHANGED from 1024

[model_arguments]
pretrained_model_name_or_path = "runwayml/stable-diffusion-v1-5"

[network_arguments]
network_dim = 32
network_alpha = 16

[training_arguments]
max_train_epochs = 8          # ✅ CHANGED from 9 (optimal point)
train_batch_size = 4
mixed_precision = "bf16"
learning_rate = 1e-4
resolution = "256,256"        # ✅ CHANGED from "512,512"

[dataset]
keep_tokens = 1
caption_dropout_rate = 0.02
```

---

## 🎯 Expected Results

### Quantitative Improvement
- **Pixel defects:** 60% → 30% (50% reduction)
- **Accessory rendering:** 50% → 75% (with enhanced captions)
- **Overall clean images:** 40% → 70-75%

### Qualitative Improvement
- ✅ Fewer stray wrong-color pixels
- ✅ Better hat/sunglasses/bow rendering
- ✅ Clearer eye placement
- ✅ Better feature color distinction

### Target Metrics (Epoch 8)
- Average unique colors: <220
- Green background test: <200
- "Messy images" rate: <30%

---

## 🔍 Post-Training Testing

### Test Script (Same as Current)
Use same 7 test prompts to compare directly:

```python
TEST_PROMPTS = [
    ("green_bg_lad", "pixel art, 24x24, portrait of bespoke punk lad, brown hair, brown eyes, medium male skin tone, bright green background..."),
    ("brown_eyes_lady", "..."),
    ("golden_earrings", "..."),
    ("sunglasses_lad", "..."),
    ("melon_lady", "..."),
    ("cash_lad", "..."),
    ("carbon_lad", "..."),
]
```

**Generate from Epochs 1-8**, count unique colors, compare with current Epoch 8 (512px).

---

## 💰 Cost Estimate

**GPU:** A100 (80GB) @ $1.69/hour
**Training Time:** 8-12 hours (8 epochs)
**Estimated Cost:** $13.50 - $20.30

**Breakdown:**
- Epoch 1-4: ~4 hours ($6.76)
- Epoch 5-8: ~4-8 hours ($6.76-$13.52)
- **Total: ~$17**

**ROI:** High - expected to solve 50-70% of quality issues

---

## 📁 Backups (Safe to Revert)

All originals backed up before changes:

- **512px images:** `/Users/ilyssaevans/Documents/GitHub/bespokebaby2/training_data_512px_backup/`
- **512px config:** `/Users/ilyssaevans/Documents/GitHub/bespokebaby2/training_config_512px_backup.toml`
- **Original captions:** `/Users/ilyssaevans/Documents/GitHub/bespokebaby2/caption_backups/phase1a_backup/`

**To revert (if needed):**
```bash
# Restore 512px images
cp training_data_512px_backup/*.png runpod_package/training_data/

# Restore 512px config
cp training_config_512px_backup.toml runpod_package/training_config.toml

# Restore original captions
cp caption_backups/phase1a_backup/*.txt runpod_package/training_data/
```

---

## ✅ Checklist Before Deployment

Pre-flight checks:

- [x] All 203 images resized to 256x256
- [x] All 203 captions enhanced (Phase 1A)
- [x] Training config updated for 256px
- [x] Backups created (512px + original captions)
- [x] Preparation log documented
- [ ] Package zipped for upload
- [ ] RunPod instance started
- [ ] Dependencies installed
- [ ] Training launched

---

## 🎯 Success Criteria

**Minimum Acceptable:**
- 30%+ reduction in pixel defects
- 25%+ improvement in accessory rendering
- At least one epoch better than current Epoch 8 (512px)

**Target Success:**
- 50%+ reduction in pixel defects
- 40%+ improvement in accessory rendering
- Epoch 8 (256px) significantly better than Epoch 8 (512px)

**Best Case:**
- 70%+ clean images (vs current 40%)
- Production-ready checkpoint at Epoch 8
- Deploy immediately

---

## 📞 Next Steps After Training

1. **Download all 8 epoch checkpoints** from RunPod
2. **Test each epoch** with 7 test prompts
3. **Count unique colors** and visual inspection
4. **Compare side-by-side** with current Epoch 8 (512px)
5. **Select best epoch** for production
6. **Create results collage** (256px vs 512px comparison)
7. **Update documentation** with findings
8. **Make deployment decision**

---

## 🚀 Ready to Launch!

**All systems go:**
- ✅ Dataset prepared (256px + enhanced captions)
- ✅ Config optimized (8 epochs, 256px resolution)
- ✅ Backups secured
- ✅ Cost estimated (~$17)
- ✅ Success criteria defined

**Deploy when ready!**

**Expected timeline:**
- Upload: 30 min
- Training: 8-12 hours
- Testing: 4-6 hours
- **Results: 2-3 days**

---

**Confidence level:** 90% this will significantly improve quality 🎯

**Good luck!** 🚀
