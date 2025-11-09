# ⚠️ BEFORE NEXT TRAINING - Action Items

**IMPORTANT:** Complete these tasks before running the next training session.

---

## 🔴 Critical: Add Missing OG Images

### Why This Matters
OG (original) images are the "before" versions of your punks - the source images before they were converted to 24x24 pixel art. Having these is important for:
- Documentation and archival
- Showing transformation process
- Quality control and comparison
- Future reference

### Current Status
- **Total Punks:** 203
- **OG Images Available:** 152
- **Missing OG Images:** 52 (including 10 new punks)

---

## 📋 Missing OG Images List

### Priority 1: New Punks (10 Missing) - MOST RECENT

These were just added and you likely have the originals somewhere:

1. **lad_047_CYGAAR1**
2. **lad_049_gainzyyyy12**
3. **lad_049_gainzyyyy18**
4. **lad_061_DOPE10**
5. **lad_061_DOPE9**
6. **lad_103_merheb3**
7. **lad_105_inkspired**
8. **lad_106_sultan**
9. **lady_083_Marianne3**
10. **lady_099_domino**

### Priority 2: Older Punks (42 Missing)

See full list in: `RECONCILIATION_REPORT.md`

---

## 🔍 Where to Look for OG Images

### Check These Locations:

1. **Downloads Folder**
   ```bash
   ls ~/Downloads/*.{png,jpg,jpeg} | grep -i "punk\|bespoke\|lady\|lad"
   ```

2. **Desktop**
   ```bash
   ls ~/Desktop/*.{png,jpg,jpeg}
   ```

3. **Pictures/Screenshots**
   ```bash
   ls ~/Pictures/*.{png,jpg,jpeg}
   ls ~/Pictures/Screenshots/*.{png,jpg,jpeg}
   ```

4. **Project Folders**
   - Check any source folders where you created these
   - Look in old project directories
   - Search email attachments

5. **Cloud Storage**
   - iCloud Photos
   - Google Drive
   - Dropbox
   - OneDrive

### Search Command (Mac/Linux)
```bash
# Search entire home directory for potential OG images
find ~ -name "*lad_047*" -o -name "*lad_049*" -o -name "*lad_061*" \
       -o -name "*lad_103*" -o -name "*lad_105*" -o -name "*lad_106*" \
       -o -name "*lady_083*" -o -name "*lady_099*" 2>/dev/null
```

---

## 📥 How to Add OG Images When Found

### Naming Convention
Original images should be named: `[punk_name]OG.[extension]`

**Examples:**
- `lad_106_sultanOG.png`
- `lady_099_dominoOG.jpg`
- `lad_047_CYGAAR1OG.png`

### Where to Put Them
```bash
# Copy to the OG folder
cp /path/to/original/image.png FORTRAINING6/bespokepunksOG/[punk_name]OG.png
```

**Example:**
```bash
cp ~/Downloads/sultan_original.png FORTRAINING6/bespokepunksOG/lad_106_sultanOG.png
```

---

## ✅ Verification Checklist

Before next training, verify:

### 1. Count Check
```bash
# Should equal number of processed punks (203)
ls FORTRAINING6/bespokepunks/*.png | wc -l
ls FORTRAINING6/bespokepunksOG/* | wc -l
```

### 2. Missing OG Images Report
```bash
# Run this to see what's still missing
cd /Users/ilyssaevans/Documents/GitHub/bespokebaby2
ls -1 FORTRAINING6/bespokepunks/*.png | xargs -n1 basename | sed 's/.png$//' | sort > /tmp/all_punks.txt
ls -1 FORTRAINING6/bespokepunksOG/* | xargs -n1 basename | sed 's/OG.*//' | sort | uniq > /tmp/og_punks.txt
comm -23 /tmp/all_punks.txt /tmp/og_punks.txt
```

### 3. Visual Verification
Spot-check a few OG images to ensure they match their processed versions:
```bash
open FORTRAINING6/bespokepunks/lad_106_sultan.png
open FORTRAINING6/bespokepunksOG/lad_106_sultanOG.png
```

---

## 🎯 Next Training Preparation

### Once OG Images Are Added:

1. **Update Dataset Count**
   - Should have 203 punks with matching OG images
   - Update documentation

2. **Create New Training Package**
   ```bash
   # Package for next training run
   zip -r bespoke_punk_training_v2_203.zip FORTRAINING6/bespokepunks FORTRAINING6/bespokepunktext
   ```

3. **Document Changes**
   - Update `RECONCILIATION_REPORT.md`
   - Note which OG images were added
   - Mark as ready for training v2.0

---

## 📝 If OG Images Can't Be Found

For punks where originals are truly lost:

### Option 1: Document as "No OG Available"
Create a placeholder or note file:
```bash
echo "No original image available" > FORTRAINING6/bespokepunksOG/lad_106_sultan_NO_OG.txt
```

### Option 2: Accept Incomplete Collection
It's okay if some OG images are missing - they're for reference only and don't affect training quality.

### Option 3: Upscale as Proxy
If needed, you could upscale the 24x24 pixel art as a proxy OG:
```bash
# This is NOT ideal but better than nothing
# Use nearest-neighbor to preserve pixels
```

---

## 🚨 REMINDER TRIGGERS

### When to Check This File:

- ✅ **Before starting next CivitAI training**
- ✅ **Before creating new training package**
- ✅ **When organizing dataset for archival**
- ✅ **When preparing for training v2.0**

### Quick Check Command:
```bash
# Add this to your .bashrc or .zshrc
alias check-og='echo "Missing OG images:" && comm -23 <(ls -1 FORTRAINING6/bespokepunks/*.png | xargs -n1 basename | sed "s/.png$//" | sort) <(ls -1 FORTRAINING6/bespokepunksOG/* | xargs -n1 basename | sed "s/OG.*//" | sort | uniq) | wc -l'
```

---

## 📊 Progress Tracker

**Current Status:**
- [ ] Found OG images for 10 new punks
- [ ] Verified naming convention
- [ ] Copied to bespokepunksOG folder
- [ ] Ran verification count
- [ ] Updated reconciliation report
- [ ] Ready for training v2.0

**Target:**
- Goal: At least find the 10 NEW punk OG images
- Ideal: Find all 52 missing OG images
- Minimum: Document which ones are unavailable

---

## 💡 Tips for Finding Lost Images

1. **Check file creation dates** around when you made the punks
2. **Search by file size** (OG images likely larger than 24x24)
3. **Look in Trash/Recently Deleted**
4. **Check source applications** (Photoshop, Figma, etc. auto-save folders)
5. **Review messaging apps** if you shared images with collaborators
6. **Check version control** if project was in git
7. **Look at Time Machine backups** (Mac)

---

## 🎯 Summary

**BEFORE next training, you MUST:**

1. ✅ Test current models (epochs 5, 7, 10)
2. ✅ Choose best checkpoint
3. ⚠️ **FIND AND ADD OG IMAGES** (especially 10 new punks)
4. ✅ Verify dataset completeness
5. ✅ Package for training v2.0

**Priority Action:**
```bash
# Start by searching for the 10 newest punk OG images
# They're the most recent so you likely still have them!
```

---

**Created:** November 8, 2025
**Priority:** HIGH
**Due:** Before next training run
**Estimated Time:** 30-60 minutes to find and organize
