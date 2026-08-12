#!/usr/bin/env python3
"""Inventory recovered manuscript/source artifacts with SHA-256 checksums."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from common import REPO_ROOT, relative


OUTPUT = REPO_ROOT / "results" / "manuscript_inventory.csv"
ROOTS = [REPO_ROOT / "manuscript", REPO_ROOT / "sources"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    paths = sorted(path for root in ROOTS for path in root.rglob("*") if path.is_file())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "category", "bytes", "sha256"])
        for path in paths:
            category = "recovered" if "recovered_versions" in path.parts else "drafted_or_source"
            writer.writerow([relative(path), category, path.stat().st_size, sha256(path)])
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(paths)} artifacts")


if __name__ == "__main__":
    main()

