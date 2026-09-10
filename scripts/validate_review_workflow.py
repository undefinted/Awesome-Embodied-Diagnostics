"""Validate review workflow integrity without pretending unfinished review work is complete."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data" / "review"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_unique(rows: list[dict[str, str]], field: str, label: str) -> set[str]:
    values = [row.get(field, "").strip() for row in rows]
    if any(not value for value in values):
        raise SystemExit(f"{label}: blank {field}")
    if len(values) != len(set(values)):
        raise SystemExit(f"{label}: duplicate {field}")
    return set(values)


def decision_is_valid(value: str) -> bool:
    return value.strip().lower() in {"", "include", "exclude", "uncertain"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--require-publication-ready", action="store_true")
    args = parser.parse_args()
    run = REVIEW / "search_runs" / args.run_id

    candidates = read_csv(run / "candidates.csv")
    queue = read_csv(run / "title_abstract_screening_queue.csv")
    candidate_ids = require_unique(candidates, "record_id", "candidates")
    queue_ids = require_unique(queue, "record_id", "title/abstract queue")
    quarantined = {
        row["record_id"] for row in candidates
        if row.get("future_year_flag", "").strip().lower() == "true"
    }
    expected_queue = candidate_ids - quarantined
    if queue_ids != expected_queue:
        raise SystemExit(
            "Every non-quarantined candidate must appear exactly once in the human screening queue; "
            f"missing={len(expected_queue - queue_ids)}, unexpected={len(queue_ids - expected_queue)}"
        )

    required_fields = {
        "abstract", "human_screening_required", "machine_decision_is_final",
        "reviewer_1_id", "reviewer_1_decision", "reviewer_2_id",
        "reviewer_2_decision", "adjudicated_decision",
    }
    missing_fields = required_fields - set(queue[0])
    if missing_fields:
        raise SystemExit("Screening queue fields missing: " + ", ".join(sorted(missing_fields)))

    for row in queue:
        if row["human_screening_required"] != "yes" or row["machine_decision_is_final"] != "no":
            raise SystemExit(f"Machine label improperly marked final: {row['record_id']}")
        for field in ("reviewer_1_decision", "reviewer_2_decision", "adjudicated_decision"):
            if not decision_is_valid(row[field]):
                raise SystemExit(f"Invalid {field} for {row['record_id']}: {row[field]}")
        if row["reviewer_1_decision"] and not row["reviewer_1_id"]:
            raise SystemExit(f"Reviewer 1 decision lacks reviewer identity: {row['record_id']}")
        if row["reviewer_2_decision"] and not row["reviewer_2_id"]:
            raise SystemExit(f"Reviewer 2 decision lacks reviewer identity: {row['record_id']}")
        if row["reviewer_1_id"] and row["reviewer_1_id"] == row["reviewer_2_id"]:
            raise SystemExit(f"Reviewers must be independent: {row['record_id']}")

    r1 = sum(bool(row["reviewer_1_decision"].strip()) for row in queue)
    r2 = sum(bool(row["reviewer_2_decision"].strip()) for row in queue)
    adjudicated = sum(bool(row["adjudicated_decision"].strip()) for row in queue)
    full_text = read_csv(REVIEW / "full_text_screening.csv")
    extracted = read_csv(REVIEW / "evidence_extraction_template.csv")
    risk = read_csv(REVIEW / "risk_of_bias_assessment.csv")
    linkage = read_csv(REVIEW / "study_system_linkage.csv")
    citation_chasing = read_csv(REVIEW / "citation_chasing.csv")
    source_registry = read_csv(REVIEW / "search_source_registry.csv")
    protocol = yaml.safe_load((REVIEW / "review_protocol.yaml").read_text(encoding="utf-8"))

    blockers = []
    if protocol.get("registration", {}).get("status") != "registered":
        blockers.append("definitive protocol registration incomplete")
    if any("pending" in row.get("query_translation_status", "").lower() for row in source_registry):
        blockers.append("information-specialist peer review of search translations incomplete")
    if any(row.get("definitive_search_status") == "not run" for row in source_registry):
        blockers.append("subscription-database searches not run or documented as unavailable at submission")
    if r1 != len(queue) or r2 != len(queue):
        blockers.append("duplicate title/abstract screening incomplete")
    if not full_text:
        blockers.append("duplicate full-text screening not started")
    if not extracted:
        blockers.append("final included-study extraction not started")
    if not linkage:
        blockers.append("report-study-system linkage not started")
    if not risk:
        blockers.append("design-specific risk-of-bias assessment not started")
    if not citation_chasing:
        blockers.append("backward/forward citation chasing not recorded")

    status = {
        "run_id": args.run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_records": len(candidates),
        "quarantined_records": len(quarantined),
        "human_screening_queue_records": len(queue),
        "reviewer_1_completed": r1,
        "reviewer_2_completed": r2,
        "adjudicated_records": adjudicated,
        "full_text_rows": len(full_text),
        "extraction_rows": len(extracted),
        "risk_of_bias_rows": len(risk),
        "study_system_linkage_rows": len(linkage),
        "citation_chasing_rows": len(citation_chasing),
        "publication_ready": not blockers,
        "publication_blockers": blockers,
        "claim_boundary": "Structural validation does not replace independent human screening or extraction.",
    }
    (run / "review_workflow_status.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(status, indent=2))
    if args.require_publication_ready and blockers:
        raise SystemExit("Review is not publication-ready: " + "; ".join(blockers))


if __name__ == "__main__":
    main()
