-- ============================================================================
-- SUPABASE BACKFILL SCRIPT - Fix Database Gaps
-- ============================================================================
-- Date: 2025-11-10
-- Purpose:
--   1. Create missing tables (user_roles, app_settings)
--   2. Log CAPTION_FIX training run (production LoRA)
--   3. Add new tables for trait detection system
--   4. Set up admin user
-- ============================================================================

-- ============================================================================
-- STEP 1: Create Missing Core Tables
-- ============================================================================

-- User Roles Table (for admin panel authentication)
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'viewer')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_roles_email ON user_roles(email);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role);

-- App Settings Table (for admin panel settings)
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    setting_description TEXT,
    updated_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(setting_key);

-- Insert default app settings
INSERT INTO app_settings (setting_key, setting_value, setting_description) VALUES
    ('public_viewing_enabled', 'true', 'Allow unauthenticated users to view data (read-only)')
ON CONFLICT (setting_key) DO NOTHING;

INSERT INTO app_settings (setting_key, setting_value, setting_description) VALUES
    ('public_editing_enabled', 'false', 'Allow unauthenticated users to edit data (NOT RECOMMENDED)')
ON CONFLICT (setting_key) DO NOTHING;

-- ============================================================================
-- STEP 2: Log CAPTION_FIX Training Run (Production LoRA)
-- ============================================================================

-- Insert CAPTION_FIX training run
INSERT INTO training_runs (
    run_name,
    run_date,
    caption_version,
    base_model,
    resolution,
    network_dim,
    network_alpha,
    learning_rate,
    num_epochs,
    notes,
    overall_verdict,
    quality_score,
    observations
) VALUES (
    'CAPTION_FIX_Epoch8_Production',
    '2025-11-09',
    'caption_fix_v1',
    'runwayml/stable-diffusion-v1-5',
    512,
    128,
    128,
    1e-4,
    10,
    'CAPTION_FIX training - Focus on clean captions, accurate colors, solid backgrounds. This is the PRODUCTION LoRA currently deployed in app_gradio.py.',
    'success',
    8.5,
    'Best epoch: 8. Cleanest results with avg 216.6 colors. Solid backgrounds maintained, accurate eye/hair colors, good pixel art style.'
)
ON CONFLICT DO NOTHING
RETURNING id;

-- Get the training_run_id for CAPTION_FIX
-- Note: If run already exists, this will return the existing ID
DO $$
DECLARE
    caption_fix_run_id INTEGER;
BEGIN
    SELECT id INTO caption_fix_run_id
    FROM training_runs
    WHERE run_name = 'CAPTION_FIX_Epoch8_Production';

    -- Insert epoch 8 result (PRODUCTION)
    INSERT INTO epoch_results (
        training_run_id,
        epoch_number,
        checkpoint_path,
        checkpoint_file_size_mb,
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
        notes,
        quantitative_metrics
    ) VALUES (
        caption_fix_run_id,
        8,
        'lora_checkpoints/caption_fix/caption_fix_epoch8.safetensors',
        36,
        10,
        9,
        8,
        8,
        false,
        false,
        false,
        false,
        false,
        ARRAY[]::text[],
        ARRAY['clean_pixel_art', 'solid_backgrounds', 'accurate_colors', 'good_eye_colors']::text[],
        'best',
        true,
        'Epoch 8: PRODUCTION READY. Cleanest results with 216.6 avg colors. Solid backgrounds maintained. Brown eyes render as brown (not black). Good pixel art quality. Currently deployed in app_gradio.py.',
        'CAPTION_FIX Epoch 8 - Currently used in production. Best balance of cleanliness and accuracy.',
        jsonb_build_object(
            'avg_colors', 216.6,
            'style_quality', 'excellent',
            'background_accuracy', 'high',
            'color_accuracy', 'high',
            'deployed_in_production', true,
            'production_file', 'app_gradio.py'
        )
    )
    ON CONFLICT (training_run_id, epoch_number)
    DO UPDATE SET
        production_ready = true,
        verdict = 'best',
        notes = 'CAPTION_FIX Epoch 8 - Currently used in production. Best balance of cleanliness and accuracy.',
        quantitative_metrics = jsonb_build_object(
            'avg_colors', 216.6,
            'style_quality', 'excellent',
            'background_accuracy', 'high',
            'color_accuracy', 'high',
            'deployed_in_production', true,
            'production_file', 'app_gradio.py'
        );
END $$;

-- ============================================================================
-- STEP 3: Create New Tables for Trait Detection System
-- ============================================================================

-- User Generations (Track production usage)
CREATE TABLE IF NOT EXISTS user_generations (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    session_id TEXT,
    uploaded_image_hash TEXT,
    auto_detected_features JSONB, -- {hair, eyes, skin, glasses, expression, etc}
    alacarte_traits_selected TEXT[], -- ['crown', 'flower_in_hair', etc]
    epoch_used INTEGER,
    lora_path TEXT,
    prompt_used TEXT,
    negative_prompt TEXT,
    generation_successful BOOLEAN DEFAULT true,
    error_message TEXT,
    output_512_path TEXT,
    output_24_path TEXT,
    generation_time_seconds DECIMAL(5,2),
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_generations_user_id ON user_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_generations_session_id ON user_generations(session_id);
CREATE INDEX IF NOT EXISTS idx_user_generations_created_at ON user_generations(created_at);
CREATE INDEX IF NOT EXISTS idx_user_generations_epoch ON user_generations(epoch_used);
CREATE INDEX IF NOT EXISTS idx_user_generations_rating ON user_generations(user_rating);
CREATE INDEX IF NOT EXISTS idx_user_generations_auto_detected ON user_generations USING gin(auto_detected_features);
CREATE INDEX IF NOT EXISTS idx_user_generations_alacarte ON user_generations USING gin(alacarte_traits_selected);

COMMENT ON TABLE user_generations IS 'Tracks all user generations for analytics and improvement';
COMMENT ON COLUMN user_generations.auto_detected_features IS 'JSON object with all auto-detected features {glasses: true, expression: smile, etc}';
COMMENT ON COLUMN user_generations.alacarte_traits_selected IS 'Array of trait IDs user manually selected [crown, cat_ears, etc]';

-- Trait Detection Accuracy (Learn and improve auto-detection)
CREATE TABLE IF NOT EXISTS trait_detection_accuracy (
    id SERIAL PRIMARY KEY,
    generation_id INTEGER REFERENCES user_generations(id) ON DELETE CASCADE,
    trait_type TEXT NOT NULL, -- 'glasses', 'expression', 'facial_hair', etc
    detected_value TEXT, -- What we detected: 'glasses', 'sunglasses', 'none'
    user_confirmed BOOLEAN, -- Did user confirm detection was correct?
    user_corrected_value TEXT, -- What user said it should be
    detection_confidence DECIMAL(3,2), -- 0.00-1.00 confidence score
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trait_accuracy_generation ON trait_detection_accuracy(generation_id);
CREATE INDEX IF NOT EXISTS idx_trait_accuracy_type ON trait_detection_accuracy(trait_type);
CREATE INDEX IF NOT EXISTS idx_trait_accuracy_confirmed ON trait_detection_accuracy(user_confirmed);

COMMENT ON TABLE trait_detection_accuracy IS 'Tracks accuracy of auto-detection to improve algorithms';

-- À La Carte Trait Usage (Track popularity and quality)
CREATE TABLE IF NOT EXISTS alacarte_trait_usage (
    id SERIAL PRIMARY KEY,
    trait_id TEXT NOT NULL UNIQUE, -- 'crown', 'cat_ears', 'jester_hat', etc
    trait_category TEXT NOT NULL, -- 'special_eyewear', 'special_hats', etc
    trait_label TEXT NOT NULL, -- Display name: "Golden Crown with Gems"
    times_selected INTEGER DEFAULT 0,
    times_rated_positive INTEGER DEFAULT 0, -- Rating >= 4
    times_rated_negative INTEGER DEFAULT 0, -- Rating <= 2
    avg_user_rating DECIMAL(3,2),
    total_rating_count INTEGER DEFAULT 0,
    last_selected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alacarte_trait_id ON alacarte_trait_usage(trait_id);
CREATE INDEX IF NOT EXISTS idx_alacarte_category ON alacarte_trait_usage(trait_category);
CREATE INDEX IF NOT EXISTS idx_alacarte_popularity ON alacarte_trait_usage(times_selected DESC);

COMMENT ON TABLE alacarte_trait_usage IS 'Tracks which à la carte traits are most popular and highest rated';

-- Epoch Usage Analytics (Which epochs get used in production)
CREATE TABLE IF NOT EXISTS epoch_usage_analytics (
    id SERIAL PRIMARY KEY,
    epoch_number INTEGER NOT NULL,
    training_run_id INTEGER REFERENCES training_runs(id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_generations INTEGER DEFAULT 0,
    successful_generations INTEGER DEFAULT 0,
    failed_generations INTEGER DEFAULT 0,
    avg_rating DECIMAL(3,2),
    avg_generation_time DECIMAL(5,2),
    UNIQUE(epoch_number, training_run_id, date)
);

CREATE INDEX IF NOT EXISTS idx_epoch_analytics_epoch ON epoch_usage_analytics(epoch_number);
CREATE INDEX IF NOT EXISTS idx_epoch_analytics_date ON epoch_usage_analytics(date);

COMMENT ON TABLE epoch_usage_analytics IS 'Daily analytics of which epochs are used and how they perform';

-- ============================================================================
-- STEP 4: Insert Initial À La Carte Traits
-- ============================================================================

-- Special Eyewear
INSERT INTO alacarte_trait_usage (trait_id, trait_category, trait_label) VALUES
    ('party_glasses', 'special_eyewear', 'Party Glasses (Translucent)'),
    ('3d_glasses', 'special_eyewear', '3D Cinema Glasses'),
    ('vr_headset', 'special_eyewear', 'VR Headset'),
    ('mog_goggles', 'special_eyewear', 'Cyberpunk Mog Goggles'),
    ('lab_goggles', 'special_eyewear', 'Lab Safety Goggles')
ON CONFLICT (trait_id) DO NOTHING;

-- Royal Accessories
INSERT INTO alacarte_trait_usage (trait_id, trait_category, trait_label) VALUES
    ('crown', 'royal_accessories', 'Golden Crown with Gems'),
    ('tiara', 'royal_accessories', 'Pearl Diamond Tiara'),
    ('flower_crown', 'royal_accessories', 'Golden Flower Crown')
ON CONFLICT (trait_id) DO NOTHING;

-- Headbands & Ears
INSERT INTO alacarte_trait_usage (trait_id, trait_category, trait_label) VALUES
    ('bandana_orange', 'headbands', 'Orange Polka Dot Bandana (1940s)'),
    ('bandana_red', 'headbands', 'Red Polka Dot Bandana (1940s)'),
    ('cat_ears', 'headbands', 'Cat Ears Headband'),
    ('ninja_headband', 'headbands', 'Ninja Headband')
ON CONFLICT (trait_id) DO NOTHING;

-- Special Hats
INSERT INTO alacarte_trait_usage (trait_id, trait_category, trait_label) VALUES
    ('top_hat', 'special_hats', 'Fancy Top Hat'),
    ('wizard_hat', 'special_hats', 'Epic Magical Wizard Hat'),
    ('jester_hat', 'special_hats', 'Colorful Jester Hat'),
    ('fedora', 'special_hats', 'Classic Fedora'),
    ('bucket_hat_furry', 'special_hats', 'Furry Bucket Hat')
ON CONFLICT (trait_id) DO NOTHING;

-- Necklaces
INSERT INTO alacarte_trait_usage (trait_id, trait_category, trait_label) VALUES
    ('gold_chain', 'necklaces', 'Thick Gold Chain'),
    ('diamond_pendant', 'necklaces', 'Diamond Pendant Necklace'),
    ('blockchain_themed', 'necklaces', 'Blockchain-Themed Jewelry')
ON CONFLICT (trait_id) DO NOTHING;

-- Decorative
INSERT INTO alacarte_trait_usage (trait_id, trait_category, trait_label) VALUES
    ('flower_in_hair', 'decorative', 'Flower in Hair (Winehouse Style)')
ON CONFLICT (trait_id) DO NOTHING;

-- ============================================================================
-- STEP 5: Create Analytics Views
-- ============================================================================

-- View: Most Popular À La Carte Traits
CREATE OR REPLACE VIEW v_popular_alacarte_traits AS
SELECT
    trait_id,
    trait_category,
    trait_label,
    times_selected,
    avg_user_rating,
    total_rating_count,
    ROUND((times_rated_positive::DECIMAL / NULLIF(total_rating_count, 0)) * 100, 1) as positive_rating_pct,
    last_selected_at
FROM alacarte_trait_usage
WHERE times_selected > 0
ORDER BY times_selected DESC, avg_user_rating DESC
LIMIT 20;

-- View: Auto-Detection Accuracy Summary
CREATE OR REPLACE VIEW v_autodetect_accuracy AS
SELECT
    trait_type,
    COUNT(*) as total_detections,
    SUM(CASE WHEN user_confirmed = true THEN 1 ELSE 0 END) as correct_detections,
    ROUND(
        (SUM(CASE WHEN user_confirmed = true THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100,
        1
    ) as accuracy_pct,
    AVG(detection_confidence) as avg_confidence
FROM trait_detection_accuracy
WHERE user_confirmed IS NOT NULL
GROUP BY trait_type
ORDER BY accuracy_pct DESC;

-- View: Daily Generation Stats
CREATE OR REPLACE VIEW v_daily_generation_stats AS
SELECT
    DATE(created_at) as generation_date,
    COUNT(*) as total_generations,
    SUM(CASE WHEN generation_successful = true THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN generation_successful = false THEN 1 ELSE 0 END) as failed,
    AVG(generation_time_seconds) as avg_time_seconds,
    AVG(user_rating) as avg_rating,
    COUNT(DISTINCT session_id) as unique_sessions
FROM user_generations
GROUP BY DATE(created_at)
ORDER BY generation_date DESC;

-- ============================================================================
-- STEP 6: Set Up Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_settings ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read user_roles (for checking permissions)
CREATE POLICY "Public read access for user_roles" ON user_roles
    FOR SELECT USING (true);

-- Policy: Only admins can modify user_roles
CREATE POLICY "Admin write access for user_roles" ON user_roles
    FOR ALL USING (
        auth.uid() IN (SELECT user_id FROM user_roles WHERE role = 'admin')
    );

-- Policy: Anyone can read app_settings
CREATE POLICY "Public read access for app_settings" ON app_settings
    FOR SELECT USING (true);

-- Policy: Only admins can modify app_settings
CREATE POLICY "Admin write access for app_settings" ON app_settings
    FOR ALL USING (
        auth.uid() IN (SELECT user_id FROM user_roles WHERE role = 'admin')
    );

-- ============================================================================
-- STEP 7: Grant Permissions
-- ============================================================================

-- Grant permissions on new tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT INSERT ON user_generations, trait_detection_accuracy TO anon, authenticated;
GRANT UPDATE ON alacarte_trait_usage, epoch_usage_analytics TO anon, authenticated;

-- Grant sequence usage
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if CAPTION_FIX run was created
SELECT id, run_name, overall_verdict, quality_score
FROM training_runs
WHERE run_name = 'CAPTION_FIX_Epoch8_Production';

-- Check if epoch 8 is marked production_ready
SELECT epoch_number, verdict, production_ready, notes
FROM epoch_results
WHERE checkpoint_path LIKE '%caption_fix_epoch8%';

-- Check app_settings
SELECT setting_key, setting_value FROM app_settings;

-- Check à la carte traits loaded
SELECT trait_category, COUNT(*) as trait_count
FROM alacarte_trait_usage
GROUP BY trait_category
ORDER BY trait_count DESC;

-- ============================================================================
-- DONE!
-- ============================================================================
-- Next steps:
-- 1. Add your user as admin:
--    INSERT INTO user_roles (user_id, email, role)
--    VALUES ('<your_auth_user_id>', 'ilyssaevans@gmail.com', 'admin');
--
-- 2. Test admin panel login
-- 3. Verify CAPTION_FIX epoch 8 appears in UI
-- ============================================================================
