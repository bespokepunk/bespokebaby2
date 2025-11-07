# 🚀 RunPod Training Setup - Bespoke Punk SDXL

Complete guide to train your Bespoke Punk model on RunPod GPU instances.

## 📋 Prerequisites

- RunPod account with credits
- Your training dataset (193 image-caption pairs)
- W&B API key (optional, for monitoring): `495752e0ee6cde7b8d27088c713f941780d902a1`

## 🎯 Quick Start

### 1. Create RunPod Instance

1. Go to [RunPod.io](https://www.runpod.io/)
2. Click **"Deploy"** → **"GPU Pods"**
3. Select a GPU (recommended options below)
4. Choose template: **"RunPod Pytorch"** or **"RunPod Fast Stable Diffusion"**
5. Set disk space: **50GB minimum**
6. Deploy!

#### Recommended GPU Options (sorted by cost/performance):

| GPU | VRAM | Batch Size | Est. Cost/hr | Training Time |
|-----|------|------------|--------------|---------------|
| RTX 4090 | 24GB | 4 | ~$0.50 | 4-6 hours |
| RTX A6000 | 48GB | 8 | ~$0.80 | 3-4 hours |
| A40 | 48GB | 8 | ~$0.60 | 3-4 hours |
| RTX 3090 | 24GB | 2 | ~$0.35 | 6-8 hours |

**Best Value**: RTX 4090 or A40

### 2. Connect to Your Pod

Once your pod is running:
```bash
# Click "Connect" → "Start Web Terminal" or use SSH
ssh root@<your-pod-ip> -p <port> -i ~/.ssh/id_ed25519
```

### 3. Setup Training Environment

Run these commands in your RunPod terminal:

```bash
# Update system
apt-get update && apt-get install -y git zip unzip

# Clone your repository
cd /workspace
git clone https://github.com/bespokepunk/bespokebaby2.git
cd bespokebaby2

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements_runpod.txt

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

### 4. Upload Your Dataset

**Option A: Using Git (if dataset is in repo)**
```bash
# Already done if you cloned the repo with data
ls FORTRAINING6/all  # Should show 193 .png files
ls FORTRAINING6/oldtext  # Should show 193 .txt files
```

**Option B: Upload via RunPod Interface**
```bash
# In RunPod web interface:
# 1. Click "Upload" button
# 2. Upload your bespokebaby2 folder or zip file
# 3. Unzip if needed:
unzip bespokebaby2.zip -d /workspace/
```

**Option C: Download from Cloud Storage**
```bash
# If you have dataset in cloud storage
cd /workspace/bespokebaby2
wget https://your-storage-url/dataset.zip
unzip dataset.zip
```

### 5. Start Training

#### **Quick Start (Default Settings)**
```bash
cd /workspace/bespokebaby2

python runpod_training.py \
  --images_dir ./FORTRAINING6/all \
  --captions_dir ./FORTRAINING6/oldtext \
  --output_dir ./models/bespoke_punk_sdxl \
  --wandb_api_key 495752e0ee6cde7b8d27088c713f941780d902a1
```

#### **Full Configuration (Recommended)**
```bash
python runpod_training.py \
  --images_dir ./FORTRAINING6/all \
  --captions_dir ./FORTRAINING6/oldtext \
  --output_dir ./models/bespoke_punk_sdxl \
  --base_model stabilityai/stable-diffusion-xl-base-1.0 \
  --resolution 512 \
  --train_batch_size 4 \
  --num_train_epochs 120 \
  --learning_rate 0.00008 \
  --lora_rank 16 \
  --lora_alpha 16 \
  --mixed_precision fp16 \
  --gradient_accumulation_steps 1 \
  --save_steps 500 \
  --validation_steps 100 \
  --wandb_project bespoke-punk-sdxl \
  --wandb_api_key 495752e0ee6cde7b8d27088c713f941780d902a1 \
  --seed 42
```

#### **For Lower VRAM GPUs (RTX 3090, 24GB)**
```bash
python runpod_training.py \
  --images_dir ./FORTRAINING6/all \
  --captions_dir ./FORTRAINING6/oldtext \
  --output_dir ./models/bespoke_punk_sdxl \
  --train_batch_size 1 \
  --gradient_accumulation_steps 4 \
  --mixed_precision fp16 \
  --wandb_api_key 495752e0ee6cde7b8d27088c713f941780d902a1
```

### 6. Monitor Training

#### **W&B Dashboard**
1. Go to [wandb.ai](https://wandb.ai)
2. Navigate to project: `bespoke-punk-sdxl`
3. Watch real-time metrics:
   - Loss curves
   - Learning rate
   - GPU utilization
   - Sample generations (if configured)

#### **In Terminal**
The training script shows live progress:
```
Training: 45%|████████████▌             | 2250/5000 [1:23:45<1:37:30, 2.13s/it, loss=0.0234, lr=6.5e-05]

📊 Step 2250/5000
   Loss: 0.0234
   LR: 6.5e-05
   GPU Memory: 18.4GB
```

#### **Check Logs**
```bash
# View training output
tail -f /workspace/bespokebaby2/training.log

# Check GPU usage
nvidia-smi

# Monitor in real-time
watch -n 1 nvidia-smi
```

### 7. Download Trained Model

#### **Option A: Download via RunPod Interface**
1. Navigate to `/workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model`
2. Right-click → Download
3. Or zip and download:
```bash
cd /workspace/bespokebaby2/models
zip -r bespoke_punk_final.zip bespoke_punk_sdxl/final_model
# Download via RunPod file browser
```

#### **Option B: Upload to Hugging Face**
```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login --token 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

# Upload model
cd /workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model
huggingface-cli upload codelace/bespoke-punk-sdxl . --repo-type model
```

#### **Option C: Use rsync/scp**
```bash
# From your local machine
scp -P <port> -i ~/.ssh/id_ed25519 -r \
  root@<pod-ip>:/workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model \
  ./local_models/
```

## 🎨 Testing the Model

After training, test your model:

```python
from diffusers import StableDiffusionXLPipeline
import torch

# Load base model
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
)

# Load your LoRA
pipe.load_lora_weights("./models/bespoke_punk_sdxl/final_model")
pipe = pipe.to("cuda")

# Generate test image
prompt = "TOK bespoke, 24x24 pixel grid portrait, female, purple background, brown hair, blue eyes, right-facing"

image = pipe(
    prompt,
    num_inference_steps=30,
    guidance_scale=7.5,
    height=512,
    width=512
).images[0]

image.save("test_output.png")
```

Or use the quick test script:
```bash
python test_model.py --model_path ./models/bespoke_punk_sdxl/final_model
```

## 📊 Training Parameters Explained

### Batch Size
- **Larger (4-8)**: Faster training, more stable, needs more VRAM
- **Smaller (1-2)**: Slower, less VRAM, can be less stable
- **Recommendation**: Start with 2-4, adjust based on GPU

### Epochs
- **120 epochs** = ~23,000 steps with 193 images
- More epochs = better learning but risk overfitting
- **Recommendation**: 100-150 epochs

### Learning Rate
- **8e-5** (0.00008): Conservative, stable
- **1e-4** (0.0001): Faster learning, less stable
- **5e-5** (0.00005): Very conservative
- **Recommendation**: 8e-5 for balanced training

### LoRA Rank
- **16**: Good balance of quality and file size
- **32**: Higher quality, larger file
- **8**: Faster, smaller file, lower quality
- **Recommendation**: 16

### Resolution
- **512**: Standard, good quality, fast
- **768**: Higher quality, slower, more VRAM
- **1024**: Best quality, slowest, most VRAM
- **Recommendation**: 512 for pixel art

## 🔧 Troubleshooting

### Out of Memory (OOM)
```bash
# Reduce batch size
--train_batch_size 1

# Enable gradient accumulation
--gradient_accumulation_steps 4

# Lower resolution
--resolution 256
```

### Training Too Slow
```bash
# Increase batch size (if VRAM allows)
--train_batch_size 8

# Use xformers
pip install xformers
# Script auto-detects and uses if available
```

### Model Not Learning
```bash
# Check if images are loading
ls -la FORTRAINING6/all/*.png | wc -l  # Should be 193

# Check captions
head -n 5 FORTRAINING6/oldtext/*.txt

# Increase learning rate
--learning_rate 0.0001

# Increase epochs
--num_train_epochs 150
```

### Connection Lost
```bash
# Use tmux to keep training running
tmux new -s training
python runpod_training.py ...
# Detach: Ctrl+B then D
# Reattach later: tmux attach -t training
```

## 💰 Cost Estimation

Based on RTX 4090 ($0.50/hr):
- **120 epochs**: ~5 hours = **$2.50**
- **150 epochs**: ~6 hours = **$3.00**
- **200 epochs**: ~8 hours = **$4.00**

**Total project cost (with testing)**: ~$5-10

## 📝 Training Checklist

Before starting:
- [ ] RunPod pod created and running
- [ ] Dataset uploaded (193 pairs verified)
- [ ] Dependencies installed
- [ ] W&B API key configured (optional)
- [ ] Training parameters chosen
- [ ] tmux session started (recommended)

During training:
- [ ] Monitor W&B dashboard
- [ ] Check GPU usage (nvidia-smi)
- [ ] Verify loss is decreasing
- [ ] Watch for OOM errors

After training:
- [ ] Download final model
- [ ] Test with sample prompts
- [ ] Upload to Hugging Face (optional)
- [ ] Stop RunPod instance!

## 🎯 Next Steps

After successful training:
1. Test model with various prompts
2. Compare checkpoints (step 500, 1000, 1500, etc.)
3. Upload best checkpoint to Hugging Face
4. Integrate into your application
5. **Don't forget to stop your RunPod instance!**

## 📚 Additional Resources

- [RunPod Documentation](https://docs.runpod.io/)
- [Diffusers Training Guide](https://huggingface.co/docs/diffusers/training/overview)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [SDXL Documentation](https://huggingface.co/docs/diffusers/using-diffusers/sdxl)

---

**Good luck with your training!** 🚀

If you encounter issues, check the logs and adjust parameters accordingly. The training script is designed to be robust and will save checkpoints regularly.
