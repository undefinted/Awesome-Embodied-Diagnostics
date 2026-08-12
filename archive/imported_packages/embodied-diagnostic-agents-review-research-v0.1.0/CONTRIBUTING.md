# Contributing

## Adding a reference

1. Add one row to `data/references.csv` with a stable `record_id` and `citekey`.
2. Use an authoritative publisher, regulator, standards-body, or repository URL.
3. State the source's evidentiary role and evidence stage; do not infer clinical maturity from topic relevance.
4. Record verification status and provenance.
5. Run `make validate` and `make outputs`.
6. Commit both the source catalog and regenerated outputs.

## Updating dynamic guidance

Never overwrite history silently. Add a row to `data/metadata_corrections.csv`, update the affected record, and explain supersession or version changes in the pull request.

## Quality bar

- Prefer DOI-backed publisher records for journal articles.
- Prefer official landing pages for regulations and guidance.
- Mark preprints explicitly.
- Preserve distinctions among reporting guidance, evidence frameworks, engineering demonstrations, simulated evaluations, clinical studies, and real-world deployment.

