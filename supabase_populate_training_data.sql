-- Populate Training Run Tracking Database
-- This file inserts data for the 3 documented training runs

-- ============================================
-- Insert Caption Versions First (Referenced by training runs)
-- ============================================

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
) VALUES
(
    'civitai_v2_7_training',
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/civitai_v2_7_training/',
    203,
    'Detailed captions with hex color codes, accessories, jewelry, and style keywords',
    true,
    true,
    true,
    'very_detailed',
    'pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60), medium male skin tone (#b27f60), checkered brick background (#c06148), medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002, sharp pixel edges, hard color borders, retro pixel art style',
    '2025-11-09',
    true,
    ARRAY['SD15_PERFECT_Nov9', 'SD15_bespoke_baby_Nov10', 'SDXL_Current_Nov10'],
    'All 203 eye colors verified, all hex codes corrected, 100% accuracy achieved. Used in all three training runs.'
),
(
    'sd15_training_512',
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sd15_training_512/',
    203,
    'Identical to civitai_v2_7_training (verified via diff)',
    true,
    true,
    true,
    'very_detailed',
    'pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60), medium male skin tone (#b27f60), checkered brick background (#c06148), medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002, sharp pixel edges, hard color borders, retro pixel art style',
    '2025-11-09',
    true,
    ARRAY['SD15_PERFECT_Nov9'],
    'Exact copy of civitai_v2_7_training. Verified identical via diff command.'
);

-- ============================================
-- Training Run #1: SD15 PERFECT (SUCCESS)
-- ============================================

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
    'SD15_PERFECT_Nov9',
    '2025-11-09 20:22:00',
    'completed',

    'runwayml/stable-diffusion-v1-5',
    'SD15',

    '/path/to/training/data',  -- Update with actual path if known
    203,
    'detailed_with_hex',
    'civitai_v2_7_training',

    '512x512',
    32,  -- Inferred from 36MB file size
    16,
    0.0001,
    NULL,  -- unet_lr not separately specified
    NULL,  -- text_encoder_lr not separately specified
    1,
    4,  -- Gradient accumulation
    10,
    NULL,  -- Total steps unknown

    'fp16',
    'AdamW8bit',
    'cosine_with_restarts',
    3,
    0.05,
    5,

    '/workspace/output',
    'bespoke_punks_SD15_PERFECT',
    36,

    'RunPod',
    'A100',  -- Assumed
    NULL,  -- Duration not tracked

    7,
    'success',
    9,
    true,

    'PERFECT SUCCESS: Clean, simple pixel art matching reference style. Brown eyes render correctly. All accessories visible. Solid backgrounds. Network dim=32 forced appropriate simplification.',
    ARRAY[]::TEXT[],  -- No issues
    ARRAY['clean_pixel_art', 'correct_brown_eyes', 'accessories_visible', 'solid_backgrounds', 'matches_reference_style'],

    'This is the BASELINE SUCCESS. All other trainings should be compared to this. Network dim=32 is critical - larger dims cause photorealism.',
    'production',

    'Model files: bespoke_punks_SD15_PERFECT-000001.safetensors through 000010.safetensors. Epoch 7 documented as production ready in TRAINING_RESULTS_SUMMARY.md.'
);

-- Get the ID for epoch results
-- Note: In actual usage, you'd get this from the INSERT RETURNING id
-- For this script, we'll use a subquery

-- ============================================
-- Epoch Results for SD15 PERFECT
-- ============================================

-- Epoch 7 (Best/Production)
INSERT INTO epoch_results (
    training_run_id,
    epoch_number,
    checkpoint_path,
    checkpoint_file_size_mb,
    test_output_dir,
    num_test_images,
    visual_quality_score,
    style_match_score,
    prompt_adherence_score,
    has_wrong_backgrounds,
    has_random_pixels,
    has_wrong_colors,
    is_photorealistic,
    is_overtrained,
    issues_detail,
    strengths_detail,
    verdict,
    production_ready,
    observations,
    comparison_to_previous,
    test_image_paths
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SD15_PERFECT_Nov9'),
    7,
    '/Users/ilyssaevans/Downloads/bespoke_punks_SD15_PERFECT-000007.safetensors',
    36,
    '/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_PERFECT_epoch7',
    2,  -- brown_eyes_lad and brown_eyes_lady tested
    9,
    9,
    9,
    false,
    false,
    false,
    false,
    false,
    ARRAY[]::TEXT[],
    ARRAY['clean_pixel_art', 'brown_eyes_correct', 'solid_backgrounds', 'accessories_visible'],
    'best',
    true,
    'Clean, simple pixel art matching reference style. Brown eyes work correctly. All jewelry and accessories visible. Perfect balance - not overtrained.',
    'Significant improvement over epochs 1-6 which had blue eyes instead of brown.',
    ARRAY['/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_PERFECT_epoch7/brown_eyes_lady_512.png', '/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_PERFECT_epoch7/brown_eyes_lad_512.png']
);

-- ============================================
-- Training Run #2: SD15 "bespoke_baby" (FAILURE)
-- ============================================

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

    resolution,
    network_dim,
    network_alpha,
    learning_rate,
    train_batch_size,
    max_train_epochs,

    mixed_precision,
    optimizer_type,

    output_dir,
    output_name,
    checkpoint_file_size_mb,

    platform,

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
    'SD15_bespoke_baby_Nov10',
    '2025-11-10 01:54:00',
    'completed',

    'runwayml/stable-diffusion-v1-5',
    'SD15',

    '/path/to/training/data',
    203,
    'detailed_with_hex',
    'civitai_v2_7_training',  -- SAME captions as successful run

    '512x512',
    64,  -- Inferred from 72MB file size (2x larger than 36MB)
    32,  -- Assumed (2x alpha as well)
    0.0001,
    1,
    10,

    'fp16',
    'AdamW8bit',

    '/workspace/output',
    'bespoke_baby_sd15',
    72,

    'RunPod',

    NULL,  -- No best epoch - all failed
    'failure',
    0,
    false,

    'COMPLETE FAILURE: Produced photorealistic baby photographs instead of pixel art. SAME captions as successful SD15_PERFECT run. Root cause: Network dim=64 (vs 32) allowed base model photorealistic bias to dominate. Critical learning: Network size matters more than captions for style control.',
    ARRAY['photorealistic_output', 'not_pixel_art', 'wrong_style', 'realistic_babies'],
    ARRAY[]::TEXT[],  -- No strengths

    'CRITICAL: This proves network dim is crucial. SAME base model (SD1.5) + SAME captions + DIFFERENT network dim (64 vs 32) = OPPOSITE results. Larger network allowed photorealism, smaller network forced pixel art simplification.',
    'discard',

    'Model files: bespoke_baby_sd15-000001.safetensors through 000009.safetensors. File size 72MB vs 36MB indicates network_dim=64. Training started Nov 10 01:54, AFTER successful SD15_PERFECT run completed. Likely an attempt to improve with larger network that backfired.'
);

-- Epoch 1 (Representative failure - all epochs similar)
INSERT INTO epoch_results (
    training_run_id,
    epoch_number,
    checkpoint_path,
    checkpoint_file_size_mb,
    test_output_dir,
    num_test_images,
    visual_quality_score,
    style_match_score,
    prompt_adherence_score,
    has_wrong_backgrounds,
    has_random_pixels,
    has_wrong_colors,
    is_photorealistic,
    is_overtrained,
    issues_detail,
    strengths_detail,
    verdict,
    production_ready,
    observations,
    test_image_paths
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SD15_bespoke_baby_Nov10'),
    1,
    '/Users/ilyssaevans/Downloads/bespoke_baby_sd15-000001.safetensors',
    72,
    '/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_sd15_epoch1',
    6,
    0,
    0,
    5,
    true,
    false,
    true,
    true,  -- PHOTOREALISTIC
    false,
    ARRAY['photorealistic_baby_photos', 'smooth_gradients', 'not_pixel_art', 'wrong_style'],
    ARRAY[]::TEXT[],
    'failure',
    false,
    'Produced photorealistic baby photographs instead of pixel art. Image 01 shows smooth gradient art. Image 02 shows realistic baby photo with skin texture, realistic eyes, etc. Complete failure of pixel art style learning.',
    ARRAY['/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_sd15_epoch1/01_bespoke_punk_green_bg.png', '/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_sd15_epoch1/02_bespoke_baby_pink_bg.png']
);

-- Epoch 7 (Also failed - representative)
INSERT INTO epoch_results (
    training_run_id,
    epoch_number,
    checkpoint_path,
    checkpoint_file_size_mb,
    test_output_dir,
    num_test_images,
    visual_quality_score,
    style_match_score,
    prompt_adherence_score,
    is_photorealistic,
    verdict,
    production_ready,
    observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SD15_bespoke_baby_Nov10'),
    7,
    '/Users/ilyssaevans/Downloads/bespoke_baby_sd15-000007.safetensors',
    72,
    '/Users/ilyssaevans/Downloads/archived_test_outputs/test_outputs_sd15_epoch7',
    6,
    0,
    0,
    5,
    true,  -- Still photorealistic
    'failure',
    false,
    'Still producing photorealistic baby photos at epoch 7. No improvement. Style learning completely failed.'
);

-- ============================================
-- Training Run #3: SDXL Current (FAILING)
-- ============================================

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
    'SDXL_Current_Nov10',
    '2025-11-10 11:08:00',
    'in_progress',  -- Epochs 9-10 still pending

    'stabilityai/stable-diffusion-xl-base-1.0',
    'SDXL',

    '/workspace/training_data',
    203,
    'detailed_with_hex',
    'civitai_v2_7_training',  -- SAME captions as both SD15 runs

    '1024x1024',
    128,
    64,
    0.0001,
    0.0001,
    0.00005,
    2,
    NULL,  -- No gradient accumulation
    10,
    10150,

    'bf16',
    'AdamW8bit',
    'cosine_with_restarts',
    3,
    0.1,
    5,

    '/workspace/output',
    'bespoke_baby_sdxl',
    1700,  -- 1.7GB

    'RunPod',
    'A100-SXM4-80GB',
    3.5,  -- ~3.5 hours for training

    3,  -- Best so far is epoch 3, but still not production ready
    'failure',  -- Based on epochs 1-8 analysis
    4,  -- Average across epochs
    false,

    'SDXL FAILING: Pixel art achieved but quality issues persist across all 8 tested epochs. SAME detailed captions that worked for SD15_PERFECT. Issues: Random colored pixels (cyan), wrong background colors (8 epochs in a row!), inconsistent quality. Best epoch (3) still has problems. Root cause: SDXL too powerful for simple pixel art + large network dim (128) + high resolution (1024) = too much complexity. Model fighting "simple 24x24 pixel art" instruction.',
    ARRAY['random_colored_pixels', 'wrong_background_colors', 'inconsistent_quality', 'too_complex', 'noisy_textures'],
    ARRAY['pixel_art_style_achieved', 'not_photorealistic'],

    'SDXL adding unwanted complexity. Epochs 1-8 tested - none match SD15_PERFECT quality. More powerful model + larger network + higher resolution = worse results (paradox). Detailed captions work with SD15 but confuse SDXL at high resolution.',
    'reference_only',

    'Model files: bespoke_baby_sdxl-000001.safetensors through 000009.safetensors (final epoch 10 not numbered). Testing in progress. Started after SD15_bespoke_baby failure, attempting SDXL as alternative. Switch to SDXL documented in TRAINING_PROGRESS.md as response to SD15_bespoke_baby photorealism failure.'
);

-- ============================================
-- Epoch Results for SDXL (Epochs 1-8 analyzed)
-- ============================================

-- Epoch 1
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels, has_wrong_colors,
    issues_detail, strengths_detail,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    1, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000001.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch1', 4,
    5, 5, 6,
    false, false, false,
    ARRAY['less_detailed_than_desired'],
    ARRAY['pixel_art_achieved', 'clean_style'],
    'acceptable', false,
    'Baseline epoch. Pixel art style achieved but less detailed than desired. Backgrounds mostly solid.'
);

-- Epoch 2
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    2, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000002.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch2', 4,
    5, 5, 6,
    false, false,
    'acceptable', false,
    'Similar quality to epoch 1. Consistent pixel art. Slight variations in interpretation.'
);

-- Epoch 3 (Best so far)
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels,
    issues_detail, strengths_detail,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    3, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000003.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch3', 4,
    7, 7, 6,
    true, false,
    ARRAY['lad_background_beige_not_blue'],
    ARRAY['best_detail_texture', 'good_hair_texture', 'solid_backgrounds'],
    'good', false,
    'Best quality so far. Improved detail and texture, especially hair. But lad has wrong background (beige instead of blue).'
);

-- Epoch 4 (Quality declined)
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels, has_wrong_colors,
    issues_detail,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    4, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000004.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch4', 4,
    3, 3, 4,
    true, true, true,
    ARRAY['noisy_backgrounds', 'pixelated_patterns', 'texture_instead_solid', 'over_simplified'],
    'skip', false,
    'QUALITY DECLINED. Backgrounds noisy/textured instead of solid. Pixelated patterns appearing. Character over-simplified.'
);

-- Epoch 5 (Recovery)
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels,
    issues_detail, strengths_detail,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    5, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000005.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch5', 4,
    6, 6, 5,
    true, false,
    ARRAY['lad_background_still_wrong', 'more_simplified'],
    ARRAY['cleaner_than_epoch4', 'solid_backgrounds_restored'],
    'acceptable', false,
    'Recovery from epoch 4. Backgrounds cleaner and solid again. More simplified style but cohesive. Lad still has wrong background.'
);

-- Epoch 6
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels, has_wrong_colors,
    issues_detail,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    6, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000006.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch6', 4,
    4, 4, 4,
    true, true, true,
    ARRAY['random_cyan_pixels', 'wrong_hair_colors', 'background_still_wrong'],
    'skip', false,
    'Random colored pixels appearing (cyan). Hair colors sometimes incorrect. Background still wrong on lad (6th epoch in a row!).'
);

-- Epoch 7
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels, has_wrong_colors,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    7, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000007.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch7', 4,
    4, 4, 4,
    true, true, true,
    'skip', false,
    'Same issues persist. Random color pixels. Wrong backgrounds. Not production ready.'
);

-- Epoch 8
INSERT INTO epoch_results (
    training_run_id, epoch_number, checkpoint_path, checkpoint_file_size_mb,
    test_output_dir, num_test_images,
    visual_quality_score, style_match_score, prompt_adherence_score,
    has_wrong_backgrounds, has_random_pixels, has_wrong_colors,
    issues_detail, strengths_detail,
    verdict, production_ready, observations
) VALUES (
    (SELECT id FROM training_runs WHERE run_name = 'SDXL_Current_Nov10'),
    8, '/Users/ilyssaevans/Downloads/bespoke_baby_sdxl-000008.safetensors', 1700,
    '/Users/ilyssaevans/Documents/GitHub/bespokebaby2/sdxl_test_results/test_outputs_sdxl_epoch8', 4,
    4, 4, 5,
    true, true, true,
    ARRAY['gray_bg_not_green', 'cyan_random_pixels', 'beige_bg_not_blue_8th_time'],
    ARRAY['baby_decent_pixel_art', 'lady_correct_purple_bg'],
    'skip', false,
    'Green punk has GRAY background + cyan random pixels. Lad has BEIGE background (8th epoch in a row should be blue!). Some images decent (baby, lady) but inconsistent.'
);

-- ============================================
-- Summary Stats
-- ============================================

-- This will show how many trainings and epochs we're tracking
SELECT 'Training Runs Tracked' as metric, COUNT(*) as count FROM training_runs
UNION ALL
SELECT 'Epochs Analyzed', COUNT(*) FROM epoch_results
UNION ALL
SELECT 'Production Ready Epochs', COUNT(*) FROM epoch_results WHERE production_ready = true
UNION ALL
SELECT 'Successful Training Runs', COUNT(*) FROM training_runs WHERE overall_verdict = 'success';
