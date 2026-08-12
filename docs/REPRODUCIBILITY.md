# Reproducibility / 复现说明

## 环境

原运行环境的关键版本：Python 3.12.13、NumPy 2.3.5、pandas 2.2.3、Matplotlib 3.10.8、Pillow 12.2.0、pypdf 6.10.0、XlsxWriter 3.2.9。`requirements.txt` 冻结了主要 Python 依赖。

中文图形使用 Noto Sans CJK SC / Noto Sans SC。字体二进制未纳入本包；请在系统中安装该字体，或按照脚本预期放入：

```text
tmp/08e9490e7d8f/fonts/package/
tmp/08e9490e7d8f/fonts/merged/
```

字体缺失时脚本会退回 DejaVu Sans，中文可能显示不完整。

## 推荐复现顺序

### 只重绘现有结果

```bash
python scripts/make_bilingual_figures_arxiv_v2.py
python scripts/make_publication_style_figures.py
python scripts/make_annual_heatmap_taxonomy_audit.py

python scripts/finalize_active_ten_task_v5.py
python scripts/make_active_10task_annual_chart_v5.py
python scripts/build_active_10task_package_v5.py
```

### 重新执行数据库检索

```bash
python scripts/collect_bibliometrics.py \
  --out data/bibliometrics_v2_arxiv \
  --refresh

python scripts/collect_active_extension_v5.py
```

注意：第二个扩展检索脚本没有命令行 `--refresh` 开关，并使用固定路径。联网重跑前建议建立新分支或新数据快照，避免覆盖冻结数据。

## 工作簿脚本

两个 `.mjs` 文件依赖原运行环境中的 `@oai/artifact-tool`。该依赖不是本归档的一部分，也不应假定能从公共 npm 注册表安装。其中 `build_taxonomy_audit_workbook.mjs` 还保留了原始绝对路径，因此作为 legacy provenance 保存；若要公开复现，建议后续改写为 `openpyxl`/`XlsxWriter` 或公开可安装的 Node 库，同时保留原文件不变。

## 可复现边界

- 固定源数据可用于重绘既有图表。
- 联网检索结果不是逐字节可复现的，因为数据库索引、合并记录和引用数会变化。
- 规则筛选具有确定性，但检索召回与任务分类仍需人工审查。
- 生成文件时间戳、PDF 元数据及字体子集可能导致二进制校验值变化，即使视觉内容相同。
