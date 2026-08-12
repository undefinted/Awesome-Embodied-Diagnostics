# Embodied clinical detection — bilingual figure package

## 中文说明

本图件包用于论文中的具身医学检测分类与文献工作量展示。除用户明确要求全英文的主动观察闭环图外，其余主图均包含中文与英文两个版本。每张图提供 PNG（600 dpi）、SVG（文字已转路径，便于跨平台显示）和 PDF（矢量）三种格式。

计数采用双层证据设计：

- **核心下界（Core lower bound）**：具身动作与具体任务在标题中明确出现，优先保证精度。
- **扩展上界（Expanded upper bound）**：允许关键证据仅出现在摘要中，优先保证召回率。

因此，图中的区间不是统计置信区间，而是由纳入规则形成的“高精度下界—高召回上界”。建议论文正文以核心集作为主分析，以扩展集作敏感性分析。

## English notes

This package supports manuscript figures on the taxonomy and literature workload of embodied clinical detection. Every main quantitative figure is supplied in Chinese and English; the active-observation closed-loop schematic is English-only as requested. Each figure is exported as 600-dpi PNG, portable SVG (text converted to paths), and vector PDF.

The counts use two evidence tiers:

- **Core lower bound:** embodiment and the concrete task are explicit in the title, prioritizing precision.
- **Expanded upper bound:** qualifying evidence may appear only in the abstract, prioritizing recall.

The displayed range is therefore not a statistical confidence interval. It is a rule-based precision–recall sensitivity band. Use the core corpus for the primary manuscript analysis and the expanded set as a sensitivity analysis.

## Search protocol / 检索方法

- Databases: OpenAlex, Europe PMC, and a direct arXiv API search.
- Search fields: title and abstract; exact task phrases plus targeted broad combinations for low-volume families.
- Deduplication: DOI first, then canonicalized title.
- Unit: deduplicated publication record, not clinical trial, product, or deployed system.
- Classification: one primary task per work.
- Cutoff: 2026-08-06; 2026 is year-to-date.
- Corpus: 5,125 raw records → 3,868 deduplicated candidates → 812 core / 1,475 expanded records across all classes.
- Direct arXiv contribution: 148 raw hits; 118 included records carried an arXiv source; 12 were arXiv-only. The net corpus increase was 14 records because two additional OpenAlex-indexed records were recovered after richer arXiv abstract metadata corrected earlier exclusions.

## Reviewer-facing limitations / 审稿风险与限制

1. “All work” means all records captured within this reproducible search boundary; it is not a claim of universal bibliographic exhaustiveness. Subscription databases and non-English terminology may add records.
2. Expanded counts are intentionally sensitive and may include adjacent applications; they should not be interpreted as an exact prevalence estimate.
3. Sparse families are especially terminology-sensitive, so a zero count means “no eligible record retrieved under this protocol,” not proof that no prototype exists.
4. One-primary-task assignment avoids double counting but suppresses genuine multi-action systems.
5. Publication counts measure research activity, not clinical maturity, regulatory clearance, trial quality, or deployment scale.
6. The 2026 point is incomplete and must not be directly compared with full calendar years.

## Source files / 源数据

- `source_data_all_task_counts_bilingual.csv`: all 24 task counts and definitions.
- `source_data_active_annual_counts_bilingual.csv`: annual active-observation counts by task and evidence tier.
- `active_observational_records_1015.csv`: auditable record-level active-observation corpus.
- `active_observational_search_queries.csv`: database-specific search strings and retrieval counts.
- `arxiv_increment_audit_by_task_bilingual.csv`: raw arXiv hits, arXiv-only inclusions, and net changes by task.
- `arxiv_added_or_metadata_recovered_records_14.csv`: the 14 net-added or metadata-recovered records.
- `summary_statistics_bilingual.csv`: headline derived statistics.
- `bibliometric_metadata.json` and `task_definitions_bilingual.json`: machine-readable protocol metadata.
