# Training Strategy: 512×512 → 24×24 Downscaling

## Current Approach (Option 1): Train-High, Generate-Low

**Status**: 🔄 IN PROGRESS

### The Problem with 24×24 Native Training:
- SD 1.5's VAE compresses images 8×:
  - 512×512 → 64×64 latents ✓ Works
  - 24×24 → 3×3 latents ✗ **Breaks VAE** (produces NaN → black images)
- SDXL had same issue (IndexError at 24×24)
- Conclusion: Standard diffusion models architecturally incompatible with tiny resolutions

### Solution: Train at 512×512, Generate & Downscale to 24×24

**Training Configuration**:
- Resolution: 512×512
- Base Model: SD 1.5 (runwayml/stable-diffusion-v1-5)
- Data: 204 Bespoke Punks upscaled from 24×24 to 576×576 (NEAREST neighbor)
- LoRA: Dim 32, Alpha 16
- Epochs: 3 with sample generation each epoch
- Output: `kohya_output_512/`

**Workflow**:
1. Train LoRA on 512×512 upscaled Bespoke Punks
2. Generate images at 512×512 using trained LoRA
3. Downscale to 24×24 using NEAREST neighbor (preserves pixels)

**Expected Results**:
- Model learns Bespoke Punk style at high resolution
- Downscaling to 24×24 should preserve key features
- May need to experiment with downscaling methods (NEAREST vs LANCZOS vs others)

---

## Backup Options (If Option 1 Fails):

### Option 2: Train at 64×64 or 128×128
**Resolution**:
- 64×64 → 8×8 latents (borderline but might work)
- 128×128 → 16×16 latents (safer choice)

**Pros**:
- Closer to target 24×24 size
- Faster training than 512×512
- Less aggressive downscaling needed

**Cons**:
- 64×64 might still be too small for VAE
- 128×128 still requires 5× downscaling

**When to use**: If 512×512 results lose too much detail when downscaled to 24×24

### Option 3: Different Architecture Entirely
**Alternatives**:
- GANs (StyleGAN, ProGAN) - better for tiny images
- Custom tiny diffusion model trained from scratch
- PixelCNN / VQ-VAE approaches
- Traditional pixel art generation tools

**Pros**:
- Purpose-built for small images
- Can train natively at 24×24

**Cons**:
- Completely different training pipeline
- More complex setup
- Less control over style

**When to use**: If both Option 1 and Option 2 fail to produce acceptable 24×24 results

---

## Testing Procedure:

After training completes:
1. Generate test images at 512×512 with various prompts
2. Downscale to 24×24 using multiple methods:
   - PIL Image.NEAREST
   - PIL Image.LANCZOS
   - PIL Image.BILINEAR
   - Custom pixel art downscaling algorithms
3. Compare to original 24×24 Bespoke Punks:
   - Visual similarity
   - Color accuracy (should be 35-50 colors)
   - Edge sharpness
   - Head-only composition (no bodies)
4. Choose best downscaling method for final workflow

---

## Current Training Progress:

**Started**: Nov 9, 2025 03:30 AM
**Model**: SD 1.5 LoRA
**Resolution**: 512×512
**Expected Duration**: ~30-60 minutes for 3 epochs
**Monitoring**: Sample images generated after each epoch

Check progress:
```bash
ls -lh /Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_output_512/
```

View samples (generated during training):
```bash
open /Users/ilyssaevans/Documents/GitHub/bespokebaby2/kohya_output_512/sample-*.png
```
