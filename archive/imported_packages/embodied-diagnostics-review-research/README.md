# Embodied Diagnostics and Therapeutics Review — research package

本仓库是综述 **From passive tools to active partners: embodied intelligence for diagnostics and therapeutics** 的可复现调研包。它把当前会话中能恢复的稿件、引用键、文献元数据、调研结果与重建的辅助代码集中到一个适合 Git/GitHub 管理的目录中。

## 先读：材料边界

- `manuscript/recovered_versions/` 是从本次工作区原样复制并规范命名的历史文本，共 7 份。
- `manuscript/drafted_sections/` 是本次会话中已经写出的 Ethics、Outlook 和 Conclusion 三段。
- `literature/references.csv` 与 `references.bib` 收录所有能从可见材料中提取的引用键，以及会话中使用过的补充文献；无法唯一核验的条目保留并明确标为 `unresolved`，没有猜测 DOI。
- `results/` 是脚本从上述输入重新生成的派生结果，不是实验或临床原始数据。
- `scripts/` 是为了让本包可复现而新建的辅助代码；此前没有可恢复的已执行分析代码、原始实验数据或统计模型输出。
- 论文 PDF 未打包。公开仓库应提交引用元数据与合法稳定链接，而不是未经许可再分发出版商 PDF。
- `sources/private_review_only/` 中两张用户提供的截图来源与再分发许可未知，默认不应推送到公开仓库。

完整来源说明见 [PROVENANCE.md](PROVENANCE.md)，公开前检查见 [OPEN_SOURCE_CHECKLIST.md](OPEN_SOURCE_CHECKLIST.md)。

## 目录

| 路径 | 内容 |
|---|---|
| `manuscript/recovered_versions/` | 可恢复的历史 LaTeX/文本版本 |
| `manuscript/drafted_sections/` | 当前会话补写的三个章节 |
| `literature/references.csv` | 主文献登记表，含核验状态和 DOI/URL |
| `literature/references.bib` | 由 CSV 生成的 BibTeX |
| `literature/citation_aliases.csv` | 重复引用键到规范键的映射 |
| `literature/search_log.csv` | 可继续追加的检索日志 |
| `literature/screening_log.csv` | 可继续追加的筛选日志 |
| `results/` | 文稿清单、引用使用、缺失引用和运行清单 |
| `scripts/` | 仅依赖 Python 标准库的复现脚本 |
| `sources/` | 辅助写作包与不可公开来源截图 |

## 快速复现

需要 Python 3.10+，无需第三方依赖。

```bash
make all
make test
```

或者：

```bash
bash scripts/run_all.sh
```

运行后会刷新：

- `literature/references.bib`
- `results/manuscript_inventory.csv`
- `results/citation_usage.csv`
- `results/missing_citations.csv`
- `results/section_word_counts.csv`
- `results/run_manifest.json`

## 推荐的 GitHub 初始化

```bash
git init
git add .
git commit -m "Initialize reproducible review research package"
```

首次公开前，请先处理 `OPEN_SOURCE_CHECKLIST.md` 中的作者身份、许可证、截图权利和未核验条目。代码以 MIT 许可提供；稿件、附件和第三方材料不自动受 MIT 许可覆盖。

