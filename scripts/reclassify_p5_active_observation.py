#!/usr/bin/env python3
"""Reclassify frozen P5 candidates by explicit clinical examination procedure.

The primary axis is a mutually exclusive, title-verifiable clinical procedure.
Modality and carrier remain independent multi-label attributes. Records without
an explicit procedure in the title are retained as T9 (unresolved/cross-cutting)
instead of inheriting a clinical label from the retrieval query that found them.
This is a conservative title-level map, not a full-text systematic-review result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


TASKS = {
    "T1": ("超声检查与主动扫查", "Ultrasound examination and active scanning"),
    "T2": ("胃肠柔性内镜检查", "Flexible gastrointestinal endoscopic examination"),
    "T3": ("主动或磁控胶囊内镜检查", "Active or magnetically controlled capsule endoscopy"),
    "T4": ("支气管镜观察与导航", "Bronchoscopic observation and navigation"),
    "T5": ("眼科主动对准与成像", "Actively aligned ophthalmic examination"),
    "T6": ("皮肤与暴露组织表面成像", "Cutaneous and exposed-tissue surface imaging"),
    "T7": ("主动听诊与声学检查", "Active auscultation and acoustic examination"),
    "T8": ("耳鼻咽喉与口腔腔道检查", "ENT and oral-cavity examination"),
    "T9": ("临床任务未定或跨任务采集技术", "Task-unresolved or cross-cutting acquisition technology"),
}

# Ordered clinical-procedure rules. Each rule requires title evidence. Generic
# words such as "eye", "gaze", "kidney", "lung nodule" and "endoscopic robot"
# are deliberately absent: they previously generated demonstrable false labels.
PROCEDURE_RULES = [
    ("T3", r"\b(capsule endoscop|capsule robot|robotic capsule|magnetic(?:ally)? (?:controlled )?capsule|active capsule|capsular endoscop)"),
    ("T4", r"\b(bronchoscop|endobronch)"),
    ("T2", r"\b(gastrointestinal|gastro-intestinal|gastroscop|colonoscop|colonic|colon\b|human intestine|intragastric|gastric|esophag|duoden|small bowel|large bowel|colorectal|biliary|upper gi|lower gi)"),
    ("T5", r"\b(ophthalm|ocular|fundus|retina|retinal|cornea|corneal|slit.?lamp|nystagmus|schlemm|moving eyes|eye disease)"),
    ("T6", r"\b(dermat|cutaneous|in vivo skin|skin (?:imag|evaluat|lesion|disease|surface|scan|mapping)|wound|(?:skin|diabetic|pressure|venous) ulcer|exposed tissue|renal surface|donor kidney assessment|kidney imaging for pre.transplant|pre.transplant kidney monitoring|thyroid gland endomicroscop|brain micro.vascular|spinal cord tumor|ex vivo (?:tissue|organ)|intraoperative tissue surface)"),
    ("T7", r"\b(auscultat|stethoscop|heart sound|lung sound)"),
    ("T8", r"\b(otoscop|ear examination|tympanic|laryngoscop|pharyng|oral cavity|oral examination|malleus|incus)"),
    ("T1", r"\b(ultrasound|sonograph)"),
]

NONMEDICAL_EXCLUDE = re.compile(
    r"\b(textile|corn leaf|crop|plant phenotyp|UAV|unmanned aerial|reconnaissance|BRDF|"
    r"scanning tunneling spectroscopy|industrial inline|remote sensing|robotic grasping system)\b",
    re.I,
)
THERAPY_NONDIAGNOSTIC_EXCLUDE = re.compile(
    r"\b(posterior capsule polishing|subretinal drug delivery|vascular anastomosis|"
    r"radical prostatectomy specimens?|robotic prostatectomy|fiducial marker implantation|"
    r"fiducial placement|radiosurgery system tracking|robotic stereotactic radiosurgery|"
    r"electromagnetic navigational bronchoscopy and robotic.assisted thoracic surgery|"
    r"ablation|resection|suturing)\b",
    re.I,
)
SECONDARY_REVIEW_EXCLUDE = re.compile(
    r"\b(review|survey|perspective|perspectives|state.of.the.art)\b|"
    r"robotics and smart instruments for translating|^discussion to:|"
    r"thoracic surgery applications of robotic bronchoscopy",
    re.I,
)
OTHER_DIAGNOSTIC_PARADIGM_EXCLUDE = re.compile(
    r"\b(capsule robot for liquid sampling|capsule robot.*sampling)\b",
    re.I,
)

MODALITY_RULES = [
    ("ultrasound", r"\b(ultrasound|sonograph)"),
    ("OCT", r"\b(optical coherence tomography|OCT)\b"),
    ("Raman_DRS_spectroscopy", r"\b(raman|diffuse reflectance|DRS|spectroscop)"),
    ("hyperspectral_multispectral", r"\b(hyperspectral|multispectral|spectral imaging)"),
    ("confocal_endomicroscopy", r"\b(confocal|endomicroscop)"),
    ("photoacoustic", r"\b(photoacoustic|optoacoustic)"),
    ("white_light_RGB_video", r"\b(white.?light|RGB|video endoscop|color imag)"),
    ("acoustic_physiological_sound", r"\b(auscultat|stethoscop|heart sound|lung sound)"),
    ("other_optical", r"\b(fluorescen|laser scanning|optical scanning|optical imaging|terahertz)"),
]

CARRIER_RULES = [
    ("robotic_manipulator_arm", r"\b(robotic arm|robot arm|manipulator|cobot|collaborative robot|[467][ -]?DOF robot)"),
    ("dedicated_mechatronic_scanner", r"\b(scanner robot|scanning robot|motorized|mechatronic|gantry|probe positioner|robotic scanner)"),
    ("flexible_continuum_endoscope", r"\b(flexible endoscop|continuum robot|soft robot|cable.driven|tendon.driven|robotic endoscop)"),
    ("magnetic_active_capsule", r"\b(magnetic capsule|active capsule|capsule robot|self.propell)"),
    ("mobile_bedside_body_mounted", r"\b(mobile robot|bedside|body.mounted|wearable robot)"),
]


def norm_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"[^\w]+", "", value, flags=re.UNICODE)


def work_key(row: dict[str, str]) -> str:
    doi = (row.get("doi") or "").strip().casefold()
    if doi:
        doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", doi)
        return f"doi:{doi}"
    return f"title:{norm_title(row.get('title', ''))}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def split_pipe(values: list[str]) -> str:
    items = set()
    for value in values:
        for item in (value or "").split(" | "):
            if item.strip():
                items.add(item.strip())
    return " | ".join(sorted(items))


def classify_primary(title: str, source_codes: set[str]) -> tuple[str, str, str]:
    text = title.casefold()
    site_hits = [(code, pattern) for code, pattern in PROCEDURE_RULES if re.search(pattern, text, re.I)]
    distinct = []
    for code, _ in site_hits:
        if code not in distinct:
            distinct.append(code)

    # A specific access/anatomy procedure takes precedence when the only other
    # hit is ultrasound, which is simultaneously a sensing modality. This keeps
    # e.g. endobronchial ultrasound under bronchoscopy with an ultrasound tag.
    if distinct:
        specific = [code for code in distinct if code != "T1"]
        if "T1" in distinct and len(specific) == 1:
            return specific[0], f"explicit_route_over_ultrasound_modality:{specific[0]}", "high"
        if "T3" in distinct and set(distinct).issubset({"T2", "T3"}):
            return "T3", "explicit_capsule_route_over_gastrointestinal_site:T3", "high"

        # The first ordered explicit procedure wins. Multiple genuinely
        # distinct procedure hits are retained for manual inspection.
        chosen = distinct[0]
        confidence = "high" if len(distinct) == 1 else "medium"
        return chosen, f"explicit_title_procedure:{chosen}", confidence

    # Retrieval buckets document search provenance, not the clinical procedure.
    # They must never be converted into a high-confidence task assignment.
    return "T9", "no_explicit_clinical_procedure_in_title", "low"


def classify_tags(title: str, primary: str) -> tuple[list[str], list[str]]:
    modalities = [tag for tag, pattern in MODALITY_RULES if re.search(pattern, title, re.I)]
    if not modalities:
        fallback = {
            "T2": "endoscopic_imaging_unspecified",
            "T3": "capsule_endoscopic_imaging_unspecified",
            "T4": "bronchoscopic_imaging_unspecified",
            "T5": "ophthalmic_imaging_unspecified",
            "T6": "surface_imaging_unspecified",
            "T7": "acoustic_physiological_sound",
            "T8": "cavity_visual_imaging_unspecified",
            "T9": "active_sensing_modality_unspecified",
        }
        if primary == "T1":
            modalities = ["ultrasound"]
        else:
            modalities = [fallback.get(primary, "unspecified")]

    carriers = [tag for tag, pattern in CARRIER_RULES if re.search(pattern, title, re.I)]
    if not carriers:
        carriers = [{
            "T2": "robotic_endoscope_unspecified",
            "T3": "magnetic_active_capsule",
            "T4": "robotic_bronchoscope_unspecified",
        }.get(primary, "robotic_mechatronic_carrier_unspecified")]
    return sorted(set(modalities)), sorted(set(carriers))


def scope_decision(title: str) -> tuple[str, str]:
    if NONMEDICAL_EXCLUDE.search(title):
        return "excluded_title", "nonmedical_or_industrial_application"
    if THERAPY_NONDIAGNOSTIC_EXCLUDE.search(title):
        return "excluded_title", "therapy_or_nondiagnostic_action"
    if SECONDARY_REVIEW_EXCLUDE.search(title):
        return "excluded_title", "secondary_review_or_perspective"
    if OTHER_DIAGNOSTIC_PARADIGM_EXCLUDE.search(title):
        return "excluded_title", "belongs_to_sample_based_interaction"
    return "included_title_candidate", "passes_title_scope_rules"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.records.open("r", encoding="utf-8-sig", newline="") as handle:
        assignments = list(csv.DictReader(handle))

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        grouped[work_key(row)].append(row)

    records = []
    counts = {code: Counter() for code in TASKS}
    matrix: dict[tuple[str, str], Counter] = defaultdict(Counter)
    carrier_counts: Counter = Counter()
    audit_queue = []
    excluded_records = []

    for key, rows in sorted(grouped.items()):
        first = rows[0]
        title = first.get("title", "").strip()
        source_codes = {r["task_code"] for r in rows}
        primary, rule, confidence = classify_primary(title, source_codes)
        modalities, carriers = classify_tags(title, primary)
        scope_status, exclusion_reason = scope_decision(title)
        available = any((r.get("public_available") or "").strip().lower() in {"1", "true", "yes"} for r in rows)
        try:
            year = int(first.get("year") or 0)
        except ValueError:
            year = 0
        review_status = "priority_manual_review" if confidence != "high" or len(source_codes) > 1 else "title_rule_classified"
        if scope_status == "excluded_title":
            review_status = "excluded_by_title_rule_reviewable"

        record = {
            "work_key": key,
            "title": title,
            "year": year or "",
            "doi": first.get("doi", ""),
            "source_task_codes": "+".join(sorted(source_codes)),
            "source_tasks": " | ".join(sorted({r["task"] for r in rows})),
            "sources": split_pipe([r.get("sources", "") for r in rows]),
            "record_urls": split_pipe([r.get("record_urls", "") for r in rows]),
            "public_visible": 1,
            "public_available": int(available),
            "public_urls": split_pipe([r.get("public_urls", "") for r in rows]),
            "primary_task_code": primary,
            "primary_task_cn": TASKS[primary][0],
            "primary_task_en": TASKS[primary][1],
            "primary_assignment_rule": rule,
            "classification_confidence": confidence,
            "modality_tags": ";".join(modalities),
            "carrier_tags": ";".join(carriers),
            "review_status": review_status,
            "scope_status": scope_status,
            "exclusion_reason": exclusion_reason,
            "evidence_level": "title-level candidate; full-text inclusion not completed",
        }
        records.append(record)
        if scope_status == "excluded_title":
            excluded_records.append(record)
            continue
        counts[primary]["public_visible"] += 1
        counts[primary]["public_available"] += int(available)
        counts[primary]["since_2021"] += int(year >= 2021)
        for modality in modalities:
            matrix[(primary, modality)]["public_visible"] += 1
            matrix[(primary, modality)]["public_available"] += int(available)
        for carrier in carriers:
            carrier_counts[(carrier, "public_visible")] += 1
            carrier_counts[(carrier, "public_available")] += int(available)
        if review_status == "priority_manual_review":
            audit_queue.append(record)

    record_fields = list(records[0])
    for filename, rows_to_write in [
        ("p5_reclassified_unique_records_2026-08-14.csv", records),
        ("p5_reclassification_manual_audit_queue_2026-08-14.csv", audit_queue),
        ("p5_reclassification_excluded_records_2026-08-14.csv", excluded_records),
    ]:
        with (args.output_dir / filename).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=record_fields)
            writer.writeheader()
            writer.writerows(rows_to_write)

    count_rows = []
    for code, (cn, en) in TASKS.items():
        visible = counts[code]["public_visible"]
        available = counts[code]["public_available"]
        count_rows.append({
            "primary_task_code": code,
            "primary_task_cn": cn,
            "primary_task_en": en,
            "public_visible_unique_title_candidates": visible,
            "public_available_location_identified": available,
            "public_available_share": round(available / visible, 4) if visible else 0,
            "since_2021": counts[code]["since_2021"],
            "status": "deterministic title-level reclassification; manual full-text screening pending",
        })
    with (args.output_dir / "p5_reclassified_task_counts_2026-08-14.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(count_rows[0]))
        writer.writeheader()
        writer.writerows(count_rows)

    matrix_rows = []
    for (task, modality), value in sorted(matrix.items()):
        matrix_rows.append({
            "primary_task_code": task,
            "primary_task_cn": TASKS[task][0],
            "modality_tag": modality,
            "public_visible_unique_title_candidates": value["public_visible"],
            "public_available_location_identified": value["public_available"],
        })
    with (args.output_dir / "p5_task_modality_matrix_2026-08-14.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(matrix_rows[0]))
        writer.writeheader()
        writer.writerows(matrix_rows)

    carrier_rows = []
    for carrier in sorted({key[0] for key in carrier_counts}):
        carrier_rows.append({
            "carrier_tag": carrier,
            "public_visible_unique_title_candidates": carrier_counts[(carrier, "public_visible")],
            "public_available_location_identified": carrier_counts[(carrier, "public_available")],
            "interpretation": "title-derived or task-default tag; detailed hardware audit pending",
        })
    with (args.output_dir / "p5_carrier_tag_counts_2026-08-14.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(carrier_rows[0]))
        writer.writeheader()
        writer.writerows(carrier_rows)

    qc = {
        "classification_rule_version": "p5-clinical-procedure-title-explicit-v2",
        "input": str(args.records),
        "input_sha256": sha256(args.records),
        "task_assignment_rows": len(assignments),
        "unique_works": len(records),
        "included_title_candidates": len(records) - len(excluded_records),
        "excluded_by_title_scope_rules": len(excluded_records),
        "visible_count_sum": sum(r["public_visible_unique_title_candidates"] for r in count_rows),
        "public_available_unique_works": sum(r["public_available_location_identified"] for r in count_rows),
        "task_resolved_title_candidates": sum(counts[c]["public_visible"] for c in TASKS if c != "T9"),
        "task_resolved_public_available": sum(counts[c]["public_available"] for c in TASKS if c != "T9"),
        "multi_bucket_unique_works": sum("+" in r["source_task_codes"] for r in records),
        "priority_manual_review": len(audit_queue),
        "task_unresolved_cross_cutting_T9": counts["T9"]["public_visible"],
        "task_unresolved_cross_cutting_T9_public_available": counts["T9"]["public_available"],
        "low_confidence_included": sum(r["classification_confidence"] == "low" and r["scope_status"] == "included_title_candidate" for r in records),
        "medium_confidence_included": sum(r["classification_confidence"] == "medium" and r["scope_status"] == "included_title_candidate" for r in records),
        "high_confidence_included": sum(r["classification_confidence"] == "high" and r["scope_status"] == "included_title_candidate" for r in records),
        "counting_unit": "unique work after DOI-first/title-second deduplication",
        "scope_warning": "Title-level reclassified candidates, not systematic-review full-text inclusions.",
    }
    (args.output_dir / "p5_reclassification_qc_2026-08-14.json").write_text(
        json.dumps(qc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(qc, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
