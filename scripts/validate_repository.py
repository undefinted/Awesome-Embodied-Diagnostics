"""Lightweight repository checks suitable for local use and GitHub Actions."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_RUN_ID = "2026-09-10-public-v3"


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
        ROOT / "data" / "review" / "review_protocol.yaml",
        ROOT / "data" / "review" / "evidence_extraction_template.csv",
        ROOT / "data" / "review" / "full_text_screening.csv",
        ROOT / "data" / "review" / "study_system_linkage.csv",
        ROOT / "data" / "review" / "risk_of_bias_assessment.csv",
        ROOT / "data" / "review" / "citation_chasing.csv",
        ROOT / "data" / "review" / "search_source_registry.csv",
        ROOT / "data" / "review" / "manuscript_evidence_seed.csv",
        ROOT / "data" / "review" / "search_runs" / PRIMARY_RUN_ID / "candidates.csv",
        ROOT / "data" / "review" / "search_runs" / PRIMARY_RUN_ID / "summary.json",
        ROOT / "data" / "review" / "search_runs" / PRIMARY_RUN_ID / "query_log.csv",
        ROOT / "data" / "review" / "search_runs" / PRIMARY_RUN_ID / "search_strategies.csv",
        ROOT / "data" / "review" / "search_runs" / PRIMARY_RUN_ID / "title_abstract_screening_queue.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("Missing required files:", ", ".join(missing))
        return 1

    for path in required[1:4]:
        rows, columns = count_csv(path)
        print(f"{path.name}: {rows} rows, {columns} columns")
        if not rows or not columns:
            return 1

    run = ROOT / "data" / "review" / "search_runs" / PRIMARY_RUN_ID
    candidate_rows, _ = count_csv(run / "candidates.csv")
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    if candidate_rows != summary.get("deduplicated_candidates"):
        print("Frozen search row count does not match summary")
        return 1
    with (run / "query_log.csv").open(encoding="utf-8-sig", newline="") as handle:
        query_log = list(csv.DictReader(handle))
    if len(query_log) != summary.get("configured_source_query_pairs"):
        print("Query-log row count does not match configured source-query pairs")
        return 1
    incomplete = [row for row in query_log if row.get("status") != "ok" or row.get("retrieval_complete", "").lower() != "true"]
    if incomplete or summary.get("source_queries_truncated_at_limit"):
        print(f"Primary public search has incomplete or truncated source-query pairs: {len(incomplete)}")
        return 1
    seed_rows, _ = count_csv(ROOT / "data" / "review" / "manuscript_evidence_seed.csv")
    print(f"review evidence seed: {seed_rows} study reports")
    print(f"frozen retrospective candidates: {candidate_rows} awaiting AI-assisted eligibility assessment")

    tracked_pdfs = list(ROOT.rglob("*.pdf"))
    tracked_pdfs = [p for p in tracked_pdfs if "local_only" not in p.parts]
    print(f"PDFs outside local_only: {len(tracked_pdfs)}")

    digest = hashlib.sha256((ROOT / "README.md").read_bytes()).hexdigest()
    print(f"README SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
