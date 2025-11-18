# Generate All 194 Punk World Images

## Quick Start (Easiest Way)

Just run this one command:

```bash
./generate-all.sh
```

That's it! The script will:
- ✅ Check dependencies are installed
- ✅ Verify API key is set
- ✅ Generate all 194 images automatically
- ✅ Save them to `public/punk-worlds/` with proper names
- ✅ Track progress so you can stop/resume anytime

---

## What You'll See

```
🎨 Bespoke Punks World Image Generator
======================================

✅ Setup complete!

Starting generation of 194 punk world images...
This will take approximately 30-60 minutes

💡 Tip: You can stop anytime (Ctrl+C) and restart later
   The script will resume from where it left off

[1/194] 🎭 lad_001_carbon
   📝 Claymation
   🚀 Submitting to API...
   ⏳ Task abc-123 - waiting for completion...
   ✅ Saved to public/punk-worlds/lad_001_carbon.jpg

[2/194] 🎭 lad_002_cash
   📝 Pixel art environment
   ...
```

---

## Files Created

All images are automatically named and saved:

```
public/punk-worlds/
  ├── lad_001_carbon.jpg
  ├── lad_002_cash.jpg
  ├── lad_003_chai.jpg
  ...
  ├── lady_097_dani2.jpg
  ├── lady_098_heyeah.jpg
  └── lady_099_vq.jpg
```

**Perfect naming** - Each image is named exactly as the punk (e.g., `lady_099_vq.jpg`)

---

## Setup Details

### ✅ Already Done For You:

1. **API Key**: Set in `.env` file
2. **Dependencies**: `node-fetch@2` and `dotenv` installed
3. **Anti-Realistic Keywords**: Added to all 183 prompts to prevent cute figurines
4. **Directory**: `public/punk-worlds/` will be created automatically

### What Happens:

1. Script reads `FREEPIK_PROMPTS.md`
2. Sends each prompt to Freepik API (Flux Pro 1.1 model)
3. Waits for image generation (5-30 seconds per image)
4. Downloads and saves with punk name
5. Tracks progress in `.generation-status.json`

---

## Stopping & Resuming

**To Stop**: Press `Ctrl+C` anytime

**To Resume**: Just run `./generate-all.sh` again - it will skip completed images and continue from where it stopped!

Progress is saved in `.generation-status.json`:
```json
{
  "completed": ["lad_001_carbon", "lad_002_cash", ...],
  "failed": [],
  "inProgress": {}
}
```

---

## Cost Estimate

- **Flux Pro 1.1**: ~$0.10-$0.20 per image
- **194 images**: ~$19-$38 USD total
- **Your credits**: You have $5 free, so ~$14-$33 will be charged

---

## If Something Goes Wrong

### "API error: 401"
Your API key might be wrong. Check `.env` file.

### "API error: 429"
Too many requests. The script already waits 2 seconds between requests, but you can increase `DELAY_BETWEEN_REQUESTS` in `scripts/generate-punk-worlds.js`

### Image quality issues
If a specific punk's image isn't right:
1. Delete the image: `rm public/punk-worlds/lady_099_vq.jpg`
2. Edit `.generation-status.json` and remove `"lady_099_vq"` from completed array
3. Update the prompt in `FREEPIK_PROMPTS.md` if needed
4. Re-run `./generate-all.sh` - it will regenerate only that one

---

## Testing First (Recommended)

To test with just a few images before generating all 194:

1. Create a test prompts file with just 3-5 punks
2. Modify line 20 in `scripts/generate-punk-worlds.js`:
   ```javascript
   const PROMPTS_FILE = path.join(__dirname, '../FREEPIK_PROMPTS_TEST.md');
   ```
3. Run the script
4. Check quality
5. Switch back to full file

---

## What's Different Now

✅ All 183 prompts updated with anti-realistic keywords:
- "stylized miniature not photorealistic"
- "abstract miniature not realistic"
- "miniature figurine not photorealistic"
- "stylized not realistic"

This prevents the AI from generating cute realistic dolls/figurines and keeps the atmospheric miniature world aesthetic.

✅ Special fixes for problematic punks:
- lady_099_vq: "voluminous bright golden yellow blonde afro hair"
- lady_098_heyeah: Athletic training space (not office)
- lady_097_dani2: Autumn garden with abstract distant character
- lady_095_royalty: Ballet theater (she's a ballerina!)
- lady_094_violetta: Music studio (she's a singer!)
- lady_096_yuri: Japanese school (she's a student!)
- lady_085_ira2: Hollywood red carpet atmosphere

---

## Ready to Go!

Everything is set up. Just run:

```bash
./generate-all.sh
```

And watch the magic happen! ✨
