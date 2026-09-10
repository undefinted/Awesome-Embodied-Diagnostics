# Awesome-Embodied-Diagnostics

A curated, reproducible research repository for **embodied intelligence in medical detection**: diagnostic systems in which decisions change subsequent physical observation, interaction, sampling or testing, and the resulting evidence updates later decisions.

**Live homepage:** [undefinted.github.io/Awesome-Embodied-Diagnostics](https://undefinted.github.io/Awesome-Embodied-Diagnostics/)

> **Status:** working evidence-mapping repository. The literature map and quantitative results remain under active validation. Counts are research-workflow outputs, not claims of global coverage or clinical maturity.

## Contents

- [Scope and inclusion boundary](docs/SCOPE.md)
- [Curated literature](literature/README.md)
- [Search and screening data](data/README.md)
- [Reproducible code](scripts/)
- [Daily Paper Radar](docs/DAILY_PAPER_RADAR.md)
- [Candidate evidence audit](docs/CANDIDATE_EVIDENCE_AUDIT.md)
- [Coverage and source protocol](docs/SEARCH_COVERAGE_PROTOCOL.md)
- [Review research and data plan](docs/REVIEW_RESEARCH_AND_DATA_PLAN.md)
- [Frozen public-source search quality](data/review/search_runs/2026-09-10/SEARCH_QUALITY.md)
- [Evidence-synthesis readiness and claim boundaries](data/review/evidence_synthesis/EVIDENCE_SYNTHESIS_READINESS.md)
- [Evidence synthesis codebook](docs/EVIDENCE_SYNTHESIS_CODEBOOK.md)
- [Generated results and figures](outputs/)
- [Review/manuscript research package](archive/imported_packages/)
- [Releases and provenance](provenance/)

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
python scripts/screen_review_candidates.py --run-id 2026-09-10
python scripts/verify_evidence_sources.py
python scripts/audit_seed_claims.py
python scripts/synthesize_review_evidence.py --manuscript-dir /path/to/overleaf-manuscript
```

Existing analysis scripts and exact data snapshots are preserved. Networked retrieval will change as bibliographic indexes update; freeze the query date and retain raw responses when refreshing results.

The 10 September 2026 public-source retrospective run retrieved 7,529 source-query records and produced 6,218 deduplicated **screening candidates**. These are workload denominators, not included studies or an estimate of the size of the field. See the quality report for result caps, source-query failures and known-item sensitivity.

The manuscript evidence seed currently contains 24 representative reports with 24/24 bibliographic identities re-resolved through stable identifiers. The generated manuscript table uses 14 selected evidence anchors and deliberately omits incompletely duplicated numerical outcome checks. It is not the final included-study corpus; duplicate screening of the 1,895-record queue and full-text adjudication remain open human-review tasks.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New papers should include a stable DOI, PubMed/Europe PMC, arXiv or publisher identifier; an evidence-generation label; evidence stage; and a concise statement of whether a physical feedback loop is actually demonstrated.

## Copyright and release policy

Bibliographic metadata, original curation and code can be prepared for open release after licence review. Publisher PDFs and other third-party full texts are kept in `local_only/`, ignored by Git, and must not be redistributed without permission. Provenance, author attribution and reuse terms remain under review.
