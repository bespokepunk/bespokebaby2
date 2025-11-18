# Punk Worlds Automated Generation

This script automatically generates all 194 punk world images using the Freepik API.

## Setup

### 1. Get Freepik API Key

1. Go to https://www.freepik.com/api
2. Sign up or log in
3. Get your API key (you get $5 USD in free credits)

### 2. Install Dependencies

```bash
npm install node-fetch@2
```

### 3. Set API Key

```bash
export FREEPIK_API_KEY="your-api-key-here"
```

Or add to your `.bashrc` / `.zshrc`:
```bash
echo 'export FREEPIK_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Generate All Images

```bash
node scripts/generate-punk-worlds.js
```

The script will:
- ✅ Read all prompts from `FREEPIK_PROMPTS.md`
- ✅ Generate images using Flux Pro 1.1 model
- ✅ Save to `public/punk-worlds/{punk_name}.jpg`
- ✅ Track progress in `.generation-status.json`
- ✅ Resume from where it left off if interrupted
- ✅ Retry failed generations automatically

### Features

**Smart Resume**: The script tracks which images have been generated. If interrupted, just run it again and it will continue from where it stopped.

**Rate Limiting**: Automatically waits 2 seconds between requests to avoid hitting rate limits.

**Retry Logic**: Retries failed generations up to 3 times with exponential backoff.

**Progress Tracking**: Shows real-time progress with detailed status for each punk.

**Error Handling**: Failed generations are logged and can be retried separately.

## Output

Images are saved to:
```
public/punk-worlds/
  lad_001_carbon.jpg
  lad_002_cash.jpg
  ...
  lady_099_vq.jpg
```

## Status File

Progress is tracked in `.generation-status.json`:
```json
{
  "completed": ["lad_001_carbon", "lad_002_cash"],
  "failed": [],
  "inProgress": {}
}
```

## Troubleshooting

### "FREEPIK_API_KEY environment variable not set"
Set your API key: `export FREEPIK_API_KEY="your-key"`

### "API error: 401"
Your API key is invalid. Get a new one from https://www.freepik.com/api

### "API error: 429 - Rate limit"
You're making requests too fast. The script already has rate limiting, but you can increase `DELAY_BETWEEN_REQUESTS` in the script.

### "Timeout waiting for image"
Some images take longer to generate. The script waits up to 5 minutes per image. You can increase `maxAttempts` in the `checkTaskAndDownload` function.

### Generation Quality Issues

If images don't match your vision:

1. **Update prompts** in `FREEPIK_PROMPTS.md`
2. **Delete the generated image** from `public/punk-worlds/`
3. **Remove from status**: Edit `.generation-status.json` and remove the punk name from the `completed` array
4. **Re-run the script**: It will regenerate only the missing images

## Cost Estimation

- **Free tier**: $5 USD = ~25-50 images (depending on model)
- **Flux Pro 1.1**: ~$0.10 - $0.20 per image
- **Total cost for 194 images**: ~$19-38 USD

You can start with a few punks to test quality before generating all 194.

## Testing First

To test with just a few punks before generating all 194:

1. Create a test file `FREEPIK_PROMPTS_TEST.md` with 5-10 prompts
2. Modify the script to use `FREEPIK_PROMPTS_TEST.md`
3. Generate and review
4. Adjust prompts as needed
5. Switch back to full `FREEPIK_PROMPTS.md`

## Example Output

```
🎨 Bespoke Punks World Generator

Reading prompts from FREEPIK_PROMPTS.md...
✓ Found 194 punk prompts

📊 Status: 0 completed, 194 remaining

Starting generation...

[1/194] 🎭 lad_001_carbon
   📝 Claymation
   🚀 Submitting to API...
   ⏳ Task abc-123-def - waiting for completion...
   ✅ Saved to public/punk-worlds/lad_001_carbon.jpg

[2/194] 🎭 lad_002_cash
   📝 Pixel art environment
   🚀 Submitting to API...
   ⏳ Task xyz-456-ghi - waiting for completion...
   ✅ Saved to public/punk-worlds/lad_002_cash.jpg

...

✨ Generation complete!
   ✅ Success: 194
   ❌ Failed: 0
```

## Advanced: Batch Processing

If you want to generate in smaller batches (e.g., 20 at a time):

```bash
# Modify the script or use this approach:
# Generate only lads
node scripts/generate-punk-worlds.js --filter=lad

# Generate only ladies
node scripts/generate-punk-worlds.js --filter=lady

# Generate specific range
node scripts/generate-punk-worlds.js --start=0 --end=20
```

(Note: You'll need to add these CLI argument handlers to the script)
