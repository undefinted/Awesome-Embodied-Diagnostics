# Data rigour and completeness audit

Updated: 2026-08-13

## Bottom line

This package is a reproducible, public-source scoping evidence map suitable for a research presentation and framework development. It is **not yet a completed systematic review** and must not be described as exhaustive coverage of all publicly available research.

## What is supported

- A frozen 359-record source corpus assembled from saved Europe PMC, OpenAlex, Crossref and arXiv results.
- Conservative task-specific title screening for the three clinical evidence-generation mechanisms.
- DOI or normalized-title deduplication, plus correction of punctuation variants and adjacent-task overlap found during manual audit.
- Automated discovery of OA or repository locations.
- Manual claim-level verification of 24 representative primary studies, including study design, sample/setting, reported result and loop boundary.
- An independent maximum-evidence-maturity axis, separated from volume and autonomy.

## What is not supported

- Global publication totals or a claim that every public paper was retrieved.
- Systematic-review included-study counts.
- A completed dual-reviewer title/abstract and full-text screen.
- Exhaustive task-level counts for laboratory diagnostics or everyday monitoring.
- Complete regulatory, commercial-deployment or post-market status.

## Quality controls completed

- Cross-file reconciliation of task counts, maturity matrix and presentation workbook.
- Manual title audit of response-based and sample-based candidates.
- Explicit zero-result disclaimer.
- Claim-level public-source ledger with non-extrapolation statements.
- PowerPoint overflow and template-fidelity checks.
- Repository validation and GitHub Actions checks.

## Minimum work remaining for review-grade completeness

1. Extend the frozen protocol to Embase, Scopus, Web of Science, IEEE Xplore, ACM DL and Compendex.
2. Validate search sensitivity against a predefined set of known studies.
3. Conduct independent dual-reviewer title/abstract and full-text screening with exclusion reasons.
4. Complete backward/forward citation chasing and investigator/platform searches.
5. Build task-complete corpora for laboratory diagnostics and everyday monitoring.
6. Report PRISMA flow, duplicates, full-text exclusions and inter-reviewer agreement.

