#!/usr/bin/env python3
"""Validate bilingual CDI artifacts against the frozen numeric tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "clinical_detection_intervention"
FIG = ROOT / "figures" / "public_evidence"


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


errors: list[str] = []
mechanisms = read_rows("clinical_detection_intervention_mechanism_counts.csv")
subtasks = read_rows("clinical_detection_intervention_subtask_counts.csv")
taxonomy = read_rows("clinical_detection_intervention_taxonomy.csv")
summary = read_rows("clinical_detection_intervention_summary.csv")[0]

visible = sum(int(r["public_visible_unique_title_candidates"]) for r in mechanisms)
available = sum(int(r["public_available_location_identified"]) for r in mechanisms)
since_2021 = sum(int(r["since_2021"]) for r in mechanisms)
expected = {
    "public_visible_unique_title_candidates_comparable_core": visible,
    "public_available_location_identified": available,
    "since_2021": since_2021,
}
for field, value in expected.items():
    if int(float(summary[field])) != value:
        errors.append(f"summary mismatch: {field}")

if sum(int(r["public_visible_unique_title_candidates"]) for r in subtasks) != visible:
    errors.append("subtask counts do not sum to mechanism counts")

required_taxonomy = {
    "mechanism_en", "mechanism_cn", "defining_action_en", "defining_action_cn",
    "terminal_diagnostic_evidence_en", "terminal_diagnostic_evidence_cn",
    "include_if_en", "include_if_cn", "exclude_or_reassign_if_en",
    "exclude_or_reassign_if_cn", "carrier_scope_en", "carrier_scope_cn",
}
if not taxonomy or not required_taxonomy.issubset(taxonomy[0]):
    errors.append("taxonomy is not field-level bilingual")

for report in ["REPORT_CN.md", "REPORT_EN.md", "METHODS_CN.md", "METHODS.md"]:
    if not (OUT / report).exists():
        errors.append(f"missing report: {report}")

for stem in [
    "clinical_detection_intervention_mechanisms",
    "clinical_detection_intervention_11_subtasks",
    "clinical_detection_intervention_12_subtasks",
    "clinical_detection_intervention_13_subtasks",
    "clinical_detection_intervention_annual",
]:
    for lang in ["cn", "en"]:
        for ext in ["svg", "png"]:
            if not (FIG / f"{stem}_{lang}.{ext}").exists():
                errors.append(f"missing figure: {stem}_{lang}.{ext}")

for preview in [
    "clinical_detection_intervention_workbook_preview_cn.png",
    "clinical_detection_intervention_workbook_preview_en.png",
]:
    if not (OUT / preview).exists():
        errors.append(f"missing workbook preview: {preview}")

result = {
    "status": "PASS" if not errors else "FAIL",
    "visible_total": visible,
    "available_total": available,
    "since_2021_total": since_2021,
    "mechanism_rows": len(mechanisms),
    "subtask_rows": len(subtasks),
    "taxonomy_field_level_bilingual": not any("taxonomy" in e for e in errors),
    "errors": errors,
}
(OUT / "bilingual_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=True, indent=2))
raise SystemExit(1 if errors else 0)
