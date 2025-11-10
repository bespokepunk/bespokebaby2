# Bespoke Baby - Deployment Guide

Complete guide for deploying both the **Caption Review Interface** and **Punk Generator** to Render.

---

## 📦 Project Overview

This repository contains two production-ready applications:

1. **Caption Review Interface** - Supabase-powered web UI for reviewing training captions
2. **Punk Generator** - AI pipeline that generates pixel art punks from user photos

Both can be deployed to Render for production use.

---

## 🎯 Application 1: Caption Review Interface

### Purpose
Web interface for reviewing and editing caption data stored in Supabase.

### Files Needed
- `SUPABASE_REVIEW.html` - Main review interface
- `supabase_setup.sql` OR `supabase_setup_FULL.sql` - Database schema
- `add_final_caption_txt_column.sql` - Schema update
- `.env` - Supabase credentials (API keys)

### Setup Instructions

#### 1. Supabase Database Setup

**Create a Supabase project** at https://supabase.com

**Run SQL setup scripts** in order:
```sql
-- Option A: Run full setup
-- Copy contents of supabase_setup_FULL.sql into Supabase SQL Editor

-- Option B: Run basic setup + column addition
-- 1. Copy supabase_setup.sql
-- 2. Copy add_final_caption_txt_column.sql
```

This creates the `caption_reviews` table:
```sql
CREATE TABLE caption_reviews (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE,
    original_caption TEXT,
    final_caption_txt TEXT,
    final_caption TEXT,
    user_corrections TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. Get Supabase Credentials

From your Supabase dashboard:
1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Anon/Public Key** (starts with `eyJ...`)

#### 3. Configure Environment Variables

Create `.env` file (or set in Render):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 4. Deploy to Render

**Option A: Static Site (Recommended for HTML)**
1. Connect GitHub repo to Render
2. Create new **Static Site**
3. Settings:
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.` (root)
4. Add environment variables from `.env`
5. Deploy!

**Option B: Web Service**
If you want to add backend processing:
1. Create new **Web Service**
2. Add a simple server (e.g., Python Flask or Node.js Express)
3. Serve `SUPABASE_REVIEW.html`

#### 5. Usage

Once deployed:
1. Open the URL (e.g., `https://bespoke-baby-review.onrender.com`)
2. Interface loads caption data from Supabase
3. Review captions:
   - **A** = Approve
   - **E** = Save edits
   - **S** = Skip
4. All changes save to Supabase automatically

---

## 🎨 Application 2: Punk Generator

### Purpose
AI pipeline that converts user photos into 24x24 pixel art Bespoke Punks.

### Files Needed
- `user_to_bespoke_punk_PRODUCTION.py` - Main generator script
- `app_gradio.py` OR `bespoke_punk_ui.py` - Web interface
- `requirements_runpod.txt` - Python dependencies
- Epoch 7 LoRA model file (`.safetensors`)

### Technical Stack
- **AI Model**: Stable Diffusion 1.5 + Custom LoRA
- **Framework**: Diffusers (HuggingFace)
- **UI**: Gradio (web interface)
- **Resolution**: 512x512 → 24x24 pixel art

### Setup Instructions

#### 1. Prerequisites

**Python 3.10+** and dependencies:
```bash
pip install -r requirements_runpod.txt
```

Or manually:
```bash
pip install torch diffusers pillow numpy transformers accelerate gradio peft
```

**LoRA Model File**:
- Location: `/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000007.safetensors`
- Upload to Render or cloud storage
- Or provide download URL in deployment

#### 2. Deploy to Render

**Create Web Service:**
1. Connect GitHub repo
2. Settings:
   - **Environment**: Python 3.10
   - **Build Command**: `pip install -r requirements_runpod.txt`
   - **Start Command**: `python app_gradio.py`
   - **Instance Type**: Standard Plus (need 2GB+ RAM)

3. Add environment variables:
```bash
LORA_PATH=/path/to/bespoke_punks_SD15_PERFECT-000007.safetensors
PORT=7860
```

4. Deploy!

**Important Notes:**
- Render's free tier may be too slow for AI generation
- Recommend **Standard Plus** ($7/month) or higher
- First run downloads SD 1.5 model (~4GB) - may take 5-10 minutes

#### 3. Alternative: Serverless GPU

For better performance, use **Modal** or **Replicate** instead:

**Modal.com Example:**
```python
import modal

stub = modal.Stub("bespoke-punk-generator")

@stub.function(
    image=modal.Image.debian_slim().pip_install("torch", "diffusers", "pillow"),
    gpu="A10G",
    secret=modal.Secret.from_name("my-huggingface-secret")
)
def generate_punk(image_path: str, gender: str = "lady"):
    from user_to_bespoke_punk_PRODUCTION import UserToBespokePunkPipeline

    pipeline = UserToBespokePunkPipeline(lora_path="./epoch7.safetensors")
    result = pipeline.process(image_path, gender=gender)
    return result

@stub.local_entrypoint()
def main(image_path: str):
    result = generate_punk.remote(image_path)
    print(f"Generated punk: {result}")
```

Deploy: `modal deploy app.py`

Cost: ~$0.003 per generation (only pay when used)

#### 4. Usage

**Web Interface (Gradio):**
```
https://your-app.onrender.com
```

Features:
- Upload user photo
- Select gender (lady/lad)
- Generate 512x512 and 24x24 versions
- View generated prompt
- Download NFT-ready image

**API Usage:**
```python
from user_to_bespoke_punk_PRODUCTION import UserToBespokePunkPipeline

pipeline = UserToBespokePunkPipeline(lora_path="./epoch7.safetensors")

result = pipeline.process(
    user_image_path="photo.jpg",
    gender="lady",
    seed=42  # Optional: reproducible results
)

# Returns:
{
    'image_512': PIL.Image,      # 512x512 full res
    'image_24': PIL.Image,       # 24x24 NFT
    'prompt': str,               # Generated prompt
    'features': {                # Detected features
        'hair_color': 'brown',
        'eye_color': 'brown',
        'skin_tone': 'light',
        'background_color': 'blue'
    }
}
```

---

## 🔧 Environment Variables Reference

### Caption Review Interface
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Punk Generator
```bash
LORA_PATH=/path/to/epoch7.safetensors
PORT=7860
HF_HOME=/tmp/.cache/huggingface  # For Render disk space
```

---

## 📊 Resource Requirements

### Caption Review Interface
- **CPU**: Minimal (static HTML + JS)
- **RAM**: < 512MB
- **Storage**: < 10MB
- **Cost**: Free tier works ✅

### Punk Generator
- **CPU**: Not suitable (too slow)
- **GPU**: A10G or better (for <10s generation)
- **RAM**: 2GB+ (for model loading)
- **Storage**: 5GB+ (SD 1.5 base + LoRA)
- **Cost**:
  - Render Standard: $7/month (slow, CPU only)
  - Modal/Replicate: ~$0.003/generation (fast, GPU)

---

## 🚀 Deployment Checklist

### Caption Review Interface
- [ ] Supabase project created
- [ ] Database schema deployed (run SQL scripts)
- [ ] Environment variables configured
- [ ] Static site deployed to Render
- [ ] Test: Load interface and see caption data
- [ ] Test: Save edits and verify in Supabase

### Punk Generator
- [ ] Python dependencies installed
- [ ] Epoch 7 LoRA uploaded/accessible
- [ ] Render Web Service created
- [ ] Environment variables set
- [ ] First deployment complete (model downloaded)
- [ ] Test: Upload photo and generate punk
- [ ] Test: Verify 24x24 output is pixel art

---

## 🔍 Troubleshooting

### Caption Review: "Failed to fetch"
**Problem**: CORS error or invalid Supabase URL

**Solution**:
1. Check `.env` has correct `SUPABASE_URL` and `SUPABASE_ANON_KEY`
2. Verify Supabase project is active
3. Check RLS policies allow anonymous read/write

### Punk Generator: "Out of memory"
**Problem**: Insufficient RAM for model loading

**Solution**:
1. Upgrade Render instance to Standard Plus
2. OR use serverless GPU (Modal/Replicate)
3. OR reduce batch size (if processing multiple images)

### Punk Generator: "Generation too slow" (>3 minutes)
**Problem**: Using CPU instead of GPU

**Solution**:
1. Render doesn't provide GPU on standard plans
2. Use Modal.com or Replicate.com for GPU access
3. Expected: 5-10s with GPU vs 3-5 minutes with CPU

### Database: "relation caption_reviews does not exist"
**Problem**: Database schema not created

**Solution**:
1. Run SQL setup scripts in Supabase SQL Editor
2. Verify table exists: `SELECT * FROM caption_reviews LIMIT 1;`

---

## 📁 Essential Files Summary

### Keep in Repository
```
bespokebaby2/
├── SUPABASE_REVIEW.html           # Caption review UI
├── user_to_bespoke_punk_PRODUCTION.py  # Generator core
├── app_gradio.py                  # Web interface
├── requirements_runpod.txt        # Dependencies
├── supabase_setup_FULL.sql        # DB schema
├── .env                           # Credentials (DO NOT COMMIT!)
├── .gitignore                     # Exclude .env
├── README.md                      # Project overview
├── DEPLOYMENT.md                  # This file
├── TRAINING_PROGRESS.md           # Training docs
└── TRAINING_RESULTS_SUMMARY.md    # Final results

Training Data (for reference):
├── civitai_v2_7_training/         # 203 images + captions
├── sd15_training_512/             # SD 1.5 training data
└── runpod_package/                # RunPod scripts
```

### Archived (not needed for deployment)
- All test output directories → `/Users/.../Downloads/archived_test_outputs/`
- Old scripts and experiments → Removed
- Historical documentation → `/Users/.../Downloads/archived_docs/`

---

## 🎉 Production URLs

Once deployed, you'll have:

**Caption Review Interface**:
```
https://bespoke-baby-review.onrender.com
```

**Punk Generator**:
```
https://bespoke-punk-generator.onrender.com
```

Or custom domains if configured!

---

## 💡 Next Steps

1. **Test both applications** locally first
2. **Deploy Caption Review** (easiest, static site)
3. **Test Punk Generator** locally with your LoRA
4. **Decide on GPU strategy** (Render vs Modal vs Replicate)
5. **Deploy Punk Generator** with chosen platform
6. **Connect to frontend** (if building web app)
7. **Add monitoring/analytics** (optional)

---

## 📞 Support & Resources

- **Training Documentation**: See `TRAINING_RESULTS_SUMMARY.md`
- **Generator API**: See `PRODUCTION_WORKFLOW_README.md`
- **Supabase Docs**: https://supabase.com/docs
- **Render Docs**: https://render.com/docs
- **Modal Docs**: https://modal.com/docs
- **Diffusers Docs**: https://huggingface.co/docs/diffusers

---

**Repository cleaned and ready for deployment!** 🚀
