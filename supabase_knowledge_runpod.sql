-- RunPod Training Knowledge Base Entry
-- Insert this into Supabase to permanently store working setup

INSERT INTO knowledge_base (
  project_name,
  category,
  title,
  content,
  status,
  last_verified,
  critical_lessons,
  working_commands
) VALUES (
  'bespoke_baby',
  'runpod_training',
  'RunPod SD Training Setup - VERIFIED WORKING',

  '# THE WORKING 3-STEP PROCESS

## Step 1: Clear Space & Extract
```bash
cd /workspace
rm -rf /workspace/.cache/*
rm -rf ~/.cache/*
rm -rf /workspace/training_parent
rm -rf /workspace/runpod_package
unzip -q training_data_IMPROVED.zip
mkdir -p /workspace/training_parent/10_bespoke_punk
mv /workspace/runpod_package/training_data_IMPROVED/* /workspace/training_parent/10_bespoke_punk/
df -h /workspace
```

## Step 2: Create Training Script
```bash
cat > /workspace/GO.sh << ''EOF''
#!/bin/bash
cd /workspace/sd-scripts
accelerate launch --num_cpu_threads_per_process=2 train_network.py \
  --pretrained_model_name_or_path=/workspace/models/sd15_base.safetensors \
  --train_data_dir=/workspace/training_parent \
  --resolution=512,512 \
  --output_dir=/workspace/output \
  --output_name=bespoke_punks_IMPROVED \
  --save_model_as=safetensors \
  --max_train_epochs=10 \
  --learning_rate=0.0001 \
  --unet_lr=0.0001 \
  --text_encoder_lr=0.00005 \
  --lr_scheduler=cosine_with_restarts \
  --network_module=networks.lora \
  --network_dim=32 \
  --network_alpha=16 \
  --save_every_n_epochs=2 \
  --mixed_precision=fp16 \
  --save_precision=fp16 \
  --cache_latents \
  --optimizer_type=AdamW8bit \
  --xformers \
  --train_batch_size=4 \
  --gradient_checkpointing \
  --caption_extension=.txt \
  --shuffle_caption \
  --keep_tokens=2 \
  --max_token_length=225 \
  --seed=42
EOF
```

## Step 3: Run Training
```bash
chmod +x /workspace/GO.sh
bash /workspace/GO.sh
```',

  'working',
  '2025-11-11',

  '# CRITICAL LESSONS
1. ❌ NEVER paste multi-line commands directly - terminal splits them
2. ✅ ALWAYS use script files with heredoc (cat > file << EOF)
3. ❌ 33GB cache accumulates in /workspace/.cache - MUST DELETE FIRST
4. ✅ Correct path is /workspace/sd-scripts NOT /workspace/kohya_ss/sd-scripts
5. ❌ Clearing cache deletes extracted files - must re-extract
6. ✅ Kohya requires parent/##_subfolder structure for training data
7. ❌ train_lora.py does not exist - use train_network.py
8. ✅ Files save every 2 epochs to /workspace/output/

# WHAT WENT WRONG BEFORE
- Used wrong paths repeatedly
- Pasted commands that split on newlines
- Forgot to clear 33GB cache causing disk full
- Cleared cache but forgot to re-extract data
- Gave incomplete "quick resume" commands
- Did not create robust script template

# WHAT FINALLY WORKED
Creating GO.sh script with heredoc instead of pasting multi-line commands.',

  '# QUICK REFERENCE

## Clear 33GB Cache
rm -rf /workspace/.cache/*

## Check Space
df -h /workspace

## Verify Training Data
ls /workspace/training_parent/10_bespoke_punk/ | wc -l
# Should show ~406 files (203 images + 203 captions)

## Check Saved Models
ls -lh /workspace/output/

## Expected Output When Working
"found directory /workspace/training_parent/10_bespoke_punk contains 203 image files"
"2030 train images with repeating"
"create LoRA for Text Encoder: 72 modules"
"create LoRA for U-Net: 192 modules"
"epoch 1/10"

## Variable Reference
- REPEAT_COUNT: 10 (folder name: 10_bespoke_punk)
- EPOCHS: 10
- SAVE_EVERY: 2 epochs
- RESOLUTION: 512,512
- BATCH_SIZE: 4
- LEARNING_RATE: 0.0001 (unet), 0.00005 (text encoder)
- LORA_DIM: 32
- LORA_ALPHA: 16
- KEEP_TOKENS: 2
- SEED: 42

## File Locations
- Training script: /workspace/sd-scripts/train_network.py
- Base model: /workspace/models/sd15_base.safetensors
- Training data: /workspace/training_parent/10_bespoke_punk/
- Output: /workspace/output/bespoke_punks_IMPROVED-XXXXXX.safetensors
- Launch script: /workspace/GO.sh

## Training Time
- Per epoch: 25-30 min on A40
- Total (10 epochs): 4-5 hours
- First epoch slower (caches latents)

## Download Models After Training
scp runpod:/workspace/output/*.safetensors ./models/runpod_checkpoints/'

) ON CONFLICT (project_name, title) DO UPDATE SET
  content = EXCLUDED.content,
  status = EXCLUDED.status,
  last_verified = EXCLUDED.last_verified,
  critical_lessons = EXCLUDED.critical_lessons,
  working_commands = EXCLUDED.working_commands;
