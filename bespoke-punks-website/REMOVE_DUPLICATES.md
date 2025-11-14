# Duplicate Audit Instructions

## How to Tell Me Which Punks to Remove

Review the full list in `AUDIT_LIST.txt` and tell me which ones to remove.

I'll look for patterns like:
- **Variants with numbers:** `lad_023_x`, `lad_023_x-2`, `lad_023_x-3`, `lad_023_x-4` (probably keep one?)
- **Multiple versions:** `lad_103_merheb`, `lad_103_merheb2`, `lad_103_merheb3` (keep which one?)
- **Duplicate IDs:** `lad_021_x`, `lad_022_x`, `lad_024_x`, `lad_025_x` (are these placeholders?)

## Format Your Response

Tell me in any format, such as:
- "Remove all the x-2, x-3, x-4 variants"
- "Keep merheb3, remove merheb and merheb2"
- "Remove lad_021 through lad_025 (the x ones)"
- Or just list the specific filenames to delete

## What I'll Do

1. Delete the specified files from `/public/punks-display/` ONLY
2. Keep originals in `/public/punks/` (training data safe)
3. Regenerate `punk-names.json` from the cleaned display directory
4. Update website to use display directory
5. Show you the final count

## Current Suspected Duplicates

Based on quick scan, these look like potential duplicates/variants:

**lad_023 variants:**
- lad_023_x
- lad_023_x-2
- lad_023_x-3
- lad_023_x-4

**merheb variants:**
- lad_103_merheb
- lad_103_merheb2
- lad_103_merheb3

**bunya variants:**
- lad_102_bunya
- lad_102_bunya2
- lad_102_bunya3

**Placeholder x's:**
- lad_021_x
- lad_022_x
- lad_024_x
- lad_025_x
- lad_036_x

**lady variants to check:**
- lady_044_x through lady_058_x
- lady_062_Dalia vs lady_062_Dalia-2, lady_062_Dalia-BD
- lady_065_miggs vs lady_065_miggs-4
- lady_099_VQ vs lady_099_domino

Ready for your audit! Tell me which ones to remove.
