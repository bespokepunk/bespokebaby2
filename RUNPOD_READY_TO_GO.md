# ✅ RunPod Training - Ready to Go!

Everything is configured and ready for RunPod training with W&B sample prompts!

## 🎨 W&B Sample Prompts Included

Your RunPod training will generate sample images every 100 steps using these prompts:

```
1. TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing

2. TOK bespoke punk, 24x24 pixel art, male, orange solid background, black hair, brown eyes, tan skin, right-facing

3. TOK bespoke, 24x24 pixel grid, female, pink background, blonde hair, green eyes, light skin, right-facing

4. TOK bespoke punk style, 24x24 pixel art portrait, male, teal background, red hair, blue eyes with glasses, light skin, right-facing

5. TOK bespoke, 24x24 pixel grid portrait, female, yellow background, black hair, hazel eyes, tan skin, right-facing
```

## 🚀 Quick Start Steps

### Step 1: Create RunPod Instance (5 min)
1. Go to https://www.runpod.io/
2. Click "Deploy" → "GPU Pods"
3. Choose GPU: **RTX 4090** (recommended) or **RTX 3090** (cheaper)
4. Template: "RunPod Pytorch"
5. Disk: 50GB
6. Click "Deploy"

**Estimated Cost**: $2-4 for full training

### Step 2: Connect and Setup (3 min)
In RunPod web terminal:

```bash
# Update and install tools
apt-get update && apt-get install -y git zip unzip

# Clone repository
cd /workspace
git clone https://github.com/bespokepunk/bespokebaby2.git
cd bespokebaby2

# Install dependencies
pip install --upgrade pip
pip install -r requirements_runpod.txt

# Verify
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### Step 3: Start Training (1 min)

**Option A: One-Command Start** (Recommended)
```bash
bash start_training.sh
```

**Option B: With tmux** (Keeps running if disconnected)
```bash
tmux new -s training
bash start_training.sh
# Press Ctrl+B then D to detach
```

## 📊 What Happens During Training

### W&B Monitoring

You'll see in your W&B dashboard (https://wandb.ai):

**Every 100 steps:**
- 🎨 **3 sample images generated** using the prompts above
- 📉 **Loss metrics** tracked
- 📈 **Learning rate curves**
- ⚡ **GPU utilization**

**Every 500 steps:**
- 💾 **Checkpoint saved** to disk

### Terminal Output

```
🎨 BESPOKE PUNK SDXL TRAINING
================================================================================
✅ Loaded 193 training pairs
🚀 Starting training...

Training:  5%|██▌              | 1150/23160 [14:23<4:35:12, 1.33it/s, loss=0.056, lr=7.2e-05]

📊 Step 1150/23160
   Loss: 0.0561
   LR: 7.2e-05
   GPU Memory: 18.4GB

🎨 Generating sample images for W&B...
   Generating 3 sample images...
   ✅ Logged 3 samples to W&B
```

## 📈 Training Timeline

**Total Steps**: ~23,160 (120 epochs × 193 images)

**Progress Markers:**
- **Step 500** (30 min): Basic shapes
- **Step 1,000** (1 hr): Features recognizable
- **Step 2,500** (2.5 hrs): Good quality
- **Step 5,000** (3.5 hrs): High quality
- **Step 10,000+**: Fine-tuning
- **Step 23,160** (5 hrs): Complete! ✅

## 🎨 Sample Image Quality

You'll see image quality improve in W&B:

**Early (Step 500)**:
- Basic colors and shapes
- Rough features
- Some pixelation

**Mid (Step 2,500)**:
- Clear faces
- Accurate colors
- Good pixel definition

**Late (Step 10,000+)**:
- Sharp pixel art
- Accurate features
- Perfect style

## 💾 Checkpoints Saved

Every 500 steps, model saved to:
```
./models/bespoke_punk_sdxl/checkpoint-500/
./models/bespoke_punk_sdxl/checkpoint-1000/
./models/bespoke_punk_sdxl/checkpoint-1500/
...
./models/bespoke_punk_sdxl/final_model/
```

**Pro Tip**: Best model often at step 8,000-12,000, not final!

## 🔍 Monitoring Checklist

During training, check:

✅ **W&B Dashboard**:
- [ ] Loss trending downward
- [ ] Sample images improving
- [ ] No errors in logs

✅ **GPU Usage**:
```bash
nvidia-smi
# Should show 90-100% GPU utilization
```

✅ **Training Progress**:
- [ ] No OOM errors
- [ ] Steps completing (not stuck)
- [ ] Loss not exploding (>1.0)

## 🎯 After Training

### Test Your Model
```bash
python test_model.py --model_path ./models/bespoke_punk_sdxl/final_model
```

### Download Model
```bash
cd /workspace/bespokebaby2/models
zip -r bespoke_punk_final.zip bespoke_punk_sdxl/final_model
# Download via RunPod file browser
```

### Upload to Hugging Face
```bash
pip install huggingface_hub
huggingface-cli login --token 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
cd /workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model
huggingface-cli upload codelace/bespoke-punk-sdxl . --repo-type model
```

## ⚠️ IMPORTANT: Stop Your Pod!

When training is complete:
1. Download your model
2. Go to RunPod dashboard
3. Click **"Stop"** on your pod
4. Confirm stop

**Don't forget or you'll keep getting charged!** 💰

## 📝 All Settings Pre-Configured

Your training includes:

✅ **Core Settings**:
- Resolution: 512px
- Batch size: 4
- Epochs: 120
- Learning rate: 8e-5
- LoRA rank: 16

✅ **W&B Settings**:
- Project: "bespoke-punk-sdxl"
- Sample interval: 100 steps
- 5 test prompts built-in
- Automatic logging

✅ **Checkpoints**:
- Save every: 500 steps
- Validate every: 100 steps
- Final model saved

## 🎓 Pro Tips

1. **Use tmux** - Keeps training running if you disconnect
2. **Check W&B at step 500** - Verify it's learning correctly
3. **Monitor GPU** - Should be 90-100% utilized
4. **Test multiple checkpoints** - Best might not be final
5. **Don't stop training early** - Let it complete for best results

## 🆚 Comparison with Replicate

You're running both! Here's what to expect:

| | RunPod | Replicate |
|---|---|---|
| **Status** | Starting now | Already running |
| **Time** | 5 hours | 1 hour |
| **Cost** | $2-4 | $3-5 |
| **Model** | SDXL | FLUX |
| **Samples** | Every 100 steps | Every 100 steps |
| **W&B** | Yes ✅ | Yes ✅ |

Both will generate sample images during training for monitoring!

## ✅ You're All Set!

Everything is configured:
- ✅ W&B sample prompts included
- ✅ Trigger word: "TOK"
- ✅ 193 image dataset ready
- ✅ All optimal settings
- ✅ Sample image generation enabled

**Just follow the Quick Start steps above!** 🚀

---

**Need help?** See `RUNPOD_STEP_BY_STEP.md` for detailed walkthrough.
