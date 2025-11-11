# Adaptive Epoch Selection System - Design Doc

**Date:** 2025-11-10
**Status:** 🚧 IN DEVELOPMENT
**Priority:** HIGH - Production Enhancement

---

## Executive Summary

**Core Concept:** Instead of using a single "best" epoch for all images, **dynamically route to the epoch best suited for each specific uploaded image** based on detected characteristics.

**Why This Matters:**
- Different epochs have different strengths (hats vs sunglasses vs backgrounds)
- One-size-fits-all approach leaves quality on the table
- User images have vastly different characteristics
- We have 8-10 trained epochs sitting unused

---

## System Architecture

### Component 1: Image Analysis on Upload
```python
def analyze_uploaded_image(user_image):
    """
    Analyze uploaded image to determine optimal generation strategy

    Returns:
        {
            'has_glasses': bool,
            'has_hat': bool,
            'has_earrings': bool,
            'has_bow': bool,
            'complexity': 'simple' | 'medium' | 'complex',
            'background_type': 'solid' | 'gradient' | 'complex',
            'num_accessories': int,
            'face_clarity': float (0-1),
            'dominant_colors': List[str],
            'skin_tone_category': str,
            'hair_coverage': 'bald' | 'short' | 'medium' | 'long'
        }
    """
```

### Component 2: Epoch Specialization Database
```python
EPOCH_SPECIALIZATIONS = {
    # Based on CAPTION_FIX experiment systematic testing
    'epoch_5': {
        'strengths': ['solid_backgrounds', 'simple_portraits', 'earrings'],
        'avg_colors': 238.9,
        'best_for': {
            'solid_background': 0.95,  # confidence score
            'earrings': 0.80,
            'simple_portrait': 0.85
        },
        'issues': ['complex_accessories', 'multiple_features']
    },
    'epoch_7': {
        'strengths': ['general_purpose', 'sunglasses', 'balanced'],
        'avg_colors': 296.0,
        'best_for': {
            'sunglasses': 0.90,
            'general': 0.80,
            'multiple_accessories': 0.75
        },
        'issues': ['can_be_noisy']
    },
    'epoch_8': {
        'strengths': ['cleanest', 'minimal_noise', 'simple_features'],
        'avg_colors': 216.6,
        'best_for': {
            'simple_portrait': 0.95,
            'clean_output': 0.90,
            'no_accessories': 0.85
        },
        'issues': ['may_struggle_with_complex_accessories']
    }
    # ... populate from systematic testing
}
```

### Component 3: Routing Logic
```python
def select_optimal_epoch(image_features, epoch_specializations):
    """
    Score each epoch based on detected features
    Return best match with confidence score
    """
    scores = {}

    for epoch, specs in epoch_specializations.items():
        score = 0.0

        # Score based on accessory matches
        if image_features['has_sunglasses'] and 'sunglasses' in specs['strengths']:
            score += specs['best_for'].get('sunglasses', 0)

        # Score based on complexity
        if image_features['complexity'] == 'simple':
            score += specs['best_for'].get('simple_portrait', 0)

        # Score based on background
        if image_features['background_type'] == 'solid':
            score += specs['best_for'].get('solid_background', 0)

        scores[epoch] = score

    # Return best epoch and runner-up
    sorted_epochs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return {
        'primary': sorted_epochs[0],
        'backup': sorted_epochs[1],
        'all_scores': scores
    }
```

### Component 4: Dynamic Parameter Adjustment
```python
def adjust_generation_params(image_features, selected_epoch):
    """
    Fine-tune generation parameters based on image complexity
    """
    params = {
        'guidance_scale': 7.5,
        'num_inference_steps': 30,
        'lora_scale': 1.0
    }

    # Complexity adjustments
    if image_features['complexity'] == 'high':
        params['num_inference_steps'] = 50
        params['guidance_scale'] = 8.5
    elif image_features['complexity'] == 'simple':
        params['num_inference_steps'] = 25
        params['guidance_scale'] = 7.0

    # Accessory emphasis
    if image_features['num_accessories'] >= 2:
        params['guidance_scale'] += 0.5  # Emphasize details

    # Epoch-specific tuning
    if selected_epoch == 'epoch_8':
        params['guidance_scale'] -= 0.5  # Already clean

    return params
```

### Component 5: User Feedback Collection
```python
def collect_user_feedback(generation_result, user_rating):
    """
    Log user satisfaction to improve routing over time

    Store:
    - Image features detected
    - Epoch selected
    - Parameters used
    - User rating (1-5 stars)
    - Specific issues flagged
    - Timestamp
    """
    feedback_entry = {
        'timestamp': datetime.now(),
        'image_features': generation_result['detected_features'],
        'epoch_used': generation_result['epoch'],
        'params': generation_result['params'],
        'user_rating': user_rating,
        'unique_colors': generation_result['color_count'],
        'generation_time': generation_result['time_ms']
    }

    # Save to Supabase
    save_to_database(feedback_entry)

    # Update routing weights
    update_epoch_weights(feedback_entry)
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
1. ✅ Design system architecture
2. 🚧 Implement image analysis (accessory detection, complexity)
3. ⏳ Create epoch database structure
4. ⏳ Build basic routing logic

### Phase 2: Systematic Testing (Week 1-2)
1. Test CAPTION_FIX Epochs 1-10 with:
   - 20 images with sunglasses
   - 20 images with hats
   - 20 images with earrings
   - 20 simple portraits
   - 20 complex backgrounds

2. For each epoch, measure:
   - Accessory accuracy (manual inspection)
   - Average unique colors
   - Visual quality score (1-10)
   - Failure modes

3. Build comprehensive specialization database

### Phase 3: Production Integration (Week 2)
1. Integrate into Gradio app
2. Load multiple epochs (3-5 most useful)
3. Implement dynamic routing
4. Add user feedback UI
5. Deploy and monitor

### Phase 4: Continuous Improvement (Ongoing)
1. Collect user feedback
2. Analyze routing performance
3. Adjust weights and thresholds
4. A/B test routing strategies
5. Add new epochs (Phase 1B, etc)

---

## Data Collection Requirements

### For Each Epoch:
- [ ] Test with 100 diverse images
- [ ] Score on 10 criteria (0-10 scale)
- [ ] Identify 3-5 key strengths
- [ ] Identify 3-5 key weaknesses
- [ ] Measure avg unique colors
- [ ] Measure generation consistency

### User Feedback Schema:
```sql
CREATE TABLE generation_feedback (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    user_id TEXT,

    -- Input
    image_features JSONB,
    prompt_generated TEXT,

    -- Generation
    epoch_selected TEXT,
    epoch_scores JSONB,
    params_used JSONB,

    -- Output
    output_image_url TEXT,
    unique_colors INTEGER,
    generation_time_ms INTEGER,

    -- Feedback
    user_rating INTEGER,  -- 1-5 stars
    accessory_accurate BOOLEAN,
    skin_tone_accurate BOOLEAN,
    hair_color_accurate BOOLEAN,
    background_accurate BOOLEAN,
    overall_satisfaction TEXT,

    -- Metadata
    model_version TEXT,
    app_version TEXT
);
```

---

## User Interface Enhancements

### Option 1: Transparent (Show User the Selection)
```
┌─────────────────────────────────────────┐
│  📸 Your Photo Uploaded                  │
│                                          │
│  🔍 Detected Features:                   │
│  ✓ Sunglasses detected                   │
│  ✓ Simple portrait                       │
│  ✓ Solid background                      │
│                                          │
│  🎯 Optimal Epoch: 7                     │
│     (Best for sunglasses: 90% confident) │
│                                          │
│  ⚙️  Generation Settings:                │
│     • Guidance: 8.0                      │
│     • Steps: 30                          │
│                                          │
│  [Generate Punk] [Try Different Epoch▼] │
└─────────────────────────────────────────┘
```

### Option 2: Silent (Just Works)
- User uploads photo
- System routes silently
- Generate best result
- Collect feedback after

### Option 3: Ensemble (Show Multiple Options)
```
┌─────────────────────────────────────────┐
│  We generated 3 versions for you:       │
│                                          │
│  [Image A]      [Image B]      [Image C]│
│  Epoch 7        Epoch 8        Epoch 5  │
│  (Balanced)     (Cleanest)     (Vibrant) │
│                                          │
│  Pick your favorite! ⭐                  │
└─────────────────────────────────────────┘
```

---

## Success Metrics

### Technical Metrics:
- Average unique colors per generation
- User rating distribution
- Accessory accuracy rate
- Routing confidence scores
- Generation consistency

### User Experience Metrics:
- Time to satisfaction (how many regenerations?)
- User rating trends over time
- Feature request themes
- Dropout rate (users who leave without generating)

### Business Metrics:
- Generation volume
- User retention
- Feedback submission rate
- Premium feature adoption (if we add paid tiers)

---

## Future Enhancements

### Near-Term (Next Month):
1. **Multi-Epoch Ensemble:** Generate from 2-3 epochs, let user pick
2. **Fine-Tuned Routing:** Use ML to learn optimal routing from user feedback
3. **Accessory Strength Slider:** Let users emphasize certain features
4. **Background Color Picker:** Override detected background

### Mid-Term (3 Months):
1. **Custom Epoch Training:** Users can commission training on their specific style
2. **Style Transfer:** Apply different artistic styles to generated punks
3. **Animation:** Generate multiple frames for animated punks
4. **Batch Generation:** Upload multiple photos, generate all at once

### Long-Term (6+ Months):
1. **Auto-Improvement:** System self-tunes based on aggregate feedback
2. **Community Voting:** Users vote on best generations, train on winners
3. **Marketplace Integration:** Direct mint to blockchain
4. **Mobile App:** Native iOS/Android with camera integration

---

## Open Questions & Experiments

### Routing Strategy:
- Q: Fixed thresholds vs ML-based routing?
- A: Start with fixed, add ML layer after 1000+ feedbacks

### Epoch Loading:
- Q: Load all epochs vs dynamic loading?
- A: Start with 3 in memory (5, 7, 8), add more if needed

### User Feedback:
- Q: Mandatory vs optional feedback?
- A: Optional but incentivized (show "Help improve!" badge)

### Parameter Tuning:
- Q: Per-epoch params vs global?
- A: Per-epoch with smart defaults

---

## Related Documents

- `CAPTION_FIX_FINAL_REPORT.md` - Epoch performance baseline
- `VISUAL_QUALITY_AUDIT.md` - User feedback on quality issues
- `PHASE1B_SIMPLIFIED_CAPTIONS_LOG.md` - Next training iteration
- `256PX_EXPERIMENT_FAILURE_SUMMARY.md` - What NOT to do

---

## Notes from User Discussions

**Key Insights:**
1. "when a user uploads a picture or avatar, i would assume (maybe) we fine tune parameters, as on option (or not if thats edumb/overcomplicating), but also what about using a specific epoch that is more suitable or conducible to the image type and more likely to generate an accurate bespoke punk based on the original uploaded image characteristics?"

   → **Decision:** NOT overcomplicated! Smart ML! Implement full adaptive system.

2. "user selection could also be interesting for future testing experimentation"

   → **Decision:** Build feedback loop from day 1. User choices = gold data for improvement.

3. "note all of this stuff in the last few messages"

   → **Decision:** This document captures all ideas, proposals, experiments.

---

## Implementation Status

- [x] System design documented
- [ ] Image feature detection implemented
- [ ] Epoch specialization database populated
- [ ] Routing logic implemented
- [ ] User feedback system built
- [ ] Gradio UI updated
- [ ] Systematic epoch testing complete
- [ ] Production deployment
- [ ] Monitoring dashboard

---

**Next Steps:**
1. Implement image feature detection
2. Run systematic epoch testing
3. Build routing table
4. Integrate into Gradio
5. Deploy and collect feedback
6. Iterate based on data

**Estimated Timeline:** 2 weeks to production-ready system
