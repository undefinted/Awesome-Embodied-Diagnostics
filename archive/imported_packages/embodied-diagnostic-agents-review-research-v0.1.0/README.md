# Embodied Diagnostic Agents Review — Research Archive

This repository reconstructs and preserves the literature research, evidence map, notes, and reproducibility code used while developing a review of **embodied diagnostic agents**: systems that close a loop across sensing, sampling or manipulation, reasoning, physical or workflow action, and feedback.

The archive contains **56 core references from the prior research discussion** plus **2 formal correction notices discovered during metadata verification**. It is intended to be committed directly to GitHub and extended as the review develops.

## What is included

- `data/references.csv` — canonical, machine-readable literature catalog.
- `data/references.json` — generated JSON export.
- `data/references.bib` — generated BibTeX export.
- `data/search_log.csv` — audit log of reconstructed and update searches.
- `data/metadata_corrections.csv` — corrections made while rebuilding the archive.
- `notes/` — chapter-level synthesis and claim boundaries.
- `scripts/` — validation, export, Crossref suggestion, link-check, and workbook-building code.
- `results/` — generated coverage and validation outputs.
- `outputs/literature_catalog.xlsx` — filterable literature workbook with a summary dashboard.
- `.github/workflows/validate.yml` — continuous validation for GitHub Actions.

## Important provenance statement

No analysis scripts had actually been written in the earlier conversation. The earlier work consisted of web research and narrative synthesis. In addition, the temporary workspace used by that conversation was later pruned by automated maintenance. The files here therefore **reconstruct the research record from the preserved conversation and re-verify high-risk metadata**; they are not represented as recovered original files.

## Quick start

Requires Python 3.10 or later; the core workflow uses only the standard library.

```bash
make validate
make outputs
```

Optional network checks:

```bash
make links
python scripts/query_crossref.py --mailto you@example.org --all
```

`query_crossref.py` writes suggestions only and never silently changes the source catalog.

The Excel workbook builder uses `@oai/artifact-tool` in the Codex primary runtime:

```bash
make workbook
```

## Data model

Each row in `references.csv` records:

- stable record and citation keys;
- review section(s);
- source and evidence type;
- abbreviated author string, year, title, venue, volume and locator;
- DOI and primary URL;
- the exact evidentiary role for which the source was selected;
- evidence stage, verification status, and provenance.

The catalog deliberately separates **reporting guidance**, **regulatory or standards documents**, **conceptual frameworks**, **engineering demonstrations**, **simulated clinical evaluations**, **observational studies**, **single-patient demonstrations**, and **randomized trials**.

## Claim boundaries

The review follows four non-negotiable distinctions:

1. Reporting guideline compliance is not proof of effectiveness or safety.
2. Model performance is not equivalent to human–agent team performance.
3. A laboratory or simulated demonstration is not equivalent to clinical autonomy.
4. A device-level closed loop is not equivalent to a distributed detection–intervention ecosystem.

See `notes/00_scope_and_claim_boundaries.md` for the operational definitions.

## Copyright and full text

This repository includes bibliographic metadata, original synthesis, source links, and code. It does **not** redistribute publisher PDFs or copyrighted full texts. Open-access or licensed full texts may be downloaded separately by users in accordance with their terms. Regulatory and standards links point to authoritative landing pages where possible.

## Reproducibility

Generated files are derived from `data/references.csv`:

```bash
python scripts/validate_catalog.py
python scripts/build_outputs.py
```

GitHub Actions checks that generated data remain synchronized. Run link and Crossref checks intentionally because publisher access controls can produce false failures.

## Licensing

- Code: MIT License (`LICENSE`).
- Original notes and tabular curation: CC BY 4.0 (`LICENSE-DATA.md`).
- Third-party publication metadata and linked materials remain subject to their respective terms.

