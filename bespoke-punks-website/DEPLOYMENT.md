# Deployment Guide - Bespoke Punks on Render

## Pre-Deployment Checklist

✅ All files ready:
- `render.yaml` - Render configuration
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation
- Logo, banner, and favicon in `/public`
- Metadata configured in `app/layout.tsx`
- Production build tested successfully

## Deploy to Render

### Step 1: Push to GitHub

```bash
# Add all files
git add .

# Commit changes
git commit -m "Prepare for Render deployment - add logo, banner, and configuration"

# Push to main branch
git push origin main
```

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click **"Create Web Service"**

### Step 3: Configuration (Auto-detected from render.yaml)

- **Name**: bespoke-punks-website
- **Runtime**: Node
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`
- **Plan**: Free
- **Node Version**: 20.11.0

### Step 4: Environment Variables

No environment variables needed! The site is fully static with client-side rendering.

### Step 5: Deploy

Click **"Create Web Service"** and Render will:
1. Clone your repository
2. Install dependencies
3. Build the production bundle
4. Start the server
5. Provide you with a live URL: `https://bespoke-punks-website.onrender.com`

## Post-Deployment

### Update Domain (Optional)

If you have a custom domain:
1. Go to your web service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `bespokepunks.com`)
4. Update `metadataBase` in `app/layout.tsx` to your custom domain

### Verify Deployment

Check these pages:
- `/` - Homepage with asymmetric punk layout
- `/gallery` - Full collection (174 punks)
- `/about` - Artist bio
- `/generate` - Coming soon page

### Monitor Performance

- Render provides logs in the dashboard
- Check "Logs" tab for any build or runtime errors
- Monitor response times in "Metrics"

## Troubleshooting

### Build Fails

- Check Node version is 20.11.0
- Verify all dependencies are in `package.json`
- Check build logs for specific errors

### Images Not Loading

- Verify `/public/punks-display/` has all 174 PNG files
- Check that `punk-names.json` matches available images

### Slow Performance

- Render free tier may spin down after 15 minutes of inactivity
- First load after sleep takes ~30 seconds
- Consider upgrading to paid tier for always-on service

## Free Tier Limitations

- Spins down after 15 minutes of inactivity
- 750 hours/month (enough for continuous operation)
- Shared resources (may be slower than paid tiers)

## Upgrade Options

For production use, consider:
- **Starter Plan** ($7/mo): Always-on, faster, more resources
- **Standard Plan** ($25/mo): Even more resources, better performance

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Next.js Docs: https://nextjs.org/docs

---

**Ready to deploy! Push to GitHub and create your Render service.**
