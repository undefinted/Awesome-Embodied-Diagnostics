# Bilingual figure policy

Every current audience-facing chart in `figures/public_evidence/` must have:

- an editable Chinese SVG and a matching English SVG suffixed `_en`;
- a high-resolution PNG preview for each SVG;
- identical data inputs, counting fields, snapshot dates and visual encodings;
- fully translated titles, labels, legends, footnotes and evidentiary caveats.

The English version is a presentation translation, not an independent analysis.
`scripts/validate_bilingual_figures.py` fails when either-language files are missing.
Run `scripts/reproduce_bilingual_public_figures.ps1` after changing a chart or its data.

Superseded charts retained for provenance remain explicitly documented as historical
or retrieval-audit artifacts; bilingual availability does not make them the preferred
figure for scientific interpretation.
