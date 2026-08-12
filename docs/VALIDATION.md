# Validation report / 验证记录

归档日期：2026-08-12。

## 源码检查

- 9/9 Python 文件通过 `py_compile`。
- 2/2 `.mjs` 文件通过 `node --check`。
- 交付副本与原工作区源码逐文件二进制比较一致。
- 在代码、配置和说明文件中未检测到显式 API key、密码、Bearer token 或私钥模式。

## 数据一致性

`bibliometrics_v2_arxiv`：

- candidates JSONL：3,868，和元数据一致；
- included JSONL：1,475，和元数据一致；
- candidates CSV：3,868，和元数据一致；
- included CSV：1,475，和元数据一致。

`active_extension_v5`：

- included_auto_screened CSV：1,902，和元数据一致。

不一致或无法解析的文件已经移入 `data/incomplete_workspace_files/`。

## 端到端抽查

在临时干净目录中成功执行：

```text
finalize_active_ten_task_v5.py
make_active_10task_annual_chart_v5.py
build_active_10task_package_v5.py
```

机器质检结果为 PASS，最终十任务语料为 551 条去重记录；年度行数、年度合计、重复 DOI/题名、arXiv 纳入和 A8–A10 判定完整性检查均通过。

由于测试目录未安装/复制 Noto Sans CJK SC，中文图重绘时出现缺字警告；这不是数据或代码执行失败。使用原文档指定字体即可恢复中文渲染。

