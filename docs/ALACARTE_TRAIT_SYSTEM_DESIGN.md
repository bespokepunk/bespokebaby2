# À La Carte Trait Selection System - Design Doc

**Date:** 2025-11-10
**Status:** 💡 CONCEPT - High Priority Alternative Approach
**Context:** Emerged after Phase 1B failure as smarter alternative to full auto-detection

---

## Executive Summary

Instead of trying to **detect all features automatically** from user photos, provide an **à la carte trait menu** where users can:

1. Upload photo → Generate base punk (hair, eyes, skin, background auto-detected)
2. Browse trait catalog → Select accessories from training vocabulary
3. Layer traits → Add sunglasses, earrings, hat, etc. on top
4. Smart routing → Use epoch best suited for selected traits

**Key Insight:** The model knows 50+ specific traits from training. Let users **select** rather than **detect** rare/complex features!

---

## Why This Approach?

### Problems with Auto-Detection
❌ **Computer vision is hard:** Detecting "stunner shades" vs "3D glasses" from user photo
❌ **Rare traits:** User has unique accessory model doesn't know
❌ **Ambiguity:** Is that a cap or a beanie? Crown or tiara?
❌ **Over-promising:** User expects perfect detection, gets disappointed

### Benefits of À La Carte Selection
✅ **User control:** Explicit choice = no surprises
✅ **Training vocabulary:** Only offer traits model actually knows
✅ **Epoch routing:** Route to epoch specialized for chosen traits
✅ **Experimentation:** Users try different combos easily
✅ **Fun UX:** Interactive, game-like customization

---

## User Flow

### Step 1: Upload & Generate Base
```
┌─────────────────────────────────────┐
│  📸 Upload Your Photo                │
│  [Upload button]                     │
│                                      │
│  Gender: ○ Lady  ● Lad               │
│                                      │
│  [Generate Base Punk]                │
└─────────────────────────────────────┘
```

**Auto-detected features:**
- Hair color (black, brown, blonde, red, etc.)
- Eye color (brown, blue, green, black, gray)
- Skin tone (light, medium, tan, dark)
- Background color (can be customized)

**Output:** Clean base punk with NO accessories

### Step 2: Browse Trait Catalog
```
┌─────────────────────────────────────┐
│  🎨 Add Traits (Optional)            │
│                                      │
│  👓 Eyewear                          │
│    □ Black Stunner Shades            │
│    □ 3D Glasses                      │
│    □ Small Shades                    │
│    □ Classic Shades                  │
│    □ Big Shades                      │
│    □ VR Headset                      │
│                                      │
│  🎩 Headwear                         │
│    □ Top Hat                         │
│    □ Fedora                          │
│    □ Hoodie                          │
│    □ Baseball Cap                    │
│    □ Beanie                          │
│    □ Bandana                         │
│    □ Headband                        │
│    □ Tiara                           │
│    □ Crown                           │
│                                      │
│  💍 Jewelry                          │
│    □ Gold Earrings                   │
│    □ Silver Earrings                 │
│    □ Vape                            │
│    □ Cigarette                       │
│    □ Pipe                            │
│                                      │
│  😊 Expression                       │
│    ○ Neutral (default)               │
│    ○ Frown                           │
│    ○ Buck Teeth                      │
│    ○ Smile                           │
│                                      │
│  [✨ Regenerate with Selected Traits]│
└─────────────────────────────────────┘
```

**Smart Features:**
- Multi-select (can pick multiple compatible traits)
- Compatibility validation (e.g., can't wear two hats)
- Preview which epoch will be used
- Show confidence score for each trait

### Step 3: Generate with Traits
**System does:**
1. Take base features (hair, eyes, skin)
2. Add selected traits to prompt
3. Route to optimal epoch for trait combo
4. Generate new punk with traits

**Output:**
- 512x512 full resolution
- 24x24 pixel art NFT
- Prompt used
- Epoch selected
- Confidence score

---

## Technical Architecture

### Trait Database
```python
TRAIT_CATALOG = {
    'eyewear': {
        'black_stunner_shades': {
            'label': 'Black Stunner Shades',
            'prompt_text': 'wearing black stunner shades with white reflection',
            'best_epochs': [7, 5],  # Epoch 7 best, 5 backup
            'confidence': 0.90,
            'incompatible_with': ['3d_glasses', 'small_shades'],
            'preview_image': 'assets/traits/black_stunner_shades.png',
        },
        '3d_glasses': {
            'label': '3D Glasses',
            'prompt_text': 'wearing 3D glasses',
            'best_epochs': [6, 7],
            'confidence': 0.85,
            'incompatible_with': ['black_stunner_shades', 'vr_headset'],
            'preview_image': 'assets/traits/3d_glasses.png',
        },
        # ... more eyewear
    },

    'headwear': {
        'top_hat': {
            'label': 'Top Hat',
            'prompt_text': 'wearing black top hat',
            'best_epochs': [8, 7],
            'confidence': 0.95,
            'incompatible_with': ['fedora', 'hoodie', 'bandana', 'beanie'],
            'preview_image': 'assets/traits/top_hat.png',
        },
        # ... more headwear
    },

    'jewelry': {
        'gold_earrings': {
            'label': 'Gold Earrings',
            'prompt_text': 'wearing gold earrings',
            'best_epochs': [5, 8],
            'confidence': 0.88,
            'gender_restriction': 'lady',  # Optional
            'preview_image': 'assets/traits/gold_earrings.png',
        },
        # ... more jewelry
    },

    'expression': {
        'frown': {
            'label': 'Frown',
            'prompt_text': 'frowning',
            'best_epochs': [7, 8],
            'confidence': 0.80,
            'incompatible_with': ['smile', 'buck_teeth'],
        },
        # ... more expressions
    },
}
```

### Prompt Builder with Traits
```python
class TraitAwarePromptGenerator:
    """Build prompts incorporating user-selected traits"""

    def __init__(self, trait_catalog):
        self.catalog = trait_catalog

    def generate_with_traits(self, base_features, selected_traits):
        """
        Args:
            base_features: {hair, eyes, skin, background} from photo analysis
            selected_traits: ['black_stunner_shades', 'top_hat', 'gold_earrings']

        Returns:
            {
                'prompt': full prompt string,
                'optimal_epoch': best epoch for trait combo,
                'confidence': overall confidence score
            }
        """

        # Validate compatibility
        self._validate_trait_compatibility(selected_traits)

        # Build base prompt
        prompt_parts = [
            "pixel art",
            "24x24",
            f"portrait of bespoke punk {base_features['gender']}"
        ]

        # Add base features
        prompt_parts.append(f"{base_features['hair']} hair")

        # Add selected traits in optimal order
        trait_prompts = []
        for trait_id in selected_traits:
            category = self._get_trait_category(trait_id)
            trait_data = self.catalog[category][trait_id]
            trait_prompts.append(trait_data['prompt_text'])

        prompt_parts.extend(trait_prompts)

        # Add eyes and skin (after accessories for better generation)
        prompt_parts.append(f"{base_features['eyes']} eyes")
        prompt_parts.append(f"{base_features['skin']} skin")
        prompt_parts.append(f"{base_features['background']} solid background")

        # Add style markers
        prompt_parts.extend([
            "sharp pixel edges",
            "hard color borders",
            "retro pixel art style"
        ])

        # Select optimal epoch
        optimal_epoch = self._select_epoch_for_traits(selected_traits)
        confidence = self._calculate_confidence(selected_traits, optimal_epoch)

        return {
            'prompt': ", ".join(prompt_parts),
            'optimal_epoch': optimal_epoch,
            'confidence': confidence,
        }

    def _select_epoch_for_traits(self, trait_ids):
        """Smart epoch selection based on trait combo"""
        if not trait_ids:
            return 8  # Default: CAPTION_FIX Epoch 8 for base punks

        # Collect epoch votes from each trait
        epoch_scores = {}
        for trait_id in trait_ids:
            category = self._get_trait_category(trait_id)
            trait_data = self.catalog[category][trait_id]

            for i, epoch in enumerate(trait_data['best_epochs']):
                # First choice gets more weight
                weight = 1.0 / (i + 1)
                epoch_scores[epoch] = epoch_scores.get(epoch, 0) + weight

        # Return highest scoring epoch
        return max(epoch_scores.items(), key=lambda x: x[1])[0]

    def _validate_trait_compatibility(self, trait_ids):
        """Check if selected traits are compatible"""
        for trait_id in trait_ids:
            category = self._get_trait_category(trait_id)
            trait_data = self.catalog[category][trait_id]

            incompatible = trait_data.get('incompatible_with', [])
            conflicts = set(trait_ids) & set(incompatible)

            if conflicts:
                raise ValueError(f"Trait '{trait_id}' incompatible with: {conflicts}")
```

### Generation Pipeline with Traits
```python
class AlaCarlePunkGenerator:
    """Generate punks with user-selected traits"""

    def __init__(self, trait_catalog):
        self.trait_catalog = trait_catalog
        self.prompt_builder = TraitAwarePromptGenerator(trait_catalog)

        # Load multiple epochs
        self.loaded_epochs = {
            5: load_lora('caption_fix_epoch5.safetensors'),
            6: load_lora('caption_fix_epoch6.safetensors'),
            7: load_lora('caption_fix_epoch7.safetensors'),
            8: load_lora('caption_fix_epoch8.safetensors'),
        }

    def generate(self, user_photo, gender, selected_traits=None):
        """
        Complete pipeline with optional trait selection

        Args:
            user_photo: Path to uploaded image
            gender: 'lady' or 'lad'
            selected_traits: ['black_stunner_shades', 'top_hat'] or None

        Returns:
            {
                'image_512': PIL Image,
                'image_24': PIL Image,
                'prompt': str,
                'features': dict,
                'traits_used': list,
                'epoch_used': int,
                'confidence': float,
            }
        """

        # Step 1: Analyze photo for base features
        base_features = self._analyze_photo(user_photo)
        base_features['gender'] = gender

        # Step 2: Build prompt with traits
        if selected_traits:
            prompt_data = self.prompt_builder.generate_with_traits(
                base_features,
                selected_traits
            )
        else:
            # No traits = simple base punk
            prompt_data = self.prompt_builder.generate_base(base_features)

        # Step 3: Select appropriate epoch
        epoch_num = prompt_data['optimal_epoch']
        lora_model = self.loaded_epochs[epoch_num]

        # Step 4: Generate
        image_512 = self._generate_with_lora(
            prompt_data['prompt'],
            lora_model
        )

        # Step 5: Downscale to 24x24
        image_24 = image_512.resize((24, 24), Image.NEAREST)

        return {
            'image_512': image_512,
            'image_24': image_24,
            'prompt': prompt_data['prompt'],
            'features': base_features,
            'traits_used': selected_traits or [],
            'epoch_used': epoch_num,
            'confidence': prompt_data['confidence'],
        }
```

---

## UI/UX Design

### Progressive Enhancement Approach

**Level 1: Simple (No Traits)**
- Upload photo → Generate base punk
- Fast, reliable, works every time
- Good for casual users

**Level 2: Browse & Select (À La Carte)**
- Generate base → Browse trait catalog → Select traits → Regenerate
- Interactive, fun, exploratory
- Power users love customization

**Level 3: Favorites & Presets**
- Save favorite trait combos
- "Cyberpunk preset" (VR + hoodie)
- "Classic punk preset" (mohawk + leather)

### Gradio Interface Mockup
```python
with gr.Blocks() as demo:
    with gr.Row():
        # Left: Input & Base Generation
        with gr.Column():
            input_image = gr.Image(label="Your Photo")
            gender = gr.Radio(["Lady", "Lad"], value="Lady")
            generate_base_btn = gr.Button("Generate Base Punk")

            base_output = gr.Image(label="Base Punk (no accessories)")

        # Right: Trait Selection
        with gr.Column():
            gr.Markdown("### 🎨 Add Traits (Optional)")

            with gr.Accordion("👓 Eyewear", open=False):
                eyewear = gr.CheckboxGroup(
                    choices=["Black Stunner Shades", "3D Glasses", "Small Shades"],
                    label="Select eyewear"
                )

            with gr.Accordion("🎩 Headwear", open=False):
                headwear = gr.CheckboxGroup(
                    choices=["Top Hat", "Fedora", "Hoodie", "Baseball Cap"],
                    label="Select headwear"
                )

            with gr.Accordion("💍 Jewelry", open=False):
                jewelry = gr.CheckboxGroup(
                    choices=["Gold Earrings", "Silver Earrings"],
                    label="Select jewelry"
                )

            epoch_display = gr.Textbox(label="Epoch Selected", interactive=False)
            confidence_display = gr.Number(label="Confidence", interactive=False)

            regenerate_btn = gr.Button("✨ Regenerate with Traits", variant="primary")

            trait_output = gr.Image(label="Punk with Traits")
```

---

## Implementation Phases

### Phase 1: Core System (Week 1)
- [ ] Build trait catalog database
- [ ] Implement trait-aware prompt generator
- [ ] Update generation pipeline to support trait selection
- [ ] Basic Gradio UI with trait checkboxes

### Phase 2: Epoch Routing (Week 2)
- [ ] Systematic testing: which epochs are best for which traits?
- [ ] Populate trait catalog with epoch recommendations
- [ ] Load multiple epochs into memory
- [ ] Implement smart routing logic

### Phase 3: UX Polish (Week 3)
- [ ] Add trait preview images
- [ ] Implement compatibility validation
- [ ] Add preset trait combos
- [ ] User favorites system

### Phase 4: Analytics & Optimization (Week 4)
- [ ] Track which traits users select most
- [ ] A/B test routing strategies
- [ ] Collect user ratings per trait
- [ ] Retrain model on popular trait combos

---

## Advantages Over Full Auto-Detection

| Aspect | Auto-Detection | À La Carte Selection |
|--------|---------------|---------------------|
| **Accuracy** | 60-80% (CV hard) | 100% (user choice) |
| **User Control** | None | Full control |
| **Rare Traits** | Fails | Not offered (only trained traits) |
| **Fun Factor** | Passive | Interactive, exploratory |
| **Epoch Routing** | Hard to optimize | Easy (known traits → known epochs) |
| **User Satisfaction** | Variable | Higher (explicit choice) |
| **Development Complexity** | HIGH (CV + detection) | MEDIUM (UI + catalog) |

---

## Integration with Adaptive Epoch System

**Perfect Synergy:**

1. **Base Generation** → Use CAPTION_FIX Epoch 8 (proven reliable)
2. **User Selects Traits** → Check which epochs excel at those traits
3. **Smart Routing** → Use Epoch 7 for sunglasses, Epoch 5 for earrings, etc.
4. **User Feedback** → "Was the sunglasses accurate?" → Tune routing weights

This combines:
- ✅ Reliable base generation (CAPTION_FIX Epoch 8)
- ✅ Specialized trait generation (adaptive routing)
- ✅ User control (à la carte selection)
- ✅ Continuous improvement (feedback loop)

---

## Next Steps

1. **Let Phase 1B test finish** (confirm it's a failure)
2. **Document Phase 1B failure** + lessons learned
3. **Prioritize à la carte system** over more training experiments
4. **Build trait catalog** from existing 203 training images
5. **Test CAPTION_FIX epochs** to populate trait→epoch mapping
6. **Prototype Gradio UI** with trait selection
7. **User testing** with real photos

---

## Success Criteria

- [ ] 90%+ user satisfaction with base punk (no traits)
- [ ] 80%+ accuracy when traits selected
- [ ] < 30 seconds generation time (base + traits)
- [ ] Users regenerate 3+ times on average (exploration)
- [ ] 50%+ users select at least one trait
- [ ] Trait selection increases user retention 2x

---

**Philosophy:** "Don't try to be psychic. Give users a menu and let them play!"

**Implementation Priority:** HIGH (after Phase 1B confirmed failure)
