-- Update Supabase with NEW caption version: LIPS_COMPLETE (Nov 10, 2025)
-- All 203 captions now include: lips (#hexcode), facial expression (smile/neutral)

-- Add new caption version to detailed tracking table
INSERT INTO caption_versions_detailed (
    version_name,
    version_date,
    sample_caption,
    includes_hex_codes,
    hex_code_count_avg,
    avg_length_chars,
    includes_eyes,
    includes_skin_tone,
    includes_accessories,
    includes_background,
    includes_style_tags,
    includes_lips,
    includes_facial_expression,
    total_images,
    notes
) VALUES (
    'LIPS_COMPLETE_Nov10',
    '2025-11-10 19:50:00',
    'pixel art, 24x24, portrait of bespoke punk lad, hair (#c06148), wearing gray hat with multicolored (red gold and white) logo in the center, dark brown eyes (#b27f60), lips (#c06148), slight smile, medium male skin tone (#b27f60), checkered brick background (#c06148), medium grey shirt (#000000), palette: #c06148, #b27f60, #000000, #281002, sharp pixel edges, hard color borders, retro pixel art style, #a76857, #434b4e, #353b3d, #66665a, #421901, #ede9c6, #a17d33, #714d3d',
    true,  -- includes_hex_codes
    12,    -- hex_code_count_avg
    340,   -- avg_length_chars (with lips + expression adds ~30 chars)
    true,  -- includes_eyes
    true,  -- includes_skin_tone
    true,  -- includes_accessories
    true,  -- includes_background
    true,  -- includes_style_tags
    true,  -- includes_lips ✅ NEW
    true,  -- includes_facial_expression ✅ NEW
    203,   -- total_images
    'CRITICAL QC FIX: Added lips (#hexcode) and facial expression (slight smile/neutral expression) to ALL 203 captions. Previously only 113/203 had lips. This is the COMPLETE accurate caption version with all details. Automated extraction from images + manual QC verification.'
) ON CONFLICT (version_name) DO UPDATE SET
    version_date = EXCLUDED.version_date,
    sample_caption = EXCLUDED.sample_caption,
    includes_lips = EXCLUDED.includes_lips,
    includes_facial_expression = EXCLUDED.includes_facial_expression,
    notes = EXCLUDED.notes;

-- Update caption effectiveness view to show new version
CREATE OR REPLACE VIEW caption_version_effectiveness AS
SELECT
    caption_version,
    COUNT(*) as training_count,
    AVG(quality_score) as avg_quality,
    MAX(quality_score) as best_quality,
    MIN(quality_score) as worst_quality,
    STRING_AGG(run_name, ', ' ORDER BY run_date DESC) as training_runs,
    STRING_AGG(overall_verdict, ', ') as verdicts
FROM training_runs
WHERE caption_version IS NOT NULL
GROUP BY caption_version
ORDER BY avg_quality DESC NULLS LAST;

-- Record this QC fix in the changelog
INSERT INTO caption_changelog (
    change_date,
    version_before,
    version_after,
    files_affected,
    change_type,
    description
) VALUES (
    '2025-11-10 19:50:00',
    'NEW_accurate_captions_Nov10',  -- The incomplete version
    'LIPS_COMPLETE_Nov10',          -- The corrected version
    90,  -- 90 files needed lips added
    'QC_FIX',
    'CRITICAL: Discovered 90/203 caption files were missing lips (#hexcode) and facial expression. Used automated image analysis to extract lip colors and detect expressions. Added to all 90 files. Format: "lips (#hexcode), [slight smile/neutral expression]". All 203 files now consistent and complete.'
);

-- Add note about which training was affected by incomplete captions
UPDATE training_runs
SET notes = CONCAT(notes, ' ⚠️ STOPPED: Training used incomplete captions (90/203 missing lips). Re-running with LIPS_COMPLETE version.')
WHERE run_name = 'SD15_NEW_CAPTIONS_OPTIMAL_Nov10'
AND run_date >= '2025-11-10 19:00:00';

SELECT '✓ Supabase updated with LIPS_COMPLETE caption version' as status;
SELECT '✓ Caption changelog updated with QC fix details' as status;
SELECT '✓ Caption effectiveness view refreshed' as status;
