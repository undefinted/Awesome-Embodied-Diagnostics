#!/usr/bin/env python3
"""Audit overlap among P5 retrieval buckets using DOI/title work keys."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


def normalized_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"[^\w]+", "", value, flags=re.UNICODE)


def work_key(row: dict[str, str]) -> str:
    doi = (row.get("doi") or "").strip().casefold()
    if doi:
        doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", doi)
        return f"doi:{doi}"
    return f"title:{normalized_title(row.get('title', ''))}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.records.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[work_key(row)].append(row)

    overlap_rows = []
    pair_counts: dict[str, int] = defaultdict(int)
    for key, assignments in sorted(grouped.items()):
        codes = sorted({row["task_code"] for row in assignments})
        if len(codes) <= 1:
            continue
        overlap_rows.append({
            "work_key": key,
            "task_codes": "+".join(codes),
            "tasks": " | ".join(sorted({row["task"] for row in assignments})),
            "title": assignments[0].get("title", ""),
            "doi": assignments[0].get("doi", ""),
            "assignment_count": len(codes),
        })
        for index, left in enumerate(codes):
            for right in codes[index + 1:]:
                pair_counts[f"{left}+{right}"] += 1

    csv_path = args.output_dir / "p5_retrieval_bucket_overlap_2026-08-14.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "work_key", "task_codes", "tasks", "title", "doi", "assignment_count"
        ])
        writer.writeheader()
        writer.writerows(overlap_rows)

    summary = {
        "input": str(args.records),
        "input_sha256": sha256(args.records),
        "task_assignment_rows": len(rows),
        "unique_works": len(grouped),
        "unique_works_in_multiple_buckets": len(overlap_rows),
        "overlap_pair_counts": dict(sorted(pair_counts.items())),
        "interpretation": "Retrieval buckets are non-exclusive. These figures audit overlap and are not clinical-category publication totals."
    }
    (args.output_dir / "p5_retrieval_bucket_overlap_summary_2026-08-14.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
