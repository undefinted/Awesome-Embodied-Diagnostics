# Clinical Detection and Intervention statistics

Snapshot date: **2026-08-15**  
Scope: publicly visible bibliographic records and automatically identified legal public-full-text locations.

## What is counted

The primary comparable analysis counts one DOI-first/title-second deduplicated work whose title satisfies a saved task rule in the same frozen public-index corpus. The source snapshot combines Europe PMC, OpenAlex, Crossref and arXiv records collected earlier in this project. It is a conservative **title-level candidate map**, not a systematic-review inclusion set and not an estimate of all publications worldwide.

`public_visible` means that a bibliographic record is visible in the frozen public indexes. `public_available_location_identified` means that the automated pipeline found a public repository or OpenAlex open-access location. The latter has not been individually licence-audited and must not be equated with a verified reusable full-text licence.

## Mutually exclusive primary classification

The classification unit is a diagnostic evidence-acquisition task, not the hardware form. A robotic arm, motorized probe, steerable endoscope, active capsule or other controllable physical carrier can appear in any mechanism if its action satisfies the definition.

- **1.1 Active observational sensing:** the action changes the sensor pose, contact, coverage or acquisition geometry; the terminal evidence is an in-vivo image, sound or physiological signal.
- **1.2 Response-based interactive diagnosis:** the system applies a controlled perturbation and interprets the elicited mechanical, physiological or functional response.
- **1.3 Sample-based interactive diagnosis:** the action removes or collects material and the terminal evidence is an ex-vivo pathological, cytological, biochemical, microbiological or molecular result, including sample adequacy.

For a mutually exclusive quantitative figure, a paper that hits more than one rule is assigned by the terminal evidence-action hierarchy:

1. sample acquisition (1.3);
2. elicited response (1.2);
3. active observation (1.1).

This hierarchy is not a claim that one mechanism is more important. It prevents a multistage platform from being counted twice. Secondary rule hits are retained in `clinical_detection_intervention_overlap_audit.csv` and should be used as qualitative stage tags.

Examples of resolved boundaries:

- ultrasound-guided robotic venipuncture is primarily 1.3; ultrasound remains a guidance-modality tag;
- optical coherence elastography is primarily 1.2 because controlled deformation and elasticity are the diagnostic evidence;
- endobronchial ultrasound observation is primarily an active bronchoscopic examination task in 1.1;
- a capsule that collects microbiome material is primarily 1.3 rather than capsule imaging in 1.1.

## Two statistical layers

### Comparable core

All three mechanisms use the same frozen 359-record deduplicated source, the same title-screening level, the same work key and the same access rule. After task screening and cross-rule resolution, the core contains 322 unique title-level candidates. These are the only counts that may be compared directly across 1.1–1.3 in the current release.

### Retrieval audit

The broader saved task-assignment file contains 1,111 unique records across the three search families before a uniform screen. Its mechanism-specific values are retrieval denominators only. They include false positives, legacy assignments and cross-mechanism duplicates. They are exported to show the uncompleted screening workload and must not be plotted as publication totals.

The separately developed high-recall P5 active-observation corpus is intentionally not substituted into the comparable core because equivalent high-recall retrieval and screening have not yet been completed for 1.2 and 1.3. Combining them would create an ascertainment bias that overstates 1.1.

## Reproduction

From the repository root:

```powershell
python scripts/build_clinical_detection_intervention_statistics.py `
  --screened-records outputs/public_landscape/public_title_screened_records.csv `
  --retrieval-assignments data/standalone_snapshots/2026-08-12/literature_task_assignments_all_snapshots.csv `
  --output-dir outputs/clinical_detection_intervention `
  --snapshot-date 2026-08-15

python scripts/make_clinical_detection_intervention_figures.py `
  --input-dir outputs/clinical_detection_intervention `
  --output-dir figures/public_evidence
```

## Interpretation limits

- The rules favour specificity over recall; relevant papers whose titles omit the embodiment or task concept can be missed.
- A title-level candidate can still be excluded after abstract or full-text review.
- Public-full-text discovery is automated and incomplete.
- Publication volume does not measure clinical maturity, diagnostic performance, regulatory status or real-world deployment.
- The year 2026 is incomplete through 2026-08-15.
- A journal-grade systematic/scoping review requires a protocol, complete database-specific search strings, dual screening, recorded exclusion reasons and full-text evidence extraction. The current outputs support that next step but do not replace it.

Transparent reporting should follow the principles of PRISMA 2020 when the work is converted into a systematic or scoping review.
