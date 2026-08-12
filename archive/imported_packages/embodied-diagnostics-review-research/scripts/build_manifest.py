#!/usr/bin/env python3
"""Create a machine-readable run manifest for the generated research snapshot."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from common import REPO_ROOT, relative


OUTPUT = REPO_ROOT / "results" / "run_manifest.json"
TRACKED_INPUTS = [
    REPO_ROOT / "config" / "project.json",
    REPO_ROOT / "literature" / "references.csv",
    REPO_ROOT / "literature" / "citation_aliases.csv",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    generated = [
        REPO_ROOT / "literature" / "references.bib",
        REPO_ROOT / "results" / "manuscript_inventory.csv",
        REPO_ROOT / "results" / "citation_usage.csv",
        REPO_ROOT / "results" / "missing_citations.csv",
        REPO_ROOT / "results" / "section_word_counts.csv",
    ]
    manuscript_inputs = sorted((REPO_ROOT / "manuscript").rglob("*.tex"))
    inputs = TRACKED_INPUTS + manuscript_inputs
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": git_commit(),
        "inputs": [{"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in inputs],
        "outputs": [{"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in generated],
        "summary": {
            "reference_records": csv_rows(REPO_ROOT / "literature" / "references.csv"),
            "citation_usage_records": csv_rows(REPO_ROOT / "results" / "citation_usage.csv"),
            "actionable_citation_records": csv_rows(REPO_ROOT / "results" / "missing_citations.csv"),
            "manuscript_files": len(manuscript_inputs),
        },
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

