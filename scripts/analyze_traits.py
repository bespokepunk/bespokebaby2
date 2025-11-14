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
import hashlib
import json
import logging
import math
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, List, Set, Tuple

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

COLOR_NAME_CACHE: Dict[Tuple[str, str | None], str] = {}
GLOBAL_COLOR_NAME_CACHE: Dict[str, str] = {}

EPIC_CONTEXT_SUFFIXES: Dict[str, List[str]] = {
    "general": ["Gleam", "Pulse", "Aura", "Whisper"],
    "skin": ["Aura", "Veil", "Grace", "Sheen"],
    "hair": ["Strands", "Silk", "Mane", "Tress"],
    "facial_hair": ["Beard", "Braid", "Whisker", "Trace"],
    "eyes": ["Gaze", "Iris", "Gleam", "Spark"],
    "mouth": ["Bloom", "Rouge", "Whisper", "Muse"],
    "fabric": ["Weave", "Velour", "Drape", "Thread"],
    "headwear": ["Crest", "Crown", "Shade", "Band"],
    "background": ["Horizon", "Field", "Realm", "Canvas"],
    "outline": ["Contour", "Trace", "Edge", "Line"],
    "accessory": ["Accent", "Charm", "Gleam", "Spark"],
    "adornment": ["Jewel", "Pendant", "Gleam", "Talisman"],
    "base": ["Aura", "Veil", "Contour", "Form"],
    "face": ["Expression", "Contour", "Focus", "Detail"],
    "eyewear": ["Lens", "Frame", "Shade", "Gaze"],
    "jewelry": ["Gleam", "Pendant", "Filigree", "Spark"],
    "palette": ["Spectrum", "Tone", "Blend", "Array"],
    "metal": ["Alloy", "Filigree", "Gleam", "Forge"],
    "glass": ["Lens", "Glint", "Glaze", "Sheen"],
}

EPIC_LIGHTNESS_BANDS: List[Tuple[float, List[str]]] = [
    (0.18, ["Obsidian", "Midnight", "Nocturne", "Abyss"]),
    (0.32, ["Shadow", "Sable", "Raven", "Dusk"]),
    (0.50, ["Velvet", "Ember", "Bronze", "Opulent"]),
    (0.68, ["Luminous", "Radiant", "Gilded", "Auric"]),
    (0.82, ["Celestial", "Halo", "Serene", "Aurora"]),
    (1.01, ["Ethereal", "Prismatic", "Glacial", "Iridescent"]),
]

EPIC_GRAY_BANDS: List[Tuple[float, List[str]]] = [
    (0.18, ["Jet", "Onyx", "Pitch"]),
    (0.32, ["Graphite", "Iron", "Steel"]),
    (0.50, ["Gunmetal", "Slate", "Basalt"]),
    (0.68, ["Stone", "Granite", "Fog"]),
    (0.82, ["Pearl", "Dove", "Chalk"]),
    (1.01, ["Ivory", "Porcelain", "Frost"]),
]

EPIC_HUE_BANDS: List[Tuple[float, List[str]]] = [
    (15.0, ["Crimson", "Garnet", "Sangria"]),
    (35.0, ["Cinnabar", "Copper", "Russet"]),
    (55.0, ["Amber", "Marigold", "Topaz"]),
    (75.0, ["Butterscotch", "Honey", "Dune"]),
    (95.0, ["Ochre", "Saffron", "Harvest"]),
    (125.0, ["Moss", "Verdant", "Sage"]),
    (155.0, ["Olive", "Cypress", "Basil"]),
    (185.0, ["Teal", "Lagoon", "Aqua"]),
    (215.0, ["Azure", "Cobalt", "Cerulean"]),
    (245.0, ["Sapphire", "Indigo", "Twilight"]),
    (275.0, ["Violet", "Amethyst", "Orchid"]),
    (305.0, ["Magenta", "Fuchsia", "Bougainvillea"]),
    (335.0, ["Rose", "Peony", "Rosette"]),
    (360.0, ["Scarlet", "Ruby", "Carmine"]),
]

def hashed_choice(options: List[str], key: str) -> str:
    if not options:
        raise ValueError("Options list must not be empty for hashed_choice.")
    digest = hashlib.md5(key.encode("utf-8")).digest()
    return options[digest[0] % len(options)]


def pick_from_bands(
    bands: List[Tuple[float, List[str]]],
    value: float,
    key: str,
) -> str:
    for threshold, options in bands:
        if value < threshold:
            return hashed_choice(options, key)
    return hashed_choice(bands[-1][1], key)


def generate_epic_color_name(hex_code: str, context: str | None = None) -> str:
    context_key = (context or "general").lower()
    cache_key = (hex_code.lower(), context_key)
    cached = COLOR_NAME_CACHE.get(cache_key)
    if cached:
        return cached

    global_name = GLOBAL_COLOR_NAME_CACHE.get(hex_code.lower())
    if global_name:
        COLOR_NAME_CACHE[cache_key] = global_name
        return global_name

    r, g, b = hex_to_rgb(hex_code)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

    prefix = pick_from_bands(
        EPIC_LIGHTNESS_BANDS,
        l,
        f"{hex_code}|{context_key}|prefix",
    )

    if s < 0.08:
        base = pick_from_bands(
            EPIC_GRAY_BANDS,
            l,
            f"{hex_code}|{context_key}|base",
        )
    else:
        hue_degrees = (h * 360.0) % 360.0
        base = pick_from_bands(
            EPIC_HUE_BANDS,
            hue_degrees,
            f"{hex_code}|{context_key}|base",
        )

    suffix_options = EPIC_CONTEXT_SUFFIXES.get(context_key, EPIC_CONTEXT_SUFFIXES["general"])
    suffix = hashed_choice(
        suffix_options,
        f"{hex_code}|{context_key}|suffix",
    )

    composed = f"{prefix}{base}{suffix}"
    canonical = GLOBAL_COLOR_NAME_CACHE.setdefault(hex_code.lower(), composed)
    COLOR_NAME_CACHE[cache_key] = canonical
    return canonical


def color_context_for_category(category: str | None) -> str | None:
    if not category:
        return None
    mapping = {
        "Skin": "skin",
        "Hair": "hair",
        "FacialHair": "facial_hair",
        "Eyes": "eyes",
        "Mouth": "mouth",
        "Clothing": "fabric",
        "Headwear": "headwear",
        "HeadwearAccessory": "headwear",
        "NeckAccessory": "adornment",
        "FaceAccessory": "accessory",
        "Background": "background",
        "Outline": "outline",
        "Palette": "palette",
        "PaletteFull": "palette",
        "Base": "base",
        "Face": "face",
        "Eyewear": "eyewear",
        "Jewelry": "jewelry",
    }
    return mapping.get(category, "general")


def color_name_for_category(
    hex_code: str,
    color_map: Dict[str, str],
    category: str | None = None,
    context: str | None = None,
) -> str:
    resolved_context = context or color_context_for_category(category)
    return nearest_css_name(hex_code, color_map, context=resolved_context)


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
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional JSON file to mirror the CSV output (consumed by the viewer).",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        help="Directory to store per-sprite cache files so runs can be resumed.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip sprites that already have cached results (requires --cache-dir).",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    base_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )
    LOGGER.setLevel(base_level)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)


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
    context: str | None = None,
) -> str:
    lowered = hex_code.lower()
    if lowered in custom_map:
        return custom_map[lowered]
    return generate_epic_color_name(lowered, context=context)


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


def relative_luminance(hex_code: str) -> float:
    r, g, b = hex_to_rgb(hex_code)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mask_bounds(mask: Set[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    rows = [row for row, _ in mask]
    cols = [col for _, col in mask]
    return min(rows), max(rows), min(cols), max(cols)


def mask_within(
    mask: Set[Tuple[int, int]],
    row_min: int,
    row_max: int,
    col_min: int,
    col_max: int,
    tolerance: int = 0,
) -> bool:
    for row, col in mask:
        if row < row_min - tolerance or row > row_max + tolerance:
            return False
        if col < col_min - tolerance or col > col_max + tolerance:
            return False
    return True


def classify_ear_accessory(
    mask: Set[Tuple[int, int]],
    color_hex: str,
    skin_colors: Set[str],
    hair_colors: Set[str],
) -> Tuple[str, str] | None:
    if not mask:
        return None
    lowered = color_hex.lower()
    if lowered in skin_colors or lowered in hair_colors or lowered in {"#000000"}:
        return None
    row_min, row_max, col_min, col_max = mask_bounds(mask)
    height = row_max - row_min + 1
    width = col_max - col_min + 1
    centre_col = (col_min + col_max) / 2.0
    side = "Left" if centre_col < 12 else "Right"
    luminance = relative_luminance(color_hex)
    if luminance > 210 and width <= 2 and height >= 3 and len(mask) >= 3:
        return ("Airpod", side)
    if height >= 4 and width <= 3 and len(mask) >= 3:
        return ("Dangly", side)
    if width >= 3 and height <= 3 and len(mask) >= 3:
        return ("Hoop", side)
    if width <= 2 and height <= 2 and len(mask) >= 2:
        return ("Stud", side)
    return None


def classify_mouth_accessory(
    mask: Set[Tuple[int, int]],
    color_hex: str,
    pixel_array: np.ndarray,
) -> str | None:
    if not mask:
        return None
    row_min, row_max, col_min, col_max = mask_bounds(mask)
    height = row_max - row_min + 1
    width = col_max - col_min + 1
    if row_min < 11 or row_max > 17:
        return None
    if width < 3 or width > 6:
        return None
    if height > 3:
        return None
    if col_min >= 7 and col_max <= 16:
        return None
    unique_hexes = {
        rgb_to_hex(tuple(int(pixel_array[row, col][k]) for k in range(3))) for row, col in mask
    }
    if len(unique_hexes) <= 1:
        return None
    luminance = relative_luminance(color_hex)
    if luminance > 190:
        return "Cigarette"
    if luminance > 120:
        return "CigaretteHolder"
    return "Joint"


def ensure_palette_full_entries(
    refined: List[RegionResult],
    arr: np.ndarray,
    color_map: Dict[str, str],
) -> None:
    total_pixels = arr.shape[0] * arr.shape[1]
    existing = {
        res.color_hex.lower()
        for res in refined
        if res.category == "PaletteFull"
    }
    colour_counter = collect_colors(arr)
    for (r, g, b), count in colour_counter.items():
        hex_code = rgb_to_hex((r, g, b))
        lower = hex_code.lower()
        if lower in existing:
            continue
        color_name = color_name_for_category(hex_code, color_map, "Palette")
        refined.append(
            RegionResult(
                sprite_id=refined[0].sprite_id if refined else "",
                category="PaletteFull",
                variant_hint=f"PaletteFull_{color_name}",
                color_hex=hex_code,
                color_name=color_name,
                coverage_pct=round(count / total_pixels * 100.0, 2),
                notes="full_palette_autofill",
                pixel_mask="",
            )
        )
        existing.add(lower)


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


def detect_pinstripe_background(arr: np.ndarray) -> List[Tuple[str, float]]:
    h, w, _ = arr.shape
    if w < 4:
        return []
    column_hexes: List[str] = []
    for col in range(w):
        column_slice = arr[:, col : col + 1, :]
        counts = collect_colors(column_slice)
        if not counts:
            return []
        (r, g, b), count = counts.most_common(1)[0]
        if count < int(h * 0.85):
            return []
        column_hexes.append(rgb_to_hex((r, g, b)))
    unique_hexes = list(dict.fromkeys(column_hexes))
    if len(unique_hexes) < 2 or len(unique_hexes) > 5:
        return []
    period = None
    for candidate in range(2, min(6, w // 2 + 1)):
        if all(column_hexes[i] == column_hexes[i % candidate] for i in range(w)):
            period = candidate
            break
    if period is None:
        return []
    freq = Counter(column_hexes)
    return [(hex_code, count / w) for hex_code, count in freq.items()]


def detect_panel_background(arr: np.ndarray) -> List[Tuple[str, float]]:
    h, w, _ = arr.shape
    mid_row = h // 2
    mid_col = w // 2
    if mid_row == 0 or mid_col == 0:
        return []
    quadrants = [
        (slice(0, mid_row), slice(0, mid_col)),
        (slice(0, mid_row), slice(mid_col, w)),
        (slice(mid_row, h), slice(0, mid_col)),
        (slice(mid_row, h), slice(mid_col, w)),
    ]
    total_pixels = float(h * w)
    panel_info: List[Tuple[str, float]] = []
    unique_hexes: set[str] = set()
    for row_slice, col_slice in quadrants:
        region = arr[row_slice, col_slice]
        counts = collect_colors(region)
        if not counts:
            return []
        (r, g, b), count = counts.most_common(1)[0]
        quadrant_pixels = region.shape[0] * region.shape[1]
        if quadrant_pixels == 0 or count < max(6, int(quadrant_pixels * 0.45)):
            return []
        hex_code = rgb_to_hex((r, g, b))
        unique_hexes.add(hex_code)
        panel_info.append((hex_code, count / total_pixels))
    if len(unique_hexes) < 3:
        return []
    return panel_info


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

    pinstripe_info = detect_pinstripe_background(arr)
    if pinstripe_info:
        classification = "Pinstripe"
        main_hex = pinstripe_info[0][0]
        coverage = pinstripe_info[0][1]
        pin_palette = [
            (hex_code, max(1, int(round(ratio * h * w))))
            for hex_code, ratio in pinstripe_info
        ]
        return main_hex, coverage, classification, pin_palette, [hex_code for hex_code, _ in pinstripe_info]

    panel_info = detect_panel_background(arr)
    if panel_info:
        classification = "Panels"
        main_hex = panel_info[0][0]
        coverage = panel_info[0][1]
        panel_palette = [
            (hex_code, max(1, int(round(ratio * h * w))))
            for hex_code, ratio in panel_info
        ]
        return main_hex, coverage, classification, panel_palette, [hex_code for hex_code, _ in panel_info]

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
    border_presence: Dict[str, Dict[str, bool]] = defaultdict(
        lambda: {"top": False, "bottom": False, "left": False, "right": False}
    )
    for col in range(cols):
        r, g, b, a = [int(x) for x in arr[0, col]]
        if a >= 16:
            border_presence[rgb_to_hex((r, g, b)).lower()]["top"] = True
        r, g, b, a = [int(x) for x in arr[rows - 1, col]]
        if a >= 16:
            border_presence[rgb_to_hex((r, g, b)).lower()]["bottom"] = True
    for row in range(rows):
        r, g, b, a = [int(x) for x in arr[row, 0]]
        if a >= 16:
            border_presence[rgb_to_hex((r, g, b)).lower()]["left"] = True
        r, g, b, a = [int(x) for x in arr[row, cols - 1]]
        if a >= 16:
            border_presence[rgb_to_hex((r, g, b)).lower()]["right"] = True
    for hex_code, flags in border_presence.items():
        if (flags["top"] and flags["bottom"]) or (flags["left"] and flags["right"]):
            candidate_hexes.add(hex_code)
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
        color_name = color_name_for_category(hex_code, color_map, category)
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
    bg_name = color_name_for_category(bg_hex, color_map, "Background")
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
            color_name = color_name_for_category(hex_code, color_map, "Background")
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
    total_pixels = 24 * 24
    all_colors = collect_colors(arr)
    for hex_code, count in dominant_colors(all_colors, top_colors):
        color_name = color_name_for_category(hex_code, color_map, "Palette")
        coverage = 100.0 * count / total_pixels
        results.append(
            RegionResult(
                sprite_id=sprite_id,
                category="Palette",
                variant_hint=f"Palette_{color_name}",
                color_hex=hex_code,
                color_name=color_name,
                coverage_pct=round(coverage, 2),
                notes="global_dominant_color",
            )
        )

    # Full palette coverage for validation / downstream processing.
    for (r, g, b), count in all_colors.items():
        hex_code = rgb_to_hex((r, g, b))
        color_name = color_name_for_category(hex_code, color_map, "Palette")
        coverage = 100.0 * count / total_pixels
        results.append(
            RegionResult(
                sprite_id=sprite_id,
                category="PaletteFull",
                variant_hint=f"PaletteFull_{color_name}",
                color_hex=hex_code,
                color_name=color_name,
                coverage_pct=round(coverage, 2),
                notes=f"full_palette; pixels={count}",
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


def region_result_to_dict(record: RegionResult) -> Dict[str, Any]:
    return {
        "sprite_id": record.sprite_id,
        "category": record.category,
        "variant_hint": record.variant_hint,
        "color_hex": record.color_hex,
        "color_name": record.color_name,
        "coverage_pct": round(record.coverage_pct, 2),
        "notes": record.notes,
        "pixel_mask": record.pixel_mask,
    }


def region_result_from_dict(payload: Dict[str, Any]) -> RegionResult:
    return RegionResult(
        sprite_id=payload["sprite_id"],
        category=payload["category"],
        variant_hint=payload["variant_hint"],
        color_hex=payload["color_hex"],
        color_name=payload.get("color_name", ""),
        coverage_pct=float(payload.get("coverage_pct", 0.0)),
        notes=payload.get("notes", ""),
        pixel_mask=payload.get("pixel_mask", ""),
    )


def write_json_output(path: Path, records: List[RegionResult]) -> None:
    ensure_directory(path.parent)
    data = [region_result_to_dict(record) for record in records]
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def load_cached_results(path: Path) -> List[RegionResult]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [region_result_from_dict(item) for item in payload]


def write_cache_file(path: Path, records: List[RegionResult]) -> None:
    ensure_directory(path.parent)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump([region_result_to_dict(record) for record in records], handle, indent=2)
    tmp_path.replace(path)


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
    primary = color_name_for_category(palette[0][0], color_map, "Background")
    if stripe_colors:
        stripe_names: List[str] = []
        for hex_code in stripe_colors:
            name = color_name_for_category(hex_code, color_map, "Background")
            if name not in stripe_names:
                stripe_names.append(name)
        suffix = "_".join(stripe_names).replace(" ", "")
        return f"Stripe_{suffix}"
    if bg_class == "Pinstripe":
        stripe_names: List[str] = []
        for hex_code, _ in palette:
            name = color_name_for_category(hex_code, color_map, "Background")
            if name not in stripe_names:
                stripe_names.append(name)
        suffix = "_".join(stripe_names[:4]).replace(" ", "")
        return f"Pinstripe_{suffix}"
    if bg_class == "Panels":
        panel_names: List[str] = []
        for hex_code, _ in palette[:4]:
            name = color_name_for_category(hex_code, color_map, "Background")
            if name not in panel_names:
                panel_names.append(name)
        suffix = "_".join(panel_names).replace(" ", "")
        return f"Panels_{suffix}"
    if bg_class == "Brick":
        if len(palette) < 2:
            return f"Brick_{primary}".replace(" ", "")
        secondary_count = palette[1][1]
        if secondary_count < 0.18 * total_pixels:
            return f"Brick_{primary}".replace(" ", "")
        secondary = color_name_for_category(palette[1][0], color_map, "Background")
        components = [primary, secondary]
        if len(palette) > 2 and palette[2][1] >= 0.08 * total_pixels:
            tertiary = color_name_for_category(palette[2][0], color_map, "Background")
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
        secondary = color_name_for_category(palette[1][0], color_map, "Background")
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
    import sys

    print(f"[REFINE] Starting postprocess for {sprite_id}", flush=True)

    total_pixels = 24 * 24
    outline_set = set(outline_pixels)

    print(f"[REFINE] Building category_entries from {len(results)} results", flush=True)
    category_entries: Dict[str, List[Tuple[RegionResult, set[Tuple[int, int]]]]] = defaultdict(list)
    for idx, res in enumerate(results):
        if idx % 5 == 0:
            print(f"[REFINE] Parsing result {idx}/{len(results)}: category={res.category}", flush=True)
        mask_set = parse_pixel_mask(res.pixel_mask)
        category_entries[res.category].append((res, mask_set))

    print(f"[REFINE] category_entries built: {list(category_entries.keys())}", flush=True)

    sprite_lower = sprite_id.lower()
    allow_facial_hair = not sprite_lower.startswith("lady_")

    if not allow_facial_hair and category_entries.get("FacialHair"):
        for res, mask in category_entries["FacialHair"]:
            res.category = "Hair"
            category_entries["Hair"].append((res, mask))
        category_entries.pop("FacialHair", None)

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
        elif res.category == "Clothing":
            clothing_union.update(mask)

    def update_entry_mask(res: RegionResult, new_mask: set[Tuple[int, int]]) -> None:
        category = res.category
        existing_mask = parse_pixel_mask(res.pixel_mask)
        if category == "Hair" and existing_mask:
            hair_union.difference_update(existing_mask)
        if category == "Clothing" and existing_mask:
            clothing_union.difference_update(existing_mask)
        if category not in category_to_entry:
            return
        for idx, (entry, mask) in enumerate(category_to_entry[category]):
            if entry is res:
                category_to_entry[category][idx] = (res, new_mask)
                break
        for idx, (entry, mask) in enumerate(processed_entries):
            if entry is res:
                processed_entries[idx] = (res, new_mask)
                break
        res.pixel_mask = mask_to_string(new_mask)
        res.coverage_pct = round(len(new_mask) / total_pixels * 100.0, 2)
        if category == "Hair":
            hair_union.update(new_mask)
        if category == "Clothing":
            clothing_union.update(new_mask)

    def remove_entry(res: RegionResult) -> None:
        existing_mask = parse_pixel_mask(res.pixel_mask)
        category = res.category
        if category in category_to_entry:
            category_to_entry[category] = [
                (entry, mask) for entry, mask in category_to_entry[category] if entry is not res
            ]
        processed_entries[:] = [(entry, mask) for entry, mask in processed_entries if entry is not res]
        refined[:] = [entry for entry in refined if entry is not res]
        if category == "Hair" and existing_mask:
            hair_union.difference_update(existing_mask)
            color_lower = res.color_hex.lower()
            if not any(
                entry.color_hex.lower() == color_lower for entry, _ in category_to_entry.get("Hair", [])
            ):
                hair_color_set.discard(color_lower)
        if category == "Headwear":
            color_lower = res.color_hex.lower()
            if not any(
                entry.color_hex.lower() == color_lower for entry, _ in category_to_entry.get("Headwear", [])
            ):
                headwear_color_set.discard(color_lower)
        if category == "Clothing" and existing_mask:
            clothing_union.difference_update(existing_mask)

    def update_skin_tracking(hex_code: str, coords: set[Tuple[int, int]]) -> None:
        if not coords:
            return
        skin_union.update(coords)
        lowered = hex_code.lower()
        skin_colors_map[lowered] |= coords
        skin_color_set.add(lowered)

    def extract_note_value(res: RegionResult, key: str) -> str | None:
        if not res.notes:
            return None
        for part in res.notes.split(";"):
            segment = part.strip()
            if segment.startswith(f"{key}="):
                return segment.split("=", 1)[1]
        return None

    def append_note(res: RegionResult, key: str, value: str) -> None:
        entry = f"{key}={value}"
        if res.notes:
            parts = [segment.strip() for segment in res.notes.split(";") if segment.strip()]
            if entry in parts:
                return
            parts.append(entry)
            res.notes = ";".join(parts)
        else:
            res.notes = entry

    def replace_note(res: RegionResult, key: str, value: str | None) -> None:
        parts = [segment.strip() for segment in (res.notes or "").split(";") if segment.strip()]
        filtered = [segment for segment in parts if not segment.startswith(f"{key}=")]
        if value is not None:
            filtered.append(f"{key}={value}")
        res.notes = ";".join(filtered)

    def layer_key_for_result(res: RegionResult) -> str | None:
        category = res.category or ""
        if category in {"Palette", "PaletteFull", "Unassigned"}:
            return None
        hint = res.variant_hint or ""
        parts = hint.split("_")
        if len(parts) == 1:
            return hint
        if category == "Jewelry" and len(parts) >= 3 and parts[1].startswith("Earring"):
            return "_".join(parts[:3])
        if category == "Face" and parts[1] == "MouthAccessory" and len(parts) >= 3:
            return "_".join(parts[:3])
        if category == "FaceAccessory" and len(parts) >= 3 and parts[1].startswith("Earpiece"):
            return "_".join(parts[:3])
        return "_".join(parts[:2])

    def collapse_logical_layers(results: List[RegionResult]) -> None:
        grouped: Dict[str, List[RegionResult]] = defaultdict(list)
        key_order: List[str] = []
        passthrough: List[RegionResult] = []
        for res in results:
            key = layer_key_for_result(res)
            if not key:
                passthrough.append(res)
                continue
            if key not in grouped:
                key_order.append(key)
            grouped[key].append(res)
        collapsed: List[RegionResult] = []
        for key in key_order:
            candidates = grouped[key]
            if len(candidates) == 1:
                collapsed.append(candidates[0])
                continue
            primary = max(
                candidates,
                key=lambda res: len(parse_pixel_mask(res.pixel_mask)),
            )
            union_mask: set[Tuple[int, int]] = set()
            for res in candidates:
                union_mask |= parse_pixel_mask(res.pixel_mask)
            if union_mask:
                primary.pixel_mask = mask_to_string(union_mask)
                primary.coverage_pct = round(len(union_mask) / total_pixels * 100.0, 2)
            accent_names = {
                res.color_name
                for res in candidates
                if res is not primary and res.color_name
            }
            if accent_names:
                append_note(primary, "layer_accents", ",".join(sorted(accent_names)))
            collapsed.append(primary)
        results[:] = passthrough + collapsed

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
        cols = [col for _, col in mask_set]
        min_row, max_row = min(rows), max(rows)
        if max_row >= 19:
            return False
        if len(mask_set) < 4:
            return False
        width = max(cols) - min(cols) + 1
        if width < 3:
            return False
        return min_row <= 7 and max_row <= 18

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

    def looks_like_headphones(mask_set: set[Tuple[int, int]]) -> bool:
        if not mask_set or len(mask_set) < 12:
            return False
        rows = [row for row, _ in mask_set]
        cols = [col for _, col in mask_set]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        width = max_col - min_col + 1
        if width < 8 or min_row < 4 or max_row > 20:
            return False
        spans_left = any(col <= 5 for col in cols)
        spans_right = any(col >= 18 for col in cols)
        if not (spans_left and spans_right):
            return False
        visited: set[Tuple[int, int]] = set()
        large_components = 0
        for pixel in mask_set:
            if pixel in visited:
                continue
            queue: Deque[Tuple[int, int]] = deque([pixel])
            component: set[Tuple[int, int]] = set()
            visited.add(pixel)
            while queue:
                r, c = queue.popleft()
                component.add((r, c))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nbr = (r + dr, c + dc)
                    if nbr in mask_set and nbr not in visited:
                        visited.add(nbr)
                        queue.append(nbr)
            if len(component) >= 3:
                large_components += 1
        return large_components >= 2

    def classify_headwear_shape(mask_set: set[Tuple[int, int]]) -> str | None:
        if not mask_set:
            return None
        rows = [row for row, _ in mask_set]
        cols = [col for _, col in mask_set]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        height = max_row - min_row + 1
        width = max_col - min_col + 1
        row_counts = Counter(rows)
        top_band_rows = [row for row in row_counts if row <= min_row + 1]
        top_pixels = sum(row_counts[row] for row in top_band_rows)
        top_ratio = top_pixels / len(mask_set)
        bottom_pixels = row_counts.get(max_row, 0)
        spans_left = min_col <= 1
        spans_right = max_col >= 22
        touches_bottom = max_row >= 18
        if height <= 3 and top_ratio > 0.6:
            return "Halo"
        if touches_bottom and height >= 8 and width >= 8:
            return "Hood"
        if (
            not touches_bottom
            and height >= 5
            and height <= 9
            and width >= 7
            and top_ratio >= 0.25
            and bottom_pixels <= row_counts.get(min_row, 0) + 3
        ):
            return "Beanie"
        if min_row <= 1 and top_ratio >= 0.25 and height >= 5:
            return "Crown"
        if width >= 12 and height <= 7 and spans_left and spans_right:
            return "Hat_Cowboy"
        if width >= 11 and height >= 6 and bottom_pixels > row_counts.get(min_row, 0) + 2:
            return "Hat_Bucket"
        if width <= 9 and height >= 6 and bottom_pixels >= row_counts.get(min_row, 0) - 1:
            return "Beanie"
        if height >= 8 and width <= 8:
            return "Hat_Top"
        if height <= 5 and width >= 10 and not spans_left and not spans_right:
            return "Headband"
        return None

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
        original_category = target_category
        if not allow_facial_hair and target_category == "FacialHair":
            target_category = "Hair"
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
        color_name = color_name_for_category(color_hex, color_map, target_category)
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
            hair_union_local: set[Tuple[int, int]] = set()
            for _, hair_mask in category_to_entry.get("Hair", []):
                hair_union_local |= hair_mask
            headwear_union_local: set[Tuple[int, int]] = set()
            for _, headwear_mask in category_to_entry.get("Headwear", []):
                headwear_union_local |= headwear_mask
            cleaned_mask = merged_mask - hair_union_local - headwear_union_local
            if cleaned_mask:
                merged_mask = cleaned_mask
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
            primary_entry.color_name = color_name_for_category(dominant_hex, color_map, "Skin")
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
    print(f"[REFINE] merge_skin_variants completed", flush=True)

    def reclaim_dark_foreground_from_background() -> None:
        print(f"[REFINE] reclaim_dark_foreground_from_background starting", flush=True)
        background_items = list(category_to_entry.get("Background", []))
        if not background_items:
            print(f"[REFINE] reclaim_dark: no background items", flush=True)
            return
        changed = False
        adjacency_offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for bg_idx, (res, mask) in enumerate(background_items):
            print(f"[REFINE] reclaim_dark: processing bg item {bg_idx+1}/{len(background_items)}, mask_size={len(mask)}", flush=True)
            if not mask:
                continue
            colour_luminance = relative_luminance(res.color_hex)
            if colour_luminance > 135:
                print(f"[REFINE] reclaim_dark: skipping light color (luminance={colour_luminance})", flush=True)
                continue
            remaining = set(mask)
            components: List[set[Tuple[int, int]]] = []
            outer_iter_count = 0
            MAX_OUTER_ITERATIONS = 1000
            while remaining:
                outer_iter_count += 1
                if outer_iter_count > MAX_OUTER_ITERATIONS:
                    print(f"[REFINE] reclaim_dark: INFINITE LOOP DETECTED! outer while exceeded {MAX_OUTER_ITERATIONS} iterations, remaining={len(remaining)}", flush=True)
                    raise RuntimeError(f"Infinite loop in reclaim_dark_foreground outer while: {outer_iter_count} iterations, {len(remaining)} pixels remaining")
                start = remaining.pop()
                stack = [start]
                component = {start}
                inner_iter_count = 0
                MAX_INNER_ITERATIONS = 10000
                while stack:
                    inner_iter_count += 1
                    if inner_iter_count > MAX_INNER_ITERATIONS:
                        print(f"[REFINE] reclaim_dark: INFINITE LOOP DETECTED! inner while exceeded {MAX_INNER_ITERATIONS} iterations, stack_size={len(stack)}, component_size={len(component)}", flush=True)
                        raise RuntimeError(f"Infinite loop in reclaim_dark_foreground inner while: {inner_iter_count} iterations")
                    row, col = stack.pop()
                    for dr, dc in adjacency_offsets:
                        coord = (row + dr, col + dc)
                        if coord in remaining:
                            remaining.remove(coord)
                            stack.append(coord)
                            component.add(coord)
                components.append(component)
            print(f"[REFINE] reclaim_dark: found {len(components)} components in {outer_iter_count} iterations", flush=True)
            leftover = set(mask)
            for comp in components:
                if len(comp) < 12:
                    continue
                rows = [row for row, _ in comp]
                cols = [col for _, col in comp]
                max_row = max(rows)
                if max_row <= 5:
                    continue
                interior = sum(
                    1 for row, col in comp if 4 <= row <= 20 and 3 <= col <= 20
                )
                if interior / len(comp) < 0.4:
                    continue
                adjacency_found = False
                for row, col in comp:
                    for dr, dc in adjacency_offsets:
                        nbr = (row + dr, col + dc)
                        if (
                            nbr in skin_union
                            or nbr in outline_set
                            or nbr in mouth_union
                            or nbr in eye_union
                        ):
                            adjacency_found = True
                            break
                    if adjacency_found:
                        break
                if not adjacency_found:
                    continue
                add_pixels("Hair", set(comp), res.color_hex)
                leftover -= comp
                changed = True
            if leftover != set(mask):
                if leftover:
                    update_entry_mask(res, leftover)
                else:
                    remove_entry(res)
        if changed:
            category_entries["Hair"] = category_to_entry.get("Hair", [])
            category_entries["Background"] = category_to_entry.get("Background", [])

    reclaim_dark_foreground_from_background()
    print(f"[REFINE] reclaim_dark_foreground_from_background completed", flush=True)

    processed_headwear: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
    headwear_processed_union: set[Tuple[int, int]] = set()
    headwear_color_set: set[str] = set()
    print(f"[REFINE] Processing {len(headwear_entries)} headwear entries", flush=True)
    for hw_idx, (res, mask) in enumerate(headwear_entries):
        print(f"[REFINE] Headwear {hw_idx+1}/{len(headwear_entries)}: mask_size={len(mask)}", flush=True)
        mask = mask - outline_candidates
        if background_mask:
            mask = {coord for coord in mask if coord not in background_mask}
        if not mask:
            print(f"[REFINE] Headwear: mask is empty after filtering, continuing", flush=True)
            continue
        print(f"[REFINE] Headwear: creating color counter for {len(mask)} pixels", flush=True)
        print(f"[REFINE] Headwear: mask type={type(mask)}, sample={list(mask)[:5] if mask else 'empty'}", flush=True)
        color_counts = Counter(tuple(int(c) for c in arr[row, col][:3]) for row, col in mask)
        print(f"[REFINE] Headwear: color_counts created with {len(color_counts)} unique colors", flush=True)
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
        print(f"[REFINE] Headwear: checking hair-like properties...", flush=True)
        looks_hair = looks_like_hair(mask)
        print(f"[REFINE] Headwear: looks_like_hair={looks_hair}", flush=True)
        if (
            looks_hair
            and lower_ratio >= 0.4
            and top_ratio <= 0.4
        ):
            print(f"[REFINE] Headwear: checking touches_skin/touches_hair...", flush=True)
            if touches_skin(mask) or touches_hair(mask):
                add_pixels("Hair", set(mask), dominant_hex)
                continue
        res.color_hex = dominant_hex
        res.color_name = color_name_for_category(dominant_hex, color_map, "Headwear")
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

    print(f"[REFINE] Headwear loop completed, processing Hair entries", flush=True)
    hair_entries_list = list(category_entries.get("Hair", []))  # Snapshot copy to avoid infinite loop
    print(f"[REFINE] Processing {len(hair_entries_list)} hair entries", flush=True)
    for hair_idx, (res, mask) in enumerate(hair_entries_list):
        print(f"[REFINE] Hair {hair_idx+1}/{len(hair_entries_list)}: mask_size={len(mask)}", flush=True)
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
            color_name = color_name_for_category(color_hex, color_map, "Eyes")
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
        primary_entry.color_name = color_name_for_category(dominant_hex, color_map, "Hair")
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

    def peel_nonhair_from_hair() -> None:
        hair_entries = category_to_entry.get("Hair", [])
        if not hair_entries:
            return
        updated: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in hair_entries:
            if not mask:
                continue
            color_groups: Dict[str, set[Tuple[int, int]]] = defaultdict(set)
            for row, col in mask:
                hex_code = rgb_to_hex(tuple(int(arr[row, col][k]) for k in range(3)))
                color_groups[hex_code].add((row, col))
            primary_hex = res.color_hex.lower()
            kept: set[Tuple[int, int]] = set()
            removed_any = False
            for hex_code, coords in color_groups.items():
                lower = hex_code.lower()
                if lower == primary_hex:
                    kept |= coords
                    continue
                ratio = len(coords) / len(mask)
                luminance_delta = abs(relative_luminance(hex_code) - relative_luminance(res.color_hex))
                palette_distance = distance_to_hair_palette(hex_code)
                if ratio <= 0.22 and (luminance_delta >= 25 or palette_distance > 32):
                    coord_set = set(coords)
                    if is_mouth_candidate(coord_set):
                        add_pixels("Mouth", coord_set, hex_code)
                    elif touches_skin(coord_set):
                        add_pixels("FaceAccessory", coord_set, hex_code)
                    elif min(row for row, _ in coord_set) <= 5:
                        add_pixels("Headwear", coord_set, hex_code)
                    else:
                        add_pixels("Headwear", coord_set, hex_code)
                    removed_any = True
                else:
                    kept |= coords
            if removed_any:
                if kept:
                    update_entry_mask(res, kept)
                    updated.append((res, kept))
                else:
                    remove_entry(res)
            else:
                updated.append((res, mask))
        if updated:
            category_to_entry["Hair"] = updated

    peel_nonhair_from_hair()

    def merge_facial_hair_variants() -> None:
        facial_entries = category_to_entry.get("FacialHair", [])
        if not facial_entries:
            return
        primary_entry, _ = max(facial_entries, key=lambda item: len(item[1]))
        merged_mask: set[Tuple[int, int]] = set()
        accent_colors: List[str] = []
        for entry, mask in facial_entries:
            merged_mask |= mask
            if entry is not primary_entry:
                accent_colors.append(color_name_for_category(entry.color_hex, color_map, "FacialHair"))
        if not merged_mask:
            return
        if accent_colors:
            append_note(primary_entry, "facialhair_accents", ",".join(sorted(set(accent_colors))))
        rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in merged_mask)
        if rgb_counts:
            dominant_rgb, _ = max(rgb_counts.items(), key=lambda item: item[1])
            dominant_hex = rgb_to_hex(dominant_rgb)
            primary_entry.color_hex = dominant_hex
            primary_entry.color_name = color_name_for_category(dominant_hex, color_map, "FacialHair")
            primary_entry.variant_hint = f"FacialHair_Main_{primary_entry.color_name}"
        primary_entry.pixel_mask = mask_to_string(merged_mask)
        primary_entry.coverage_pct = round(len(merged_mask) / total_pixels * 100.0, 2)
        category_to_entry["FacialHair"] = [(primary_entry, merged_mask)]
        processed_entries[:] = [
            (primary_entry if res is primary_entry else res, merged_mask if res is primary_entry else mask)
            for res, mask in processed_entries
            if res.category != "FacialHair" or res is primary_entry
        ]
        refined[:] = [res for res in refined if res.category != "FacialHair"]
        refined.append(primary_entry)

    merge_facial_hair_variants()

    for res, mask in category_entries.get("Eyes", []):
        mask = mask - outline_candidates
        if not mask:
            continue
        print(f"[REFINE] Eyes: initial mask size {len(mask)}", flush=True)
        outline_like_pixels = {
            coord
            for coord in mask
            if rgb_to_hex(
                tuple(int(arr[coord[0], coord[1]][channel]) for channel in range(3))
            ).lower()
            in OUTLINE_HEX_CODES
        }
        if outline_like_pixels:
            print(
                f"[REFINE] Eyes: reassigning {len(outline_like_pixels)} outline pixels to base",
                flush=True,
            )
            mask -= outline_like_pixels
            outline_candidates |= outline_like_pixels
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
            primary_entry.color_name = color_name_for_category(dominant_hex, color_map, "Eyes")
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
        def ensure_flag(res: RegionResult, flag: str) -> None:
            notes = res.notes or ""
            parts = [segment.strip() for segment in notes.split(";") if segment.strip()]
            if flag in parts:
                return
            parts.append(flag)
            res.notes = ";".join(parts)
        for res, mask in headwear_entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            height = max(rows) - min(rows) + 1
            width = max(cols) - min(cols) + 1
            if max(rows) <= 7 and width >= 5:
                res.variant_hint = f"Headwear_Cap_{res.color_name}"
        eye_color_set = {
            res.color_hex.lower()
            for res, _ in category_to_entry.get("Eyes", [])
            if res.color_hex
        }
        face_entries = category_to_entry.get("FaceAccessory", [])
        reflection_entries = [
            (res, mask)
            for res, mask in face_entries
            if res.color_hex and res.color_hex.lower() in ACCESSORY_WHITE_HEXES and mask
        ]
        glasses_bounds: List[Tuple[int, int, int, int, str]] = []
        for res, mask in face_entries:
            if not mask:
                continue
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            min_row, max_row = min(rows), max(rows)
            width = max(cols) - min(cols) + 1
            height = max_row - min_row + 1
            overlap = mask & eye_union
            touches_eye = bool(overlap)
            if overlap:
                overlap_cols = [col for _, col in overlap]
                coverage_ratio = len(overlap) / len(mask)
                if (
                    coverage_ratio >= 0.35
                    and width >= 4
                    and min(overlap_cols) <= 11
                    and max(overlap_cols) >= 12
                    and min_row >= 6
                    and max_row <= 16
                    and height <= 8
                        and max_row <= 16
                        and height <= 8
                ):
                    color_name = color_name_for_category(res.color_hex, color_map, context="glass")
                    variant = f"FaceAccessory_Glasses_{color_name}"
                    res.variant_hint = variant
                    res.color_name = color_name
                    ensure_flag(res, "glasses_lens")
                    ensure_flag(res, "glasses_tint")
                    glasses_bounds.append((min_row, max_row, min(cols), max(cols), variant))
                    continue
            if (
                min_row >= 6
                and max_row <= 16
                and height <= 6
                and width >= 4
                and looks_like_glasses(mask, res.color_hex)
                and res.color_hex.lower() not in eye_color_set
            ):
                has_reflection = False
                for refl_res, refl_mask in reflection_entries:
                    if refl_res is res:
                        continue
                    r_rows = [row for row, _ in refl_mask]
                    r_cols = [col for _, col in refl_mask]
                    if not r_rows or not r_cols:
                        continue
                    r_min_row, r_max_row = min(r_rows), max(r_rows)
                    r_min_col, r_max_col = min(r_cols), max(r_cols)
                    if (
                        r_min_row >= min_row - 1
                        and r_max_row <= max_row + 1
                        and r_min_col >= min(cols) - 1
                        and r_max_col <= max(cols) + 1
                    ):
                        has_reflection = True
                        break
                color_name = color_name_for_category(res.color_hex, color_map, context="glass")
                variant = f"FaceAccessory_Glasses_{color_name}"
                res.variant_hint = variant
                res.color_name = color_name
                ensure_flag(res, "glasses_lens")
                if has_reflection:
                    ensure_flag(res, "glasses_reflection")
                else:
                    ensure_flag(res, "glasses_solid")
                glasses_bounds.append((min_row, max_row, min(cols), max(cols), variant))
                continue
            if not touches_eye:
                touches_eye = any(
                    (row + dr, col + dc) in eye_union
                    for row, col in mask
                    for dr in (-1, 0, 1)
                    for dc in (-1, 0, 1)
                )
            if (
                res.color_hex
                and res.color_hex.lower() in ACCESSORY_WHITE_HEXES
                and min_row >= 6
                and max_row <= 16
                and height <= 6
                and width >= 2
                and touches_eye
            ):
                color_name = color_name_for_category(res.color_hex, color_map, context="glass")
                variant = f"FaceAccessory_Glasses_{color_name}"
                res.variant_hint = variant
                res.color_name = color_name
                ensure_flag(res, "glasses_reflection")
                ensure_flag(res, "glasses_lens")
                glasses_bounds.append((min_row, max_row, min(cols), max(cols), variant))
                continue
            if looks_like_headphones(mask):
                color_name = color_name_for_category(res.color_hex, color_map, "FaceAccessory")
                res.variant_hint = f"FaceAccessory_Headphones_{color_name}"
                res.color_name = color_name
                ensure_flag(res, "headphones")
                continue
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
                        res.color_name = color_name_for_category(res.color_hex, color_map, context="glass")
                        ensure_flag(res, "glasses_reflection")
                        break

    def merge_glasses_entries() -> None:
        entries = category_to_entry.get("FaceAccessory", [])
        if not entries:
            return
        glasses_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        other_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in entries:
            notes = res.notes or ""
            rows = [row for row, _ in mask]
            cols = [col for _, col in mask]
            min_row = min(rows) if rows else 24
            max_row = max(rows) if rows else -1
            width = max(cols) - min(cols) + 1 if cols else 0
            height = max_row - min_row + 1 if rows else 0
            adjacent_to_eye = bool(mask & eye_union) or any(
                (row + dr, col + dc) in eye_union
                for row, col in mask
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
            )
            is_glasses_candidate = (
                "glasses" in notes
                or res.variant_hint.startswith("FaceAccessory_Glasses_")
                or (
                    mask
                    and 6 <= min_row <= 16
                    and 2 <= width <= 12
                    and height <= 8
                    and (
                        res.color_hex.lower() in ACCESSORY_WHITE_HEXES
                        or looks_like_glasses(mask, res.color_hex)
                    )
                )
            )
            if is_glasses_candidate:
                glasses_entries.append((res, mask))
            else:
                other_entries.append((res, mask))
        if not glasses_entries:
            return
        grouped: Dict[str, List[Tuple[RegionResult, set[Tuple[int, int]]]]] = {}
        for res, mask in glasses_entries:
            key = res.variant_hint if res.variant_hint.startswith("FaceAccessory_Glasses_") else "FaceAccessory_Glasses"
            grouped.setdefault(key, []).append((res, mask))
        merged_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        removed_ids = {id(res) for res, _ in glasses_entries}
        for key, items in grouped.items():
            union_mask: set[Tuple[int, int]] = set()
            color_counter = Counter()
            note_fragments: set[str] = set()
            for res, mask in items:
                union_mask |= mask
                color_counter.update([res.color_hex.lower()])
                if res.notes:
                    note_fragments.update(segment.strip() for segment in res.notes.split(";") if segment.strip())
            dominant_hex = max(color_counter.items(), key=lambda kv: kv[1])[0]
            color_name = color_name_for_category(dominant_hex, color_map, context="glass")
            variant = f"FaceAccessory_Glasses_{color_name}"
            merged_res = RegionResult(
                sprite_id=items[0][0].sprite_id,
                category="FaceAccessory",
                variant_hint=variant,
                color_hex=dominant_hex,
                color_name=color_name,
                coverage_pct=round(len(union_mask) / total_pixels * 100.0, 2),
                notes=";".join(sorted(note_fragments)) if note_fragments else "glasses_merged",
                pixel_mask=mask_to_string(union_mask),
            )
            merged_entries.append((merged_res, union_mask))
        category_to_entry["FaceAccessory"] = other_entries + merged_entries
        processed_entries[:] = [
            (res, mask) for res, mask in processed_entries if id(res) not in removed_ids
        ] + merged_entries
        refined[:] = [res for res in refined if id(res) not in removed_ids]
        refined.extend([res for res, _ in merged_entries])

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
            elif (
                classify_headwear_shape(mask) is None
                and min_row <= 2
                and max_row >= 10
                and relative_luminance(res.color_hex) <= 120
                and sum(1 for row, _ in mask if 6 <= row <= 14) >= 0.3 * len(mask)
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

    def connected_components_from_mask(mask: set[Tuple[int, int]]) -> List[set[Tuple[int, int]]]:
        components: List[set[Tuple[int, int]]] = []
        remaining = set(mask)
        while remaining:
            start = remaining.pop()
            stack = [start]
            component: set[Tuple[int, int]] = {start}
            while stack:
                row, col = stack.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    coord = (row + dr, col + dc)
                    if coord in remaining:
                        remaining.remove(coord)
                        stack.append(coord)
                        component.add(coord)
            components.append(component)
        return components

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
        allowed_rows = range(8, 18)
        allowed_cols = range(4, 20)
        trimmed_mask: set[Tuple[int, int]] = set()
        for row, col in merged_mask:
            if row not in allowed_rows or col not in allowed_cols:
                continue
            rgb = tuple(int(arr[row, col][k]) for k in range(3))
            if rgb_to_hex(rgb).lower() in skin_color_set:
                continue
            trimmed_mask.add((row, col))
        if not trimmed_mask:
            trimmed_mask = {coord for coord in merged_mask if coord[0] in allowed_rows and coord[1] in allowed_cols}
        if trimmed_mask:
            components = connected_components_from_mask(trimmed_mask)
            scored_components: List[Tuple[float, set[Tuple[int, int]]]] = []
            for comp in components:
                rows = [row for row, _ in comp]
                cols = [col for _, col in comp]
                size = len(comp)
                row_span = max(rows) - min(rows) + 1
                col_center = sum(cols) / size
                centre_distance = abs(col_center - 11.5)
                score = size - centre_distance
                if row_span <= 3 or size >= 3:
                    scored_components.append((score, comp))
            scored_components.sort(key=lambda item: item[0], reverse=True)
            selected_mask: set[Tuple[int, int]] = set()
            for score, comp in scored_components:
                if not selected_mask:
                    selected_mask |= comp
                    continue
                overlap = selected_mask & comp
                if overlap:
                    selected_mask |= comp
                elif len(comp) >= 3:
                    selected_mask |= comp
            if selected_mask:
                merged_mask = selected_mask
        rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in merged_mask)
        filtered = [item for item in rgb_counts.items() if rgb_to_hex(item[0]).lower() not in skin_color_set]
        if filtered:
            dominant_rgb = max(filtered, key=lambda kv: kv[1])[0]
        else:
            dominant_rgb = min(
                rgb_counts.items(),
                key=lambda kv: (relative_luminance(rgb_to_hex(kv[0])), -kv[1]),
            )[0]
        dominant_hex = rgb_to_hex(dominant_rgb)
        primary_entry.color_hex = dominant_hex
        primary_entry.color_name = color_name_for_category(dominant_hex, color_map, "Mouth")
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
    def component_dominant_hex(comp: set[Tuple[int, int]]) -> str:
        rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in comp)
        dominant_rgb = max(rgb_counts.items(), key=lambda kv: kv[1])[0]
        return rgb_to_hex(dominant_rgb)

    def looks_like_headwear_component(comp: set[Tuple[int, int]]) -> bool:
        if not comp:
            return False
        rows = [row for row, _ in comp]
        cols = [col for _, col in comp]
        min_row, max_row = min(rows), max(rows)
        width = max(cols) - min(cols) + 1
        height = max_row - min_row + 1
        if min_row <= 2 and width >= 4:
            return True
        if min_row <= 4 and height <= 6 and width >= 6:
            return True
        return False

    def promote_glasses_from_outline() -> None:
        if not outline_candidates or not eye_union:
            return
        visited: set[Tuple[int, int]] = set()
        height, width = arr.shape[:2]
        pending: List[Tuple[set[Tuple[int, int]], str]] = []
        for start in list(outline_candidates):
            if start in visited or start not in outline_candidates:
                continue
            stack = [start]
            component: set[Tuple[int, int]] = set()
            while stack:
                row, col = stack.pop()
                if (row, col) in visited or (row, col) not in outline_candidates:
                    continue
                visited.add((row, col))
                component.add((row, col))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in visited:
                        if (nr, nc) in outline_candidates:
                            stack.append((nr, nc))
            if len(component) < 4:
                continue
            rows = [r for r, _ in component]
            cols = [c for _, c in component]
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)
            comp_width = max_col - min_col + 1
            comp_height = max_row - min_row + 1
            if comp_width < 4 or comp_height > 6:
                continue
            if min_row < 5 or max_row > 16:
                continue
            if comp_width < comp_height:
                continue
            touches_eye = bool(component & eye_union)
            if not touches_eye:
                for row, col in component:
                    neighbourhood = {
                        (row + dr, col + dc)
                        for dr in (-1, 0, 1)
                        for dc in (-1, 0, 1)
                    }
                    if neighbourhood & eye_union:
                        touches_eye = True
                        break
            if not touches_eye:
                continue
            sample_row, sample_col = next(iter(component))
            rgb = tuple(int(arr[sample_row, sample_col][k]) for k in range(3))
            hex_code = rgb_to_hex(rgb)
            pending.append((component, hex_code))
        for comp, hex_code in pending:
            outline_candidates.difference_update(comp)
            add_pixels("FaceAccessory", set(comp), hex_code)

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
        pending_headwear: List[set[Tuple[int, int]]] = []
        headphone_components: List[Tuple[set[Tuple[int, int]], str]] = []
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
            accessory_components: List[Tuple[set[Tuple[int, int]], str]] = []
            primary_hex = res.color_hex
            primary_rgb = hex_to_rgb(primary_hex) if primary_hex else (0, 0, 0)
            primary_lum = relative_luminance(primary_hex) if primary_hex else 0.0
            for comp in components:
                rows = [row for row, _ in comp]
                min_row = min(rows)
                max_row = max(rows)
                lower_count = sum(1 for row in rows if row >= 11)
                comp_hex = component_dominant_hex(comp)
                headphone_clusters: List[set[Tuple[int, int]]] = []
                candidate_pixels: set[Tuple[int, int]] = {
                    (row, col)
                    for row, col in comp
                    if (col <= 6 or col >= 17)
                    and any(
                        (row + dr, col + dc) in skin_union
                        for dr in (-1, 0, 1)
                        for dc in (-1, 0, 1)
                    )
                }
                while candidate_pixels:
                    start = candidate_pixels.pop()
                    stack = [start]
                    cluster = {start}
                    while stack:
                        row, col = stack.pop()
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nbr = (row + dr, col + dc)
                            if nbr in candidate_pixels:
                                candidate_pixels.remove(nbr)
                                cluster.add(nbr)
                                stack.append(nbr)
                    cluster_rows = [row for row, _ in cluster]
                    cluster_cols = [col for _, col in cluster]
                    cluster_height = max(cluster_rows) - min(cluster_rows) + 1
                    cluster_width = max(cluster_cols) - min(cluster_cols) + 1
                    if (
                        len(cluster) >= 6
                        and cluster_width >= 2
                        and cluster_width <= 8
                        and cluster_height <= 8
                        and min(cluster_rows) >= 6
                        and max(cluster_rows) <= 18
                    ):
                        headphone_clusters.append(cluster)
                if headphone_clusters:
                    for cluster in headphone_clusters:
                        cluster_hex = component_dominant_hex(cluster)
                        headphone_components.append((cluster, cluster_hex))
                        comp.difference_update(cluster)
                    changed = True
                    if not comp:
                        continue
                rows = [row for row, _ in comp]
                min_row = min(rows)
                max_row = max(rows)
                cols = [col for _, col in comp]
                min_col = min(cols)
                max_col = max(cols)
                width = max_col - min_col + 1
                height = max_row - min_row + 1
                centre_col = sum(cols) / len(cols)
                if (
                    comp_hex
                    and primary_hex
                    and comp_hex.lower() != primary_hex.lower()
                    and len(comp) <= 80
                    and min_row <= 12
                ):
                    comp_rgb = hex_to_rgb(comp_hex)
                    dist = squared_distance(comp_rgb, primary_rgb)
                    lum_delta = abs(relative_luminance(comp_hex) - primary_lum)
                    if (
                        dist > 15000
                        or lum_delta > 85
                        or (
                            len(comp) <= 20
                            and lum_delta >= 25
                            and min_row <= 10
                        )
                    ):
                        accessory_components.append((comp, comp_hex))
                        changed = True
                        continue
                if (
                    comp_hex
                    and looks_like_headphones(comp)
                ):
                    headphone_components.append((comp, comp_hex))
                    changed = True
                    continue
                if (
                    lower_count >= 3
                    and lower_count / len(comp) >= 0.5
                    and max_row >= 11
                    and touches_skin(comp)
                    and width >= 3
                    and height <= 5
                    and 7.0 <= centre_col <= 17.0
                ):
                    facial_candidates.append(comp)
                elif looks_like_headwear_component(comp):
                    pending_headwear.append(comp)
                    changed = True
                else:
                    keep_components.append(comp)
            if headphone_components:
                for comp, comp_hex in headphone_components:
                    color_name = color_name_for_category(comp_hex, color_map, "FaceAccessory")
                    headphone_res = RegionResult(
                        sprite_id=sprite_id,
                        category="FaceAccessory",
                        variant_hint=f"FaceAccessory_Headphones_{color_name}",
                        color_hex=comp_hex,
                        color_name=color_name,
                        coverage_pct=round(len(comp) / total_pixels * 100.0, 2),
                        notes="headphones",
                        pixel_mask=mask_to_string(comp),
                    )
                    register_entry(headphone_res, set(comp))
                    changed = True
            if accessory_components:
                for comp, comp_hex in accessory_components:
                    if not comp_hex:
                        continue
                    color_name = color_name_for_category(comp_hex, color_map, "Hair")
                    accessory_res = RegionResult(
                        sprite_id=sprite_id,
                        category="Hair",
                        variant_hint=f"Hair_Accessory_{color_name}",
                        color_hex=comp_hex,
                        color_name=color_name,
                        coverage_pct=round(len(comp) / total_pixels * 100.0, 2),
                        notes="hair_accessory",
                        pixel_mask=mask_to_string(comp),
                    )
                    register_entry(accessory_res, set(comp))
                    changed = True
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
        if pending_headwear:
            for comp in pending_headwear:
                headwear_pixels |= comp
                comp_hex = component_dominant_hex(comp)
                add_pixels("Headwear", comp, comp_hex)
                if comp_hex:
                    headwear_color_set.add(comp_hex.lower())
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
                rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in mask)
                dominant_rgb = max(rgb_counts.items(), key=lambda kv: kv[1])[0]
                dominant_hex = rgb_to_hex(dominant_rgb)
                res.color_hex = dominant_hex
                res.color_name = color_name_for_category(dominant_hex, color_map, "Hair")
                res.variant_hint = f"Hair_{res.color_name}"
                hair_color_set.add(dominant_hex.lower())
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
    promote_glasses_from_outline()
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
            color_name = color_name_for_category(res.color_hex, color_map, context="glass")
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
            eye_color_name = color_name_for_category(res.color_hex, color_map, "Eyes")
            eye_result = RegionResult(
                sprite_id=res.sprite_id,
                category="Eyes",
                variant_hint=f"Eyes_{eye_color_name}",
                color_hex=res.color_hex,
                color_name=eye_color_name,
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

    def scrub_hair_leakage_into_base_face() -> None:
        if not hair_union:
            return
        for category in ("Base", "Face"):
            entries = list(category_to_entry.get(category, []))
            if not entries:
                continue
            refreshed: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
            for res, mask in entries:
                cleaned = mask - hair_union - headwear_processed_union
                if cleaned == mask:
                    refreshed.append((res, mask))
                    continue
                if not cleaned:
                    remove_entry(res)
                    continue
                update_entry_mask(res, cleaned)
                refreshed.append((res, cleaned))
            if refreshed:
                category_to_entry[category] = refreshed
            else:
                category_to_entry.pop(category, None)

    scrub_hair_leakage_into_base_face()

    merge_glasses_entries()
    merge_eye_variants()
    def scrub_eyes_from_hair_headwear() -> None:
        eye_entries_local = category_to_entry.get("Eyes", [])
        if not eye_entries_local:
            return
        eye_union_local: set[Tuple[int, int]] = set()
        for _, mask in eye_entries_local:
            eye_union_local |= mask
        for cat in ("Hair", "Headwear"):
            entries = category_to_entry.get(cat, [])
            if not entries:
                continue
            cleaned_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
            for res, mask in entries:
                cleaned_mask = mask - eye_union_local
                if cleaned_mask == mask:
                    cleaned_entries.append((res, mask))
                    continue
                if cleaned_mask:
                    update_entry_mask(res, cleaned_mask)
                    cleaned_entries.append((res, cleaned_mask))
                else:
                    remove_entry(res)
            category_to_entry[cat] = cleaned_entries

    scrub_eyes_from_hair_headwear()
    def expand_eyewear_masks() -> None:
        eyewear_entries = []
        for res, mask in category_to_entry.get("FaceAccessory", []):
            notes = res.notes or ""
            if "glasses_lens" in notes or res.variant_hint.startswith("FaceAccessory_Glasses_"):
                eyewear_entries.append((res, mask))
        if not eyewear_entries:
            return
        for res, mask in eyewear_entries:
            expanded = set(mask)
            queue = deque(mask)
            while queue:
                row, col = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = row + dr, col + dc
                    if not (0 <= nr < arr.shape[0] and 0 <= nc < arr.shape[1]):
                        continue
                    coord = (nr, nc)
                    if coord in expanded:
                        continue
                    if coord not in outline_candidates:
                        continue
                    if nr < 5 or nr > 18:
                        continue
                    rgb = tuple(int(arr[nr, nc][k]) for k in range(3))
                    hex_lower = rgb_to_hex(rgb).lower()
                    if hex_lower in {res.color_hex.lower(), "#000000"}:
                        outline_candidates.discard(coord)
                        expanded.add(coord)
                        queue.append(coord)
            if expanded != set(mask):
                update_entry_mask(res, expanded)

    expand_eyewear_masks()

    for res, mask in category_entries.get("Clothing", []):
        mask = mask - headwear_processed_union - outline_candidates
        if not mask:
            continue
        if is_mouth_candidate(mask):
            if res.color_hex.lower() in ACCESSORY_WHITE_HEXES:
                add_pixels("FaceAccessory", mask, res.color_hex)
                continue
            color_hex = res.color_hex
            color_name = color_name_for_category(color_hex, color_map, "Mouth")
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
            color_name = color_name_for_category(primary_hex, color_map, "Mouth")
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
            res.color_name = color_name_for_category(primary_hex, color_map, "Clothing")
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
            color_name = color_name_for_category(hex_code, color_map, "Clothing")
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

    def cleanup_clothing_hair_overlap() -> None:
        entries = list(category_to_entry.get("Clothing", []))
        if not entries:
            return
        for res, mask in entries:
            if not mask:
                continue
            components = connected_components_from_mask(mask)
            remaining = set(mask)
            for comp in components:
                if not comp:
                    continue
                rows = [row for row, _ in comp]
                min_row = min(rows)
                if min_row >= 18:
                    continue
                rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in comp)
                if not rgb_counts:
                    continue
                dominant_rgb = max(rgb_counts.items(), key=lambda kv: kv[1])[0]
                comp_hex = rgb_to_hex(dominant_rgb)
                if (
                    distance_to_hair_palette(comp_hex) <= 26.0
                    and (min_row <= 14 or touches_hair(comp))
                ):
                    add_pixels("Hair", set(comp), comp_hex)
                    clothing_union.difference_update(comp)
                    remaining -= comp
            if remaining != set(mask):
                if remaining:
                    update_entry_mask(res, remaining)
                else:
                    remove_entry(res)

    cleanup_clothing_hair_overlap()

    def extract_neck_jewelry() -> None:
        clothing_entries = list(category_to_entry.get("Clothing", []))
        if not clothing_entries:
            return
        for res, mask in clothing_entries:
            potential_chain: set[Tuple[int, int]] = set()
            for row, col in mask:
                if row < 14 or row > 20:
                    continue
                rgb = tuple(int(arr[row, col][k]) for k in range(3))
                luminance = relative_luminance(rgb_to_hex(rgb))
                if luminance < 140:
                    continue
                r, g, b = rgb
                if r >= g + 5 and r >= b + 10:
                    potential_chain.add((row, col))
            if not potential_chain:
                continue
            components = connected_components_from_mask(potential_chain)
            found_chain = False
            remaining = set(mask)
            for comp in components:
                if len(comp) < 4:
                    continue
                rows = [row for row, _ in comp]
                cols = [col for _, col in comp]
                min_row, max_row = min(rows), max(rows)
                min_col, max_col = min(cols), max(cols)
                height = max_row - min_row + 1
                width = max_col - min_col + 1
                if len(comp) <= 40:
                    if width >= 3 or height >= 4:
                        pass
                    else:
                        continue
                    found_chain = True
                    remaining -= comp
                    rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in comp)
                    dominant_rgb = max(rgb_counts.items(), key=lambda kv: kv[1])[0]
                    hex_code = rgb_to_hex(dominant_rgb)
                    color_name = color_name_for_category(hex_code, color_map, "Jewelry")
                    jewelry_entry = RegionResult(
                        sprite_id=sprite_id,
                        category="Jewelry",
                        variant_hint=f"Jewelry_Neck_{color_name}",
                        color_hex=hex_code,
                        color_name=color_name,
                        coverage_pct=round(len(comp) / total_pixels * 100.0, 2),
                        notes="auto_chain_detect",
                        pixel_mask=mask_to_string(comp),
                    )
                    register_entry(jewelry_entry, set(comp))
            if found_chain:
                if remaining:
                    update_entry_mask(res, remaining)
                else:
                    remove_entry(res)

    extract_neck_jewelry()

    merge_facial_hair_variants()
    def scrub_mouth_from_facial_hair() -> None:
        if not mouth_union:
            return
        entries = list(category_to_entry.get("FacialHair", []))
        if not entries:
            return
        for res, mask in entries:
            cleaned_mask = mask - mouth_union
            if cleaned_mask != mask:
                if cleaned_mask:
                    update_entry_mask(res, cleaned_mask)
                else:
                    remove_entry(res)

    scrub_mouth_from_facial_hair()

    # Palette entries remain unchanged.
    for res, mask in category_entries.get("Palette", []):
        processed_entries.append((res, mask))
        category_to_entry[res.category].append((res, mask))

    for res, mask in category_entries.get("PaletteFull", []):
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
            rows_local = [row for row, _ in coords]
            min_row = min(rows_local)
            max_row = max(rows_local)
            if (
                (touches_hair(coords) or hex_code.lower() in hair_color_set or looks_like_hair(coords))
                and max_row <= 14
                and min_row <= 10
            ):
                add_pixels("Hair", coords, hex_code)
                continue
            if is_mouth_candidate(coords):
                color_name = color_name_for_category(hex_code, color_map, "Mouth")
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
    hair_like_pixels: set[Tuple[int, int]] = set()
    for res in refined:
        if res.category in {"Hair", "FacialHair"}:
            hair_like_pixels |= parse_pixel_mask(res.pixel_mask)
    outline_set -= hair_like_pixels
    face_accessory_pixels: set[Tuple[int, int]] = set()
    for res in refined:
        if res.category in {"FaceAccessory", "Eyewear"} or (
            res.category == "Face" and res.variant_hint.startswith("Face_Eyes")
        ):
            face_accessory_pixels |= parse_pixel_mask(res.pixel_mask)
    outline_set -= face_accessory_pixels
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

    def apply_taxonomy_labels(results: List[RegionResult]) -> None:
        for res in results:
            orig_category = res.category
            color_hex = res.color_hex
            if orig_category == "Skin":
                color_name = color_name_for_category(color_hex, color_map, "Skin")
                res.category = "Base"
                res.color_name = color_name
                res.variant_hint = f"Base_Skin_{color_name}"
            elif orig_category == "Outline":
                color_name = color_name_for_category(color_hex, color_map, "Outline")
                res.category = "Base"
                res.color_name = color_name
                res.variant_hint = f"Base_Outline_{color_name}"
            elif orig_category == "Hair":
                color_name = color_name_for_category(color_hex, color_map, "Hair")
                res.category = "Hair"
                res.color_name = color_name
                if res.variant_hint.startswith("Hair_Accessory_"):
                    res.variant_hint = f"Hair_Accessory_{color_name}"
                else:
                    res.variant_hint = f"Hair_Main_{color_name}"
            elif orig_category == "FacialHair":
                color_name = color_name_for_category(color_hex, color_map, "FacialHair")
                res.category = "FacialHair"
                res.color_name = color_name
                if "Beard" in res.variant_hint or "Stubble" in res.variant_hint:
                    res.variant_hint = f"FacialHair_{res.variant_hint.split('_', 1)[1]}"
                else:
                    res.variant_hint = f"FacialHair_Main_{color_name}"
            elif orig_category == "Eyes":
                color_name = color_name_for_category(color_hex, color_map, "Eyes")
                res.category = "Face"
                res.color_name = color_name
                res.variant_hint = f"Face_Eyes_{color_name}"
            elif orig_category == "Mouth":
                color_name = color_name_for_category(color_hex, color_map, "Mouth")
                res.category = "Face"
                res.color_name = color_name
                res.variant_hint = f"Face_Mouth_{color_name}"
            elif orig_category == "FaceAccessory":
                if res.variant_hint.startswith("FaceAccessory_Glasses_"):
                    color_name = color_name_for_category(color_hex, color_map, "Eyewear")
                    res.category = "Eyewear"
                    res.color_name = color_name
                    res.variant_hint = f"Eyewear_{color_name}"
                elif res.variant_hint.startswith("FaceAccessory_Headphones_"):
                    color_name = color_name_for_category(color_hex, color_map, "FaceAccessory")
                    res.category = "FaceAccessory"
                    res.color_name = color_name
                    res.variant_hint = f"FaceAccessory_Headphones_{color_name}"
                elif res.variant_hint.startswith("FaceAccessory_Earpiece_"):
                    color_name = color_name_for_category(color_hex, color_map, "FaceAccessory")
                    res.category = "FaceAccessory"
                    res.color_name = color_name
                    res.variant_hint = f"{res.variant_hint}_{color_name}"
                elif res.variant_hint.startswith("FaceAccessory_Cigarette"):
                    color_name = color_name_for_category(color_hex, color_map, "FaceAccessory")
                    res.category = "Face"
                    res.color_name = color_name
                    res.variant_hint = f"Face_MouthAccessory_Cigarette_{color_name}"
                elif res.variant_hint.startswith("FaceAccessory_CigaretteHolder"):
                    color_name = color_name_for_category(color_hex, color_map, "FaceAccessory")
                    res.category = "Face"
                    res.color_name = color_name
                    res.variant_hint = f"Face_MouthAccessory_Holder_{color_name}"
                elif res.variant_hint.startswith("FaceAccessory_Joint"):
                    color_name = color_name_for_category(color_hex, color_map, "FaceAccessory")
                    res.category = "Face"
                    res.color_name = color_name
                    res.variant_hint = f"Face_MouthAccessory_Joint_{color_name}"
                else:
                    color_name = color_name_for_category(color_hex, color_map, "FaceAccessory")
                    res.color_name = color_name
                    res.variant_hint = f"FaceAccessory_{color_name}"
            elif orig_category == "Headwear":
                color_name = color_name_for_category(color_hex, color_map, "Headwear")
                res.category = "Headwear"
                res.color_name = color_name
                shape_token = extract_note_value(res, "headwear_shape")
                if shape_token:
                    res.variant_hint = f"Headwear_{shape_token}_{color_name}"
                elif "_Cap_" in res.variant_hint:
                    res.variant_hint = f"Headwear_Cap_{color_name}"
                else:
                    res.variant_hint = f"Headwear_{color_name}"
            elif orig_category == "Clothing":
                color_name = color_name_for_category(color_hex, color_map, "Clothing")
                res.category = "Clothing"
                res.color_name = color_name
                garment_token = extract_note_value(res, "garment_type")
                garment_label = garment_token if garment_token else "Top"
                garment_label = garment_label.replace(" ", "")
                res.variant_hint = f"Clothing_{garment_label}_{color_name}"
                extra_token = extract_note_value(res, "garment_extra")
                if extra_token:
                    res.variant_hint = f"{res.variant_hint}_{extra_token.replace(' ', '')}"
            elif orig_category == "NeckAccessory":
                color_name = color_name_for_category(color_hex, color_map, "Jewelry")
                res.category = "Jewelry"
                res.color_name = color_name
                res.variant_hint = f"Jewelry_Neck_{color_name}"
            elif orig_category == "Jewelry":
                color_name = color_name_for_category(color_hex, color_map, "Jewelry")
                res.category = "Jewelry"
                res.color_name = color_name
                if res.variant_hint.startswith("Jewelry_Earring"):
                    res.variant_hint = f"{res.variant_hint}_{color_name}"
                elif res.variant_hint.startswith("Jewelry_Neck_"):
                    res.variant_hint = f"Jewelry_Neck_{color_name}"
                else:
                    res.variant_hint = f"Jewelry_{color_name}"
            elif orig_category == "Background":
                color_name = color_name_for_category(color_hex, color_map, "Background")
                res.color_name = color_name
                if not res.variant_hint.startswith("Background_"):
                    res.variant_hint = f"Background_{color_name}"
            elif orig_category == "Palette":
                color_name = color_name_for_category(color_hex, color_map, "Palette")
                res.color_name = color_name
                if not res.variant_hint.startswith("Palette_"):
                    res.variant_hint = f"Palette_{color_name}"
            elif orig_category == "PaletteFull":
                color_name = color_name_for_category(color_hex, color_map, "Palette")
                res.color_name = color_name
                res.variant_hint = f"PaletteFull_{color_name}"
            elif orig_category == "Unassigned":
                color_name = color_name_for_category(color_hex, color_map, "Unassigned")
                res.color_name = color_name
                res.variant_hint = f"Unassigned_{color_name}"

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

    def refine_micro_accessories(results: List[RegionResult]) -> None:
        eye_entries_local = category_to_entry.get("Eyes", [])
        eye_color_set_local = {
            res.color_hex.lower()
            for res, _ in eye_entries_local
            if res.color_hex
        }
        eye_masks_local = [
            parse_pixel_mask(res.pixel_mask) for res, _ in eye_entries_local
        ]
        for res in results:
            mask_set = parse_pixel_mask(res.pixel_mask)
            if not mask_set:
                continue
            if res.category in {"FaceAccessory", "Jewelry", "Clothing", "Headwear"}:
                if mask_within(mask_set, 7, 16, 0, 8, tolerance=1) or mask_within(mask_set, 7, 16, 16, 24, tolerance=1):
                    ear_info = classify_ear_accessory(
                        mask_set,
                        res.color_hex,
                        skin_color_set,
                        hair_color_set,
                    )
                    if ear_info:
                        variant, side = ear_info
                        if variant == "Airpod":
                            res.category = "FaceAccessory"
                            res.variant_hint = f"FaceAccessory_Earpiece_{side}"
                        else:
                            res.category = "Jewelry"
                            res.variant_hint = f"Jewelry_Earring{variant}_{side}"
                        append_note(res, "micro_detect", f"{variant.lower()}_{side.lower()}")
                        continue
            if res.category in {"FaceAccessory", "Clothing"}:
                if mask_within(mask_set, 11, 17, 6, 18, tolerance=1):
                    mouth_variant = classify_mouth_accessory(mask_set, res.color_hex, arr)
                    if mouth_variant:
                        lower = res.color_hex.lower() if res.color_hex else ""
                        if lower in eye_color_set_local:
                            continue
                        if eye_masks_local:
                            overlap_ratio = max(
                                len(mask_set & eye_mask) / max(len(mask_set), 1)
                                for eye_mask in eye_masks_local
                            )
                            if overlap_ratio >= 0.5:
                                continue
                        res.category = "FaceAccessory"
                        res.variant_hint = f"FaceAccessory_{mouth_variant}"
                        append_note(res, "micro_detect", mouth_variant.lower())

    refine_micro_accessories(refined)
    def annotate_headwear_shapes() -> None:
        entries = category_to_entry.get("Headwear", [])
        if not entries:
            return
        for res, mask in entries:
            shape = classify_headwear_shape(mask)
            if not shape:
                continue
            shape_token = shape.replace(" ", "_")
            append_note(res, "headwear_shape", shape_token)

    annotate_headwear_shapes()
    def extract_headphones_from_hair() -> None:
        hair_entries_snapshot = list(category_to_entry.get("Hair", []))
        if not hair_entries_snapshot:
            return
        for res, mask in hair_entries_snapshot:
            if not mask:
                continue
            components = connected_components_from_mask(mask)
            left_candidates: List[set[Tuple[int, int]]] = []
            right_candidates: List[set[Tuple[int, int]]] = []
            band_candidates: List[set[Tuple[int, int]]] = []
            for comp in components:
                rows = [row for row, _ in comp]
                cols = [col for _, col in comp]
                min_row, max_row = min(rows), max(rows)
                min_col, max_col = min(cols), max(cols)
                height = max_row - min_row + 1
                width = max_col - min_col + 1
                if 3 <= width <= 5 and 3 <= height <= 9 and 6 <= min_row <= 16 and max_row <= 18:
                    if min_col <= 3 and touches_skin(comp):
                        left_candidates.append(comp)
                    elif max_col >= 20 and touches_skin(comp):
                        right_candidates.append(comp)
                    continue
                if (
                    width >= 6
                    and height <= 3
                    and min_row <= 9
                    and max_row <= 12
                    and min_col >= 5
                    and max_col <= 18
                ):
                    band_candidates.append(comp)
            if not left_candidates or not right_candidates:
                continue
            left_comp = max(left_candidates, key=len)
            right_comp = max(right_candidates, key=len)
            headphone_mask = set(left_comp) | set(right_comp)
            if band_candidates:
                band_comp = max(band_candidates, key=len)
                headphone_mask |= band_comp
            remaining_mask = set(mask) - headphone_mask
            hair_union.difference_update(headphone_mask)
            if remaining_mask:
                update_entry_mask(res, remaining_mask)
            else:
                remove_entry(res)
            color_name = color_name_for_category(res.color_hex, color_map, "FaceAccessory")
            headphone_res = RegionResult(
                sprite_id=sprite_id,
                category="FaceAccessory",
                variant_hint=f"FaceAccessory_Headphones_{color_name}",
                color_hex=res.color_hex,
                color_name=color_name,
                coverage_pct=round(len(headphone_mask) / total_pixels * 100.0, 2),
                notes="headphones",
            )
            headphone_res.pixel_mask = mask_to_string(headphone_mask)
            register_entry(headphone_res, headphone_mask)
            refined.append(headphone_res)

    extract_headphones_from_hair()
    def classify_clothing_garment(mask: set[Tuple[int, int]]) -> Tuple[str | None, List[str]]:
        if not mask:
            return (None, [])
        rows = [row for row, _ in mask]
        cols = [col for _, col in mask]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        height = max_row - min_row + 1
        width = max_col - min_col + 1
        hood_edge_pixels = sum(
            1 for row, col in mask if row <= min_row + 3 and (col <= 4 or col >= 19)
        )
        hood_ratio = hood_edge_pixels / len(mask)
        bottom_pixels = sum(1 for row, _ in mask if row >= max_row - 2)
        collar_pixels = sum(1 for row, _ in mask if row <= min_row + 1)
        components = connected_components_from_mask(mask)
        centre_col = (min_col + max_col) / 2.0
        extras: List[str] = []
        for comp in components:
            comp_rows = [row for row, _ in comp]
            comp_cols = [col for _, col in comp]
            comp_min_row, comp_max_row = min(comp_rows), max(comp_rows)
            comp_min_col, comp_max_col = min(comp_cols), max(comp_cols)
            comp_height = comp_max_row - comp_min_row + 1
            comp_width = comp_max_col - comp_min_col + 1
            if (
                comp_width <= 2
                and comp_height >= 4
                and abs(((comp_min_col + comp_max_col) / 2.0) - centre_col) <= 1.5
                and comp_min_row <= min_row + 6
            ):
                extras.append("Tie")
                break
        garment = "Top"
        if hood_ratio >= 0.08 and width >= 10:
            garment = "Hoodie"
        elif height >= 12 and bottom_pixels >= 8:
            garment = "Coat"
        elif width >= 10 and height >= 6:
            garment = "Jacket"
        elif width <= 8 and height >= 10:
            garment = "DressTop"
        elif collar_pixels >= max(6, int(len(mask) * 0.2)) and height <= 5 and width <= 8:
            garment = "Turtleneck"
        elif height <= 5 and width >= 8:
            garment = "SuitTop"
        elif bottom_pixels >= 6 and width >= 9:
            garment = "Jacket"
        if "Tie" in extras and garment in {"Top", "SuitTop"}:
            garment = "SuitTop"
        return (garment, extras)

    def annotate_clothing_garments() -> None:
        entries = category_to_entry.get("Clothing", [])
        if not entries:
            return
        combined_mask: set[Tuple[int, int]] = set()
        for _, mask in entries:
            combined_mask |= mask
        garment, extras = classify_clothing_garment(combined_mask)
        for res, _ in entries:
            if garment:
                append_note(res, "garment_type", garment.replace(" ", ""))
            for extra in extras:
                append_note(res, "garment_extra", extra.replace(" ", ""))

    annotate_clothing_garments()

    def merge_headwear_components() -> None:
        entries = category_to_entry.get("Headwear", [])
        if not entries:
            return
        primary_res, primary_mask = max(entries, key=lambda item: len(item[1]))
        combined_mask: set[Tuple[int, int]] = set(primary_mask)
        accent_names: List[str] = []
        for res, mask in entries:
            if res is primary_res:
                continue
            combined_mask |= mask
            accent_names.append(color_name_for_category(res.color_hex, color_map, "Headwear"))
            remove_entry(res)
        if accent_names:
            existing = extract_note_value(primary_res, "headwear_accents")
            values = set(accent_names)
            if existing:
                values.update(value.strip() for value in existing.split(","))
            replace_note(primary_res, "headwear_accents", ",".join(sorted(values)))
        update_entry_mask(primary_res, combined_mask)
        category_to_entry["Headwear"] = [(primary_res, combined_mask)]

    merge_headwear_components()
    def scrub_headwear_from_hair() -> None:
        headwear_union_local: set[Tuple[int, int]] = set()
        for res, mask in category_to_entry.get("Headwear", []):
            headwear_union_local |= mask
        if not headwear_union_local:
            return
        hair_entries_local = category_to_entry.get("Hair", [])
        if not hair_entries_local:
            return
        cleaned: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for res, mask in hair_entries_local:
            cleaned_mask = mask - headwear_union_local
            if cleaned_mask != mask:
                if cleaned_mask:
                    update_entry_mask(res, cleaned_mask)
                    cleaned.append((res, cleaned_mask))
                else:
                    remove_entry(res)
            else:
                cleaned.append((res, mask))
        category_to_entry["Hair"] = cleaned

    scrub_headwear_from_hair()

    def merge_clothing_components() -> None:
        entries = category_to_entry.get("Clothing", [])
        if not entries:
            return
        grouped: Dict[str, List[Tuple[int, RegionResult, set[Tuple[int, int]]]]] = defaultdict(list)
        for idx, (res, mask) in enumerate(entries):
            garment = extract_note_value(res, "garment_type") or "Top"
            grouped[garment].append((idx, res, mask))
        merged_entries: List[Tuple[RegionResult, set[Tuple[int, int]]]] = []
        for garment, comps in grouped.items():
            combined_mask: set[Tuple[int, int]] = set()
            for _, _, mask in comps:
                combined_mask |= mask
            if not combined_mask:
                continue
            primary_idx, primary_res, _ = max(comps, key=lambda item: len(item[2]))
            rgb_counts = Counter(tuple(int(arr[row, col][k]) for k in range(3)) for row, col in combined_mask)
            if rgb_counts:
                dominant_rgb, _ = max(rgb_counts.items(), key=lambda item: item[1])
                dominant_hex = rgb_to_hex(dominant_rgb)
                primary_res.color_hex = dominant_hex
                primary_res.color_name = color_name_for_category(dominant_hex, color_map, "Clothing")
            garment_token = garment.replace(" ", "")
            append_note(primary_res, "garment_type", garment_token)
            accent_names: List[str] = []
            for idx, res, mask in comps:
                if idx == primary_idx:
                    continue
                accent_names.append(color_name_for_category(res.color_hex, color_map, "Clothing"))
            if accent_names:
                append_note(primary_res, "clothing_accents", ",".join(sorted(set(accent_names))))
            update_entry_mask(primary_res, combined_mask)
            merged_entries.append((primary_res, combined_mask))
            for idx, res, _ in comps:
                if idx == primary_idx:
                    continue
                remove_entry(res)
        category_to_entry["Clothing"] = merged_entries

    merge_clothing_components()

    def prune_false_eyewear(results: List[RegionResult]) -> None:
        total_pixels = 24 * 24
        eye_map: Dict[str, RegionResult] = {}
        for res in results:
            if (
                res.category == "Face"
                and res.variant_hint.startswith("Face_Eyes")
                and res.color_hex
            ):
                eye_map.setdefault(res.color_hex.lower(), res)
        filtered: List[RegionResult] = []
        for res in results:
            if res.category == "Eyewear":
                notes = res.notes or ""
                has_reflection = "glasses_reflection" in notes or "glasses_tint" in notes
                if not has_reflection and res.color_hex:
                    key = res.color_hex.lower()
                    eye_res = eye_map.get(key)
                    if eye_res:
                        eye_mask = parse_pixel_mask(eye_res.pixel_mask)
                        eyewear_mask = parse_pixel_mask(res.pixel_mask)
                        combined = eye_mask | eyewear_mask
                        eye_res.pixel_mask = mask_to_string(combined)
                        eye_res.coverage_pct = round(len(combined) / total_pixels * 100.0, 2)
                        continue
            filtered.append(res)
        results[:] = filtered

    # Keep ordering similar to original: Background, Outline, Skin, Hair, Headwear...
    order_priority = {
        "Background": 0,
        "Base": 1,
        "Face": 2,
        "Hair": 3,
        "FacialHair": 4,
        "Headwear": 5,
        "Eyewear": 6,
        "FaceAccessory": 7,
        "Jewelry": 8,
        "Clothing": 9,
        "NeckAccessory": 10,
        "Palette": 200,
        "PaletteFull": 201,
        "Unassigned": 300,
    }

    collapse_logical_layers(refined)
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
        preferred_categories = (
            "Headwear",
            "Hair",
            "FacialHair",
            "Clothing",
            "Face",
            "Base",
            "Background",
        )
        for hex_code, coords in missing_hex_map.items():
            lower_hex = hex_code.lower()
            coord_set = set(coords)
            assigned = False
            for category in preferred_categories:
                for res in refined:
                    if res.category == category and res.color_hex.lower() == lower_hex:
                        existing_mask = parse_pixel_mask(res.pixel_mask)
                        updated_mask = existing_mask | coord_set
                        res.pixel_mask = mask_to_string(updated_mask)
                        res.coverage_pct = round(len(updated_mask) / total_pixels * 100.0, 2)
                        assigned = True
                        break
                if assigned:
                    break
            if assigned:
                continue
            context_map = {
                "Headwear": "Headwear",
                "Hair": "Hair",
                "FacialHair": "FacialHair",
                "Clothing": "Clothing",
                "Face": "Eyes",
                "Base": "Skin",
                "Background": "Background",
            }
            for category in preferred_categories:
                candidates = [res for res in refined if res.category == category]
                if not candidates:
                    continue
                template = max(
                    candidates,
                    key=lambda res: len(parse_pixel_mask(res.pixel_mask)),
                )
                template_tokens = template.variant_hint.split("_")
                if len(template_tokens) >= 2:
                    base_hint = "_".join(template_tokens[:2])
                else:
                    base_hint = template.variant_hint
                context = context_map.get(category, category)
                color_name = color_name_for_category(hex_code, color_map, context)
                new_variant = f"{base_hint}_{color_name}"
                new_entry = RegionResult(
                    sprite_id=sprite_id,
                    category=category,
                    variant_hint=new_variant,
                    color_hex=hex_code,
                    color_name=color_name,
                    coverage_pct=round(len(coord_set) / total_pixels * 100.0, 2),
                    notes="auto_backfill",
                    pixel_mask=mask_to_string(coord_set),
                )
                refined.append(new_entry)
                assigned = True
                break
            if assigned:
                continue
            color_name = color_name_for_category(hex_code, color_map, "Unassigned")
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

    ensure_palette_full_entries(refined, arr, color_map)
    apply_taxonomy_labels(refined)
    collapse_logical_layers(refined)
    if not allow_facial_hair:
        for res in refined:
            if res.category == "FacialHair":
                res.category = "Hair"
                res.color_name = color_name_for_category(res.color_hex, color_map, "Hair")
                res.variant_hint = f"Hair_Main_{res.color_name}"
    prune_false_eyewear(refined)
    refined.sort(key=lambda res: (order_priority.get(res.category, 99), res.variant_hint))
    return refined


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)
    color_map = load_custom_color_map(args.color_map)

    if args.resume and not args.cache_dir:
        LOGGER.error("--resume requires --cache-dir to be specified.")
        return 1

    cache_dir: Path | None = args.cache_dir
    if cache_dir:
        ensure_directory(cache_dir)
        LOGGER.info("Caching per-sprite results in %s (resume=%s)", cache_dir, args.resume)

    if args.json_output:
        ensure_directory(args.json_output.parent)

    if not args.src.exists():
        LOGGER.error("Source directory does not exist: %s", args.src)
        return 1

    if args.src.is_file():
        files = [args.src]
    else:
        files = sorted(args.src.rglob("*.png"))
    if not files:
        LOGGER.error("No PNG files found in %s", args.src)
        return 1

    total = len(files)
    LOGGER.info("Analysing %d sprite%s…", total, "" if total == 1 else "s")
    all_results: List[RegionResult] = []
    failures: List[str] = []
    progress_interval = max(1, total // 50)  # log at ~50 checkpoints
    for index, path in enumerate(files, start=1):
        sprite_id = path.stem
        cache_file: Path | None = cache_dir / f"{sprite_id}.json" if cache_dir else None
        sprite_results: List[RegionResult] = []
        try:
            if cache_file and cache_file.exists() and args.resume:
                LOGGER.debug("Loading cached results for %s", sprite_id)
                sprite_results = load_cached_results(cache_file)
            else:
                sprite_results = analyze_sprite(path, color_map, args.top_colors)
                if cache_file:
                    write_cache_file(cache_file, sprite_results)
        except Exception:
            failures.append(sprite_id)
            LOGGER.exception("Failed to analyse %s", sprite_id)
            continue
        if index == 1 or index == total or index % progress_interval == 0:
            LOGGER.info("Processed %4d / %d (%s)", index, total, sprite_id)
        all_results.extend(sprite_results)

    write_csv(args.output, all_results)
    LOGGER.info("Wrote %s with %d records.", args.output, len(all_results))
    if args.json_output:
        write_json_output(args.json_output, all_results)
        LOGGER.info("Wrote %s with %d records.", args.json_output, len(all_results))
    if failures:
        LOGGER.warning("Completed with %d failures: %s", len(failures), ", ".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

