# 🎯 Replicate Training Settings - Bespoke Punk Pixel Art

## Dataset Overview
- **Total Training Pairs**: 193 (from FORTRAINING6/all + oldtext)
- **Image Format**: 24x24 PNG pixel art portraits
- **Caption Format**: Ultra-detailed coordinate specifications
- **Trigger Word**: TOK (or bespoke)
- **Style**: Symbolic punk style pixel art

## 🔥 Recommended Replicate Training Configuration

### **Option 1: FLUX.1-dev (RECOMMENDED for Latest Quality)**

```bash
replicate training create \
  --destination "your-username/bespoke-punk-flux" \
  --input input_images=@bespoke_punk_training_193.zip \
  --input trigger_word="TOK" \
  --input steps=2000 \
  --input lora_rank=16 \
  --input lora_alpha=16 \
  --input learning_rate=0.0004 \
  --input batch_size=1 \
  --input resolution="512,768,1024" \
  --input optimizer="adamw8bit" \
  --input caption_dropout_rate=0.05 \
  --input cache_latents_to_disk=false \
  --input gradient_checkpointing=false \
  --input wandb_project="bespoke_punk_training" \
  --input wandb_sample_interval=100 \
  --input wandb_save_interval=100
```

### **Option 2: SDXL (Classic Stable Diffusion)**

```bash
replicate training create \
  --destination "your-username/bespoke-punk-sdxl" \
  --input input_images=@bespoke_punk_training_193.zip \
  --input trigger_word="TOK" \
  --input lora_rank=16 \
  --input optimizer="adamw8bit" \
  --input resolution="512" \
  --input train_batch_size=2 \
  --input num_train_epochs=120 \
  --input learning_rate=0.00008 \
  --input lr_scheduler="cosine" \
  --input mixed_precision="fp16" \
  --input validation_epochs=10
```

## 📊 Detailed Parameter Breakdown

### **Core Training Settings**
```yaml
# Training Duration
steps: 2000                      # For FLUX (alternative: num_train_epochs: 120 for SDXL)

# Learning Configuration
learning_rate: 0.0004            # FLUX (0.00008 for SDXL)
lr_scheduler: "cosine"           # Smooth learning rate decay
optimizer: "adamw8bit"           # Memory-efficient optimizer

# Batch Configuration
batch_size: 1                    # Conservative for complex captions
train_batch_size: 2              # For SDXL

# Resolution
resolution: "512,768,1024"       # FLUX multi-resolution
# OR
resolution: "512"                # SDXL single resolution
```

### **LoRA Configuration**
```yaml
lora_rank: 16                    # Complexity of learned features
lora_alpha: 16                   # Scaling factor (typically matches rank)
lora_dropout: 0.1                # Regularization (0.05-0.1)
target_modules:                  # Which model parts to train
  - "to_k"
  - "to_q"
  - "to_v"
  - "to_out.0"
```

### **Advanced Settings**
```yaml
caption_dropout_rate: 0.05       # Helps generalization
cache_latents_to_disk: false     # Memory vs speed tradeoff
gradient_checkpointing: false    # Memory optimization
mixed_precision: "fp16"          # Faster training
validation_epochs: 10            # Test quality every N epochs
```

### **Monitoring (W&B Integration)**
```yaml
wandb_project: "bespoke_punk_training"
wandb_sample_interval: 100       # Generate samples every N steps
wandb_save_interval: 100         # Save checkpoints every N steps
```

## 🎨 Caption Format (Critical for Success!)

Your captions follow this proven format:
```
bespoke, 24x24 pixel grid portrait, symbolic punk style, [background color] solid background, [hair description] starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12), [eye color] iris eyes at (9,12) and (14,12), black nose dot at (11,13), [lip description] spanning x=10-13 y=15-16, [skin tone] with jaw defined at y=19, [collar/accent] at bottom edge y=20-22, right-facing, pure pixel art with no gradients or anti-aliasing, clean color boundaries, all features contained within 22x22 center grid
```

## 📈 Training Timeline Expectations

### **FLUX.1-dev (2000 steps)**
```yaml
Steps 0-500:
  - Basic shape and color learning
  - Background color recognition
  - Rough feature placement

Steps 500-1000:
  - Hair style recognition
  - Accurate eye placement
  - Skin tone learning

Steps 1000-1500:
  - Advanced feature synthesis
  - Precise coordinate accuracy
  - Accessory placement (glasses, hats, etc.)

Steps 1500-2000:
  - Fine-tuning and polish
  - Style consistency
  - Clean pixel boundaries
```

### **Recommended Checkpoints to Save**
- Step 600: Early quality check
- Step 800: Breakthrough point (based on prior experience)
- Step 1200: Advanced features
- Step 1600: Pre-final
- Step 2000: Final model

## 🎯 Test Prompts After Training

### **Basic Test**
```
TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing
```

### **Advanced Coordinate Test**
```
TOK bespoke, 24x24 pixel grid portrait, symbolic punk style, vibrant orange solid background, black hair starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12), brown iris eyes at (9,12) and (14,12), black nose dot at (11,13), pink lips spanning x=10-13 y=15-16, tan skin tone with jaw defined at y=19, blue collar at bottom edge y=20-22, right-facing, pure pixel art with no gradients or anti-aliasing
```

### **Accessory Test**
```
TOK bespoke, 24x24 pixel art, male, glasses spanning x=7-16 y=11-13, black hair, green solid background, right-facing profile
```

## 🔧 Environment Variables Needed

```bash
# Replicate API
REPLICATE_API_TOKEN=r8_bkX5IVUJk9IqmmXZ35XvCjkqsWy1hcM24kTye

# Weights & Biases (Optional - for monitoring)
WANDB_API_KEY=495752e0ee6cde7b8d27088c713f941780d902a1

# Hugging Face (Optional - for model storage)
HUGGINGFACE_TOKEN=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
```

## 📦 Preparing Your Dataset for Upload

Your dataset is already prepared! Just zip the files:

```bash
# Navigate to your repo
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2

# Create training zip with image-caption pairs
zip -r bespoke_punk_training_193.zip FORTRAINING6/all FORTRAINING6/oldtext
```

Or create a proper structure:
```bash
# Create clean training folder
mkdir -p training_package
cp FORTRAINING6/all/*.png training_package/
cp FORTRAINING6/oldtext/*.txt training_package/
cd training_package
zip -r ../bespoke_punk_training_193.zip *
```

## 🚀 Quick Start Command

```bash
# Set your API key
export REPLICATE_API_TOKEN=r8_bkX5IVUJk9IqmmXZ35XvCjkqsWy1hcM24kTye

# Create training (FLUX recommended)
replicate training create \
  --destination "codelace/bespoke-punk-v2" \
  --input input_images=@bespoke_punk_training_193.zip \
  --input trigger_word="TOK" \
  --input steps=2000 \
  --input lora_rank=16 \
  --input learning_rate=0.0004 \
  --input batch_size=1 \
  --input resolution="512,768,1024" \
  --input optimizer="adamw8bit" \
  --input caption_dropout_rate=0.05
```

## 📊 Success Criteria

### **Quality Benchmarks**
- ✅ Accurate 24x24 pixel art generation
- ✅ Proper coordinate-based prompt following
- ✅ Clean color boundaries (no anti-aliasing)
- ✅ Exact eye placement at (8,12) and (13,12)
- ✅ Consistent right-facing profile orientation
- ✅ Proper hair, skin tone, and accessory rendering

### **Feature Recognition Targets**
- Hair colors and styles: >90% accuracy
- Eye colors: >90% accuracy
- Background colors: Exact hex matching
- Accessories (glasses, hats, etc.): >85% accuracy
- Skin tones: >90% accuracy

## 🎓 Tips Based on Previous Training Experience

1. **Caption Quality is King**: Your ultra-detailed coordinate captions are the secret sauce
2. **Start Conservative**: Use batch_size=1 initially, increase if training is stable
3. **Monitor Early**: Check samples at step 600 to verify it's learning correctly
4. **Save Checkpoints**: The best model might not be the final one (often around step 800-1200)
5. **Test Thoroughly**: Use various prompts to test different features
6. **Pixel Art Matters**: Ensure inference uses nearest-neighbor resampling, not bilinear

## 📁 Alternative: Using Hugging Face AutoTrain

If Replicate gives issues, you can also use Hugging Face:

```bash
huggingface-cli login --token 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

autotrain dreambooth \
  --model stabilityai/stable-diffusion-xl-base-1.0 \
  --output ./bespoke-punk-model \
  --data-path ./training_package \
  --prompt "TOK bespoke punk" \
  --resolution 512 \
  --num-steps 2000 \
  --batch-size 1 \
  --lr 0.0004 \
  --lora-rank 16
```

---

**Generated**: 2025-11-06
**Dataset**: FORTRAINING6 - 193 matched pairs
**Ready for**: Immediate Replicate deployment
**Based on**: Proven training configurations from bespokebaby repo
