# Trait Analysis Pipeline – Summary & Handoff

## 1. Objective
Generate authoritative trait data for every sprite (currently 203 assets) before the Aseprite cleanup/annotation phase.

## 2. Source Assets & Preprocessing
- The original high-resolution artwork lives under `runpod_package/training_data/` (and related archives). Each sprite may include captions used for LoRA training.
- `scripts/downscale_and_export.py` (plus PIL) converts those source PNGs into the canonical directories:
  - `data/punks_24px/` – the 24×24 images analysed by the pipeline.
  - `data/punks_512px/` – matching high-res references (not analysed, but useful for QA/Aseprite).
- Ensure new sprites follow the naming convention (`lad_*`, `lady_*`) and appear in both directories before running the analyser.

## 3. Key Components

| Path | Role |
| --- | --- |
| `scripts/analyze_traits.py` | Core analyser for a single sprite (colour clustering, trait extraction, naming).
| `scripts/analyze_all_with_cache.py` | Iterates all sprites, writes per-sprite caches, logs errors (continues on failure), aggregates results.
| `scripts/downscale_and_export.py` | Preprocesses original assets into 24×24 and 512×512 directories.
| `runpod_start.sh` | Convenience script for remote runs (venv, dependencies, incremental analyser, validation).
| `requirements-runpod.txt` | Minimal dependency list used on RunPod (`numpy`, `Pillow`).
| `.cache/trait_analyzer/` | Per-sprite JSON caches (one per PNG).
| `data/punks_24px/`, `data/punks_512px/` | Inputs (24×24) and high-res references (512×512).
| `data/trait_suggestions.csv` / `.json` | Aggregated outputs consumed by the viewer and downstream tooling.
| `trait_viewer.js` / `trait_suggestions.html` | Viewer bundle that renders the analysed data.
| `docs/punk_layering_guide.md` | Layer/trait taxonomy referenced by the analyser and viewer.

## 4. Colour Naming & Language Guidelines
- The analyser uses `data/color_name_map.json` plus `generate_epic_color_name` in `scripts/analyze_traits.py` to produce premium, LoRA-friendly colour names.
- Every hex code must map to:
  - A consistent, evocative name (magnetic tone, human-friendly).
  - Logical trait roll-ups so each variant surfaces a dominant colour even when multiple accents exist.
- When new colours are discovered, update `data/color_name_map.json`, verify the tone in the procedural naming engine, then regenerate outputs.

## 5. Local Usage
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-runpod.txt

python3 scripts/analyze_all_with_cache.py \
  --src-dir data/punks_24px \
  --cache-dir .cache/trait_analyzer \
  --color-map data/color_name_map.json \
  --output-csv data/trait_suggestions.csv \
  --output-json data/trait_suggestions.json \
  --resume

python3 scripts/validate_traits.py --traits data/trait_suggestions.csv
```

## 6. RunPod Workflow
> We ship `runpod_payload.zip` containing scripts, data directories, helper script, and requirements. Upload once; the cache ensures we never reprocess completed sprites.

1. Upload `runpod_payload.zip` to `/workspace`.
2. On the pod:
   ```bash
   cd /workspace
   unzip -oq runpod_payload.zip -d bespokebaby2
   cd /workspace/bespokebaby2
   bash runpod_start.sh >> runpod_analyzer.log 2>&1 &
   ```
   - Creates `.venv`, installs deps, runs incremental analyser.
   - Logs each sprite; errors are recorded but processing continues.
3. Monitor progress:
   ```bash
   tail -f runpod_analyzer.log
   # or
   watch -n 15 'ls .cache/trait_analyzer | wc -l'
   ```
   Cache count should reach 203 (one per sprite).
4. Upon completion the script runs validation automatically; aggregated outputs appear in `data/`.
5. (Optional) download results back to your machine via `scp`.

## 7. Updating the Trait Viewer / Site
1. Regenerate data (steps above).
2. Copy `data/trait_suggestions.csv` / `.json` into the viewer project if it lives elsewhere.
3. Rebuild viewer assets (`npm install && npm run build`) if using a bundler.
4. Deploy to the hosting target (GitHub Pages, S3, etc.). The viewer reads directly from `data/trait_suggestions.json`.

## 8. Validation
- `scripts/validate_traits.py` checks sprite coverage, pixel overlaps (skin vs. hair/headwear, eyes vs. other face features, mouth vs. facial hair, eyewear vs. outline), logical layer uniqueness, and palette completeness (`PaletteFull`).
- Run manually:
  ```bash
  python3 scripts/validate_traits.py --traits data/trait_suggestions.csv
  ```
  Expect `sprites=203` with no errors. `runpod_start.sh` triggers validation automatically at the end of a remote run.

## 9. Requirements & Watchlist

| Area | Requirement / Regression Tests |
| --- | --- |
| Hair & Headwear | Hair remains separate from headwear/facial hair; female sprites never receive facial hair.<br>Check `lad_002_cash`, `lad_024_x`, `lad_066_monalisa-3`, `lady_075_clementine`. |
| Eyewear vs Eyes/Outline | Eyewear (opaque/translucent/visors) owns lens pixels and reflections; no leakage into outline or eye categories.<br>Check `lad_001_carbon`, `lad_002_cash`, `lad_014_sugar`, `lady_099_VQ`, `lad_057_Hugh*`. |
| Backgrounds | Correctly classify solid, gradient, brick (incl. multi-colour), stripe, pinstripe, panel layouts.<br>Check `lad_001_carbon`, `lad_057_Hugh*`, `lady_034_lavender`, `lady_066_monalisa-3`, `lady_065_miggs`. |
| Mouth & Accessories | Mouth colour distinct from skin, accessories only when pixel evidence exists, highlights routed to `FaceAccessory`.<br>Check `lad_002_cash`, `lad_014_sugar`, `lad_016_tungsten`. |
| Palette & Naming | `PaletteFull` includes every colour with premium, LoRA-friendly names; logical roll-ups surface the dominant colour.<br>Check `lad_002_cash`, `lad_014_sugar`, `lady_085_IRA2`. |
| Trait Viewer UX | Collapsible sections, filter-aware counts, roll-up/expandable traits, clear highlight reset. |
| Coverage & Site Integration | Cache must reach 203 entries; validation must pass; viewer consumes `data/trait_suggestions.json` without manual tweaks. |

Keep this table updated whenever new bugs or UX feedback appear so future contributors know what to audit.

## 10. Outstanding Work & Future Tasks

### Immediate
- Finish the current RunPod run; confirm `ls .cache/trait_analyzer | wc -l` returns 203, then rerun validation.
- Audit the watchlist sprites (hair/headwear, eyewear bleed, backgrounds, mouth accessories, palette coverage).
- Polish and redeploy the trait viewer once data is verified.
- Maintain `data/color_name_map.json` and the premium naming language as new hexes appear (keep names LoRA-friendly yet vivid).
- Plan the Aseprite import/annotation workflow now that the trait data is stabilising.

### Future Sprites / Expansion
- Add new sprites (e.g., additional Hugh variants) to both `data/punks_24px` and `data/punks_512px`, then rerun the incremental analyser + validation.
- Update the taxonomy guide and viewer if naming conventions or layer types evolve.

Track these tasks in your issue/project board so the next contributor has clear direction. The aim is complete trait coverage with validated data, a responsive viewer, and a solid foundation for the upcoming Aseprite pass.

