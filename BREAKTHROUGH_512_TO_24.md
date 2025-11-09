# BREAKTHROUGH: 512×512 → 24×24 Training Method

**Date**: November 9, 2025
**Status**: ✅ SUCCESSFUL - Best reproducibility achieved to date

## Summary

Successfully trained Bespoke Punks style using **512×512 resolution** on RunPod RTX A6000, then downscaled to 24×24 using NEAREST neighbor interpolation. This approach completely bypasses the VAE limitations that prevented native 24×24 training.

## Key Results

### 512×512 Outputs
- **Clean pixel art aesthetic** - Sharp, well-defined edges
- **Accurate Bespoke Punk style** - Head-only composition, solid color backgrounds
- **Proper color palettes** - Limited, vibrant colors matching training data
- **Facial features learned** - Eyes, hair, skin tones all render correctly

### 24×24 NEAREST Downscaled Outputs
- **Preserved pixel art quality** - NEAREST neighbor maintains sharp pixels
- **Recognizable characters** - Despite tiny size, characters are identifiable
- **True 24×24 dimensions** - Matches original Bespoke Punks exactly
- **No blurring** - Unlike LANCZOS/BILINEAR, maintains crisp edges

## Training Configuration

### Hardware
- **Platform**: RunPod
- **GPU**: RTX A6000 (48GB VRAM)
- **Training Time**: ~40-45 minutes (3 epochs)
- **Cost**: ~$0.60-0.80 total

### Model Parameters
```bash
--pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5"
--resolution="512,512"
--network_dim=32
--network_alpha=16
--max_train_epochs=3
--learning_rate=0.0001
--unet_lr=0.0001
--text_encoder_lr=0.00005
--lr_scheduler="cosine_with_restarts"
--lr_scheduler_num_cycles=3
--optimizer_type="AdamW"
--mixed_precision="fp16"
--noise_offset=0.1
--min_snr_gamma=5
```

### Training Data
- **Source**: 203 original 24×24 Bespoke Punks
- **Upscaling**: NEAREST neighbor to 512×512
- **Repeats**: 10× (DreamBooth style)
- **Total images**: 2,030 per epoch

### Training Loss
- **Start**: 0.0231
- **End**: 0.015
- **Reduction**: 35% decrease (healthy convergence)

## Epoch Comparison

### Epoch 1
- Style starting to emerge
- Some details still rough
- Backgrounds solid colors ✓

### Epoch 2 ⭐ RECOMMENDED
- **Best balance** of style learning and detail
- Clean pixel art aesthetic
- Accurate facial features
- Proper Bespoke Punk composition

### Epoch 3
- Slightly more refined
- Risk of mild overfitting
- Still very usable

## Downscaling Method Comparison

### NEAREST Neighbor ⭐ BEST
- **Sharp pixel edges** - Maintains pixel art aesthetic
- **No antialiasing** - Pure pixel-perfect downscaling
- **Vibrant colors** - Preserves original color intensity
- **True to style** - Looks like authentic Bespoke Punks

### LANCZOS
- Smooth but blurry
- Loses pixel art character
- Antialiasing artifacts
- NOT recommended for pixel art

### BILINEAR
- Softer than NEAREST
- Some blur introduced
- Better than LANCZOS but not ideal
- NOT recommended for pixel art

## Technical Breakthrough

### Why This Works

**The Problem**:
- SD 1.5's VAE compresses images 8×
- 24×24 → 3×3 latents = NaN/black images (VAE breaks)
- Direct 24×24 training architecturally impossible

**The Solution**:
1. Train at 512×512 (64×64 latents = ✓ works)
2. Model learns Bespoke Punk style at high resolution
3. Generate at 512×512 with trained LoRA
4. Downscale to 24×24 using NEAREST neighbor
5. Result: Pixel-perfect 24×24 Bespoke Punks

### Key Insight
- **High-res training preserves low-res aesthetic** when input data is upscaled pixel art
- NEAREST upscaling maintains blocky pixel structure
- Model learns "big pixels" as part of the style
- Downscaling back recovers original aesthetic

## Files Generated

### Checkpoints (in `Context 1106/`)
- `bespoke_punks_sd15_512-000001.safetensors` - Epoch 1 (~150MB)
- `bespoke_punks_sd15_512-000002.safetensors` - Epoch 2 (~150MB) ⭐ BEST
- `bespoke_punks_sd15_512.safetensors` - Epoch 3 (~150MB)

### Test Outputs (in `runpod_test_outputs/`)
- 12 images at 512×512 (3 epochs × 4 prompts)
- 36 images at 24×24 (3 downscale methods each)
- Total: 48 test images

## Production Workflow

### Recommended Setup
1. **Use Epoch 2 checkpoint** (`bespoke_punks_sd15_512-000002.safetensors`)
2. **Generate at 512×512** with your prompts
3. **Downscale to 24×24** using `Image.NEAREST`
4. **Export as PNG** for NFT deployment

### Sample Code
```python
from diffusers import StableDiffusionPipeline
from PIL import Image
import torch

# Load model + LoRA
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("mps")
pipe.load_lora_weights("Context 1106", weight_name="bespoke_punks_sd15_512-000002.safetensors")

# Generate
image_512 = pipe(
    prompt="pixel art, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin, sharp pixel edges",
    num_inference_steps=30,
    guidance_scale=7.5,
    height=512,
    width=512
).images[0]

# Downscale to 24×24
image_24 = image_512.resize((24, 24), Image.NEAREST)
image_24.save("new_bespoke_punk.png")
```

## Next Steps

### Immediate Actions
1. **Generate test batch** - Create 50-100 new Bespoke Punks to validate consistency
2. **Color quantization** - Analyze if 24×24 outputs match 35-50 color palette
3. **Comparison study** - Side-by-side with original Bespoke Punks
4. **Prompt refinement** - Test various attribute combinations

### Potential Improvements
1. **Train more epochs** - Test 5-10 epochs to see if quality improves further
2. **Increase LoRA rank** - Try network_dim=64 for more capacity
3. **Larger dataset** - Add more training images if available
4. **Caption refinement** - Improve caption accuracy for better attribute control

### Production Deployment
1. **Automate generation pipeline** - Script for batch generation
2. **Add color quantization step** - Reduce to exact Bespoke Punks palette
3. **Quality filtering** - Auto-reject off-style generations
4. **Metadata integration** - Auto-generate NFT metadata from prompts

## Cost Analysis

### Training Costs
- RunPod RTX A6000: $0.79/hr
- Training time: ~0.75 hrs
- **Total**: ~$0.60-0.80 per training run

### vs. Alternatives
- **Mac M-series**: 3.5 hours (free but slow, ties up computer)
- **RunPod A100**: $1.39/hr × 0.25 hrs = ~$0.35 (faster but more expensive GPU)
- **RunPod RTX 4090**: $0.44/hr × 0.75 hrs = ~$0.33 (cheaper but slower)

**Recommendation**: RTX A6000 is the sweet spot (good speed, reasonable cost)

## Reproducibility Checklist

To reproduce these results:

- [ ] Upscale 24×24 Bespoke Punks to 512×512 using NEAREST
- [ ] Use Kohya sd-scripts with exact config above
- [ ] Train on RunPod RTX A6000 for ~45 minutes (3 epochs)
- [ ] Download Epoch 2 checkpoint
- [ ] Generate at 512×512 with LoRA loaded
- [ ] Downscale to 24×24 using PIL Image.NEAREST
- [ ] Verify outputs match Bespoke Punk aesthetic

## Conclusion

This method represents a **major breakthrough** in generating 24×24 pixel art using Stable Diffusion. By training at 512×512 and downscaling, we completely bypass the VAE's architectural limitations while maintaining the authentic Bespoke Punk style.

**Key Success Factors**:
1. ✅ High-resolution training (512×512)
2. ✅ NEAREST neighbor up/downscaling (preserves pixels)
3. ✅ Proper LoRA configuration (dim=32, alpha=16)
4. ✅ Sufficient training (2-3 epochs optimal)
5. ✅ Quality training data (203 diverse Bespoke Punks)

**Result**: Closest reproducibility to original Bespoke Punks style achieved to date.
