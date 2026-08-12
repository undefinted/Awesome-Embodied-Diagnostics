"""Lightweight repository checks suitable for local use and GitHub Actions."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def count_csv(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        return sum(1 for _ in reader), len(header)


def main() -> int:
    required = [
        ROOT / "README.md",
        ROOT / "data" / "standalone_snapshots" / "2026-08-12" / "literature_multisource_deduplicated.csv",
        ROOT / "data" / "standalone_snapshots" / "2026-08-12" / "literature_task_assignments_all_snapshots.csv",
        ROOT / "data" / "standalone_snapshots" / "2026-08-12" / "query_log.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("Missing required files:", ", ".join(missing))
        return 1

    for path in required[1:]:
        rows, columns = count_csv(path)
        print(f"{path.name}: {rows} rows, {columns} columns")
        if not rows or not columns:
            return 1

    tracked_pdfs = list(ROOT.rglob("*.pdf"))
    tracked_pdfs = [p for p in tracked_pdfs if "local_only" not in p.parts]
    print(f"PDFs outside local_only: {len(tracked_pdfs)}")

    digest = hashlib.sha256((ROOT / "README.md").read_bytes()).hexdigest()
    print(f"README SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
