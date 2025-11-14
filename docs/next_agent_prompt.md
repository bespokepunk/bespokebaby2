# Next Agent Prompt

We’ve been refining the pixel-trait analysis pipeline for the “bespokebaby2” sprites and have a comprehensive handoff in place:

- **Primary reference:** `docs/trait_analysis_workflow.md` — outlines the entire workflow (preprocessing with `scripts/downscale_and_export.py`, incremental analysis via `scripts/analyze_all_with_cache.py`, naming conventions, validation, and outstanding tasks).
- **Regression checklist:** `docs/regression_test_cases.md` — enumerates all high-priority sprites and trait behaviours that must be re-verified after each run (hair/headwear separation, eyewear handling, mouth accessories, backgrounds, palette coverage, viewer UX, premium naming, LoRA-friendly language).

Current challenge: the analyser halts after processing 12 sprites (`lad_012_chromium.png`) both locally and on RunPod. We’ve tried the new incremental driver with per-sprite caching, but RunPod pods often reset or refuse SSH connections midway, so the job never reaches completion. The `.cache/trait_analyzer/` count has yet to advance beyond 12.

You should review the handoff doc for the complete picture, including the pipeline, requirements, colour naming/language guidelines, and outstanding tasks, then investigate why the RunPod/local runs stop after sprite 12 and how to stabilise the full 203-sprite pass (watch the cache count, log output, and pod stability). The regression checklist will be crucial once the run finally completes.

Aim for diagnosis and stabilization based on those docs; no specific next steps are prescribed beyond understanding the documented environment and the stopping issue.
