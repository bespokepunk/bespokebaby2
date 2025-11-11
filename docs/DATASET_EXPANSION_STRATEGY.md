# Dataset Expansion Strategy: Using Generated Images as Training Data

## Overview

We have 203 original (OG) images that serve as our ground truth. Using SD15_PERFECT and other high-quality models, we've generated variations of these images with:
- Different backgrounds
- Additional accessories (crowns, necklaces, earrings)
- Different traits and features
- Variations in color schemes

**Proposal:** Add these 203 generated images to the training dataset, effectively expanding from 203 → 406 images.

## Rationale

### ✅ Advantages

**1. Controlled Dataset Expansion**
- We have 100% authentic, accurate outputs for all 203 OG images (ground truth)
- Generated variations provide diversity while maintaining quality standards
- Doubles dataset size without manual creation overhead

**2. Quality Convergence Assessment**
- OG images: Can measure EXACT accuracy (pixel-perfect comparisons)
- Generated images: Represent desired output variations
- Enables measuring: "How close to OG?" vs "How close to desired variations?"

**3. Data Efficiency**
- Hypothesis Generator ranked "Expand dataset to 300+" as LOW priority (40% confidence)
- Reason: Creating 150+ NEW images manually is expensive
- Solution: Use already-generated high-quality images

**4. Style Consistency**
- Generated images already match desired pixel art style (from SD15_PERFECT)
- Provides training signal for "good variations" vs "bad variations"
- May reduce training time to achieve quality convergence

### ⚠️ Risks and Considerations

**1. Model Collapse / Overfitting**
- Risk: Training on model-generated images can reinforce existing biases
- Mitigation: OG images remain as ground truth anchor
- Mitigation: Use different prompts/variations, not identical repeats

**2. Caption Quality**
- Question: Do we have accurate captions for the 203 generated images?
- Need: Verify captions match actual image content (accessories, backgrounds, etc.)
- Risk: Incorrect captions could harm training more than help

**3. Background Color Confusion**
- Issue: Generated images may have WRONG backgrounds (like our current model)
- Risk: Training on wrong backgrounds could reinforce the error
- Solution: Only use generated images with CORRECT backgrounds, or
- Solution: Re-caption generated images with ACTUAL background colors (not expected)

**4. Quality Validation**
- Question: Are all 203 generated images high quality (8+/10)?
- Need: Filter out low-quality generated images before adding to dataset
- Process: Manual review or automated quality scoring

## Proposed Implementation Strategy

### Phase 1: Quality Assessment (Before Adding to Dataset)

```bash
# 1. Review generated images
# - Verify backgrounds are correct OR
# - Re-caption with actual background colors

# 2. Quality filter
# - Only include generated images with quality score 8+/10
# - Ensure pixel art style matches OG images
# - Verify accessories/traits are clearly visible

# 3. Caption validation
# - Check captions match actual image content
# - Update captions if needed (especially background colors)
```

### Phase 2: Dataset Structure

```
training_data/
├── 203_original/          # OG images (ground truth - 100% weight)
│   ├── image_001.png
│   ├── image_001.txt      # Original accurate captions
│   └── ...
├── 203_generated/         # Generated variations (diversity weight)
│   ├── image_001_var.png
│   ├── image_001_var.txt  # Captions matching ACTUAL content
│   └── ...
```

### Phase 3: Training Configuration

**Option A: Equal Weight (Simple)**
```toml
train_data_dir = "/workspace/training_data"  # All 406 images
# Both datasets weighted equally
```

**Option B: Weighted Dataset (Recommended)**
```toml
# OG images: Higher weight (ground truth)
# Generated images: Lower weight (diversity/variation)

# This requires custom dataset weighting in Kohya
# May need to duplicate OG images 2x or use custom loss weights
```

**Option C: Sequential Training (Conservative)**
```
1. Train Epochs 1-5 on OG images only (203 images)
2. Train Epochs 6-10 on combined dataset (406 images)
3. Allows model to learn basics before introducing variations
```

## Quality Convergence Metrics

With 203 OG images as ground truth, we can measure:

### 1. Exact Accuracy (OG Images Only)
```python
def measure_og_accuracy(generated, og_image):
    """
    Pixel-perfect comparison to ground truth
    """
    return {
        "background_exact_match": compare_background(generated, og_image),
        "hair_color_exact_match": compare_hair(generated, og_image),
        "accessory_presence": compare_accessories(generated, og_image),
        "overall_similarity": structural_similarity(generated, og_image)
    }
```

### 2. Variation Quality (Generated Images)
```python
def measure_variation_quality(generated, variation_image):
    """
    How well model reproduces intended variations
    """
    return {
        "style_consistency": pixel_art_style_match(generated, variation_image),
        "variation_accuracy": variation_features_match(generated, variation_image),
        "quality_preservation": quality_score(generated)
    }
```

### 3. Convergence Timeline
```
Epoch 1-3: Measure OG image accuracy (baseline)
Epoch 4-6: Measure variation accuracy (generalization)
Epoch 7-10: Measure overall quality convergence

Success Criteria:
- OG images: 95%+ exact match by Epoch 7
- Variations: 90%+ style consistency by Epoch 7
- Overall quality: 8+/10 by Epoch 7
```

## Decision Matrix

| Scenario | Risk | Reward | Recommendation |
|----------|------|--------|----------------|
| **Use all 203 generated images** | Medium | High | ⚠️ Only if quality-filtered and re-captioned |
| **Use only high-quality subset (e.g., 50-100 images)** | Low | Medium | ✅ Safe approach for first experiment |
| **Sequential training (OG first, then combined)** | Low | Medium | ✅ Recommended for conservative approach |
| **Don't use generated images yet** | None | None | ⏸️ Wait until keep_tokens=3 training completes |

## Recommended Next Steps

### Step 1: Validate Generated Images (Manual Review)
```bash
# 1. Check a sample (20-30 images) from the 203 generated set
# 2. Verify:
#    - Backgrounds are correct (or can be accurately re-captioned)
#    - Quality is 8+/10
#    - Accessories match captions
#    - Pixel art style is consistent
```

### Step 2: Re-Caption Generated Images
```bash
# For each generated image:
# 1. Identify ACTUAL background color (not expected)
# 2. List ACTUAL accessories present
# 3. Write accurate caption matching visible content
#
# Example:
# Original caption: "bespoke baby, lady, pink hair, crown, green background"
# If background is actually purple:
# New caption: "bespoke baby, lady, pink hair, crown, purple background"
```

### Step 3: Quality Filter
```bash
# Only include generated images that meet criteria:
# - Clear pixel art style
# - Visible and accurate features
# - 8+/10 quality score (subjective or automated)
# - Matching caption
```

### Step 4: Test with Small Subset First
```bash
# Training Run: SD15_KEEP_TOKENS_3_PLUS_50_GENERATED
# Dataset: 203 OG + 50 best generated = 253 images
# Purpose: Validate approach before full expansion
# Success: Compare convergence vs SD15_KEEP_TOKENS_3 (203 OG only)
```

## Expected Timeline

**Immediate (After keep_tokens=3 completes):**
1. Review generated images (1-2 hours)
2. Re-caption 50-100 best images (2-3 hours)
3. Test training with small subset (10 epochs = ~2 hours GPU time)

**Short-term (If successful):**
1. Re-caption all 203 generated images
2. Full training run with 406 images
3. Compare quality convergence metrics

**Long-term (Dataset expansion):**
1. Generate additional variations with keep_tokens=3 model
2. Continue expanding dataset with high-quality outputs
3. Establish continuous improvement loop

## Success Metrics

The dataset expansion will be considered successful if:

✅ **Quality:** Model maintains 8+/10 quality with expanded dataset
✅ **Convergence:** Reaches quality faster (e.g., Epoch 5 vs Epoch 7)
✅ **Variety:** Generates more diverse outputs for similar prompts
✅ **Stability:** No training oscillation or quality degradation
✅ **OG Accuracy:** Still achieves 95%+ accuracy on OG images

## Conclusion

**Recommendation:** Proceed with dataset expansion AFTER keep_tokens=3 training completes successfully.

**First step:** Review and re-caption 50-100 best generated images, then test with small expansion (203 OG + 50 generated).

**If successful:** Expand to full 406-image dataset for next training run.

**If unsuccessful:** Continue with OG images only and explore other optimization strategies (conv_dim, learning rate, etc.).

---

**Status:** 📋 Proposal - Awaiting keep_tokens=3 results and manual image review
