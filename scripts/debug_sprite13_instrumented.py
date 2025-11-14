#!/usr/bin/env python3
"""
Instrumented test for sprite 13 to identify infinite loop location.
Adds strategic logging to refine_results_postprocess() without modifying the original file.
"""

import sys
import time
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from analyze_traits import analyze_sprite, refine_results_postprocess
import analyze_traits as at

# Load color map
color_map_path = Path(__file__).parent.parent / "data" / "color_name_map.json"
with open(color_map_path) as f:
    color_map = json.load(f)

sprite_path = Path(__file__).parent.parent / "data" / "punks_24px" / "lad_013_caramel.png"

print(f"[INFO] Starting instrumented analysis of {sprite_path.name}", flush=True)
print(f"[INFO] This will add detailed logging to track down the infinite loop\n", flush=True)

# Wrap refine_results_postprocess with instrumentation
original_refine = at.refine_results_postprocess

def instrumented_refine(
    results,
    sprite_id,
    color_map,
    arr,
    outline_pixels,
    background_mask,
    background_hex,
    background_palette,
):
    print(f"[DEBUG] refine_results_postprocess ENTRY", flush=True)
    print(f"[DEBUG]   sprite_id={sprite_id}", flush=True)
    print(f"[DEBUG]   results count={len(results)}", flush=True)
    print(f"[DEBUG]   outline_pixels count={len(outline_pixels)}", flush=True)
    print(f"[DEBUG]   background_mask count={len(background_mask)}", flush=True)

    start_time = time.time()
    last_progress_time = start_time
    iteration_count = [0]  # Mutable for closure

    # Patch helper functions inside refine to track progress
    # We'll need to instrument the function code itself...
    # Since we can't easily patch nested functions, let's use a timeout approach

    import signal

    def timeout_handler(signum, frame):
        elapsed = time.time() - start_time
        print(f"\n[ERROR] TIMEOUT after {elapsed:.1f}s in refine_results_postprocess!", flush=True)
        print(f"[ERROR] Function appears to be in infinite loop", flush=True)
        print(f"[ERROR] Last known state:", flush=True)
        print(f"[ERROR]   sprite_id={sprite_id}", flush=True)
        raise TimeoutError(f"refine_results_postprocess exceeded 30s timeout")

    # Set 30-second timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)

    try:
        result = original_refine(
            results,
            sprite_id,
            color_map,
            arr,
            outline_pixels,
            background_mask,
            background_hex,
            background_palette,
        )
        signal.alarm(0)  # Cancel timeout
        elapsed = time.time() - start_time
        print(f"[DEBUG] refine_results_postprocess EXIT (took {elapsed:.2f}s)", flush=True)
        return result
    except TimeoutError:
        signal.alarm(0)
        raise
    except Exception as e:
        signal.alarm(0)
        print(f"[ERROR] Exception in refine_results_postprocess: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

at.refine_results_postprocess = instrumented_refine

# Also instrument analyze_sprite to see overall flow
original_analyze = at.analyze_sprite

def instrumented_analyze(path, color_map, top_colors):
    print(f"\n[DEBUG] analyze_sprite ENTRY: {path.name}", flush=True)
    start = time.time()
    try:
        results = original_analyze(path, color_map, top_colors)
        elapsed = time.time() - start
        print(f"[DEBUG] analyze_sprite EXIT: {len(results)} results in {elapsed:.2f}s\n", flush=True)
        return results
    except Exception as e:
        elapsed = time.time() - start
        print(f"[ERROR] analyze_sprite FAILED after {elapsed:.2f}s: {e}", flush=True)
        raise

at.analyze_sprite = instrumented_analyze

# Run the test
try:
    results = analyze_sprite(sprite_path, color_map, 5)
    print(f"\n✓ SUCCESS! Analyzed sprite 13 with {len(results)} results")
except TimeoutError as e:
    print(f"\n✗ TIMEOUT: {e}")
    print("\nThe function hung in refine_results_postprocess.")
    print("We need to add more granular logging inside that function.")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
