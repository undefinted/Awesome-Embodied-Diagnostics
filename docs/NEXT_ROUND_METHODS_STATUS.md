# Next-round methods status

## Completed by code and public-data retrieval

- Corrected missingness so blank and explicit `NR` values are both counted;
  zero remains an observed value.
- Enforced an exact match between main-table reviewer coding and the citation
  selection file.
- Added explicit PubMed `[Title/Abstract]` and Europe PMC `TITLE_ABS` query
  translation. An aborted diagnostic run records why generic Automatic Term
  Mapping was rejected.
- Completed public-v3 across 28 query families and PubMed, Europe PMC and
  arXiv: 84/84 source-query pairs, 11,933 raw source-query records, zero
  returned-count mismatches and zero configured result-cap truncation.
- Preserved exact search strings, query-registry hash, source-reported totals,
  timestamps, raw JSONL checkpoints, deduplicated candidates and provenance.
- Increased convenience known-seed retrieval from 19/24 to 21/24. Retrieval
  was 17/17 for seeds reviewer-coded as direct, bounded, human-mediated or
  assisted-sampling evidence. This is not an estimate of unknown-universe
  recall.
- Put every one of the 6,354 non-quarantined public-v3 candidates into the
  human screening ledger. Machine labels order work and finalize zero records.
- Added auditable forms for full-text decisions, report-study-system linkage,
  citation chasing, expanded extraction and design-specific risk of bias.

## Deliberately not represented as complete

- Protocol registration for the definitive review cycle.
- Information-specialist peer review of each platform-specific search.
- IEEE Xplore, Embase, Scopus and Web of Science exports, which require access.
- Two independent human title/abstract and full-text reviewers.
- Full-text exclusion reasons, duplicate extraction, study/system linkage,
  citation chasing, risk-of-bias assessment and outcome-level certainty.

The workflow validator reports these as publication blockers. A single Codex
run cannot truthfully substitute for two independent human reviewers or obtain
subscription records without authorized database access.
