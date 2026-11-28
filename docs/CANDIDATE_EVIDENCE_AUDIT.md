# Candidate Evidence Audit

Audit date: 2026-11-28

> These counts describe the current automated candidate inbox, not the complete literature and not clinically validated systems.

## Reconciled counts

- Raw candidate records: 99
- Unique candidate works: 97
- Identifier-verified works: 91
- Core candidates: 5
- Adjacent/borderline: 11
- Excluded after scope screening: 75
- Unverified identifiers: 6
- Future-year metadata flags: 27

## Rules

- DOI records are checked against Crossref; arXiv-only records are checked against the primary arXiv page.
- Core candidate status requires explicit title-level evidence of diagnostic embodiment.
- General robotic surgery, static diagnostic AI, reviews without an acquisition agent, and keyword collisions are excluded.
- Core candidate is a screening decision, not final inclusion; full-text loop verification remains required.

See `data/audited_candidates.csv` for every decision and reason.
