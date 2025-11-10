# Bespoke Punk ML Training Pipeline - Process Documentation

**Version:** 1.0
**Date:** November 10, 2025
**Purpose:** Systematic LoRA training, validation, and continuous improvement

---

## 🎯 Pipeline Overview

This is a **professional machine learning pipeline** for training, validating, and deploying LoRA models for 24x24 pixel art generation.

### Core Components

1. **Training Execution** (RunPod)
2. **Validation & Testing** (Local Mac)
3. **Results Tracking** (Supabase)
4. **Version Control** (GitHub)
5. **Production Deployment** (app_gradio.py)

---

## 📋 Standard Operating Procedure

### Phase 1: Training Setup

**Before Training:**

1. **Prepare Caption Dataset**
   - Location: `runpod_package/training_data/`
   - Format: 203 PNG + TXT pairs
   - Validation: All captions have 12+ hex codes, lips, expressions
   - Log to Supabase: `caption_versions` table

2. **Create Training Run Entry**
   ```bash
   # Update supabase_add_current_training_run.sql with parameters
   # Execute SQL to create training_runs entry
   psql -h aws-1-us-east-2.pooler.supabase.com ... -f supabase_add_current_training_run.sql
   ```

3. **Upload to RunPod**
   - Package: `runpod_package/` (zip if needed)
   - Training data: 203 images + captions
   - Config: `training_config.toml`

4. **Check Disk Space**
   ```bash
   df -h /workspace
   # Must have 500MB+ free for 10 epochs
   ```

5. **Start Training**
   ```bash
   cd /workspace/runpod_package
   bash start_training.sh
   ```

---

### Phase 2: Epoch Validation (Repeat for Each Epoch)

**After Each Epoch Completes:**

#### Step 1: Download Checkpoint
```bash
# From RunPod: /workspace/output/bespoke_baby_sd15_lora-000001.safetensors
# To Local: /Users/ilyssaevans/Downloads/
```

#### Step 2: Generate Test Images
```bash
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2

# Auto-generates images in quick_tests/epoch_N/
python quick_test_epoch.py "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000001.safetensors"
```

**Output:**
- `quick_tests/epoch_N/bespoke_baby_sd15_lora-000001_test_512.png`
- `quick_tests/epoch_N/bespoke_baby_sd15_lora-000001_test_24.png`

#### Step 3: Visual Evaluation

**Evaluate on 0-10 scale:**

| Metric | Criteria |
|--------|----------|
| **Visual Quality** | Clean pixels, accurate colors, no artifacts |
| **Style Match** | Pure pixel art, sharp edges, correct aesthetic |
| **Prompt Adherence** | Correct hair color, background, accessories |

**Scoring Guide:**
- 9-10: Perfect, production ready
- 7-8: Good, minor issues
- 5-6: Acceptable, needs improvement
- 0-4: Poor, major issues

#### Step 4: Log to Supabase
```bash
python log_epoch_to_supabase.py <epoch> <visual> <style> <prompt> "Observations"

# Example:
python log_epoch_to_supabase.py 3 7 7 7 "Two-toned hair, garbled crown, pink background"
```

**This automatically:**
- Calculates average score
- Determines verdict (best/good/acceptable/skip)
- Identifies issues (wrong backgrounds, color problems)
- Records strengths (pixel art style, not photorealistic)
- Links test images

#### Step 5: Commit to Version Control
```bash
git add quick_tests/epoch_N/
git commit -m "Add Epoch N test results - <verdict> (<score>/10)

- <Key observation 1>
- <Key observation 2>
- Score: Visual=X, Style=Y, Prompt=Z

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

---

### Phase 3: Convergence Analysis

**After Every 2-3 Epochs:**

#### Check Progress Trend
```sql
SELECT
    epoch_number,
    visual_quality_score,
    style_match_score,
    prompt_adherence_score,
    (visual_quality_score + style_match_score + prompt_adherence_score) / 3.0 as avg_score,
    verdict,
    observations
FROM epoch_results
WHERE training_run_id = (SELECT id FROM training_runs WHERE run_name = 'SD15_FINAL_CORRECTED_CAPTIONS')
ORDER BY epoch_number;
```

#### Identify Convergence Patterns

**Improving (Good):**
```
Epoch 1: 6/10 → Epoch 2: 7/10 → Epoch 3: 7/10
```
- ✅ Scores increasing or stable at good level
- ✅ Issues decreasing
- ✅ Continue training

**Plateauing (Check):**
```
Epoch 5: 7/10 → Epoch 6: 7/10 → Epoch 7: 7/10
```
- ⚠️ No improvement for 3 epochs
- Decision: Test current epoch, may be best available

**Degrading (Stop):**
```
Epoch 7: 9/10 → Epoch 8: 8/10 → Epoch 9: 6/10
```
- ❌ Scores declining
- Action: Use Epoch 7, stop training

---

### Phase 4: Best Epoch Selection

**When Training Completes (or Earlier if Plateau/Degrading):**

#### Step 1: Full Comparison Test
```bash
# Update test_SD15_FINAL_CORRECTED_vs_PERFECT.py with all epoch paths
python test_SD15_FINAL_CORRECTED_vs_PERFECT.py
```

Generates side-by-side comparison:
- Baseline (SD15_PERFECT Epoch 7 - 9/10)
- All new epochs (1-10)
- 6 test prompts each
- 512px + 24px versions

#### Step 2: Identify Best Epoch
```sql
SELECT
    epoch_number,
    (visual_quality_score + style_match_score + prompt_adherence_score) / 3.0 as avg_score,
    verdict,
    production_ready
FROM epoch_results
WHERE training_run_id = (SELECT id FROM training_runs WHERE run_name = 'SD15_FINAL_CORRECTED_CAPTIONS')
ORDER BY avg_score DESC
LIMIT 5;
```

#### Step 3: Mark Production Ready
```sql
-- Update best epoch as production ready
UPDATE epoch_results
SET production_ready = true,
    verdict = 'best',
    notes = 'Selected as production model for deployment'
WHERE training_run_id = (SELECT id FROM training_runs WHERE run_name = 'SD15_FINAL_CORRECTED_CAPTIONS')
  AND epoch_number = 7;  -- Replace with actual best epoch

-- Update training run status
UPDATE training_runs
SET status = 'completed',
    overall_verdict = 'success',  -- or 'failure' or 'partial'
    quality_score = 9,  -- Best epoch score
    best_epoch = 7,
    production_ready = true
WHERE run_name = 'SD15_FINAL_CORRECTED_CAPTIONS';
```

---

### Phase 5: Production Deployment

#### Step 1: Update Generator App
```python
# Edit app_gradio.py
LORA_PATH = "/Users/ilyssaevans/Downloads/bespoke_punks_SD15_FINAL_CORRECTED-000007.safetensors"
```

#### Step 2: Test Generator
```bash
python app_gradio.py
# Visit http://127.0.0.1:7861
# Upload test image
# Verify quality
```

#### Step 3: Document Production Model
```bash
# Create production model documentation
echo "Production Model: SD15_FINAL_CORRECTED_CAPTIONS Epoch 7
Score: 9/10
Date: $(date)
Parameters: dim=32, alpha=16, 512x512
Caption Format: final_corrected_v1 (12+ hex codes, lips, expressions)
Issues: None
Status: Production Ready
" > PRODUCTION_MODEL.txt

git add PRODUCTION_MODEL.txt app_gradio.py
git commit -m "Deploy Epoch 7 as production model (9/10)"
git push
```

---

## 📊 Data Architecture & Tracking

### Supabase Schema

**training_runs**
- Master record of each training experiment
- Parameters, architecture, caption version
- Overall verdict and quality score

**epoch_results**
- Per-epoch performance metrics
- Scores: visual_quality, style_match, prompt_adherence
- Issues, strengths, observations
- Links to test images and checkpoints

**caption_versions**
- Dataset version tracking
- Format description, detail level
- Used in which training runs

### Local File Structure
```
bespokebaby2/
├── quick_tests/              # Epoch validation images
│   ├── epoch_1/
│   ├── epoch_2/
│   └── ...
├── runpod_package/           # Training data & config
│   ├── training_data/        # 203 PNG + TXT
│   ├── training_config.toml
│   └── start_training.sh
├── quick_test_epoch.py       # Single epoch tester
├── log_epoch_to_supabase.py  # Supabase logging
└── test_SD15_FINAL_CORRECTED_vs_PERFECT.py  # Full comparison
```

---

## 🔄 Continuous Improvement Workflow

### After Each Training Run

1. **Analyze Results**
   ```sql
   -- Compare to previous runs
   SELECT
       run_name,
       network_dim,
       caption_version,
       quality_score,
       overall_verdict,
       best_epoch
   FROM training_runs
   ORDER BY run_date DESC
   LIMIT 5;
   ```

2. **Identify Learnings**
   - What worked? (Architecture, captions, parameters)
   - What failed? (Photorealistic, wrong colors, etc.)
   - What to try next?

3. **Document Insights**
   ```bash
   # Update TRAINING_COMPARISON_ANALYSIS.md
   # Add new findings to knowledge base
   ```

4. **Plan Next Experiment**
   - Hypothesis: "If we X, then Y will improve"
   - Test one variable at a time
   - Document in training_runs.notes

---

## 🎯 Success Metrics

### Model Quality Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 9-10 | Excellent | Deploy to production |
| 7-8 | Good | Consider for production |
| 5-6 | Acceptable | Keep training or adjust |
| 0-4 | Poor | Stop, analyze failure |

### Production Readiness Criteria

**Must Have:**
- ✅ Pixel art style (not photorealistic)
- ✅ Accurate color rendering
- ✅ Solid backgrounds (no noise)
- ✅ Clean accessory rendering
- ✅ Score ≥ 8/10

**Nice to Have:**
- Better than current production (9/10 from SD15_PERFECT)
- Consistent across different prompts
- No random artifacts

---

## 🚀 Quick Reference Commands

```bash
# === TRAINING ===
# RunPod cleanup
rm -rf /workspace/.cache/huggingface/hub/* && pip cache purge && df -h

# Start training
cd /workspace/runpod_package && bash start_training.sh

# === VALIDATION ===
# Test epoch
python quick_test_epoch.py "/Users/ilyssaevans/Downloads/bespoke_baby_sd15_lora-000003.safetensors"

# Log to Supabase
python log_epoch_to_supabase.py 3 7 7 7 "Observations here"

# Commit results
git add quick_tests/epoch_3/ && git commit -m "Epoch 3 results" && git push

# === ANALYSIS ===
# View progress
psql ... -c "SELECT epoch_number, visual_quality_score, style_match_score, prompt_adherence_score FROM epoch_results WHERE training_run_id = ... ORDER BY epoch_number"

# Full comparison
python test_SD15_FINAL_CORRECTED_vs_PERFECT.py

# === DEPLOYMENT ===
# Update production
# Edit app_gradio.py LORA_PATH
python app_gradio.py
```

---

## 📝 Process Checklist

**Before Training:**
- [ ] Captions verified (12+ hex codes, lips, expressions)
- [ ] Training run logged in Supabase
- [ ] RunPod disk space checked (500MB+ free)
- [ ] Training config reviewed

**During Training (Per Epoch):**
- [ ] Checkpoint downloaded
- [ ] Test images generated
- [ ] Visual evaluation completed (scores 0-10)
- [ ] Results logged to Supabase
- [ ] Committed to version control

**After Training:**
- [ ] All epochs evaluated
- [ ] Best epoch identified
- [ ] Full comparison test run
- [ ] Production readiness assessed
- [ ] Training run marked complete in Supabase
- [ ] Learnings documented

**If Production Ready:**
- [ ] Generator app updated
- [ ] Production model documented
- [ ] Deployed and tested
- [ ] Old model archived

---

## 🔮 Future Improvements

See `TODO_PIPELINE_IMPROVEMENTS.md` for:
- Automated validation metrics
- A/B testing framework
- Progressive validation (early stopping)
- Multi-prompt test suites
- Quantitative color accuracy metrics
- Automated convergence detection
- Training progress dashboard

---

**Last Updated:** November 10, 2025
**Maintained By:** Ilyssa Evans
**Status:** Active Production Pipeline
