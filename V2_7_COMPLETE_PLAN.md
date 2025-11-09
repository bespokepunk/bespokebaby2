# V2.7 Complete Implementation Plan

## Status: IN PROGRESS
Before regenerating ALL training captions, we need to complete V2.7 with:

---

## ✅ COMPLETED FEATURES

### 1. Eye Color Detection
- **Status**: COMPLETE (but model needs retraining)
- Narrower eye region (38-42% instead of 35-45%)
- Skin tone filtering
- Darkest saturated color selection
- **Issue**: Model still generates wrong colors due to training data

### 2. Color-to-Feature Mapping
- **Status**: COMPLETE
- Changed from "using colors X, Y, Z" to "orange clothing with gray accents"
- Maps colors to specific features (clothing, highlights, shadows)
- Removes generic color lists

---

## ⏳ INCOMPLETE FEATURES (BLOCKING CAPTION REGEN)

### 3. Accessory Detection
**Status**: NOT IMPLEMENTED
**Priority**: CRITICAL

**Required Detection:**
```python
def detect_accessories(self):
    """
    Detect accessories in specific image regions:
    - Sunglasses: Dark uniform region covering eyes (38-42% height)
    - Earrings: Bright/shiny spots at ear positions (45-55% height, 10-25% and 75-90% width)
    - Hats/headwear: Distinct shapes in top 15% of image
    - Necklaces: Bright line at neck area (55-60% height)
    """
    accessories = []

    # Sunglasses detection
    eye_region = self.image_array[int(self.height * 0.38):int(self.height * 0.42), :]
    if self.is_wearing_sunglasses(eye_region):
        accessories.append("sunglasses")
        # IMPORTANT: Skip eye color detection if sunglasses present

    # Earring detection
    left_ear = self.image_array[int(self.height * 0.45):int(self.height * 0.55), :int(self.width * 0.25)]
    right_ear = self.image_array[int(self.height * 0.45):int(self.height * 0.55), int(self.width * 0.75):]

    if self.has_bright_accent(left_ear) or self.has_bright_accent(right_ear):
        accessories.append("earrings")

    # Hat detection
    top_region = self.image_array[:int(self.height * 0.15), :]
    if self.has_hat(top_region):
        accessories.append("hat")

    return accessories
```

**Example Outputs:**
- "wearing gold-framed sunglasses"
- "gold hoop earrings"
- "black hat"

---

### 4. Hair Style Detection
**Status**: PARTIALLY IMPLEMENTED (only texture: curly/wavy/fluffy)
**Priority**: CRITICAL

**Required Hair Styles:**
Based on training data, detect:
- ✅ Texture: curly, wavy, straight, fluffy (already done)
- ❌ **Specific styles:**
  - `braided` - rope-like vertical patterns, distinct segments
  - `bun` - concentrated mass at top/back of head
  - `ponytail` - hair pulled to one side/back
  - `dreadlocks` - multiple thick vertical segments
  - `afro` - large spherical volume
  - `short cropped` - minimal hair region
  - `slicked back` - smooth, pulled back appearance

**Implementation:**
```python
def detect_hair_style(self):
    """
    Detect specific hair styles using pattern analysis
    """
    hair_region = self.image_array[:int(self.height * 0.4), :]

    # Check for braids (rope-like patterns)
    if self.has_braid_pattern(hair_region):
        return "braided"

    # Check for bun (concentrated top/back mass)
    if self.has_bun_shape(hair_region):
        return "bun"

    # Check for ponytail (asymmetric distribution)
    if self.has_ponytail_pattern(hair_region):
        return "ponytail"

    # Fallback to texture-based description
    return self.analyze_hair_region()['texture']
```

---

### 5. Gender Detection (Lad/Lady)
**Status**: PARTIALLY IMPLEMENTED (but inaccurate)
**Priority**: HIGH

**Current Issue:**
`lad_001_carbon.png` was detected as "lady" - wrong!

**Improved Detection:**
```python
def detect_gender_accurate(self):
    """
    Accurate lad/lady detection:
    1. Check filename prefix first (lad_* or lady_*)
    2. If no filename hint, use heuristics:
       - Hair length
       - Accessories (earrings strongly suggest lady)
       - Color palette
    """
    # First try filename
    filename = Path(self.image_path).stem
    if filename.startswith('lad_'):
        return "lad"
    elif filename.startswith('lady_'):
        return "lady"

    # Fallback to heuristics
    hair_info = self.analyze_hair_region()
    accessories = self.detect_accessories()

    female_score = 0
    if hair_info['length'] == 'long':
        female_score += 1
    if 'earrings' in accessories:
        female_score += 3  # Strong indicator
    if hair_info['volume'] in ['large voluminous', 'voluminous']:
        female_score += 1

    return "lady" if female_score >= 3 else "lad"
```

---

### 6. Caption Validation System
**Status**: NOT IMPLEMENTED
**Priority**: MEDIUM (nice to have)

**Purpose:**
Auto-validate generated captions against images to catch errors

**Features:**
```python
def validate_caption(image_path, caption):
    """
    Validate caption accuracy:
    - Check if detected accessories match visual features
    - Verify hair style description matches image
    - Flag suspicious detections (e.g., "sunglasses" but eyes visible)
    """
    issues = []

    # Check for contradictions
    if "sunglasses" in caption and can_see_eyes_clearly(image_path):
        issues.append("WARNING: Sunglasses detected but eyes clearly visible")

    if "braided" in caption and not has_braid_pattern(image_path):
        issues.append("WARNING: Braided hair detected but no braid pattern found")

    return issues
```

---

## IMPLEMENTATION ORDER

### Step 1: Add Accessory Detection to V2.7 ✅
1. Add `detect_accessories()` method
2. Add `is_wearing_sunglasses()` helper
3. Add `has_bright_accent()` for earrings
4. Add `has_hat()` for headwear
5. **IMPORTANT**: Skip eye detection if sunglasses present
6. Include accessories in prompt: "wearing gold sunglasses, hoop earrings"

### Step 2: Improve Hair Style Detection ✅
1. Add `detect_specific_hair_style()` method
2. Implement braid pattern detection
3. Implement bun shape detection
4. Implement ponytail detection
5. Update prompt to use specific styles

### Step 3: Fix Gender Detection ✅
1. Check filename first (`lad_*` or `lady_*`)
2. Use improved heuristics as fallback
3. Give heavy weight to earrings (strong lady indicator)

### Step 4: Test V2.7 Complete ✅
1. Test on Marianne punk (braided hair, sunglasses, earrings)
2. Test on a lad (verify correct gender)
3. Test on various hair styles
4. Verify all features work together

### Step 5: Regenerate ALL Captions ✅
1. Run caption regeneration script with complete V2.7
2. Save to `FORTRAINING6/bespokepunktext/`
3. Spot-check 10-20 captions for accuracy
4. Copy to `FORTRAINING6/bespokepunks/` for training

### Step 6: Retrain Model ✅
1. Use updated captions
2. Train for 3-5 epochs
3. Test generation
4. Verify eye colors now correct

---

## EXPECTED CAPTION FORMAT (Complete V2.7)

**Example 1 - Marianne Punk:**
```
pixel art, 24x24, portrait of bespoke punk lady,
long braided black hair, wearing gold-framed sunglasses,
gold hoop earrings, brown skin, white turtleneck,
pink-to-green gradient background (#ff69b4 to #00ff00),
dark shadows, sharp pixel edges, hard color borders,
retro pixel art style
```

**Example 2 - Lad:**
```
pixel art, 24x24, portrait of bespoke punk lad,
short black hair, brown eyes, tan skin,
blue solid background (#0000ff), orange clothing,
white highlights, sharp pixel edges, hard color borders,
retro pixel art style
```

---

## SUCCESS CRITERIA

Before retraining:
- [ ] Sunglasses correctly detected (and eye detection skipped)
- [ ] Earrings correctly detected
- [ ] Hair styles accurate (braided, bun, ponytail, etc.)
- [ ] Gender always correct (lad/lady)
- [ ] All 200+ captions generated and spot-checked
- [ ] No obvious errors in sample review

After retraining:
- [ ] Eye colors match input (brown → brown, NOT green)
- [ ] Hair styles match input
- [ ] Accessories appear in generation
- [ ] Overall quality improved

---

##Next Action
Implement accessory detection + hair style detection + gender fix in V2.7, THEN regenerate captions.
