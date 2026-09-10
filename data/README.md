# Data / 数据说明

| 目录 | 状态 | 主要内容 |
|---|---|---|
| `bibliometrics_v2_arxiv/` | 当前首选快照 | 24 任务、三数据库、候选和纳入记录、检索日志、API 缓存 |
| `active_extension_v5/` | 扩展检索 | A8–A10 自动筛选与稳定纳入表 |
| `bibliometrics/` | 早期版本，部分可用 | 元数据、任务定义、查询日志和完整 `included.jsonl` |
| `incomplete_workspace_files/` | 不可分析 | 截断 CSV/JSONL 和无法解析的 API 缓存 |
| `review/search_runs/2026-09-10/` | 冻结检索快照 | 公共数据库检索、查询日志、候选队列、机器辅助筛选和质量审计 |
| `review/search_runs/2026-09-10-public-v3/` | 当前首选公共检索 | 28 个检索族、84 个无截断 source-query 组合、原始检查点、精确检索式、全量人工筛选账本和质量审计 |
| `review/full_text_screening.csv` | 待人工填写 | 双人全文纳排、单一排除理由和裁决记录 |
| `review/study_system_linkage.csv` | 待人工填写 | report--study--system 关联及其判断依据 |
| `review/risk_of_bias_assessment.csv` | 待人工填写 | 按研究设计选择工具的双人偏倚风险判断 |
| `review/citation_chasing.csv` | 待人工填写 | 前向/后向引文追踪、去重和筛选状态 |
| `review/search_source_registry.csv` | 当前状态 | 公共/订阅数据库的访问、检索、检索式验证和导出状态 |
| `review/evidence_characteristics.csv` | 人工编码输入 | 人群/材料、分母类型、设计、比较项、结局和转化阶段；尚待双人重复提取 |
| `review/outcome_category_coding.csv` | 人工编码输入 | 代表性证据种子的多标签结局域编码；不是全领域发生率 |
| `review/evidence_synthesis/` | 代表性证据锚点 | 标识符复核、响应哈希、数值字符串审计、编码账本、分层统计、证据缺口矩阵和正文表格源文件 |
| `review/nbe_table_benchmark/` | 表格设计基准 | 选定 Nature Biomedical Engineering 综述的表题/表头模式、来源 URL、时间戳与响应哈希；不是期刊普查 |

计数单位是跨数据库去重后的文献记录，不是机器人数量、实验数量或临床试验数量。预印本和期刊版本的合并逻辑见检索脚本。

正式综述发布前应重新评估：任务定义、排除规则、综述文章过滤、预印本—期刊关联、同一系统多论文问题，以及自动筛选的误纳/漏纳。
