#!/usr/bin/env python3
"""
Batch convert 576×576 pixel-art PNGs into 24×24 masters and 512×512 upscales.

Usage example:

    python scripts/downscale_and_export.py \
        --src /Users/ilyssaevans/Documents/ONFTS/Aseperite/all \
        --out-24 /Users/ilyssaevans/Documents/GitHub/bespokebaby2/data/punks_24px \
        --out-512 /Users/ilyssaevans/Documents/GitHub/bespokebaby2/data/punks_512px
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, Tuple

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - safety message for missing dependency
    raise SystemExit(
        "Pillow is required. Install it with `pip install pillow` before running this script."
    ) from exc


LOGGER = logging.getLogger(__name__)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Batch convert pixel-art PNGs into 24×24 masters and 512×512 nearest-neighbour upscales."
        )
    )
    parser.add_argument(
        "--src",
        required=True,
        type=Path,
        help="Directory containing source 576×576 PNG files.",
    )
    parser.add_argument(
        "--out-24",
        required=True,
        type=Path,
        help="Destination directory for 24×24 outputs.",
    )
    parser.add_argument(
        "--out-512",
        required=True,
        type=Path,
        help="Destination directory for 512×512 outputs.",
    )
    parser.add_argument(
        "--size-small",
        type=int,
        default=24,
        help="Target dimension for the downscaled image (default: 24).",
    )
    parser.add_argument(
        "--size-large",
        type=int,
        default=512,
        help="Target dimension for the upscaled image (default: 512).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report actions without writing any files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing outputs if they already exist.",
    )
    parser.add_argument(
        "--glob",
        default="*.png",
        help="Glob pattern for source files (default: *.png).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args(argv)


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def iter_source_files(src_dir: Path, pattern: str) -> Iterable[Path]:
    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {src_dir}")
    yield from sorted(src_dir.rglob(pattern))


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def resize_image(
    image: Image.Image,
    dimension: int,
) -> Image.Image:
    return image.resize((dimension, dimension), resample=Image.NEAREST)


def process_image(
    src_path: Path,
    dest_24: Path,
    dest_512: Path,
    size_small: int,
    size_large: int,
    dry_run: bool,
    overwrite: bool,
) -> Tuple[Path, Path]:
    with Image.open(src_path) as img:
        img = img.convert("RGBA")
        if img.width != img.height:
            LOGGER.warning("Skipping %s (not square: %sx%s)", src_path, img.width, img.height)
            return dest_24, dest_512

        out_small = dest_24 / src_path.name
        out_large = dest_512 / src_path.name

        if not overwrite:
            if out_small.exists():
                LOGGER.debug("Skipping existing small output: %s", out_small)
            if out_large.exists():
                LOGGER.debug("Skipping existing large output: %s", out_large)
        if dry_run:
            LOGGER.info("Would process %s → (%s, %s)", src_path, out_small, out_large)
            return out_small, out_large

        if overwrite or not out_small.exists():
            resize_image(img, size_small).save(out_small)
            LOGGER.info("Saved %s", out_small)

        if overwrite or not out_large.exists():
            resize_image(img, size_large).save(out_large)
            LOGGER.info("Saved %s", out_large)

    return out_small, out_large


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    configure_logging(args.verbose)

    ensure_directory(args.out_24)
    ensure_directory(args.out_512)

    files = list(iter_source_files(args.src, args.glob))
    if not files:
        LOGGER.warning("No files found in %s matching %s", args.src, args.glob)
        return 1

    LOGGER.info("Found %d files to process.", len(files))

    for src_path in files:
        process_image(
            src_path=src_path,
            dest_24=args.out_24,
            dest_512=args.out_512,
            size_small=args.size_small,
            size_large=args.size_large,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
        )

    LOGGER.info("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

