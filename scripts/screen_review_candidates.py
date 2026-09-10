"""Create a traceable, machine-assisted screening package.

The output is a prioritization aid. It never changes a record to final include.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "data" / "review" / "screening_rules.yaml"


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def matches(text: str, terms: list[str]) -> list[str]:
    value = normalized(text)
    return sorted({term for term in terms if normalized(term) in value})


def classify(row: dict[str, str], rules: dict) -> dict[str, str]:
    title = normalized(row.get("title", ""))
    full_text = normalized(f"{row.get('title', '')} {row.get('abstract', '')}")
    publication_hits = {
        reason: matches(title, terms)
        for reason, terms in rules["publication_type_exclusions"].items()
    }
    publication_hits = {key: value for key, value in publication_hits.items() if value}
    context_hits = matches(full_text, rules["nonmedical_context_exclusions"])
    diagnostic_hits = matches(full_text, rules["diagnostic_objective_terms"])
    adaptation_hits = matches(full_text, rules["observation_conditioned_terms"])
    physical_hits = matches(full_text, rules["physical_interaction_terms"])
    family_hits = {
        family: matches(full_text, terms)
        for family, terms in rules["task_families"].items()
    }
    family_hits = {key: value for key, value in family_hits.items() if value}

    if publication_hits:
        suggestion = "exclude_non_primary"
        reason = "title indicates review, commentary, protocol, correction, or abstract"
    elif context_hits and not family_hits:
        suggestion = "exclude_nonmedical_context"
        reason = "nonmedical active-sensing or robotics context"
    elif family_hits and diagnostic_hits and physical_hits and adaptation_hits:
        suggestion = "priority_core_screen"
        reason = "task-specific physical diagnostic and observation-conditioned signals"
    elif family_hits and diagnostic_hits and physical_hits:
        suggestion = "priority_enabling_screen"
        reason = "task-specific physical diagnostic signals; loop closure requires review"
    elif family_hits or (diagnostic_hits and physical_hits):
        suggestion = "manual_scope_screen"
        reason = "partial scope signals; requires title-and-abstract adjudication"
    else:
        suggestion = "low_priority_screen"
        reason = "insufficient explicit title-and-abstract scope signals"

    return {
        "machine_screening_suggestion": suggestion,
        "machine_screening_reason": reason,
        "matched_task_families": ";".join(sorted(family_hits)),
        "matched_diagnostic_terms": ";".join(diagnostic_hits),
        "matched_physical_terms": ";".join(physical_hits),
        "matched_adaptation_terms": ";".join(adaptation_hits),
        "matched_exclusion_terms": ";".join(
            sorted(context_hits + [term for values in publication_hits.values() for term in values])
        ),
        "reviewer_1_decision": "",
        "reviewer_1_reason": "",
        "reviewer_2_decision": "",
        "reviewer_2_reason": "",
        "adjudicated_decision": "",
        "adjudicated_reason": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run = ROOT / "data" / "review" / "search_runs" / args.run_id
    rules_bytes = RULES_PATH.read_bytes()
    rules = yaml.safe_load(rules_bytes)
    with (run / "candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    screened = []
    for row in rows:
        item = dict(row)
        item.update(classify(row, rules))
        screened.append(item)

    priority = {
        "priority_core_screen": 0,
        "priority_enabling_screen": 1,
        "manual_scope_screen": 2,
        "exclude_non_primary": 3,
        "exclude_nonmedical_context": 4,
        "low_priority_screen": 5,
    }
    screened.sort(key=lambda row: (
        priority[row["machine_screening_suggestion"]],
        row.get("direction", ""),
        -(int(row["year"]) if row.get("year", "").isdigit() else 0),
        row.get("title", ""),
    ))
    fields = list(screened[0]) if screened else []
    output = run / "machine_assisted_screening.csv"
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(screened)

    counts = Counter(row["machine_screening_suggestion"] for row in screened)
    summary = {
        "run_id": args.run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": len(screened),
        "rules_version": rules["version"],
        "rules_sha256": hashlib.sha256(rules_bytes).hexdigest(),
        "suggestion_counts": dict(sorted(counts.items())),
        "claim_boundary": rules["claim_boundary"],
    }
    (run / "machine_screening_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

