# Bespoke Baby SD 1.5 LoRA Training Package

Complete RunPod training package for Stable Diffusion 1.5 LoRA fine-tuning.

## Quick Start

1. Upload this package to your RunPod instance
2. Extract: `unzip bespoke_baby_runpod_training.zip`
3. Navigate: `cd bespoke_baby_training`
4. Run: `bash start_training.sh`

That's it! The script handles everything automatically.

## What's Included

- **training_data/**: 203 pixel art images + captions (24x24, 512x512 resolution)
- **training_config.toml**: Pre-configured training parameters
- **start_training.sh**: Automated training script
- **README.md**: This file

## Training Configuration

- Model: Stable Diffusion 1.5
- LoRA Rank (Network Dim): 32
- Network Alpha: 16
- Learning Rate: 1e-4
- Epochs: 10
- Batch Size: 1
- Gradient Accumulation: 4
- Mixed Precision: FP16
- Optimizer: AdamW8bit
- Scheduler: Cosine with restarts

## Output

Trained models will be saved to `/workspace/output/` as:
- `bespoke_baby_sd15_lora-000001.safetensors` (Epoch 1)
- `bespoke_baby_sd15_lora-000002.safetensors` (Epoch 2)
- ... up to Epoch 10

## Requirements

- RunPod instance with GPU (RTX 3090/4090 or A100 recommended)
- CUDA 11.8+
- 24GB+ VRAM recommended
- Ubuntu 20.04/22.04

## Support

Training logs available at `/workspace/logs/`
