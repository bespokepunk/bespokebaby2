# RunPod Training Instructions - V2.7 (COMPLETE)

## What Was Wrong Before

1. **Wrong zip structure** - Old zip had `FORTRAINING6/bespokepunks/` folders, scripts expected `/workspace/training_data/`
2. **Missing dependencies** - Scripts were missing critical packages causing random failures
3. **Incomplete setup** - Multiple steps needed, easy to miss one

## What's Fixed Now

✅ **Complete dependency installation** - ALL packages in one script
✅ **Correct zip structure** - Files extract directly, no nested folders
✅ **Automatic data handling** - Script handles extraction and moving files
✅ **Full error checking** - Verifies everything before training starts

## How to Use (3 Simple Steps)

### Step 1: Upload Files to RunPod

Upload these 2 files to `/workspace/`:
- `RUNPOD_COMPLETE_V2_7.sh` (the training script)
- `bespoke_punks_v2_7_CORRECT.zip` (the training data)

### Step 2: Make Script Executable

```bash
cd /workspace
chmod +x RUNPOD_COMPLETE_V2_7.sh
```

### Step 3: Run Training

```bash
bash RUNPOD_COMPLETE_V2_7.sh
```

That's it! The script will:
1. Install Kohya SS
2. Install ALL dependencies (no more missing packages!)
3. Extract and organize training data properly
4. Verify everything is correct
5. Start training

## Expected Output

```
Training started at: [timestamp]
Expected Duration: 2-3 hours on RTX 4090

[Training progress will show here]

✓ TRAINING COMPLETE!
Output models:
  /workspace/output/bespoke_punks_v2_7-000001.safetensors
  /workspace/output/bespoke_punks_v2_7-000002.safetensors
  ...
  /workspace/output/bespoke_punks_v2_7-000010.safetensors
```

## Files You Need

Use these NEW files (NOT the old ones):
- ✅ `RUNPOD_COMPLETE_V2_7.sh` - Complete training script with ALL dependencies
- ✅ `bespoke_punks_v2_7_CORRECT.zip` - Correctly structured training data (881KB)

## Troubleshooting

If training fails:
1. Check `/workspace/training_data/` exists and has 200+ images
2. Check `/workspace/kohya_ss/sd-scripts/train_network.py` exists
3. Run `nvidia-smi` to verify GPU is available
4. Check disk space: `df -h /workspace`

## Training Parameters

- **Resolution**: 24x24 (native pixel art size)
- **Base Model**: SDXL (stable-diffusion-xl-base-1.0)
- **Epochs**: 10
- **Batch Size**: 4
- **Learning Rate**: 0.0001
- **Network Dim**: 32
- **Network Alpha**: 16

## After Training

Download all `.safetensors` files from `/workspace/output/`

Test different epochs to find the best one (usually epoch 3-5 is optimal).
