# Evidence Synthesis Codebook

## Evidence questions tied to the manuscript

1. **What closes the loop?** Record the observation, evidence-conditioned decision, physical or human-mediated action, returned feedback and stopping rule.
2. **How mature is the evidence?** Keep engineering, phantom, animal, volunteer, retrospective, prospective, diagnostic-accuracy, randomized and patient-outcome evidence distinct.
3. **Who has authority?** Separate device execution, supervised execution, human-mediated action and human-controlled assistance.
4. **What is the consequence of acting?** Separate repeatable reversible sensing from stimulation, specimen-only operations and invasive single-authorized actions.
5. **Does the evidence support translation?** Extract operating domain, comparator, diagnostic outcome, safety, failure, abort, override, handover, workflow and patient-relevant outcomes without converting missingness to zero.

## Translational evidence stages

- `T0`: transferable technical precedent outside direct diagnostic validation.
- `T1`: bench, phantom, ex vivo, animal or retrospective method validation.
- `T2`: human feasibility or technical validation without prospective clinical-performance evidence.
- `T3`: prospective comparative, randomized-feasibility or clinical-performance evaluation.
- `T4`: demonstrated patient benefit or clinical utility in the intended pathway.

The stage records what was evaluated. It is not a quality score and does not replace design-specific risk-of-bias assessment.

These questions map directly to the manuscript's conceptual definition, application taxonomy, risk-gated loop, simulation-to-clinic pathway and evaluation sections.

## Units of analysis

- `report_id`: one publication or public report.
- `study_id`: one empirical study, which may have multiple reports.
- `system_id`: one platform or system, which may have multiple studies.
- participant, specimen and procedure denominators remain separate.
- development-data volume remains separate from clinical denominators.

The current representative seed has report identifiers only. Study and system linking must be completed during full-text extraction before publication counts can be interpreted as independent systems or evaluations.

## Evidence roles

- `direct_embodied_diagnostic`: current evidence directly selects a later diagnostic acquisition or testing action.
- `bounded_embodied_acquisition`: feedback closes acquisition or verification within a bounded task, without an unrestricted strategic loop.
- `human_mediated_embodied_diagnostic`: evidence prompts a person to execute the next diagnostic action.
- `assisted_sampling_evidence`: robotic assistance supports diagnostic sampling, but strategic acquisition remains human controlled.
- `technical_precedent`: relevant closed-loop capability outside direct clinical diagnosis.
- `nonadaptive_comparator`: sensing, robotics or AI is present, but current evidence does not alter later acquisition.

## Verification states

- `verified_identifier`: a DOI, PMID or PMCID resolves to the source record. Title similarity is retained as a QC signal, not used to reject documented shorthand titles.
- `all_numeric_strings_found`: every extracted numeric token occurs in retrieved primary-source text. This is string-level QC only.
- `manual_primary_record_check`: a human-readable primary record resolves a representational mismatch, such as a number written in words.
- `partial_numeric_string_support` or `numeric_strings_not_found`: the value is withheld from the generated manuscript table pending context review.
- `unverified`: no claim or metadata is inferred.

## Synthesis gates

The generated selected-anchor table requires a stable-identifier match, explicit reviewer coding and an existing manuscript citation key. Numerical outcome claims are intentionally excluded until duplicate context verification is documented. A final included-study table additionally requires duplicate title/abstract decisions, adjudicated full-text decisions, report--study--system linkage, second-person extraction checks and design-specific risk-of-bias assessment.

## Reproducible outputs

- `machine_assisted_screening.csv`: prioritization only; blank reviewer and adjudication fields are preserved.
- `source_verification.csv`: resolved title, identifier, source URL, retrieval time and response SHA-256.
- `claim_string_audit.csv`: source hash, numeric tokens and missing-token status.
- `verified_evidence_ledger.csv`: joined seed, reviewer coding and provenance.
- `by_*.csv`: report-level descriptive counts with the denominator repeated in every row.
- `evidence_gap_matrix.csv`: direction by T0--T4 report counts for the representative seed.
- `by_outcome_category.csv`: multi-label reporting coverage for technical acquisition, diagnostic performance, analytical validity, safety, workflow, human factors and patient outcomes.
- `manuscript_table3.tex`: generated selected-anchor table with an explicit non-exhaustive boundary.

No generated output should be described as a complete systematic-review result until the remaining human review gates are satisfied.
