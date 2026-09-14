# Frozen Public-Source Search Quality

Run: `2026-09-14-weekly`; date range: 2026-07-31 to 2026-09-14.

## Denominators

- Source-query records retrieved: 1,965.
- DOI/PMID/arXiv/title-deduplicated candidate records: 1,681.
- Conservative high-signal records: 21.
- Possible-signal records: 316.
- Records retrieved through more than one source family: 94.
- Source-query pairs completed successfully: 85/112.
- Source-query pairs ending in a recorded error: 27.
- Configured source-query pairs not run: 0.
- Source-query pairs reaching the configured result cap: 14.

## Metadata quality controls

- Blank titles: 1.
- Duplicate normalized-title clusters remaining after identifier-first deduplication: 0.
- Malformed DOI strings: 0.
- Records dated beyond the frozen search year: 0.
- Records without DOI, PMID, PMCID or arXiv identifier: 45.
These checks detect internal metadata problems; DOI/title agreement and full-text relevance still require verification.

## Known-item sensitivity check

Known-item testing has not been run.
Role-stratified known-item testing has not been run.
This is sensitivity against a small convenience set, not recall against an unknown universe. Missing known items require query refinement or documented citation chasing.

## Can these data support review figures?

Not yet for publication-volume or prevalence claims. Result caps, heterogeneous index coverage and pending human screening make raw retrieval counts unsuitable as estimates of the field.
The data are suitable for managing screening workload, finding terminology gaps and documenting source coverage.

The high/possible subset is an ordering aid only. Every non-quarantined candidate remains in the title-and-abstract eligibility ledger; existing rule-based low-priority or exclusion suggestions are never final decisions.
After duplicate human screening, final included records can support descriptive counts by direction, year, evidence stage, loop execution and safety-reporting status. Task-success percentages should remain study-level unless a separate meta-analysis establishes compatible designs and outcomes.

## Required next steps

1. Split every capped query by year or narrower concept until no stratum is truncated.
2. Resolve any recorded source-query failures and preserve them explicitly when a source remains unavailable.
3. Import IEEE Xplore, Embase, Scopus and Web of Science exports where institutional access permits.
4. Screen every non-quarantined candidate independently in duplicate; machine signals only determine order.
5. Perform backward and forward citation chasing and deduplicate at both report and system level.
6. Populate the extraction schema and conduct study-design-appropriate quality assessment.
