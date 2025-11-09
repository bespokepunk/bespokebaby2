# RunPod Deployment Guide - Bespoke Punks Training

Train your Bespoke Punks LoRA **20× faster** on A100 GPU for ~$0.70-1.00 total cost.

**Why RunPod?** Mac training takes 3.5 hours. A100 training takes 10-15 minutes.

## Step 1: Create RunPod Account

1. Go to https://runpod.io
2. Sign up / Log in
3. Add $10 credit (you'll only use $1-2)

## Step 2: Deploy Pod

1. Click "Deploy" → "Pods"
2. Choose GPU:
   - **A100** ($1.39/hr) ← FASTEST (10-15 min training)
   - RTX A6000 ($0.79/hr) - Fast (20-25 min training)
   - RTX 4090 ($0.44/hr) - Good (25-30 min training)
3. Select Template: **RunPod Pytorch**
4. Set Pod Configuration:
   - Container Disk: 50GB
   - Volume: 20GB
5. Click "Deploy On-Demand"

## Step 3: Upload Training Data

Once pod starts, click "Connect" → "Start Jupyter Lab"

In Jupyter terminal, run:

```bash
# Install Kohya
cd /workspace
git clone https://github.com/kohya-ss/sd-scripts.git
cd sd-scripts
pip install -r requirements.txt
pip install --upgrade diffusers accelerate transformers safetensors
```

Then upload your training data:

```bash
# Create training directory
mkdir -p /workspace/training_data/10_bespokepunks

# Upload the zip file (use Jupyter file upload)
# Then extract:
cd /workspace
unzip bespoke_punks_training_512.zip -d training_data/10_bespokepunks/
```

## Step 4: Run Training

Copy this EXACT command into the terminal:

```bash
cd /workspace/sd-scripts

python train_network.py \
  --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
  --train_data_dir="/workspace/training_data" \
  --resolution="512,512" \
  --output_dir="/workspace/output" \
  --output_name="bespoke_punks_sd15_512" \
  --save_model_as=safetensors \
  --prior_loss_weight=1.0 \
  --max_train_epochs=3 \
  --learning_rate=0.0001 \
  --unet_lr=0.0001 \
  --text_encoder_lr=0.00005 \
  --lr_scheduler="cosine_with_restarts" \
  --lr_scheduler_num_cycles=3 \
  --network_module=networks.lora \
  --network_dim=32 \
  --network_alpha=16 \
  --save_every_n_epochs=1 \
  --mixed_precision="fp16" \
  --save_precision="fp16" \
  --cache_latents \
  --optimizer_type="AdamW8bit" \
  --max_data_loader_n_workers=4 \
  --caption_extension=".txt" \
  --clip_skip=1 \
  --noise_offset=0.1 \
  --min_snr_gamma=5 \
  --gradient_checkpointing \
  --xformers \
  --sample_every_n_epochs=1 \
  --sample_sampler="euler_a" \
  --sample_prompts="pixel art, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin, sharp pixel edges" \
  --sample_prompts="pixel art, portrait of bespoke punk, checkered pattern background, brown hair, brown eyes, tan skin, sharp pixel edges"
```

**IMPORTANT: Sample Images Will Be Generated Automatically!**
- After EACH epoch completes, training will auto-generate 2 sample images
- Find them in `/workspace/output/sample-000001-000000.png` etc.
- You can view them in Jupyter file browser while training is still running
- These let you monitor quality and decide when to stop if needed

## Expected Timeline:

**With A100 (FASTEST - RECOMMENDED):**
- **Setup**: 5-10 minutes
- **Training**: 10-15 minutes (3 epochs with sample images)
- **Download results**: 2-5 minutes
- **Total**: ~20-30 minutes, ~$0.70-1.00 cost

**With RTX 4090 (Budget option):**
- **Setup**: 5-10 minutes
- **Training**: 25-30 minutes
- **Download results**: 2-5 minutes
- **Total**: ~35-45 minutes, ~$0.30-0.50 cost

## Step 5: Download Results

After training completes:

```bash
# Check outputs
ls -lh /workspace/output/

# Zip for download
cd /workspace
zip -r bespoke_punks_results.zip output/
```

Download via Jupyter file browser:
- Checkpoints: `bespoke_punks_sd15_512-000001.safetensors` (Epoch 1)
- Checkpoints: `bespoke_punks_sd15_512-000002.safetensors` (Epoch 2)
- Checkpoints: `bespoke_punks_sd15_512-000003.safetensors` (Epoch 3)
- Sample images: `sample-*.png`

## Step 6: Stop Pod

**IMPORTANT**: Stop the pod immediately after downloading to avoid charges!

1. Go to RunPod dashboard
2. Click "Stop" on your pod
3. Verify it shows "Stopped"

## Cost Breakdown:

**A100 (FASTEST - RECOMMENDED):**
- Training: $1.39/hr × 0.25-0.33hr = **$0.35-0.46**
- Setup buffer: +$0.25-0.35
- **Total: ~$0.70-1.00**
- **Speed: 20× faster than Mac**

**RTX 4090 (Budget option):**
- Training: $0.44/hr × 0.42-0.5hr = **$0.18-0.22**
- Setup buffer: +$0.25
- **Total: ~$0.50-0.70**
- **Speed: 10× faster than Mac**

vs. Mac training: 3.5 hours locally (free but slow + ties up computer)
