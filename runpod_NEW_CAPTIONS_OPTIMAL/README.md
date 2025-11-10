# RunPod Training Package: NEW Captions + Optimal Parameters

**Created:** 2025-11-10
**Purpose:** Test if NEW accurate captions work with proven successful architecture

---

## What This Package Does

**Tests:** Do NEW accurate captions produce good results with optimal parameters?

**Configuration:**
- ✅ NEW accurate captions (Nov 10, 12:53 AM version)
- ✅ ALL optimal parameters from SD15_PERFECT (9/10 success)
- ✅ network_dim=32 (proven successful)
- ✅ 203 training images with detailed captions

**Expected Outcome:**
- If SUCCESS: We have production model with accurate captions! ✅
- If FAILURE: Caption detail is the problem → Try Option 3 (simplified captions)

---

## Package Contents

```
runpod_NEW_CAPTIONS_OPTIMAL/
├── train_sd15_new_captions_optimal.sh  ← Main training script
├── training_data/                      ← 203 images + NEW accurate captions
│   ├── lad_001_carbon.png
│   ├── lad_001_carbon.txt             ← NEW: 12+ hex codes, detailed
│   └── ... (203 total)
├── README.md                           ← This file
└── SETUP_INSTRUCTIONS.md               ← RunPod setup guide
```

---

## Caption Version

**NEW Accurate Captions (Nov 10, 12:53 AM)**

**Example (`lad_001_carbon.txt`):**
```
pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat
with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60),
medium male skin tone (#b27f60), checkered brick background (#c06148),
medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002,
sharp pixel edges, hard color borders, retro pixel art style, #a76857, #434b4e,
#353b3d, #66665a, #421901, #ede9c6, #a17d33, #714d3d
```

**Characteristics:**
- Specific accurate descriptions
- 12+ hex codes with complete color palette
- Eye colors specified
- Skin tone hex codes
- Accurate accessory details
- Accurate background descriptions
- ~320 characters average

---

## Training Parameters (OPTIMAL)

All parameters from SD15_PERFECT (9/10 success):

### Network Architecture
- network_dim: **32** ← PROVEN SUCCESSFUL
- network_alpha: 16
- resolution: 512x512

### Training Settings
- batch_size: 4
- epochs: 10
- learning_rate: 0.0001
- text_encoder_lr: 0.00005
- lr_scheduler: cosine_with_restarts (3 cycles)

### Caption Handling (CRITICAL)
- shuffle_caption: **TRUE** ← Randomizes caption word order
- keep_tokens: **2** ← Keeps "pixel art, 24x24" at start
- max_token_length: 225

### Noise/Regularization (CRITICAL)
- noise_offset: 0.1
- multires_noise_iterations: **6** ← Advanced noise injection
- multires_noise_discount: **0.3**
- adaptive_noise_scale: **0.00357**
- min_snr_gamma: 5

### Other
- mixed_precision: fp16
- optimizer: AdamW8bit
- gradient_accumulation_steps: 1

---

## Quick Start (RunPod)

### 1. Upload Package
```bash
# On your local machine
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2
zip -r runpod_NEW_CAPTIONS_OPTIMAL.zip runpod_NEW_CAPTIONS_OPTIMAL/

# Upload zip to RunPod via web interface or:
# Use RunPod file browser to upload
```

### 2. Extract on RunPod
```bash
cd /workspace
unzip runpod_NEW_CAPTIONS_OPTIMAL.zip
cd runpod_NEW_CAPTIONS_OPTIMAL
```

### 3. Copy Training Data
```bash
mkdir -p /workspace/training_data/10_bespoke_baby
cp training_data/*.png /workspace/training_data/10_bespoke_baby/
cp training_data/*.txt /workspace/training_data/10_bespoke_baby/

# Verify
ls /workspace/training_data/10_bespoke_baby/*.png | wc -l  # Should show 203
ls /workspace/training_data/10_bespoke_baby/*.txt | wc -l  # Should show 203
```

### 4. Install Kohya SS
```bash
cd /workspace
git clone https://github.com/kohya-ss/sd-scripts.git kohya_ss
cd kohya_ss
pip install -r requirements.txt
```

### 5. Run Training
```bash
cd /workspace/runpod_NEW_CAPTIONS_OPTIMAL
chmod +x train_sd15_new_captions_optimal.sh
bash train_sd15_new_captions_optimal.sh
```

### 6. Monitor
Training will take approximately 2-4 hours depending on GPU.

Watch for:
- Epoch checkpoints saved every epoch
- Loss values decreasing
- Completion message

---

## After Training

### 1. Download Checkpoints
```bash
cd /workspace/output
ls -lh *.safetensors

# Download all epochs:
# bespoke_punks_SD15_NEW_CAPTIONS_OPTIMAL-000001.safetensors
# bespoke_punks_SD15_NEW_CAPTIONS_OPTIMAL-000002.safetensors
# ... (epochs 1-9)
# bespoke_punks_SD15_NEW_CAPTIONS_OPTIMAL.safetensors (final)
```

### 2. Test Each Epoch
Use test script (similar to previous tests) to generate sample images for each epoch.

### 3. Compare to SD15_PERFECT
- SD15_PERFECT: 9/10 quality with OLD captions
- This training: ?/10 quality with NEW captions

### 4. Analysis
**If Results are BETTER or EQUAL (8-10/10):**
- ✅ SUCCESS! NEW accurate captions work!
- ✅ Use this model for production
- ✅ Update Supabase with results

**If Results are WORSE (0-7/10):**
- ⚠️ Caption detail may be the problem
- ⚠️ Try Option 3: Simplified captions
- ⚠️ Update Supabase with findings

---

## Option 3: Simplified Captions (If This Fails)

**If this training doesn't produce good results**, try simplified captions that:
- Keep basic structure ("pixel art, 24x24, portrait of...")
- Include main colors (3-5 hex codes, not 12+)
- Simplify descriptions (no excessive detail)
- Focus on primary visual elements

**Example Simplified Caption:**
```
pixel art, 24x24, portrait of bespoke punk lad, brown hair, gray hat,
brown eyes, light skin, brown checkered background, gray shirt,
sharp pixel edges, retro pixel art style
```

Package will be created if needed.

---

## Tracking & Documentation

### Supabase Entry
This training will be added to Supabase as:
- run_name: SD15_NEW_CAPTIONS_OPTIMAL_Nov10
- caption_version: NEW_accurate_captions_Nov10
- network_dim: 32
- All parameters documented

### Expected Database Update
After training completes and testing is done:
```sql
INSERT INTO training_runs (
    run_name, run_date, status,
    base_model, model_type,
    network_dim, network_alpha,
    caption_version,
    overall_verdict, quality_score,
    production_ready,
    notes
) VALUES (
    'SD15_NEW_CAPTIONS_OPTIMAL_Nov10',
    '2025-11-10 [TIME]',
    'completed',
    'runwayml/stable-diffusion-v1-5',
    'SD15',
    32, 16,
    'NEW_accurate_captions_Nov10',
    '[success/failure]',
    [0-10],
    [true/false],
    'Testing if NEW accurate captions work with proven optimal parameters.'
);
```

---

## Success Criteria

**GOAL:** Match or exceed SD15_PERFECT (9/10 quality)

**Success Indicators:**
- ✅ Clean pixel art style
- ✅ Correct colors matching captions
- ✅ No random pixels or artifacts
- ✅ No photorealistic rendering
- ✅ Sharp pixel edges
- ✅ Proper backgrounds

**Failure Indicators:**
- ❌ Photorealistic babies/faces
- ❌ Wrong colors or backgrounds
- ❌ Random colored pixels
- ❌ Blurry or soft edges
- ❌ Over-complicated rendering

---

## Questions?

Refer to:
- `FINAL_COMPLETE_ANALYSIS_AND_RECOMMENDATIONS.md` - Full analysis
- `TRAINING_PARAMETERS_COMPARISON.md` - Parameter comparison
- `COMPLETE_TRAINING_VERIFICATION.md` - All training verification

---

**Ready to train! Upload to RunPod and follow Quick Start instructions.**
