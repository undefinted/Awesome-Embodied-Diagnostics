#!/usr/bin/env python3
"""Build JSON, BibTeX, and coverage summaries from the reference CSV."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "references.csv"


def bibtex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def bib_author(value: str) -> str:
    if value.endswith(" et al."):
        return value.removesuffix(" et al.") + " and others"
    if ";" in value:
        return " and ".join(part.strip() for part in value.split(";"))
    return "{" + value + "}"


def entry_type(source_type: str) -> str:
    if source_type in {"standard", "regulation", "regulatory_guidance", "technical_guidance", "policy_framework"}:
        return "misc"
    if source_type in {"preprint", "dataset_benchmark"}:
        return "misc"
    return "article"


def top_level_sections(section_field: str) -> set[str]:
    return {item.split("/", 1)[0] for item in section_field.split("|")}


def main() -> None:
    with CATALOG.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    (ROOT / "data" / "references.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    bib_entries: list[str] = []
    for row in rows:
        fields = [
            ("author", bib_author(row["authors_short"])),
            ("title", "{" + bibtex_escape(row["title"]) + "}"),
            ("year", row["year"]),
        ]
        if entry_type(row["source_type"]) == "article":
            fields.append(("journal", "{" + bibtex_escape(row["venue"]) + "}"))
        else:
            fields.append(("howpublished", "{" + bibtex_escape(row["venue"]) + "}"))
        for key in ("volume", "locator", "doi", "url"):
            if row[key]:
                bib_key = "pages" if key == "locator" and "–" in row[key] else key
                value = row[key].replace("–", "--") if bib_key == "pages" else row[key]
                fields.append((bib_key, "{" + bibtex_escape(value) + "}"))
        fields.extend(
            [
                ("note", "{Evidence role: " + bibtex_escape(row["evidence_role"]) + "}"),
                ("keywords", "{" + bibtex_escape(row["sections"].replace("|", ",")) + "}"),
            ]
        )
        body = ",\n".join(f"  {key} = {{{value}}}" if key == "author" else f"  {key} = {value}" for key, value in fields)
        bib_entries.append(f"@{entry_type(row['source_type'])}{{{row['citekey']},\n{body}\n}}")
    (ROOT / "data" / "references.bib").write_text("\n\n".join(bib_entries) + "\n", encoding="utf-8")

    section_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    verification_counts: Counter[str] = Counter()
    for row in rows:
        for section in top_level_sections(row["sections"]):
            section_counts[section] += 1
        type_counts[row["source_type"]] += 1
        verification_counts[row["verification_status"]] += 1

    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    with (results / "coverage_by_section.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "reference_count"])
        writer.writerows(sorted(section_counts.items()))

    md = [
        "# Coverage summary",
        "",
        f"- Catalog records: {len(rows)}",
        f"- Core references from the prior discussion: {sum(r['core_reference'] == '1' for r in rows)}",
        f"- Records with DOI: {sum(bool(r['doi']) for r in rows)}",
        f"- Records verified on a primary page on 2026-08-12: {sum(r['verification_status'].startswith('verified_primary') for r in rows)}",
        "",
        "## References by top-level section",
        "",
        "| Section | Count |",
        "|---|---:|",
        *(f"| {key} | {value} |" for key, value in sorted(section_counts.items())),
        "",
        "## Source types",
        "",
        "| Source type | Count |",
        "|---|---:|",
        *(f"| {key} | {value} |" for key, value in sorted(type_counts.items())),
        "",
        "## Verification status",
        "",
        "| Status | Count |",
        "|---|---:|",
        *(f"| {key} | {value} |" for key, value in sorted(verification_counts.items())),
        "",
    ]
    (results / "coverage_summary.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()

