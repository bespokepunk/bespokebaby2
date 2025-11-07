# 🚀 Complete Replicate Training Guide

Step-by-step guide to train your Bespoke Punk model on Replicate with FLUX.1-dev.

## ⚡ Quick Start (Recommended)

```bash
# 1. Install Replicate CLI
pip install replicate

# 2. Run the training script
bash start_replicate_training.sh
```

That's it! The script handles everything automatically.

## 📋 Manual Setup (Alternative)

If you prefer manual control:

### 1. Prepare Dataset

```bash
# Create training zip
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2
zip -r bespoke_punk_193.zip FORTRAINING6/all/*.png FORTRAINING6/oldtext/*.txt
```

### 2. Set API Token

```bash
export REPLICATE_API_TOKEN=r8_bkX5IVUJk9IqmmXZ35XvCjkqsWy1hcM24kTye
```

### 3. Start Training

```bash
replicate training create \
  ostris/flux-dev-lora-trainer:4ffd32160efd92e956d39c5338a9b8fbafca58e03f791f6d8011f3e20e8ea6fa \
  --destination "codelace/bespoke-punk-flux-v2" \
  --input input_images=@bespoke_punk_193.zip \
  --input trigger_word="TOK" \
  --input steps=2000 \
  --input lora_rank=16 \
  --input learning_rate=0.0004 \
  --input batch_size=1 \
  --input resolution="512,768,1024" \
  --input caption_dropout_rate=0.05 \
  --input optimizer="adamw8bit" \
  --input cache_latents_to_disk=false \
  --input gradient_checkpointing=false \
  --input hf_repo_id="codelace/bespoke-punk-flux-v2" \
  --input hf_token="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" \
  --input wandb_project="bespoke-punk-flux-training" \
  --input wandb_api_key="495752e0ee6cde7b8d27088c713f941780d902a1" \
  --input wandb_sample_interval=100 \
  --input wandb_save_interval=100 \
  --input wandb_sample_prompts="$(cat wandb_sample_prompts.txt | tr '\n' '\n')"
```

## 🎯 Configuration Breakdown

### Core Settings (Required)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `trigger_word` | `"TOK"` | Word to trigger your LoRA in prompts |
| `steps` | `2000` | Training steps (500-4000) |
| `lora_rank` | `16` | LoRA complexity (8-32) |
| `learning_rate` | `0.0004` | How fast model learns |
| `resolution` | `"512,768,1024"` | Multi-resolution training |

### Advanced Settings (Optional)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `batch_size` | `1` | Images per training step |
| `caption_dropout_rate` | `0.05` | Ignore caption 5% of time |
| `optimizer` | `"adamw8bit"` | Optimizer algorithm |
| `cache_latents_to_disk` | `false` | Cache to disk (for many images) |
| `gradient_checkpointing` | `false` | Save memory (slower) |
| `layers_to_optimize_regex` | `""` | Target specific layers |

### Hugging Face Upload (Optional)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `hf_repo_id` | `"codelace/bespoke-punk-flux-v2"` | Where to upload LoRA |
| `hf_token` | `"hf_..."` | Your HF token |

### W&B Monitoring (Highly Recommended)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `wandb_api_key` | `"495752..."` | Your W&B API key |
| `wandb_project` | `"bespoke-punk-flux-training"` | Project name |
| `wandb_run` | `"flux-bespoke-punk-2000steps"` | Run name (optional) |
| `wandb_sample_interval` | `100` | Generate samples every N steps |
| `wandb_save_interval` | `100` | Save checkpoints every N steps |
| `wandb_sample_prompts` | See below | Test prompts for visualization |

## 📊 W&B Sample Prompts

These prompts will be used to generate sample images during training:

```
TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing
TOK bespoke punk, 24x24 pixel art, male, orange solid background, black hair, brown eyes, tan skin, right-facing
TOK bespoke, 24x24 pixel grid, female, pink background, blonde hair, green eyes, light skin, right-facing
TOK bespoke punk style, 24x24 pixel art portrait, male, teal background, red hair, blue eyes with glasses, light skin, right-facing
TOK bespoke, 24x24 pixel grid portrait, female, yellow background, black hair, hazel eyes, tan skin, right-facing
TOK bespoke punk, 24x24 pixel art, male, deep blue background, silver hair, brown eyes, light skin, right-facing
TOK bespoke, 24x24 pixel grid, female, green background, purple hair, blue eyes, light skin, right-facing
TOK bespoke punk style, 24x24 pixel art, male, red background, black hair with cap, brown eyes, medium skin, right-facing
```

These cover:
- ✅ Different genders
- ✅ Various hair colors
- ✅ Different eye colors
- ✅ Multiple backgrounds
- ✅ Different accessories

## 💰 Cost & Time Estimates

| Configuration | Steps | Time | Cost |
|---------------|-------|------|------|
| **Quick Test** | 500 | 20-30 min | ~$1-2 |
| **Standard** ⭐ | 2000 | 50-70 min | ~$3-5 |
| **High Quality** | 3000 | 80-120 min | ~$6-8 |
| **Maximum** | 4000 | 120-150 min | ~$8-12 |

**Recommended**: Start with 2000 steps for best balance.

## 📈 Monitoring Training

### Replicate Dashboard
1. Go to https://replicate.com/codelace
2. Navigate to your model
3. Click on "Trainings" tab
4. Watch real-time progress

### W&B Dashboard (Recommended)
1. Go to https://wandb.ai
2. Navigate to project: `bespoke-punk-flux-training`
3. View:
   - Loss curves
   - Sample images generated every 100 steps
   - Learning rate schedule
   - Training metrics

### Email Notifications
Replicate sends emails when:
- Training starts
- Training completes
- Training fails

## 🎨 Using Your Trained Model

### Via Replicate Web UI
1. Go to https://replicate.com/codelace/bespoke-punk-flux-v2
2. Enter prompt: `TOK bespoke, 24x24 pixel art, female, purple background, brown hair`
3. Click "Run"

### Via Replicate API

```python
import replicate

output = replicate.run(
    "codelace/bespoke-punk-flux-v2:latest",
    input={
        "prompt": "TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing",
        "num_inference_steps": 28,
        "guidance_scale": 3.5
    }
)

print(output)
```

### Download LoRA from Hugging Face

If you enabled HF upload:

```bash
# Download the LoRA weights
wget https://huggingface.co/codelace/bespoke-punk-flux-v2/resolve/main/lora.safetensors

# Use with ComfyUI or any FLUX interface
```

## 📊 Training Settings Explained

### Steps (500-4000)
- **500**: Quick test, basic features
- **1000**: Good baseline
- **2000**: ⭐ Recommended - Best quality/cost ratio
- **3000**: High quality, diminishing returns
- **4000**: Maximum, rarely needed

### LoRA Rank (1-128)
- **8**: Fast, small file, lower quality
- **16**: ⭐ Recommended - Good balance
- **32**: Higher quality, 2x training time
- **64+**: Advanced users, long training

### Learning Rate (0.0001-0.001)
- **0.0004**: ⭐ Default - Works for most cases
- **0.0003**: More conservative, slower learning
- **0.0005**: Faster learning, less stable
- Don't change unless you know what you're doing!

### Caption Dropout (0-1)
- **0.0**: Always use captions
- **0.05**: ⭐ Default - 5% dropout
- **0.1-0.2**: For style training
- **0.5+**: Rarely useful

### Resolution
- **"512"**: Single resolution, faster
- **"512,768"**: Two resolutions
- **"512,768,1024"**: ⭐ Multi-res, best flexibility

## 🔧 Troubleshooting

### Training Fails Immediately
- Check API token is correct
- Verify dataset zip is under 500MB
- Ensure images are PNG format

### Training Starts But Fails
- Check W&B logs for errors
- Reduce batch_size to 1
- Enable gradient_checkpointing

### Poor Quality Results
- Increase steps (try 3000)
- Check caption quality
- Lower caption_dropout_rate to 0.02
- Try different checkpoint (not just final)

### OOM Errors
- Enable cache_latents_to_disk
- Enable gradient_checkpointing
- Reduce resolution to "512"

## ✅ Pre-Flight Checklist

Before starting:
- [ ] Replicate API token set
- [ ] Dataset zip created (bespoke_punk_193.zip)
- [ ] W&B account ready (optional but recommended)
- [ ] Hugging Face token ready (optional)
- [ ] Sufficient credits (~$5 recommended)

During training:
- [ ] W&B dashboard open for monitoring
- [ ] Email notifications enabled
- [ ] Sample images look good at step 500

After training:
- [ ] Test with various prompts
- [ ] Compare different checkpoints
- [ ] Download best checkpoint
- [ ] Upload to HF (if not auto-uploaded)

## 🎓 Pro Tips

1. **Start with 2000 steps** - Best quality/cost ratio
2. **Always use W&B** - Essential for monitoring
3. **Check step 500** - Verify it's learning correctly
4. **Save checkpoints** - Best model might not be final
5. **Test prompts early** - Use same style as training captions
6. **Multi-resolution** - Use "512,768,1024" for flexibility
7. **Caption quality** - Your detailed captions are the secret sauce
8. **Compare checkpoints** - Test step 800, 1200, 1600, 2000

## 📚 Additional Resources

- [Replicate Documentation](https://replicate.com/docs)
- [FLUX.1 Model Card](https://huggingface.co/black-forest-labs/FLUX.1-dev)
- [LoRA Training Guide](https://replicate.com/blog/lora-training)
- [W&B Documentation](https://docs.wandb.ai/)

---

**Ready to train?** Run `bash start_replicate_training.sh` and you're good to go! 🚀
