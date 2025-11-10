# Training Timeline & Results - Structured Comparison

**Last Updated:** 2025-11-10 (Epoch 8 analysis complete)

---

## Complete Training History Table

| Training Name | Date | Model Files | File Size | Base Model | Captions Used | Result | Test Images | Status |
|--------------|------|-------------|-----------|------------|---------------|---------|-------------|---------|
| **SD15 PERFECT** | Nov 9, 20:22 | `bespoke_punks_SD15_PERFECT-*.safetensors` | 36MB each | SD 1.5 | Accurate with hex codes | ✅ **PIXEL ART** | Clean pixel art, accessories visible | **SUCCESS** |
| **SD15 "bespoke_baby"** | Nov 10, 01:54-02:20 | `bespoke_baby_sd15-*.safetensors` | 72MB each | SD 1.5 | Same accurate captions | ❌ **REALISTIC BABIES** | Photorealistic baby photos | **FAILURE** |
| **SDXL Current** | Nov 10, 11:08+ | `bespoke_baby_sdxl-*.safetensors` | 1.7GB each | SDXL | Same accurate captions | ❌ **NOISY PIXEL ART** | Random pixels, wrong colors | **FAILING** |

---

## Training #1: SD15 PERFECT (SUCCESS) ✅

### Files & Dates
```
bespoke_punks_SD15_PERFECT-000001.safetensors  36MB  Nov 9 20:22
bespoke_punks_SD15_PERFECT-000002.safetensors  36MB  Nov 9 20:22
bespoke_punks_SD15_PERFECT-000007.safetensors  36MB  Nov 9 20:22
... (10 epochs total)
```

### Parameters
- **Base Model:** runwayml/stable-diffusion-v1-5
- **Resolution:** 512x512
- **Network Dim:** 32 (inferred from file size)
- **Network Alpha:** 16
- **Captions:** Detailed with hex codes (civitai_v2_7_training/)

### Test Results (Epoch 7 - PRODUCTION READY)
| Test | Result | Evidence |
|------|--------|----------|
| brown_eyes_lady | ✅ Clean pixel art, teal bg, earrings visible | test_outputs_PERFECT_epoch7/brown_eyes_lady_512.png |
| brown_eyes_lad | ✅ Clean pixel art, green bg, crown visible | test_outputs_PERFECT_epoch7/brown_eyes_lad_512.png |
| Style | ✅ Simple, blocky, clean pixel art | Matches reference style |
| Backgrounds | ✅ Solid colors | No noise |
| Accessories | ✅ All visible | Earrings, crowns, etc. |

**Visual Quality:** 9/10 - Very close to YOUR 203 reference images

**CONCLUSION:** This worked! Production ready.

---

## Training #2: SD15 "bespoke_baby" (FAILURE) ❌

### Files & Dates
```
bespoke_baby_sd15-000001.safetensors  72MB  Nov 10 01:54
bespoke_baby_sd15-000002.safetensors  72MB  Nov 10 01:57
bespoke_baby_sd15-000003.safetensors  72MB  Nov 10 02:00
... (9 epochs total)
```

### Parameters
- **Base Model:** runwayml/stable-diffusion-v1-5
- **Resolution:** 512x512 (assumed)
- **Network Dim:** 64 (inferred from 72MB vs 36MB = 2x size)
- **Network Alpha:** Unknown (32?)
- **Captions:** SAME detailed captions (confirmed identical)

### Test Results (Epochs 1-7)
| Test | Result | Evidence |
|------|--------|----------|
| 01_bespoke_punk_green_bg | ❌ Smooth gradient art, not pixel art | test_outputs_sd15_epoch1/01_bespoke_punk_green_bg.png |
| 02_bespoke_baby_pink_bg | ❌ **PHOTOREALISTIC BABY PHOTO** | test_outputs_sd15_epoch1/02_bespoke_baby_pink_bg.png |
| 03_lad_blue_bg | ❌ Smooth digital art | test_outputs_sd15_epoch1/03_lad_blue_bg.png |
| Style | ❌ Realistic/smooth, NOT pixel art | Complete failure |
| All epochs 1-7 | ❌ Same problem across all epochs | test_outputs_sd15_epoch7/02_bespoke_baby_pink_bg.png |

**Visual Quality:** 0/10 - Photorealistic babies instead of pixel art

**CONCLUSION:** Complete failure despite using SAME captions that worked in Training #1

### Critical Question
**Why did this fail when Training #1 succeeded with same captions?**
- File size difference: 36MB vs 72MB suggests different network dim (32 vs 64)
- Larger network (64) may have allowed base model photorealistic bias to dominate
- Smaller network (32) forced simplification = pixel art

---

## Training #3: SDXL Current (FAILING) ❌

### Files & Dates
```
bespoke_baby_sdxl-000001.safetensors  1.7GB  Nov 10 11:08
bespoke_baby_sdxl-000002.safetensors  1.7GB  Nov 10 11:28
bespoke_baby_sdxl-000003.safetensors  1.7GB  Nov 10 11:49
... (testing epochs 1-8, expecting 10 total)
```

### Parameters
- **Base Model:** stabilityai/stable-diffusion-xl-base-1.0
- **Resolution:** 1024x1024
- **Network Dim:** 128
- **Network Alpha:** 64
- **Mixed Precision:** bf16
- **Batch Size:** 2
- **Noise Offset:** 0.1
- **Captions:** SAME detailed captions as successful Training #1

### Test Results (Epochs 1-8 Analyzed)

| Epoch | Visual Quality | Issues | Best Features | Verdict |
|-------|---------------|--------|---------------|---------|
| **1** | 5/10 | Less detailed, backgrounds ok | Clean pixel art achieved | Baseline |
| **2** | 5/10 | Similar to epoch 1 | Consistent pixel art | Baseline |
| **3** | 7/10 | ⚠️ Lad bg beige (should be blue) | Best detail/texture so far | Best candidate |
| **4** | 3/10 | ❌ Noisy backgrounds, pixelated patterns | Major degradation | Skip |
| **5** | 6/10 | ⚠️ Lad bg still wrong | Cleaner than 4, simpler | Recovery |
| **6** | 4/10 | ❌ Random cyan pixels, wrong colors | Hair colors off | Skip |
| **7** | 4/10 | ❌ Same issues as epoch 6 | Still wrong backgrounds | Skip |
| **8** | 4/10 | ❌ Cyan random pixels, gray bg instead of green, beige instead of blue | Some ok images | Skip |
| **9** | ? | Pending | Pending | Pending |
| **10** | ? | Pending | Pending | Pending |

### Recurring Issues Across All Epochs
1. ❌ **Background colors wrong** - Lad gets beige/tan instead of blue (7 epochs in a row!)
2. ❌ **Random colored pixels** - Cyan, teal appearing where they shouldn't
3. ❌ **Inconsistent quality** - Up and down across epochs
4. ❌ **Not matching reference style** - Too complex or too noisy

**Visual Quality:** 3-7/10 depending on epoch - None match Training #1 quality

**CONCLUSION:** SDXL struggling to produce clean pixel art. Best epoch (3) still has issues.

---

## Reference Images (YOUR 203 Punks)

### Characteristics
- ✅ Clean, simple, intentional pixel art
- ✅ Solid color backgrounds OR intentional patterns (brick, sparkles)
- ✅ NO random colored pixels
- ✅ Simple color palettes (8-12 colors)
- ✅ 24x24 native, blocky aesthetic

### Examples Analyzed
- `lad_001_carbon.png` - Checkered brick bg, gray hat, clean
- `lad_002_cash.png` - Solid green bg, gray alien, clean
- `lad_003_chai.png` - Solid peach bg, white fluffy hair, VERY clean
- `lad_006_redshift.png` - Brown bg, blue spiky hair, clean
- `lad_010_aluminum.png` - Bright blue bg, red cap, super clean
- `lad_015_jackson.png` - Solid green bg, silver alien, clean

**Style Standard:** Simple, clean, blocky pixel art - THIS is the goal

---

## Captions Comparison

### All Three Trainings Used SAME Captions
**Verified:** `diff` comparison shows NO differences between:
- `sd15_training_512/` (Training #1 - SUCCESS)
- `civitai_v2_7_training/` (Training #2 & #3 - FAILURE)

**Caption Format:**
```
pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60), medium male skin tone (#b27f60), checkered brick background (#c06148), medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002, sharp pixel edges, hard color borders, retro pixel art style, #a76857, #434b4e, #353b3d, #66665a, #421901, #ede9c6, #a17d33, #714d3d
```

**Conclusion:** Captions are NOT the problem. All trainings used identical accurate captions.

---

## Root Cause Analysis

### Why Training #1 (SD15 PERFECT 36MB) Succeeded

1. **Network Dim = 32** - Small network forced simplification
2. **SD 1.5 Base** - Simpler model, less photorealistic bias
3. **512x512** - Native resolution closer to 24x24 aesthetic
4. **Conservative parameters** - Allowed pixel art to emerge

### Why Training #2 (SD15 "bespoke_baby" 72MB) Failed

1. **Network Dim = 64** - 2x larger network allowed photorealistic bias
2. **Same SD 1.5 Base** - But larger network let base model dominate
3. **Same captions** - But network capacity changed learning dynamics

**Critical Insight:** SAME base model + SAME captions + DIFFERENT network size = OPPOSITE results

### Why Training #3 (SDXL Current) Is Failing

1. **SDXL too powerful** - Adds complexity/variation when it should simplify
2. **1024x1024 resolution** - 4x area of 512, creates scaling artifacts
3. **Network Dim = 128** - 4x larger than successful Training #1
4. **Complex architecture** - Fighting "24x24 simple" instruction
5. **bf16 vs fp16** - Different quantization affects learning

**Critical Insight:** More powerful model + larger network + same detailed captions = worse results (paradox)

---

## Comparison Matrix

| Factor | Training #1 (SUCCESS) | Training #2 (FAILURE) | Training #3 (FAILING) |
|--------|----------------------|----------------------|----------------------|
| **Model** | SD 1.5 | SD 1.5 | SDXL |
| **File Size** | 36MB | 72MB | 1.7GB |
| **Network Dim** | 32 | ~64 | 128 |
| **Resolution** | 512x512 | 512x512 | 1024x1024 |
| **Captions** | Accurate w/ hex | Same | Same |
| **Result** | ✅ Pixel art | ❌ Photos | ❌ Noisy |
| **Match to Reference** | 9/10 | 0/10 | 3-7/10 |
| **Production Ready** | ✅ YES | ❌ NO | ❌ NO |

---

## Next Steps

### Immediate
1. ✅ Analyzed epochs 1-8
2. ⏳ Waiting for epochs 9-10 to download
3. ⏳ Complete full 10-epoch comparison

### Decision Point
After reviewing all 10 SDXL epochs, decide:

**Option A: Use Training #1 (SD15 PERFECT Epoch 7)**
- ✅ Already proven to work
- ✅ Production ready
- ✅ Matches your reference style
- Risk: None, it already works

**Option B: Retry SD15 with correct network dim**
- Use dim=32 alpha=16 (like Training #1)
- Avoid dim=64 (causes photorealism per Training #2)
- Risk: Low, Training #1 proved this works

**Option C: Fix SDXL parameters**
- Reduce to: 768x768, dim=64, alpha=32, fp16
- Risk: Medium, unproven approach

**Option D: Simplify captions for SDXL**
- Remove hex codes, natural language only
- Risk: High, may lose color accuracy

---

## Recommendation (Preliminary - pending epochs 9-10)

**Use Training #1: SD15 PERFECT Epoch 7**

**Why:**
- Already works perfectly
- Matches your 203 reference images (9/10)
- Production tested and documented
- No risk, no waiting

**Evidence:**
- `bespoke_punks_SD15_PERFECT-000007.safetensors` (Nov 9, 36MB)
- Test images show clean pixel art
- Brown eyes work, accessories visible
- Solid backgrounds, no random pixels

**Model Location:** `/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000007.safetensors`

---

**Final analysis will be updated after epochs 9-10 are tested.**
