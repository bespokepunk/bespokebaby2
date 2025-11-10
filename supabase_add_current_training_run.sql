-- Add Current Training Run to Supabase
-- Date: 2025-11-10
-- Purpose: Document the SD15 FINAL CORRECTED CAPTIONS training run

-- Add caption version first
INSERT INTO caption_versions (
    version_name,
    directory_path,
    num_caption_files,
    format_description,
    includes_hex_codes,
    includes_accessories,
    includes_jewelry,
    detail_level,
    sample_caption,
    created_date,
    accuracy_verified,
    used_in_training_runs,
    notes
) VALUES (
    'final_corrected_v1',
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/runpod_package/training_data',
    203,
    'FINAL CORRECTED captions with lips, expressions, 12+ hex codes per caption. Format: pixel art, 24x24, portrait... with all features (hair, eyes, lips, skin, background) using specific hex colors.',
    true,  -- includes hex codes
    true,  -- includes accessories
    true,  -- includes jewelry
    'very_detailed',
    'pixel art, 24x24, portrait of bespoke punk lady, pink hair (#ff66cc), crown, hoop earrings, eyes (#663300), lips (#cc6666), neutral expression, skin (#f0c090), solid green background (#00ff00)',
    '2025-11-10',
    true,  -- accuracy verified in Supabase
    ARRAY['SD15_FINAL_CORRECTED_CAPTIONS'],
    'All 203 captions verified and corrected. Added lips with hex colors, classified all expressions (113 slight smile, 90 neutral), fixed all typos, corrected smoking accessories. This is the most accurate caption set.'
)
ON CONFLICT (version_name) DO UPDATE SET
    format_description = EXCLUDED.format_description,
    notes = EXCLUDED.notes,
    accuracy_verified = true;

-- Insert new training run
INSERT INTO training_runs (
    run_name,
    run_date,
    status,
    base_model,
    model_type,
    training_data_path,
    num_images,
    caption_format,
    caption_version,
    caption_version_details,
    caption_update_date,
    resolution,
    network_dim,
    network_alpha,
    learning_rate,
    unet_lr,
    text_encoder_lr,
    train_batch_size,
    gradient_accumulation_steps,
    max_train_epochs,
    total_steps,
    mixed_precision,
    optimizer_type,
    lr_scheduler,
    lr_scheduler_cycles,
    noise_offset,
    min_snr_gamma,
    output_dir,
    output_name,
    checkpoint_file_size_mb,
    platform,
    gpu_type,
    training_duration_hours,
    best_epoch,
    overall_verdict,
    quality_score,
    production_ready,
    key_findings,
    issues_found,
    strengths,
    comparison_notes,
    recommended_for,
    notes
) VALUES (
    'SD15_FINAL_CORRECTED_CAPTIONS',
    '2025-11-10',
    'in_progress',
    'runwayml/stable-diffusion-v1-5',
    'SD15',
    '/workspace/training_data',
    203,
    'pixel art, 24x24, portrait format with 12+ hex codes',
    'final_corrected_v1',
    'Captions with lips, expressions, all typos fixed. 12+ hex codes per caption. Synced to Supabase.',
    '2025-11-10',
    '512x512',
    32,  -- CRITICAL: Same as SD15_PERFECT (9/10 success)
    16,
    0.0001,  -- 1e-4
    0.0001,  -- unet_lr
    0.00005, -- 5e-5 text_encoder_lr
    1,       -- Effective batch = 1 * 4 = 4
    4,       -- Gradient accumulation
    10,      -- max_train_epochs
    NULL,    -- total_steps (will calculate after training)
    'fp16',
    'AdamW8bit',
    'cosine_with_restarts',
    3,
    0.05,    -- noise_offset (PERFECT used 0.1)
    5,       -- min_snr_gamma
    '/workspace/output',
    'bespoke_baby_sd15_lora',
    36,      -- Expected file size (dim=32 → ~36MB)
    'RunPod',
    'NVIDIA A40/A100',  -- Update with actual GPU
    NULL,    -- training_duration_hours (will update when complete)
    NULL,    -- best_epoch (TBD after testing)
    'pending',
    NULL,    -- quality_score (TBD)
    false,   -- production_ready (TBD)
    'Testing if FINAL CORRECTED captions (with lips, expressions, all typos fixed) improve upon SD15_PERFECT (9/10). Uses ALL optimal parameters from PERFECT run. Network dim=32 proven successful.',
    NULL,    -- issues_found (TBD)
    ARRAY['Uses proven successful network_dim=32', 'All optimal parameters from SD15_PERFECT', 'Most accurate captions (verified in Supabase)', 'Includes lips with hex colors', 'All expressions classified', 'All typos fixed'],
    'Direct comparison to SD15_PERFECT. Testing caption quality impact with identical architecture/parameters.',
    'Testing whether detailed captions improve quality',
    'Training started Nov 10, 2025 on RunPod. Epoch 1 completed and downloaded. Using final_corrected_v1 captions with 12+ hex codes, lips, expressions.'
)
RETURNING id, run_name, status;

-- Check what training runs we have now
SELECT
    run_name,
    model_type,
    network_dim,
    status,
    overall_verdict,
    quality_score,
    production_ready,
    run_date
FROM training_runs
ORDER BY run_date DESC
LIMIT 10;
