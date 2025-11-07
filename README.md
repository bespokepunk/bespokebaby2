# Bespoke Baby 2 - Pixel Art Training

Complete training setup for Bespoke Punk 24x24 pixel art portraits using SDXL and FLUX models.

## 📦 What's Included

- **193 Training Pairs**: High-quality 24x24 pixel art portraits with detailed captions
- **RunPod Training**: Ready-to-use SDXL training for GPU cloud
- **Replicate Training**: Configuration for FLUX.1-dev training
- **Complete Documentation**: Step-by-step guides and configs

## 🚀 Quick Start

### Option 1: RunPod (SDXL - Recommended for Full Control)

```bash
# On RunPod instance
git clone https://github.com/bespokepunk/bespokebaby2.git
cd bespokebaby2
pip install -r requirements_runpod.txt
bash start_training.sh
```

**See**: [RUNPOD_QUICKSTART.md](RUNPOD_QUICKSTART.md) for 5-minute setup

### Option 2: Replicate (FLUX.1-dev - Easiest)

```bash
# Prepare dataset
cd bespokebaby2
zip -r bespoke_punk_193.zip FORTRAINING6/all FORTRAINING6/oldtext

# Upload and train
replicate training create \
  --destination "your-username/bespoke-punk" \
  --input input_images=@bespoke_punk_193.zip \
  --input trigger_word="TOK" \
  --input steps=2000 \
  --input lora_rank=16 \
  --input learning_rate=0.0004
```

**See**: [REPLICATE_TRAINING_SETTINGS.md](REPLICATE_TRAINING_SETTINGS.md) for complete settings

## 📁 Repository Structure

```
bespokebaby2/
├── FORTRAINING6/
│   ├── all/              # 193 PNG training images (24x24 pixel art)
│   └── oldtext/          # 193 matching caption files
│
├── Context 1106/         # Project context and documentation
│   └── Context.rtf       # Workflow and credentials
│
├── runpod_training.py    # Main SDXL training script
├── start_training.sh     # One-command training start
├── test_model.py         # Test your trained model
├── requirements_runpod.txt  # Python dependencies
│
├── training_config.yaml  # Customizable training settings
├── RUNPOD_QUICKSTART.md  # 5-minute setup guide
├── RUNPOD_SETUP_INSTRUCTIONS.md  # Detailed RunPod guide
└── REPLICATE_TRAINING_SETTINGS.md  # Replicate configuration
```

## 🎨 Dataset Details

- **Total Pairs**: 193 matched image-caption pairs
- **Image Format**: 24x24 PNG pixel art
- **Style**: Bespoke punk symbolic pixel art
- **Captions**: Ultra-detailed with coordinate specifications

Example caption:
```
bespoke, 24x24 pixel grid portrait, symbolic punk style, purple solid background,
brown hair starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12),
blue iris eyes at (9,12) and (14,12), black nose dot at (11,13), pink lips spanning
x=10-13 y=15-16, light skin tone with jaw defined at y=19, right-facing, pure pixel art
with no gradients or anti-aliasing, clean color boundaries
```

## 🎯 Training Options Comparison

| Platform | Model | Time | Cost | Difficulty | Control |
|----------|-------|------|------|------------|---------|
| **RunPod** | SDXL | 4-6h | $2-4 | Medium | Full |
| **Replicate** | FLUX.1 | 3-5h | $5-8 | Easy | Limited |
| **Hugging Face** | SDXL | 4-6h | Free* | Hard | Full |

*Hugging Face Spaces: Free but slow, or pay for GPU

**Recommendation**:
- **Beginners**: Use Replicate (easiest, great results)
- **Advanced**: Use RunPod (full control, cheaper)

## 📊 Expected Results

After training, your model will generate:
- ✅ Authentic 24x24 pixel art portraits
- ✅ Accurate coordinate-based features
- ✅ Clean color boundaries (no anti-aliasing)
- ✅ Consistent bespoke punk style
- ✅ Right-facing profile orientation
- ✅ Proper rendering of hair, eyes, skin tones, accessories

## 🧪 Testing Your Model

```bash
# Generate test images
python test_model.py --model_path ./models/bespoke_punk_sdxl/final_model

# Test with custom prompt
python -c "
from diffusers import StableDiffusionXLPipeline
import torch

pipe = StableDiffusionXLPipeline.from_pretrained(
    'stabilityai/stable-diffusion-xl-base-1.0',
    torch_dtype=torch.float16
).to('cuda')

pipe.load_lora_weights('./models/bespoke_punk_sdxl/final_model')

image = pipe(
    'TOK bespoke, 24x24 pixel art, female, purple background, brown hair, blue eyes',
    num_inference_steps=30
).images[0]

image.save('test.png')
"
```

## 📚 Documentation

- [RUNPOD_QUICKSTART.md](RUNPOD_QUICKSTART.md) - Get started in 5 minutes
- [RUNPOD_SETUP_INSTRUCTIONS.md](RUNPOD_SETUP_INSTRUCTIONS.md) - Complete RunPod guide
- [REPLICATE_TRAINING_SETTINGS.md](REPLICATE_TRAINING_SETTINGS.md) - Replicate configuration
- [Context 1106/Context.rtf](Context%201106/Context.rtf) - Project workflow and API keys

## 🔑 API Keys & Credentials

Stored in `Context 1106/Context.rtf`:
- Replicate API: `r8_bkX5IVUJk9IqmmXZ35XvCjkqsWy1hcM24kTye`
- W&B API: `495752e0ee6cde7b8d27088c713f941780d902a1`
- Hugging Face: `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`

## 🛠️ Requirements

### RunPod Training
- GPU: RTX 3090 or better (24GB+ VRAM recommended)
- Disk: 50GB minimum
- Python: 3.10+
- CUDA: 11.8+

### Replicate Training
- Just a Replicate account and API key
- No local GPU needed

## 🎓 Training Tips

1. **Start with default settings** - They're optimized for this dataset
2. **Monitor W&B** - Watch for loss curves and sample images
3. **Save checkpoints** - Best model might not be the final one
4. **Test early** - Generate samples at step 500 to verify learning
5. **Batch size** - Adjust based on GPU (1-8)
6. **Epochs** - 100-150 is usually optimal for this dataset

## 🔧 Troubleshooting

### Common Issues

**Out of Memory**
```bash
python runpod_training.py --train_batch_size 1 --gradient_accumulation_steps 4
```

**Model Not Learning**
- Check dataset: `ls FORTRAINING6/all/*.png | wc -l` (should be 193)
- Increase epochs: `--num_train_epochs 150`
- Adjust learning rate: `--learning_rate 0.0001`

**Slow Training**
- Increase batch size (if VRAM allows)
- Use better GPU (RTX 4090, A100)
- Enable xformers: `pip install xformers`

## 📈 Training Timeline

**120 epochs on RTX 4090**:
- Steps: ~23,000
- Time: ~5 hours
- Cost: ~$2.50
- Checkpoints: Every 500 steps

**Progress markers**:
- Step 500: Basic shapes learned
- Step 1000: Features recognizable
- Step 1500: High quality emerging
- Step 2000+: Fine-tuning

## 🎯 Next Steps

After training:
1. ✅ Test with `test_model.py`
2. ✅ Compare checkpoints
3. ✅ Upload to Hugging Face
4. ✅ Integrate into your application
5. ⚠️ **STOP your RunPod instance!**

## 🤝 Contributing

This is a training repository. To improve:
- Add more training images to FORTRAINING6/
- Enhance caption quality
- Optimize training parameters
- Share results and findings

## 📄 License

Training data and scripts for personal/commercial use.

## 🙏 Acknowledgments

- Based on Stable Diffusion XL and FLUX.1-dev
- Training methodology from bespokebaby repo
- RunPod for GPU infrastructure
- Replicate for easy training

---

**Ready to train?** Start with [RUNPOD_QUICKSTART.md](RUNPOD_QUICKSTART.md) or [REPLICATE_TRAINING_SETTINGS.md](REPLICATE_TRAINING_SETTINGS.md)!
