# Search Coverage Protocol

## Claim boundary

The repository is a living evidence map, not yet a completed systematic review. A daily surveillance search cannot establish historical completeness. Counts must always identify whether they refer to raw retrieval records, unique verified records, screened candidates, or full-text included studies.

## Active discovery sources

| Source | Primary purpose | Important limitation |
|---|---|---|
| arXiv | Rapid robotics, AI, and engineering preprints | Does not cover most clinical journals |
| Europe PMC | Biomedical abstracts and PubMed-linked literature | Query syntax and indexing lag can affect recall |
| OpenAlex | Cross-disciplinary journal and conference discovery | Search relevance can introduce keyword collisions |
| Crossref | DOI and publisher metadata discovery/verification | Metadata search is not a substitute for bibliographic database screening |

## Definitive public-v3 snapshot

The 10 September 2026 public-v3 run uses explicit PubMed Title/Abstract and
Europe PMC TITLE_ABS fields plus the registered arXiv syntax. Across 28 query
families, all 84 source-query pairs completed, returned records matched the
source-reported totals, and no configured result cap remained. OpenAlex is kept
as supplementary discovery because its broad `search` parameter did not behave
as an equivalent Boolean bibliographic query. These engineering checks improve
retrieval integrity but do not establish completeness across subscription
indexes or replace information-specialist peer review.

## Retrieval families

The active registry in `data/discovery_queries.yaml` covers robotic ultrasound, endoscopy, capsule and luminal robots, palpation/tactile examination, auscultation, biopsy and phlebotomy, ophthalmic and dental examination, medical VLA, active diagnostic sensing, multimodal physical examination, adaptive examination, and closed-loop diagnostic laboratories.

## Required completeness work

For a publishable systematic or scoping review, the repository still requires:

- retrospective searches from database inception or a prespecified start year;
- PubMed/MEDLINE query validation and, where accessible, IEEE Xplore, Scopus, Web of Science, Embase, and conference-library searches;
- backward and forward citation chasing from included reviews and landmark systems;
- deduplication before screening;
- dual-reviewer title/abstract and full-text screening;
- recorded exclusion reasons and a PRISMA-style flow diagram;
- frozen search dates, exact queries, and exported result counts.

No source is described as complete on its own. Missing subscription-database access must be reported as a limitation rather than silently inferred away.
