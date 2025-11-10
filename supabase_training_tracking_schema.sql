-- Supabase Training Run Tracking Schema
-- Purpose: Track all LoRA training experiments with full metadata for comparison and decision-making

-- ============================================
-- Table 1: Training Runs (Master table)
-- ============================================
CREATE TABLE IF NOT EXISTS training_runs (
    id SERIAL PRIMARY KEY,

    -- Identification
    run_name TEXT NOT NULL UNIQUE,
    run_date TIMESTAMP NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'completed', 'failed', 'cancelled')),

    -- Model Configuration
    base_model TEXT NOT NULL,  -- e.g., 'runwayml/stable-diffusion-v1-5' or 'stabilityai/stable-diffusion-xl-base-1.0'
    model_type TEXT NOT NULL CHECK (model_type IN ('SD15', 'SDXL', 'other')),

    -- Training Data
    training_data_path TEXT,
    num_images INTEGER,
    caption_format TEXT,  -- 'detailed_with_hex', 'simple', 'natural_language', etc.
    caption_version TEXT, -- 'civitai_v2_7', 'sd15_training_512', etc.

    -- Training Parameters
    resolution TEXT,  -- '512x512', '1024x1024', etc.
    network_dim INTEGER,
    network_alpha INTEGER,
    learning_rate FLOAT,
    unet_lr FLOAT,
    text_encoder_lr FLOAT,
    train_batch_size INTEGER,
    gradient_accumulation_steps INTEGER,
    max_train_epochs INTEGER,
    total_steps INTEGER,

    -- Advanced Parameters
    mixed_precision TEXT,  -- 'fp16', 'bf16', 'no'
    optimizer_type TEXT,
    lr_scheduler TEXT,
    lr_scheduler_cycles INTEGER,
    noise_offset FLOAT,
    min_snr_gamma INTEGER,

    -- Output
    output_dir TEXT,
    output_name TEXT,
    checkpoint_file_size_mb INTEGER,  -- File size in MB (useful for identifying network dim)

    -- Platform
    platform TEXT,  -- 'RunPod', 'local', 'Civitai', 'Replicate', etc.
    gpu_type TEXT,  -- 'A100', 'local_mps', etc.
    training_duration_hours FLOAT,

    -- Results & Analysis
    best_epoch INTEGER,
    overall_verdict TEXT CHECK (overall_verdict IN ('success', 'failure', 'partial', 'pending')),
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 10),
    production_ready BOOLEAN DEFAULT false,

    -- Summary
    key_findings TEXT,  -- Brief summary of what worked/didn't work
    issues_found TEXT[],  -- Array of issues: ['realistic_babies', 'wrong_backgrounds', 'random_pixels']
    strengths TEXT[],  -- Array of strengths: ['clean_pixel_art', 'correct_colors']

    -- References
    comparison_notes TEXT,  -- How it compares to other runs
    recommended_for TEXT,  -- 'production', 'testing', 'reference_only', 'discard'

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

-- ============================================
-- Table 2: Epoch Results (Per-epoch analysis)
-- ============================================
CREATE TABLE IF NOT EXISTS epoch_results (
    id SERIAL PRIMARY KEY,
    training_run_id INTEGER REFERENCES training_runs(id) ON DELETE CASCADE,

    epoch_number INTEGER NOT NULL,

    -- Model file
    checkpoint_path TEXT,
    checkpoint_file_size_mb INTEGER,

    -- Test Results
    test_output_dir TEXT,
    num_test_images INTEGER,

    -- Quality Assessment
    visual_quality_score INTEGER CHECK (visual_quality_score >= 0 AND visual_quality_score <= 10),
    style_match_score INTEGER CHECK (style_match_score >= 0 AND style_match_score <= 10),
    prompt_adherence_score INTEGER CHECK (prompt_adherence_score >= 0 AND prompt_adherence_score <= 10),

    -- Specific Issues
    has_wrong_backgrounds BOOLEAN DEFAULT false,
    has_random_pixels BOOLEAN DEFAULT false,
    has_wrong_colors BOOLEAN DEFAULT false,
    is_photorealistic BOOLEAN DEFAULT false,  -- For tracking SD15 failure
    is_overtrained BOOLEAN DEFAULT false,

    -- Details
    issues_detail TEXT[],  -- Specific issues found in this epoch
    strengths_detail TEXT[],  -- What worked well

    -- Verdict
    verdict TEXT CHECK (verdict IN ('best', 'good', 'acceptable', 'skip', 'failure')),
    production_ready BOOLEAN DEFAULT false,

    -- Analysis Notes
    observations TEXT,
    comparison_to_previous TEXT,  -- How it compares to previous epoch

    -- Test Images (store paths or references)
    test_image_paths TEXT[],  -- Array of paths to test images

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,

    UNIQUE(training_run_id, epoch_number)
);

-- ============================================
-- Table 3: Test Prompts (What we test with)
-- ============================================
CREATE TABLE IF NOT EXISTS test_prompts (
    id SERIAL PRIMARY KEY,
    prompt_name TEXT NOT NULL UNIQUE,
    prompt_text TEXT NOT NULL,
    negative_prompt TEXT,
    purpose TEXT,  -- 'brown_eyes_test', 'accessories_test', 'background_test', etc.
    expected_result TEXT,  -- What we expect to see
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Table 4: Test Results Per Prompt
-- ============================================
CREATE TABLE IF NOT EXISTS prompt_test_results (
    id SERIAL PRIMARY KEY,
    epoch_result_id INTEGER REFERENCES epoch_results(id) ON DELETE CASCADE,
    test_prompt_id INTEGER REFERENCES test_prompts(id),

    -- Result
    image_path TEXT,
    passed BOOLEAN,

    -- Specific checks
    correct_background_color BOOLEAN,
    correct_hair_color BOOLEAN,
    correct_eye_color BOOLEAN,
    accessories_visible BOOLEAN,
    is_pixel_art BOOLEAN,
    has_random_artifacts BOOLEAN,

    -- Notes
    observations TEXT,
    score INTEGER CHECK (score >= 0 AND score <= 10),

    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Table 5: Caption Files Tracking
-- ============================================
CREATE TABLE IF NOT EXISTS caption_versions (
    id SERIAL PRIMARY KEY,
    version_name TEXT NOT NULL UNIQUE,  -- 'civitai_v2_7', 'sd15_training_512', etc.

    -- Location
    directory_path TEXT,
    num_caption_files INTEGER,

    -- Format
    format_description TEXT,
    includes_hex_codes BOOLEAN DEFAULT false,
    includes_accessories BOOLEAN DEFAULT false,
    includes_jewelry BOOLEAN DEFAULT false,
    detail_level TEXT CHECK (detail_level IN ('minimal', 'moderate', 'detailed', 'very_detailed')),

    -- Sample
    sample_caption TEXT,  -- Example caption from this version

    -- Metadata
    created_date DATE,
    accuracy_verified BOOLEAN DEFAULT false,
    used_in_training_runs TEXT[],  -- Array of training_run names

    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Indexes for Performance
-- ============================================
CREATE INDEX idx_training_runs_status ON training_runs(status);
CREATE INDEX idx_training_runs_verdict ON training_runs(overall_verdict);
CREATE INDEX idx_training_runs_date ON training_runs(run_date DESC);
CREATE INDEX idx_epoch_results_training ON epoch_results(training_run_id);
CREATE INDEX idx_epoch_results_verdict ON epoch_results(verdict);
CREATE INDEX idx_prompt_results_epoch ON prompt_test_results(epoch_result_id);

-- ============================================
-- Views for Easy Querying
-- ============================================

-- View: Best Training Runs
CREATE OR REPLACE VIEW best_training_runs AS
SELECT
    run_name,
    run_date,
    model_type,
    network_dim,
    network_alpha,
    resolution,
    best_epoch,
    quality_score,
    production_ready,
    key_findings
FROM training_runs
WHERE overall_verdict = 'success'
    AND production_ready = true
ORDER BY quality_score DESC, run_date DESC;

-- View: Production-Ready Epochs
CREATE OR REPLACE VIEW production_ready_epochs AS
SELECT
    tr.run_name,
    tr.model_type,
    er.epoch_number,
    er.checkpoint_path,
    er.visual_quality_score,
    er.style_match_score,
    er.prompt_adherence_score,
    er.verdict
FROM epoch_results er
JOIN training_runs tr ON er.training_run_id = tr.id
WHERE er.production_ready = true
ORDER BY er.visual_quality_score DESC;

-- View: Training Comparison Summary
CREATE OR REPLACE VIEW training_comparison AS
SELECT
    tr.run_name,
    tr.run_date,
    tr.model_type,
    tr.base_model,
    tr.network_dim,
    tr.network_alpha,
    tr.resolution,
    tr.caption_version,
    tr.checkpoint_file_size_mb,
    tr.overall_verdict,
    tr.quality_score,
    tr.production_ready,
    tr.key_findings,
    COUNT(er.id) as num_epochs_tested
FROM training_runs tr
LEFT JOIN epoch_results er ON tr.id = er.training_run_id
GROUP BY tr.id
ORDER BY tr.run_date DESC;

-- ============================================
-- Function: Update training run timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_training_run_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER training_runs_update_timestamp
    BEFORE UPDATE ON training_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_training_run_timestamp();

-- ============================================
-- Comments for Documentation
-- ============================================
COMMENT ON TABLE training_runs IS 'Master table tracking all LoRA training experiments';
COMMENT ON TABLE epoch_results IS 'Per-epoch test results and analysis for each training run';
COMMENT ON TABLE test_prompts IS 'Standard test prompts used to evaluate models';
COMMENT ON TABLE prompt_test_results IS 'Detailed results for each test prompt per epoch';
COMMENT ON TABLE caption_versions IS 'Tracks different caption file versions and their characteristics';

COMMENT ON COLUMN training_runs.network_dim IS 'LoRA network dimension (rank) - affects model capacity and file size';
COMMENT ON COLUMN training_runs.checkpoint_file_size_mb IS 'Useful for identifying network dim: SD15 32=36MB, 64=72MB; SDXL 128=1700MB';
COMMENT ON COLUMN epoch_results.is_photorealistic IS 'Tracks if model produced realistic photos instead of pixel art (SD15 failure case)';
