-- MLOps Parameter Tracking - Schema Migration
-- Date: November 10, 2025
-- Purpose: Add comprehensive parameter tracking for root cause analysis

-- =============================================================================
-- PHASE 1: Add JSONB columns for flexible parameter storage
-- =============================================================================

-- Add all_parameters column to training_runs
ALTER TABLE training_runs
ADD COLUMN IF NOT EXISTS all_parameters JSONB;

COMMENT ON COLUMN training_runs.all_parameters IS
'Complete training parameters in structured JSONB format.
Includes: architecture, hyperparameters, data, augmentation, preprocessing, stability, derived.
See MLOPS_PARAMETERS.md for full schema.';

-- Add quantitative_metrics column to epoch_results
ALTER TABLE epoch_results
ADD COLUMN IF NOT EXISTS quantitative_metrics JSONB;

COMMENT ON COLUMN epoch_results.quantitative_metrics IS
'Automated quantitative measurements including:
- color_accuracy: Background, hair, accessory accuracy (%)
- style_quality: Edge sharpness, pixel art purity, photorealism scores
Replaces subjective scoring with reproducible metrics.';

-- Add diagnosed_issues column to epoch_results
ALTER TABLE epoch_results
ADD COLUMN IF NOT EXISTS diagnosed_issues JSONB;

COMMENT ON COLUMN epoch_results.diagnosed_issues IS
'Automated issue detection and root cause analysis.
Example: {"photorealism": true, "two_toned_hair": true, "wrong_background": false}';

-- Add recommendations column to epoch_results
ALTER TABLE epoch_results
ADD COLUMN IF NOT EXISTS recommendations TEXT[];

COMMENT ON COLUMN epoch_results.recommendations IS
'Actionable recommendations for improvement.
Example: ["Increase keep_tokens to 3", "Reduce network_dim to 32"]';

-- =============================================================================
-- PHASE 2: Create indexes for fast parameter queries
-- =============================================================================

-- GIN index for fast JSONB queries on training_runs.all_parameters
CREATE INDEX IF NOT EXISTS idx_training_runs_all_parameters
ON training_runs USING GIN (all_parameters);

-- GIN index for fast JSONB queries on epoch_results.quantitative_metrics
CREATE INDEX IF NOT EXISTS idx_epoch_results_quantitative_metrics
ON epoch_results USING GIN (quantitative_metrics);

-- GIN index for fast JSONB queries on epoch_results.diagnosed_issues
CREATE INDEX IF NOT EXISTS idx_epoch_results_diagnosed_issues
ON epoch_results USING GIN (diagnosed_issues);

-- Specific indexes for commonly queried parameters
CREATE INDEX IF NOT EXISTS idx_training_runs_network_dim
ON training_runs ((all_parameters->>'network_dim'));

CREATE INDEX IF NOT EXISTS idx_training_runs_learning_rate
ON training_runs ((all_parameters->>'learning_rate'));

CREATE INDEX IF NOT EXISTS idx_training_runs_caption_version
ON training_runs ((all_parameters->'data'->>'caption_version'));

-- =============================================================================
-- PHASE 3: Create SQL views for easy parameter comparison
-- =============================================================================

-- View: Training run comparison with key parameters
CREATE OR REPLACE VIEW v_training_comparison AS
SELECT
    tr.id,
    tr.run_name,
    tr.run_date,
    tr.status,

    -- Architecture parameters
    (tr.all_parameters->'architecture'->>'network_dim')::integer as network_dim,
    (tr.all_parameters->'architecture'->>'network_alpha')::integer as network_alpha,
    (tr.all_parameters->'architecture'->>'conv_dim')::integer as conv_dim,

    -- Key hyperparameters
    (tr.all_parameters->'hyperparameters'->>'learning_rate')::float as learning_rate,
    tr.all_parameters->'hyperparameters'->>'lr_scheduler' as lr_scheduler,
    (tr.all_parameters->'hyperparameters'->>'max_train_epochs')::integer as max_train_epochs,

    -- Data parameters
    tr.all_parameters->'data'->>'caption_version' as caption_version,
    (tr.all_parameters->'data'->>'num_images')::integer as num_images,
    (tr.all_parameters->'data'->>'keep_tokens')::integer as keep_tokens,
    (tr.all_parameters->'data'->>'caption_dropout_rate')::float as caption_dropout_rate,

    -- Results
    tr.quality_score,
    tr.best_epoch,
    tr.overall_verdict,
    tr.production_ready

FROM training_runs tr
ORDER BY tr.run_date DESC;

COMMENT ON VIEW v_training_comparison IS
'Quick comparison view of all training runs with key parameters extracted.
Use for: "SELECT * FROM v_training_comparison WHERE network_dim = 32"';

-- View: Epoch progression with quantitative metrics
CREATE OR REPLACE VIEW v_epoch_metrics_progression AS
SELECT
    tr.run_name,
    er.epoch_number,

    -- Subjective scores (legacy)
    er.visual_quality_score,
    er.style_match_score,
    er.prompt_adherence_score,
    (er.visual_quality_score + er.style_match_score + er.prompt_adherence_score) / 3.0 as avg_subjective_score,

    -- Quantitative metrics (new)
    (er.quantitative_metrics->'color_accuracy'->>'overall')::float as color_accuracy,
    (er.quantitative_metrics->'color_accuracy'->>'background_accuracy')::float as background_accuracy,
    (er.quantitative_metrics->'color_accuracy'->>'hair_accuracy')::float as hair_accuracy,
    (er.quantitative_metrics->'color_accuracy'->>'hair_is_two_toned')::boolean as hair_two_toned,

    (er.quantitative_metrics->'style_quality'->>'overall')::float as style_quality,
    (er.quantitative_metrics->'style_quality'->>'pixel_art_purity')::float as pixel_art_purity,
    (er.quantitative_metrics->'style_quality'->>'photorealism_score')::float as photorealism_score,

    -- Verdict and status
    er.verdict,
    er.production_ready,
    er.observations

FROM epoch_results er
JOIN training_runs tr ON er.training_run_id = tr.id
ORDER BY tr.run_date DESC, er.epoch_number ASC;

COMMENT ON VIEW v_epoch_metrics_progression IS
'Track quantitative metrics across epochs for a training run.
Use for: "SELECT * FROM v_epoch_metrics_progression WHERE run_name = ''SD15_FINAL_CORRECTED_CAPTIONS''"';

-- View: Parameter correlation analysis helper
CREATE OR REPLACE VIEW v_parameter_correlation_data AS
SELECT
    tr.id as training_run_id,
    tr.run_name,

    -- Extract all critical parameters as columns for easy correlation analysis
    (tr.all_parameters->'architecture'->>'network_dim')::integer as network_dim,
    (tr.all_parameters->'architecture'->>'network_alpha')::integer as network_alpha,
    (tr.all_parameters->'architecture'->>'conv_dim')::integer as conv_dim,
    (tr.all_parameters->'architecture'->>'conv_alpha')::integer as conv_alpha,

    (tr.all_parameters->'hyperparameters'->>'learning_rate')::float as learning_rate,
    tr.all_parameters->'hyperparameters'->>'lr_scheduler' as lr_scheduler,
    (tr.all_parameters->'hyperparameters'->>'max_train_epochs')::integer as max_train_epochs,

    tr.all_parameters->'data'->>'caption_version' as caption_version,
    (tr.all_parameters->'data'->>'num_images')::integer as num_images,
    (tr.all_parameters->'data'->>'keep_tokens')::integer as keep_tokens,
    (tr.all_parameters->'data'->>'caption_dropout_rate')::float as caption_dropout_rate,

    (tr.all_parameters->'augmentation'->>'color_aug')::boolean as color_aug,
    (tr.all_parameters->'augmentation'->>'flip_aug')::boolean as flip_aug,
    (tr.all_parameters->'augmentation'->>'noise_offset')::float as noise_offset,

    -- Outcome variables
    tr.quality_score,
    tr.best_epoch,
    tr.overall_verdict,
    tr.production_ready,

    -- Computed: Did it fail with photorealism?
    CASE
        WHEN tr.overall_verdict = 'failure' AND tr.notes ILIKE '%photorealistic%' THEN true
        ELSE false
    END as failed_photorealism,

    -- Computed: Caption complexity (extract from caption_version)
    CASE
        WHEN tr.all_parameters->'data'->>'caption_version' ILIKE '%12hex%' THEN 'high'
        WHEN tr.all_parameters->'data'->>'caption_version' ILIKE '%detailed%' THEN 'medium'
        ELSE 'low'
    END as caption_complexity

FROM training_runs tr
WHERE tr.all_parameters IS NOT NULL
ORDER BY tr.run_date DESC;

COMMENT ON VIEW v_parameter_correlation_data IS
'Flattened parameter view optimized for correlation analysis in pandas/scipy.
Export to CSV for statistical analysis:
psql -c "COPY (SELECT * FROM v_parameter_correlation_data) TO STDOUT CSV HEADER" > params.csv';

-- =============================================================================
-- PHASE 4: Utility functions
-- =============================================================================

-- Function: Get parameter value by path
CREATE OR REPLACE FUNCTION get_parameter(
    training_run_id_input INTEGER,
    param_path TEXT
) RETURNS TEXT AS $$
DECLARE
    result TEXT;
BEGIN
    SELECT all_parameters #>> string_to_array(param_path, '.')
    INTO result
    FROM training_runs
    WHERE id = training_run_id_input;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_parameter IS
'Get parameter value by dot-notation path.
Example: SELECT get_parameter(12, ''architecture.network_dim'')';

-- Function: Compare two training runs
CREATE OR REPLACE FUNCTION compare_training_runs(
    run_id_a INTEGER,
    run_id_b INTEGER
) RETURNS TABLE(
    parameter_path TEXT,
    value_a TEXT,
    value_b TEXT,
    different BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH params_a AS (
        SELECT all_parameters FROM training_runs WHERE id = run_id_a
    ),
    params_b AS (
        SELECT all_parameters FROM training_runs WHERE id = run_id_b
    )
    SELECT
        key as parameter_path,
        (SELECT all_parameters->>key FROM params_a) as value_a,
        (SELECT all_parameters->>key FROM params_b) as value_b,
        (SELECT all_parameters->>key FROM params_a) IS DISTINCT FROM
        (SELECT all_parameters->>key FROM params_b) as different
    FROM params_a, jsonb_object_keys((SELECT all_parameters FROM params_a)) as key
    ORDER BY different DESC, key;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION compare_training_runs IS
'Compare all parameters between two training runs.
Example: SELECT * FROM compare_training_runs(11, 12) WHERE different = true';

-- =============================================================================
-- PHASE 5: Sample queries for documentation
-- =============================================================================

-- Example 1: Find all runs with network_dim > 32
-- SELECT run_name, network_dim, quality_score, overall_verdict
-- FROM v_training_comparison
-- WHERE network_dim > 32;

-- Example 2: Compare runs with same architecture but different captions
-- SELECT run_name, caption_version, quality_score
-- FROM v_training_comparison
-- WHERE network_dim = 32 AND network_alpha = 16
-- ORDER BY run_date DESC;

-- Example 3: Track color accuracy improvement across epochs
-- SELECT epoch_number, background_accuracy, hair_accuracy, hair_two_toned
-- FROM v_epoch_metrics_progression
-- WHERE run_name = 'SD15_FINAL_CORRECTED_CAPTIONS'
-- ORDER BY epoch_number;

-- Example 4: Find best epoch across all runs
-- SELECT tr.run_name, er.epoch_number,
--        er.visual_quality_score, er.style_match_score, er.prompt_adherence_score,
--        (quantitative_metrics->'color_accuracy'->>'overall')::float as color_accuracy
-- FROM epoch_results er
-- JOIN training_runs tr ON er.training_run_id = tr.id
-- WHERE er.verdict = 'best'
-- ORDER BY (er.visual_quality_score + er.style_match_score + er.prompt_adherence_score) / 3.0 DESC;

-- Example 5: Identify parameter patterns in successful runs
-- SELECT network_dim, learning_rate, keep_tokens, caption_version, COUNT(*) as count
-- FROM v_training_comparison
-- WHERE quality_score >= 8 AND overall_verdict = 'success'
-- GROUP BY network_dim, learning_rate, keep_tokens, caption_version
-- ORDER BY count DESC;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Verify migration
DO $$
BEGIN
    RAISE NOTICE 'Migration complete!';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Run scripts/backfill_parameters.py to populate historical data';
    RAISE NOTICE '2. Test views: SELECT * FROM v_training_comparison LIMIT 5';
    RAISE NOTICE '3. Begin tracking parameters in new training runs';
END $$;
