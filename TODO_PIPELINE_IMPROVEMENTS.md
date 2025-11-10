# ML Pipeline Improvements TODO

**Purpose:** Track future enhancements for validation, convergence detection, and continuous improvement

**Status:** Planning Phase
**Priority:** Medium-High (implement as pipeline matures)

---

## 🎯 High Priority: Validation & Convergence

### 1. Automated Convergence Detection

**Goal:** Automatically identify when model has converged or is degrading

**Implementation:**
```python
def detect_convergence(epoch_results):
    """
    Analyze last 3 epochs to detect:
    - Plateau (no improvement)
    - Degradation (scores declining)
    - Optimal point (peak before decline)

    Returns: "continue", "plateau", "degrading", "optimal"
    """
    # Calculate rolling average
    # Detect trend direction
    # Flag early stopping opportunity
```

**Features:**
- [ ] Rolling average score calculation (window=3)
- [ ] Trend detection (improving/stable/declining)
- [ ] Early stopping recommendation
- [ ] Email/Slack notification when convergence detected
- [ ] Auto-update Supabase with convergence status

**Benefits:**
- Save compute costs (stop training early if not improving)
- Prevent overtraining
- Identify optimal epoch automatically

---

### 2. Quantitative Color Accuracy Metrics

**Goal:** Replace subjective scoring with measurable color accuracy

**Current:** Manual visual inspection
**Proposed:** Automated color analysis

**Metrics to Implement:**
```python
def measure_color_accuracy(generated_image, expected_colors):
    """
    Quantitative metrics:
    1. Background color match (% pixels matching expected hex)
    2. Hair color accuracy (dominant color vs expected)
    3. Accessory presence detection (via object detection)
    4. Color purity (solid vs multi-toned)

    Returns: accuracy_score (0-100)
    """
```

**Implementation Tasks:**
- [ ] Extract dominant colors from generated image
- [ ] Compare to expected hex codes from prompt
- [ ] Calculate % match for each region (hair, background, etc.)
- [ ] Detect multi-toning (hair should be solid, not two-toned)
- [ ] Auto-score: 90%+ match = 9-10, 70-90% = 7-8, etc.
- [ ] Store metrics in Supabase (`color_accuracy_score` column)

**Benefits:**
- Objective, reproducible measurements
- Faster evaluation (no manual review)
- Precise tracking of color learning progress

---

### 3. Multi-Prompt Test Suite

**Goal:** Test each epoch with diverse prompts, not just one

**Current:** Single prompt (pink hair, crown, green background)
**Proposed:** 10-15 diverse test prompts

**Test Suite:**
```python
TEST_PROMPTS = [
    # Color variations
    ("pink_hair_green_bg", "..."),
    ("blue_hair_red_bg", "..."),
    ("brown_hair_yellow_bg", "..."),

    # Accessory variations
    ("crown", "..."),
    ("sunglasses", "..."),
    ("necklace", "..."),

    # Skin tone variations
    ("light_skin", "..."),
    ("medium_skin", "..."),
    ("dark_skin", "..."),

    # Expression variations
    ("smile", "..."),
    ("neutral", "..."),
]
```

**Features:**
- [ ] Expand test prompt library
- [ ] Generate all prompts per epoch (10-15 images)
- [ ] Calculate average score across all prompts
- [ ] Identify weak areas (e.g., "fails on blue hair but works on pink")
- [ ] Store per-prompt results in `prompt_test_results` table

**Benefits:**
- Comprehensive model evaluation
- Identify edge cases and failures
- More confident production deployment

---

### 4. Progressive Validation Strategy

**Goal:** Quick validation early, thorough validation at key epochs

**Strategy:**
```
Epochs 1-2: Quick test (1 prompt, ~2 min)
Epochs 3-4: Quick test (1 prompt)
Epoch 5:    Medium test (5 prompts, ~10 min)
Epochs 6-7: Quick test (1 prompt)
Epoch 7:    Full test (15 prompts, ~30 min)  ← Expected best
Epochs 8-10: Medium test (5 prompts) to check overtraining
```

**Implementation:**
- [ ] Create `progressive_test_epoch.py` script
- [ ] Auto-selects test depth based on epoch number
- [ ] Saves compute time on early epochs
- [ ] Thorough testing at critical epochs (5, 7, 10)

---

### 5. Automated Comparison Reports

**Goal:** Generate comparison reports automatically after each epoch

**Report Contents:**
1. **Epoch Progression Chart**
   - Line graph: Epochs 1-N vs scores
   - Identify inflection points

2. **Comparison to Baseline**
   - Side-by-side images (new epoch vs SD15_PERFECT Epoch 7)
   - Automated diff highlighting

3. **Issue Tracking**
   - Issues by epoch (wrong backgrounds, color problems)
   - Track which issues are resolving vs persisting

4. **Recommendations**
   - "Continue training" or "Stop, Epoch X is best"
   - Confidence score

**Implementation:**
- [ ] Create `generate_epoch_report.py`
- [ ] Use matplotlib for progression charts
- [ ] Auto-generate HTML report with images
- [ ] Save to `reports/epoch_N_report.html`
- [ ] Optional: Auto-open in browser

**Benefits:**
- Quick at-a-glance progress assessment
- Shareable reports for collaboration
- Historical record of training progression

---

## 📊 Medium Priority: Dashboard & Visualization

### 6. Real-Time Training Dashboard

**Goal:** Live view of training progress

**Features:**
- [ ] Web dashboard (Flask or Streamlit)
- [ ] Real-time metrics from Supabase
- [ ] Epoch progression charts
- [ ] Latest test images displayed
- [ ] Training run comparison view
- [ ] Prediction: "Estimated best epoch: 6-7"

**Tech Stack:**
- Streamlit (easiest) or Flask + Chart.js
- WebSocket for real-time updates
- Hosted locally or on cloud

---

### 7. A/B Testing Framework

**Goal:** Compare two models head-to-head

**Use Case:** "Is new model better than production?"

**Implementation:**
```python
def ab_test(model_a_path, model_b_path, test_prompts):
    """
    Generate same prompts with both models
    Display side-by-side
    User votes: A better, B better, or Tie

    Statistical significance test after N comparisons
    """
```

**Features:**
- [ ] Side-by-side image generation
- [ ] Blind testing (randomize A/B order)
- [ ] Vote tracking in Supabase
- [ ] Statistical analysis (confidence intervals)
- [ ] Final recommendation: "Use Model B (95% confidence)"

---

## 🔬 Low Priority: Advanced Features

### 8. Automated Caption Quality Analysis

**Goal:** Detect caption issues before training

**Checks:**
- [ ] All captions have 12+ hex codes
- [ ] Lips are specified
- [ ] Expressions are classified
- [ ] No typos (spell check)
- [ ] Consistent formatting

**Auto-fix:**
- [ ] Suggest corrections
- [ ] Batch update captions
- [ ] Re-sync to Supabase

---

### 9. Transfer Learning Experiment Tracker

**Goal:** Track which training runs influenced which

**Use Case:** "Epoch 7 of Run A became starting point for Run B"

**Schema Addition:**
```sql
ALTER TABLE training_runs ADD COLUMN parent_run_id INTEGER REFERENCES training_runs(id);
ALTER TABLE training_runs ADD COLUMN starting_checkpoint TEXT;
```

---

### 10. Cost Tracking & Optimization

**Goal:** Track training costs and optimize

**Metrics:**
- [ ] RunPod GPU time per epoch
- [ ] Cost per epoch
- [ ] Total training run cost
- [ ] Storage costs
- [ ] Compare to budget

**Optimization:**
- [ ] Identify expensive failed experiments
- [ ] Recommend cheaper GPUs for early epochs
- [ ] Auto-stop if cost exceeds threshold

---

## 🎯 Implementation Priority

**Phase 1 (Next 1-2 weeks):**
1. ✅ Basic epoch logging (DONE!)
2. Automated convergence detection
3. Multi-prompt test suite

**Phase 2 (Next month):**
4. Quantitative color metrics
5. Automated comparison reports
6. Progressive validation strategy

**Phase 3 (Future):**
7. Real-time dashboard
8. A/B testing framework
9. Advanced features (caption analysis, transfer learning, cost tracking)

---

## 📈 Success Metrics for Pipeline Improvements

**Before Improvements:**
- Manual epoch evaluation: ~10 min/epoch
- Subjective scoring: Variable between reviewers
- No early stopping: Train all 10 epochs always
- No automated reporting

**After Improvements:**
- Automated evaluation: ~2 min/epoch
- Objective metrics: Reproducible scores
- Smart early stopping: Save 30-40% compute
- Auto-generated reports: Share with team instantly

**ROI:**
- Time saved: 8 min/epoch × 10 epochs = 80 min/run
- Cost saved: Early stopping at epoch 6 saves 40% GPU cost
- Quality: Objective metrics = better model selection

---

## 🔄 Continuous Improvement Loop

```
1. Train → 2. Validate → 3. Analyze → 4. Learn → 5. Improve → 1. Train
```

**Current State:**
- ✅ Train: RunPod with Kohya
- ✅ Validate: quick_test_epoch.py
- ✅ Analyze: Manual Supabase queries
- ⚠️ Learn: Manual documentation
- ⚠️ Improve: Ad-hoc experimentation

**Goal State:**
- ✅ Train: Automated with monitoring
- ✅ Validate: Multi-prompt automated testing
- ✅ Analyze: Auto-generated reports + dashboard
- ✅ Learn: AI-assisted pattern detection
- ✅ Improve: Data-driven hypothesis testing

---

## 📝 Next Steps

**Immediate (This Week):**
- [ ] Finish Epochs 4-10 of current run
- [ ] Test automated logging workflow
- [ ] Document learnings from SD15_FINAL_CORRECTED

**Short-term (This Month):**
- [ ] Implement convergence detection
- [ ] Build multi-prompt test suite
- [ ] Create epoch comparison reports

**Long-term (Next Quarter):**
- [ ] Build training dashboard
- [ ] Implement quantitative metrics
- [ ] A/B testing framework

---

**Last Updated:** November 10, 2025
**Status:** Active Development Roadmap
**Owner:** Ilyssa Evans
