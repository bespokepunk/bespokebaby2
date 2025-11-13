#!/usr/bin/env python3
"""
Analyse 24×24 pixel-art sprites to suggest trait names and palette information.

Example usage:

    python scripts/analyze_traits.py \
        --src /Users/ilyssaevans/Documents/GitHub/bespokebaby2/data/punks_24px \
        --output /Users/ilyssaevans/Documents/GitHub/bespokebaby2/data/trait_suggestions.csv \
        --color-map /Users/ilyssaevans/Documents/GitHub/bespokebaby2/data/color_name_map.json
"""

from __future__ import annotations

import argparse
import colorsys
import csv
import json
import logging
import math
import re
from collections import Counter, deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Tuple

import numpy as np
from PIL import Image

LOGGER = logging.getLogger(__name__)


# Basic CSS-like colour names for fallback matching.
CSS_COLOR_NAME_TO_HEX: Dict[str, str] = {
    "black": "#000000",
    "dimgray": "#696969",
    "gray": "#808080",
    "darkgray": "#a9a9a9",
    "silver": "#c0c0c0",
    "lightgray": "#d3d3d3",
    "gainsboro": "#dcdcdc",
    "white": "#ffffff",
    "snow": "#fffafa",
    "ivory": "#fffff0",
    "beige": "#f5f5dc",
    "antiquewhite": "#faebd7",
    "navajowhite": "#ffdead",
    "tan": "#d2b48c",
    "burlywood": "#deb887",
    "sandybrown": "#f4a460",
    "peru": "#cd853f",
    "chocolate": "#d2691e",
    "sienna": "#a0522d",
    "saddlebrown": "#8b4513",
    "maroon": "#800000",
    "darkred": "#8b0000",
    "firebrick": "#b22222",
    "crimson": "#dc143c",
    "red": "#ff0000",
    "tomato": "#ff6347",
    "coral": "#ff7f50",
    "salmon": "#fa8072",
    "darksalmon": "#e9967a",
    "lightcoral": "#f08080",
    "orange": "#ffa500",
    "darkorange": "#ff8c00",
    "gold": "#ffd700",
    "goldenrod": "#daa520",
    "darkgoldenrod": "#b8860b",
    "khaki": "#f0e68c",
    "darkkhaki": "#bdb76b",
    "olive": "#808000",
    "yellow": "#ffff00",
    "lightyellow": "#ffffe0",
    "greenyellow": "#adff2f",
    "chartreuse": "#7fff00",
    "lime": "#00ff00",
    "limegreen": "#32cd32",
    "forestgreen": "#228b22",
    "seagreen": "#2e8b57",
    "mediumseagreen": "#3cb371",
    "darkseagreen": "#8fbc8f",
    "darkolivegreen": "#556b2f",
    "teal": "#008080",
    "darkcyan": "#008b8b",
    "lightseagreen": "#20b2aa",
    "turquoise": "#40e0d0",
    "paleturquoise": "#afeeee",
    "darkturquoise": "#00ced1",
    "aqua": "#00ffff",
    "deepskyblue": "#00bfff",
    "dodgerblue": "#1e90ff",
    "cornflowerblue": "#6495ed",
    "royalblue": "#4169e1",
    "steelblue": "#4682b4",
    "midnightblue": "#191970",
    "navy": "#000080",
    "blue": "#0000ff",
    "slateblue": "#6a5acd",
    "mediumpurple": "#9370db",
    "darkorchid": "#9932cc",
    "purple": "#800080",
    "darkmagenta": "#8b008b",
    "magenta": "#ff00ff",
    "mediumvioletred": "#c71585",
    "deeppink": "#ff1493",
    "hotpink": "#ff69b4",
    "pink": "#ffc0cb",
}

ACCESSORY_WHITE_HEXES = {"#ffffff", "#fefefe", "#fdfdfd"}

OUTLINE_HEX_CODES = {"#000000", "#111111", "#181818", "#1e1e1e", "#241010", "#281002"}


REGION_SLICES = [
    ("Skin", (slice(7, 18), slice(8, 16), 1)),
    ("Headwear", (slice(0, 8), slice(2, 22), 2)),
    ("Hair", (slice(3, 13), slice(2, 22), 2)),
    ("Eyes", (slice(9, 12), slice(8, 16), 2)),
    ("Mouth", (slice(12, 16), slice(9, 15), 1)),
    ("Clothing", (slice(15, 24), slice(5, 19), 2)),
    ("Accessory_Face", (slice(8, 16), slice(6, 18), 2)),
    ("NeckAccessory", (slice(17, 24), slice(6, 18), 1)),
]


@dataclass
class RegionResult:
    sprite_id: str
    category: str
    variant_hint: str
    color_hex: str
    color_name: str
    coverage_pct: float
    notes: str
    pixel_mask: str = ""


@dataclass
class RegionBounds:
    row_start: int
    row_end: int
    col_start: int
    col_end: int

    @property
    def row_mid(self) -> float:
        return (self.row_start + self.row_end) / 2



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-suggest trait colours for 24×24 sprites.")
    parser.add_argument("--src", required=True, type=Path, help="Directory of 24×24 PNG sprites.")
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Destination CSV for trait suggestions.",
    )
    parser.add_argument(
        "--color-map",
        type=Path,
        help="JSON file mapping hex colours to custom names.",
    )
    parser.add_argument(
        "--top-colors",
        type=int,
        default=5,
        help="Number of dominant colours to record per sprite for background analysis (default: 5).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )


def load_custom_color_map(path: Path | None) -> Dict[str, str]:
    if not path:
        return {}
    if not path.exists():
        LOGGER.warning("Colour map file not found: %s", path)
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return {hex_code.lower(): name for hex_code, name in data.items()}


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def squared_distance(rgb_a: Tuple[int, int, int], rgb_b: Tuple[int, int, int]) -> float:
    return sum((a - b) ** 2 for a, b in zip(rgb_a, rgb_b))


def nearest_css_name(
    hex_code: str,
    custom_map: Dict[str, str],
) -> str:
    lowered = hex_code.lower()
    if lowered in custom_map:
        return custom_map[lowered]
    return describe_color_custom(lowered)


def describe_color_custom(hex_code: str) -> str:
    r, g, b = hex_to_rgb(hex_code)
    rn = r / 255.0
    gn = g / 255.0
    bn = b / 255.0
    h, l, s = colorsys.rgb_to_hls(rn, gn, bn)
    hue = (h * 360.0) % 360.0

    if s < 0.12:
        if l < 0.18:
            base = "GrayCharcoal"
        elif l < 0.38:
            base = "GraySlate"
        elif l < 0.6:
            base = "GrayStone"
        else:
            base = "GrayPearl"
        return base

    def lightness_descriptor(value: float) -> str:
        if value < 0.2:
            return "Deep"
        if value < 0.35:
            return "Dark"
        if value < 0.55:
            return "Rich"
        if value < 0.75:
            return "Soft"
        return "Pale"

    if 10 <= hue < 45:
        base = "BrownClay"
    elif 45 <= hue < 70:
        base = "OchreGold"
    elif 70 <= hue < 110:
        base = "OliveGreen"
    elif 110 <= hue < 150:
        base = "ForestGreen"
    elif 150 <= hue < 200:
        base = "TealBay"
    elif 200 <= hue < 250:
        base = "CobaltBlue"
    elif 250 <= hue < 290:
        base = "IndigoNight"
    elif 290 <= hue < 330:
        base = "PlumViolet"
    else:
        base = "BrickRust"

    descriptor = lightness_descriptor(l)
    return f"{descriptor}{base}"


def describe_color(rgb: Tuple[int, int, int]) -> str:
    r, g, b = [c / 255.0 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue_names = ["Red", "Orange", "Yellow", "Green", "Teal", "Blue", "Purple", "Magenta"]
    hue = int(h * 360)

    if s < 0.12:
        base = "Gray"
    else:
        index = int(((hue + 22.5) % 360) / 45)
        base = hue_names[index]

    if l < 0.2:
        prefix = "Dark"
    elif l < 0.4:
        prefix = "Deep"
    elif l < 0.6:
        prefix = ""
    elif l < 0.8:
        prefix = "Light"
    else:
        prefix = "VeryLight"

    return f"{prefix}_{base}" if prefix else base


def collect_colors(region: np.ndarray) -> Counter:
    counter: Counter = Counter()
    for pixel in region.reshape(-1, region.shape[-1]):
        r, g, b, a = [int(v) for v in pixel]
        if a < 16:
            continue
        counter[(r, g, b)] += 1
    return counter


def dominant_colors(counter: Counter, top_n: int) -> List[Tuple[str, int]]:
    return [(rgb_to_hex(rgb), count) for rgb, count in counter.most_common(top_n)]


def detect_vertical_stripes(arr: np.ndarray) -> List[Tuple[str, float]]:
    rows, cols = arr.shape[:2]
    if cols < 6:
        return []
    sample_rows = sorted(
        {0, rows // 3, (2 * rows) // 3, rows - 1}
    )
    segments_per_row: List[List[Tuple[Tuple[int, int, int], int]]] = []
    for row_idx in sample_rows:
        row = arr[row_idx]
        segments: List[Tuple[Tuple[int, int, int], int]] = []
        sum_rgb = [int(v) for v in row[0][:3]]
        length = 1
        for col in range(1, cols):
            rgb = tuple(int(v) for v in row[col][:3])
            avg_rgb = tuple(round(sum_rgb[i] / length) for i in range(3))
            if squared_distance(rgb, avg_rgb) <= 120:
                sum_rgb[0] += rgb[0]
                sum_rgb[1] += rgb[1]
                sum_rgb[2] += rgb[2]
                length += 1
            else:
                avg_rgb = tuple(round(sum_rgb[i] / length) for i in range(3))
                segments.append((avg_rgb, length))
                sum_rgb = [rgb[0], rgb[1], rgb[2]]
                length = 1
        avg_rgb = tuple(round(sum_rgb[i] / length) for i in range(3))
        segments.append((avg_rgb, length))
        segments_per_row.append(segments)
    segment_counts = {len(seg) for seg in segments_per_row}
    if len(segment_counts) != 1:
        return []
    stripe_count = segment_counts.pop()
    if stripe_count < 2 or stripe_count > 6:
        return []
    stripe_data: List[Tuple[str, float]] = []
    total_ratio = 0.0
    for idx in range(stripe_count):
        lengths = [seg[idx][1] for seg in segments_per_row]
        if min(lengths) < max(2, cols * 0.08):
            return []
        if max(lengths) - min(lengths) > 2:
            return []
        total_len = sum(lengths)
        weighted_rgb = [0.0, 0.0, 0.0]
        for seg, length in zip(segments_per_row, lengths):
            rgb = seg[idx][0]
            weighted_rgb[0] += rgb[0] * length
            weighted_rgb[1] += rgb[1] * length
            weighted_rgb[2] += rgb[2] * length
        avg_rgb = tuple(
            int(round(weighted_rgb[i] / total_len)) for i in range(3)
        )
        for seg in segments_per_row:
            if squared_distance(seg[idx][0], avg_rgb) > 200:
                return []
        ratio = (sum(lengths) / len(lengths)) / cols
        total_ratio += ratio
        stripe_data.append((rgb_to_hex(avg_rgb), ratio))
    if total_ratio < 0.9:
        return []
    return stripe_data


def classify_background(arr: np.ndarray) -> Tuple[str, float, str, List[Tuple[str, int]], List[str]]:
    h, w, _ = arr.shape
    all_colors = collect_colors(arr)
    if not all_colors:
        return "#000000", 0.0, "Unknown", [], []

    top_colors = all_colors.most_common()
    main_hex = rgb_to_hex(top_colors[0][0])
    coverage = top_colors[0][1] / float(h * w)

    unique_count = len(all_colors)
    classification = "Solid"

    stripe_info = detect_vertical_stripes(arr)
    if stripe_info:
        classification = "Stripe"
        main_hex = stripe_info[0][0]
        coverage = stripe_info[0][1]
        stripe_palette = [
            (hex_code, max(1, int(round(ratio * h * w))))
            for hex_code, ratio in stripe_info
        ]
        return main_hex, coverage, classification, stripe_palette, [hex_code for hex_code, _ in stripe_info]

    if unique_count > 1 and coverage < 0.95:
        if looks_like_brick(arr, top_colors[0][0]):
            classification = "Brick"
        elif looks_like_gradient(arr):
            classification = "Gradient"
        else:
            classification = "Mixed"

    edge_ratio = edge_color_ratio(arr, top_colors[0][0])
    if classification in {"Gradient", "Mixed"} and edge_ratio >= 0.5 and coverage >= 0.18:
        classification = "Solid"

    if classification == "Brick":
        if len(top_colors) < 2 or (top_colors[1][1] / float(h * w)) < 0.18:
            classification = "Solid"
    if classification == "Mixed" and len(top_colors) >= 2:
        second_coverage = top_colors[1][1] / float(h * w)
        color_distance = squared_distance(top_colors[0][0], top_colors[1][0]) ** 0.5
        if color_distance < 45 and second_coverage > 0.05 and edge_ratio < 0.45:
            classification = "Gradient"
        elif coverage > 0.75 and second_coverage < 0.12 and color_distance < 60:
            classification = "Solid"

    return main_hex, coverage, classification, dominant_colors(all_colors, 5), []


def looks_like_gradient(arr: np.ndarray) -> bool:
    h, w, _ = arr.shape
    # sample colour per row and per column and test for smooth transitions
    def luminance(rgb):
        r, g, b = [c / 255.0 for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    row_colors = [dominant_color_for_slice(arr, slice(y, y + 1), slice(0, w)) for y in range(h)]
    col_colors = [dominant_color_for_slice(arr, slice(0, h), slice(x, x + 1)) for x in range(w)]

    row_changes = sum(abs(luminance(row_colors[i]) - luminance(row_colors[i - 1])) for i in range(1, h))
    col_changes = sum(abs(luminance(col_colors[i]) - luminance(col_colors[i - 1])) for i in range(1, w))

    smooth_rows = row_changes / max(h - 1, 1) < 0.2
    smooth_cols = col_changes / max(w - 1, 1) < 0.2
    return smooth_rows or smooth_cols


def dominant_color_for_slice(arr: np.ndarray, row_slice: slice, col_slice: slice) -> Tuple[int, int, int]:
    counter = collect_colors(arr[row_slice, col_slice])
    if not counter:
        return (0, 0, 0)
    return counter.most_common(1)[0][0]


def looks_like_brick(arr: np.ndarray, background_rgb: Tuple[int, int, int]) -> bool:
    h, w, _ = arr.shape
    bg = np.array(background_rgb, dtype=np.uint8)
    mask = (arr[:, :, :3] == bg).all(axis=2)
    # brick backgrounds usually have moderate coverage from one tone
    coverage = mask.mean()
    if coverage < 0.25 or coverage > 0.9:
        return False

    # check for alternating pattern every few rows/columns
    row_pattern = []
    for y in range(h):
        row_pattern.append(mask[y].tolist())
    alternating_rows = sum(1 for y in range(1, h) if row_pattern[y] != row_pattern[y - 1])
    return alternating_rows > h / 3


def edge_color_ratio(arr: np.ndarray, rgb: Tuple[int, int, int]) -> float:
    h, w, _ = arr.shape
    target = np.array(rgb, dtype=np.uint8)
    total = 2 * w + 2 * (h - 2 if h > 2 else 0)
    if total <= 0:
        return 0.0
    matches = 0
    for x in range(w):
        if np.array_equal(arr[0, x, :3], target):
            matches += 1
        if np.array_equal(arr[h - 1, x, :3], target):
            matches += 1
    for y in range(1, h - 1):
        if np.array_equal(arr[y, 0, :3], target):
            matches += 1
        if np.array_equal(arr[y, w - 1, :3], target):
            matches += 1
    return matches / total


def compute_pixel_mask(
    arr: np.ndarray,
    row_slice: slice,
    col_slice: slice,
    hex_code: str,
) -> str:
    target_rgb = hex_to_rgb(hex_code)
    pixels: List[str] = []
    for row in range(row_slice.start, row_slice.stop):
        for col in range(col_slice.start, col_slice.stop):
            r, g, b, a = [int(x) for x in arr[row, col]]
            if a < 16:
                continue
            if (r, g, b) == target_rgb:
                pixels.append(f"{row},{col}")
    return ";".join(pixels)


def collect_background_pixels(arr: np.ndarray, primary_hex: str, palette: List[Tuple[str, int]]) -> str:
    rows, cols = arr.shape[:2]
    candidate_hexes = {primary_hex.lower()}
    border_rows = set(range(rows))
    rows_with_color: Dict[str, set[int]] = {}
    for hex_code, _ in palette:
        rows_with_color[hex_code.lower()] = set()
    for row in range(rows):
        for col in range(cols):
            r, g, b, a = [int(x) for x in arr[row, col]]
            if a < 16:
                continue
            hex_code = rgb_to_hex((r, g, b)).lower()
            if hex_code in rows_with_color:
                rows_with_color[hex_code].add(row)
    for lowered, row_set in rows_with_color.items():
        if row_set == border_rows:
            candidate_hexes.add(lowered)
    candidate_rgbs = {hex_to_rgb(code) for code in candidate_hexes}

    visited: set[Tuple[int, int]] = set()
    mask: set[Tuple[int, int]] = set()
    queue: Deque[Tuple[int, int]] = deque()

    def try_enqueue(row: int, col: int) -> None:
        if (row, col) in visited:
            return
        r, g, b, a = [int(x) for x in arr[row, col]]
        if a < 16:
            visited.add((row, col))
            return
        if (r, g, b) not in candidate_rgbs:
            visited.add((row, col))
            return
        visited.add((row, col))
        mask.add((row, col))
        queue.append((row, col))

    for col in range(cols):
        try_enqueue(0, col)
        try_enqueue(rows - 1, col)
    for row in range(rows):
        try_enqueue(row, 0)
        try_enqueue(row, cols - 1)

    while queue:
        row, col = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr = row + dr
            nc = col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                try_enqueue(nr, nc)

    return ";".join(f"{row},{col}" for row, col in sorted(mask))


def collect_outline_pixels(
    arr: np.ndarray,
    outline_hex_codes: set[str],
    background_mask: set[Tuple[int, int]],
) -> set[Tuple[int, int]]:
    rows, cols = arr.shape[:2]
    outline_coords: set[Tuple[int, int]] = set()
    outline_rgbs = {hex_to_rgb(code) for code in outline_hex_codes}
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for row in range(rows):
        for col in range(cols):
            r, g, b, a = [int(x) for x in arr[row, col]]
            if a < 16:
                continue
            rgb = (r, g, b)
            if rgb not in outline_rgbs:
                continue
            if (row, col) in background_mask:
                continue
            for dr, dc in directions:
                nr = row + dr
                nc = col + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    nr_r, nr_g, nr_b, nr_a = [int(x) for x in arr[nr, nc]]
                    if nr_a < 16:
                        continue
                    if (nr_r, nr_g, nr_b) != rgb:
                        outline_coords.add((row, col))
                        break
    return outline_coords


def analyze_region(
    sprite_id: str,
    arr: np.ndarray,
    category: str,
    row_slice: slice,
    col_slice: slice,
    top_n: int,
    ignore_hexes: Iterable[str],
    color_map: Dict[str, str],
) -> List[RegionResult]:
    region = arr[row_slice, col_slice]
    colors = collect_colors(region)
    for hex_code in ignore_hexes:
        rgb = hex_to_rgb(hex_code)
        if rgb in colors:
            colors.pop(rgb)
    if not colors:
        return []

    total_pixels = sum(colors.values())
    if category in {"Clothing", "Headwear"} and len(colors) > 1:
        black_rgb = (0, 0, 0)
        black_count = colors.get(black_rgb, 0)
        if black_count and (black_count / total_pixels) < 0.6:
            colors.pop(black_rgb, None)
            total_pixels -= black_count
            if not colors or total_pixels <= 0:
                return []
    suggestions: List[RegionResult] = []
    for rank, (hex_code, count) in enumerate(dominant_colors(colors, top_n), start=1):
        coverage = 100.0 * count / total_pixels
        if coverage < 1.0:
            continue
        color_name = nearest_css_name(hex_code, color_map)
        variant_hint = f"{category}_{color_name.replace(' ', '_')}"
        if rank > 1:
            variant_hint += f"_alt{rank}"
        notes = f"region_rows={row_slice.start}:{row_slice.stop},cols={col_slice.start}:{col_slice.stop}"
        pixel_mask = compute_pixel_mask(arr, row_slice, col_slice, hex_code)
        suggestions.append(
            RegionResult(
                sprite_id=sprite_id,
                category=category,
                variant_hint=variant_hint,
                color_hex=hex_code,
                color_name=color_name,
                coverage_pct=round(coverage, 2),
                notes=notes,
                pixel_mask=pixel_mask,
            )
        )
    return suggestions


REGION_PATTERN = re.compile(r"region_rows=(\d+):(\d+),cols=(\d+):(\d+)")


def parse_region_bounds(notes: str) -> RegionBounds | None:
    match = REGION_PATTERN.search(notes)
    if not match:
        return None
    row_start, row_end, col_start, col_end = map(int, match.groups())
    return RegionBounds(row_start=row_start, row_end=row_end, col_start=col_start, col_end=col_end)


def update_category_prefix(result: RegionResult, new_category: str) -> None:
    if result.category == new_category:
        return
    prefix = f"{result.category}_"
    if result.variant_hint.startswith(prefix):
        suffix = result.variant_hint[len(prefix) :]
    else:
        parts = result.variant_hint.split("_", 1)
        suffix = parts[1] if len(parts) == 2 else result.variant_hint
    result.category = new_category
    result.variant_hint = f"{new_category}_{suffix}" if suffix else new_category


def refine_result(result: RegionResult) -> None:
    bounds = parse_region_bounds(result.notes)
    if result.category == "Accessory_Face":
        if not bounds:
            update_category_prefix(result, "FaceAccessory")
            return
        if bounds.row_mid <= 7.5:
            update_category_prefix(result, "Headwear")
        elif bounds.row_mid >= 16.0:
            update_category_prefix(result, "NeckAccessory")
        else:
            update_category_prefix(result, "FaceAccessory")
    elif result.category == "Headwear":
        if bounds and bounds.row_mid > 11.5:
            update_category_prefix(result, "FaceAccessory")


def analyze_sprite(
    path: Path,
    color_map: Dict[str, str],
    top_colors: int,
) -> List[RegionResult]:
    sprite_id = path.stem
    with Image.open(path) as img:
        arr = np.array(img.convert("RGBA"))

    if arr.shape[0] != 24 or arr.shape[1] != 24:
        LOGGER.warning("Skipping %s (expected 24×24, got %sx%s)", path, arr.shape[1], arr.shape[0])
        return []

    results: List[RegionResult] = []

    total_pixels = 24 * 24

    bg_hex, bg_cov, bg_class, bg_palette, stripe_colors = classify_background(arr)
    bg_name = nearest_css_name(bg_hex, color_map)
    variant_suffix = describe_background_variant(
        bg_class, bg_palette, color_map, total_pixels, stripe_colors
    )
    mask = collect_background_pixels(arr, bg_hex, bg_palette)
    background_mask_set = parse_pixel_mask(mask)
    outline_pixels = collect_outline_pixels(arr, OUTLINE_HEX_CODES, background_mask_set)
    final_bg_class = variant_suffix.split("_", 1)[0] if variant_suffix else bg_class
    notes = f"class={final_bg_class}; coverage={bg_cov:.2f}; palette={bg_palette}"
    results.append(
        RegionResult(
            sprite_id=sprite_id,
            category="Background",
            variant_hint=f"Background_{variant_suffix}",
            color_hex=bg_hex,
            color_name=bg_name,
            coverage_pct=round(bg_cov * 100.0, 2),
            notes=notes,
            pixel_mask=mask,
        )
    )

    if background_mask_set and final_bg_class.startswith("Brick"):
        bg_color_counts: Dict[str, set[Tuple[int, int]]] = {}
        for row, col in background_mask_set:
            r, g, b = [int(arr[row, col][k]) for k in range(3)]
            hex_code = rgb_to_hex((r, g, b)).lower()
            bg_color_counts.setdefault(hex_code, set()).add((row, col))
        for hex_code, coords in bg_color_counts.items():
            if hex_code == bg_hex.lower():
                continue
            coverage_pct = round(len(coords) / total_pixels * 100.0, 2)
            if coverage_pct < 1.0:
                continue
            color_name = nearest_css_name(hex_code, color_map)
            accent_variant = f"Background_BrickAccent_{color_name}".replace(" ", "")
            results.append(
                RegionResult(
                    sprite_id=sprite_id,
                    category="Background",
                    variant_hint=accent_variant,
                    color_hex=hex_code,
                    color_name=color_name,
                    coverage_pct=coverage_pct,
                    notes="brick_accent",
                    pixel_mask=mask_to_string(coords),
                )
            )

    ignore_hexes = [bg_hex]
    skin_hexes: set[str] = set()

    for category, (rows, cols, top_n) in REGION_SLICES:
        local_ignore = ignore_hexes
        if category == "Mouth":
            local_ignore = [hx for hx in ignore_hexes if hx.lower() not in skin_hexes]
        suggestions = analyze_region(
            sprite_id=sprite_id,
            arr=arr,
            category=category,
            row_slice=rows,
            col_slice=cols,
            top_n=top_n,
            ignore_hexes=local_ignore,
            color_map=color_map,
        )
        for suggestion in suggestions:
            refine_result(suggestion)
            results.append(suggestion)
        if category == "Skin":
            for suggestion in suggestions:
                skin_hexes.add(suggestion.color_hex.lower())
        if suggestions and category in {"Skin", "Hair", "Headwear", "Accessory_Face", "NeckAccessory"}:
            for suggestion in suggestions[:2]:
                if suggestion.coverage_pct >= 5.0:
                    ignore_hexes.append(suggestion.color_hex)

    # Record dominant palette overall for quick reference.
    all_colors = collect_colors(arr)
    for hex_code, count in dominant_colors(all_colors, top_colors):
        color_name = nearest_css_name(hex_code, color_map)
        coverage = 100.0 * count / (24 * 24)
        results.append(
            RegionResult(
                sprite_id=sprite_id,
                category="Palette",
                variant_hint=f"Color_{color_name}",
                color_hex=hex_code,
                color_name=color_name,
                coverage_pct=round(coverage, 2),
                notes="global_dominant_color",
            )
        )

    return refine_results_postprocess(
        results,
        sprite_id,
        color_map,
        arr,
        outline_pixels,
        background_mask_set,
        bg_hex,
        bg_palette,
    )


def write_csv(path: Path, records: List[RegionResult]) -> None:
    ensure_directory(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "sprite_id",
                "category",
                "variant_hint",
                "color_hex",
                "color_name",
                "coverage_pct",
                "notes",
                "pixel_mask",
            ]
        )
        for row in records:
            writer.writerow(
                [
                    row.sprite_id,
                    row.category,
                    row.variant_hint,
                    row.color_hex,
                    row.color_name,
                    f"{row.coverage_pct:.2f}",
                    row.notes,
                    row.pixel_mask,
                ]
            )


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def describe_background_variant(
    bg_class: str,
    palette: List[Tuple[str, int]],
    color_map: Dict[str, str],
    total_pixels: int,
    stripe_colors: List[str] | None = None,
) -> str:
    if not palette:
        return bg_class
    primary = nearest_css_name(palette[0][0], color_map)
    if stripe_colors:
        stripe_names: List[str] = []
        for hex_code in stripe_colors:
            name = nearest_css_name(hex_code, color_map)
            if name not in stripe_names:
                stripe_names.append(name)
        suffix = "_".join(stripe_names).replace(" ", "")
        return f"Stripe_{suffix}"
    if bg_class == "Brick":
        if len(palette) < 2:
            return f"Brick_{primary}".replace(" ", "")
        secondary_count = palette[1][1]
        if secondary_count < 0.18 * total_pixels:
            return f"Brick_{primary}".replace(" ", "")
        secondary = nearest_css_name(palette[1][0], color_map)
        components = [primary, secondary]
        if len(palette) > 2 and palette[2][1] >= 0.08 * total_pixels:
            tertiary = nearest_css_name(palette[2][0], color_map)
            if tertiary != secondary:
                components.append(tertiary)
        unique = []
        for name in components:
            if name not in unique:
                unique.append(name)
        suffix = "_".join(unique).replace(" ", "")
        return f"Brick_{suffix}"
    if bg_class == "Gradient":
        if len(palette) < 2:
            return f"Solid_{primary}".replace(" ", "")
        secondary = nearest_css_name(palette[1][0], color_map)
        if secondary == primary:
            return f"Solid_{primary}".replace(" ", "")
        return f"Gradient_{primary}_{secondary}".replace(" ", "")
    return f"Solid_{primary}".replace(" ", "")


def parse_pixel_mask(mask: str) -> set[Tuple[int, int]]:
    if not mask:
        return set()
    coords = set()
    for pair in mask.split(";"):
        try:
            row_str, col_str = pair.split(",")
            coords.add((int(row_str), int(col_str)))
        except ValueError:
            continue
    return coords


def mask_to_string(coords: set[Tuple[int, int]]) -> str:
    if not coords:
        return ""
    return ";".join(f"{row},{col}" for row, col in sorted(coords))


def is_dark_color(hex_code: str) -> bool:
    r, g, b = hex_to_rgb(hex_code)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return luminance < 90


def luminance_from_hex(hex_code: str) -> float:
    r, g, b = hex_to_rgb(hex_code)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def refine_results_postprocess(
    results: List[RegionResult],
    sprite_id: str,
    color_map: Dict[str, str],
    arr: np.ndarray,
    outline_pixels: set[Tuple[int, int]],
    background_mask: set[Tuple[int, int]],
    background_hex: str,
    background_palette: List[Tuple[str, int]],
) -> List[RegionResult]:
    from collections import defaultdict, Counter

    total_pixels = 24 * 24
    outline_set = set(outline_pixels)

    category_entries: Dict[str, List[Tuple[RegionResult, set[Tuple[int, int]]]]] = defaultdict(list)
    for res in results:
        mask_set = parse_pixel_mask(res.pixel_mask)
        category_entries[res.category].append((res, mask_set))

    background_entries = category_entries.get("Background", [])
    refined: List[RegionResult] = []
    category_to_entry: Dict[str, List[Tuple[RegionResult, set[Tuple[int, int]]]]] = defaultdict(list)
    background_hexes: set[str] = set()
    for row, col in background_mask:
        r, g, b = [int(arr[row, col][k]) for k in range(3)]
        background_hexes.add(rgb_to_hex((r, g, b)).lower())
    if not background_hexes:
        background_hexes = {background_hex.lower()}
    if background_entries:
        primary_res, primary_mask = background_entries[0]
        if background_mask:
            primary_mask = set(background_mask)
        primary_res.pixel_mask = mask_to_string(primary_mask)
        primary_res.coverage_pct = round(len(primary_mask) / total_pixels * 100.0, 2)
        refined.append(primary_res)
        category_to_entry["Background"].append((primary_res, primary_mask))
        for extra_res, extra_mask in background_entries[1:]:
            extra_mask = parse_pixel_mask(extra_res.pixel_mask)
            extra_res.pixel_mask = mask_to_string(extra_mask)
            extra_res.coverage_pct = round(len(extra_mask) / total_pixels * 100.0, 2)
            refined.append(extra_res)
            category_to_entry["Background"].append((extra_res, extra_mask))

    skin_union: set[Tuple[int, int]] = set()
    skin_colors_map: Dict[str, set[Tuple[int, int]]] = defaultdict(set)
    skin_color_set: set[str] = set()
    hair_color_set: set[str] = set()
    mouth_union: set[Tuple[int, int]] = set()

    hair_union: set[Tuple[int, int]] = set()
    for res, mask in category_entries.get("Hair", []):
        hair_union |= mask
        hair_color_set.add(res.color_hex.lower())

    headwear_entries = category_entries.get("Headwear", [])
    clothing_union: set[Tuple[int, int]] = set()
    for _, mask in category_entries.get("Clothing", []):
        clothing_union |= mask

    eye_union: set[Tuple[int, int]] = set()
    for _, mask in category_entries.get("Eyes", []):
        eye_union |= mask

    outline_candidates = outline_set.copy()

    # Absorb face accessory dots (pupils, nose) into outline.
    kept_face_accessories: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
    for res, mask in category_entries.get("FaceAccessory", []):
        if not mask:
            continue
        if mask and mask.issubset(eye_union):
            continue
        if (res.color_hex.lower() in OUTLINE_HEX_CODES or is_dark_color(res.color_hex)) and len(mask) <= 3:
            if all(6 <= row <= 16 for row, _ in mask):
                outline_candidates |= mask
                continue
        kept_face_accessories.append((res, mask))

    # Merge clothing pixels that overlap hair/headwear into their parent categories.
    processed_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []

    # Helper to register entries consistently
    def register_entry(res: RegionResult, mask: set[Tuple[int, int]]):
        processed_entries.append((res, mask))
        category_to_entry[res.category].append((res, mask))
        if res.category == "Hair":
            hair_union.update(mask)
            hair_color_set.add(res.color_hex.lower())

    def update_skin_tracking(hex_code: str, coords: set[Tuple[int, int]]) -> None:
        if not coords:
            return
        skin_union.update(coords)
        lowered = hex_code.lower()
        skin_colors_map[lowered] |= coords
        skin_color_set.add(lowered)

    def touches_skin(coords: set[Tuple[int, int]]) -> bool:
        if not coords or not skin_union:
            return False
        for row, col in coords:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (row + dr, col + dc) in skin_union:
                        return True
        return False

    def is_facial_hair_candidate(mask_set: set[Tuple[int, int]]) -> bool:
        if not mask_set:
            return False
        rows = [row for row, _ in mask_set]
        cols = [col for _, col in mask_set]
        min_row, max_row = min(rows), max(rows)
        if max_row < 11:
            return False
        if min_row < 6 and max_row < 14:
            return False
        count = len(mask_set)
        if count < 4 or count > 220:
            return False
        width = max(cols) - min(cols) + 1
        if width < 3 or width > 18:
            return False
        lower_count = sum(1 for row in rows if row >= 12)
        if lower_count < 3 and max_row < 14:
            return False
        return touches_skin(mask_set)

    def looks_like_hair(mask_set: set[Tuple[int, int]]) -> bool:
        if not mask_set:
            return False
        rows = [row for row, _ in mask_set]
        min_row, max_row = min(rows), max(rows)
        if max_row >= 18:
            return False
        return min_row <= 10 and max_row <= 17

    def looks_like_glasses(mask_set: set[Tuple[int, int]], hex_code: str) -> bool:
        if not mask_set:
            return False
        rows = [row for row, _ in mask_set]
        cols = [col for _, col in mask_set]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        width = max_col - min_col + 1
        height = max_row - min_row + 1
        if width < 4 or height > 6 or len(mask_set) < 4:
            return False
        if min_row < 6 or max_row > 16:
            return False
        luminance = luminance_from_hex(hex_code)
        return luminance < 150

    def distance_to_hair_palette(hex_code: str) -> float:
        if not hair_color_set:
            return float("inf")
        rgb = hex_to_rgb(hex_code)
        return min(
            squared_distance(rgb, hex_to_rgb(existing)) ** 0.5 for existing in hair_color_set
        )

    def touches_hair(coords: set[Tuple[int, int]]) -> bool:
        if not coords or not hair_union:
            return False
        for row, col in coords:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (row + dr, col + dc) in hair_union:
                        return True
        return False

    def add_pixels(target_category: str, coords: set[Tuple[int, int]], hex_code: str | None = None):
        if not coords:
            return
        entries = category_to_entry.get(target_category)
        target_idx: int | None = None
        if entries:
            if hex_code is not None:
                for idx, (entry_res, _) in enumerate(entries):
                    if entry_res.color_hex.lower() == hex_code.lower():
                        target_idx = idx
                        break
        if entries and target_idx is not None:
            res, mask = entries[target_idx]
            combined = mask | coords
            res.pixel_mask = mask_to_string(combined)
            res.coverage_pct = round(len(combined) / total_pixels * 100.0, 2)
            entries[target_idx] = (res, combined)
            for idx, (entry_res, _) in enumerate(processed_entries):
                if entry_res is res:
                    processed_entries[idx] = (res, combined)
                    break
            if target_category == "Skin":
                update_skin_tracking(res.color_hex, combined)
            if target_category == "Hair":
                hair_union.update(combined)
                hair_color_set.add(res.color_hex.lower())
            if target_category == "Mouth":
                mouth_union |= coords
            return

        if hex_code is None:
            first_coord = next(iter(coords))
            color_hex = rgb_to_hex(tuple(int(v) for v in arr[first_coord[0], first_coord[1]][:3]))
        else:
            color_hex = hex_code
        color_name = nearest_css_name(color_hex, color_map)
        res = RegionResult(
            sprite_id=sprite_id,
            category=target_category,
            variant_hint=f"{target_category}_{color_name}",
            color_hex=color_hex,
            color_name=color_name,
            coverage_pct=round(len(coords) / total_pixels * 100.0, 2),
            notes="residual_assignment",
            pixel_mask=mask_to_string(coords),
        )
        register_entry(res, set(coords))
        if target_category == "Skin":
            update_skin_tracking(color_hex, set(coords))
        if target_category == "Hair":
            hair_union.update(coords)
            hair_color_set.add(color_hex.lower())
        if target_category == "Mouth":
            mouth_union |= coords

    for res, mask in category_entries.get("Skin", []):
        mask = mask - outline_candidates
        if not mask:
            continue
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        register_entry(res, mask)
        update_skin_tracking(res.color_hex, mask)

    def merge_skin_variants() -> None:
        skin_entries = category_to_entry.get("Skin", [])
        if not skin_entries:
            return
        primary_entry, primary_mask = max(skin_entries, key=lambda item: len(item[1]))
        merged_mask = set()
        for entry, mask in skin_entries:
            merged_mask |= mask
        if merged_mask == primary_mask and len(skin_entries) == 1:
            return
        # Recompute dominant colour within merged mask
        if merged_mask:
            rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in merged_mask)
            sorted_colors = sorted(rgb_counts.items(), key=lambda kv: kv[1], reverse=True)
            dominant_rgb: Tuple[int, int, int] | None = None
            for rgb, _ in sorted_colors:
                hex_candidate = rgb_to_hex(rgb)
                lowered = hex_candidate.lower()
                if lowered in background_hexes or lowered in headwear_color_set:
                    continue
                dominant_rgb = rgb
                break
            if dominant_rgb is None:
                dominant_rgb = sorted_colors[0][0]
            dominant_hex = rgb_to_hex(dominant_rgb)
            primary_entry.color_hex = dominant_hex
            primary_entry.color_name = nearest_css_name(dominant_hex, color_map)
        primary_entry.pixel_mask = mask_to_string(merged_mask)
        primary_entry.coverage_pct = round(len(merged_mask) / total_pixels * 100.0, 2)
        primary_entry.variant_hint = f"Skin_{primary_entry.color_name}"
        category_to_entry["Skin"] = [(primary_entry, merged_mask)]
        processed_updated: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in processed_entries:
            if res.category == "Skin":
                if res is primary_entry:
                    processed_updated.append((res, merged_mask))
                continue
            processed_updated.append((res, mask))
        processed_entries.clear()
        processed_entries.extend(processed_updated)
        skin_union.clear()
        skin_color_set.clear()
        skin_colors_map.clear()
        update_skin_tracking(primary_entry.color_hex, merged_mask)

    merge_skin_variants()

    processed_headwear: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
    headwear_processed_union: set[Tuple[int, int]] = set()
    headwear_color_set: set[str] = set()
    for res, mask in headwear_entries:
        mask = mask - outline_candidates
        if background_mask:
            mask = {coord for coord in mask if coord not in background_mask}
        if not mask:
            continue
        color_counts = Counter(tuple(int(c) for c in arr[row, col][:3]) for row, col in mask)
        if not color_counts:
            continue
        sorted_colors = color_counts.most_common()
        dominant_rgb, _ = sorted_colors[0]
        dominant_hex = rgb_to_hex(dominant_rgb)
        if dominant_hex.lower() in background_hexes or dominant_hex.lower() in skin_color_set:
            add_pixels("FaceAccessory", mask, dominant_hex)
            continue
        lower_ratio = sum(1 for row, _ in mask if row >= 7) / len(mask)
        top_ratio = sum(1 for row, _ in mask if row <= 3) / len(mask)
        if (
            looks_like_hair(mask)
            and lower_ratio >= 0.4
            and top_ratio <= 0.4
            and (touches_skin(mask) or touches_hair(mask))
        ):
            add_pixels("Hair", set(mask), dominant_hex)
            continue
        res.color_hex = dominant_hex
        res.color_name = nearest_css_name(dominant_hex, color_map)
        res.variant_hint = f"Headwear_{res.color_name}"
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        register_entry(res, mask)
        headwear_processed_union |= mask
        headwear_color_set.add(dominant_hex.lower())

    def is_mouth_candidate(mask_set: set[Tuple[int, int]]) -> bool:
        if not mask_set:
            return False
        rows = [row for row, _ in mask_set]
        cols = [col for _, col in mask_set]
        return (
            10 <= min(rows) <= 18
            and max(rows) <= 17
            and len(mask_set) >= 2
            and len(mask_set) <= 10
            and min(cols) >= 8
            and max(cols) <= 16
        )

    def is_eye_candidate(mask_set: set[Tuple[int, int]]) -> bool:
        if not mask_set:
            return False
        rows = [row for row, _ in mask_set]
        cols = [col for _, col in mask_set]
        return (
            8 <= min(rows) <= 14
            and max(rows) <= 15
            and len(mask_set) <= 18
            and (max(rows) - min(rows)) <= 4
            and min(cols) >= 4
            and max(cols) <= 20
        )

    pending_eye_highlights: List[Tuple[str, set[Tuple[int, int]]]] = []

    for res, mask in category_entries.get("Hair", []):
        mask = mask - outline_candidates - headwear_processed_union
        if not mask:
            continue
        color_lower = res.color_hex.lower()
        if color_lower in headwear_color_set:
            add_pixels("Headwear", mask, res.color_hex)
            headwear_processed_union |= mask
            headwear_color_set.add(color_lower)
            continue
        if mask:
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)
            band_height = max_row - min_row + 1
            band_width = max_col - min_col + 1
            if (
                7 <= min_row <= 16
                and max_row <= 18
                and band_height <= 8
                and len(mask) <= 70
                and luminance_from_hex(res.color_hex) < 130
            ):
                add_pixels("FaceAccessory", mask, res.color_hex)
                continue
        if is_eye_candidate(mask):
            color_hex = res.color_hex
            color_name = nearest_css_name(color_hex, color_map)
            eye_result = RegionResult(
                sprite_id=res.sprite_id,
                category="Eyes",
                variant_hint=f"Eyes_{color_name}",
                color_hex=color_hex,
                color_name=color_name,
                coverage_pct=round(len(mask) / total_pixels * 100.0, 2),
                notes="converted_from_hair",
                pixel_mask=mask_to_string(mask),
            )
            refined.append(eye_result)
            register_entry(eye_result, mask)
            eye_union |= mask
            continue
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        register_entry(res, mask)
        hair_color_set.add(res.color_hex.lower())

    def merge_hair_variants() -> None:
        hair_entries = category_to_entry.get("Hair", [])
        if not hair_entries:
            return
        primary_entry, _ = max(hair_entries, key=lambda item: len(item[1]))
        merged_mask: set[Tuple[int, int]] = set()
        for entry, mask in hair_entries:
            merged_mask |= mask
        if not merged_mask:
            return
        rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in merged_mask)
        dominant_rgb = rgb_counts.most_common(1)[0][0]
        dominant_hex = rgb_to_hex(dominant_rgb)
        primary_entry.color_hex = dominant_hex
        primary_entry.color_name = nearest_css_name(dominant_hex, color_map)
        primary_entry.variant_hint = f"Hair_{primary_entry.color_name}"
        primary_entry.pixel_mask = mask_to_string(merged_mask)
        primary_entry.coverage_pct = round(len(merged_mask) / total_pixels * 100.0, 2)
        category_to_entry["Hair"] = [(primary_entry, merged_mask)]
        hair_union.clear()
        hair_union.update(merged_mask)
        hair_color_set.clear()
        hair_color_set.add(primary_entry.color_hex.lower())
        processed_entries[:] = [
            (primary_entry if res is primary_entry else res, merged_mask if res is primary_entry else mask)
            for res, mask in processed_entries
            if res.category != "Hair" or res is primary_entry
        ]
        refined[:] = [res for res in refined if res.category != "Hair"]
        refined.append(primary_entry)

    merge_hair_variants()

    for res, mask in category_entries.get("Eyes", []):
        mask = mask - outline_candidates
        if not mask:
            continue
        if res.color_hex.lower() in ACCESSORY_WHITE_HEXES and len(mask) <= 6:
            pending_eye_highlights.append((res.color_hex, mask))
            continue
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        register_entry(res, mask)

    def merge_eye_variants() -> None:
        eye_entries = category_to_entry.get("Eyes", [])
        if not eye_entries:
            return
        primary_entry, _ = max(eye_entries, key=lambda item: len(item[1]))
        merged_mask: set[Tuple[int, int]] = set()
        for entry, mask in eye_entries:
            merged_mask |= mask
        if merged_mask:
            rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in merged_mask)
            def eye_priority(rgb: Tuple[int, int, int]) -> Tuple[float, int]:
                r, g, b = rgb
                luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
                return (luminance, -rgb_counts[rgb])
            dominant_rgb = min(rgb_counts.keys(), key=eye_priority)
            dominant_hex = rgb_to_hex(dominant_rgb)
            primary_entry.color_hex = dominant_hex
            primary_entry.color_name = nearest_css_name(dominant_hex, color_map)
            primary_entry.variant_hint = f"Eyes_{primary_entry.color_name}"
        if "converted_from_" in primary_entry.notes and len(merged_mask) >= 4:
            add_pixels("FaceAccessory", merged_mask, primary_entry.color_hex)
            category_to_entry.pop("Eyes", None)
            processed_entries[:] = [
                (res, mask) for res, mask in processed_entries if res.category != "Eyes"
            ]
            refined[:] = [res for res in refined if res.category != "Eyes"]
            return
        primary_entry.pixel_mask = mask_to_string(merged_mask)
        primary_entry.coverage_pct = round(len(merged_mask) / total_pixels * 100.0, 2)
        category_to_entry["Eyes"] = [(primary_entry, merged_mask)]
        updated_processed: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in processed_entries:
            if res.category == "Eyes":
                if res is primary_entry:
                    updated_processed.append((res, merged_mask))
                continue
            updated_processed.append((res, mask))
        processed_entries.clear()
        processed_entries.extend(updated_processed)
        refined[:] = [res for res in refined if res.category != "Eyes"]
        refined.append(primary_entry)

    def relabel_headwear_and_glasses() -> None:
        headwear_entries = category_to_entry.get("Headwear", [])
        for res, mask in headwear_entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            height = max(rows) - min(rows) + 1
            width = max(cols) - min(cols) + 1
            if max(rows) <= 7 and width >= 5:
                res.variant_hint = f"Headwear_Cap_{res.color_name}"
        face_entries = category_to_entry.get("FaceAccessory", [])
        glasses_bounds: List[Tuple[int, int, int, int, str]] = []
        for res, mask in face_entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            min_row, max_row = min(rows), max(rows)
            width = max(cols) - min(cols) + 1
            height = max_row - min_row + 1
            if (
                min_row >= 6
                and height <= 6
                and width >= 6
                and looks_like_glasses(mask, res.color_hex)
            ):
                color_name = nearest_css_name(res.color_hex, color_map)
                variant = f"FaceAccessory_Glasses_{color_name}"
                res.variant_hint = variant
                res.color_name = color_name
                current_notes = res.notes or ""
                if "glasses_lens" not in current_notes:
                    res.notes = (
                        f"{current_notes};glasses_lens".strip(";")
                        if current_notes
                        else "glasses_lens"
                    )
                glasses_bounds.append((min_row, max_row, min(cols), max(cols), variant))
        if glasses_bounds:
            for res, mask in face_entries:
                if not mask or res.color_hex.lower() not in ACCESSORY_WHITE_HEXES:
                    continue
                rows = [row for row, _ in mask]
                cols = [col for _, col in mask]
                min_row, max_row = min(rows), max(rows)
                min_col, max_col = min(cols), max(cols)
                for g_min_row, g_max_row, g_min_col, g_max_col, variant in glasses_bounds:
                    if (
                        min_row >= g_min_row - 1
                        and max_row <= g_max_row + 1
                        and min_col >= g_min_col - 1
                        and max_col <= g_max_col + 1
                    ):
                        res.variant_hint = variant
                        res.color_name = nearest_css_name(res.color_hex, color_map)
                        current_notes = res.notes or ""
                        if "glasses_reflection" not in current_notes:
                            res.notes = (
                                f"{current_notes};glasses_reflection".strip(";")
                                if current_notes
                                else "glasses_reflection"
                            )
                        break

    def reassign_cap_pixels() -> None:
        entries = category_to_entry.get("FaceAccessory", [])
        if not entries:
            return
        keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            min_row = min(rows) if rows else 24
            max_row = max(rows) if rows else -1
            if rows and max_row <= 9:
                add_pixels("Headwear", set(mask), res.color_hex)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
            else:
                keep.append((res, mask))
        category_to_entry["FaceAccessory"] = keep

    def reassign_headwear_to_hair() -> None:
        entries = category_to_entry.get("Headwear", [])
        if not entries:
            return
        keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            min_row = min(rows)
            max_row = max(rows)
            height = max_row - min_row + 1
            color_lower = res.color_hex.lower()
            touches = touches_hair(mask)
            if min_row >= 3:
                add_pixels("Hair", set(mask), res.color_hex)
                hair_color_set.add(res.color_hex.lower())
                headwear_color_set.discard(color_lower)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
            elif (
                looks_like_hair(mask)
                and (
                    touches
                    or touches_skin(mask)
                    or distance_to_hair_palette(res.color_hex) <= 32.0
                )
                and sum(1 for row, _ in mask if row >= 7) >= 0.2 * len(mask)
                and sum(1 for row, _ in mask if row <= 3) <= 0.25 * len(mask)
            ):
                add_pixels("Hair", set(mask), res.color_hex)
                hair_color_set.add(res.color_hex.lower())
                headwear_color_set.discard(color_lower)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
            else:
                keep.append((res, mask))
        category_to_entry["Headwear"] = keep

    def promote_hair_to_headwear() -> None:
        if category_to_entry.get("Headwear"):
            return
        hair_entries = category_to_entry.get("Hair", [])
        for res, mask in hair_entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            min_row, max_row = min(rows), max(rows)
            width = max(cols) - min(cols) + 1
            height = max_row - min_row + 1
            top_band = sum(1 for row, _ in mask if row <= 2)
            top_ratio = top_band / len(mask)
            if (
                min_row <= 2
                and width >= 6
                and len(mask) >= 20
                and height <= 12
                and top_band >= 8
                and top_ratio >= 0.32
            ):
                res.category = "Headwear"
                res.variant_hint = f"Headwear_{res.color_name}"
                headwear_color_set.add(res.color_hex.lower())
                category_to_entry["Headwear"].append((res, mask))
                category_to_entry["Hair"] = [
                    (h_res, h_mask) for h_res, h_mask in category_to_entry["Hair"] if h_res is not res
                ]
                for idx, (entry, entry_mask) in enumerate(processed_entries):
                    if entry is res:
                        processed_entries[idx] = (res, mask)
                hair_color_set.discard(res.color_hex.lower())
                return

    for res, mask in category_entries.get("Mouth", []):
        mask = mask - outline_candidates
        if not mask:
            continue
        if res.color_hex.lower() in ACCESSORY_WHITE_HEXES:
            add_pixels("FaceAccessory", mask, res.color_hex)
            continue
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        register_entry(res, mask)

    def merge_mouth_variants() -> None:
        mouth_entries = category_to_entry.get("Mouth", [])
        if not mouth_entries:
            return
        primary_entry, _ = max(mouth_entries, key=lambda item: len(item[1]))
        merged_mask: set[Tuple[int, int]] = set()
        for entry, mask in mouth_entries:
            merged_mask |= mask
        if not merged_mask:
            return
        rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in merged_mask)
        filtered = [item for item in rgb_counts.items() if rgb_to_hex(item[0]).lower() not in skin_color_set]
        if filtered:
            dominant_rgb = max(filtered, key=lambda kv: kv[1])[0]
        else:
            dominant_rgb = max(rgb_counts.items(), key=lambda kv: kv[1])[0]
        dominant_hex = rgb_to_hex(dominant_rgb)
        primary_entry.color_hex = dominant_hex
        primary_entry.color_name = nearest_css_name(dominant_hex, color_map)
        primary_entry.variant_hint = f"Mouth_{primary_entry.color_name}"
        primary_entry.pixel_mask = mask_to_string(merged_mask)
        primary_entry.coverage_pct = round(len(merged_mask) / total_pixels * 100.0, 2)
        category_to_entry["Mouth"] = [(primary_entry, merged_mask)]
        processed_entries[:] = [
            (primary_entry if res is primary_entry else res, merged_mask if res is primary_entry else mask)
            for res, mask in processed_entries
            if res.category != "Mouth" or res is primary_entry
        ]
        refined[:] = [res for res in refined if res.category != "Mouth"]
        refined.append(primary_entry)

    def prune_hair_overlap() -> None:
        if not skin_union:
            return
        hair_entries = category_to_entry.get("Hair", [])
        if not hair_entries:
            return
        updated_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        changed = False
        for res, mask in hair_entries:
            cleaned = mask - skin_union
            if cleaned != mask:
                changed = True
            if not cleaned:
                continue
            res.pixel_mask = mask_to_string(cleaned)
            res.coverage_pct = round(len(cleaned) / total_pixels * 100.0, 2)
            updated_entries.append((res, cleaned))
        if not changed:
            return
        category_to_entry["Hair"] = updated_entries
        hair_union.clear()
        for _, mask in updated_entries:
            hair_union |= mask
        updated_processed: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in processed_entries:
            if res.category == "Hair":
                new_mask = next((m for r, m in updated_entries if r is res), None)
                if new_mask:
                    updated_processed.append((res, new_mask))
                continue
            updated_processed.append((res, mask))
        processed_entries.clear()
        processed_entries.extend(updated_processed)

    merge_mouth_variants()
    prune_hair_overlap()
    def refine_hair_components() -> None:
        nonlocal hair_union
        hair_entries = category_to_entry.get("Hair", [])
        if not hair_entries:
            return
        headwear_pixels: set[Tuple[int, int]] = set()
        for _, mask in category_to_entry.get("Headwear", []):
            headwear_pixels |= mask
        updated_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        facial_components: List[set[Tuple[int, int]]] = []
        changed = False
        for res, mask in hair_entries:
            working = set(mask)
            if headwear_pixels:
                trimmed = working - headwear_pixels
                if trimmed != working:
                    changed = True
                working = trimmed
            if not working:
                changed = True
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
                continue
            visited: set[Tuple[int, int]] = set()
            components: List[set[Tuple[int, int]]] = []
            for pixel in working:
                if pixel in visited:
                    continue
                stack = [pixel]
                visited.add(pixel)
                component: set[Tuple[int, int]] = set()
                while stack:
                    row, col = stack.pop()
                    component.add((row, col))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nbr = (row + dr, col + dc)
                        if nbr in working and nbr not in visited:
                            visited.add(nbr)
                            stack.append(nbr)
                components.append(component)
            keep_components: List[set[Tuple[int, int]]] = []
            facial_candidates: List[set[Tuple[int, int]]] = []
            for comp in components:
                rows = [row for row, _ in comp]
                min_row = min(rows)
                max_row = max(rows)
                lower_count = sum(1 for row in rows if row >= 11)
                if (
                    lower_count >= 3
                    and lower_count / len(comp) >= 0.5
                    and max_row >= 11
                    and touches_skin(comp)
                ):
                    facial_candidates.append(comp)
                else:
                    keep_components.append(comp)
            if keep_components:
                combined_hair = set().union(*keep_components)
                if combined_hair != mask:
                    changed = True
                res.pixel_mask = mask_to_string(combined_hair)
                res.coverage_pct = round(len(combined_hair) / total_pixels * 100.0, 2)
                updated_entries.append((res, combined_hair))
            else:
                changed = True
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
            if facial_candidates:
                facial_components.append(set().union(*facial_candidates))
        if updated_entries:
            category_to_entry["Hair"] = updated_entries
        elif hair_entries:
            category_to_entry.pop("Hair", None)
        if changed:
            hair_union.clear()
            for _, mask in updated_entries:
                hair_union |= mask
            updated_processed: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
            hair_res_ids = {id(res) for res, _ in updated_entries}
            for res, mask in processed_entries:
                if res.category == "Hair":
                    if id(res) in hair_res_ids:
                        new_mask = next((m for r, m in updated_entries if r is res), None)
                        if new_mask is not None:
                            updated_processed.append((res, new_mask))
                    continue
                updated_processed.append((res, mask))
            processed_entries.clear()
            processed_entries.extend(updated_processed)
            if updated_entries:
                refined[:] = [res for res in refined if res.category != "Hair" or id(res) in hair_res_ids]
            hair_color_set.clear()
            for res, mask in updated_entries:
                if not mask:
                    continue
                sample_row, sample_col = next(iter(mask))
                sample_rgb = tuple(int(arr[sample_row, sample_col][k]) for k in range(3))
                sample_hex = rgb_to_hex(sample_rgb)
                res.color_hex = sample_hex
                res.color_name = nearest_css_name(sample_hex, color_map)
                res.variant_hint = f"Hair_{res.color_name}"
                hair_color_set.add(sample_hex.lower())
        if facial_components:
            combined_facial = set().union(*facial_components)
            if combined_facial:
                rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in combined_facial)
                if rgb_counts:
                    dominant_hex = rgb_to_hex(max(rgb_counts.items(), key=lambda kv: kv[1])[0])
                    add_pixels("FacialHair", combined_facial, dominant_hex)
    def demote_headwear_to_hair() -> None:
        nonlocal headwear_processed_union
        entries = category_to_entry.get("Headwear", [])
        if not entries:
            return
        keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        changed = False
        for res, mask in entries:
            if not mask:
                continue
            lower_ratio = sum(1 for row, _ in mask if row >= 7) / len(mask)
            top_ratio = sum(1 for row, _ in mask if row <= 3) / len(mask)
            if (
                looks_like_hair(mask)
                and lower_ratio >= 0.2
                and top_ratio <= 0.25
                and (
                    touches_hair(mask)
                    or touches_skin(mask)
                    or distance_to_hair_palette(res.color_hex) <= 32.0
                )
            ):
                add_pixels("Hair", set(mask), res.color_hex)
                headwear_color_set.discard(res.color_hex.lower())
                headwear_processed_union.difference_update(mask)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
                changed = True
                continue
            keep.append((res, mask))
        cleaned_keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in keep:
            if len(mask) < 4 and (touches_hair(mask) or touches_skin(mask)):
                add_pixels("Hair", set(mask), res.color_hex)
                headwear_color_set.discard(res.color_hex.lower())
                headwear_processed_union.difference_update(mask)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
                changed = True
                continue
            cleaned_keep.append((res, mask))
        keep = cleaned_keep
        if changed:
            category_to_entry["Headwear"] = keep
            if not keep:
                category_to_entry.pop("Headwear", None)
        else:
            category_to_entry["Headwear"] = keep
    def promote_headwear_hairless_case() -> None:
        nonlocal headwear_processed_union
        if category_to_entry.get("Hair"):
            return
        entries = category_to_entry.get("Headwear", [])
        if not entries:
            return
        keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        changed = False
        for res, mask in entries:
            if not mask:
                continue
            lower_ratio = sum(1 for row, _ in mask if row >= 7) / len(mask)
            top_ratio = sum(1 for row, _ in mask if row <= 3) / len(mask)
            if (
                looks_like_hair(mask)
                and lower_ratio >= 0.2
                and top_ratio <= 0.25
                and (
                    touches_skin(mask)
                    or distance_to_hair_palette(res.color_hex) <= 34.0
                )
            ):
                add_pixels("Hair", set(mask), res.color_hex)
                headwear_color_set.discard(res.color_hex.lower())
                headwear_processed_union.difference_update(mask)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
                changed = True
                continue
            keep.append((res, mask))
        cleaned_keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in keep:
            if len(mask) < 4 and touches_skin(mask):
                add_pixels("Hair", set(mask), res.color_hex)
                headwear_color_set.discard(res.color_hex.lower())
                headwear_processed_union.difference_update(mask)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
                changed = True
                continue
            cleaned_keep.append((res, mask))
        keep = cleaned_keep
        if changed:
            category_to_entry["Headwear"] = keep
            if not keep:
                category_to_entry.pop("Headwear", None)
        else:
            category_to_entry["Headwear"] = keep
    def final_headwear_cleanup() -> None:
        entries = category_to_entry.get("Headwear", [])
        if not entries:
            return
        keep: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        changed = False
        for res, mask in entries:
            if not mask:
                continue
            lower_ratio = sum(1 for row, _ in mask if row >= 7) / len(mask)
            top_ratio = sum(1 for row, _ in mask if row <= 3) / len(mask)
            if (
                looks_like_hair(mask)
                and lower_ratio >= 0.2
                and top_ratio <= 0.25
                and touches_skin(mask)
            ):
                add_pixels("Hair", set(mask), res.color_hex)
                headwear_color_set.discard(res.color_hex.lower())
                headwear_processed_union.difference_update(mask)
                refined[:] = [r for r in refined if r is not res]
                processed_entries[:] = [(r, m) for r, m in processed_entries if r is not res]
                changed = True
                continue
            keep.append((res, mask))
        if changed:
            if keep:
                category_to_entry["Headwear"] = keep
            else:
                category_to_entry.pop("Headwear", None)
        else:
            category_to_entry["Headwear"] = keep
    refine_hair_components()
    reassign_cap_pixels()
    reassign_headwear_to_hair()
    promote_hair_to_headwear()
    final_headwear_cleanup()
    merge_eye_variants()
    relabel_headwear_and_glasses()

    eye_entries_after = category_to_entry.get("Eyes")
    if eye_entries_after:
        entry, mask = eye_entries_after[0]
        if len(mask) <= 3:
            add_pixels("FaceAccessory", mask, entry.color_hex)
            category_to_entry.pop("Eyes", None)
            processed_entries[:] = [
                (res, m) for res, m in processed_entries if res is not entry
            ]

    for hex_code, coords in pending_eye_highlights:
        add_pixels("FaceAccessory", coords, hex_code)

    have_eye_entry = bool(category_to_entry.get("Eyes"))

    for res, mask in kept_face_accessories:
        mask = mask - outline_candidates
        if not mask:
            continue
        if looks_like_glasses(mask, res.color_hex):
            color_name = nearest_css_name(res.color_hex, color_map)
            res.variant_hint = f"FaceAccessory_Glasses_{color_name}"
            res.color_name = color_name
            current_notes = res.notes or ""
            if "glasses_lens" not in current_notes:
                res.notes = (
                    f"{current_notes};glasses_lens".strip(";")
                    if current_notes
                    else "glasses_lens"
                )
            register_entry(res, mask)
            continue
        rows = [row for row, _ in mask]
        cols = [col for _, col in mask]
        min_row, max_row = min(rows), max(rows)
        width = max(cols) - min(cols) + 1
        if (
            not have_eye_entry
            and res.color_hex.lower() not in ACCESSORY_WHITE_HEXES
            and 8 <= min_row <= 12
            and max_row <= 15
            and width >= 2
            and len(mask) <= 12
        ):
            eye_result = RegionResult(
                sprite_id=res.sprite_id,
                category="Eyes",
                variant_hint=f"Eyes_{nearest_css_name(res.color_hex, color_map)}",
                color_hex=res.color_hex,
                color_name=nearest_css_name(res.color_hex, color_map),
                coverage_pct=round(len(mask) / total_pixels * 100.0, 2),
                notes="converted_from_face_accessory",
                pixel_mask=mask_to_string(mask),
            )
            register_entry(eye_result, set(mask))
            eye_union |= mask
            have_eye_entry = True
            continue
        if (
            res.color_hex.lower() not in ACCESSORY_WHITE_HEXES
            and
            min_row <= 12
            and max_row <= 14
            and width >= 4
            and (max_row - min_row + 1) <= 3
            and len(mask) <= 40
        ):
            add_pixels("Eyes", set(mask), res.color_hex)
            eye_union |= mask
            have_eye_entry = True
            continue
        if (
            res.color_hex.lower() in hair_color_set
            or looks_like_hair(mask)
            or touches_hair(mask)
        ):
            add_pixels("Hair", set(mask), res.color_hex)
            continue
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        register_entry(res, mask)

    for res, mask in category_entries.get("Clothing", []):
        mask = mask - headwear_processed_union - outline_candidates
        if not mask:
            continue
        if is_mouth_candidate(mask):
            if res.color_hex.lower() in ACCESSORY_WHITE_HEXES:
                add_pixels("FaceAccessory", mask, res.color_hex)
                continue
            color_hex = res.color_hex
            color_name = nearest_css_name(color_hex, color_map)
            mouth_result = RegionResult(
                sprite_id=res.sprite_id,
                category="Mouth",
                variant_hint=f"Mouth_{color_name}",
                color_hex=color_hex,
                color_name=color_name,
                coverage_pct=round(len(mask) / total_pixels * 100.0, 2),
                notes="converted_from_clothing",
                pixel_mask=mask_to_string(mask),
            )
            refined.append(mouth_result)
            register_entry(mouth_result, mask)
            continue
        color_counts = Counter(tuple(int(c) for c in arr[row, col][:3]) for row, col in mask)
        if not color_counts:
            continue
        sorted_colors = color_counts.most_common()
        primary_rgb = None
        for rgb, _ in sorted_colors:
            hex_candidate = rgb_to_hex(tuple(int(v) for v in rgb))
            if hex_candidate.lower() not in skin_color_set:
                primary_rgb = rgb
                break
        if primary_rgb is None:
            primary_rgb = sorted_colors[0][0]
        primary_coords = {
            coord for coord in mask if tuple(int(c) for c in arr[coord[0], coord[1]][:3]) == primary_rgb
        }
        primary_hex = rgb_to_hex(primary_rgb)
        remaining = set(mask) - primary_coords
        if is_mouth_candidate(primary_coords):
            if primary_hex.lower() in ACCESSORY_WHITE_HEXES:
                add_pixels("FaceAccessory", primary_coords, primary_hex)
                remaining = set(mask) - primary_coords
                continue
            color_name = nearest_css_name(primary_hex, color_map)
            mouth_result = RegionResult(
                sprite_id=res.sprite_id,
                category="Mouth",
                variant_hint=f"Mouth_{color_name}",
                color_hex=primary_hex,
                color_name=color_name,
                coverage_pct=round(len(primary_coords) / total_pixels * 100.0, 2),
                notes="converted_from_clothing",
                pixel_mask=mask_to_string(primary_coords),
            )
            refined.append(mouth_result)
            register_entry(mouth_result, primary_coords)
            mouth_union |= primary_coords
        elif primary_hex.lower() in skin_color_set and touches_skin(primary_coords):
            add_pixels("Skin", primary_coords, primary_hex)
            update_skin_tracking(primary_hex, primary_coords)
            clothing_union -= primary_coords
        elif (
            primary_hex.lower() in hair_color_set
            or looks_like_hair(primary_coords)
            or touches_hair(primary_coords)
        ):
            add_pixels("Hair", primary_coords, primary_hex)
            clothing_union -= primary_coords
        elif is_facial_hair_candidate(primary_coords):
            add_pixels("FacialHair", primary_coords, primary_hex)
            clothing_union -= primary_coords
        else:
            res.color_hex = primary_hex
            res.color_name = nearest_css_name(primary_hex, color_map)
            res.variant_hint = f"Clothing_{res.color_name}"
            res.pixel_mask = mask_to_string(primary_coords)
            res.coverage_pct = round(len(primary_coords) / total_pixels * 100.0, 2)
            register_entry(res, primary_coords)
        for rgb, _ in sorted_colors[1:]:
            coords = {
                coord for coord in remaining if tuple(int(c) for c in arr[coord[0], coord[1]][:3]) == rgb
            }
            if not coords:
                continue
            remaining -= coords
            hex_code = rgb_to_hex(rgb)
            color_name = nearest_css_name(hex_code, color_map)
            lower = hex_code.lower()
            if lower in hair_color_set or looks_like_hair(coords) or touches_hair(coords):
                add_pixels("Hair", coords, hex_code)
                clothing_union -= coords
                continue
            if is_mouth_candidate(coords):
                if lower in ACCESSORY_WHITE_HEXES:
                    add_pixels("FaceAccessory", coords, hex_code)
                    continue
                mouth_result = RegionResult(
                    sprite_id=res.sprite_id,
                    category="Mouth",
                    variant_hint=f"Mouth_{color_name}",
                    color_hex=hex_code,
                    color_name=color_name,
                    coverage_pct=round(len(coords) / total_pixels * 100.0, 2),
                    notes="converted_from_clothing",
                    pixel_mask=mask_to_string(coords),
                )
                refined.append(mouth_result)
                register_entry(mouth_result, coords)
                mouth_union |= coords
                continue
            if lower in skin_color_set and (touches_skin(coords) or any(coord in skin_union for coord in coords)):
                add_pixels("Skin", coords, hex_code)
                update_skin_tracking(hex_code, coords)
                clothing_union -= coords
                continue
            if is_facial_hair_candidate(coords):
                add_pixels("FacialHair", coords, hex_code)
                clothing_union -= coords
                continue
            extra_res = RegionResult(
                sprite_id=res.sprite_id,
                category="Clothing",
                variant_hint=f"Clothing_{color_name}",
                color_hex=hex_code,
                color_name=color_name,
                coverage_pct=round(len(coords) / total_pixels * 100.0, 2),
                notes="clothing_variant",
                pixel_mask=mask_to_string(coords),
            )
            register_entry(extra_res, coords)

    # Palette entries remain unchanged.
    for res, mask in category_entries.get("Palette", []):
        processed_entries.append((res, mask))
        category_to_entry[res.category].append((res, mask))

    merge_skin_variants()

    # Assign residual pixels that were not captured by any trait.
    assigned_pixels: set[Tuple[int, int]] = set(background_mask) | outline_candidates
    for _, mask in processed_entries:
        assigned_pixels |= mask

    residual_pixels: set[Tuple[int, int]] = set()
    rows, cols = arr.shape[:2]
    for row in range(rows):
        for col in range(cols):
            if int(arr[row, col][3]) < 16:
                continue
            coord = (row, col)
            if coord not in assigned_pixels:
                residual_pixels.add(coord)

    residual_assignments: Dict[Tuple[str, str], set[Tuple[int, int]]] = defaultdict(set)
    outline_additions: set[Tuple[int, int]] = set()

    for row, col in residual_pixels:
        r, g, b = [int(v) for v in arr[row, col][:3]]
        hex_code = rgb_to_hex((r, g, b))
        hex_lower = hex_code.lower()

        if (row, col) in background_mask:
            residual_assignments[("Background", hex_code)].add((row, col))
            continue

        if hex_lower in background_hexes:
            residual_assignments[("Background", hex_code)].add((row, col))
            continue

        if hex_lower in headwear_color_set:
            residual_assignments[("Headwear", hex_code)].add((row, col))
            continue
        if hex_lower in hair_color_set or touches_hair({(row, col)}):
            residual_assignments[("Hair", hex_code)].add((row, col))
            continue
        if hex_lower in skin_color_set:
            residual_assignments[("Skin", hex_code)].add((row, col))
            continue

        if row <= 5:
            if hex_lower in background_hexes:
                residual_assignments[("Background", hex_code)].add((row, col))
                continue
            if hex_lower in skin_color_set:
                residual_assignments[("Skin", hex_code)].add((row, col))
                continue
            if category_to_entry.get("Headwear"):
                residual_assignments[("Headwear", hex_code)].add((row, col))
            elif category_to_entry.get("Hair"):
                residual_assignments[("Hair", hex_code)].add((row, col))
            else:
                residual_assignments[("Background", hex_code)].add((row, col))
        elif row <= 10:
            if category_to_entry.get("Hair"):
                residual_assignments[("Hair", hex_code)].add((row, col))
            elif category_to_entry.get("Skin"):
                residual_assignments[("Skin", hex_code)].add((row, col))
            else:
                outline_additions.add((row, col))
        elif row <= 15:
            if category_to_entry.get("Skin"):
                residual_assignments[("Skin", hex_code)].add((row, col))
            elif category_to_entry.get("Clothing"):
                residual_assignments[("Clothing", hex_code)].add((row, col))
            else:
                outline_additions.add((row, col))
        else:
            if category_to_entry.get("Clothing"):
                residual_assignments[("Clothing", hex_code)].add((row, col))
            else:
                outline_additions.add((row, col))

    for (category, hex_code), coords in list(residual_assignments.items()):
        if category == "Headwear" and hex_code.lower() in background_hexes:
            residual_assignments.pop((category, hex_code))
            residual_assignments[("Background", hex_code)].update(coords)
            continue
        if category == "Clothing":
            if touches_hair(coords) or hex_code.lower() in hair_color_set or looks_like_hair(coords):
                add_pixels("Hair", coords, hex_code)
                continue
            if is_mouth_candidate(coords):
                color_name = nearest_css_name(hex_code, color_map)
                mouth_result = RegionResult(
                    sprite_id=sprite_id,
                    category="Mouth",
                    variant_hint=f"Mouth_{color_name}",
                    color_hex=hex_code,
                    color_name=color_name,
                    coverage_pct=round(len(coords) / total_pixels * 100.0, 2),
                    notes="converted_from_residual",
                    pixel_mask=mask_to_string(coords),
                )
                refined.append(mouth_result)
                register_entry(mouth_result, coords)
                continue
            if hex_code.lower() in skin_color_set and (touches_skin(coords) or any(coord in skin_union for coord in coords)):
                add_pixels("Skin", coords, hex_code)
                update_skin_tracking(hex_code, coords)
                continue
        if category == "Mouth" and hex_code.lower() in ACCESSORY_WHITE_HEXES:
            add_pixels("FaceAccessory", coords, hex_code)
            continue
        add_pixels(category, coords, hex_code)
        if category == "Skin":
            update_skin_tracking(hex_code, coords)
        if category == "Headwear":
            headwear_processed_union |= coords
            headwear_color_set.add(hex_code.lower())
        if category == "Mouth":
            mouth_union |= coords

    merge_skin_variants()
    merge_hair_variants()
    merge_mouth_variants()
    refine_hair_components()
    demote_headwear_to_hair()
    promote_headwear_hairless_case()
    merge_hair_variants()

    if outline_additions:
        outline_candidates |= outline_additions

    merged_processed: Dict[Tuple[str, str, str], Tuple[RegionResult, set[Tuple[int, int]]]] = {}
    for res, mask in processed_entries:
        key = (res.sprite_id, res.category, res.variant_hint)
        existing = merged_processed.get(key)
        if existing is None:
            merged_processed[key] = (res, set(mask))
        else:
            existing_res, existing_mask = existing
            existing_mask |= mask
            merged_processed[key] = (existing_res, existing_mask)
    for res, mask in merged_processed.values():
        res.pixel_mask = mask_to_string(mask)
        res.coverage_pct = round(len(mask) / total_pixels * 100.0, 2)
        refined.append(res)

    outline_set = outline_candidates
    occupied_pixels: set[Tuple[int, int]] = set()
    for res, mask in processed_entries:
        if res.category != "Outline":
            occupied_pixels |= mask
    outline_set -= occupied_pixels
    outline_result = RegionResult(
        sprite_id=sprite_id,
        category="Outline",
        variant_hint="Outline_Face_Black",
        color_hex="#000000",
        color_name="black",
        coverage_pct=round(len(outline_set) / total_pixels * 100.0, 2),
        notes="auto_outline",
        pixel_mask=mask_to_string(outline_set),
    )
    refined.append(outline_result)

    if not any(res.category == "Headwear" for res in refined):
        for res in refined:
            if res.category != "Hair":
                continue
            coords = parse_pixel_mask(res.pixel_mask)
            if not coords:
                continue
            rows_vals = [row for row, _ in coords]
            cols_vals = [col for _, col in coords]
            min_row = min(rows_vals)
            max_row = max(rows_vals)
            width = max(cols_vals) - min(cols_vals) + 1
            height = max_row - min_row + 1
            if min_row <= 2 and width >= 6 and len(coords) >= 20 and height <= 12:
                res.category = "Headwear"
                res.variant_hint = f"Headwear_{res.color_name}"
                break

    merged: Dict[Tuple[str, str, str], RegionResult] = {}
    for res in refined:
        key = (res.category, res.variant_hint, res.color_hex)
        if key in merged:
            existing = merged[key]
            combined = parse_pixel_mask(existing.pixel_mask) | parse_pixel_mask(res.pixel_mask)
            existing.pixel_mask = mask_to_string(combined)
            existing.coverage_pct = round(len(combined) / total_pixels * 100.0, 2)
        else:
            merged[key] = res
    refined = list(merged.values())

    # Keep ordering similar to original: Background, Outline, Skin, Hair, Headwear...
    order_priority = {
        "Background": 0,
        "Outline": 1,
        "Skin": 2,
        "Headwear": 3,
        "HeadwearLogo": 4,
        "Hair": 5,
        "FacialHair": 6,
        "Eyes": 7,
        "Mouth": 8,
        "FaceAccessory": 9,
        "Clothing": 10,
        "NeckAccessory": 11,
        "Palette": 200,
    }

    refined.sort(key=lambda res: (order_priority.get(res.category, 99), res.variant_hint))

    captured_pixels = set(background_mask) | outline_candidates
    for _, mask in processed_entries:
        captured_pixels |= mask

    missing = []
    rows, cols = arr.shape[:2]
    for row in range(rows):
        for col in range(cols):
            if int(arr[row, col][3]) < 16:
                continue
            if (row, col) not in captured_pixels:
                missing.append((row, col))

    if missing:
        missing_hex_map: Dict[str, set[Tuple[int, int]]] = defaultdict(set)
        for row, col in missing:
            r, g, b = [int(v) for v in arr[row, col][:3]]
            missing_hex_map[rgb_to_hex((r, g, b))].add((row, col))
        for hex_code, coords in missing_hex_map.items():
            color_name = nearest_css_name(hex_code, color_map)
            refined.append(
                RegionResult(
                    sprite_id=sprite_id,
                    category="Unassigned",
                    variant_hint=f"Unassigned_{color_name}",
                    color_hex=hex_code,
                    color_name=color_name,
                    coverage_pct=round(len(coords) / total_pixels * 100.0, 2),
                    notes="auto_unassigned",
                    pixel_mask=mask_to_string(coords),
                )
            )
    return refined


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)
    color_map = load_custom_color_map(args.color_map)

    if not args.src.exists():
        LOGGER.error("Source directory does not exist: %s", args.src)
        return 1

    files = sorted(args.src.rglob("*.png"))
    if not files:
        LOGGER.error("No PNG files found in %s", args.src)
        return 1

    LOGGER.info("Analysing %d sprites…", len(files))
    all_results: List[RegionResult] = []
    for path in files:
        sprite_results = analyze_sprite(path, color_map, args.top_colors)
        if sprite_results:
            all_results.extend(sprite_results)

    write_csv(args.output, all_results)
    LOGGER.info("Wrote %s with %d records.", args.output, len(all_results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

