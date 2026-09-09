# Review Research and Data Plan

## Objective

Build a living, auditable evidence map that supports the manuscript's central
question: how can an agent actively acquire sufficient medical evidence through
risk-bounded physical interaction? The public repository must support daily
surveillance, while the journal review requires a separately frozen
retrospective search and human screening process.

The most defensible publication design is therefore a **scoping review with a
living evidence-map companion**, not a single pooled effectiveness review. JBI
defines scoping reviews as systematic attempts to identify and map the breadth
of evidence, which matches a field spanning diagnostic accuracy, engineering
validation, workflow studies and technical precedents. Reporting should follow
PRISMA 2020 and PRISMA-ScR; the searches themselves should be reported with
PRISMA-S.

## What still needs to be researched

### Core application evidence

- Robotic and human-guided adaptive imaging: ultrasound, OCT, endoscopy,
  capsule systems, ophthalmic and dental acquisition.
- Response-based examination: palpation, stiffness mapping, auscultation,
  stimulation-response mapping and provocation tests.
- Sample acquisition: venipuncture, swabbing, biopsy and other fluid/tissue
  collection, with within-attempt control separated from repeat-attempt
  authority.
- Diagnostic laboratory loops: specimen inspection, adaptive routing,
  autoverification, microfluidic feedback and closed experimental optimization.
- Everyday loops: monitoring that actually changes confirmatory measurement or
  escalation, separated from one-way sensing.

### Translation and evaluation evidence

- Simulation-to-real evidence ladders and operating-domain validation.
- Human factors, workload, overrides, aborted procedures and safe handover.
- Analytical validity, diagnostic accuracy, clinical utility and patient-
  relevant outcomes as separate evidence levels.
- Failure taxonomies, calibration drift, hardware wear, cybersecurity,
  maintenance and post-deployment monitoring.
- Equity at the sensing interface, accessibility, privacy and responsibility.

### Technical precedents

Foundation/VLA models, diffusion policies, world models, surgical robotics,
self-driving laboratories and therapeutic closed loops should be coded as
technical or governance precedents unless they directly acquire diagnostic
evidence. Their paper counts must never be added to the core clinical corpus.

## Data to extract

Use `data/review/evidence_extraction_template.csv`. In addition to ordinary
bibliographic and study-design fields, the review needs explicit fields for the
observation, adaptive decision, physical action, returned feedback, stopping
rule, human role, autonomy level, operating domain and whether the action is
repeatable. Sample size must be decomposed into participants, specimens and
procedures rather than stored as one ambiguous number.

The unit of analysis must also be recorded explicitly. One platform can produce
several reports, one report can contain several experiments, and one experiment
can include participants, specimens and repeated procedures. The repository
should preserve `system_id`, `study_id` and `report_id` separately so that a
publication count is never mistaken for a count of independent systems or
clinical evaluations.

## Evidence maturity gates

Each record should pass through visible, reversible stages:

1. retrieved candidate;
2. identifier and metadata verified;
3. title/abstract screened independently by two reviewers;
4. full text screened with a recorded exclusion reason;
5. extracted and second-person checked;
6. assigned a study-design-appropriate risk-of-bias assessment;
7. eligible for a named synthesis table or figure.

Automated relevance signals may prioritize work but cannot advance a record
past human eligibility screening. Diagnostic-accuracy reports should use the
current QUADAS tool (QUADAS-3); randomized interventions, non-randomized
interventions and prediction-model studies require their own appropriate tools
rather than one universal quality score.

## Analyses that are defensible

After duplicate full-text screening, the following descriptive analyses are
reasonable:

- included-study flow with explicit denominators;
- studies by direction, year and evidence stage;
- study role and loop-completeness distributions;
- human-mediated versus device-executed loops;
- repeatable versus non-repeatable actions and their stopping/handover rules;
- presence of safety, failure, override and clinical-utility outcomes;
- evidence-gap matrices linking diagnostic task to translation stage.

Performance estimates should remain study-level unless populations, devices,
outcomes and thresholds are sufficiently homogeneous for a prespecified
meta-analysis. A pooled "success rate of embodied diagnostics" would not be
scientifically meaningful.

## Analyses that are not yet defensible

- claiming that candidate counts equal the number of papers in the field;
- comparing task areas by raw database hits;
- treating multiple reports of one platform as independent systems;
- pooling phantom, volunteer and patient results;
- converting missing outcomes into zero;
- calling an automated title screen a final inclusion decision;
- claiming exhaustive coverage without subscription databases, citation
  chasing and duplicate independent screening.

## Search programme

`scripts/retrospective_search.py` creates a frozen public-source search run.
PubMed and Europe PMC provide biomedical coverage; OpenAlex and arXiv broaden
engineering and conference/preprint discovery. Crossref remains useful for DOI
verification and supplementary discovery, but is not treated as a substitute
for a bibliographic database. IEEE Xplore, Embase, Scopus and Web of Science
exports should be imported when access is available and reported as separate
sources.

The daily workflow detects newly indexed records. It does not replace the
retrospective run, which should be frozen before submission and followed by
dual-reviewer screening, backward/forward citation chasing and a PRISMA flow.

## Methodological basis

- [JBI Manual for Evidence Synthesis: Scoping reviews](https://jbi-global.atlassian.net/wiki/spaces/MANUAL/pages/355862497/10.+Scoping+reviews)
  guides protocol development, searching, charting and presentation for broad
  evidence maps.
- [PRISMA 2020](https://www.bmj.com/content/372/bmj.n71) supplies the review
  reporting checklist and study-flow framework.
- [PRISMA-S](https://doi.org/10.1186/s13643-020-01542-z) requires enough detail
  about databases, platforms, complete strategies, dates and deduplication for
  the search to be reproducible.
- [SWiM](https://www.bmj.com/content/368/bmj.l6890) supports transparent
  grouping and reporting when heterogeneous quantitative results cannot be
  meta-analyzed; it is a reporting guide, not a substitute for a prespecified
  synthesis method.
- [QUADAS-3](https://www.bristol.ac.uk/population-health-sciences/projects/quadas/)
  is the current recommended risk-of-bias and applicability tool for diagnostic
  accuracy estimates. Other study designs must use design-specific tools.
