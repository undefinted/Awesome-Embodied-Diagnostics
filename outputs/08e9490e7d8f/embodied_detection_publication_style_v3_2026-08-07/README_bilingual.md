# Embodied clinical detection — publication-style bilingual figures

This package contains journal-ready English and Chinese figures based on the arXiv-inclusive corpus. The quantitative data and cutoff are unchanged from the previous version; only visual design and terminology were revised.

## Main changes / 主要修改

- Standardized to 180-mm full-width biomedical-journal artwork.
- Replaced "core lower bound / expanded upper bound" with "strict title-explicit set / broad title/abstract set".
- Replaced stacked pale bars with filled/open dumbbell marks that remain interpretable in greyscale.
- Put all 24 tasks on a common log10(n+1) axis and retained exact values.
- Removed oversized in-figure titles and moved interpretation into bilingual captions.
- Exported PDF, SVG, 600-dpi PNG and 600-dpi LZW-TIFF.

## Files / 文件

- `Fig1` taxonomy: English and Chinese.
- `Fig2` workload by major class: English and Chinese.
- `Fig3` all 24 task families: English and Chinese.
- `Fig4` active observational sensing loop: English, as requested.
- `Fig5` active observational sensing landscape: English and Chinese.
- `Bilingual_Publication_Figure_Packet_2026-08-07.pdf`: nine-page combined packet.
- `publication_figure_specification_bilingual.md`: exact style contract.
- `figure_captions_bilingual.md`: manuscript-ready bilingual captions.
- Source CSV/JSON/record-level audit files and the complete plotting script.

## Interpretation note / 解释说明

The strict and broad sets are reproducible retrieval sets, not statistical lower and upper confidence limits. For a final systematic/scoping review, the manuscript's primary count should ideally be based on a fully screened and adjudicated corpus; the broad set can remain a sensitivity analysis.
