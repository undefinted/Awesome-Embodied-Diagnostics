# Provenance / 溯源说明

## 已按原文件恢复的代码

以下文件从现存工作区直接复制，未改写其研究逻辑：

| 文件 | 作用 |
|---|---|
| `scripts/collect_bibliometrics.py` | 从 OpenAlex、Europe PMC、arXiv 检索、去重和规则筛选 24 类任务 |
| `scripts/make_bilingual_figures.py` | 较早版双语分类与工作量图 |
| `scripts/make_bilingual_figures_arxiv_v2.py` | 包含直接 arXiv 检索的双语图 |
| `scripts/make_publication_style_figures.py` | 期刊风格图形和机器质检 |
| `scripts/make_annual_heatmap_taxonomy_audit.py` | 年度热力图与任务分类缺口审计 |
| `scripts/collect_active_extension_v5.py` | A8–A10 扩展检索 |
| `scripts/finalize_active_ten_task_v5.py` | 合并 A1–A10 稳定筛选记录并生成年度源数据 |
| `scripts/make_active_10task_annual_chart_v5.py` | 生成十任务年度热力图和年度总量图 |
| `scripts/build_active_10task_package_v5.py` | 生成 Excel、PDF、质检和打包结果 |
| `scripts/workbooks/build_workbook.mjs` | 生成较早版任务与工作量工作簿 |
| `scripts/workbooks/build_taxonomy_audit_workbook.mjs` | 生成分类审计工作簿 |

原代码的 SHA-256 值记录在 `provenance/ORIGINAL_CODE_SHA256SUMS.txt`。

## 数据状态

- `bibliometrics_v2_arxiv` 的 `candidates.jsonl`、`included.jsonl`、CSV 与元数据计数一致，是当前较完整的核心快照。
- `active_extension_v5/included_auto_screened.csv` 含 1,902 条自动纳入记录；最终 A8–A10 结果还经过脚本中显式记录的人工 ID 判定。
- 早期 `bibliometrics` 的 `included.jsonl` 仍完整，但其 CSV 和候选 JSONL 在后续未完成运行中被截断。
- 四个 API JSON 缓存无法完成 JSON 解析，已连同截断文件移入 `data/incomplete_workspace_files/`。

这些移动只发生在本交付副本中；原工作区文件没有被删除或覆盖。

## 未恢复内容

现存工作区中没有 `.pptx/.pptm/.odp`，也没有检测到用于生成“医学检测具身智能_完整优化版.pptx”的独立 PowerPoint 源码。因此：

- 本包提供的是此前文献计量、数据整理、制图和工作簿代码；
- 不能把任何后来重写的 PPT 脚本表述为当时实际运行的原代码；
- 如果用户重新提供 PPT，可在后续版本中将其和新的可复现生成代码加入仓库。

## 新增的归档文件

根目录 README、依赖清单、Git 配置、开放发布检查表和清单文件是本次为归档与 GitHub 管理新增的辅助材料，不是此前分析时运行的研究代码。

