#!/usr/bin/env python3
"""Write SHA-256 checksums for repository files in deterministic order."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST.sha256"
EXCLUDED_PARTS = {".git", "__pycache__", "node_modules"}


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        path.is_file()
        and path != OUTPUT
        and not any(part in EXCLUDED_PARTS or part.startswith("workbook_tmp.") for part in relative.parts)
    )


def main() -> None:
    lines = []
    for path in sorted((item for item in ROOT.rglob("*") if included(item)), key=lambda item: item.as_posix()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

