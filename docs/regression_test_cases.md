# Trait Regression Test Cases

Use this checklist to verify long-standing problem sprites after each analyser run. The goal is to ensure known misclassification bugs do not reappear.

## Hair / Headwear Separation
- `lad_002_cash` – hair vs. headwear bleed (sunglasses pixels merging with outline).
- `lad_024_x` – hat vs. hair segmentation; crown should be independent.
- `lady_075_clementine` – dog ears and fur coat; ensure headwear/accessory categories are correct.
- `lady_066_monalisa-3` – hoodie vs. hair; white bear beanie must be classified as headwear.

## Eyewear vs. Eyes / Outline
- `lad_001_carbon` – sunglasses should not be in `Base_Outline`.
- `lad_002_cash` – sunglasses plus reflection; eyewear should own lens pixels.
- `lad_014_sugar` – eye vs. eyewear colour segregation.
- `lad_057_Hugh5`, `lad_057_Hughx`, `lady_099_VQ` – visors/opaque glasses; ensure tints/reflections handled consistently.

## Background Classification
- `lad_001_carbon`, `lad_057_Hugh`, `lad_057_Hugh5`, `lad_057_Hughx` – brick vs. gradient vs. solid detection.
- `lady_034_lavender`, `lady_066_monalisa-3`, `lady_065_miggs` – pinstripe vs. gradient backgrounds.
- Any sprite with vertical multi-colour backgrounds (flagged earlier as “Italian flag,” “gallery,” “candlestick”).

## Mouth & Accessories
- `lad_002_cash` – phantom cigarette detection should be disabled unless mouth accessory is present.
- `lad_014_sugar`, `lad_016_tungsten`, `lad_002_cash` – mouth colour must be distinct from skin; white highlights go to `FaceAccessory`.

## Palette / Colour Naming
- `lad_002_cash`, `lad_014_sugar`, `lady_085_IRA2` – ensure every palette colour appears in `PaletteFull` with premium naming.
- Random sampling – confirm the viewer now shows all colours (not just top five).

## Colour Naming & Language
- Confirm `PaletteFull` and trait roll-ups expose premium, LoRA-friendly colour names.
- Ensure new hex codes are captured in `data/color_name_map.json` and render the desired evocative tone.
- Spot-check naming on sprites such as `lad_002_cash`, `lad_014_sugar`, `lady_085_IRA2`.

## Trait Viewer UI
- Validate on a few sprites after data refresh:
  - Collapsible sections maintain counts.
  - Filter badges reflect current selection.
  - Roll-up behaviour (traits with subcomponents) matches expectations.
  - “Clear highlight” returns to original image.

## Validation Script
After each run, manually confirm:
```bash
python3 scripts/validate_traits.py --traits data/trait_suggestions.csv
```
- Must output `sprites=203`.
- No overlap errors (skin vs. hair/headwear, eyes vs. other face features, mouth vs. facial hair, eyewear vs. outline).
- No duplicated logical layers.
- Palette completeness reported.

Keep this file up to date; append new cases when regressions are discovered so future contributors know exactly what to check. Continuous validation plus targeted manual review on these sprites prevents known issues from sneaking back in.

