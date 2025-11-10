# RunPod SD 1.5 Training - Complete Instructions

## STEP 1: CLEANUP DISK (OPTIONAL)

To free up space before uploading, run:

```bash
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2
bash CLEANUP_COMMANDS.sh
```

This will remove old RunPod files, scripts, and model files. If you need more space, edit the script and uncomment the lines to remove large folders (output/, models/, kohya_ss/).

---

## STEP 2: UPLOAD TO RUNPOD

### File to Upload:
`/Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke_baby_runpod_training.zip`

### Upload Methods:

**Option A - Via RunPod Web Interface:**
1. Go to your RunPod pod
2. Use the file manager to upload `bespoke_baby_runpod_training.zip`
3. Upload to `/workspace/`

**Option B - Via SCP (if SSH enabled):**
```bash
scp /Users/ilyssaevans/Documents/GitHub/bespokebaby2/bespoke_baby_runpod_training.zip root@YOUR_POD_IP:/workspace/
```

**Option C - Via wget (upload to a temporary host first):**
```bash
# On RunPod terminal:
cd /workspace
wget YOUR_DOWNLOAD_URL/bespoke_baby_runpod_training.zip
```

---

## STEP 3: START TRAINING (SINGLE COMMAND)

Once the zip file is uploaded, connect to your RunPod terminal and run:

```bash
cd /workspace && unzip -q bespoke_baby_runpod_training.zip && cd bespoke_baby_training && bash start_training.sh
```

That's it! The script will:
1. Setup all directories
2. Install all dependencies (Kohya SS, PyTorch, xformers, etc.)
3. Clone Kohya SS sd-scripts
4. Configure training parameters
5. Start the training automatically

---

## TRAINING DETAILS

- **Model:** Stable Diffusion 1.5
- **LoRA Rank:** 32
- **Learning Rate:** 1e-4
- **Epochs:** 10
- **Dataset:** 203 images with world-class captions
- **Batch Size:** 1 (with gradient accumulation 4)
- **Optimizer:** AdamW8bit
- **Output:** `/workspace/output/bespoke_baby_sd15_lora-NNNNNN.safetensors`

---

## MONITORING

Training logs will be displayed in real-time. Models are saved every epoch to:
`/workspace/output/`

Download your trained LoRA models from this directory when training completes.

---

## TROUBLESHOOTING

If training fails:
1. Check `/workspace/logs/` for detailed logs
2. Ensure GPU has 24GB+ VRAM
3. Verify CUDA 11.8+ is installed
4. Check disk space with `df -h`

---

## PACKAGE CONTENTS

```
bespoke_baby_runpod_training.zip
├── training_data/          # 203 PNG + TXT pairs (world-class captions)
├── training_config.toml    # Pre-configured training parameters
├── start_training.sh       # Executable training script
└── README.md              # Quick reference
```
