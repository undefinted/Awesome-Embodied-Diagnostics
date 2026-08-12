# Literature registry

`references.csv` is the source of truth. `scripts/build_bibtex.py` deterministically generates `references.bib` from it.

## Metadata states

- `verified`: title and persistent identifier were checked against a publisher, PubMed, an official organization, or another authoritative record during this work.
- `provisional`: the work is identifiable, but one or more bibliographic fields should still be checked before submission.
- `unresolved`: a citation key existed in a recovered manuscript, but the exact work could not be established with sufficient confidence. The row is retained so the omission is visible.
- `alias`: a duplicate key maps to a canonical entry in `citation_aliases.csv`.

No article PDFs are included. A DOI or official URL is not itself a license to redistribute the article file. If PDFs are later collected for private research, store them outside the public Git history unless the exact version has a compatible license.

`search_log.csv` records searches recoverable from this session and is not a claim of a completed systematic search. `screening_log.csv` is a structured template for prospective inclusion/exclusion decisions.

