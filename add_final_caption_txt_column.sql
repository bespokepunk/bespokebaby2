-- Add final_caption_txt column to caption_reviews table
-- Run this in your Supabase SQL Editor

-- Add the column if it doesn't exist
ALTER TABLE caption_reviews
ADD COLUMN IF NOT EXISTS final_caption_txt TEXT;

-- Add a comment to the column
COMMENT ON COLUMN caption_reviews.final_caption_txt IS 'The final caption from the .txt file (before any user edits)';

-- Update existing rows to populate final_caption_txt from final_caption if empty
UPDATE caption_reviews
SET final_caption_txt = final_caption
WHERE final_caption_txt IS NULL OR final_caption_txt = '';
