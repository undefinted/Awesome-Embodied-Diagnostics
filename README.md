# Awesome-Embodied-Diagnostics

A curated, reproducible research repository for **embodied intelligence in medical detection**: diagnostic systems in which decisions change subsequent physical observation, interaction, sampling or testing, and the resulting evidence updates later decisions.

**Live homepage:** [undefinted.github.io/Awesome-Embodied-Diagnostics](https://undefinted.github.io/Awesome-Embodied-Diagnostics/)

[![Validation](https://github.com/undefinted/Awesome-Embodied-Diagnostics/actions/workflows/validate.yml/badge.svg)](https://github.com/undefinted/Awesome-Embodied-Diagnostics/actions/workflows/validate.yml) [![Pages](https://github.com/undefinted/Awesome-Embodied-Diagnostics/actions/workflows/pages.yml/badge.svg)](https://github.com/undefinted/Awesome-Embodied-Diagnostics/actions/workflows/pages.yml)

> **Status:** working evidence-mapping repository. The literature map and quantitative results remain under active validation. Counts are research-workflow outputs, not claims of global coverage or clinical maturity.

> **Frozen evidence snapshot (public-v3, 10 September 2026):** 11,933 source-query records; 6,358 deduplicated screening candidates; 24/24 identifier-verified representative seed reports; 14 selected evidence anchors. These are workflow denominators, not a final included-study corpus, prevalence estimate, or clinical-readiness claim.
>
> **Refresh note:** the repository snapshot is frozen by run ID for reproducibility. Discovery feeds can change as bibliographic indexes update; always cite the run date and preserve raw responses when refreshing.
>
> A separate weekly surveillance update is pending in [PR #16](https://github.com/undefinted/Awesome-Embodied-Diagnostics/pull/16). Its retrieval counts are workload denominators and are intentionally not mixed with the frozen public-v3 evidence snapshot above.

## Contents

- [Scope and inclusion boundary](docs/SCOPE.md)
- [Verified evidence ledger](data/review/evidence_synthesis/verified_evidence_ledger.csv)
- [Row-level performance-table audit](data/review/evidence_synthesis/table_reported_performance_audit.csv)
- [Manuscript denominator map](data/review/evidence_synthesis/manuscript_denominator_map.csv)
- [Search and screening data](data/README.md)
- [Reproducible code](scripts/)
- [Daily Paper Radar](docs/DAILY_PAPER_RADAR.md)
- [Candidate evidence audit](docs/CANDIDATE_EVIDENCE_AUDIT.md)
- [Coverage and source protocol](docs/SEARCH_COVERAGE_PROTOCOL.md)
- [Review research and data plan](docs/REVIEW_RESEARCH_AND_DATA_PLAN.md)
- [Definitive public-source v3 search quality](data/review/search_runs/2026-09-10-public-v3/SEARCH_QUALITY.md)
- [Evidence-synthesis readiness and claim boundaries](data/review/evidence_synthesis/EVIDENCE_SYNTHESIS_READINESS.md)
- [Evidence synthesis codebook](docs/EVIDENCE_SYNTHESIS_CODEBOOK.md)
- [Nature BME table-design benchmark](docs/NBE_TABLE_DESIGN_BENCHMARK.md)
- [Next-round methods status and remaining human gates](docs/NEXT_ROUND_METHODS_STATUS.md)
- [Minimum human actions and AI-work boundary](docs/MINIMUM_HUMAN_ACTIONS.md)
- [Generated results and figures](outputs/)
- [Review/manuscript research package](archive/imported_packages/)
- [Releases and provenance](provenance/)

## Evidence snapshot

The current evidence synthesis is intentionally bounded and report-level. The analysis population is a 24-report representative seed with stable-identifier checks for all 24 records; 14 reports are selected as manuscript evidence anchors. Outcome domains are multi-label, so their counts should not be added together.

| Evidence view | Count | What it supports |
|---|---:|---|
| Source-query records | 11,933 | Retrieval workload in the frozen public-v3 run |
| Deduplicated screening candidates | 6,358 | Title/abstract screening workload; not included studies |
| Representative seed reports | 24 | Bounded descriptive evidence synthesis |
| Selected manuscript anchors | 14 | Explicitly selected comparison rows |
| Technical/acquisition outcomes | 19/24 | Most commonly coded outcome domain in the seed |
| Diagnostic-performance outcomes | 9/24 | Diagnostic endpoint reporting in the seed |
| Patient-benefit stage (T4) | 0/24 | No seed report demonstrated patient benefit |

Source-linked breakdowns are available in [search quality](data/review/search_runs/2026-09-10-public-v3/SEARCH_QUALITY.md), [seed summary](outputs/review_evidence/summary.json), [evidence synthesis readiness](data/review/evidence_synthesis/EVIDENCE_SYNTHESIS_READINESS.md), [outcome categories](data/review/evidence_synthesis/by_outcome_category.csv), [translation stages](data/review/evidence_synthesis/by_translation_stage.csv), and the [selected-anchor table](data/review/evidence_synthesis/manuscript_table3.tex).

## Manuscript crosswalk

- **Main evidence table:** 31 report-level rows, including 14 selected anchors from the 24-report seed plus identifier-verified clinical, laboratory and response-based rows; it is reviewer-coded and not a final systematic-review corpus. The [row-level audit](data/review/evidence_synthesis/table_reported_performance_audit.csv) records the study design, denominator, outcome fields and source URL for every row.
- **Outcome summary:** 19/24 technical or acquisition, 9/24 diagnostic performance, 7/24 analytical validity, 7/24 workflow or efficiency, 4/24 safety, 4/24 human factors, and 0/24 patient-benefit outcomes.
- **Latency histogram / Supplementary Fig. 3:** the current manuscript plots 13 source-linked observations from 10 reports; interval-only interface statements and non-response handling times are excluded. The auditable row-level data are in the [latency ledger](data/review/evidence_synthesis/latency_ledger.csv). The distribution is descriptive and does not pool heterogeneous endpoints.
- **Figure 4 resource panel:** 12 representative platforms and interaction datasets are shown from a 44-entry named resource/version audit; the panel is illustrative rather than an exhaustive inventory.
- **Denominator boundary:** the manuscript's historical 41-report catalogue and this public-v3 24-report verified seed are separate denominators and must not be added together. The [denominator map](data/review/evidence_synthesis/manuscript_denominator_map.csv) records the relationship among all five quantitative evidence products.

## Working taxonomy

| Evidence-generation mechanism | Diagnostic action | Typical tasks |
|---|---|---|
| Active observational sensing | Repositions or controls a sensor to acquire new evidence | Robotic ultrasound, endoscopy, capsule inspection, OCT, auscultation |
| Response-based interactive diagnosis | Applies a controlled stimulus and measures the response | Palpation, stiffness mapping, provocation tests, stimulation-response mapping |
| Sample-based interactive diagnosis | Acquires tissue or fluid for downstream analysis | Biopsy, blood draw, swab and capsule sampling |

The taxonomy is task-level and multi-label. Static classification, report generation and fixed trajectories without feedback are not treated as complete embodied diagnostic loops.

## Reproduce

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_repository.py
python scripts/screen_review_candidates.py --run-id 2026-09-10-public-v3
python scripts/validate_review_workflow.py --run-id 2026-09-10-public-v3
python scripts/verify_evidence_sources.py
python scripts/audit_seed_claims.py
python scripts/benchmark_nbe_review_tables.py
python scripts/synthesize_review_evidence.py --manuscript-dir /path/to/overleaf-manuscript

# Windows PowerShell example:
python scripts/synthesize_review_evidence.py --manuscript-dir C:\\path\\to\\overleaf-manuscript
```

Existing analysis scripts and exact data snapshots are preserved. Networked retrieval will change as bibliographic indexes update; freeze the query date and retain raw responses when refreshing results.

The 10 September 2026 public-v3 retrospective run retrieved 11,933 source-query records and produced 6,358 deduplicated **screening candidates** across PubMed, Europe PMC and arXiv. All 84 registered source-query pairs completed with returned counts matching source-reported totals and no configured result-cap truncation. These remain workload denominators, not included studies or an estimate of field size.

The manuscript evidence seed currently contains 24 representative reports with 24/24 bibliographic identities re-resolved through stable identifiers. Public-v3 retrieved 21/24 of this convenience set and 17/17 seeds coded as direct, bounded, human-mediated or assisted-sampling evidence. The generated manuscript table uses 14 selected evidence anchors. It is not the final included-study corpus. All 6,354 non-quarantined candidates are present in the title/abstract eligibility ledger; the 1,747 high/possible-signal subset is an ordering aid only. Provenance-preserving AI assessment, source-linked full-text review and accountable-author confirmation remain incomplete.

## Cite this repository

For reproducibility, cite the repository URL together with the frozen run identifier (`public-v3`, 10 September 2026) and the exact evidence artifact used. Preserve the run date and source ledger when reusing the quantitative summaries.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New papers should include a stable DOI, PubMed/Europe PMC, arXiv or publisher identifier; an evidence-generation label; evidence stage; and a concise statement of whether a physical feedback loop is actually demonstrated.

## Copyright and release policy

Bibliographic metadata, original curation and code can be prepared for open release after licence review. Publisher PDFs and other third-party full texts are kept in `local_only/`, ignored by Git, and must not be redistributed without permission. Provenance, author attribution and reuse terms remain under review.
