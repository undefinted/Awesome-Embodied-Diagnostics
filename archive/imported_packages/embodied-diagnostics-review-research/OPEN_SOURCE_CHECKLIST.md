# Open-source release checklist

Complete this list before making the GitHub repository public.

- [ ] Add all authors, affiliations, ORCID identifiers, repository URL, and preferred citation to `CITATION.cff`.
- [ ] Decide and document a manuscript license separately from the MIT code license.
- [ ] Review `literature/references.csv`; resolve every `unresolved` or `provisional` metadata row.
- [ ] Run `make all && make test` and commit the refreshed `results/` files.
- [ ] Inspect `results/missing_citations.csv`; distinguish truly missing references from intentional placeholders.
- [ ] Do not commit publisher PDFs unless the exact version and redistribution license are verified.
- [ ] Establish the provenance and reuse rights of both PNG screenshots under `sources/private_review_only/`, or remove them from the public release.
- [ ] Remove any patient-level, identifiable, confidential, or contract-restricted data before adding future datasets.
- [ ] Add a data dictionary and license for each future dataset under `data/`.
- [ ] Add search dates, databases, full queries, deduplication rules, and inclusion/exclusion reasons to the literature logs.
- [ ] Consider archiving a release on Zenodo and adding the release DOI to `CITATION.cff`.

