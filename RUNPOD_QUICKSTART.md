# ⚡ RunPod Quick Start - 5 Minute Setup

The fastest way to start training your Bespoke Punk model on RunPod.

## 🚀 One-Command Setup

Once you're connected to your RunPod instance:

```bash
# Clone repo, install dependencies, and start training
git clone https://github.com/bespokepunk/bespokebaby2.git && \
cd bespokebaby2 && \
pip install -r requirements_runpod.txt && \
bash start_training.sh
```

That's it! Training will start automatically with optimal settings.

## 📊 What Happens Next

1. **Setup** (2-3 minutes): Downloads base SDXL model and dependencies
2. **Training** (4-6 hours): Trains on your 193 pixel art images
3. **Checkpoints**: Saves every 500 steps to `./models/bespoke_punk_sdxl/`
4. **Completion**: Final model saved to `./models/bespoke_punk_sdxl/final_model/`

## 🎮 Recommended RunPod GPU

| GPU | Cost/hr | Training Time | Sweet Spot |
|-----|---------|---------------|------------|
| RTX 4090 | $0.50 | 4-6 hours | ⭐ BEST |
| A40 | $0.60 | 3-4 hours | ⭐⭐ FASTEST |
| RTX 3090 | $0.35 | 6-8 hours | 💰 CHEAPEST |

**Total cost**: $2-4 for full training

## 📈 Monitor Training

### W&B Dashboard (Recommended)
Go to: https://wandb.ai/your-username/bespoke-punk-sdxl

You'll see:
- Real-time loss curves
- Learning rate schedule
- GPU utilization
- Training progress

### Terminal Output
```
Training: 45%|████████▌      | 2250/5000 [1:23<1:37, 2.1s/it, loss=0.023, lr=6.5e-05]

📊 Step 2250/5000
   Loss: 0.0234
   LR: 6.5e-05
   GPU Memory: 18.4GB
```

### Check GPU
```bash
nvidia-smi  # One-time check
watch -n 1 nvidia-smi  # Live monitoring
```

## 🧪 Test Your Model

After training completes:

```bash
python test_model.py
```

This generates 5 test images in `./test_outputs/` to verify quality.

## 💾 Download Your Model

### Option 1: Direct Download (Easiest)
1. In RunPod interface, navigate to: `/workspace/bespokebaby2/models/bespoke_punk_sdxl/final_model`
2. Right-click folder → Download

### Option 2: Upload to Hugging Face
```bash
pip install huggingface_hub
huggingface-cli login --token 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
huggingface-cli upload codelace/bespoke-punk-sdxl ./models/bespoke_punk_sdxl/final_model
```

### Option 3: Zip and Download
```bash
cd models
zip -r bespoke_punk_final.zip bespoke_punk_sdxl/final_model
# Download via RunPod file browser
```

## 🎨 Using Your Model

```python
from diffusers import StableDiffusionXLPipeline
import torch

# Load base + your LoRA
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
).to("cuda")

pipe.load_lora_weights("./models/bespoke_punk_sdxl/final_model")

# Generate
image = pipe(
    "TOK bespoke, 24x24 pixel art, female, purple background, brown hair, blue eyes",
    num_inference_steps=30,
    guidance_scale=7.5
).images[0]

image.save("output.png")
```

## ⚙️ Advanced: Custom Settings

Edit `training_config.yaml` or use command-line arguments:

```bash
python runpod_training.py \
  --train_batch_size 8 \
  --num_train_epochs 150 \
  --learning_rate 0.0001 \
  --lora_rank 32
```

See `RUNPOD_SETUP_INSTRUCTIONS.md` for all options.

## 🔧 Troubleshooting

### Out of Memory
```bash
# Use smaller batch size
python runpod_training.py --train_batch_size 1 --gradient_accumulation_steps 4
```

### Training Not Starting
```bash
# Check dataset
ls -la FORTRAINING6/all/*.png | wc -l  # Should be 193
ls -la FORTRAINING6/oldtext/*.txt | wc -l  # Should be 193

# Verify dependencies
pip install -r requirements_runpod.txt
```

### Connection Lost
```bash
# Use tmux to persist training
tmux new -s training
bash start_training.sh
# Detach: Ctrl+B then D
# Reattach: tmux attach -t training
```

## ✅ Quick Checklist

Before starting:
- [ ] RunPod instance running (RTX 4090 or better)
- [ ] Connected to pod terminal
- [ ] Sufficient credits (~$5 recommended)

During training:
- [ ] W&B dashboard open
- [ ] tmux session active (optional but recommended)
- [ ] GPU utilization >90%

After training:
- [ ] Test images generated and look good
- [ ] Model downloaded/backed up
- [ ] **RunPod instance STOPPED** ⚠️

## 💰 Don't Forget!

**STOP YOUR RUNPOD INSTANCE WHEN DONE!**

In RunPod dashboard: Click "Stop" button on your pod.

---

**Ready to train? Run the one-command setup above!** 🚀
