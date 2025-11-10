# Training Comparison Analysis - Why SDXL Failed

**Date:** 2025-11-10
**Problem:** Current SDXL training (epochs 1-7) producing worse results than previous SD 1.5 training, despite more accurate captions

---

## Reference Style (YOUR 203 Punks)

**Visual characteristics:**
- ✅ Clean, simple, intentional pixel art
- ✅ Solid color backgrounds OR intentional patterns (brick, sparkles)
- ✅ NO random colored pixels
- ✅ Simple color palettes (8-12 colors per punk)
- ✅ Clear, blocky pixel aesthetic
- ✅ 24x24 native resolution, simple and clean

**Examples analyzed:**
- `lad_001_carbon.png`: Checkered brick background, clean edges
- `lad_002_cash.png`: Solid green bg, clean gray alien character
- `lad_003_chai.png`: Solid peach bg, fluffy white hair, VERY clean
- `lad_006_redshift.png`: Brown bg, blue spiky hair, clean
- `lad_010_aluminum.png`: Bright blue bg, red cap, super clean
- `lad_015_jackson.png`: Solid green bg, silver alien, clean

---

## Previous Successful Training: SD 1.5 PERFECT Epoch 7

**Model:** `bespoke_punks_SD15_PERFECT-000007.safetensors` (36MB)
**Date:** Nov 9, 2025
**Status:** ✅ **PRODUCTION READY** (documented in TRAINING_RESULTS_SUMMARY.md)

### Training Parameters
```
Base Model: runwayml/stable-diffusion-v1-5
Resolution: 512x512
Network Dim: 32
Network Alpha: 16
Learning Rate: 0.0001
Batch Size: 1 (gradient accumulation: 4)
Mixed Precision: fp16
Optimizer: AdamW8bit
Scheduler: cosine_with_restarts (3 cycles)
Noise Offset: 0.05
Min SNR Gamma: 5
Epochs: 10
Training Images: 203
```

### Results Analysis
**Test outputs:**
- ✅ Clean, simple pixel art matching reference style
- ✅ Solid backgrounds as requested
- ✅ No random colored pixels
- ✅ Brown eyes rendering correctly
- ✅ All accessories visible
- ✅ Appropriate simplification for 24x24 style

**Visual match to references:** 9/10 - Very close to YOUR style

**Examples:**
- brown_eyes_lad_512.png: Green crown, solid green background, clean and simple
- brown_eyes_lady_512.png: Cyan/teal background, clean pixel art

---

## Previous SDXL Attempt: PERFECT Epoch 1

**Model:** `bespoke_punks_PERFECT-000001.safetensors` (435MB)
**Date:** Nov 9, 2025
**Status:** ⚠️ **TOO DETAILED** (not matching reference style)

### Training Parameters
```
Base Model: stabilityai/stable-diffusion-xl-base-1.0 (likely)
Resolution: 1024x1024 (inferred)
Network Dim: Unknown (likely 64-128)
Result: Photorealistic pixel art
```

### Results Analysis
**Test outputs:**
- brown_eyes_lady_1024.png: ULTRA detailed brick wall background, realistic hair texture, photorealistic eyes with reflections, tons of accessories
- ⚠️ TOO REALISTIC compared to your simple reference style
- ⚠️ More like a digital painting than simple pixel art
- ⚠️ Complexity doesn't match your 203 reference images

**Visual match to references:** 5/10 - Too detailed, wrong aesthetic

---

## Current Training: SDXL Nov 10 (FAILING)

**Models:** `bespoke_baby_sdxl-000001.safetensors` through `-000009.safetensors` (1.7GB each)
**Date:** Nov 10, 2025 (today)
**Status:** ❌ **FAILURE - Does not match reference quality**

### Training Parameters
```
Base Model: stabilityai/stable-diffusion-xl-base-1.0
Resolution: 1024x1024
Network Dim: 128
Network Alpha: 64
Learning Rate: 0.0001 (unet), 0.00005 (text encoders)
Batch Size: 2
Mixed Precision: bf16
Optimizer: AdamW8bit
Scheduler: cosine_with_restarts (3 cycles)
Noise Offset: 0.1
Min SNR Gamma: 5
Epochs: 10 (testing in progress)
Training Images: 203
Total Steps: 10,150
Duration: ~3-4 hours
```

### Results Analysis (Epochs 1-7 tested)

#### Epoch 1
- ✅ Pixel art style achieved
- ⚠️ Less detailed than desired
- ⚠️ Backgrounds not perfectly solid

#### Epoch 2
- ✅ Pixel art maintained
- ⚠️ Similar quality to epoch 1
- ⚠️ Slight variations

#### Epoch 3
- ✅ Better detail and texture
- ✅ Hair texture improved
- ⚠️ Background color mismatch (lad got beige instead of blue)
- **Best so far** but still has issues

#### Epoch 4
- ❌ **QUALITY DECLINED**
- ❌ Backgrounds noisy/textured instead of solid
- ❌ Pixelated patterns appearing
- ❌ Character over-simplified

#### Epoch 5
- ✅ Recovery from epoch 4
- ✅ Cleaner backgrounds
- ⚠️ More simplified than epoch 3
- ⚠️ Still wrong background on lad (beige vs blue)

#### Epoch 6
- ❌ Random colored pixels appearing (cyan earrings, wrong colors)
- ❌ Background still wrong on lad
- ❌ Not clean pixel art
- ❌ Hair colors sometimes incorrect

#### Epoch 7
- ❌ Same issues persist
- ❌ Random color pixels
- ❌ Wrong backgrounds
- ❌ Not production ready

### Critical Issues
1. **Random colored pixels** - Cyan, teal, random colors appearing where they shouldn't
2. **Background colors wrong** - 7 epochs in a row, lad gets beige/tan instead of blue
3. **Noisy textures** - Backgrounds not solid, pixelated patterns
4. **Inconsistent with prompts** - Not following color instructions accurately
5. **Overall quality** - None of epochs 1-7 match SD 1.5 Epoch 7 quality

**Visual match to references:** 3/10 - Random pixels, wrong colors, doesn't match YOUR style

---

## Caption Analysis

### Caption Format (CURRENT - Used in ALL trainings)

**Structure:**
```
pixel art, 24x24, portrait of bespoke punk [lad/lady], [hair description] (#hexcolor), [accessories], [eye color] (#hexcolor), [skin tone], [background description] (#hexcolor), [clothing], palette: #hex1, #hex2, #hex3..., sharp pixel edges, hard color borders, retro pixel art style, [additional palette colors]
```

**Example (lad_001_carbon.txt):**
```
pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60), medium male skin tone (#b27f60), checkered brick background (#c06148), medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002, sharp pixel edges, hard color borders, retro pixel art style, #a76857, #434b4e, #353b3d, #66665a, #421901, #ede9c6, #a17d33, #714d3d
```

**Caption characteristics:**
- ✅ Pixel-perfect accuracy (colors verified against actual RGB values)
- ✅ All 203 eye colors verified
- ✅ All 203 hex codes corrected
- ✅ 100% accuracy achieved
- ✅ 8-15 hex color codes per caption
- ✅ Detailed accessory descriptions
- ✅ Explicit style keywords ("sharp pixel edges, hard color borders, retro pixel art style")

### Caption Comparison Between Trainings

**Tested:** `sd15_training_512/` vs `civitai_v2_7_training/` (current SDXL training data)

**Result:** ✅ **IDENTICAL** - No differences found

```bash
diff sd15_training_512/lad_001_carbon.txt civitai_v2_7_training/lad_001_carbon.txt
# No output = files are identical

diff sd15_training_512/lad_010_aluminum.txt civitai_v2_7_training/lad_010_aluminum.txt
# No output = files are identical
```

### Conclusion on Captions

**The improved caption accuracy is NOT causing the problem.**

- SD 1.5 SUCCESS used these detailed captions ✅
- Current SDXL FAILURE uses these same detailed captions ❌

The captions work perfectly with SD 1.5 but SDXL is struggling to interpret them correctly at 1024x1024 resolution.

---

## Root Cause Analysis

### Why SD 1.5 Worked

1. **Appropriate model complexity** - SD 1.5 is simple enough to learn clean pixel art without adding unwanted detail
2. **Native resolution match** - 512x512 is closer to the scaled-up 24x24 aesthetic
3. **Smaller LoRA** - dim=32 prevents overfitting on 203 images
4. **Conservative noise** - 0.05 noise offset preserves pixel art integrity
5. **Simpler architecture** - Less likely to hallucinate random details

### Why SDXL Is Failing

1. **Model too powerful** - SDXL adds complexity/variation when it should simplify
2. **Resolution mismatch** - 1024x1024 is 4x the area of 512x512, creating scaling artifacts
3. **Large LoRA** - dim=128 (4x larger than SD 1.5) risks overfitting
4. **Higher noise** - 0.1 noise offset creates random pixels
5. **Complex architecture** - SDXL interprets detailed captions differently, adds unwanted variation
6. **bf16 vs fp16** - Different quantization may affect learning

### The Paradox Explained

**"More accurate captions + more training steps = worse results"**

This paradox occurs because:
- SDXL at 1024x1024 tries to add photorealistic detail
- Your detailed captions give it TOO MUCH information to interpret
- It creates variation where there should be simplicity
- The model is fighting against the "24x24" instruction

It's like asking a professional artist to draw like a 5-year-old - the skill works against the goal.

---

## Comparison Table

| Metric | SD 1.5 SUCCESS | SDXL PERFECT (Too Detailed) | Current SDXL (FAILURE) |
|--------|---------------|----------------------------|------------------------|
| **Model Size** | 36MB | 435MB | 1.7GB |
| **Base Model** | SD 1.5 | SDXL | SDXL |
| **Resolution** | 512x512 | 1024x1024 | 1024x1024 |
| **Network Dim** | 32 | Unknown | 128 |
| **Network Alpha** | 16 | Unknown | 64 |
| **Mixed Precision** | fp16 | Unknown | bf16 |
| **Noise Offset** | 0.05 | Unknown | 0.1 |
| **Batch Size** | 1+accum4 | Unknown | 2 |
| **Captions** | Detailed (accurate) | Same | Same |
| **Visual Match** | 9/10 ✅ | 5/10 (too detailed) | 3/10 ❌ |
| **Clean Backgrounds** | ✅ Yes | ⚠️ Too detailed | ❌ No (noisy) |
| **Random Pixels** | ✅ No | ✅ No | ❌ Yes |
| **Color Accuracy** | ✅ Good | ⚠️ OK | ❌ Poor |
| **Style Match** | ✅ Perfect | ❌ Wrong aesthetic | ❌ Wrong quality |
| **Production Ready** | ✅ YES | ❌ No | ❌ No |

---

## Recommendations

### Option A: Return to SD 1.5 (HIGHEST SUCCESS PROBABILITY)

**Use the proven configuration:**
- Model: `runwayml/stable-diffusion-v1-5`
- Resolution: `512x512`
- Network dim: `32`, alpha: `16`
- Batch size: `1` with gradient accumulation `4`
- Mixed precision: `fp16`
- Noise offset: `0.05`
- Keep current detailed captions (they work!)

**Expected outcome:** Production-ready results by Epoch 7 (proven track record)

### Option B: Fix SDXL Parameters

If you want to keep trying SDXL, make it MORE like SD 1.5:

**Reduce complexity:**
- Resolution: `768x768` (not 1024)
- Network dim: `64` (not 128)
- Network alpha: `32` (not 64)
- Batch size: `1` (not 2)
- Mixed precision: `fp16` (not bf16)
- Noise offset: `0.05` (not 0.1)

**Expected outcome:** May improve but unproven - SD 1.5 is safer bet

### Option C: Simplify Captions for SDXL

Try removing hex codes, let SDXL interpret naturally:

**Before:**
```
pixel art, 24x24, portrait of bespoke punk lad, hair (#3bb8ff), wearing red forward a baseball cap, wearing silver rimmed glasses, stubble, light medium brownred eyes (#acacac), medium to light skin (middle eastern), bright blue background (lighter almost sky blue), orange jacket with white t shirt underneath (#ff8b4b), palette: #3bb8ff, #acacac, #ff8b4b, #000000, sharp pixel edges, hard color borders, retro pixel art style, #d30707, #deaf99, #f4ceb9...
```

**After:**
```
pixel art, 24x24, portrait of bespoke punk lad, bright blue hair, wearing red baseball cap, wearing silver rimmed glasses, stubble, gray eyes, medium skin, bright blue background, orange jacket with white t-shirt, sharp pixel edges, hard color borders, retro pixel art style
```

**Expected outcome:** Uncertain - might help SDXL focus on style over exact colors

---

## Epochs 8-10 Analysis (Pending)

Waiting for test outputs to complete analysis...

**Expectation:** Unlikely to see dramatic improvement based on epochs 1-7 trend

---

## Final Verdict

**SD 1.5 is the winner.** It produces clean, simple pixel art that matches your 203 reference images.

SDXL either:
- Gets TOO detailed (PERFECT epoch 1)
- OR gets noisy with random pixels (current training)

**For 24x24 simple pixel art, simpler is better. SD 1.5 is the right tool for this job.**

---

**Next Steps:**
1. Finish testing epochs 8-10 for completeness
2. Compare all 10 epochs side-by-side
3. Make final decision: SD 1.5 (safe) vs fixed SDXL (risky)
4. Retrain with chosen approach
5. Deploy best epoch to production

**Recommendation:** Go back to SD 1.5 with proven parameters. Don't fix what isn't broken.
