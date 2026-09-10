"""Join reviewed evidence records, audit denominators, and generate manuscript Table 3.

The script intentionally analyses the representative evidence seed only. It
refuses to generate the table when a bibliographic identity is unresolved or a
selected row lacks an explicit reviewer code and manuscript citation key.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data" / "review"
OUT = REVIEW / "evidence_synthesis"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def keyed(rows: list[dict[str, str]], field: str, label: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get(field, "").strip()
        if not key:
            raise SystemExit(f"{label}: blank {field}")
        if key in result:
            raise SystemExit(f"{label}: duplicate {field}: {key}")
        result[key] = row
    return result


def latex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "±": r"$\pm$", "×": r"$\times$", "–": "--", "—": "--",
    }
    return "".join(replacements.get(char, char) for char in value)


def concise(value: str) -> str:
    return value.replace("_", " ").strip()


def denominator_summary(row: dict[str, str]) -> str:
    fields = (
        ("participants", row["participant_n"]),
        ("measures", row["specimen_or_measurement_n"]),
        ("procedures", row["procedure_n"]),
        ("development data", row["development_data"]),
    )
    reported = [f"{label}: {value}" for label, value in fields if value and value != "NR"]
    return "; ".join(reported) if reported else "NR"


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_counts(path: Path, field: str, rows: list[dict[str, str]]) -> None:
    counts = Counter(row[field] or "not_reported" for row in rows)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[field, "report_count", "denominator", "analysis_population"])
        writer.writeheader()
        for key, count in sorted(counts.items()):
            writer.writerow({field: key, "report_count": count, "denominator": len(rows), "analysis_population": "representative evidence-seed reports"})


def write_multivalue_counts(path: Path, field: str, rows: list[dict[str, str]], expected: set[str] | None = None) -> None:
    counts: Counter[str] = Counter()
    for row in rows:
        values = [value.strip() for value in row[field].split(";") if value.strip()]
        counts.update(values or ["not_reported"])
    for value in expected or set():
        counts.setdefault(value, 0)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[field, "reports_with_domain", "report_denominator", "analysis_population"])
        writer.writeheader()
        for key, count in sorted(counts.items()):
            writer.writerow({field: key, "reports_with_domain": count, "report_denominator": len(rows), "analysis_population": "representative evidence-seed reports; domains are multi-label"})


def write_gap_matrix(path: Path, rows: list[dict[str, str]]) -> None:
    stages = ["T0", "T1", "T2", "T3", "T4"]
    domains = sorted({row["domain"] for row in rows})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["domain", *stages, "report_total", "analysis_population"])
        writer.writeheader()
        for domain in domains:
            selected = [row for row in rows if row["domain"] == domain]
            counts = Counter(row["translation_stage"].split()[0] for row in selected)
            writer.writerow({"domain": domain, **{stage: counts[stage] for stage in stages}, "report_total": len(selected), "analysis_population": "representative evidence-seed reports"})


def build_table(selected: list[dict[str, str]]) -> str:
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{longtable}{L{0.15\textwidth} L{0.13\textwidth} L{0.17\textwidth} L{0.17\textwidth} L{0.12\textwidth} L{0.14\textwidth}}",
        (r"\caption{Selected, identifier-verified evidence anchors for embodied medical detection. "
         r"The denominator is %d selected reports from a 24-report representative evidence seed; this is not an exhaustive included-study table. "
         r"The table follows a translational comparison structure: platform, population or material, design and denominator, adaptive function, authority boundary and reported outcome domains. Missing data are marked NR and are not interpreted as zero.}\label{tab:included_evidence}\\" % len(selected)),
        r"\toprule",
        r"Platform / task & Population / material & Evidence stage, design and denominator & Adaptive diagnostic function & Authority / action boundary & Reported outcome domains / limitation \\",
        r"\midrule",
        r"\endfirsthead",
        r"\multicolumn{6}{l}{\textit{Table \thetable\ continued}}\\",
        r"\toprule",
        r"Platform / task & Population / material & Evidence stage, design and denominator & Adaptive diagnostic function & Authority / action boundary & Reported outcome domains / limitation \\",
        r"\midrule",
        r"\endhead",
        r"\midrule \multicolumn{6}{r}{Continued on next page}\\ \endfoot",
        r"\bottomrule \endlastfoot",
    ]
    current_domain = ""
    for row in selected:
        if row["domain"] != current_domain:
            current_domain = row["domain"]
            lines.append(r"\addlinespace[2pt]\multicolumn{6}{l}{\textbf{" + latex(current_domain) + r"}}\\")
        report = f"{row['display_label']} ({row['year']}) \\cite{{{row['citation_key']}}}"
        denominators = denominator_summary(row)
        if row["sample_string_support"] not in {"all_numeric_strings_found", "no_numeric_tokens", "manual_primary_record_check"}:
            denominators = "NR pending duplicate source-context check"
        design = f"{row['translation_stage']}; {row['study_design']}; {denominators}"
        adaptive = f"{concise(row['loop_architecture'])}: {row['rationale']}"
        authority = f"{concise(row['execution_authority'])}; {concise(row['action_risk'])}"
        outcomes = f"{row['outcome_domains']}; limitation: {row['loop_boundary']}"
        values = [report, row["population_or_material"], design, adaptive, authority, outcomes]
        lines.append(" & ".join(latex(value) if "\\cite{" not in value else latex(value.split(" \\cite{")[0]) + " \\cite{" + value.split(" \\cite{")[1] for value in values) + r" \\")
    lines.extend([
        r"\end{longtable}",
        r"\noindent\footnotesize\textit{Coding and evidence stages:} Adaptive functions, outcome domains and stages are reviewer-coded from the cited primary reports and have not yet undergone duplicate extraction. NR, not reported in the current verified ledger; T0, transferable technical precedent; T1, bench or preclinical validation; T2, human feasibility or technical validation; T3, prospective comparative or clinical-performance evidence; T4, demonstrated patient benefit. Stages describe what was evaluated, not study quality or risk of bias.",
        r"\endgroup", "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript-dir", type=Path)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    seeds = keyed(read_csv(REVIEW / "manuscript_evidence_seed.csv"), "study", "seed")
    codes = keyed(read_csv(REVIEW / "evidence_coding.csv"), "study", "coding")
    verified = keyed(read_csv(OUT / "source_verification.csv"), "study", "verification")
    claim_audit = keyed(read_csv(OUT / "claim_string_audit.csv"), "study", "claim audit")
    characteristics = keyed(read_csv(REVIEW / "evidence_characteristics.csv"), "study", "characteristics")
    outcome_categories = keyed(read_csv(REVIEW / "outcome_category_coding.csv"), "study", "outcome categories")
    context_checks = read_csv(REVIEW / "claim_context_checks.csv")
    sample_overrides = {
        row["study"]: row for row in context_checks
        if row["field"] == "sample_or_setting" and row["status"] == "manual_primary_record_check"
    }
    citations = keyed(read_csv(REVIEW / "main_table_citations.csv"), "study", "citations")
    if any(set(seeds) != set(dataset) for dataset in (codes, verified, claim_audit, characteristics, outcome_categories)):
        raise SystemExit("All reviewer-coded, verification and claim-audit study sets must match the seed exactly")

    ledger: list[dict[str, str]] = []
    for index, study in enumerate(seeds, start=1):
        if verified[study]["metadata_status"] != "verified_identifier":
            raise SystemExit(f"Unresolved bibliographic identity: {study}")
        row = {
            "report_id": f"EAD-R{index:03d}",
            **seeds[study],
            **{key: value.strip() for key, value in codes[study].items() if key != "study"},
            **{key: value.strip() for key, value in characteristics[study].items() if key not in {"study", "main_table"}},
            "outcome_categories": outcome_categories[study]["outcome_categories"],
            "resolved_title": verified[study]["resolved_title"],
            "resolved_identifier": verified[study]["resolved_identifier"],
            "metadata_status": verified[study]["metadata_status"],
            "metadata_source_url": verified[study]["source_url"],
            "metadata_response_sha256": verified[study]["response_sha256"],
            "metadata_checked_at": verified[study]["checked_at"],
            "sample_string_support": "manual_primary_record_check" if study in sample_overrides else claim_audit[study]["sample_string_support"],
            "result_string_support": claim_audit[study]["result_string_support"],
            "claim_audit_source_url": claim_audit[study]["source_url"],
            "claim_audit_response_sha256": claim_audit[study]["response_sha256"],
            "claim_status": "prior_manual_article_check; not independently duplicated",
        }
        ledger.append(row)

    selected = []
    for study, citation in citations.items():
        if study not in seeds or codes[study]["main_table"] != "yes" or characteristics[study]["main_table"] != "yes":
            raise SystemExit(f"Invalid main-table selection: {study}")
        selected.append({**next(row for row in ledger if row["study"] == study), **citation})

    if args.manuscript_dir:
        bib = (args.manuscript_dir / "references.bib").read_text(encoding="utf-8")
        bib_keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
        missing_keys = sorted({row["citation_key"] for row in selected} - bib_keys)
        if missing_keys:
            raise SystemExit("Missing manuscript citation keys: " + ", ".join(missing_keys))

    write_rows(OUT / "verified_evidence_ledger.csv", ledger)
    for field in ("domain", "evidence_role", "evidence_stage", "translation_stage", "loop_architecture", "action_risk", "execution_authority"):
        write_counts(OUT / f"by_{field}.csv", field, ledger)
    write_multivalue_counts(
        OUT / "by_outcome_category.csv",
        "outcome_categories",
        ledger,
        expected={
            "technical_acquisition", "diagnostic_performance", "analytical_validity",
            "safety", "workflow_efficiency", "human_factors",
            "clinical_utility_patient_outcomes",
        },
    )
    write_gap_matrix(OUT / "evidence_gap_matrix.csv", ledger)
    outcome_counts = Counter(
        value.strip()
        for row in ledger
        for value in row["outcome_categories"].split(";")
        if value.strip()
    )
    missingness = [{"field": field, "missing_reports": sum(not row.get(field, "").strip() for row in ledger), "denominator": len(ledger)} for field in ledger[0]]
    write_rows(OUT / "missingness.csv", missingness)

    table = build_table(selected)
    (OUT / "manuscript_table3.tex").write_text(table, encoding="utf-8")
    evidence_summary = (
        "In the 24-report representative evidence seed, technical or acquisition outcomes were coded in "
        f"{outcome_counts['technical_acquisition']} reports, diagnostic-performance outcomes in "
        f"{outcome_counts['diagnostic_performance']}, analytical-validity outcomes in "
        f"{outcome_counts['analytical_validity']}, workflow or efficiency outcomes in "
        f"{outcome_counts['workflow_efficiency']}, safety outcomes in {outcome_counts['safety']}, "
        f"and human-factors outcomes in {outcome_counts['human_factors']}. No seed report reached the "
        "T4 patient-benefit stage. These report-level, multi-label counts diagnose extraction and "
        "translation gaps within the representative seed only; they do not estimate field prevalence "
        "or comparative effectiveness.\n"
    )
    (OUT / "manuscript_evidence_summary.tex").write_text(evidence_summary, encoding="utf-8")
    if args.manuscript_dir:
        (args.manuscript_dir / "generated_table3.tex").write_text(table, encoding="utf-8")
        (args.manuscript_dir / "generated_evidence_summary.tex").write_text(evidence_summary, encoding="utf-8")

    summary = {
        "analysis_population": "representative evidence-seed reports",
        "reports": len(ledger),
        "identifier_verified_reports": sum(row["metadata_status"] == "verified_identifier" for row in ledger),
        "main_table_selected_reports": len(selected),
        "direct_or_bounded_or_human_mediated_reports": sum(row["evidence_role"] in {"direct_embodied_diagnostic", "bounded_embodied_acquisition", "human_mediated_embodied_diagnostic"} for row in ledger),
        "technical_precedent_or_nonadaptive_comparator_reports": sum(row["evidence_role"] in {"technical_precedent", "nonadaptive_comparator"} for row in ledger),
        "assisted_sampling_reports": sum(row["evidence_role"] == "assisted_sampling_evidence" for row in ledger),
        "T4_patient_benefit_reports": sum(row["translation_stage"].startswith("T4") for row in ledger),
        "claim_boundary": "Descriptive counts characterize the 24-report representative seed, not field prevalence or a final systematic-review corpus.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "synthesis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report = f"""# Evidence Synthesis Readiness

## Audited denominator

- Analysis population: **{len(ledger)} representative evidence-seed reports**.
- Bibliographic identities verified by stable identifier: **{summary['identifier_verified_reports']}/{len(ledger)}**.
- Rows selected for manuscript Table 3: **{len(selected)}**.
- Unit of counting: report. These counts are not counts of independent systems, experiments or patients.

## Permitted use

The ledger supports a bounded, qualitative comparison of application direction, evidence stage, loop architecture, action consequence, human authority and reported outcome domains. Table 3 is explicitly labelled as a selected set of evidence anchors. It uses concise platform labels, separately labelled denominator types, explicit NR values and a translational stage that describes what was evaluated rather than study quality. Adaptive functions, outcome domains and stages are reviewer-coded and have not yet undergone duplicate extraction. The table must not be described as all included studies or used to estimate publication prevalence.

## Current evidence gaps in the representative seed

- Reports reaching T4 demonstrated patient benefit: **{summary['T4_patient_benefit_reports']}/{len(ledger)}**.
- Reports coding technical or acquisition outcomes: **{outcome_counts['technical_acquisition']}/{len(ledger)}**.
- Reports coding diagnostic-performance outcomes: **{outcome_counts['diagnostic_performance']}/{len(ledger)}**.
- Reports coding safety outcomes: **{outcome_counts['safety']}/{len(ledger)}**.
- Reports coding human-factors outcomes: **{outcome_counts['human_factors']}/{len(ledger)}**.

Outcome domains are multi-label, so these rows are not mutually exclusive and must not be summed. They describe the representative seed only.

## Remaining publication gates

The 1,895-record title/abstract queue has not completed duplicate independent screening. Full-text inclusion, report--study--system linkage, design-specific risk-of-bias assessment and second-person extraction checks remain required before a final systematic/scoping-review evidence table or PRISMA flow can replace the selected-anchor table. Numerical results in the seed retain their prior manual article-check status and were deliberately omitted from generated Table 3 until duplicate checking is documented.
"""
    (OUT / "EVIDENCE_SYNTHESIS_READINESS.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
