-- Supabase Authentication & RBAC Setup
-- Date: 2025-11-10
-- Purpose: Enable email authentication with public read, admin write

-- ==============================================================================
-- STEP 1: Create User Roles Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'viewer')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id),
    UNIQUE(email)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_email ON user_roles(email);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_user_roles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_roles_update_timestamp
    BEFORE UPDATE ON user_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_roles_timestamp();

-- ==============================================================================
-- STEP 2: Create Settings Table (for admin control panel)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id)
);

-- Insert default settings
INSERT INTO app_settings (setting_key, setting_value, description) VALUES
    ('public_viewing_enabled', 'true', 'Allow unauthenticated users to view data (read-only)'),
    ('public_editing_enabled', 'false', 'Allow unauthenticated users to edit data (NOT RECOMMENDED)')
ON CONFLICT (setting_key) DO NOTHING;

-- ==============================================================================
-- STEP 3: Whitelist Admin User
-- ==============================================================================

-- Note: This will work AFTER the user signs up via Supabase Auth
-- We'll insert the role after they create their account
-- For now, create a function to add admin when user signs up

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if this is the admin email
    IF NEW.email = 'ilyssaevans@gmail.com' THEN
        INSERT INTO public.user_roles (user_id, email, role)
        VALUES (NEW.id, NEW.email, 'admin');
    ELSE
        -- Default: viewer role for all other users
        INSERT INTO public.user_roles (user_id, email, role)
        VALUES (NEW.id, NEW.email, 'viewer');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ==============================================================================
-- STEP 4: Helper Functions
-- ==============================================================================

-- Check if user is admin
CREATE OR REPLACE FUNCTION public.is_admin(user_email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_roles
        WHERE email = user_email AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user is admin by ID
CREATE OR REPLACE FUNCTION public.is_admin_by_id(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_roles
        WHERE user_id = user_uuid AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if public viewing is enabled
CREATE OR REPLACE FUNCTION public.is_public_viewing_enabled()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        SELECT setting_value::BOOLEAN
        FROM app_settings
        WHERE setting_key = 'public_viewing_enabled'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==============================================================================
-- STEP 5: Row Level Security (RLS) Policies
-- ==============================================================================

-- Enable RLS on caption_reviews table
ALTER TABLE caption_reviews ENABLE ROW LEVEL SECURITY;

-- Policy 1: Public can view if public_viewing_enabled is true
DROP POLICY IF EXISTS "Public can view caption_reviews" ON caption_reviews;
CREATE POLICY "Public can view caption_reviews"
    ON caption_reviews
    FOR SELECT
    TO public
    USING (
        -- Allow if public viewing is enabled
        public.is_public_viewing_enabled()
        OR
        -- OR if user is authenticated
        auth.uid() IS NOT NULL
    );

-- Policy 2: Authenticated viewers can view
DROP POLICY IF EXISTS "Authenticated viewers can view caption_reviews" ON caption_reviews;
CREATE POLICY "Authenticated viewers can view caption_reviews"
    ON caption_reviews
    FOR SELECT
    TO authenticated
    USING (true);

-- Policy 3: Only admins can insert
DROP POLICY IF EXISTS "Only admins can insert caption_reviews" ON caption_reviews;
CREATE POLICY "Only admins can insert caption_reviews"
    ON caption_reviews
    FOR INSERT
    TO authenticated
    WITH CHECK (
        public.is_admin_by_id(auth.uid())
    );

-- Policy 4: Only admins can update
DROP POLICY IF EXISTS "Only admins can update caption_reviews" ON caption_reviews;
CREATE POLICY "Only admins can update caption_reviews"
    ON caption_reviews
    FOR UPDATE
    TO authenticated
    USING (
        public.is_admin_by_id(auth.uid())
    )
    WITH CHECK (
        public.is_admin_by_id(auth.uid())
    );

-- Policy 5: Only admins can delete
DROP POLICY IF EXISTS "Only admins can delete caption_reviews" ON caption_reviews;
CREATE POLICY "Only admins can delete caption_reviews"
    ON caption_reviews
    FOR DELETE
    TO authenticated
    USING (
        public.is_admin_by_id(auth.uid())
    );

-- ==============================================================================
-- Apply same RLS to training_runs table
-- ==============================================================================

ALTER TABLE training_runs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can view training_runs" ON training_runs;
CREATE POLICY "Public can view training_runs"
    ON training_runs FOR SELECT TO public
    USING (public.is_public_viewing_enabled() OR auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS "Only admins can modify training_runs" ON training_runs;
CREATE POLICY "Only admins can modify training_runs"
    ON training_runs FOR ALL TO authenticated
    USING (public.is_admin_by_id(auth.uid()))
    WITH CHECK (public.is_admin_by_id(auth.uid()));

-- ==============================================================================
-- Apply RLS to epoch_results table
-- ==============================================================================

ALTER TABLE epoch_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can view epoch_results" ON epoch_results;
CREATE POLICY "Public can view epoch_results"
    ON epoch_results FOR SELECT TO public
    USING (public.is_public_viewing_enabled() OR auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS "Only admins can modify epoch_results" ON epoch_results;
CREATE POLICY "Only admins can modify epoch_results"
    ON epoch_results FOR ALL TO authenticated
    USING (public.is_admin_by_id(auth.uid()))
    WITH CHECK (public.is_admin_by_id(auth.uid()));

-- ==============================================================================
-- Apply RLS to app_settings table (admin-only)
-- ==============================================================================

ALTER TABLE app_settings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Only admins can view settings" ON app_settings;
CREATE POLICY "Only admins can view settings"
    ON app_settings FOR SELECT TO authenticated
    USING (public.is_admin_by_id(auth.uid()));

DROP POLICY IF EXISTS "Only admins can modify settings" ON app_settings;
CREATE POLICY "Only admins can modify settings"
    ON app_settings FOR ALL TO authenticated
    USING (public.is_admin_by_id(auth.uid()))
    WITH CHECK (public.is_admin_by_id(auth.uid()));

-- ==============================================================================
-- Apply RLS to user_roles table (admin-only)
-- ==============================================================================

ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Admins can view all user roles" ON user_roles;
CREATE POLICY "Admins can view all user roles"
    ON user_roles FOR SELECT TO authenticated
    USING (public.is_admin_by_id(auth.uid()));

DROP POLICY IF EXISTS "Users can view own role" ON user_roles;
CREATE POLICY "Users can view own role"
    ON user_roles FOR SELECT TO authenticated
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Only admins can modify user roles" ON user_roles;
CREATE POLICY "Only admins can modify user roles"
    ON user_roles FOR ALL TO authenticated
    USING (public.is_admin_by_id(auth.uid()))
    WITH CHECK (public.is_admin_by_id(auth.uid()));

-- ==============================================================================
-- VERIFICATION QUERIES
-- ==============================================================================

-- Check tables and RLS status
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('caption_reviews', 'training_runs', 'epoch_results', 'user_roles', 'app_settings')
ORDER BY tablename;

-- Check policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Show settings
SELECT * FROM app_settings ORDER BY setting_key;

-- Show user roles (will be empty until users sign up)
SELECT * FROM user_roles;

-- ==============================================================================
-- NOTES FOR MANUAL STEPS
-- ==============================================================================

-- After running this SQL, you need to:
--
-- 1. Enable Email Auth in Supabase Dashboard:
--    - Go to Authentication > Providers
--    - Enable "Email" provider
--    - Configure email templates if desired
--
-- 2. Sign up the admin user:
--    - Go to Authentication > Users
--    - Click "Invite user"
--    - Enter: ilyssaevans@gmail.com
--    - They will receive invite email and can set password
--    - OR: Manually create user in dashboard
--
-- 3. Verify admin role was assigned:
--    SELECT * FROM user_roles WHERE email = 'ilyssaevans@gmail.com';
--
-- 4. Test authentication in SUPABASE_REVIEW.html
