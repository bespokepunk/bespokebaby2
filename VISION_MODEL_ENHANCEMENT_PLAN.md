# Vision Model Enhancement Plan: BLIP-2 / LLaVA Integration

## Overview

This document outlines the plan for integrating vision-language models (BLIP-2 or LLaVA) into the Bespoke Punk Generator to improve feature detection accuracy.

## Current Limitations

### V2 Generator (Current Approach)
**Method**: K-means color clustering + training vocabulary mapping

**Problems Identified**:
- Cannot distinguish between **hair** vs **hats/helmets** vs **accessories**
- Misidentifies **pink bows** as "light red hair"
- Detects **helmets** as "hair"
- Inaccurate **skin tone** detection (medium brown → "dark", light → "dark")
- No understanding of **accessories** (earrings, necklaces, glasses)
- No **semantic understanding** of the image content

**Example Failures**:
```
Input: lad_001_carbon.png (person wearing dark gray helmet)
Detected: "light red hair" ❌ (it's a helmet!)

Input: lady_001_hazelnut.png (brown hair with pink bow)
Detected: "light red hair" ❌ (detected the bow, not hair!)
```

## What Are Vision-Language Models?

### BLIP-2 (Bootstrapped Language-Image Pre-training 2)
- **Publisher**: Salesforce Research
- **Purpose**: Understands images and can describe them in natural language
- **Capabilities**:
  - Image captioning ("a person wearing a red hat")
  - Visual question answering (Q: "What color is the hair?" A: "Brown")
  - Can understand context and relationships

### LLaVA (Large Language and Vision Assistant)
- **Publisher**: Microsoft / University of Wisconsin
- **Purpose**: Multimodal AI that can "see" and reason about images
- **Capabilities**:
  - Detailed image understanding
  - Can distinguish accessories from features
  - Understands spatial relationships
  - More conversational and flexible

## Why This Solves Our Problems

### Semantic Understanding
```
Current V2: "Red pixels detected" → maps to "red hair"
Vision Model: "Person wearing a red helmet" → "wearing red hat"
```

### Accessory Detection
```
Current V2: "Pink pixels near head" → "pink hair"
Vision Model: "Brown hair with pink bow" → "brown hair, wearing pink bow"
```

### Accurate Feature Identification
```
Current V2: Color-based guessing
Vision Model: Actual understanding of:
  - Hair vs headwear
  - Facial features vs accessories
  - Clothing vs background
```

## Implementation Approaches

### Option 1: BLIP-2 Integration (Recommended for MVP)

**Model**: `Salesforce/blip2-opt-2.7b` or `Salesforce/blip2-flan-t5-xl`

**Pros**:
- Well-documented, mature
- Good balance of accuracy vs speed
- 2.7B parameters = reasonable memory footprint (~6GB VRAM)
- Excellent for Q&A format

**Cons**:
- Larger model download (~5GB)
- Slower inference than color extraction

**Use Case**:
- Ask targeted questions about the image
- Extract specific features we care about

**Code Structure**:
```python
class VisionFeatureDetector:
    def __init__(self):
        self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-opt-2.7b",
            torch_dtype=torch.float16
        ).to("mps")

    def detect_features(self, image_path):
        image = Image.open(image_path)

        # Ask specific questions
        questions = [
            "What color is the person's hair?",
            "What color are the person's eyes?",
            "What is the person's skin tone?",
            "Is the person wearing a hat or headwear?",
            "What accessories is the person wearing?",
            "Describe the background color"
        ]

        answers = {}
        for question in questions:
            inputs = self.processor(image, question, return_tensors="pt").to("mps", torch.float16)
            out = self.model.generate(**inputs, max_new_tokens=20)
            answer = self.processor.decode(out[0], skip_special_tokens=True)
            answers[question] = answer

        return answers
```

### Option 2: LLaVA Integration (More Powerful)

**Model**: `llava-hf/llava-1.5-7b-hf` or `llava-hf/llava-1.5-13b-hf`

**Pros**:
- State-of-the-art understanding
- Very flexible, conversational
- Can handle complex instructions

**Cons**:
- Larger (7B-13B parameters)
- Requires more VRAM (~14GB for 7B model)
- Slightly slower
- More recent, less battle-tested than BLIP-2

**Code Structure**:
```python
class LLaVAFeatureDetector:
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
        self.model = LlavaForConditionalGeneration.from_pretrained(
            "llava-hf/llava-1.5-7b-hf",
            torch_dtype=torch.float16
        ).to("mps")

    def detect_features(self, image_path):
        image = Image.open(image_path)

        # Single comprehensive prompt
        prompt = """Analyze this portrait and describe:
        1. Hair color (not hats/accessories)
        2. Eye color
        3. Skin tone
        4. Any headwear (hats, helmets, crowns)
        5. Accessories (earrings, necklaces, glasses)
        6. Background color

        Format as JSON."""

        inputs = self.processor(image, text=prompt, return_tensors="pt").to("mps", torch.float16)
        out = self.model.generate(**inputs, max_new_tokens=200)
        response = self.processor.decode(out[0], skip_special_tokens=True)

        return self.parse_response(response)
```

## Integration Architecture

### Hybrid Approach (Recommended)

Combine **color palette extraction** (V2) + **vision model** (BLIP-2/LLaVA) for best results:

```
User uploads image
    ↓
1. Extract color palette (V2 approach)
   └─> Get dominant colors for background/overall tone
    ↓
2. Run vision model
   └─> Understand features, accessories, headwear
    ↓
3. Merge insights
   ├─> Use vision model for: hair, eyes, skin, accessories
   ├─> Use color palette for: background color (with hex)
   └─> Combine into training caption format
    ↓
4. Generate Bespoke Punk
```

**Benefits**:
- **Color accuracy**: Palette extraction ensures exact hex colors for background
- **Feature accuracy**: Vision model ensures correct identification
- **Best of both worlds**: Fast color detection + smart feature understanding

### Code Integration Point

**File**: `bespoke_punk_generator_v3.py` (new file)

**Classes**:
```python
class VisionFeatureDetector:
    """Uses BLIP-2 or LLaVA for semantic feature detection"""

class HybridPromptGenerator:
    """Combines color palette + vision features"""

    def generate(self, image_path):
        # 1. Extract color palette
        palette = ColorPaletteExtractor(image_path).get_color_palette()
        background = palette[0]  # Most dominant color

        # 2. Detect features with vision model
        vision = VisionFeatureDetector()
        features = vision.detect_features(image_path)

        # 3. Map vision features to training vocabulary
        hair = self.map_hair(features['hair'], features['headwear'])
        eyes = self.map_eyes(features['eyes'])
        skin = self.map_skin(features['skin_tone'])
        accessories = self.extract_accessories(features['accessories'])

        # 4. Build training format prompt
        prompt = self.build_prompt(
            background=background,
            hair=hair,
            eyes=eyes,
            skin=skin,
            accessories=accessories
        )

        return prompt
```

## Implementation Plan

### Phase 1: Research & Testing (1-2 days)
- [ ] Test BLIP-2 on sample Bespoke Punk images
- [ ] Test LLaVA on sample Bespoke Punk images
- [ ] Compare accuracy vs V2 approach
- [ ] Benchmark inference speed
- [ ] Choose which model to use

### Phase 2: Integration (2-3 days)
- [ ] Create `VisionFeatureDetector` class
- [ ] Create `HybridPromptGenerator` class
- [ ] Integrate with existing pipeline
- [ ] Add model download/caching logic
- [ ] Update UI to show vision model insights

### Phase 3: Refinement (1-2 days)
- [ ] Fine-tune prompts/questions for BLIP-2/LLaVA
- [ ] Improve feature mapping to training vocabulary
- [ ] Add error handling (fallback to V2 if vision model fails)
- [ ] Optimize for speed (caching, batching)

### Phase 4: Testing & Validation (1 day)
- [ ] Test with all training images
- [ ] Test with user-uploaded images
- [ ] Compare results: V1 vs V2 vs V3 (hybrid)
- [ ] Gather user feedback

## Requirements

### Additional Dependencies

```bash
pip install transformers>=4.30.0 pillow torch accelerate
```

### Model Downloads

**BLIP-2 (Recommended)**:
```python
# ~5GB download
Salesforce/blip2-opt-2.7b
```

**LLaVA (Alternative)**:
```python
# ~14GB download
llava-hf/llava-1.5-7b-hf
```

### System Requirements

**BLIP-2**:
- VRAM: 6GB minimum (MPS on M-series Macs)
- RAM: 8GB
- Disk: 6GB for model files

**LLaVA**:
- VRAM: 14GB minimum
- RAM: 16GB
- Disk: 15GB for model files

## Expected Improvements

### Accuracy Gains

| Feature | V2 (Current) | V3 (Vision Model) |
|---------|--------------|-------------------|
| Hair vs Hat | ❌ Often wrong | ✅ Correct |
| Accessories | ❌ Can't detect | ✅ Detected |
| Skin Tone | ⚠️ ~60% accurate | ✅ ~90% accurate |
| Eye Color | ⚠️ ~70% accurate | ✅ ~95% accurate |
| Background | ✅ Accurate (hex) | ✅ Accurate (hex + desc) |

### Performance Impact

**V2 (Current)**:
- Processing time: ~2-3 seconds
- Memory: ~3GB

**V3 (with BLIP-2)**:
- Processing time: ~8-12 seconds (5-10 sec vision model + 2 sec generation)
- Memory: ~9GB (6GB model + 3GB generation)

**Trade-off**: 4x slower but **dramatically** more accurate

## Alternative: On-Demand Vision Model

To avoid performance impact, offer two modes in UI:

1. **Fast Mode (V2)**: Color-based, ~3 seconds
2. **Accurate Mode (V3)**: Vision model, ~12 seconds

Let users choose based on their needs.

## Example Improved Outputs

### Before (V2)
```
Input: lad_001_carbon.png (dark gray helmet)
Prompt: "pixel art, 24x24, portrait of bespoke punk,
         red solid background (#ad624d),
         light red hair,  ❌
         brown eyes,
         light skin,
         sharp pixel edges, hard color borders"
```

### After (V3 with Vision Model)
```
Input: lad_001_carbon.png (dark gray helmet)
Prompt: "pixel art, 24x24, portrait of bespoke punk,
         red solid background (#ad624d),
         bald or very short hair, ✅
         wearing dark gray helmet with gold badge, ✅
         brown eyes,
         tan skin, ✅
         sharp pixel edges, hard color borders"
```

## Future Enhancements

### Post-MVP Ideas

1. **Fine-tuned Vision Model**: Train BLIP-2/LLaVA specifically on Bespoke Punk dataset
2. **Multi-angle Support**: Generate multiple punk variants from single input
3. **Style Transfer**: "Make it more cyberpunk" / "Add steampunk elements"
4. **Interactive Editing**: "Change hair to blue" / "Add sunglasses"

## Decision Matrix

| Criterion | BLIP-2 | LLaVA | V2 (Current) |
|-----------|---------|--------|--------------|
| Accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Memory | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Maturity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation**: Start with **BLIP-2** for balance of accuracy and performance.

## Next Steps

1. ✅ Document enhancement plan (this file)
2. ⏳ Install transformers library
3. ⏳ Test BLIP-2 on 5-10 sample images
4. ⏳ Build proof-of-concept integration
5. ⏳ Compare V2 vs V3 results
6. ⏳ Decide: integrate as default or offer as option

## References

- [BLIP-2 Paper](https://arxiv.org/abs/2301.12597)
- [BLIP-2 Hugging Face](https://huggingface.co/docs/transformers/model_doc/blip-2)
- [LLaVA Paper](https://arxiv.org/abs/2304.08485)
- [LLaVA Hugging Face](https://huggingface.co/llava-hf)
