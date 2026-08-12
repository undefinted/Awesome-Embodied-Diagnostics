# Awesome Embodied Diagnostics

[![Repository validation](https://github.com/undefinted/awesome-embodied-diagnostics/actions/workflows/validate.yml/badge.svg)](https://github.com/undefinted/awesome-embodied-diagnostics/actions/workflows/validate.yml)
![Status](https://img.shields.io/badge/status-active%20curation-5B1A6E)
![Scope](https://img.shields.io/badge/scope-medical%20detection-3569A8)
![Evidence](https://img.shields.io/badge/evidence-stage%20aware-2E7D65)

A curated, reproducible research repository for **embodied intelligence in medical detection**: diagnostic systems in which decisions change subsequent physical observation, interaction, sampling or testing, and the resulting evidence updates later decisions.

> **Status:** private working repository. The literature map and quantitative results remain under active validation. Counts are research-workflow outputs, not claims of global coverage or clinical maturity.

## Core thesis

> Embodied intelligence extends medical detection from interpreting isolated measurements to **adaptive evidence acquisition** across patients, samples, instruments and care environments.

The basic unit is a `sensing → decision → action → feedback` loop. A system is treated as fully embodied only when an inference changes a subsequent physical measurement or diagnostic action and the consequence updates later decisions.

## Contents

- [Scope and inclusion boundary](docs/SCOPE.md)
- [Curated literature](literature/README.md)
- [Search and screening data](data/README.md)
- [Reproducible code](scripts/)
- [Generated results and figures](outputs/)
- [Review/manuscript research package](archive/imported_packages/)
- [Releases and provenance](provenance/)
- [P5–P29 page-by-page research support](docs/PRESENTATION_SLIDE_SUPPORT.md)
- [Application evidence and analysis package](docs/APPLICATION_PRESENTATION.md)

## Application map

| Domain | How the action creates evidence | High-priority loop |
|---|---|---|
| Active observational sensing | Changes viewpoint, contact or scan trajectory | uncertainty-driven rescan and stopping |
| Response-based interactive diagnosis | Applies a stimulus and measures response | sequential palpation or stimulation mapping |
| Sample-based interactive diagnosis | Acquires tissue or fluid | adequacy-aware resampling and stopping |
| Laboratory diagnostics | Routes samples, tests or experiments | result-driven reflex, recovery and protocol adaptation |
| Everyday monitoring | Changes confirmation or escalation after anomaly | personal-baseline detection followed by bounded confirmation |

## Featured evidence anchors

- Autonomous thyroid and carotid ultrasound provide human workflow evidence, but not randomized outcome evidence.
- Multicentre robotic phlebotomy includes analytical equivalence and a 1,633-participant routine-use cohort.
- Ferrobotic and digital-microfluidic platforms demonstrate programmable physical laboratory loops; deployment evidence remains limited.
- Large wearable cohorts show longitudinal sensing at scale, while most action loops remain human-mediated.

See [`data/presentation/application_evidence.csv`](data/presentation/application_evidence.csv) for claim-level qualifiers and sources.

## Current reproducible snapshot

The frozen 2026-08-12 task-assignment file contains 1,454 saved rows. After selected task aliases are merged and saved snapshots are deduplicated, the analysis produces 1,150 unique task–paper candidate pairs. Within-category paper counts are 869 for active observational sensing, 131 for response-based interaction and 118 for sample-based interaction.

These are **curation-pipeline results**, not estimates of all publications and not measures of clinical maturity. Reproduce them with:

```bash
python scripts/analyze_application_landscape.py
```

Results are written to [`outputs/application_landscape/`](outputs/application_landscape/), including a filterable research workbook, normalized task counts and evidence-stage summaries.

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
python scripts/analyze_application_landscape.py
```

Existing analysis scripts and exact data snapshots are preserved. Networked retrieval will change as bibliographic indexes update; freeze the query date and retain raw responses when refreshing results.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New papers should include a stable DOI, PubMed/Europe PMC, arXiv or publisher identifier; an evidence-generation label; evidence stage; and a concise statement of whether a physical feedback loop is actually demonstrated.

## Copyright and release policy

Bibliographic metadata, original curation and code can be prepared for open release after licence review. Publisher PDFs and other third-party full texts are kept in `local_only/`, ignored by Git, and must not be redistributed without permission. The repository is private while provenance, author attribution and reuse terms are being reviewed.
