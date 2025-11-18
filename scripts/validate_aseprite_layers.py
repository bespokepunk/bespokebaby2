#!/usr/bin/env python3
"""
Validate that Aseprite layer names follow the agreed BespokeBaby2 taxonomy.

The script shells out to the Aseprite CLI (`aseprite --batch <file> --list-layers`)
to obtain layer names, then checks each one against the allowed naming patterns
documented in `docs/layering_guidelines.md`.

Usage:
    python scripts/validate_aseprite_layers.py                 # scan default dirs
    python scripts/validate_aseprite_layers.py path/to/file.aseprite
    python scripts/validate_aseprite_layers.py Aseprite --aseprite /path/to/aseprite

Set the `ASEPRITE_PATH` environment variable if the binary is not on PATH.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
import io
import struct
import shutil

LAYER_PATTERNS: Sequence[Tuple[str, re.Pattern[str]]] = [
    ("00_Ref", re.compile(r"^00_Ref(_[A-Za-z0-9]+)*$")),
    ("01_Background", re.compile(r"^01_Background(_[A-Za-z0-9]+)*$")),
    ("02_BackAccessory", re.compile(r"^02_BackAccessory(_[A-Za-z0-9]+)*$")),
    ("03_Outline", re.compile(r"^03_Outline(_[A-Za-z0-9]+)*$")),
    ("04_Base_Skin", re.compile(r"^04_Base_Skin(_[A-Za-z0-9]+)*$")),
    ("05_Base_Shadows", re.compile(r"^05_Base_Shadows(_[A-Za-z0-9]+)*$")),
    ("06_Hair_Main", re.compile(r"^06_Hair_Main(_[A-Za-z0-9]+)*$")),
    ("07_Hair_Accessory", re.compile(r"^07_Hair_Accessory(_[A-Za-z0-9]+)*$")),
    ("07_Hair_Facial", re.compile(r"^07_Hair_Facial(_[A-Za-z0-9]+)*$")),
    ("08_Headwear", re.compile(r"^08_Headwear(_[A-Za-z0-9]+)*$")),
    ("09_Headwear_Accent", re.compile(r"^09_Headwear_Accent(_[A-Za-z0-9]+)*$")),
    ("10_Face_Eyes", re.compile(r"^10_Face_Eyes(_[A-Za-z0-9]+)*$")),
    ("11_Face_EyeMakeup", re.compile(r"^11_Face_EyeMakeup(_[A-Za-z0-9]+)*$")),
    ("12_Face_Eyes_Laser", re.compile(r"^12_Face_Eyes_Laser(_[A-Za-z0-9]+)*$")),
    ("13_Face_Mouth", re.compile(r"^13_Face_Mouth(_[A-Za-z0-9]+)*$")),
    ("14_Face_Marks", re.compile(r"^14_Face_Marks(_[A-Za-z0-9]+)*$")),
    ("15_Eyewear", re.compile(r"^15_Eyewear(_[A-Za-z0-9]+)*$")),
    ("16_FaceAccessory", re.compile(r"^16_FaceAccessory(_[A-Za-z0-9]+)*$")),
    ("17_Face_Implant_Brow", re.compile(r"^17_Face_Implant_Brow(_[A-Za-z0-9]+)*$")),
    ("18_Face_Implant_Cheek", re.compile(r"^18_Face_Implant_Cheek(_[A-Za-z0-9]+)*$")),
    ("19_CL_Mid_Sweater", re.compile(r"^19_CL_Mid_Sweater(_[A-Za-z0-9]+)*$")),
    ("20_CL_Outer_Blazer", re.compile(r"^20_CL_Outer_Blazer(_[A-Za-z0-9]+)*$")),
    ("21_CL_Outer_Coat", re.compile(r"^21_CL_Outer_Coat(_[A-Za-z0-9]+)*$")),
    ("22_CL_Scarf_Hood", re.compile(r"^22_CL_Scarf_Hood(_[A-Za-z0-9]+)*$")),
    ("23_CL_Tie", re.compile(r"^23_CL_Tie(_[A-Za-z0-9]+)*$")),
    ("24_CL_PocketAccessory", re.compile(r"^24_CL_PocketAccessory(_[A-Za-z0-9]+)*$")),
    ("25_CL_Bottoms", re.compile(r"^25_CL_Bottoms(_[A-Za-z0-9]+)*$")),
    ("26_CL_SleeveAccent", re.compile(r"^26_CL_SleeveAccent(_[A-Za-z0-9]+)*$")),
    ("29_Jewelry_Earring", re.compile(r"^29_Jewelry_Earring(_[A-Za-z0-9]+)*$")),
    ("29_Jewelry_Necklace", re.compile(r"^29_Jewelry_Necklace(_[A-Za-z0-9]+)*$")),
    ("30_Prop_Front", re.compile(r"^30_Prop_Front(_[A-Za-z0-9]+)*$")),
    ("31_Prop_Back", re.compile(r"^31_Prop_Back(_[A-Za-z0-9]+)*$")),
    ("32_Smoke_Joint", re.compile(r"^32_Smoke_Joint(_[A-Za-z0-9]+)*$")),
    ("33_Smoke_Cigarette", re.compile(r"^33_Smoke_Cigarette(_[A-Za-z0-9]+)*$")),
    ("34_Smoke_Cigar", re.compile(r"^34_Smoke_Cigar(_[A-Za-z0-9]+)*$")),
    ("35_Smoke_Holder", re.compile(r"^35_Smoke_Holder(_[A-Za-z0-9]+)*$")),
]

LAYER_REGEXES = [pattern for _, pattern in LAYER_PATTERNS]
LAYER_NAME_RE = re.compile(r'"([^"]+)"')


def collect_targets(paths: Sequence[Path]) -> List[Path]:
    files: List[Path] = []
    for target in paths:
        if target.is_dir():
            files.extend(sorted(target.rglob("*.aseprite")))
        elif target.is_file() and target.suffix.lower() == ".aseprite":
            files.append(target)
        else:
            print(f"[WARN] Skipping {target}: not an .aseprite file or directory", file=sys.stderr)
    return files


def parse_layers(aseprite_output: str) -> List[str]:
    layers: List[str] = []
    for raw_line in aseprite_output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = LAYER_NAME_RE.search(line)
        if match:
            name = match.group(1)
        else:
            # Accept formats like "Layer: name" or "* name"
            if ":" in line:
                name = line.split(":", 1)[1].strip()
            else:
                name = line.lstrip("* ").strip()
        if name:
            layers.append(name)
    return layers


def run_aseprite_list_layers(aseprite_cmd: str, file_path: Path) -> List[str]:
    cmd = [aseprite_cmd, "--batch", str(file_path), "--list-layers"]
    try:
        completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Aseprite CLI not found ({aseprite_cmd!r}). "
            "Install Aseprite and/or set ASEPRITE_PATH or --aseprite."
        ) from exc
    if completed.returncode != 0:
        raise RuntimeError(
            f"Aseprite returned {completed.returncode} for {file_path}:\n{completed.stderr.strip()}"
        )
    return parse_layers(completed.stdout)


def read_word(stream: io.BufferedReader) -> int:
    data = stream.read(2)
    if len(data) != 2:
        raise EOFError("Unexpected end of file while reading WORD")
    return struct.unpack("<H", data)[0]


def read_short(stream: io.BufferedReader) -> int:
    data = stream.read(2)
    if len(data) != 2:
        raise EOFError("Unexpected end of file while reading SHORT")
    return struct.unpack("<h", data)[0]


def read_dword(stream: io.BufferedReader) -> int:
    data = stream.read(4)
    if len(data) != 4:
        raise EOFError("Unexpected end of file while reading DWORD")
    return struct.unpack("<I", data)[0]


def read_byte(stream: io.BufferedReader) -> int:
    data = stream.read(1)
    if len(data) != 1:
        raise EOFError("Unexpected end of file while reading BYTE")
    return data[0]


def read_ase_string(stream: io.BufferedReader) -> str:
    length = read_word(stream)
    raw = stream.read(length)
    if len(raw) != length:
        raise EOFError("Unexpected end of file while reading string")
    return raw.decode("utf-8", errors="replace").rstrip("\x00")


def parse_layers_from_file(file_path: Path) -> List[str]:
    with open(file_path, "rb") as fh:
        data = fh.read()
    stream = io.BytesIO(data)

    header = stream.read(128)
    if len(header) != 128:
        raise RuntimeError(f"{file_path}: invalid ASE header")
    frame_count = struct.unpack_from("<H", header, 6)[0]

    layers: List[str] = []
    for _frame_idx in range(frame_count):
        frame_start = stream.tell()
        frame_bytes = read_dword(stream)
        frame_magic = read_word(stream)
        if frame_magic != 0xF1FA:
            raise RuntimeError(f"{file_path}: invalid frame magic {frame_magic:#x}")
        old_chunk_count = read_word(stream)
        _frame_duration = read_word(stream)
        stream.read(2)  # reserved
        new_chunk_count = read_dword(stream)
        chunk_count = new_chunk_count if new_chunk_count != 0 else old_chunk_count

        for _ in range(chunk_count):
            chunk_size = read_dword(stream)
            chunk_type = read_word(stream)
            chunk_data = stream.read(chunk_size - 6)
            if len(chunk_data) != chunk_size - 6:
                raise RuntimeError(f"{file_path}: truncated chunk data")

            if chunk_type == 0x2004:  # Layer chunk
                chunk_stream = io.BytesIO(chunk_data)
                _flags = read_word(chunk_stream)
                _layer_type = read_word(chunk_stream)
                _child_level = read_word(chunk_stream)
                _default_width = read_word(chunk_stream)
                _default_height = read_word(chunk_stream)
                _blend_mode = read_short(chunk_stream)
                _opacity = read_byte(chunk_stream)
                chunk_stream.read(3)  # reserved
                name = read_ase_string(chunk_stream)
                layers.append(name)

        stream.seek(frame_start + frame_bytes)

    return layers


def layer_is_valid(name: str) -> bool:
    return any(pattern.match(name) for pattern in LAYER_REGEXES)


def validate_layers(layers: Sequence[str]) -> Tuple[List[str], List[str]]:
    invalid = [layer for layer in layers if not layer_is_valid(layer)]
    duplicates = [name for name, count in Counter(layers).items() if count > 1]
    return invalid, duplicates


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Aseprite layer names against BespokeBaby2 layering guidelines."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("Aseprite")],
        help="Files or directories to scan (default: ./Aseprite)",
    )
    parser.add_argument(
        "--aseprite",
        default=os.environ.get("ASEPRITE_PATH", "aseprite"),
        help="Path to aseprite executable (default: from ASEPRITE_PATH or 'aseprite').",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-file success messages.",
    )
    args = parser.parse_args(argv)

    targets = collect_targets(args.paths)
    if not targets:
        print("[INFO] No .aseprite files found in the given paths.", file=sys.stderr)
        return 1

    overall_errors: List[str] = []

    use_cli = False
    aseprite_cmd = args.aseprite
    if aseprite_cmd:
        if Path(aseprite_cmd).exists():
            use_cli = True
        else:
            cli_path = shutil.which(aseprite_cmd)
            if cli_path:
                aseprite_cmd = cli_path
                use_cli = True

    for file_path in targets:
        try:
            if use_cli:
                layers = run_aseprite_list_layers(aseprite_cmd, file_path)
            else:
                layers = parse_layers_from_file(file_path)
        except FileNotFoundError as exc:
            print(exc, file=sys.stderr)
            return 2
        except RuntimeError as exc:
            overall_errors.append(f"{file_path}: {exc}")
            continue

        invalid, duplicates = validate_layers(layers)
        if invalid or duplicates:
            if invalid:
                overall_errors.append(
                    f"{file_path}: invalid layer name(s): {', '.join(invalid)}"
                )
            if duplicates:
                overall_errors.append(
                    f"{file_path}: duplicate layer name(s): {', '.join(duplicates)}"
                )
        elif args.verbose:
            print(f"[OK] {file_path} ({len(layers)} layers)")

    if overall_errors:
        print("[FAIL] Layer validation found issues:", file=sys.stderr)
        for message in overall_errors:
            print(f"  - {message}", file=sys.stderr)
        return 1

    print(f"[PASS] Validated {len(targets)} file(s); all layer names conform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

