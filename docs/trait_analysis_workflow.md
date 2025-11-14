# Trait Analysis Pipeline – Summary & Handoff

## Objective

Generate authoritative trait data for all pixel sprites (203 assets) before moving into the Aseprite cleanup/annotation phase. The pipeline:

1. Analyses each 24×24 PNG in `data/punks_24px`.
2. Produces per-sprite JSON caches and aggregated outputs (`data/trait_suggestions.csv` / `.json`).
3. Validates that every sprite has full trait coverage.

The datasets are also mirrored in `data/punks_512px` (high-res reference) but only the 24×24 inputs drive the analyzer.

## Key Files

| Path | Purpose |
| --- | --- |
| `scripts/analyze_traits.py` | Core analyzer used for single-sprite processing. |
| `scripts/analyze_all_with_cache.py` | Driver that iterates all sprites, writes caches, and aggregates results. |
| `runpod_start.sh` | Convenience script for remote environments (creates venv, installs deps, runs the driver, validates). |
| `requirements-runpod.txt` | Minimal dependency list for RunPod (`numpy`, `Pillow`). |
| `.cache/trait_analyzer/` | Per-sprite JSON caches (one file per sprite). |
| `data/trait_suggestions.csv` / `.json` | Aggregated outputs consumed by the trait viewer. |

## Local Usage (optional)

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

## RunPod Workflow

1. **Upload package** – `runpod_payload.zip` (contains scripts, data, helper script, requirements).
2. **On the pod**:
   ```bash
   cd /workspace
   unzip -oq runpod_payload.zip -d bespokebaby2
   cd /workspace/bespokebaby2
   bash runpod_start.sh >> runpod_analyzer.log 2>&1 &
   ```
   - Creates `.venv` (once), installs requirements, runs incremental analyzer.
   - The driver logs each sprite; failures are recorded but do not abort the run.
3. **Monitor progress**:
   ```bash
   tail -f runpod_analyzer.log
   # or
   watch -n 15 'ls .cache/trait_analyzer | wc -l'
   ```
   The cache count should reach **203** (one per sprite).
4. **After completion** – validation runs automatically; the aggregated CSV/JSON are in `data/`.
5. **Download results (optional)**:
   ```bash
   scp root@<pod-ip>:/workspace/bespokebaby2/data/trait_suggestions.csv \
       <local-path>/data/
   scp root@<pod-ip>:/workspace/bespokebaby2/data/trait_suggestions.json \
       <local-path>/data/
   scp -r root@<pod-ip>:/workspace/bespokebaby2/.cache/trait_analyzer \
       <local-path>/.cache/
   ```

### Notes

- Pods without GPUs work; the analyzer is CPU-only.
- The cache directory must persist between runs. Do **not** delete `bespokebaby2/` once the cache has started to populate.
- `runpod_start.sh` can be re-run at any time; it automatically resumes from the cache.
- Any sprite-level exception is logged as `[ERROR]` but the process continues.

## Outputs & Next Steps

Once `data/trait_suggestions.csv/.json` and `.cache/trait_analyzer/` reflect all 203 sprites, we have a consistent, validated trait dataset ready for:

1. Feeding into the web trait viewer (`trait_viewer.js`).
2. Driving validation scripts/tests.
3. Serving as the baseline before Aseprite-layer extraction and manual artwork adjustments.

Keep this document with the repo so future developers can reproduce the pipeline quickly on RunPod or locally.

