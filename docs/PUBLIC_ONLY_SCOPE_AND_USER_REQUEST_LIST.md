# 公开可访问版综述：范围声明与用户获取清单

更新日期：2026-08-13

## 当前范围声明

当前版本采用 **publicly available evidence scope**。允许纳入并据以核验的材料包括：

- 开放获取的出版社全文；
- PubMed Central / Europe PMC 全文；
- arXiv、medRxiv、bioRxiv 等公开预印本，并明确其未同行评议状态；
- 作者接受稿和机构知识库版本；
- 公开试验注册、监管文件、官方指南和标准公开页面；
- 公开摘要只能支持摘要直接报告的信息，不能替代全文方法学判断。

付费数据库和订阅全文不计入当前公开版覆盖分母。因此，所有计量结果应表述为：

> a structured map of publicly available evidence

而不是 exhaustive global literature count 或 systematic review of all published evidence。

## 需要用户后续获取的数据库

### 第一优先级

1. **IEEE Xplore**：补机器人控制、主动感知、力反馈、TMS、微流控和工程会议论文。
2. **Scopus**：跨领域去重、引文追踪及会议/期刊覆盖敏感性分析。
3. **Embase**：医疗器械、诊断研究、会议摘要和 Emtree 扩展。
4. **Web of Science Core Collection**：独立引文追踪和会议论文覆盖核查。

### 第二优先级

- Engineering Village / Compendex：工程、机电和器械会议补充。
- ACM Digital Library：环境智能、HCI、临床 Agent 和交互式感知。
- CINAHL：家庭监测、护理工作流、床旁实施和可用性。

### 可选

- PsycINFO：依从性、行为响应和心理健康自适应支持。
- ProQuest Dissertations & Theses：早期系统和灰色文献，仅作引文追踪。

精确导出字段、获取路径和网址见 `data/access/subscription_database_requests.csv`。数据库导出必须同时记录：数据库、平台、完整检索式、检索日期、时间范围、过滤器、原始命中数和导出格式。

## 当前需要获取的文章/标准

人工复核后，当前清单包含 12 项：

- 3项 P1：如果要在正文作强方法学或详细结果陈述，应优先获取；
- 4项 P1：属于重要架构/设备例证，但可用公开摘要作有限陈述，或用开放文献替换；
- 4项 P2：只有保留为中心背景或支持技术时才需要；
- 1项 P3：当前诊断范围不建议为其付费。

完整逐项清单见 `data/access/manually_vetted_article_acquisition_queue.csv`。它已删除两个自动审计假阳性：

- smart reflex ferritin 论文已有 PMC 全文；
- STARD-AI correction 有公开出版社记录，且无需单独购买全文。

## 获取后的文件管理

- 付费或版权受限 PDF 放在 `local_only/papers/`，不得提交到 GitHub。
- 建议命名：`FirstAuthor_Year_ShortTitle_DOI.pdf`。
- 在证据表记录合法获取方式：institutional subscription、document delivery、author manuscript 或 author request。
- 原始数据库导出放入 `local_only/database_exports/<database>/<YYYY-MM-DD>/`，不改动原文件；另建立 processed 副本进行去重。

## 当前公开版写作规则

1. 公开全文已核验：可以提取方法、样本量、比较对象、结果和局限。
2. 只有公开摘要：只能陈述摘要明确报告的事实，并标注 abstract-level verification。
3. 只有书目信息：仅用于列入候选池，不能支撑正文结论。
4. 订阅资源可能改变结论时：写入 sensitivity-extension backlog，不假定结果方向。
5. 不把缺少公开全文解释为低质量或负面证据；它只是当前证据范围限制。

