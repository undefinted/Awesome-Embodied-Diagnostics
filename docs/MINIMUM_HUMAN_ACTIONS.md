# Minimum human actions

This project uses code and AI assistance for retrieval, prioritization,
bibliographic verification, evidence pre-extraction, consistency checks,
synthesis drafts and manuscript maintenance. AI-produced decisions must remain
labelled as such and are not represented as independent human review.

## Actions that require an accountable person

1. **Authorize and access restricted services.** A person must sign in to, or
   obtain lawful institutional access to, subscription databases, publisher
   full text, Overleaf, OSF and journal submission systems. Credentials must not
   be placed in the repository.
2. **Accept authorship responsibility.** At least one accountable author must
   approve the review question, the final eligibility boundary, the submitted
   manuscript, the data-availability statement, competing-interest statement
   and any declaration of AI use. An AI system cannot be an author or accept
   these responsibilities.
3. **Make declarations and obtain permissions.** Authors must make truthful
   conflict-of-interest, funding, ethics and copyright declarations and obtain
   permissions for any reused figure or restricted material.
4. **Perform any human review promised in the manuscript.** If the manuscript
   states that two independent reviewers screened, extracted or assessed risk
   of bias, two real people must actually perform those tasks. AI agents cannot
   be reported as human reviewers. If that work is not performed, the Methods,
   claims and review label must be changed accordingly.
5. **Provide final scientific sign-off.** Before submission, an accountable
   author must inspect the evidence tables and a claim-to-source audit, resolve
   unresolved `NR`/`unknown` items, and confirm that clinical and safety claims
   do not exceed the cited evidence.

Reviewer names are not required in a double-anonymized manuscript. Screening
files may use stable role labels such as `R1`, `R2` and `R3`; any private mapping
between labels and people stays outside the public repository and submission
files.

## Work performed by code or AI assistance

Subject to the claim boundaries above, the project can automate or AI-assist:

- public-source searching, query translation drafts and update surveillance;
- import, normalization, identifier verification, deduplication and version
  linkage suggestions;
- relevance prioritization and clearly labelled AI eligibility assessments;
- structured pre-extraction with source locations and uncertainty flags;
- candidate report--study--system linkage;
- draft risk-of-bias signalling, citation chasing and missingness checks;
- descriptive analysis, tables, figures, PRISMA count reconciliation and
  manuscript drafting;
- DOI, title, year, citation-key and claim-string validation.

These outputs can reduce human workload but do not create evidence that is not
present in a source. Missing or ambiguous information is recorded as `NR`,
`unknown` or `requires_author_confirmation`.

## Submission boundary

An AI-only evidence map can be published as an explicitly AI-assisted,
structured narrative resource. It must not claim duplicate independent human
screening or the assurance level of a conventional systematic review. To make
those claims, the corresponding human procedures remain required.
