# Publicly available scope and acquisition request

Updated: 2026-08-13

## Current review scope

The current review version uses legally publicly available evidence: open-access publisher full text, PubMed Central/Europe PMC full text, preprints, author-accepted manuscripts in institutional repositories, public trial registrations, and public regulatory or standards documents. Bibliographic metadata alone does not count as full-text verification.

Subscription-only database searches and paywalled articles are not included in the current coverage denominator. They are maintained as a prospective sensitivity-extension queue. Therefore, current counts must be described as a **publicly available evidence map**, not as an exhaustive global literature count.

## What the user should obtain

### P1 database exports

1. IEEE Xplore: all clinical robotic sensing, response and sampling task queries, plus laboratory automation/microfluidic queries.
2. Scopus: all-domain search and forward/backward citation exports.
3. Embase: clinical device, diagnostic, laboratory and everyday-monitoring queries with Emtree terms.
4. Web of Science Core Collection: independent citation and conference-proceedings sensitivity search.

Exact requested fields and routes are in `data/access/subscription_database_requests.csv`. Export records rather than screenshots. Preserve the database name, platform, exact query, date, timespan, filters, raw hit count and file format.

### Article full text

The generated `outputs/access_audit/user_acquisition_queue.csv` lists curated references for which no public full text was identified or access remains unresolved. Obtain P1 items first. Acceptable routes are institutional subscriptions, interlibrary loan/document delivery, an author-accepted manuscript, or direct author request. Do not bulk-download licensed databases and do not commit copyrighted PDFs to GitHub.

Store acquired PDFs only under `local_only/papers/` using `FirstAuthor_Year_ShortTitle_DOI.pdf`. Record the file and access route in the evidence ledger, but keep the PDF excluded by `.gitignore`.

## After materials are returned

1. Import database exports without editing the raw files.
2. Deduplicate against DOI, PMID, arXiv ID and normalized title.
3. Screen title/abstract before requesting additional full texts.
4. Read full text for every potentially eligible physical-loop study.
5. Report a sensitivity comparison between the public-only map and the subscription-extended map.

