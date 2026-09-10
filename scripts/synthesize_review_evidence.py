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


def build_table(selected: list[dict[str, str]]) -> str:
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{longtable}{L{0.12\textwidth} L{0.17\textwidth} L{0.17\textwidth} L{0.18\textwidth} L{0.12\textwidth} L{0.12\textwidth}}",
        (r"\caption{Selected, identifier-verified evidence anchors for embodied medical detection. "
         r"The denominator is %d selected reports from a 24-report representative evidence seed; this is not an exhaustive included-study table. "
         r"Evidence stage, loop architecture, action risk and execution authority are reviewer-coded. Missing outcomes are not interpreted as zero.}\label{tab:included_evidence}\\" % len(selected)),
        r"\toprule",
        r"Direction & Report (year) & Study setting/design & Observation-conditioned loop & Authority and action risk & Evidence boundary \\",
        r"\midrule",
        r"\endfirsthead",
        r"\multicolumn{6}{l}{\textit{Table \thetable\ continued}}\\",
        r"\toprule",
        r"Direction & Report (year) & Study setting/design & Observation-conditioned loop & Authority and action risk & Evidence boundary \\",
        r"\midrule",
        r"\endhead",
        r"\midrule \multicolumn{6}{r}{Continued on next page}\\ \endfoot",
        r"\bottomrule \endlastfoot",
    ]
    for row in selected:
        report = f"{row['study']} ({row['year']}) \\cite{{{row['citation_key']}}}"
        sample = row["sample_or_setting"]
        if row["sample_string_support"] not in {"all_numeric_strings_found", "no_numeric_tokens", "manual_primary_record_check"}:
            sample = "Numeric denominator withheld pending duplicate source-context check"
        setting = f"{concise(row['evidence_stage'])}; {row['study_design']}. {sample}"
        authority = f"{concise(row['execution_authority'])}; {concise(row['action_risk'])}"
        values = [row["domain"], report, setting, concise(row["loop_architecture"]), authority, row["loop_boundary"]]
        lines.append(" & ".join(latex(value) if "\\cite{" not in value else latex(value.split(" \\cite{")[0]) + " \\cite{" + value.split(" \\cite{")[1] for value in values) + r" \\")
    lines.extend([r"\end{longtable}", r"\endgroup", ""])
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
    context_checks = read_csv(REVIEW / "claim_context_checks.csv")
    sample_overrides = {
        row["study"]: row for row in context_checks
        if row["field"] == "sample_or_setting" and row["status"] == "manual_primary_record_check"
    }
    citations = keyed(read_csv(REVIEW / "main_table_citations.csv"), "study", "citations")
    if set(seeds) != set(codes) or set(seeds) != set(verified) or set(seeds) != set(claim_audit):
        raise SystemExit("Seed, coding, verification and claim-audit study sets must match exactly")

    ledger: list[dict[str, str]] = []
    for index, study in enumerate(seeds, start=1):
        if verified[study]["metadata_status"] != "verified_identifier":
            raise SystemExit(f"Unresolved bibliographic identity: {study}")
        row = {
            "report_id": f"EAD-R{index:03d}",
            **seeds[study],
            **{key: value.strip() for key, value in codes[study].items() if key != "study"},
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
        if study not in seeds or codes[study]["main_table"] != "yes":
            raise SystemExit(f"Invalid main-table selection: {study}")
        selected.append({**next(row for row in ledger if row["study"] == study), **citation})

    if args.manuscript_dir:
        bib = (args.manuscript_dir / "references.bib").read_text(encoding="utf-8")
        bib_keys = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
        missing_keys = sorted({row["citation_key"] for row in selected} - bib_keys)
        if missing_keys:
            raise SystemExit("Missing manuscript citation keys: " + ", ".join(missing_keys))

    write_rows(OUT / "verified_evidence_ledger.csv", ledger)
    for field in ("domain", "evidence_role", "evidence_stage", "loop_architecture", "action_risk", "execution_authority"):
        write_counts(OUT / f"by_{field}.csv", field, ledger)
    missingness = [{"field": field, "missing_reports": sum(not row.get(field, "").strip() for row in ledger), "denominator": len(ledger)} for field in ledger[0]]
    write_rows(OUT / "missingness.csv", missingness)

    table = build_table(selected)
    (OUT / "manuscript_table3.tex").write_text(table, encoding="utf-8")
    if args.manuscript_dir:
        (args.manuscript_dir / "generated_table3.tex").write_text(table, encoding="utf-8")

    summary = {
        "analysis_population": "representative evidence-seed reports",
        "reports": len(ledger),
        "identifier_verified_reports": sum(row["metadata_status"] == "verified_identifier" for row in ledger),
        "main_table_selected_reports": len(selected),
        "direct_or_bounded_or_human_mediated_reports": sum(row["evidence_role"] in {"direct_embodied_diagnostic", "bounded_embodied_acquisition", "human_mediated_embodied_diagnostic"} for row in ledger),
        "technical_precedent_or_nonadaptive_comparator_reports": sum(row["evidence_role"] in {"technical_precedent", "nonadaptive_comparator"} for row in ledger),
        "assisted_sampling_reports": sum(row["evidence_role"] == "assisted_sampling_evidence" for row in ledger),
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

The ledger supports a bounded, qualitative comparison of application direction, evidence stage, loop architecture, action consequence and human authority. Table 3 is explicitly labelled as a selected set of evidence anchors. It must not be described as all included studies or used to estimate publication prevalence.

## Remaining publication gates

The 1,895-record title/abstract queue has not completed duplicate independent screening. Full-text inclusion, report--study--system linkage, design-specific risk-of-bias assessment and second-person extraction checks remain required before a final systematic/scoping-review evidence table or PRISMA flow can replace the selected-anchor table. Numerical results in the seed retain their prior manual article-check status and were deliberately omitted from generated Table 3 until duplicate checking is documented.
"""
    (OUT / "EVIDENCE_SYNTHESIS_READINESS.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
