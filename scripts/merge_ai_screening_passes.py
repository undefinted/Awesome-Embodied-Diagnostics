"""Merge two independently produced AI eligibility passes with provenance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "data" / "review" / "search_runs" / "2026-09-10-public-v3"
DEFAULT_OUTPUT = ROOT / "data" / "review" / "ai_assisted_screening.csv"
DECISIONS = {"include", "exclude", "uncertain"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def keyed(rows: list[dict[str, str]], source: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        record_id = row.get("record_id", "").strip()
        decision = row.get("decision", "").strip().lower()
        if not record_id or record_id in output:
            raise SystemExit(f"{source}: blank or duplicate record_id {record_id!r}")
        if decision not in DECISIONS:
            raise SystemExit(f"{source}: invalid decision for {record_id}: {decision!r}")
        output[record_id] = row
    return output


def input_hash(row: dict[str, str]) -> str:
    payload = json.dumps(
        {"record_id": row["record_id"], "title": row.get("title", ""), "abstract": row.get("abstract", "")},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass-1", required=True, type=Path)
    parser.add_argument("--pass-2", required=True, type=Path)
    parser.add_argument("--suggestion", default="priority_core_screen")
    parser.add_argument("--model-1", default="codex-ai-review-pass-1")
    parser.add_argument("--model-2", default="codex-ai-review-pass-2")
    parser.add_argument("--adjudication", type=Path)
    parser.add_argument("--adjudication-model", default="codex-ai-review-adjudication")
    parser.add_argument("--prompt-version", default="aed-eligibility-2026-09-10.1")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    candidates = {
        row["record_id"]: row for row in read_csv(RUN / "machine_assisted_screening.csv")
        if row.get("machine_screening_suggestion") == args.suggestion
    }
    pass_1 = keyed(read_csv(args.pass_1), "pass 1")
    pass_2 = keyed(read_csv(args.pass_2), "pass 2")
    adjudication = keyed(read_csv(args.adjudication), "adjudication") if args.adjudication else {}
    expected = set(candidates)
    for label, records in (("pass 1", pass_1), ("pass 2", pass_2)):
        if set(records) != expected:
            raise SystemExit(
                f"{label}: expected {len(expected)} records; "
                f"missing={len(expected - set(records))}, unexpected={len(set(records) - expected)}"
            )

    existing = {
        row["record_id"]: row for row in read_csv(args.output)
    } if args.output.exists() else {}
    created_at = datetime.now(timezone.utc).isoformat()
    for record_id in sorted(expected):
        source = candidates[record_id]
        first = pass_1[record_id]
        second = pass_2[record_id]
        first_decision = first["decision"].strip().lower()
        second_decision = second["decision"].strip().lower()
        agreement = first_decision == second_decision
        final_decision = first_decision if agreement else "uncertain"
        adjudicated = adjudication.get(record_id)
        if adjudicated:
            final_decision = adjudicated["decision"].strip().lower()
        existing[record_id] = {
            "record_id": record_id,
            "assessment_1_model": args.model_1,
            "assessment_1_prompt_version": args.prompt_version,
            "assessment_1_input_sha256": input_hash(source),
            "assessment_1_decision": first_decision,
            "assessment_1_scope_evidence": first.get("scope_evidence", "").strip(),
            "assessment_1_confidence": first.get("confidence", "").strip(),
            "assessment_2_model": args.model_2,
            "assessment_2_prompt_version": args.prompt_version,
            "assessment_2_input_sha256": input_hash(source),
            "assessment_2_decision": second_decision,
            "assessment_2_scope_evidence": second.get("scope_evidence", "").strip(),
            "assessment_2_confidence": second.get("confidence", "").strip(),
            "conflict_resolution": (
                ("ai_adjudicated_uncertain" if final_decision == "uncertain" else "ai_adjudicated")
                if adjudicated else ("agreement" if agreement else "pending_ai_adjudication")
            ),
            "final_ai_decision": final_decision,
            "final_ai_reason": (
                adjudicated.get("reason", "").strip() if adjudicated else
                (first.get("reason", "").strip() if agreement else
                 f"Pass disagreement: {first_decision} versus {second_decision}")
            ),
            "ai_adjudication_model": args.adjudication_model if adjudicated else "",
            "ai_adjudication_evidence": adjudicated.get("scope_evidence", "").strip() if adjudicated else "",
            "ai_adjudication_confidence": adjudicated.get("confidence", "").strip() if adjudicated else "",
            "requires_author_confirmation": (
                "yes" if final_decision == "uncertain" else
                (adjudicated.get("requires_author_confirmation", "no").strip().lower() if adjudicated else "no")
            ),
            "created_at": created_at,
        }

    fields = [
        "record_id", "assessment_1_model", "assessment_1_prompt_version", "assessment_1_input_sha256",
        "assessment_1_decision", "assessment_1_scope_evidence", "assessment_1_confidence",
        "assessment_2_model", "assessment_2_prompt_version", "assessment_2_input_sha256",
        "assessment_2_decision", "assessment_2_scope_evidence", "assessment_2_confidence",
        "conflict_resolution", "final_ai_decision", "final_ai_reason",
        "ai_adjudication_model", "ai_adjudication_evidence", "ai_adjudication_confidence",
        "requires_author_confirmation", "created_at",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(existing[key] for key in sorted(existing))
    print(f"merged={len(expected)} total_ledger={len(existing)} output={args.output}")


if __name__ == "__main__":
    main()
