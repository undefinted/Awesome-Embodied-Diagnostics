# Clinical Detection and Intervention: public-source candidate statistics

Snapshot date: **2026-08-15**. Date window: **2000-01-01 to 2026-08-15**.

This directory contains a reproducible public-source **candidate evidence map** for the final Clinical Detection and Intervention taxonomy. It is intentionally not described as a systematic-review inclusion set: title/abstract screening is deterministic and reproducible, but dual-reviewer full-text eligibility and sensing–decision–action–feedback verification remain pending.

## Counting units

- Task chart (A1–A5, R1–R5, S1–S6): one task–study pair after DOI-first and normalized-title-second deduplication within that task.
- Mechanism chart (1.1, 1.2, 1.3): unique works within the mechanism; task–study pairs are also retained.
- Domain chart: unique works across Clinical Detection and Intervention. Cross-task and cross-mechanism overlap is audited separately rather than assigned arbitrarily.
- `public full text located`: a public full-text location was identified from OpenAlex, Europe PMC/PMC or arXiv. It is not a page-by-page licence audit.

## Current candidate counts

| Level | Public-visible screened candidates | Public full text located |
|---|---:|---:|
| Clinical Detection and Intervention (unique works) | 1,790 | 900 |
| 1.1 Active observational sensing (unique works) | 1,461 | 749 |
| 1.2 Response-eliciting interactive diagnosis (unique works) | 199 | 93 |
| 1.3 Diagnostic sample acquisition (unique works) | 144 | 66 |

The exact 16 task-family counts are in `task_counts.csv`. Zero is retained and displayed; it means that no record passed this reproducible title-screening rule, not that the task or technology cannot exist.

## Files

- `query_log.csv`: source, exact query, date window, reported hits and retrieved records.
- `retrieval_records.csv`: source-level records before task-level deduplication.
- `screened_candidates.csv`: auditable candidate task–study pairs.
- `excluded_records.csv`: records rejected by the deterministic screen with reasons.
- `task_counts.csv`, `mechanism_counts.csv`, `domain_summary.csv`: chart data.
- `overlap_audit.csv`: cross-task or cross-mechanism candidates requiring boundary adjudication.
- `qc.json`: machine-readable integrity checks and interpretation warning.
- `figures/`: 40 charts in Chinese and English, each exported as editable SVG and high-resolution PNG (80 files).

## Reproduction

```powershell
python scripts\build_clinical_detection_intervention_public_statistics_v2.py `
  --output-dir outputs\clinical_detection_intervention_statistics_v2 `
  --cache-dir data\cache\clinical_detection_intervention_statistics_v3 `
  --end-date 2026-08-15 `
  --sources openalex,epmc,arxiv

$env:RUNTIME_NODE_MODULES='<bundled Node modules path>'
node scripts\render_cdi_statistics_charts.mjs `
  outputs\clinical_detection_intervention_statistics_v2 `
  outputs\clinical_detection_intervention_statistics_v2\figures
```

Crossref is not used as a corpus-discovery denominator because its bibliographic query is relevance-ranked and nearly always returns a match. It is reserved for later DOI/metadata resolution. This prevents broad fuzzy matches from being presented as study counts.

