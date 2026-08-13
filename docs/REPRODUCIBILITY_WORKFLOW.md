# 可复现运行说明

## 强制规则

任何进入 PPT、论文或 GitHub README 的统计或图表，必须在根目录 `产物与代码映射.csv` 中登记：产物、输入、生成代码、检索日志、方法说明、冻结日期和可复现状态。未登记或标记为 `manual_curated`、`provenance_missing` 的结果不得作为自动可复现统计使用。

## P5 扩展公开版图

生成链：

1. `05_可复现代码/build_p5_comprehensive_public_landscape.py`
   - 查询 OpenAlex、Europe PMC、Crossref、arXiv；
   - 保存 API 查询状态；
   - DOI 优先、规范题名其次去重；
   - 建立高召回题名/摘要候选池；
   - 识别公开全文位置。
2. `05_可复现代码/screen_p5_high_recall_candidates.py`
   - 任务级题名规则精筛；
   - 排除治疗、手术、纯静态分类和非医学用途。
3. `05_可复现代码/make_p5_public_visible_available_figure.py`
   - 读取冻结汇总 CSV；
   - 生成紫色 public-visible、绿色 public-available 的 SVG。
4. `05_可复现代码/rasterize_svg.mjs` 使用 `sharp` 将指定 SVG 栅格化为 PNG。

网络检索可能受数据库更新、API 排序和 429 限流影响。正式冻结版本必须同时保存 query log、运行日期和输出 CSV；不能只保存图片。

## P5/P9/P13 旧版公开题名图与成熟度图

GitHub 仓库运行：

```powershell
python scripts/build_public_title_screened_landscape.py
node scripts/make_public_presentation_figures.mjs
node scripts/rasterize_public_figures.mjs
```

输入为冻结多来源文献库、题名规则和成熟度矩阵。当前目录保存了脚本副本，但部分脚本使用 GitHub 仓库目录约定，因此推荐在仓库中执行。

## 工作簿

`公开证据与PPT工作簿.xlsx` 由 `build_public_evidence_workbook.mjs` 生成。输入是任务计数、领域计数、成熟度矩阵、已核验一手证据和题名筛选记录。

## 验证

```powershell
powershell -ExecutionPolicy Bypass -File 05_可复现代码/reproduce_current_outputs.ps1 -Target verify
```

验证器检查所有登记产物、输入和代码是否存在，并输出 SHA-256。

## 当前非自动生成数据

`P7_主动机器人光学光谱扫描_专项数据.csv` 与 `P7_主动机器人光学光谱扫描_硬件与临床任务.csv` 是基于公开原始来源的人工 claim-level 整理表，目前没有自动生成脚本。它们可以作为人工证据表使用，但不能声称是自动检索所得或完整计量结果。后续若用于数量统计，应另建检索、筛选和生成程序。
