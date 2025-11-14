# Bespoke Punks Website - Directory Structure

## Punk Image Directories

### `/public/punks/` - TRAINING DATA (DO NOT MODIFY)
**Purpose:** Original 203 punk images used for ML training
**Source:** Copied from `/runpod_package/training_data/`
**Status:** FROZEN - Used for model training only
**Count:** 203 images
**Note:** This directory mirrors the exact training data. Never delete or modify files here.

### `/public/punks-display/` - WEBSITE DISPLAY (CURATED)
**Purpose:** Curated punk images for website display
**Source:** Copy of `/public/punks/` with duplicates/training-only removed
**Status:** ACTIVE - This is what the website shows
**Count:** 203 initially (will be reduced after audit)
**Note:** Safe to remove duplicates/variants from this directory. Training data remains intact.

## Workflow

1. **Training data stays in:** `/public/punks/` and original `/runpod_package/training_data/`
2. **Website displays from:** `/public/punks-display/`
3. **To remove a punk from display:**
   - Delete it from `/public/punks-display/` ONLY
   - Regenerate `punk-names.json` from this directory
   - Training data in `/public/punks/` remains unchanged

## Current Status

- ✅ Training data: 203 punks in `/public/punks/`
- ✅ Display data: 203 punks in `/public/punks-display/` (awaiting audit)
- ⏳ Audit in progress: Identifying duplicates/variants to remove from display
- ⏳ Website currently points to: `/public/punks/` (needs update to `/public/punks-display/`)

## Next Steps

1. Audit display directory for duplicates (e.g., lad_103_merheb vs merheb2 vs merheb3)
2. Remove duplicates from `/public/punks-display/` only
3. Regenerate `/public/punk-names.json` from display directory
4. Update website code to use `/public/punks-display/`
5. Final count will be fewer than 203 (display-ready honoraries only)
