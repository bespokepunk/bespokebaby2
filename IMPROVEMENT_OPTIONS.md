# Options for Improving 24×24 Output Quality

**Date**: November 9, 2025
**Current Status**: 512×512 → 24×24 outputs have correct composition but **colors/shapes still not accurate** to original Bespoke Punks

---

## Option 1: Post-Processing (Quick Fix) ⚡

**Status**: IN PROGRESS
**Time**: 30-60 minutes
**Cost**: Free

### What It Does
Apply post-processing to existing 24×24 outputs to make them more pixel-art-like:
1. **Color quantization** - Reduce to limited palette (8-16 colors like originals)
2. **Edge sharpening** - Make pixel boundaries crisp
3. **Posterization** - Reduce color gradations

### Pros
- Quick to test
- Uses existing trained models
- No additional training cost
- Reversible (can always go back to originals)

### Cons
- Only improves existing outputs, doesn't fix fundamental model issues
- May not solve all color/shape problems
- Post-processing is a "band-aid" not a real fix

### Implementation
- Script: `postprocess_pixel_perfect.py`
- Tests 4 different color palette sizes (8, 10, 12, 16 colors)
- Generates before/after comparisons

---

## Option 2: More Training with Better Captions (Medium Effort) 🔄

**Status**: PENDING
**Time**: 1-2 hours (caption update) + 45 min (training on RunPod)
**Cost**: ~$0.60-0.80 per training run

### What It Does
Re-train the model with improved captions that emphasize pixel art constraints:
- Update captions to explicitly mention "limited color palette"
- Add "geometric pixel art" descriptions
- Emphasize "sharp pixel boundaries", "blocky style"
- Train for 5-10 epochs instead of 3

### Example Caption Updates

**Before**:
```
pixel art, portrait of bespoke punk, green solid background, black hair, blue eyes, light skin
```

**After**:
```
pixel art portrait, limited 8-color palette, sharp pixel boundaries, geometric simplified style, bespoke punk character, solid green background, black blocky hair, blue square eyes, light tan skin, 24x24 resolution style
```

### Pros
- Addresses root cause (model needs to learn stricter constraints)
- Uses proven 512×512 method that already works
- Can test on RunPod quickly
- Might dramatically improve quality

### Cons
- Requires manual caption updates (203 files)
- Costs money for each training run
- No guarantee it will work
- Might need multiple iterations to get right

### Implementation Steps
1. Update all 203 caption files with enhanced descriptions
2. Upload new captions to RunPod
3. Train for 5-10 epochs (longer training)
4. Test and compare to previous results

---

## Option 3: Different Approach Entirely (High Effort) 🔬

**Status**: PENDING
**Time**: Days to weeks
**Cost**: Variable (free to expensive depending on approach)

### Approach 3A: Hybrid AI + Manual Touch-Up
- Use current model as "draft generator"
- Manually edit in pixel art editor (Aseprite, etc.)
- Build library of hand-touched versions
- **Pros**: Guaranteed quality
- **Cons**: Not scalable, labor intensive

### Approach 3B: Different Model Architecture
- Try **GAN-based pixel art generators** (no VAE limitations)
- Look for **pixel-art-specific models** (PixelCNN, etc.)
- Custom architecture trained specifically for 24×24
- **Pros**: Could work natively at 24×24
- **Cons**: Requires ML expertise, significant R&D time

### Approach 3C: Advanced Post-Processing Pipeline
- Extract original Bespoke Punk color palettes (from all 203)
- Build "style transfer" post-processor
- Use dithering algorithms specifically for pixel art
- Implement edge detection + hard boundary snapping
- **Pros**: One-time setup, works on any SD output
- **Cons**: Complex to implement, might not preserve details

### Approach 3D: Revisit SD-piXL or Similar
- Previous attempts with SD-piXL had issues
- Try different configurations or newer pixel art models
- Explore ControlNet for pixel art specifically
- **Pros**: Purpose-built for pixel art
- **Cons**: Already tried, had technical issues

---

## Recommendation: Sequential Testing

### Phase 1 (Now): Option 1 - Post-Processing
Test if post-processing can salvage current outputs
- **IF GOOD ENOUGH**: Ship it, done
- **IF NOT GOOD ENOUGH**: Proceed to Phase 2

### Phase 2 (If needed): Option 2 - Better Captions
Update captions and retrain for 5-10 epochs
- **IF GOOD ENOUGH**: Ship it, done
- **IF NOT GOOD ENOUGH**: Proceed to Phase 3

### Phase 3 (If needed): Option 3 - Different Approach
Research and test alternative methods
- Likely requires significant time investment
- May need to pivot strategy entirely

---

## Success Criteria

An output is "good enough" if:
1. ✅ Limited color palette (5-15 colors per character)
2. ✅ Sharp pixel boundaries (no antialiasing or blending)
3. ✅ Matches general Bespoke Punk aesthetic
4. ✅ Recognizable features (eyes, hair, accessories)
5. ✅ Solid backgrounds (single colors, no gradients)
6. ✅ Geometric simplification appropriate for 24×24

---

## Current Status

**Completed**:
- RunPod training at 512×512 (3 epochs)
- Test generations with 3 downscaling methods
- Identified NEAREST neighbor as best downscaling method

**In Progress**:
- Option 1: Post-processing script created, testing now

**Next Steps**:
1. Review post-processed outputs
2. Decide if quality is acceptable or if Option 2 is needed
3. If Option 2: Begin caption enhancement work
