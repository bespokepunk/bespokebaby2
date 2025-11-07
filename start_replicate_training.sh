#!/bin/bash

# 🚀 Replicate FLUX.1-dev Training - Quick Start Script
# Bespoke Punk Pixel Art LoRA Training

set -e  # Exit on error

echo "🎨 REPLICATE FLUX.1-DEV TRAINING SETUP"
echo "========================================"
echo ""

# ========================================
# CONFIGURATION
# ========================================

# Your Replicate API token
REPLICATE_API_TOKEN="r8_bkX5IVUJk9IqmmXZ35XvCjkqsWy1hcM24kTye"

# Where to save the trained model on Replicate
DESTINATION="codelace/bespoke-punk-flux-v2"

# Dataset zip file
DATASET_ZIP="bespoke_punk_193.zip"

# Training settings
STEPS=2000
LORA_RANK=16
LEARNING_RATE=0.0004
BATCH_SIZE=1
RESOLUTION="512,768,1024"
CAPTION_DROPOUT=0.05
OPTIMIZER="adamw8bit"

# Hugging Face settings (optional)
HF_REPO_ID="codelace/bespoke-punk-flux-v2"
HF_TOKEN="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"

# W&B settings (recommended for monitoring)
WANDB_API_KEY="495752e0ee6cde7b8d27088c713f941780d902a1"
WANDB_PROJECT="bespoke-punk-flux-training"
WANDB_RUN="flux-bespoke-punk-193images-${STEPS}steps"
WANDB_SAMPLE_INTERVAL=100
WANDB_SAVE_INTERVAL=100

# ========================================
# PRE-FLIGHT CHECKS
# ========================================

echo "🔍 Pre-flight checks..."
echo ""

# Check if replicate CLI is installed
if ! command -v replicate &> /dev/null; then
    echo "❌ Replicate CLI not found!"
    echo ""
    echo "Install with:"
    echo "  pip install replicate"
    echo ""
    exit 1
fi

echo "✅ Replicate CLI found"

# Check if dataset exists
if [ ! -f "$DATASET_ZIP" ]; then
    echo "⚠️  Dataset not found: $DATASET_ZIP"
    echo ""
    echo "Creating dataset from FORTRAINING6..."

    if [ ! -d "FORTRAINING6/all" ] || [ ! -d "FORTRAINING6/oldtext" ]; then
        echo "❌ Error: FORTRAINING6 folders not found!"
        echo "Expected: FORTRAINING6/all and FORTRAINING6/oldtext"
        exit 1
    fi

    # Create proper training structure
    echo "📦 Packaging training data..."
    mkdir -p temp_training
    cp FORTRAINING6/all/*.png temp_training/
    cp FORTRAINING6/oldtext/*.txt temp_training/

    cd temp_training
    zip -r "../$DATASET_ZIP" ./*
    cd ..
    rm -rf temp_training

    echo "✅ Created $DATASET_ZIP"
else
    echo "✅ Dataset found: $DATASET_ZIP"
fi

# Verify dataset contents
DATASET_SIZE=$(du -h "$DATASET_ZIP" | cut -f1)
echo "   Size: $DATASET_SIZE"
echo ""

# Set API token
export REPLICATE_API_TOKEN="$REPLICATE_API_TOKEN"

# ========================================
# TRAINING CONFIGURATION SUMMARY
# ========================================

echo "📊 Training Configuration:"
echo "   Destination: $DESTINATION"
echo "   Steps: $STEPS"
echo "   LoRA Rank: $LORA_RANK"
echo "   Learning Rate: $LEARNING_RATE"
echo "   Resolution: $RESOLUTION"
echo "   Batch Size: $BATCH_SIZE"
echo "   Optimizer: $OPTIMIZER"
echo "   Caption Dropout: $CAPTION_DROPOUT"
echo ""
echo "   Hugging Face Upload: $([ -n "$HF_REPO_ID" ] && echo "Yes ($HF_REPO_ID)" || echo "No")"
echo "   W&B Monitoring: $([ -n "$WANDB_API_KEY" ] && echo "Yes ($WANDB_PROJECT)" || echo "No")"
echo ""

# Estimate cost and time
ESTIMATED_TIME_MIN=$((STEPS / 35))
ESTIMATED_COST=$(echo "scale=2; $ESTIMATED_TIME_MIN * 0.07" | bc)

echo "💰 Estimates:"
echo "   Training Time: ~$ESTIMATED_TIME_MIN minutes"
echo "   Estimated Cost: ~\$$ESTIMATED_COST"
echo ""

read -p "🚀 Ready to start training? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Training cancelled."
    exit 0
fi

# ========================================
# START TRAINING
# ========================================

echo ""
echo "🚀 Starting Replicate training..."
echo ""

# Build W&B sample prompts
WANDB_PROMPTS="TOK bespoke, 24x24 pixel grid portrait, female, purple solid background, brown hair, blue eyes, light skin tone, right-facing
TOK bespoke punk, 24x24 pixel art, male, orange solid background, black hair, brown eyes, tan skin, right-facing
TOK bespoke, 24x24 pixel grid, female, pink background, blonde hair, green eyes, light skin, right-facing
TOK bespoke punk style, 24x24 pixel art portrait, male, teal background, red hair, blue eyes with glasses, light skin, right-facing
TOK bespoke, 24x24 pixel grid portrait, female, yellow background, black hair, hazel eyes, tan skin, right-facing"

# Create training command
replicate training create \
  ostris/flux-dev-lora-trainer:4ffd32160efd92e956d39c5338a9b8fbafca58e03f791f6d8011f3e20e8ea6fa \
  --destination "$DESTINATION" \
  --input input_images=@"$DATASET_ZIP" \
  --input trigger_word="TOK" \
  --input steps=$STEPS \
  --input lora_rank=$LORA_RANK \
  --input learning_rate=$LEARNING_RATE \
  --input batch_size=$BATCH_SIZE \
  --input resolution="$RESOLUTION" \
  --input caption_dropout_rate=$CAPTION_DROPOUT \
  --input optimizer="$OPTIMIZER" \
  --input cache_latents_to_disk=false \
  --input gradient_checkpointing=false \
  --input hf_repo_id="$HF_REPO_ID" \
  --input hf_token="$HF_TOKEN" \
  --input wandb_project="$WANDB_PROJECT" \
  --input wandb_api_key="$WANDB_API_KEY" \
  --input wandb_run="$WANDB_RUN" \
  --input wandb_sample_interval=$WANDB_SAMPLE_INTERVAL \
  --input wandb_save_interval=$WANDB_SAVE_INTERVAL \
  --input wandb_sample_prompts="$WANDB_PROMPTS"

TRAINING_EXIT_CODE=$?

echo ""
echo "========================================"

if [ $TRAINING_EXIT_CODE -eq 0 ]; then
    echo "✅ Training started successfully!"
    echo ""
    echo "📊 Monitor your training:"
    echo "   Replicate: https://replicate.com/$DESTINATION"
    echo "   W&B: https://wandb.ai/$WANDB_PROJECT"
    echo ""
    echo "📧 You'll receive email updates from Replicate"
    echo ""
    echo "⏱️  Estimated completion: ~$ESTIMATED_TIME_MIN minutes"
    echo "💰 Estimated cost: ~\$$ESTIMATED_COST"
else
    echo "❌ Training failed to start!"
    echo "Check your Replicate API token and try again."
    exit 1
fi
