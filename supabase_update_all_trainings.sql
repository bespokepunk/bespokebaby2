-- Complete Supabase Update: All Training Runs Verified
-- Date: 2025-11-10
-- Includes: 6+ training runs, verified caption versions, complete metadata

-- First, add caption_version_details column if it doesn't exist
ALTER TABLE training_runs
ADD COLUMN IF NOT EXISTS caption_version_details TEXT,
ADD COLUMN IF NOT EXISTS caption_update_date TIMESTAMP;

-- Update existing records with caption version info
UPDATE training_runs
SET
    caption_version_details = 'OLD captions from backup - generic descriptions, fewer hex codes, less accurate',
    caption_update_date = '2025-11-09 19:09:00'
WHERE run_name = 'SD15_PERFECT_Nov9';

UPDATE training_runs
SET
    caption_version_details = 'NEW accurate captions - specific details, complete color palettes, all hex codes',
    caption_update_date = '2025-11-10 00:53:32'
WHERE run_name IN ('SD15_bespoke_baby_Nov10', 'SDXL_Current_Nov10');

-- Add newly discovered training runs

-- Training Run: 218MB SDXL attempts (Nov 8-9)
INSERT INTO training_runs (
    run_name, run_date, status,
    base_model, model_type,
    resolution, network_dim, network_alpha,
    checkpoint_file_size_mb,
    caption_version, caption_version_details,
    overall_verdict, production_ready,
    notes
) VALUES (
    'SDXL_218MB_Nov8',
    '2025-11-08 17:41:00',
    'completed',
    'stabilityai/stable-diffusion-xl-base-1.0',
    'SDXL',
    '1024x1024',
    64,  -- estimated from file size
    32,  -- estimated
    218,
    'unknown',
    'UNKNOWN - caption version not verified, likely older version',
    'unknown',
    false,
    'Multiple checkpoint files found (Bespoke_Punks_24x24_Pixel_Art, BespokePunks3, BespokePunks5). No test outputs found to match. File size suggests network_dim around 32-64.'
) ON CONFLICT (run_name) DO UPDATE SET
    notes = EXCLUDED.notes,
    checkpoint_file_size_mb = EXCLUDED.checkpoint_file_size_mb;

-- Training Run: 36MB SD1.5 Early (Nov 9, 2AM)
INSERT INTO training_runs (
    run_name, run_date, status,
    base_model, model_type,
    resolution, network_dim, network_alpha,
    checkpoint_file_size_mb,
    caption_version, caption_version_details,
    overall_verdict, production_ready,
    notes
) VALUES (
    'SD15_36MB_Early_Nov9',
    '2025-11-09 02:20:00',
    'incomplete',
    'runwayml/stable-diffusion-v1-5',
    'SD15',
    '512x512',
    32,
    16,
    36,
    'unknown',
    'UNKNOWN - likely OLD captions (before 12:53 AM update)',
    'unknown',
    false,
    'Only 2-3 epochs found (BespokePunks4). No test outputs matched. Incomplete training.'
) ON CONFLICT (run_name) DO UPDATE SET
    notes = EXCLUDED.notes;

-- Training Run: 435MB SDXL Single Epoch (Nov 9, 7PM)
INSERT INTO training_runs (
    run_name, run_date, status,
    base_model, model_type,
    resolution, network_dim, network_alpha,
    checkpoint_file_size_mb,
    caption_version, caption_version_details,
    overall_verdict, quality_score, production_ready,
    notes
) VALUES (
    'SDXL_435MB_Nov9',
    '2025-11-09 19:54:00',
    'incomplete',
    'stabilityai/stable-diffusion-xl-base-1.0',
    'SDXL',
    '1024x1024',
    64,  -- estimated from file size
    32,  -- estimated
    435,
    'unknown',
    'UNKNOWN - likely OLD captions (before 12:53 AM update)',
    'partial_success',
    7,  -- estimated from test output visual quality
    false,
    'Only epoch 1 found (bespoke_punks_PERFECT-000001). Test output test_outputs_PERFECT_SDXL_epoch1 shows GOOD 1024x1024 pixel art. Training incomplete but promising results.'
) ON CONFLICT (run_name) DO UPDATE SET
    notes = EXCLUDED.notes,
    quality_score = EXCLUDED.quality_score;

-- Update SD15_PERFECT with verified caption info
UPDATE training_runs
SET
    caption_version = 'OLD_captions_backup_Nov9',
    caption_version_details = 'Generic descriptions, some hex codes, less detailed than NEW version. Example: "dark gray fluffy voluminous hair, wearing dark gray sunglasses, light skin, brown solid background (#a76857)" vs NEW: "hair (#c06148), wearing gray hat with multicolored (red gold and white) logo, dark brown eyes (#b27f60), checkered brick background (#c06148), full palette"',
    caption_update_date = '2025-11-09 19:09:00',
    notes = 'SUCCESS with OLD less-accurate captions. This is critical: simpler captions may have helped by not overloading the model with details.',
    key_findings = 'CRITICAL FINDING: This training used OLD, LESS ACCURATE captions and SUCCEEDED. All subsequent trainings with NEW MORE ACCURATE captions failed/struggled. Suggests that: (1) Caption accuracy may not be the primary factor, OR (2) Simpler captions work better for pixel art style learning, OR (3) Too much detail in captions confuses the model.'
WHERE run_name = 'SD15_PERFECT_Nov9';

-- Update SD15_bespoke_baby with verified caption info
UPDATE training_runs
SET
    caption_version = 'NEW_accurate_captions_Nov10',
    caption_version_details = 'Highly detailed accurate captions with: specific accessory descriptions (hat logo details), eye colors, complete hex code palettes (12+ colors), accurate background descriptions (checkered brick vs solid), skin tone hex codes.',
    caption_update_date = '2025-11-10 00:53:32',
    notes = 'FAILURE with NEW accurate captions + network_dim=64. Produced realistic baby photographs instead of pixel art.',
    key_findings = 'Used NEW ACCURATE captions but FAILED completely. Root cause likely: network_dim=64 (too large). But raises question: did MORE ACCURATE captions contribute to failure by giving model more photorealistic details to latch onto?',
    issues_found = ARRAY[
        'realistic_baby_photographs',
        'photorealistic_rendering',
        'no_pixel_art_style',
        'base_model_bias_dominates',
        'network_dim_too_large',
        'detailed_captions_may_encourage_realism'
    ]
WHERE run_name = 'SD15_bespoke_baby_Nov10';

-- Update SDXL_Current with verified caption info
UPDATE training_runs
SET
    caption_version = 'NEW_accurate_captions_Nov10',
    caption_version_details = 'Same highly detailed accurate captions as SD15_bespoke_baby. Complete hex codes, specific details, accurate descriptions.',
    caption_update_date = '2025-11-10 00:53:32',
    notes = 'FAILING with NEW accurate captions + network_dim=128 + missing training parameters (shuffle_caption, keep_tokens, multires_noise). Produces pixel art but with wrong colors and artifacts.',
    key_findings = 'Used NEW ACCURATE captions but FAILING. Root causes: (1) network_dim=128 too large, (2) Missing shuffle_caption and keep_tokens parameters, (3) Missing multires_noise regularization, (4) Possibly: detailed captions conflict with simple 24x24 pixel art style',
    issues_found = ARRAY[
        'wrong_background_colors',
        'random_colored_pixels',
        'color_bleeding',
        'inconsistent_style',
        'network_dim_too_large',
        'missing_shuffle_caption',
        'missing_keep_tokens',
        'missing_multires_noise'
    ]
WHERE run_name = 'SDXL_Current_Nov10';

-- Add caption version tracking table
CREATE TABLE IF NOT EXISTS caption_versions_detailed (
    id SERIAL PRIMARY KEY,
    version_name TEXT NOT NULL UNIQUE,
    version_date TIMESTAMP NOT NULL,
    backup_file TEXT,
    sample_caption TEXT,
    detail_level TEXT,
    includes_hex_codes BOOLEAN,
    hex_code_count_avg INTEGER,
    includes_specific_accessories BOOLEAN,
    includes_eye_colors BOOLEAN,
    includes_skin_tone_hex BOOLEAN,
    includes_background_details BOOLEAN,
    avg_caption_length INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert caption versions
INSERT INTO caption_versions_detailed (
    version_name, version_date, backup_file,
    sample_caption, detail_level,
    includes_hex_codes, hex_code_count_avg,
    includes_specific_accessories, includes_eye_colors,
    includes_skin_tone_hex, includes_background_details,
    avg_caption_length, notes
) VALUES (
    'OLD_captions_backup_Nov9',
    '2025-11-09 19:09:00',
    'caption_files_backup_20251109_190911.tar.gz',
    'pixel art, 24x24, portrait of bespoke punk lad, dark gray fluffy voluminous hair, wearing dark gray sunglasses, light skin, brown solid background (#a76857), red clothing with black accents, sharp pixel edges, hard color borders, retro pixel art style',
    'moderate',
    true, 2,
    false, false,
    false, true,
    180,
    'Generic descriptions. Some hex codes (1-3 per caption). Less specific about accessories and features. Used by SD15_PERFECT (SUCCESS).'
), (
    'NEW_accurate_captions_Nov10',
    '2025-11-10 00:53:32',
    NULL,
    'pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60), medium male skin tone (#b27f60), checkered brick background (#c06148), medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002, sharp pixel edges, hard color borders, retro pixel art style, #a76857, #434b4e, #353b3d, #66665a, #421901, #ede9c6, #a17d33, #714d3d',
    'very_detailed',
    true, 12,
    true, true,
    true, true,
    320,
    'Highly detailed with specific accessory descriptions (hat logo, jewelry), eye colors, skin tone hex codes, complete color palettes (12+ hex codes). Accurate background descriptions. Used by SD15_bespoke_baby (FAILURE) and SDXL_Current (FAILING).'
) ON CONFLICT (version_name) DO UPDATE SET
    sample_caption = EXCLUDED.sample_caption,
    notes = EXCLUDED.notes;

-- Add unmatched test outputs table for investigation
CREATE TABLE IF NOT EXISTS unmatched_test_outputs (
    id SERIAL PRIMARY KEY,
    output_directory_name TEXT NOT NULL,
    sample_image_path TEXT,
    visual_quality TEXT,
    suspected_network_dim INTEGER,
    suspected_base_model TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert unmatched test outputs
INSERT INTO unmatched_test_outputs (
    output_directory_name, visual_quality,
    suspected_network_dim, suspected_base_model, notes
) VALUES
    ('test_outputs_FIXED_*', 'mixed', 32, 'SD15', 'Epoch 1: tiny 24x24 EXCELLENT. Epoch 3: larger but WRONG COLORS (pink skin). No matching checkpoint files found.'),
    ('test_outputs_SD15_epoch4', 'good', 32, 'SD15', 'Clean pixel art. No matching checkpoint files found.'),
    ('test_outputs_sd15_epoch3_complete', 'excellent', 32, 'SD15', 'Clean pixel art SUCCESS. Does NOT match 72MB failure checkpoints. Different training?'),
    ('test_outputs_sd15_epoch7', 'good', 32, 'SD15', 'Clean pixel art. Does NOT match any known checkpoint files.')
ON CONFLICT DO NOTHING;

-- Summary statistics
CREATE OR REPLACE VIEW training_summary AS
SELECT
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE overall_verdict = 'success') as successful_runs,
    COUNT(*) FILTER (WHERE overall_verdict = 'failure') as failed_runs,
    COUNT(*) FILTER (WHERE overall_verdict LIKE '%fail%') as failing_runs,
    COUNT(*) FILTER (WHERE overall_verdict = 'unknown') as unknown_runs,
    COUNT(*) FILTER (WHERE caption_version LIKE 'OLD%') as old_caption_runs,
    COUNT(*) FILTER (WHERE caption_version LIKE 'NEW%') as new_caption_runs,
    COUNT(*) FILTER (WHERE production_ready = true) as production_ready_count
FROM training_runs;

-- Caption version effectiveness
CREATE OR REPLACE VIEW caption_version_effectiveness AS
SELECT
    caption_version,
    COUNT(*) as num_runs,
    AVG(quality_score) as avg_quality,
    STRING_AGG(DISTINCT overall_verdict, ', ') as verdicts,
    STRING_AGG(run_name, ', ') as runs
FROM training_runs
WHERE caption_version IS NOT NULL
GROUP BY caption_version;

COMMIT;

-- Display summary
SELECT * FROM training_summary;
SELECT * FROM caption_version_effectiveness;
