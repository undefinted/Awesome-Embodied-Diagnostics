# Nature Biomedical Engineering Review Table Benchmark

## Scope and method

This is a targeted design benchmark, not a census of the journal. Four recent
Nature Biomedical Engineering Review or quantitative-synthesis articles were
selected because they represent translational technology comparison, clinical
trial mapping, explicit missing-data handling and meta-analysis. PubMed records
were resolved by PMID and DOI; table captions and header schemas were extracted
from NCBI PMC JATS XML. Retrieval URLs, timestamps and response SHA-256 hashes
are stored under `data/review/nbe_table_benchmark/`.

## Observed patterns

1. **Translation-oriented Reviews use selective synthesis tables.** The
   continuous-monitoring Review uses a table of representative successfully
   translated technologies, organized by technology, interface, functionality
   and factors associated with translation. It does not present the table as a
   complete literature count. Source:
   [Barriers to translating continuous monitoring technologies for preventative medicine](https://www.nature.com/articles/s41551-025-01520-7).
2. **Clinical evidence tables separate population, design and denominator.**
   The exoskeleton Review organizes recent clinical trials by device,
   population, trial type, evidence level, N, study outcome/type and reference.
   Source:
   [Opportunities and challenges in the development of exoskeletons for locomotor assistance](https://www.nature.com/articles/s41551-022-00984-1).
3. **Unavailable characteristics are visible.** The algorithmic-fairness Review
   states in its table caption that dashes denote demographic data that were not
   publicly available or acquired. It does not turn missing demographic values
   into zero. Source:
   [Algorithmic fairness in artificial intelligence for medicine and healthcare](https://www.nature.com/articles/s41551-023-01056-8).
4. **Quantitative synthesis is a different evidence product.** The blood--brain
   barrier meta-analysis does not use a narrative technology-comparison table in
   the accessible article XML. Its quantitative claims depend on systematic
   extraction and prespecified analysis rather than a representative examples
   table. Source:
   [Meta-analysis of the make-up and properties of in vitro models of the healthy and diseased blood-brain barrier](https://www.nature.com/articles/s41551-024-01250-2).

## Design adopted for this Review

The main manuscript table is therefore a selective translational evidence map,
not a disguised systematic-review table. It uses concise platform/task labels
and compares:

- population or material;
- evidence stage and study design;
- separately labelled participant, specimen/measurement, procedure and
  development-data denominators;
- the observation-conditioned diagnostic function;
- human authority and action consequence;
- reported outcome domains and the principal evidence limitation;
- a primary-source citation.

`NR` means not reported in the current verified ledger. Translational stages
T0--T4 describe what was evaluated, not methodological quality. Risk of bias
remains design-specific and is not compressed into this staging variable.

The complete report-level ledger and missingness outputs remain in the public
repository. A future final included-study table must replace the representative
table only after duplicate screening, full-text adjudication, report--study--
system linkage, second-person extraction checks and risk-of-bias assessment.
