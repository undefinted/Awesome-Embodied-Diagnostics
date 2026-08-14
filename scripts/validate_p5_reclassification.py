#!/usr/bin/env python3
"""Validate P5 reclassification accounting and derived tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--records", required=True, type=Path)
    p.add_argument("--counts", required=True, type=Path)
    p.add_argument("--matrix", required=True, type=Path)
    p.add_argument("--projects", required=True, type=Path)
    p.add_argument("--qc", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    records, counts, matrix, projects = map(read_csv, [args.records, args.counts, args.matrix, args.projects])
    qc = json.loads(args.qc.read_text(encoding="utf-8"))
    errors = []
    included = [r for r in records if r["scope_status"] == "included_title_candidate"]
    excluded = [r for r in records if r["scope_status"] == "excluded_title"]

    if len(records) != qc["unique_works"]: errors.append("unique-work record count does not match QC")
    if len(included) != qc["included_title_candidates"]: errors.append("included count does not match QC")
    if len(excluded) != qc["excluded_by_title_scope_rules"]: errors.append("excluded count does not match QC")
    if len(included) + len(excluded) != len(records): errors.append("scope accounting does not close")
    if any(not r["primary_task_code"] for r in records): errors.append("missing primary task")
    if len({r["work_key"] for r in records}) != len(records): errors.append("duplicate work key in unique records")

    derived = defaultdict(lambda: Counter(public_visible=0, public_available=0))
    modality = defaultdict(lambda: Counter(public_visible=0, public_available=0))
    for r in included:
        task = r["primary_task_code"]
        derived[task]["public_visible"] += 1
        derived[task]["public_available"] += int(r["public_available"])
        for tag in filter(None, r["modality_tags"].split(";")):
            modality[(task, tag)]["public_visible"] += 1
            modality[(task, tag)]["public_available"] += int(r["public_available"])

    for r in counts:
        task = r["primary_task_code"]
        if int(r["public_visible_unique_title_candidates"]) != derived[task]["public_visible"]:
            errors.append(f"visible task count mismatch: {task}")
        if int(r["public_available_location_identified"]) != derived[task]["public_available"]:
            errors.append(f"available task count mismatch: {task}")
    if sum(int(r["public_visible_unique_title_candidates"]) for r in counts) != len(included):
        errors.append("task count sum does not equal included unique works")

    matrix_seen = set()
    for r in matrix:
        key = (r["primary_task_code"], r["modality_tag"])
        matrix_seen.add(key)
        if int(r["public_visible_unique_title_candidates"]) != modality[key]["public_visible"]:
            errors.append(f"modality visible mismatch: {key}")
        if int(r["public_available_location_identified"]) != modality[key]["public_available"]:
            errors.append(f"modality available mismatch: {key}")
    if matrix_seen != set(modality): errors.append("modality matrix keys do not match record-derived keys")

    if len({r["project_id"] for r in projects}) != len(projects): errors.append("duplicate project_id")
    if any(not r["source_url"] for r in projects): errors.append("project missing source URL")
    if any(not r["primary_task_code"] for r in projects): errors.append("project missing primary task")

    report = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "unique_works": len(records),
        "included_title_candidates": len(included),
        "excluded_title_records": len(excluded),
        "public_available_unique_included": sum(int(r["public_available"]) for r in included),
        "task_rows": len(counts),
        "task_modality_rows": len(matrix),
        "curated_projects": len(projects),
        "projects_added_to_publication_counts": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if errors: raise SystemExit(1)


if __name__ == "__main__":
    main()
