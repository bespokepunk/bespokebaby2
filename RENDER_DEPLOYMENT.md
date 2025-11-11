# Render Deployment Guide - Bespoke Punk Generator

## Quick Deploy to Render

### 1. Prepare Repository

```bash
# Commit all changes
git add .
git commit -m "Add authentication and Render deployment config"
git push origin main
```

### 2. Create Render Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `bespokebaby2`
4. Configure settings:

**Basic Settings:**
- **Name:** `bespoke-punk-generator`
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** (leave blank)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app_gradio.py`

**Instance Type:**
- Start with **Starter** ($7/month)
- Upgrade to **Standard** if needed (more RAM for model)

### 3. Environment Variables

Add these in Render Dashboard → Environment tab:

```
GRADIO_USERNAME=admin
GRADIO_PASSWORD=YourSecurePassword123!
RENDER=true
```

### 4. Advanced Settings

**Disk:**
- Add a disk mount at `/opt/render/project/src/.cache` (for model caching)
- Size: 10GB

**Health Check:**
- Path: `/`
- Wait: 180 seconds (model loading takes time)

### 5. Deploy

Click **"Create Web Service"** - First deployment takes 10-15 minutes:
1. Building (pip install dependencies)
2. Model download (~2GB for SD 1.5)
3. LoRA loading
4. Server start

### 6. Access Your App

Your app will be at: `https://bespoke-punk-generator.onrender.com`

Login with credentials you set in environment variables.

---

## Troubleshooting

### Issue: Out of Memory
**Solution:** Upgrade to Standard instance (4GB RAM minimum)

### Issue: Slow Cold Starts
**Render free tier spins down after inactivity**
**Solution:**
- Keep instance always on (paid plans)
- Or accept 2-3 min cold start

### Issue: Model not found
**Solution:** Ensure `lora_checkpoints/caption_fix/caption_fix_epoch8.safetensors` is committed to repo

---

## Cost Estimate

**Starter Plan:** $7/month
- 512 MB RAM (may need upgrade)
- Automatic sleeping after inactivity

**Standard Plan:** $25/month
- 2 GB RAM (recommended)
- Always on
- Better performance

---

## Production Checklist

- [ ] Push code to GitHub
- [ ] Create Render web service
- [ ] Set environment variables (auth credentials)
- [ ] Configure disk storage for models
- [ ] Wait for initial deployment (10-15 min)
- [ ] Test authentication works
- [ ] Test image generation
- [ ] Monitor performance and upgrade instance if needed

---

## Local Testing with Auth

```bash
# Set environment variables
export GRADIO_USERNAME=admin
export GRADIO_PASSWORD=test123

# Run app
python app_gradio.py
```

Then visit http://127.0.0.1:7860 and login with credentials.
