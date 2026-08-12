# Annual publication trajectory — statistical method / 年度发表轨迹统计方法

## 中文

1. 在 OpenAlex、Europe PMC 与 arXiv 中对24个任务分别进行题名/摘要检索，检索截止日为2026-08-06。
2. 先按 DOI 合并，再按规范化题名合并；期刊论文与其 arXiv 预印本只计算一次。
3. 仅使用“核心下界”记录，即具身主体和具体检测任务在题名中均明确出现。
4. 当一篇文献同时涉及多个动作时，只归入一个主要证据生成任务，不进行重复或分数计数。
5. 年份来自 OpenAlex `publication_year`、Europe PMC `firstPublicationDate` 或 arXiv `published`。若同一工作存在更早的 arXiv 预印本日期，且比期刊日期早不超过10年，则采用该更早日期；这一合理性窗口用于避免数据库中的异常年份覆盖正确日期。
6. 对每个年份执行整数计数：A1 为机器人超声，A2 为机器人内镜，A3–A7 合并为“新兴任务”。
7. 2026年仅统计到8月6日，图中以虚线和YTD标注，不与完整年度直接比较。

因此图中某年的纵轴值是“该年首次发表、跨库去重、进入核心集并归入该任务的文献篇数”，不是引用次数、系统数量或临床试验数量。

## English

1. Title/abstract searches were run separately for all 24 tasks in OpenAlex, Europe PMC and arXiv, with a cutoff of 6 August 2026.
2. Records were merged by DOI and then by canonicalized title; a journal article and its arXiv preprint contribute one work.
3. The trajectory uses only the core lower-bound corpus, where both embodiment and the concrete diagnostic task are explicit in the title.
4. Each work is assigned to one primary evidence-generating task; no duplicate or fractional counting is used.
5. The year is derived from OpenAlex `publication_year`, Europe PMC `firstPublicationDate`, or arXiv `published`. An earlier arXiv date replaces the journal date only when the lead is no more than ten years; this plausibility safeguard prevents anomalous metadata years from overriding a valid date.
6. Integer annual counts are calculated for A1 robotic ultrasound, A2 robotic endoscopy, and the combined A3–A7 emerging-task group.
7. The 2026 observation is year-to-date through 6 August and is shown with a dashed segment and YTD label.

Accordingly, each y-axis value is the number of deduplicated core works first published in that year and assigned to that task—not citations, systems, or clinical trials.
