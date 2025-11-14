#!/usr/bin/env python3
"""
Incrementally analyse all sprites with caching.

This script processes each PNG in the source directory one-by-one,
writing per-sprite caches so that the run can be resumed if interrupted.
Once all sprites have been processed it aggregates the cache back into
the canonical CSV / JSON outputs used by the viewer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from analyze_traits import (
    analyze_sprite,
    load_custom_color_map,
    region_result_from_dict,
    region_result_to_dict,
    write_csv,
    write_json_output,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse sprites with per-sprite caching.")
    parser.add_argument("--src-dir", required=True, type=Path, help="Directory containing 24×24 PNG sprites.")
    parser.add_argument(
        "--cache-dir",
        required=True,
        type=Path,
        help="Directory to store per-sprite JSON caches.",
    )
    parser.add_argument(
        "--color-map",
        required=True,
        type=Path,
        help="Path to colour name map JSON.",
    )
    parser.add_argument(
        "--output-csv",
        required=True,
        type=Path,
        help="Path to write aggregated CSV output.",
    )
    parser.add_argument(
        "--output-json",
        required=True,
        type=Path,
        help="Path to write aggregated JSON output.",
    )
    parser.add_argument(
        "--top-colors",
        type=int,
        default=5,
        help="Number of dominant colours to track per sprite (default: 5).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip sprites that already have cache files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit on the number of sprites to process (useful for testing).",
    )
    return parser.parse_args()


def write_cache(cache_path: Path, data: List[dict]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    tmp_path.replace(cache_path)


def read_cache(cache_path: Path) -> List[dict]:
    with cache_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    args = parse_args()

    if not args.src_dir.exists():
        raise SystemExit(f"Source directory does not exist: {args.src_dir}")

    png_files = sorted(path for path in args.src_dir.glob("*.png"))
    if not png_files:
        raise SystemExit(f"No PNG files found in {args.src_dir}")

    color_map = load_custom_color_map(args.color_map)
    cache_dir = args.cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)

    total = len(png_files)
    limit = args.limit if args.limit > 0 else total
    processed = 0

    for index, png_path in enumerate(png_files, start=1):
        if processed >= limit:
            break

        cache_path = cache_dir / f"{png_path.stem}.json"
        if cache_path.exists() and args.resume:
            continue

        try:
            sprite_results = analyze_sprite(png_path, color_map, args.top_colors)
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"[ERROR] Failed to analyse {png_path.name}: {exc}", flush=True)
            continue

        cache_payload = [region_result_to_dict(result) for result in sprite_results]
        write_cache(cache_path, cache_payload)
        processed += 1
        print(f"[INFO] Processed {index} / {total} -> {png_path.name} ({processed} new)", flush=True)

    # Aggregate all cache files back into CSV / JSON
    aggregated = []
    cache_files = sorted(cache_dir.glob("*.json"))
    for cache_path in cache_files:
        payload = read_cache(cache_path)
        aggregated.extend(region_result_from_dict(item) for item in payload)

    if not aggregated:
        print("[WARN] No cache entries found – skipping aggregation.")
        return 0

    write_csv(args.output_csv, aggregated)
    write_json_output(args.output_json, aggregated)
    print(
        f"[INFO] Aggregated {len(cache_files)} sprites "
        f"-> {args.output_csv} / {args.output_json}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

