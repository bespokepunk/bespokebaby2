# RunPod Training - Quick Start

**Last Updated:** 2025-11-11 ✅ VERIFIED WORKING

## 🚨 CRITICAL: Use Script Method, NOT Copy-Paste

RunPod terminal splits multi-line commands incorrectly. **Always use the script method below.**

---

## The 3-Step Process

### 1️⃣ Clear Space & Extract (1 command)

```bash
cd /workspace && rm -rf /workspace/.cache/* ~/.cache/* /workspace/training_parent /workspace/runpod_package && unzip -q training_data_IMPROVED.zip && mkdir -p /workspace/training_parent/10_bespoke_punk && mv /workspace/runpod_package/training_data_IMPROVED/* /workspace/training_parent/10_bespoke_punk/ && df -h /workspace
```

### 2️⃣ Create Training Script (1 block)

```bash
cat > /workspace/GO.sh << 'EOF'
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

### 3️⃣ Run Training (2 commands)

```bash
chmod +x /workspace/GO.sh
bash /workspace/GO.sh
```

---

## ✅ Success Indicators

Training is working when you see:
- `found directory /workspace/training_parent/10_bespoke_punk contains 203 image files`
- `2030 train images with repeating`
- `create LoRA for Text Encoder: 72 modules`
- `create LoRA for U-Net: 192 modules`
- `epoch 1/10`
- `steps: 1%|█▉`

---

## 📊 Training Info

- **Duration:** 4-5 hours (10 epochs on A40)
- **Checkpoints:** Every 2 epochs → `/workspace/output/`
- **Files:** `bespoke_punks_IMPROVED-000002.safetensors`, `-000004.safetensors`, etc.
- **Space Required:** 5GB+ free (clear 33GB cache first)

---

## 🔍 Check Progress

```bash
# Check saved models
ls -lh /workspace/output/

# Monitor training (in separate terminal)
watch -n 10 'ls -lh /workspace/output/'
```

---

## 📥 Download After Training

```bash
# From local machine:
scp runpod:/workspace/output/*.safetensors ./models/runpod_checkpoints/
```

---

## 📚 Full Documentation

- **Complete Setup:** `docs/RUNPOD_SETUP_FINAL.md`
- **Retraining Guide:** `docs/RETRAINING_INSTRUCTIONS.md`
- **Supabase Record:** `supabase_knowledge_runpod.sql`

---

## ❌ Common Mistakes (Don't Do These)

1. ❌ Pasting multi-line commands directly
2. ❌ Forgetting to clear 33GB cache first
3. ❌ Using wrong paths (kohya_ss vs sd-scripts)
4. ❌ Clearing cache without re-extracting data

## ✅ What Works

1. ✅ Use script file with heredoc (`cat > file << 'EOF'`)
2. ✅ Clear cache before every run
3. ✅ Use `/workspace/sd-scripts/` (not kohya_ss)
4. ✅ Re-extract after clearing cache

---

**Training is currently running and working correctly as of 2025-11-11.**
