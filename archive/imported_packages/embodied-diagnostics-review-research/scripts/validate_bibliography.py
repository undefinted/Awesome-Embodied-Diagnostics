#!/usr/bin/env python3
"""Compare manuscript citation keys with the literature registry."""

from __future__ import annotations

import csv
from collections import defaultdict

from common import REPO_ROOT


USAGE = REPO_ROOT / "results" / "citation_usage.csv"
REFERENCES = REPO_ROOT / "literature" / "references.csv"
OUTPUT = REPO_ROOT / "results" / "missing_citations.csv"


def main() -> None:
    with REFERENCES.open(newline="", encoding="utf-8") as handle:
        reference_rows = {row["citation_key"]: row for row in csv.DictReader(handle)}
    cited_in: dict[str, set[str]] = defaultdict(set)
    with USAGE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            cited_in[row["citation_key"]].add(row["file"])
    rows: list[list[str]] = []
    for key in sorted(cited_in):
        ref = reference_rows.get(key)
        if ref is None:
            issue = "missing_registry_entry"
            status = "missing"
        elif ref["metadata_status"] in {"unresolved", "provisional"}:
            issue = "metadata_requires_verification"
            status = ref["metadata_status"]
        else:
            continue
        rows.append([key, status, issue, ";".join(sorted(cited_in[key]))])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["citation_key", "metadata_status", "issue", "cited_in"])
        writer.writerows(rows)
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(rows)} actionable records")


if __name__ == "__main__":
    main()

