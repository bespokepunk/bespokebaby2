-- Drop existing table if it exists
DROP TABLE IF EXISTS caption_reviews CASCADE;
DROP VIEW IF EXISTS review_progress CASCADE;
DROP FUNCTION IF EXISTS update_updated_at() CASCADE;

-- Create comprehensive caption_reviews table
CREATE TABLE caption_reviews (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,

    -- Original data
    current_caption TEXT,
    ai_comprehensive_caption TEXT,

    -- User input and status
    user_input TEXT,
    user_corrections TEXT,
    status TEXT CHECK (status IN ('pending', 'approved', 'edited', 'skipped')) DEFAULT 'pending',

    -- Final merged caption (combines AI + user edits + color enhancements)
    final_caption TEXT,

    -- Full color palette and analysis
    full_palette_15 JSONB,  -- Array of {hex, rgb, percentage}
    region_analysis JSONB,  -- Detailed region-by-region color analysis
    detected_traits JSONB,  -- {hairColor, eyeColor, skinTone, backgroundColor, etc}

    -- Complete raw data
    full_data JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX idx_filename ON caption_reviews(filename);
CREATE INDEX idx_status ON caption_reviews(status);
CREATE INDEX idx_updated_at ON caption_reviews(updated_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE caption_reviews ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (since this is just for you)
CREATE POLICY "Allow all operations" ON caption_reviews
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON caption_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Create view for progress summary
CREATE VIEW review_progress AS
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'approved') as approved,
    COUNT(*) FILTER (WHERE status = 'edited') as edited,
    COUNT(*) FILTER (WHERE status = 'skipped') as skipped,
    COUNT(*) FILTER (WHERE status = 'pending') as pending,
    ROUND(COUNT(*) FILTER (WHERE status IN ('approved', 'edited'))::NUMERIC / COUNT(*)::NUMERIC * 100, 2) as percent_complete
FROM caption_reviews;

-- Grant permissions
GRANT ALL ON caption_reviews TO anon;
GRANT ALL ON caption_reviews TO authenticated;
GRANT SELECT ON review_progress TO anon;
GRANT SELECT ON review_progress TO authenticated;
