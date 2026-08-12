#!/usr/bin/env python3
"""Validate the reference catalog without network access."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
REQUIRED = {
    "record_id",
    "citekey",
    "core_reference",
    "sections",
    "source_type",
    "authors_short",
    "year",
    "title",
    "venue",
    "url",
    "evidence_role",
    "evidence_stage",
    "verification_status",
    "provenance",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", nargs="?", default="data/references.csv")
    parser.add_argument("--report", default="results/validation_report.txt")
    args = parser.parse_args()

    catalog = Path(args.catalog)
    report = Path(args.report)
    errors: list[str] = []
    warnings: list[str] = []

    with catalog.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED - set(reader.fieldnames or [])
        if missing_columns:
            errors.append(f"Missing columns: {sorted(missing_columns)}")
        rows = list(reader)

    for field in ("record_id", "citekey"):
        duplicates = [key for key, count in Counter(r[field] for r in rows).items() if count > 1]
        if duplicates:
            errors.append(f"Duplicate {field}: {duplicates}")

    for index, row in enumerate(rows, start=2):
        label = row.get("record_id") or f"line {index}"
        for field in REQUIRED:
            if not row.get(field, "").strip():
                errors.append(f"{label}: empty required field {field}")
        try:
            year = int(row["year"])
            if not 1900 <= year <= 2100:
                errors.append(f"{label}: implausible year {year}")
        except ValueError:
            errors.append(f"{label}: non-integer year {row['year']!r}")

        doi = row.get("doi", "").strip()
        if doi and not DOI_RE.match(doi):
            errors.append(f"{label}: malformed DOI {doi!r}")

        parsed = urlparse(row.get("url", ""))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{label}: URL must be absolute HTTPS: {row.get('url')!r}")

        if row.get("authors_short", "").endswith("et al."):
            warnings.append(f"{label}: abbreviated author list; Crossref enrichment recommended")

    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Reference catalog validation",
        f"records={len(rows)}",
        f"core_records={sum(r.get('core_reference') == '1' for r in rows)}",
        f"errors={len(errors)}",
        f"warnings={len(warnings)}",
        "",
        "ERRORS",
        *(errors or ["none"]),
        "",
        "WARNINGS",
        *(warnings or ["none"]),
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:6]))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

