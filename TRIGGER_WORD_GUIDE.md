# 🎯 Trigger Word Guide - TOK vs bespoke

Quick guide on trigger words for your Bespoke Punk training.

## Current Setup (Recommended) ✅

**Trigger Word**: `TOK`

**Training Captions** (what you have):
```
bespoke, 24x24 pixel grid portrait, female, purple background...
```

**Sample Prompts** (for W&B):
```
TOK bespoke, 24x24 pixel grid portrait, female, purple background...
```

**Inference** (using the model):
```
TOK bespoke, 24x24 pixel art, female, purple background, brown hair, blue eyes
```

### Why This Works Best

1. ✅ "TOK" is unique and won't conflict with base model
2. ✅ "bespoke" reinforces your specific style
3. ✅ Together they give most consistent results
4. ✅ Clear signal to activate your LoRA

## Alternative Option: Use "bespoke" as Trigger

If you want simpler prompts, you could change to:

**Trigger Word**: `bespoke`

**Sample Prompts**:
```
bespoke, 24x24 pixel grid portrait, female, purple background...
```

**Inference**:
```
bespoke, 24x24 pixel art, female, purple background, brown hair, blue eyes
```

### To Change to This

Edit in your config files:
- `trigger_word="bespoke"` (instead of "TOK")
- Remove "TOK" from sample prompts
- Keep training captions as-is

### Pros/Cons

**TOK + bespoke** (Current):
- ✅ Most specific
- ✅ Won't interfere with base model
- ✅ Can use "bespoke" in regular prompts without LoRA
- ⚠️ Slightly longer prompts

**Just "bespoke"**:
- ✅ Simpler prompts
- ✅ Natural trigger word
- ⚠️ Might activate partially on any "bespoke" mention
- ⚠️ Less distinct from base model

## 🎓 Best Practices

### For Training
Your captions should:
- ❌ NOT include trigger word manually
- ✅ Trainer adds it automatically
- ✅ Keep your current format: "bespoke, 24x24..."

### For W&B Sample Prompts
- ✅ MUST include trigger word: "TOK bespoke..."
- ✅ Match your training caption style
- ✅ Test different variations

### For Inference
Always start with trigger word:
```python
# ✅ CORRECT
"TOK bespoke, 24x24 pixel art, female, purple background..."

# ❌ WRONG - Won't use your LoRA
"24x24 pixel art, female, purple background..."
```

## 📊 Quick Reference

| Situation | Include TOK? | Include bespoke? |
|-----------|-------------|------------------|
| **Training captions** (.txt files) | ❌ No | ✅ Yes |
| **Trigger word setting** | ✅ "TOK" | or "bespoke" |
| **W&B sample prompts** | ✅ Yes | ✅ Yes |
| **Inference prompts** | ✅ Yes | ✅ Yes (recommended) |

## 🔧 Current Files Using Trigger Words

All your files are already set up correctly:

### Replicate
- `start_replicate_training.sh`: `trigger_word="TOK"` ✅
- `replicate_config.yaml`: `trigger_word: "TOK"` ✅
- `wandb_sample_prompts.txt`: All start with "TOK bespoke" ✅

### RunPod
- `start_training.sh`: W&B prompts use "TOK bespoke" ✅
- `runpod_training.py`: Accepts your captions as-is ✅

## 💡 My Recommendation

**Keep it as-is!** Your current setup is optimal:

1. Trigger word: "TOK"
2. Training captions: "bespoke, 24x24..." (no TOK)
3. Sample prompts: "TOK bespoke, 24x24..."
4. Inference: "TOK bespoke, 24x24..."

This gives you:
- ✅ Maximum control
- ✅ Most consistent results
- ✅ Clear activation signal
- ✅ No conflicts with base model

## 🎨 Example Prompts

### Basic
```
TOK bespoke, 24x24 pixel art, female, purple background, brown hair, blue eyes
```

### Detailed (like training captions)
```
TOK bespoke, 24x24 pixel grid portrait, symbolic punk style, purple solid background, brown hair starting at y=3 extending to y=17, black pupils fixed at (8,12) and (13,12), blue iris eyes at (9,12) and (14,12), light skin tone, right-facing
```

### Simplified (still works)
```
TOK bespoke punk, female portrait, purple background, brown hair, blue eyes, pixel art style
```

All will activate your LoRA, but more detailed = more consistent with training!

---

**Bottom line**: Your setup is already correct. Use "TOK bespoke" in all sample and inference prompts! ✅
