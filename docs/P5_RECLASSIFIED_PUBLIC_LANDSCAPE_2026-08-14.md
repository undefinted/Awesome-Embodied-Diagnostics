# P5 active-observation public landscape after taxonomy revision

Freeze date for bibliographic discovery: 2026-08-13. Reclassification,
scope audit and project-page access check: 2026-08-14.

## What changed

The previous 11 retrieval buckets mixed clinical tasks, sensing modalities and
physical carriers. The revised analysis uses one mutually exclusive primary
clinical acquisition task for each unique work. OCT, spectroscopy,
endomicroscopy, photoacoustic imaging and other sensing methods are retained as
multi-label modality attributes. Manipulators, capsules, endoscopes and other
physical embodiments are retained as carrier attributes.

The old chart remains a search-coverage audit. The new chart is the P5 figure
for task-level interpretation.

## Accounting

| Stage | Count |
|---|---:|
| Original task assignments | 861 |
| Unique works after DOI-first/title-second deduplication | 855 |
| Excluded by explicit title-scope rules | 21 |
| Reclassified public-visible title candidates | 834 |
| Candidates with a public full-text/preprint location identified | 378 |
| Priority manual full-text audit queue | 33 |
| Separately curated named public projects/systems | 12 |

The 21 title exclusions comprise nine treatment or non-diagnostic actions,
seven non-medical/industrial applications, four reviews/perspectives, and one
sample-based interaction paper. Every excluded record and reason is preserved
in `data/presentation/p5_reclassification_excluded_records_2026-08-14.csv`.

## Revised task counts

| Primary clinical acquisition task | Public visible | Public available |
|---|---:|---:|
| Ultrasound examination and active scanning | 341 | 149 |
| Active or magnetically controlled capsule endoscopy | 237 | 117 |
| Bronchoscopic observation and navigation | 91 | 32 |
| Flexible gastrointestinal endoscopic inspection | 80 | 40 |
| Actively aligned ophthalmic examination | 27 | 14 |
| Generic active-scanning technology platform | 27 | 14 |
| Skin, wound and exposed-tissue surface mapping | 14 | 6 |
| Active auscultation and acoustic examination | 13 | 5 |
| ENT and oral-cavity examination | 4 | 1 |

T9 is removed from the main clinical-task bars because its titles do not specify
a clinical acquisition site. The figure reconciles 807 site-resolved clinical-task
candidates plus 27 generic technical-platform candidates to the 834 title-level
records. T9 remains in the task-by-modality matrix and audit tables, where it is
shown in grey and must not be interpreted as a clinical-application volume.

## Classification rules

1. Deduplicate by normalized DOI; use normalized title only when DOI is absent.
2. Apply explicit scope exclusions while retaining excluded rows and reasons.
3. Assign the primary clinical task from access-route/anatomical title terms.
4. If the title does not specify a site, use a direct clinical retrieval bucket.
5. If only a cross-cutting modality bucket is available, assign T9 and place the
   record in the priority manual audit queue.
6. Derive modality and carrier tags independently; tags are non-exclusive and
   their counts must not be summed to obtain unique works.
7. Keep named projects/systems in a separate curated table and never add them to
   publication counts.

All rules are implemented in
`scripts/reclassify_p5_active_observation.py`. Project mappings are explicit in
`scripts/reclassify_p5_public_projects.py`. Accounting and modality tables are
checked independently by `scripts/validate_p5_reclassification.py`.

## Validation result

The validation report passes with zero errors:

- 855 unique work keys;
- 834 included title candidates plus 21 title exclusions;
- exactly one primary task for every unique record;
- task counts reconcile to included unique records;
- modality matrix reconciles to record-level tags;
- 378 unique included works have a public location identified;
- 12 project IDs are unique and contain source URLs;
- projects are not added to publication counts.

## P5 use

Use `figures/public_evidence/p5_reclassified_clinical_tasks.svg` as the main P5
visual. It is a 16:9 slide-sized editable vector. Use
`figures/public_evidence/p5_task_modality_matrix.svg` as a second panel,
appendix figure or discussion backup. PNG copies are provided for rapid preview.

Suggested spoken claim:

> After deduplicating and separating clinical tasks from sensing modalities,
> the public title-level candidate landscape remains dominated by ultrasound
> and active capsule endoscopy. OCT and optical spectroscopy no longer appear
> as competing application categories; they are cross-cutting modalities used
> across ophthalmic, endoscopic, bronchoscopic and surface-mapping tasks.

## Interpretation limits

- These are deterministic title-level candidates, not systematic-review
  full-text inclusions.
- Public available means that a public full-text or complete preprint location
  was identified; it is not a per-item licence audit.
- Thirty-three records remain prioritized for manual full-text confirmation,
  but all have an explicit provisional primary task.
- Index coverage and rate-limited supplemental queries constrain completeness.
- Counts measure the visible public research corpus, not clinical maturity,
  diagnostic efficacy or regulatory deployment.

## Public project source checks

The 12 curated project/system sources were revisited on 2026-08-14. Examples
include CMU autonomous ultrasound, Aalborg robot-assisted obstetric ultrasound,
REMDOC, RWTH 3D robotic ultrasound, UltraBot tactile extension, ROPCA,
robotized slit-lamp imaging, two robotic auscultation systems, autonomous
endomicroscopy and robotic capsule endomicroscopy. Source URLs and loop
characterizations are preserved in
`data/presentation/p5_reclassified_public_projects_2026-08-14.csv`.
