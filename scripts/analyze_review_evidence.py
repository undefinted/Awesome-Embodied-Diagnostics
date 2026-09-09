"""Audit review seed data and produce only denominator-bounded summaries."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "review" / "manuscript_evidence_seed.csv"
OUT = ROOT / "outputs" / "review_evidence"


def write_counts(name: str, label: str, counts: Counter[str]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=[label, "study_reports"])
        writer.writeheader()
        writer.writerows({label: key or "not_reported", "study_reports": value} for key, value in sorted(counts.items()))


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"domain", "task", "study", "year", "study_design", "sample_or_setting", "key_publicly_verified_result", "loop_boundary", "public_url"}
    missing_columns = sorted(required - set(rows[0] if rows else []))
    if missing_columns:
        raise SystemExit("Missing columns: " + ", ".join(missing_columns))
    OUT.mkdir(parents=True, exist_ok=True)
    duplicate_titles = [title for title, count in Counter(r["study"].strip().lower() for r in rows).items() if title and count > 1]
    missingness = {column: sum(not r.get(column, "").strip() for r in rows) for column in sorted(required)}
    write_counts("by_domain.csv", "domain", Counter(r["domain"] for r in rows))
    write_counts("by_task.csv", "task", Counter(r["task"] for r in rows))
    write_counts("by_year.csv", "year", Counter(r["year"] for r in rows))
    write_counts("by_study_design.csv", "study_design", Counter(r["study_design"] for r in rows))
    summary = {
        "denominator": "manuscript evidence seed study reports",
        "study_reports": len(rows),
        "unique_normalized_titles": len({r["study"].strip().lower() for r in rows}),
        "duplicate_titles": duplicate_titles,
        "missingness": missingness,
        "analysis_status": "provisional descriptive seed audit; not a final included-study analysis",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Review Evidence Data Readiness", "",
        f"Denominator: **{len(rows)} manuscript evidence-seed study reports**. This is not the final included-study set.", "",
        "## Current seed", "",
        f"- Unique normalized titles: {summary['unique_normalized_titles']}",
        f"- Duplicate titles: {len(duplicate_titles)}", "- Required-field missingness: " + ", ".join(f"{k}={v}" for k, v in missingness.items()), "",
        "## Interpretation", "",
        "Direction, task, year and study-design counts are suitable for checking the balance of the current manuscript examples. They are not estimates of field prevalence because the seed was assembled for narrative support rather than through completed dual-reviewer screening.", "",
        "Study-level success rates are intentionally not pooled. The records span engineering validation, phantoms, volunteers, patients, randomized trials and adjacent technical precedents with incompatible denominators and endpoints.", "",
        "## Next data gate", "",
        "Populate the full extraction template only after title/abstract and full-text decisions are adjudicated. Final figures should use records with `screening_status=include` and a completed evidence stage, loop description and verification trail.", "",
    ]
    (OUT / "DATA_READINESS.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
