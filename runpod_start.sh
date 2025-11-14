#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "[+] creating .venv"
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "[+] upgrading pip"
pip install --upgrade pip

echo "[+] installing requirements"
pip install -r requirements-runpod.txt

echo "[+] running incremental analyzer with caching"
python3 scripts/analyze_all_with_cache.py \
  --src-dir data/punks_24px \
  --cache-dir .cache/trait_analyzer \
  --color-map data/color_name_map.json \
  --output-csv data/trait_suggestions.csv \
  --output-json data/trait_suggestions.json \
  --top-colors 5 \
  --resume

echo "[+] running validation"
python3 scripts/validate_traits.py --traits data/trait_suggestions.csv

echo "[+] completed"
