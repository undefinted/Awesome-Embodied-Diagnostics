# Candidate Evidence Audit

Audit date: 2026-09-03

> These counts describe the current automated candidate inbox, not the complete literature and not clinically validated systems.

## Reconciled counts

- Raw candidate records: 34
- Unique candidate works: 33
- Identifier-verified works: 31
- Core candidates: 2
- Adjacent/borderline: 6
- Excluded after scope screening: 23
- Unverified identifiers: 2
- Future-year metadata flags: 4

## Rules

- DOI records are checked against Crossref; arXiv-only records are checked against the primary arXiv page.
- Core candidate status requires explicit title-level evidence of diagnostic embodiment.
- General robotic surgery, static diagnostic AI, reviews without an acquisition agent, and keyword collisions are excluded.
- Core candidate is a screening decision, not final inclusion; full-text loop verification remains required.

See `data/audited_candidates.csv` for every decision and reason.
