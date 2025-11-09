# 🛠️ Kohya_ss Setup Guide - For True 24x24 Native Training

## What is Kohya?

**Kohya_ss** is the industry-standard tool for local LoRA training with complete control over:
- ✅ Any resolution (including 24x24!)
- ✅ Any base model
- ✅ All training parameters
- ✅ No platform limitations

**Use when**: CivitAI can't do what you need (like 24x24 native training)

---

## Installation Options

### Option 1: Local (Your Mac) - FREE but needs good GPU

**Requirements**:
- Mac with M1/M2/M3 chip (you have this!)
- 16GB+ RAM recommended
- 50GB free disk space

**Pros**:
- ✅ Completely free
- ✅ Full control
- ✅ Privacy (data stays local)

**Cons**:
- ❌ Slower than cloud GPUs
- ❌ More setup required

### Option 2: Google Colab - ~$10/month

**Requirements**:
- Google account
- Colab Pro subscription ($9.99/month)

**Pros**:
- ✅ Faster GPU (T4 or better)
- ✅ Less setup
- ✅ No local disk space needed

**Cons**:
- ❌ Costs $10/month
- ❌ Session time limits (12 hours)

### Option 3: RunPod - ~$0.50-1.00/hour

**Requirements**:
- RunPod account
- Pay per hour

**Pros**:
- ✅ Powerful GPUs (A100, etc.)
- ✅ Pay only when training
- ✅ Very fast

**Cons**:
- ❌ Most complex setup
- ❌ Costs per hour

---

## Recommended: Start with Local (Free)

Let's set up Kohya locally on your Mac first. If it's too slow, we can move to Colab.

---

## Installation Steps (Mac)

### Step 1: Install Prerequisites

Open Terminal and run:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10
brew install python@3.10

# Install Git
brew install git

# Verify installations
python3.10 --version
git --version
```

### Step 2: Clone Kohya Repository

```bash
# Navigate to your projects folder
cd ~/Documents/GitHub

# Clone Kohya_ss
git clone https://github.com/bmaltais/kohya_ss.git
cd kohya_ss

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (Mac M1/M2/M3)
pip install torch torchvision torchaudio
pip install -r requirements.txt
```

### Step 3: Install Additional Mac Dependencies

```bash
# Install MPS (Metal Performance Shaders) support
pip install --upgrade pip
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu

# Install Kohya scripts
pip install -U -r requirements.txt
```

### Step 4: Download Base Model

```bash
# Create models directory
mkdir -p models

# Download SDXL base (or SD 1.5, or any model)
# You can download from HuggingFace or use existing models

# Example: Use a model you already have
# Copy it to: ~/Documents/GitHub/kohya_ss/models/
```

---

## Training Configuration for Bespoke Punks

### Create Config File: `bespoke_punks_24x24.toml`

```toml
[general]
# Bespoke Punks 24x24 Native Training
pretrained_model_name_or_path = "models/sdxl-base-1.0"  # Or your chosen base model
output_dir = "output/bespoke_punks_24x24"
output_name = "bespoke_punks_v3_kohya"
save_model_as = "safetensors"

[dataset]
# Your training data
train_data_dir = "/Users/ilyssaevans/Documents/GitHub/bespokebaby2/FORTRAINING6/bespokepunks"
resolution = "24,24"  # CRITICAL: Native 24x24!
batch_size = 4
num_epochs = 3

[network]
# LoRA settings
network_module = "networks.lora"
network_dim = 32  # LoRA rank
network_alpha = 16
network_train_unet_only = false

[training]
# Training parameters
learning_rate = 0.0001
unet_lr = 0.0001
text_encoder_lr = 0.00005
lr_scheduler = "cosine_with_restarts"
lr_scheduler_num_cycles = 3

optimizer_type = "AdamW8bit"
max_train_steps = 153  # Will be calculated based on epochs

# Important flags for pixel art
mixed_precision = "fp16"
gradient_checkpointing = true
cache_latents = true

# NO augmentation!
flip_aug = false
color_aug = false
random_crop = false

# Bucketing - DISABLE for strict 24x24
enable_bucket = false
bucket_no_upscale = true
bucket_reso_steps = 1

[saving]
# Save every epoch
save_every_n_epochs = 1
save_precision = "fp16"

[logging]
logging_dir = "logs"
log_with = "tensorboard"

[sample]
# Generate samples during training
sample_every_n_epochs = 1
sample_prompts = [
    "pixel art, 24x24, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin, sharp pixel edges",
    "pixel art, 24x24, portrait of bespoke punk, checkered pattern background, brown hair, brown eyes, tan skin, sharp pixel edges"
]
```

---

## Running Training

### Option A: Using GUI (Easiest)

```bash
# Activate environment
cd ~/Documents/GitHub/kohya_ss
source venv/bin/activate

# Launch GUI
python kohya_gui.py
```

Then:
1. Open browser to `http://localhost:7860`
2. Load `bespoke_punks_24x24.toml` config
3. Click "Start Training"

### Option B: Using Command Line

```bash
# Activate environment
cd ~/Documents/GitHub/kohya_ss
source venv/bin/activate

# Run training
accelerate launch --num_cpu_threads_per_process=8 train_network.py \
  --config_file=bespoke_punks_24x24.toml
```

---

## Expected Performance (Mac)

**M1/M2/M3 Mac**:
- Speed: ~2-5 minutes per epoch (slower than cloud GPUs)
- Total time: ~15-30 minutes for 3 epochs
- Memory: 8-12GB during training

**If too slow**: Switch to Google Colab (instructions below)

---

## Google Colab Setup (Alternative)

### Step 1: Open Colab Notebook

Search for "Kohya Colab" on GitHub or use this template:
https://colab.research.google.com/

### Step 2: Install Kohya in Colab

```python
# Cell 1: Install
!git clone https://github.com/bmaltais/kohya_ss.git
%cd kohya_ss
!pip install -r requirements.txt
!pip install -U -r requirements.txt
```

### Step 3: Upload Training Data

```python
# Cell 2: Upload data
from google.colab import files
uploaded = files.upload()

# Or mount Google Drive
from google.colab import drive
drive.mount('/content/drive')
```

### Step 4: Run Training

```python
# Cell 3: Train
!accelerate launch train_network.py \
  --config_file=bespoke_punks_24x24.toml
```

**Cost**: $9.99/month for Colab Pro (includes GPU)

---

## Troubleshooting

### Mac: "MPS not available"
```bash
# Install latest PyTorch with MPS support
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Out of Memory
- Reduce batch_size to 2 or 1
- Enable `gradient_checkpointing`
- Reduce `network_dim` to 16

### Training too slow
- Switch to Google Colab
- Or use RunPod with A100 GPU

---

## Output Files

After training completes, you'll have:

```
output/bespoke_punks_24x24/
  ├── bespoke_punks_v3_kohya-000001.safetensors  (Epoch 1)
  ├── bespoke_punks_v3_kohya-000002.safetensors  (Epoch 2)
  ├── bespoke_punks_v3_kohya-000003.safetensors  (Epoch 3)
  └── samples/  (Generated test images)
```

---

## Testing Results

Use the same testing script, just point to Kohya output:

```bash
python3 test_v3_epoch1.py
# Edit LORA_PATH to point to Kohya output
```

---

## When to Use Kohya vs CivitAI

**Use CivitAI when**:
- ✅ Standard resolutions (512, 1024)
- ✅ Want fast/easy setup
- ✅ Don't mind platform limits

**Use Kohya when**:
- ✅ Need 24x24 native training
- ✅ Want complete control
- ✅ CivitAI base models don't work
- ✅ Need custom configurations

---

## Cost Comparison

| Platform | Setup Time | Training Time | Cost | Control |
|----------|------------|---------------|------|---------|
| **CivitAI** | 5 min | 30-60 min | $2-6 | Limited |
| **Kohya Local** | 1 hour | 15-30 min | FREE | Complete |
| **Kohya Colab** | 30 min | 10-15 min | $10/mo | Complete |
| **Kohya RunPod** | 45 min | 5-10 min | $0.50/hr | Complete |

---

## Next Steps

1. **NOW**: Start SD 1.5 PixNite training on CivitAI
2. **While that trains**: Install Kohya locally (follow steps above)
3. **If PixNite works**: Great! No need for Kohya yet
4. **If PixNite fails**: Use Kohya for 24x24 native training

---

## Quick Start Commands

```bash
# Clone and setup (5 minutes)
cd ~/Documents/GitHub
git clone https://github.com/bmaltais/kohya_ss.git
cd kohya_ss
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Launch GUI
python kohya_gui.py
# Open: http://localhost:7860
```

Ready to install Kohya now, or wait for PixNite results first?
