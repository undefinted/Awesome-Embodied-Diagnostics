# Statistical protocol for Clinical Detection and Intervention

## Purpose

The protocol supports transparent scoping statistics for the three evidence-generation mechanisms and their 16 task families. It is designed for public-source landscape figures, not PRISMA-grade final inclusion counts.

## Sources and discovery

Discovery uses OpenAlex, Europe PMC and arXiv over a common 2000-01-01 to 2026-08-15 window. Every task has multiple short, inspectable concept-pair queries. Source records are retained with the query that retrieved them.

Crossref was tested but removed from corpus discovery because `query.bibliographic` is a fuzzy citation-resolution query and can report extremely large relevance-ranked result sets. Crossref may later enrich DOI metadata for already discovered candidates; it must not be interpreted as an exhaustive denominator.

Primary API documentation: [OpenAlex](https://help.openalex.org/), [Europe PMC web services reference](https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf), [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) and [arXiv API manual](https://info.arxiv.org/help/api/index.html).

## Screening safeguards

1. Every non-stopword query term must co-occur within a 96-character window in the title.
2. The title/abstract must contain the task-defining clinical route or evidence-generation concept.
3. The title/abstract must contain a controllable physical-carrier or physical-action signal, such as a robot, actuator, motorized or steerable device, probe/sensor positioning, scan trajectory, active locomotion, visual servoing, force control or explicit closed-loop/feedback control.
4. Reviews, protocols and neighbouring therapeutic/training tasks are rejected using recorded deterministic rules.
5. DOI is the primary deduplication key; normalized title is the fallback.

This high-precision title screen deliberately sacrifices sensitivity. It still requires manual full-text adjudication for whether diagnostic evidence actually changes the next physical action and whether sampling was performed rather than merely guided.

## Boundary rules

- 1.1: action changes where/how an in-vivo signal is observed; no deliberately evoked response and no removal of diagnostic material.
- 1.2: action deliberately perturbs the patient/tissue/physiology and the response is the evidence.
- 1.3: action physically removes or collects material and the ex-vivo specimen result is the evidence.
- A multimodal system can create multiple task–study pairs when distinct evidence-acquisition stages are reported. Mechanism and domain totals use unique works so these pairs are not silently double counted.

## Interpretation

The purple series is labelled **Title-screened candidate records**, not “included studies”. The green series is labelled **Of these: publicly accessible full text**. The gold series is labelled **Of these: published in 2021–2026**. Task families are ordered by the purple measure in descending order, with the green and gold measures used as deterministic tie-breakers. Named products/projects are maintained separately and are not added to literature bars unless represented by a retrievable publication.
