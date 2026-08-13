# Public-source scope: limitations and next acquisitions

Updated: 2026-08-13

The current presentation evidence package deliberately uses sources that can be found through public bibliographic indexes and, wherever possible, legally accessible publisher or repository full text. This is an auditable interim scope; it is not a substitute for a formal multi-database systematic search.

## What has been covered

- Public bibliographic discovery: Europe PMC, OpenAlex, Crossref and arXiv.
- Deduplication by DOI or normalized title.
- Conservative task-specific title screening for clinical active-observation, response-based and sample-based tasks.
- Automated discovery of an OA or repository location through OpenAlex, followed by manual verification of the primary studies used for slide-level quantitative claims.
- Independent annotation of publication volume, loop completeness and maximum evidence maturity.

## What remains outside the present count

The following subscription resources should be searched before any claim of systematic or near-complete coverage:

| Resource | Why it matters | Recommended acquisition route |
|---|---|---|
| Embase | Biomedical devices, conference abstracts and European indexing beyond PubMed | institutional library; export full records with Emtree terms |
| Scopus | Broad engineering and biomedical citation coverage | institutional library; export CSV/RIS with abstracts and cited-by counts |
| Web of Science Core Collection | Citation-network checking and multidisciplinary coverage | institutional library; export full record and cited references |
| IEEE Xplore | Robotics, control, sensing and conference proceedings | institutional library; export CSV/BibTeX with abstracts and DOI |
| ACM Digital Library | Human–computer interaction and agent/workflow conference literature | institutional library; export BibTeX/CSV |
| Compendex / Engineering Village | Engineering-device literature not consistently indexed medically | institutional library |
| Cochrane CENTRAL | Controlled trials and trial reports | institutional library or Cochrane access |
| ClinicalTrials.gov, WHO ICTRP, EU CTIS | Unpublished, ongoing and terminated prospective studies | public registries; retain registry snapshots |
| ProQuest Dissertations & Theses | Negative or early engineering results and terminology variants | institutional library |

## Full texts that should be acquired legally

Prioritize full text when a public abstract currently supports a maturity claim, methods are needed to distinguish physical closure from decision support, or the study is a central comparator. Store licensed PDFs only in `local_only/` and never commit them.

High-priority acquisition classes:

1. robotic joint-laxity and provocation studies;
2. clinical robotic palpation and elastography reports beyond phantoms;
3. autonomous or quality-driven robotic biopsy and adequacy sensing;
4. laboratory autoverification, reflex-testing and total-lab-automation studies whose physical rerouting details are behind paywalls;
5. prospective everyday-monitoring studies where alert logic, adherence and confirmatory testing are incompletely reported in the abstract;
6. regulatory submissions, instructions for use and post-market evidence for deployed systems.

For every acquired article record DOI, lawful source, licence/access condition, acquisition date, screening decision and claim-level extraction. Do not redistribute publisher PDFs unless the licence explicitly permits it.

## What can and cannot be said now

Safe wording: **public-index title-screened candidates in a frozen reproducible corpus**, **OA or repository location automatically identified**, and **maximum publicly verifiable evidence level**.

Unsafe wording: **all papers**, **global publication count**, **complete literature**, **systematic-review included studies**, or **clinically mature**, unless the relevant protocol, screening and evidence criteria have been completed.

