# Training Run Tracking System

**Purpose:** Comprehensive database system for tracking all LoRA training experiments, preventing circular analysis, and enabling data-driven decisions.

---

## Setup Instructions

### 1. Create Database Schema

In your Supabase SQL Editor, run:

```sql
-- Run this file first
\i supabase_training_tracking_schema.sql
```

This creates:
- **5 tables**: `training_runs`, `epoch_results`, `test_prompts`, `prompt_test_results`, `caption_versions`
- **3 views**: `best_training_runs`, `production_ready_epochs`, `training_comparison`
- **Indexes** for performance
- **Trigger** for automatic timestamp updates

### 2. Populate with Existing Data

```sql
-- Run this file second
\i supabase_populate_training_data.sql
```

This inserts:
- 3 complete training runs (SD15 PERFECT, SD15 bespoke_baby, SDXL Current)
- 13 epoch results (with detailed analysis)
- 2 caption versions

---

## Database Schema Overview

### Table: `training_runs` (Master Table)

Tracks each complete training run with full metadata.

**Key fields:**
- `run_name` - Unique identifier (e.g., 'SD15_PERFECT_Nov9')
- `run_date` - When training started
- `base_model` - Which SD model used
- `network_dim`, `network_alpha` - LoRA configuration
- `caption_version` - Which captions were used
- `overall_verdict` - success/failure/partial/pending
- `quality_score` - 0-10 rating
- `production_ready` - Boolean
- `key_findings` - Summary of what worked/didn't work
- `issues_found` - Array of problems
- `strengths` - Array of what worked well

### Table: `epoch_results`

Per-epoch analysis and test results.

**Key fields:**
- `training_run_id` - Links to training_runs
- `epoch_number` - 1-10
- `visual_quality_score`, `style_match_score`, `prompt_adherence_score` - 0-10 ratings
- `has_wrong_backgrounds`, `has_random_pixels`, `is_photorealistic` - Boolean flags
- `verdict` - best/good/acceptable/skip/failure
- `production_ready` - Boolean
- `observations` - Detailed notes

### Table: `caption_versions`

Tracks different caption file versions.

**Key fields:**
- `version_name` - 'civitai_v2_7_training', 'sd15_training_512', etc.
- `includes_hex_codes`, `includes_accessories`, `includes_jewelry` - Boolean
- `detail_level` - minimal/moderate/detailed/very_detailed
- `sample_caption` - Example for reference
- `used_in_training_runs` - Array of which runs used these captions

---

## Quick Queries

### View All Training Runs

```sql
SELECT * FROM training_comparison ORDER BY run_date DESC;
```

### Find Production-Ready Models

```sql
SELECT * FROM production_ready_epochs;
```

### Compare Training Parameters

```sql
SELECT
    run_name,
    model_type,
    network_dim,
    network_alpha,
    resolution,
    overall_verdict,
    quality_score
FROM training_runs
ORDER BY quality_score DESC;
```

### Find Best Epoch for a Specific Run

```sql
SELECT
    er.epoch_number,
    er.visual_quality_score,
    er.verdict,
    er.observations
FROM epoch_results er
JOIN training_runs tr ON er.training_run_id = tr.id
WHERE tr.run_name = 'SD15_PERFECT_Nov9'
ORDER BY er.visual_quality_score DESC;
```

### Analyze Failure Patterns

```sql
SELECT
    run_name,
    network_dim,
    issues_found,
    key_findings
FROM training_runs
WHERE overall_verdict = 'failure';
```

### Compare Same Captions, Different Networks

```sql
SELECT
    run_name,
    network_dim,
    network_alpha,
    checkpoint_file_size_mb,
    caption_version,
    overall_verdict,
    quality_score,
    key_findings
FROM training_runs
WHERE caption_version = 'civitai_v2_7_training'
ORDER BY quality_score DESC;
```

This query shows the critical finding: SAME captions + different network dims = different results.

---

## Adding a New Training Run

### Step 1: Insert Training Run

```sql
INSERT INTO training_runs (
    run_name,
    run_date,
    status,
    base_model,
    model_type,
    num_images,
    caption_version,
    resolution,
    network_dim,
    network_alpha,
    -- ... other parameters
    notes
) VALUES (
    'Your_Run_Name_Date',
    NOW(),
    'in_progress',
    'runwayml/stable-diffusion-v1-5',
    'SD15',
    203,
    'civitai_v2_7_training',
    '512x512',
    32,
    16,
    -- ... other values
    'Brief description of this training run'
) RETURNING id;
```

### Step 2: Add Epoch Results as They Complete

```sql
INSERT INTO epoch_results (
    training_run_id,
    epoch_number,
    checkpoint_path,
    checkpoint_file_size_mb,
    test_output_dir,
    visual_quality_score,
    style_match_score,
    prompt_adherence_score,
    has_wrong_backgrounds,
    has_random_pixels,
    verdict,
    production_ready,
    observations
) VALUES (
    123,  -- Use the id from previous query
    1,
    '/path/to/epoch-000001.safetensors',
    36,
    '/path/to/test/outputs',
    7,
    8,
    7,
    false,
    false,
    'good',
    false,
    'Your observations here'
);
```

### Step 3: Update Overall Verdict After All Epochs

```sql
UPDATE training_runs
SET
    status = 'completed',
    overall_verdict = 'success',  -- or 'failure'
    quality_score = 9,
    production_ready = true,
    best_epoch = 7,
    key_findings = 'Summary of results',
    issues_found = ARRAY['issue1', 'issue2'],
    strengths = ARRAY['strength1', 'strength2']
WHERE run_name = 'Your_Run_Name_Date';
```

---

## Analysis Workflows

### Before Starting a New Training

**Check what's been tried:**

```sql
-- See all training runs
SELECT * FROM training_comparison;

-- Check if similar parameters have been tried
SELECT * FROM training_runs
WHERE network_dim = 32 AND resolution = '512x512';

-- See what caption versions worked
SELECT
    cv.version_name,
    tr.run_name,
    tr.overall_verdict,
    tr.quality_score
FROM caption_versions cv
JOIN training_runs tr ON cv.version_name = tr.caption_version
ORDER BY tr.quality_score DESC;
```

### During Training

**Track progress:**

```sql
-- Add epoch results as tests complete
INSERT INTO epoch_results (...) VALUES (...);

-- Check current best epoch
SELECT epoch_number, visual_quality_score, verdict
FROM epoch_results
WHERE training_run_id = (SELECT id FROM training_runs WHERE run_name = 'Current_Run')
ORDER BY visual_quality_score DESC;
```

### After Training

**Compare to previous runs:**

```sql
SELECT
    run_name,
    network_dim,
    network_alpha,
    quality_score,
    best_epoch,
    key_findings
FROM training_runs
WHERE model_type = 'SD15'  -- or 'SDXL'
ORDER BY quality_score DESC;
```

---

## Key Findings from Current Data

### Finding #1: Network Dimension is Critical

```sql
SELECT
    run_name,
    network_dim,
    checkpoint_file_size_mb,
    overall_verdict,
    quality_score,
    key_findings
FROM training_runs
WHERE model_type = 'SD15'
ORDER BY network_dim;
```

**Result:**
- dim=32 (36MB) → SUCCESS (quality 9/10)
- dim=64 (72MB) → FAILURE (photorealistic babies)

**Learning:** Smaller network forces simplification = pixel art. Larger network allows base model bias = photorealism.

### Finding #2: SDXL Struggles with Simple Pixel Art

```sql
SELECT
    model_type,
    network_dim,
    resolution,
    AVG(quality_score) as avg_quality
FROM training_runs
GROUP BY model_type, network_dim, resolution;
```

**Result:**
- SD15 (dim=32, 512x512) → 9/10
- SDXL (dim=128, 1024x1024) → 4/10

**Learning:** More powerful model ≠ better results for simple styles.

### Finding #3: Caption Accuracy Alone Doesn't Guarantee Success

```sql
SELECT
    caption_version,
    COUNT(*) as num_runs,
    AVG(quality_score) as avg_quality,
    STRING_AGG(overall_verdict, ', ') as verdicts
FROM training_runs
GROUP BY caption_version;
```

**Result:**
All 3 runs used 'civitai_v2_7_training' (detailed, accurate captions):
- 1 success (9/10)
- 1 failure (0/10)
- 1 partial (4/10)

**Learning:** Model architecture and parameters matter MORE than caption quality for style learning.

---

## Exporting Data

### Export Training Summary as CSV

```sql
COPY (
    SELECT
        run_name,
        run_date,
        model_type,
        network_dim,
        resolution,
        overall_verdict,
        quality_score,
        production_ready,
        key_findings
    FROM training_runs
    ORDER BY run_date DESC
) TO '/tmp/training_runs.csv' WITH CSV HEADER;
```

### Export for Analysis

```sql
-- Get all data as JSON
SELECT json_agg(t) FROM training_comparison t;
```

---

## Maintenance

### Clean Up Old Test Data

```sql
-- Delete training runs marked for discard (keeps history but flags as not relevant)
DELETE FROM training_runs
WHERE recommended_for = 'discard'
AND run_date < NOW() - INTERVAL '6 months';
```

### Update Analysis

```sql
-- After reviewing more test images, update epoch analysis
UPDATE epoch_results
SET
    visual_quality_score = 8,
    observations = 'Updated after detailed review',
    updated_at = NOW()
WHERE training_run_id = (SELECT id FROM training_runs WHERE run_name = 'Run_Name')
AND epoch_number = 5;
```

---

## Dashboard Queries

### Training Success Rate

```sql
SELECT
    model_type,
    COUNT(*) as total_runs,
    SUM(CASE WHEN overall_verdict = 'success' THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(quality_score), 2) as avg_quality
FROM training_runs
GROUP BY model_type;
```

### Best Parameters

```sql
SELECT
    network_dim,
    network_alpha,
    resolution,
    COUNT(*) as times_tried,
    AVG(quality_score) as avg_quality,
    MAX(quality_score) as best_quality
FROM training_runs
WHERE overall_verdict != 'pending'
GROUP BY network_dim, network_alpha, resolution
ORDER BY avg_quality DESC;
```

### Issue Frequency

```sql
SELECT
    UNNEST(issues_found) as issue,
    COUNT(*) as frequency
FROM training_runs
WHERE overall_verdict = 'failure'
GROUP BY issue
ORDER BY frequency DESC;
```

---

## Benefits of This System

1. **No More Circular Analysis** - All findings documented, searchable
2. **Data-Driven Decisions** - Compare parameters, see what worked
3. **Complete Traceability** - Every training run tracked with full metadata
4. **Pattern Recognition** - Identify what causes failures/successes
5. **Time Savings** - Don't retry failed approaches
6. **Knowledge Base** - Historical record of all experiments

---

## Next Steps

1. ✅ Run schema setup SQL
2. ✅ Populate with 3 existing trainings
3. ⏳ Add epochs 9-10 for SDXL when available
4. ⏳ Use findings to plan next training (likely SD15 dim=32 retry)
5. 📊 Create Supabase dashboard for visualization
6. 🔄 Update after every new training run

---

## Files

- `supabase_training_tracking_schema.sql` - Database schema
- `supabase_populate_training_data.sql` - Initial data
- `TRAINING_TRACKING_README.md` - This file (documentation)
- `TRAINING_TIMELINE_TABLE.md` - Human-readable summary
- `TRAINING_COMPARISON_ANALYSIS.md` - Detailed analysis

---

**This system ensures we never lose track of what we've tried and can make informed decisions about next steps based on actual data, not assumptions.**
