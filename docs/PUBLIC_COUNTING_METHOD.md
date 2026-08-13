# Public-source counting and evidence maturity

Updated: 2026-08-13

## What the count means

The presentation uses a reproducible **public-index title-screened candidate count**, not an estimate of all publications and not a systematic-review included-study count. The frozen source snapshot contains 359 records retrieved from Europe PMC, OpenAlex, Crossref and arXiv and deduplicated by DOI or normalized title. `scripts/build_public_title_screened_landscape.py` applies a conservative task-specific title rule to this corpus.

The numerator shown for a task is the number of unique records whose title contains both an embodiment concept and the diagnostic task concept after explicit neighbouring-task exclusions. The adjacent lighter bar is the number for which OpenAlex or an explicit repository URL automatically identifies an open-access or repository location. The latter is a discovery indicator, not a manually verified licence audit.

## What the count does not mean

- It is not the global number of papers on the task.
- It is not the number of studies that would survive full-text inclusion screening.
- It is not a measure of loop completeness, technical performance or clinical maturity.
- A zero means no record was found under this frozen corpus and rule; it does not prove that no study exists.

False negatives are expected when a relevant title omits the robot, autonomy or task term. False positives can remain when a title satisfies the rule but the full text does not implement an embodied diagnostic loop. Journal publication therefore requires duplicate human title/abstract screening, full-text eligibility assessment and a database sensitivity extension.

## Independent maturity axis

Evidence maturity is assigned from the strongest publicly verifiable primary evidence located for the task:

0. no strict public-index candidate located;
1. simulation or engineering prototype;
2. phantom or in vitro;
3. ex vivo or animal;
4. human feasibility, reliability or observational study;
5. prospective multicentre, controlled trial or routine-use cohort;
6. randomized patient-outcome evidence or established regulated deployment.

The maturity level is deliberately independent of publication volume. For example, robotic venipuncture has only 12 strict title-screened candidates in the frozen public corpus, but a 2026 multicentre routine-use cohort enrolled 1,633 patients. Conversely, robotic palpation has more title-screened candidates but remains dominated by phantom and preclinical validation.

## Reproduce

```powershell
python scripts/build_public_title_screened_landscape.py
```

Outputs are written to `outputs/public_landscape/`. Presentation-ready synthesis is in `data/presentation/public_evidence_maturity_matrix.csv`.
