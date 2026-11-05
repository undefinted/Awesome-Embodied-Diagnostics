# Candidate Evidence Audit

Audit date: 2026-11-05

> These counts describe the current automated candidate inbox, not the complete literature and not clinically validated systems.

## Reconciled counts

- Raw candidate records: 86
- Unique candidate works: 84
- Identifier-verified works: 80
- Core candidates: 4
- Adjacent/borderline: 11
- Excluded after scope screening: 65
- Unverified identifiers: 4
- Future-year metadata flags: 18

## Rules

- DOI records are checked against Crossref; arXiv-only records are checked against the primary arXiv page.
- Core candidate status requires explicit title-level evidence of diagnostic embodiment.
- General robotic surgery, static diagnostic AI, reviews without an acquisition agent, and keyword collisions are excluded.
- Core candidate is a screening decision, not final inclusion; full-text loop verification remains required.

See `data/audited_candidates.csv` for every decision and reason.
