#!/usr/bin/env python3
"""Build mutually exclusive Clinical Detection and Intervention statistics.

This script deliberately separates two evidence layers:

1. ``comparable_core``: one frozen, DOI-first/title-second deduplicated public-
   index corpus screened with the same title rules for all three mechanisms.
   A paper receives one primary mechanism and one primary subtask.  The
   hierarchy is sample acquisition > elicited response > active observation,
   because the terminal diagnostic-evidence action defines the primary class.
2. ``retrieval_audit``: the broader saved search assignments.  These figures
   quantify search coverage and are *not* publication counts or included-study
   counts.  They are exported only to expose the denominator and screening gap.

The outputs are suitable for audit and presentation, but remain title-level
candidate statistics.  Full-text dual screening is required before they may be
reported as systematic-review inclusion counts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


MECHANISMS = {
    "1.1": ("Active observational sensing", "主动观察式检测"),
    "1.2": ("Response-based interactive diagnosis", "响应式交互诊断"),
    "1.3": ("Sample-based interactive diagnosis", "采样式交互诊断"),
}

TASKS = {
    "A1": ("1.1", "Ultrasound examination and active scanning", "超声检查与主动扫描"),
    "A2": ("1.1", "Flexible gastrointestinal endoscopic examination", "胃肠柔性内镜检查"),
    "A3": ("1.1", "Active or magnetically controlled capsule endoscopy", "主动或磁控胶囊内镜检查"),
    "A4": ("1.1", "Bronchoscopic observation and navigation", "支气管镜观察与导航"),
    "A5": ("1.1", "Optical coherence tomography acquisition", "光学相干断层成像采集"),
    "A6": ("1.1", "Active auscultation and acoustic examination", "主动听诊与声学检查"),
    "R1": ("1.2", "Robotic palpation", "机器人触诊"),
    "R2": ("1.2", "Elastography and stiffness mapping", "弹性成像与刚度测绘"),
    "R3": ("1.2", "Joint laxity and provocation examination", "关节松弛度与激发检查"),
    "R4": ("1.2", "Tone and spasticity assessment", "肌张力与痉挛评估"),
    "R5": ("1.2", "Percussion and reflex examination", "叩诊与反射检查"),
    "R6": ("1.2", "Stimulation-response mapping", "刺激—响应映射"),
    "S1": ("1.3", "Percutaneous or core-needle biopsy", "经皮或芯针活检"),
    "S2": ("1.3", "Endoscopic or bronchoscopic biopsy", "内镜或支气管镜活检"),
    "S3": ("1.3", "Capsule-based tissue or fluid sampling", "胶囊组织或体液采样"),
    "S4": ("1.3", "Venipuncture and phlebotomy", "静脉穿刺与采血"),
    "S5": ("1.3", "Swab and cavity-specimen collection", "拭子与腔道标本采集"),
}

# Route/evidence-specific tasks take precedence over generic modalities.
MECHANISM_PRIORITY = {"1.3": 0, "1.2": 1, "1.1": 2}
TASK_PRIORITY = {
    "S3": 0, "S2": 1, "S4": 2, "S5": 3, "S1": 4,
    "R2": 0, "R6": 1, "R3": 2, "R4": 3, "R5": 4, "R1": 5,
    "A4": 0, "A3": 1, "A2": 2, "A5": 3, "A6": 4, "A1": 5,
}


def norm_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def work_key(row: dict[str, str]) -> str:
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", (row.get("doi") or "").strip().casefold())
    return f"doi:{doi}" if doi else f"title:{norm_title(row.get('title', ''))}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def yes(value: str) -> int:
    return int((value or "").strip().casefold() in {"1", "true", "yes", "y"})


def choose_primary(codes: set[str]) -> str:
    mechanisms = {TASKS[c][0] for c in codes}
    mechanism = min(mechanisms, key=lambda x: MECHANISM_PRIORITY[x])
    candidates = [c for c in codes if TASKS[c][0] == mechanism]
    return min(candidates, key=lambda x: TASK_PRIORITY.get(x, 999))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screened-records", required=True, type=Path)
    parser.add_argument("--retrieval-assignments", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--snapshot-date", default="2026-08-15")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.screened_records.open("r", encoding="utf-8-sig", newline="") as handle:
        screened = list(csv.DictReader(handle))
    with args.retrieval_assignments.open("r", encoding="utf-8-sig", newline="") as handle:
        retrieval = list(csv.DictReader(handle))

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in screened:
        grouped[work_key(row)].append(row)

    unique_rows: list[dict] = []
    overlap_rows: list[dict] = []
    for key, rows in sorted(grouped.items()):
        codes = {r["task_code"] for r in rows}
        primary = choose_primary(codes)
        mechanism = TASKS[primary][0]
        first = rows[0]
        secondary = sorted(codes - {primary})
        public_available = int(any(yes(r.get("public_full_text_identified")) for r in rows))
        try:
            year = int(first.get("year") or 0)
        except ValueError:
            year = 0
        unique = {
            "work_key": key,
            "title": first.get("title", ""),
            "year": year or "",
            "doi": first.get("doi", ""),
            "primary_mechanism_code": mechanism,
            "primary_mechanism_en": MECHANISMS[mechanism][0],
            "primary_mechanism_cn": MECHANISMS[mechanism][1],
            "primary_task_code": primary,
            "primary_task_en": TASKS[primary][1],
            "primary_task_cn": TASKS[primary][2],
            "secondary_task_codes": ";".join(secondary),
            "all_title_rule_hits": ";".join(sorted(codes)),
            "classification_rule": "terminal evidence-action hierarchy: sample > response > observation; route-specific task precedence",
            "public_visible": 1,
            "public_available_location_identified": public_available,
            "best_public_url": next((r.get("best_public_url", "") for r in rows if r.get("best_public_url")), ""),
            "record_url": first.get("record_url", ""),
            "sources": first.get("sources", ""),
            "screening_level": "comparable conservative automated title screen; full-text inclusion pending",
        }
        unique_rows.append(unique)
        if len(codes) > 1:
            overlap_rows.append({
                "work_key": key,
                "title": first.get("title", ""),
                "year": year or "",
                "doi": first.get("doi", ""),
                "all_title_rule_hits": ";".join(sorted(codes)),
                "primary_task_code": primary,
                "primary_mechanism_code": mechanism,
                "resolution_basis": unique["classification_rule"],
                "requires_full_text_confirmation": "yes",
            })

    mechanism_rows: list[dict] = []
    for code in MECHANISMS:
        rows = [r for r in unique_rows if r["primary_mechanism_code"] == code]
        mechanism_rows.append({
            "mechanism_code": code,
            "mechanism_en": MECHANISMS[code][0],
            "mechanism_cn": MECHANISMS[code][1],
            "public_visible_unique_title_candidates": len(rows),
            "public_available_location_identified": sum(r["public_available_location_identified"] for r in rows),
            "public_available_share": round(sum(r["public_available_location_identified"] for r in rows) / len(rows), 4) if rows else "",
            "since_2021": sum(isinstance(r["year"], int) and r["year"] >= 2021 for r in rows),
            "share_of_comparable_core": round(len(rows) / len(unique_rows), 4) if unique_rows else "",
            "counting_unit": "one unique work; primary mechanism mutually exclusive",
        })

    task_rows: list[dict] = []
    for task, (mechanism, en, cn) in TASKS.items():
        rows = [r for r in unique_rows if r["primary_task_code"] == task]
        task_rows.append({
            "mechanism_code": mechanism,
            "task_code": task,
            "task_en": en,
            "task_cn": cn,
            "public_visible_unique_title_candidates": len(rows),
            "public_available_location_identified": sum(r["public_available_location_identified"] for r in rows),
            "public_available_share": round(sum(r["public_available_location_identified"] for r in rows) / len(rows), 4) if rows else "",
            "since_2021": sum(isinstance(r["year"], int) and r["year"] >= 2021 for r in rows),
            "counting_unit": "one unique work assigned to one primary subtask",
        })

    years = sorted({r["year"] for r in unique_rows if isinstance(r["year"], int)})
    annual_rows = []
    for year in years:
        row = {"year": year}
        for code in MECHANISMS:
            subset = [r for r in unique_rows if r["year"] == year and r["primary_mechanism_code"] == code]
            row[f"{code}_public_visible"] = len(subset)
            row[f"{code}_public_available"] = sum(r["public_available_location_identified"] for r in subset)
        row["total_public_visible"] = sum(row[f"{c}_public_visible"] for c in MECHANISMS)
        row["total_public_available"] = sum(row[f"{c}_public_available"] for c in MECHANISMS)
        annual_rows.append(row)

    # The retrieval audit uses only labels assigned by the saved search snapshots.
    # It is intentionally not filtered into the comparable title-screened core.
    retrieval_map = {
        "Active observational sensing": "1.1", "主动观察式检测": "1.1",
        "Response-based interactive diagnosis": "1.2", "响应式交互检测": "1.2",
        "Sample-based interactive diagnosis": "1.3", "采样式交互检测": "1.3",
    }
    retrieval_keys: dict[str, set[str]] = defaultdict(set)
    for row in retrieval:
        mechanism = retrieval_map.get(row.get("category", ""))
        if mechanism:
            retrieval_keys[mechanism].add(work_key(row))
    retrieval_union = set().union(*retrieval_keys.values())
    retrieval_audit = []
    for code in MECHANISMS:
        core = next(r["public_visible_unique_title_candidates"] for r in mechanism_rows if r["mechanism_code"] == code)
        retrieval_audit.append({
            "mechanism_code": code,
            "mechanism_en": MECHANISMS[code][0],
            "retrieval_assigned_unique_records_unscreened": len(retrieval_keys[code]),
            "comparable_core_title_candidates": core,
            "difference_requiring_screening_or_scope_reconciliation": len(retrieval_keys[code]) - core,
            "interpretation": "retrieval coverage denominator only; assignments may contain false positives and cross-mechanism duplicates",
        })

    umbrella = [{
        "domain": "Clinical Detection and Intervention",
        "snapshot_date": args.snapshot_date,
        "public_visible_unique_title_candidates_comparable_core": len(unique_rows),
        "public_available_location_identified": sum(r["public_available_location_identified"] for r in unique_rows),
        "public_available_share": round(sum(r["public_available_location_identified"] for r in unique_rows) / len(unique_rows), 4),
        "since_2021": sum(isinstance(r["year"], int) and r["year"] >= 2021 for r in unique_rows),
        "multi_rule_records_resolved": len(overlap_rows),
        "retrieval_assignment_union_unscreened": len(retrieval_union),
        "scope_note": "comparable core is a conservative title-level candidate map, not a systematic-review inclusion count",
    }]

    taxonomy_rows = [
        {
            "mechanism_code": "1.1",
            "mechanism_en": MECHANISMS["1.1"][0],
            "mechanism_cn": MECHANISMS["1.1"][1],
            "defining_action": "move, orient, align or scan an in-vivo sensor to change the next observation",
            "terminal_diagnostic_evidence": "in-vivo image, sound or physiological signal",
            "include_if": "the physical action changes acquisition geometry/coverage/contact and the diagnostic endpoint remains an in-vivo observation",
            "exclude_or_reassign_if": "material is removed for ex-vivo testing (1.3), or a controlled perturbation is interpreted through its elicited response (1.2)",
            "carrier_scope": "robot arm, motorized probe, steerable endoscope, active/magnetic capsule or other controllable physical carrier",
        },
        {
            "mechanism_code": "1.2",
            "mechanism_en": MECHANISMS["1.2"][0],
            "mechanism_cn": MECHANISMS["1.2"][1],
            "defining_action": "apply a controlled mechanical, acoustic, electrical or neurophysiological perturbation",
            "terminal_diagnostic_evidence": "elicited deformation, force, physiological or functional response",
            "include_if": "stimulus parameters or contact are purposeful diagnostic actions and the response is measured to infer state",
            "exclude_or_reassign_if": "force is used only for safe positioning (1.1), or the terminal evidence is an ex-vivo sample result (1.3)",
            "carrier_scope": "robotic or mechatronic actuator, controlled stimulator or instrumented contact device",
        },
        {
            "mechanism_code": "1.3",
            "mechanism_en": MECHANISMS["1.3"][0],
            "mechanism_cn": MECHANISMS["1.3"][1],
            "defining_action": "puncture, aspirate, cut, swab or collect material from the patient",
            "terminal_diagnostic_evidence": "ex-vivo pathological, cytological, biochemical, microbiological or molecular result, including sample adequacy",
            "include_if": "the action obtains diagnostic material and sampling/adequacy is part of the sensing-decision-action-feedback pathway",
            "exclude_or_reassign_if": "needle/endoscope motion is purely therapeutic, or imaging alone is the diagnostic endpoint (1.1)",
            "carrier_scope": "robot arm, needle or biopsy device, endoscope, capsule, venipuncture system or specimen-collection platform",
        },
    ]

    write_csv(args.output_dir / "clinical_detection_intervention_unique_records.csv", unique_rows)
    write_csv(args.output_dir / "clinical_detection_intervention_overlap_audit.csv", overlap_rows)
    write_csv(args.output_dir / "clinical_detection_intervention_mechanism_counts.csv", mechanism_rows)
    write_csv(args.output_dir / "clinical_detection_intervention_subtask_counts.csv", task_rows)
    write_csv(args.output_dir / "clinical_detection_intervention_annual_counts.csv", annual_rows)
    write_csv(args.output_dir / "clinical_detection_intervention_retrieval_audit.csv", retrieval_audit)
    write_csv(args.output_dir / "clinical_detection_intervention_summary.csv", umbrella)
    write_csv(args.output_dir / "clinical_detection_intervention_taxonomy.csv", taxonomy_rows)

    qc = {
        "schema_version": "clinical-detection-intervention-exclusive-v1",
        "snapshot_date": args.snapshot_date,
        "screened_input": str(args.screened_records),
        "screened_input_sha256": sha256(args.screened_records),
        "retrieval_input": str(args.retrieval_assignments),
        "retrieval_input_sha256": sha256(args.retrieval_assignments),
        "screened_task_rows": len(screened),
        "comparable_core_unique_works": len(unique_rows),
        "mechanism_count_sum": sum(r["public_visible_unique_title_candidates"] for r in mechanism_rows),
        "task_count_sum": sum(r["public_visible_unique_title_candidates"] for r in task_rows),
        "public_available_unique_works": sum(r["public_available_location_identified"] for r in unique_rows),
        "overlap_records_resolved": len(overlap_rows),
        "retrieval_assignment_rows": len(retrieval),
        "retrieval_unique_union_unscreened": len(retrieval_union),
        "checks": {
            "mechanisms_sum_to_core": sum(r["public_visible_unique_title_candidates"] for r in mechanism_rows) == len(unique_rows),
            "subtasks_sum_to_core": sum(r["public_visible_unique_title_candidates"] for r in task_rows) == len(unique_rows),
            "one_primary_mechanism_per_work": len({r["work_key"] for r in unique_rows}) == len(unique_rows),
            "public_available_not_above_visible": all(r["public_available_location_identified"] <= r["public_visible_unique_title_candidates"] for r in mechanism_rows + task_rows),
        },
        "interpretation_warning": "Title-level candidates from a frozen public-index snapshot; not exhaustive global counts and not full-text systematic-review inclusions.",
    }
    (args.output_dir / "clinical_detection_intervention_qc.json").write_text(
        json.dumps(qc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"summary": umbrella[0], "mechanisms": mechanism_rows, "qc": qc["checks"]}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
