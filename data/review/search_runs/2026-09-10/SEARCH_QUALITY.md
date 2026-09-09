# Frozen Public-Source Search Quality

Run: `2026-09-10`; date range: 2000-01-01 to 2026-09-10.

## Denominators

- Source-query records retrieved: 7,529.
- DOI/PMID/arXiv/title-deduplicated candidate records: 6,218.
- Conservative high-signal records: 358.
- Possible-signal records: 1,538.
- Records retrieved through more than one source family: 678.
- Source-query pairs completed successfully: 104/104.
- Source-query pairs ending in a recorded error: 0.
- Configured source-query pairs not run: 0.
- Source-query pairs reaching the configured result cap: 67.

## Metadata quality controls

- Blank titles: 0.
- Duplicate normalized-title clusters remaining after identifier-first deduplication: 0.
- Malformed DOI strings: 0.
- Records dated beyond the frozen search year: 11.
- Records without DOI, PMID, PMCID or arXiv identifier: 65.
These checks detect internal metadata problems; DOI/title agreement and full-text relevance still require verification.

## Known-item sensitivity check

The strategy retrieved 19/24 manuscript evidence seeds (79.2%)
This is sensitivity against a small convenience set, not recall against an unknown universe. Missing known items require query refinement or documented citation chasing.

## Can these data support review figures?

Not yet for publication-volume or prevalence claims. Capped queries, heterogeneous index coverage and pending human screening make raw retrieval counts unsuitable as estimates of the field. The data are suitable for managing screening workload, finding terminology gaps and documenting source coverage.

After duplicate human screening, final included records can support descriptive counts by direction, year, evidence stage, loop execution and safety-reporting status. Task-success percentages should remain study-level unless a separate meta-analysis establishes compatible designs and outcomes.

## Required next steps

1. Split every capped query by year or narrower concept until no stratum is truncated.
2. Resolve any recorded source-query failures and preserve them explicitly when a source remains unavailable.
3. Import IEEE Xplore, Embase, Scopus and Web of Science exports where institutional access permits.
4. Screen the high/possible queue independently in duplicate, then retrieve full text.
5. Perform backward and forward citation chasing and deduplicate at both report and system level.
6. Populate the extraction schema and conduct study-design-appropriate quality assessment.
