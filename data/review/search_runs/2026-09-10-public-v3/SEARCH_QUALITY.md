# Frozen Public-Source Search Quality

Run: `2026-09-10-public-v3`; date range: 2000-01-01 to 2026-09-10.

## Denominators

- Source-query records retrieved: 11,933.
- DOI/PMID/arXiv/title-deduplicated candidate records: 6,358.
- Conservative high-signal records: 225.
- Possible-signal records: 1,522.
- Records retrieved through more than one source family: 5,237.
- Source-query pairs completed successfully: 84/84.
- Source-query pairs ending in a recorded error: 0.
- Configured source-query pairs not run: 0.
- Source-query pairs reaching the configured result cap: 0.

## Metadata quality controls

- Blank titles: 0.
- Duplicate normalized-title clusters remaining after identifier-first deduplication: 0.
- Malformed DOI strings: 0.
- Records dated beyond the frozen search year: 4.
- Records without DOI, PMID, PMCID or arXiv identifier: 51.
These checks detect internal metadata problems; DOI/title agreement and full-text relevance still require verification.

## Known-item sensitivity check

The strategy retrieved 21/24 manuscript evidence seeds (87.5%)
Among seed reports coded as direct, bounded, human-mediated or assisted-sampling evidence, it retrieved 17/17 (100.0%).
This is sensitivity against a small convenience set, not recall against an unknown universe. Missing known items require query refinement or documented citation chasing.

## Can these data support review figures?

Not yet for publication-volume or prevalence claims. Although this run has no configured result-cap truncation, heterogeneous index coverage, known-item gaps and pending human screening make raw retrieval counts unsuitable as estimates of the field.
The data are suitable for managing screening workload, finding terminology gaps and documenting source coverage.

The high/possible subset is an ordering aid only. Every non-quarantined candidate remains eligible for human title-and-abstract screening; automated low-priority or exclusion suggestions are never final decisions.
After duplicate human screening, final included records can support descriptive counts by direction, year, evidence stage, loop execution and safety-reporting status. Task-success percentages should remain study-level unless a separate meta-analysis establishes compatible designs and outcomes.

## Required next steps

1. Preserve the zero-truncation audit and rerun any source-query pair whose returned count no longer matches its reported total.
2. Resolve any recorded source-query failures and preserve them explicitly when a source remains unavailable.
3. Import IEEE Xplore, Embase, Scopus and Web of Science exports where institutional access permits.
4. Screen every non-quarantined candidate independently in duplicate; machine signals only determine order.
5. Perform backward and forward citation chasing and deduplicate at both report and system level.
6. Populate the extraction schema and conduct study-design-appropriate quality assessment.
