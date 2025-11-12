# Punk Layering Guide

This guide documents the naming conventions, layer order, and supporting files for building 24×24 pixel-art sprites that can be exported into 512×512 LoRA training assets.

## File Workflow
- **Source**: 576×576 PNGs (archived).
- **Downscale**: Run `python scripts/downscale_and_export.py --src <src_dir> --out-24 data/punks_24px --out-512 data/punks_512px --dry-run` to preview, then execute without `--dry-run`. All resizing uses nearest-neighbour to preserve the pixel grid.
- **Layering**: Open the 24×24 PNG in Aseprite, duplicate to `.aseprite`, and extract traits into named layers following the taxonomy below.
- **Analysis**: Run `python scripts/analyze_traits.py --src data/punks_24px --output data/trait_suggestions.csv --color-map data/color_name_map.json` to get suggested colour names and region coverage.
- **Export**: Toggle desired layer combinations, upscale to 512/576 with nearest-neighbour, export PNGs, and attach captions referencing standardized trait names.

## Layer Naming Taxonomy
Use `Category_Variant[_Detail]`. Add `_01`, `_02`, … if you retain multiple distinct variants within the same sprite.

| Category | Examples | Notes |
| --- | --- | --- |
| `Base` | `Base_Skin_Porcelain`, `Base_Outline` | Skin tone + silhouette. Outline optional. |
| `Face` | `Face_Eyes_Base`, `Face_Eyes_DeepBlue_alt2`, `Face_Brows_Straight_Dark`, `Face_Mouth_SoftSmile`, `FacialHair_Stubble_Light`, `FacialHair_Beard_Pointed_Coffee` | Use `Face_` prefix for anything anchored to the face. Facial hair gets `FacialHair_`. |
| `Hair` | `Hair_Main_Blonde_Sun`, `Hair_Highlight_Caramel`, `Hair_Accessory_Bow_Rose_Large`, `Hair_Accessory_Flower_Indigo` | Separate main fill from highlights or accessories only if you plan to swap independently. |
| `Headwear` | `Headwear_Crown_Spiked_Gold`, `Headwear_Hat_Beret_Olive`, `Headwear_Halo_Iridescent` | Use when an item sits on top of hair. |
| `Eyewear` | `Eyewear_Square_White`, `Eyewear_Shades_Coal`, `FaceAccessory_Cigarette`, `FaceAccessory_CigHolder` | Eyewear vs. other face accessories. |
| `Jewelry` | `Earrings_Hoop_Silver_Left`, `Earrings_Hoop_Silver_Right`, `Necklace_Pearl_Classic`, `NoseRing_Gold` | Split left/right if asymmetrical. |
| `Clothing` | `Clothing_Top_Suit_Brown`, `Clothing_Collar_Cream`, `Clothing_Emblem_Star_Gold` | Reserve a layer for logos/emblems only if interchangeable. |
| `Background` | `Background_Solid_Cornflower`, `Background_Gradient_PurpleBlue`, `Background_Brick_Basil`, `Background_Special_Eclipse` | Colour descriptors come from the trait suggestions CSV. |
| `Prop` / `Effect` | `Prop_Cigarette`, `Prop_Joint`, `Effect_Glow_Magenta` | Optional catch-all for handheld items or FX. |

## Layer Order
Recommended stacking from bottom to top:

1. `Background_*`
2. `Base_*` (skin, outline)
3. `Clothing_*`
4. `FacialHair_*`
5. `Face_*` (eyes, mouth, brows, nose)
6. `Hair_Main_*`
7. `Hair_Highlight_*`
8. `Hair_Accessory_*`
9. `Headwear_*`
10. `Eyewear_*`
11. `Jewelry_*`
12. `Prop_*` / `Effect_*`

Adjust as needed per sprite to achieve correct overlap.

## Colour Naming Support
- Default mappings live in `data/color_name_map.json`. Add entries when you encounter new swatches (hex keys must be lowercase).
- `scripts/analyze_traits.py` infers CSS-style names for unlisted colours and writes `data/trait_suggestions.csv` with:
  - `sprite_id`: filename stem,
  - `category`: region analysed,
  - `variant_hint`: suggested `Category_Color`,
  - `color_hex`: dominant hex value,
  - `color_name`: nearest colour name (custom or CSS),
  - `coverage_pct`: percent coverage inside the region,
  - `notes`: diagnostic context (e.g., background class).
- Use the CSV as a reference when renaming layers—copy the suggested `variant_hint` and refine only when necessary (e.g., `Hair_Main_Blonde_Sun` vs. `Hair_Main_Blonde_Gold`).

## Background Classification
The analysis script labels backgrounds as:
- `Background_Solid`: single dominant colour (`coverage > 95%`).
- `Background_Gradient`: smooth luminance change across rows/columns.
- `Background_Brick`: alternating block pattern with 45–90% coverage.
- `Background_Mixed`: none of the above.

For bricks, append the dominant colour name (`Background_Brick_Crimson`). For gradients, combine endpoints (`Background_Gradient_PurpleBlue`).

## Skin Tone Tiers
Start with the provided names; add more hex mappings if you discover new values.

| Name | Hex |
| --- | --- |
| `Skin_Porcelain` | `#f6d5b3` |
| `Skin_Peach` | `#f0b48b` |
| `Skin_Sunset` | `#d98962` |
| `Skin_Caramel` | `#b86a4a` |
| `Skin_Espresso` | `#8c4a30` |

## Hair Palette Seeds

| Name | Hex |
| --- | --- |
| `Hair_Blonde_Sun` | `#f8e26a` |
| `Hair_Blonde_Gold` | `#f4c542` |
| `Hair_Brown_Walnut` | `#7a4b1f` |
| `Hair_Brown_Mocha` | `#532b17` |
| `Hair_Brown_Espresso` | `#2f1a10` |
| `Hair_Black_Plum` | `#271f3a` |
| `Hair_Black_Ink` | `#15151a` |

## Accessories & Metals

| Layer Prefix | Example Names | Notes |
| --- | --- | --- |
| `Hair_Accessory_*` | `Hair_Accessory_Bow_Rose`, `Hair_Accessory_Bow_Ruby`, `Hair_Accessory_Flower_Indigo`, `Hair_Accessory_Clip_Silver` | Use size descriptors (`Small`, `Large`) when variants exist. |
| `Eyewear_*` | `Eyewear_Square_White`, `Eyewear_Shades_Coal` | Add `_Logo_*` if branding swaps. |
| `Jewelry_*` | `Earrings_Hoop_Silver`, `Necklace_Beads_Ochre` | For mixed metals, separate base vs. gem colour with `_Gem_*`. |

## Captions & Metadata
- Generate captions from layer names: e.g., “pixel art woman with `Hair_Main_Blonde_Sun`, `Eyewear_Square_White`, `Background_Gradient_PurpleBlue`”.
- Store sprite-to-layer mappings alongside captions for reproducibility (`data/trait_manifest.json` recommended in future automation).

## Quality Checklist
- Pixel grid confirmed at 24×24 before layering.
- Each trait sits on its own layer with clear naming.
- Background classification verified.
- Palette entries updated for any new hex values.
- 512×512 exports generated with nearest-neighbour and saved alongside captions.

Following this structure keeps manual work predictable and sets up automation hooks for future scripts that read layer names, export combinations, or produce LoRA training manifests.**

