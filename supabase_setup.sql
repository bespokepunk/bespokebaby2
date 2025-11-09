-- Create caption_reviews table
CREATE TABLE caption_reviews (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    current_caption TEXT,
    ai_caption TEXT,
    user_input TEXT,
    status TEXT CHECK (status IN ('pending', 'approved', 'edited', 'skipped')),
    full_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
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
    COUNT(*) FILTER (WHERE status = 'pending') as pending
FROM caption_reviews;
