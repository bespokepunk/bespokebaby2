# Punk Trait Prep Summary

This note captures the deliverables created for the pixel-trait workflow.

## Generated Assets
- `data/punks_24px/` – 193 sprites resized to 24×24 (nearest neighbour) from `Aseperite/all/`.
- `data/punks_512px/` – matching 512×512 upscales for LoRA training.
- `data/trait_suggestions.csv` – 3,088 auto-suggested trait entries (see columns below).
- `data/trait_suggestions.json` – JSON version consumed by the browser viewer.
- `trait_suggestions.html` – interactive viewer (run `python3 -m http.server` and open in a browser).

## Scripts
`python scripts/downscale_and_export.py --src Aseperite/all --out-24 data/punks_24px --out-512 data/punks_512px`
- Downscales originals to 24×24 and regenerates 512×512 versions.
- Options: `--dry-run`, `--overwrite`, `--glob`, `--size-small`, `--size-large`.

`python scripts/analyze_traits.py --src data/punks_24px --output data/trait_suggestions.csv --color-map data/color_name_map.json`
- Analyses each 24×24 sprite and writes region-based suggestions.
- Outputs columns: `sprite_id`, `category`, `variant_hint`, `color_hex`, `color_name`, `coverage_pct`, `notes`.
- Uses `data/color_name_map.json` for custom hex→name overrides; defaults to nearest CSS colour names.

## How to Use the CSV
1. Open the 24×24 PNG in Aseprite, duplicate to `.aseprite`.
2. Select a trait (hair, eyewear, etc.), copy → paste-in-place → promote to new layer.
3. Filter `data/trait_suggestions.csv` by `sprite_id`; copy the relevant `variant_hint` (e.g., `Hair_peru`, `Background_Gradient`).
4. Rename the layer with `Category_Variant[_Detail]`; adjust wording when needed.
5. Repeat per trait. The `coverage_pct` and `notes` fields help you spot-check accuracy.

## Documentation
- `docs/punk_layering_guide.md` – Layer taxonomy, ordering, background classes, palette seeds, and naming conventions.
- `data/color_name_map.json` – Initial palette overrides for skin, hair, and accessories; extend this file as you meet new colours and re-run the analysis script.

## Ongoing Workflow
1. Run `downscale_and_export.py` whenever new source PNGs arrive.
2. Run `analyze_traits.py` to refresh `trait_suggestions.csv`.
3. Use the CSV + layering guide to structure `.aseprite` files.
4. Upscale or export training sets from the layered masters (nearest neighbour).

This keeps trait naming consistent while still allowing manual spot checks for colour and style accuracy.

