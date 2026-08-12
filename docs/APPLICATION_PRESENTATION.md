# Application presentation package

This package supports the group-meeting deck on applications of embodied intelligence in medical detection. It is organized around how diagnostic evidence is generated, not around robot morphology.

## Narrative

1. Active observational sensing: actions improve the next view or signal.
2. Response-based interactive diagnosis: controlled stimuli expose mechanical, physiological or functional state.
3. Sample-based interactive diagnosis: physical acquisition produces ex-vivo evidence.
4. Laboratory diagnostics: results redirect sample handling, testing or assay development.
5. Everyday monitoring: longitudinal state estimates trigger confirmation, escalation or bounded support.

The common evaluation question is whether feedback reduces clinically consequential uncertainty. Literature volume, autonomy and hardware sophistication are not used as substitutes for clinical maturity.

## Reproducible assets

- `data/presentation/application_evidence.csv`: claim-level evidence ledger used by the deck.
- `data/presentation/slide_plan.csv`: page-by-page communication job, layout and source plan.
- `scripts/presentations/rebuild_application_deck.mjs`: Artifact Tool round-trip build entry point.
- `presentations/医学检测具身智能_应用完整版.pptx`: versioned presentation output.

Numbers in the presentation should be read with the evidence-stage qualifier in the ledger. Bibliometric task counts are curated workflow outputs and not global publication totals.
