#!/usr/bin/env bash
set -euo pipefail

review_repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$review_repo_dir"

python3 scripts/build_bibtex.py
python3 scripts/build_inventory.py
python3 scripts/extract_citations.py
python3 scripts/validate_bibliography.py
python3 scripts/count_words.py
python3 scripts/build_manifest.py
python3 -m unittest discover -s tests -v

