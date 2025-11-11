# RunPod Disk Space Cleanup Guide

**When to use:** RunPod instance running out of disk space
**Safe to run:** Yes - script checks before deleting

---

## 🔍 What Takes Up Space on RunPod

### Common Space Hogs:

1. **Old Training Checkpoints** (5-20 GB)
   - Location: `/workspace/output/*.safetensors`
   - Safe to delete: YES (if already downloaded locally)

2. **Hugging Face Model Cache** (10-50 GB)
   - Location: `~/.cache/huggingface/`
   - Safe to delete: YES (models will re-download)

3. **Training Data** (500 MB - 5 GB)
   - Location: `/workspace/training_data/`
   - Safe to delete: ONLY old/superseded data

4. **Pip Cache** (1-5 GB)
   - Location: `~/.cache/pip/`
   - Safe to delete: YES (packages will re-download if needed)

5. **Docker Images/Layers** (10-30 GB)
   - Safe to delete: YES (if you have access)

---

## 🚀 Quick Cleanup (SSH into RunPod)

### Step 1: Upload cleanup script

**On your local machine:**
```bash
# Upload to RunPod
scp runpod_cleanup.sh root@<runpod-ip>:/workspace/
```

**Or copy/paste directly into RunPod terminal:**
```bash
# Create file on RunPod
nano /workspace/runpod_cleanup.sh
# Paste the script contents
# Ctrl+O to save, Ctrl+X to exit

# Make executable
chmod +x /workspace/runpod_cleanup.sh
```

### Step 2: Run cleanup script

```bash
cd /workspace
./runpod_cleanup.sh
```

---

## ⚡ Manual Quick Cleanup Commands

**If you just want to run commands directly:**

### 1. Check disk usage
```bash
df -h /workspace
du -sh /workspace/* | sort -hr | head -10
```

### 2. Clear pip cache (1-5 GB)
```bash
pip cache purge
```

### 3. Clear temp files (100 MB - 1 GB)
```bash
rm -rf /tmp/*
```

### 4. Remove old training checkpoints (if downloaded)
```bash
# LIST first to verify
ls -lh /workspace/output/*.safetensors

# Delete specific old run
rm -rf /workspace/output/old_experiment_name-*.safetensors

# Or delete ALL old checkpoints (BE CAREFUL!)
# rm -rf /workspace/output/*.safetensors
```

### 5. Clear Hugging Face cache (10-50 GB)
```bash
# This will free a LOT of space but models will re-download
rm -rf ~/.cache/huggingface/*
```

### 6. Docker cleanup (if available)
```bash
docker system prune -a -f
```

---

## 🎯 Recommended Cleanup Strategy

### Before Training (Prep for new run):

```bash
# 1. Check available space
df -h /workspace

# 2. Clear pip cache (safe, always do this)
pip cache purge

# 3. Clear temp files (safe)
rm -rf /tmp/*

# 4. Remove OLD checkpoints (if you have them backed up locally)
# VERIFY FIRST! ls -lh /workspace/output/
rm -rf /workspace/output/old_experiment_*.safetensors

# 5. If still need space, clear HuggingFace cache
# (models will re-download - adds ~30 min to training start)
# rm -rf ~/.cache/huggingface/*
```

### After Training (Download checkpoints first!):

```bash
# 1. Download all checkpoints to local machine first!
# scp root@<runpod>:/workspace/output/*.safetensors ~/Downloads/

# 2. Then clear output directory
rm -rf /workspace/output/*.safetensors

# 3. Clear caches
pip cache purge
rm -rf /tmp/*
```

---

## ⚠️ What NOT to Delete

**DO NOT DELETE:**
- `/workspace/runpod_package/` - Your current training data
- `/workspace/sd-scripts/` - Training framework
- `/workspace/training_config.toml` - Your config
- **Any .safetensors you haven't downloaded yet!**

---

## 📊 Typical Space Usage

**Fresh RunPod Instance:**
- Base system: ~10-15 GB
- Available: ~35-40 GB (on 50 GB disk)

**After Training Setup:**
- + sd-scripts: ~2 GB
- + Python packages: ~5 GB
- + Hugging Face models: ~15 GB
- Available: ~15-20 GB

**During Training:**
- + Training data: ~500 MB
- + Checkpoints (per epoch): ~500 MB
- + Logs: ~100 MB
- Available: ~10-15 GB (enough for 8 epochs)

**Common Issue:**
If you run multiple training runs without cleanup, old checkpoints pile up!

---

## 🔧 Emergency Cleanup (Out of Space!)

**If training fails with "No space left on device":**

```bash
# 1. Immediate cleanup (safe)
pip cache purge && rm -rf /tmp/*

# 2. Check what's using space
du -sh /workspace/* | sort -hr

# 3. Remove old checkpoints (verify first!)
ls -lh /workspace/output/
rm /workspace/output/old_*.safetensors

# 4. Nuclear option: Clear HuggingFace cache
# (adds 30 min re-download time)
rm -rf ~/.cache/huggingface/*

# 5. Restart training
```

---

## 📁 Script Files

**Cleanup script location (local):**
`/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_cleanup.sh`

**To use on RunPod:**
1. Upload via web interface or `scp`
2. `chmod +x runpod_cleanup.sh`
3. `./runpod_cleanup.sh`

---

## ✅ Best Practices

1. **Before each training run:** Clear pip cache and temp files
2. **After each training run:** Download checkpoints, then delete from RunPod
3. **Monitor space:** `df -h` before training starts
4. **Keep current run only:** Delete old experiment checkpoints

---

**Quick one-liner cleanup (safe):**
```bash
pip cache purge && rm -rf /tmp/* && df -h /workspace
```

This typically frees 2-5 GB and is safe to run anytime!
