# P5 public-index evidence landscape after conservative task revision

Bibliographic discovery freeze: 2026-08-13. Classification revision:
2026-08-14.

## Accounting

| Stage | Count |
|---|---:|
| Retrieval-task assignment rows | 861 |
| Unique works after DOI-first/title-second deduplication | 855 |
| Excluded by explicit title-scope rules | 21 |
| Retained title-level candidates | 834 |
| Candidates with a public full-text/preprint location identified | 378 |
| Task-resolved clinical-procedure candidates | 759 |
| Task-unresolved/cross-cutting technology candidates (T9) | 75 |

The 21 title exclusions and their rule-based reasons remain in
`data/presentation/p5_reclassification_excluded_records_2026-08-14.csv`.

## Conservative procedure counts

| Title-verifiable clinical examination procedure | Public visible | Public available |
|---|---:|---:|
| Ultrasound examination and active scanning | 330 | 138 |
| Active or magnetically controlled capsule endoscopy | 239 | 117 |
| Bronchoscopic observation and navigation | 91 | 32 |
| Flexible gastrointestinal endoscopic examination | 54 | 25 |
| Actively aligned ophthalmic examination | 20 | 10 |
| Active auscultation and acoustic examination | 13 | 5 |
| Cutaneous and exposed-tissue surface imaging | 8 | 3 |
| ENT and oral-cavity examination | 4 | 1 |
| **Task-resolved total shown in the main chart** | **759** | **331** |
| Task-unresolved/cross-cutting technology (T9; not a clinical bar) | 75 | 47 |
| **All retained candidates** | **834** | **378** |

## Counting rules

1. Deduplicate by normalized DOI and then normalized title when DOI is absent.
2. Apply explicit title-scope exclusions while retaining excluded rows.
3. Assign a procedure only when the title explicitly supports it.
4. Never convert the retrieval query/bucket into a clinical assignment.
5. Put records without an explicit procedure into T9 and the manual audit
   queue; do not distribute them by assumption.
6. Derive modality and physical-carrier tags independently. These are
   multi-label attributes and cannot be summed as unique papers.
7. Keep named projects/systems separate from publication counts.

The pipeline is implemented by
`scripts/reclassify_p5_active_observation.py` and checked by
`scripts/validate_p5_reclassification.py`.

## Figure use

Use `figures/public_evidence/p5_reclassified_clinical_tasks.svg` (Chinese) or
`p5_reclassified_clinical_tasks_en.svg` (English) for the main evidence map.
The right-hand panel reports the unresolved T9 residual explicitly. Use the
task-by-modality matrix only as a secondary/backup panel.

Suggested claim:

> In this frozen public-index title corpus, ultrasound and active capsule
> endoscopy form the largest task-resolved candidate clusters. Optical and
> spectroscopic methods are treated as cross-cutting sensing modalities rather
> than competing clinical applications. Seventy-five candidates could not be
> assigned to a prespecified clinical examination procedure from the title
> alone and were retained as an unresolved audit corpus.

## Limits

- These are title-level candidates, not full-text systematic-review inclusions.
- A task-resolved title does not prove a complete embodied sensing–decision–
  action–feedback loop.
- Public availability is a located full-text/preprint endpoint, not an
  item-by-item licence certification.
- Counts measure the visible indexed research corpus, not clinical maturity,
  diagnostic efficacy, autonomy or regulatory deployment.
