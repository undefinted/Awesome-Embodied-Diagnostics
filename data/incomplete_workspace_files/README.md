# Incomplete workspace files / 不完整文件

这些文件由后来一次未完成的数据刷新留下，或无法通过 JSON 解析。它们被保留用于溯源和故障分析，但已经从对应的正常数据目录移出。

已确认问题：

- `bibliometrics/candidates.csv`：仅 73 条可解析记录，元数据期望 3,849 条候选。
- `bibliometrics/candidates.jsonl`：2,916 条有效记录并有 1 条损坏记录，元数据期望 3,849 条候选。
- `bibliometrics/included.csv`：仅 981 条可解析记录，完整 `included.jsonl` 有 1,461 条。
- `active_extension_v5/candidates_auto_screened.csv`：475 条可解析记录，元数据记录 3,710 条去重候选。
- 四个 `openalex*.json` 缓存无法完成 JSON 解析。

不要用本目录中的文件生成综述数字。若需恢复，应重新运行检索并写入新的版本化目录。

