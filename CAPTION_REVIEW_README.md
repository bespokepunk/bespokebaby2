# Caption Review Interface

## Quick Start

Run this command:
```bash
python review_final_captions.py
```

A browser window will open with the review interface.

---

## Features

### 1. **View Images & Final Captions**
- See each image with its current final caption
- View original caption for reference
- Track progress (approved/modified/pending)

### 2. **Edit Captions**
- Edit captions directly in the text box
- Add feedback notes explaining your changes
- Changes auto-save to the .txt files

### 3. **Navigation**
- **Previous/Next**: Browse through all images
- **Jump to Pending**: Skip to next unreviewed image
- **Approve**: Mark caption as good (no changes needed)
- **Save Modified**: Save your edits and move to next

### 4. **Track Progress**
- ✅ **Approved**: Caption is perfect, no changes
- ✏️ **Modified**: Caption was edited
- ⏳ **Pending**: Not yet reviewed

### 5. **Export Feedback**
- Click "Export Feedback for Regeneration"
- Creates `caption_feedback_for_regeneration.json`
- Contains all your edits and notes for analysis

---

## Workflow

1. **Review** the image and caption
2. **Choose one:**
   - ✅ Approve if perfect
   - ✏️ Edit caption + add feedback, then Save Modified
3. **Repeat** until all done
4. **Export** feedback when finished

---

## Files Created

- `caption_review_status.json` - Tracks your review progress
- `caption_feedback_for_regeneration.json` - Your edits for analysis
- `civitai_v2_7_training/*.txt` - Caption files (updated with your edits)

---

## Tips

- **Feedback box**: Explain WHY you changed something (helps improve the caption generator)
- **Jump to Pending**: Quickly find items you haven't reviewed yet
- **Progress stats**: Always visible at the top

---

## Resume Reviewing

The system saves your progress automatically. If you close the browser:

1. Just run `python review_final_captions.py` again
2. Your progress is preserved
3. Continue where you left off
