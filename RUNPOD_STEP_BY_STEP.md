# 🚀 RunPod Setup - Step by Step Guide

Complete walkthrough to get your Bespoke Punk SDXL training running on RunPod.

## Step 1: Create RunPod Instance (5 minutes)

### 1.1 Go to RunPod
- Visit: https://www.runpod.io/
- Sign in to your account

### 1.2 Deploy a GPU Pod
1. Click **"Deploy"** (top right)
2. Select **"GPU Pods"**

### 1.3 Choose Your GPU

**Recommended Options** (pick ONE):

| GPU | VRAM | Speed | Cost/hr | My Pick |
|-----|------|-------|---------|---------|
| **RTX 4090** | 24GB | Fast | $0.44-0.59 | ⭐ BEST VALUE |
| **A40** | 48GB | Very Fast | $0.54-0.79 | ⭐ FASTEST |
| **RTX 3090** | 24GB | Good | $0.29-0.44 | 💰 CHEAPEST |

**How to choose:**
- Click **"GPU Type"** dropdown
- Select one of the above
- Filter by "Secure Cloud" or "Community Cloud"
  - Secure Cloud: More expensive, more reliable
  - Community Cloud: Cheaper, slightly less reliable

### 1.4 Configure Pod Settings

**Template:**
- Select: **"RunPod Pytorch"** or **"RunPod Fast Stable Diffusion"**
- (Either works fine)

**Volume Disk:**
- Set to: **50 GB** minimum
- (Recommended: 100 GB for safety)

**Expose Ports:**
- Leave default (22 for SSH)
- Can also enable Jupyter if you want

**Environment Variables** (optional):
- Skip for now

### 1.5 Deploy!
1. Review configuration
2. Click **"Deploy On-Demand"** (or Spot if you want to save money)
   - **On-Demand**: More reliable, can't be interrupted
   - **Spot**: 50% cheaper, might be interrupted (save work often!)
3. Wait 30-60 seconds for pod to start

**Cost estimate for full training:**
- RTX 4090: 5 hours × $0.50 = **$2.50**
- RTX 3090: 7 hours × $0.35 = **$2.45**

---

## Step 2: Connect to Your Pod (2 minutes)

### 2.1 Get Connection Info

Once pod is running, you'll see:
- **Status**: Green "Running"
- **Connect** button

### 2.2 Open Terminal

**Option A: Web Terminal** (Easiest)
1. Click **"Connect"** button
2. Select **"Start Web Terminal"**
3. Terminal opens in browser ✅

**Option B: SSH** (Advanced)
1. Click **"Connect"** → **"TCP Port Mappings"**
2. Copy SSH command (looks like):
   ```bash
   ssh root@X.X.X.X -p XXXXX -i ~/.ssh/id_ed25519
   ```
3. Run in your local terminal

**Use Option A** (Web Terminal) - it's easier!

---

## Step 3: Setup Environment (3 minutes)

Copy and paste these commands into your RunPod terminal:

### 3.1 Update System
```bash
apt-get update && apt-get install -y git zip unzip
```

### 3.2 Check GPU
```bash
nvidia-smi
```

You should see your GPU info! ✅

### 3.3 Clone Your Repository
```bash
cd /workspace
git clone https://github.com/bespokepunk/bespokebaby2.git
cd bespokebaby2
```

### 3.4 Verify Dataset
```bash
ls FORTRAINING6/all/*.png | wc -l
# Should show: 193

ls FORTRAINING6/oldtext/*.txt | wc -l
# Should show: 193
```

✅ If both show 193, you're good!

### 3.5 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements_runpod.txt
```

This takes 3-5 minutes. You'll see lots of packages installing.

### 3.6 Verify Installation
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

Should show:
```
PyTorch: 2.x.x
CUDA Available: True
GPU: [Your GPU Name]
```

✅ All set!

---

## Step 4: Start Training (1 minute)

### 4.1 Use tmux (Recommended)

Tmux keeps training running even if you disconnect:

```bash
# Start tmux session
tmux new -s training

# Now you're in tmux!
```

**Tmux Quick Reference:**
- `Ctrl+B` then `D` = Detach (keep running in background)
- `tmux attach -t training` = Reattach to session
- `Ctrl+C` = Stop training

### 4.2 Start Training

Simply run:
```bash
bash start_training.sh
```

**OR** with custom settings:
```bash
python runpod_training.py \
  --train_batch_size 4 \
  --num_train_epochs 120 \
  --wandb_api_key 495752e0ee6cde7b8d27088c713f941780d902a1
```

### 4.3 What You'll See

Initial output:
```
🎨 BESPOKE PUNK SDXL TRAINING
================================================================================
📊 Configuration:
   base_model: stabilityai/stable-diffusion-xl-base-1.0
   resolution: 512
   train_batch_size: 4
   num_train_epochs: 120
   learning_rate: 8e-05
   ...

📦 Loading dataset...
✅ Loaded 193 training pairs

📝 Sample training captions:
   1. bespoke, 24x24 pixel grid portrait, symbolic punk style...
   2. bespoke, 24x24 pixel grid portrait, symbolic punk style...
   3. bespoke, 24x24 pixel grid portrait, symbolic punk style...

📥 Loading base model: stabilityai/stable-diffusion-xl-base-1.0
```

Then training starts:
```
Training:   0%|          | 0/23160 [00:00<?, ?it/s]
```

✅ Training has started!

### 4.4 Detach from tmux (Optional)

If you want to close your terminal but keep training:
1. Press `Ctrl+B`
2. Then press `D`

Your training keeps running! ✅

To check back later:
```bash
tmux attach -t training
```

---

## Step 5: Monitor Training

### 5.1 Weights & Biases (Best)

1. Go to: https://wandb.ai
2. Navigate to project: **"bespoke-punk-sdxl"**
3. You'll see:
   - 📉 Loss curves (should trend down)
   - 🎨 Sample images (every 100 steps)
   - 📊 Learning rate schedule
   - ⚡ GPU metrics

**Check at these milestones:**
- Step 500: Basic shapes learned
- Step 1000: Features recognizable
- Step 1500: High quality emerging
- Step 2000+: Fine details

### 5.2 Terminal (If Connected)

Live progress bar:
```
Training: 45%|████████▌     | 10350/23160 [1:23<1:37, 8.2it/s, loss=0.023, lr=6.5e-05]

📊 Step 10350/23160
   Loss: 0.0234
   LR: 6.5e-05
   GPU Memory: 18.4GB
```

### 5.3 GPU Monitoring

In a separate terminal/tmux pane:
```bash
# One-time check
nvidia-smi

# Live monitoring
watch -n 1 nvidia-smi
```

Should show ~90-100% GPU utilization ✅

---

## Step 6: While Training Runs (4-6 hours)

### What to Do

**You can:**
- ✅ Close browser (training continues)
- ✅ Disconnect from pod (if using tmux)
- ✅ Go do other things!
- ✅ Check W&B periodically

**Do NOT:**
- ❌ Click "Stop Pod" in RunPod dashboard
- ❌ Ctrl+C in terminal (unless in tmux)
- ❌ Close SSH without tmux

### Check Progress

Every hour, check W&B:
1. Is loss decreasing? ✅
2. Do sample images look good? ✅
3. Any errors in logs? ❌

**Expected training time:**
- RTX 4090: 4-5 hours
- RTX 3090: 6-8 hours
- A40: 3-4 hours

---

## Step 7: Training Complete!

You'll see:
```
💾 Saving final model...

🎉 TRAINING COMPLETE!
💾 Final model saved to: ./models/bespoke_punk_sdxl/final_model
📊 Final loss: 0.0234
🎯 Total steps: 23160
```

### 7.1 Test Your Model

```bash
python test_model.py --model_path ./models/bespoke_punk_sdxl/final_model
```

This generates 5 test images in `./test_outputs/`

View them:
```bash
# Download via RunPod file browser
# OR view in Jupyter if enabled
```

### 7.2 Download Your Model

**Option A: RunPod File Browser** (Easiest)
1. In RunPod web UI, click on pod
2. Navigate to: `/workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model`
3. Right-click folder → Download

**Option B: Zip and Download**
```bash
cd /workspace/bespokebaby2/models
zip -r bespoke_punk_final.zip bespoke_punk_sdxl/final_model
# Download via file browser
```

**Option C: Upload to Hugging Face**
```bash
pip install huggingface_hub
huggingface-cli login --token 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
cd /workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model
huggingface-cli upload codelace/bespoke-punk-sdxl . --repo-type model
```

---

## Step 8: STOP YOUR POD! ⚠️

**VERY IMPORTANT:**

1. Go to RunPod dashboard
2. Find your pod
3. Click **"Stop"** button
4. Confirm

**If you forget, you'll keep getting charged!** 💰

---

## 🔧 Troubleshooting

### Training Not Starting
```bash
# Check dataset
ls -la FORTRAINING6/all/*.png | wc -l  # Should be 193

# Reinstall dependencies
pip install -r requirements_runpod.txt --force-reinstall

# Check GPU
nvidia-smi
```

### Out of Memory (OOM)
```bash
# Reduce batch size
python runpod_training.py --train_batch_size 1 --gradient_accumulation_steps 4
```

### Lost Connection
```bash
# Reconnect to pod
# In RunPod, click "Connect" → "Start Web Terminal"

# Reattach to tmux
tmux attach -t training
```

### Training Too Slow
```bash
# Check GPU usage
nvidia-smi

# Should show ~95%+ GPU utilization
# If low, might need to adjust batch size
```

---

## ✅ Quick Checklist

Setup:
- [ ] RunPod pod created and running
- [ ] Connected to terminal
- [ ] Repository cloned
- [ ] Dataset verified (193 files)
- [ ] Dependencies installed
- [ ] PyTorch + CUDA working

Training:
- [ ] tmux session started
- [ ] Training command executed
- [ ] W&B monitoring active
- [ ] GPU utilization >90%

Completion:
- [ ] Training finished successfully
- [ ] Test images generated
- [ ] Model downloaded/uploaded
- [ ] **POD STOPPED** ⚠️

---

## 📞 Need Help?

**Common Issues:**

1. **"No module named 'diffusers'"**
   ```bash
   pip install -r requirements_runpod.txt
   ```

2. **"CUDA out of memory"**
   ```bash
   python runpod_training.py --train_batch_size 1
   ```

3. **"Connection lost"**
   - Use tmux (see Step 4.1)
   - Training continues in background

4. **"Dataset not found"**
   ```bash
   # Make sure you're in the right directory
   cd /workspace/bespokebaby2
   ls FORTRAINING6/
   ```

---

**Ready? Let's do this!** Start with Step 1 above. 🚀

Estimated total time: **10 minutes setup + 5 hours training**
