# P5–P29 逐页施工清单

适用画布：16:9。全篇统一采用顶部标题区 0–12%、主体区 12–91%、底部来源/页码区 91–100%。正文中文为主，英文只作副标题或关键词。紫色表示 observation/state，蓝色表示 action，绿色表示 feedback/evidence，橙色表示 boundary/gap。

> 使用规则：每页只保留一个 takeaway；论文数字放入证据卡，不把候选文献数量画成成熟度；所有系统图片优先使用作者开放许可图、机构新闻图或自行重绘示意图，并在页脚标 DOI。

## Clinical detection and intervention

### P5｜主动观察式检测：研究版图与证据边界

- 左上 12–60%：横向条形图 `figures/application_support/clinical_task_candidate_counts.png`，只显示任务归一化后的候选量。
- 右上 60–96%：三张证据卡——机器人超声（人体）、眼科 OCT（人体）、磁控胶囊（人体/随机质量控制）。
- 下方 12–96%：橙色边界条：“候选量 ≠ 纳入论文数 ≠ 临床成熟度”。
- 数据：`clinical_task_candidate_counts.csv`；证据：甲状腺/颈动脉超声、RobOCTNet、MCCG AQCS。
- 一句话：主动观察已经形成研究集群，但闭环深度从自主对准、质量提示到自主下一视角差异很大。

### P6｜方向一：不确定性驱动的机器人超声

- 左侧 8–58%：自绘闭环——实时图像/接触力 → 切面质量与不确定性 → 位姿/力控制 → 新切面。
- 右侧 60–96%：上下两张证据卡。上：甲状腺研究的样本与时间；下：UltraBot 的示范数据、成功率和重复性。
- 底部：硬件条（7-DOF 机械臂、临床探头、六维力、RGB-D/人体跟踪、急停）。
- 不使用：单独的超声分割准确率作为具身证据。
- 一句话：下一步不是“自动扫完固定轨迹”，而是以切面质量、风险和信息增益决定下一动作与停止。

### P7｜方向二：质量/覆盖驱动的光学与内镜扫描

- 左侧 8–46%：两幅场景示意——机器人 OCT 主动对准；磁控胶囊覆盖胃内解剖区域。
- 中部 48–72%：能力阶梯：自主对准 → 覆盖/质量评估 → 复扫提示 → 系统自主复扫。
- 右侧 74–96%：三条证据：contactless robotic OCT、RobOCTNet、MCCG AQCS RCT。
- 下方橙条：AQCS 的运动由操作者执行；RobOCTNet 分类未驱动复扫。
- 一句话：最有价值的研究缺口是把质量和病灶不确定性真正接回视点选择、复扫和停止条件。

### P8｜响应式交互诊断：定义与闭环

- 中央 12–82%：大环图——选择刺激位置/幅度/速度 → 施加机械/神经刺激 → 测量力学/生理响应 → 更新隐状态。
- 环图下方三例：触诊/刚度、关节/肌张力、TMS–MEP。
- 右下边界卡：只移动传感器观察图像属于主动观察；主动压缩并利用形变属于响应式。

### P9｜响应式交互：已有工作与证据成熟度

- 左 8–56%：响应任务候选条形图，突出触诊占主导。
- 右 58–96%：成熟度阶梯：幻模 → 动物/离体 → 小样本人体 → 前瞻临床；把各任务贴在相应层级。
- 下方边界条：关节松弛度和痉挛机器人多为标准化测量，不等于自适应检查策略。
- 数据：`clinical_task_candidate_counts.csv`、`domain_coverage_audit.csv`。

### P10｜方向一：多模态触诊与弹性测绘

- 左 8–58%：二维 sequential-search 示意，显示稀疏触点、后验刚度图和下一触点。
- 右 60–96%：两张证据卡——bimodal tactile tomography（幻模、≤30 次迭代）和 minimally invasive palpation（动物组织、肿瘤模拟物）。
- 底部实验条件：力/扭矩传感器、OCT/触觉探头、组织幻模、呼吸运动平台、金标准成像。
- 一句话：前沿是用不确定性选择触点，而不是更密地扫描整块组织。

### P11｜方向二：神经刺激—响应主动映射

- 左 8–60%：头皮点位图和闭环——选点 → TMS → MEP/EMG/EEG → GP 后验 → 下一点。
- 右 62–96%：自动 hotspot 与 GP active mapping 两张证据卡；另放 reliability 警示卡。
- 下方：数据与硬件（机器人 TMS、导航、EMG、个体 MRI、刺激安全约束）。
- 一句话：机器人定位不是闭环本身；响应必须改变下一刺激位置或强度。

### P12｜采样式交互检测：定义与闭环

- 中央大流程：定位 → 进针/取样 → 充分性/质量检查 → 接受、重定位或复采 → 实验室结果。
- 左下三种证据：组织、细胞、体液/拭子。
- 右下边界：到达目标是 acquisition success；获得可诊断样本才是 diagnostic success。

### P13｜采样式交互：已有工作与断点

- 左 8–52%：任务候选条形图（活检、胶囊采样、采血、拭子）。
- 右 54–96%：四列链条并用红色断点标注：靶区定位｜采样动作｜样本充分性｜诊断结果回流。
- TARGET 支气管镜、ADOPT 采血、机器人拭子作为三张小证据卡。
- 一句话：多数系统把闭环停在“完成采样”，最关键断点是样本充分性反馈。

### P14｜方向一：样本充分性感知的机器人活检

- 左 8–58%：建议系统架构——影像定位、针尖跟踪、快速充分性传感/ROSE、接受或复采决策。
- 右上：现有证据卡（TARGET 等）只支持导航与诊断率边界。
- 右下：可执行研究设计：组织幻模 → 离体组织 → 动物 → 人体可行性；终点为可诊断样本率、针次、并发症和时间。
- 不应写：现有机器人已自动根据病理结果重采。

### P15｜方向二：静脉采血与拭子采样

- 左半：ADOPT 流程与临床数据卡；突出可见静脉的一次成功率和不良事件。
- 右半：拭子机器人流程、速度与成功率，并放患者耐受/样本质量空缺卡。
- 底部横条：近期可转化价值在采集可靠性与工作流；完整诊断闭环仍需要结果回流。

## Laboratory diagnostics and assay development

### P16｜实验室具身诊断：样本—仪器—结果闭环

- 主体为三层环：物理执行层（移液/液滴/仪器）—状态层（质控/样本质量/异常）—决策层（复检/反射/改协议）。
- 右侧边界卡：自动化 ≠ 自适应；报告放行 ≠ 物理闭环。
- 底部列出四个子任务：异常路由、可编程微流控、自驱动 assay、主动显微/培养。

### P17｜结果驱动的复检、反射与异常恢复

- 左 8–55%：结果流转决策树（放行/复核/复检/反射/升级）。
- 右 57–96%：LIS 规则、ML autoverification、smart reflex 三张证据卡。
- 用虚线区分软件路由与实体复检；只有仪器实际复测并反馈才闭合物理环。
- 一句话：最可实施的方向是为异常恢复建立限定动作集，而不是让模型自由开单。

### P18｜可编程微流控：从动作纠错到检测闭环

- 左 8–58%：液滴移动失败—视觉/阻抗检测—重试/改道—检测结果示意。
- 右侧：2011 feedback DMF、2023 AI magnetic DMF、ferrobotic swarms 三张卡。
- 底部硬件：DMF/磁操控板、相机/阻抗、控制电子学、温控/读出、标准品。
- 一句话：这里的 embodied loop 最明确，但目前多证明执行可靠性，不等于临床 test-selection 效用。

### P19｜自驱动检测开发：选择下一实验

- 左 8–62%：objective → protocol → robot execution → assay readout → Bayesian update → next experiment。
- 右 64–96%：SAMPLE/生物 assay/细胞培养案例卡，按“诊断 assay”“生物发现”“工艺开发”上色区分。
- 底部：评价指标为达到目标性能所需实验次数、失败恢复、跨平台复现和临床样本验证。

### P20｜实验室方向优先级

- 主体 12–82%：2×2 矩阵，横轴物理闭环可验证性，纵轴临床价值；点位为反射复检、DMF 纠错、自驱动 assay、跨仪器恢复、主动显微。
- 右上加推荐标签：跨仪器异常恢复、结果驱动的 reflex/retest。
- 数据来自 `domain_coverage_audit.csv`，定位是证据综合判断，不伪装成定量 meta-analysis。

## Everyday embodied monitoring and adaptive support

### P21｜日常具身监测：定义与闭环

- 主体环：连续/环境感知 → 个人状态与上下文 → 异常/不确定性 → 提问、提高采样、家庭检测或转人工 → 新证据。
- 左下：可穿戴/植入；中下：环境/无接触；右下：家庭检测/支持。
- 边界：持续记录或一次报警本身不是完整闭环。

### P22｜日常监测证据版图

- 左 8–55%：证据阶梯，放 Apple Heart、PD nocturnal breathing、ambient vital signs、DETECT-AHEAD、EQUAL。
- 右 57–96%：`figures/application_support/coverage_status_by_domain.png` 或五张简化证据卡。
- 下方：测量有效性、依从性、隐私/旁观者、连接性四个风险标签。
- 一句话：大样本检测证据不少，但“异常后主动确认”才接近具身诊断闭环。

### P23｜方向一：个人基线驱动的纵向检测

- 左 8–62%：个人时间序列图，群体阈值和个体基线并列；标出偏离与恢复。
- 右 64–96%：COVID 可穿戴、PD 呼吸、wearable-to-lab prediction 三张卡。
- 底部：需要区分疾病变化、行为、治疗、传感器漂移和缺失。
- 一句话：个人化 state estimation 是闭环的状态层，不自动构成 embodied action。

### P24｜方向二：异常后的主动确认

- 左半：DETECT-AHEAD 漏斗——450 随机 → 118 提示 → 61 完成 → 19 阳性。
- 右半：EQUAL RCT——437 随机，AF 9.6% vs 2.3%；补 Apple Heart 作为大规模观察性背景。
- 下方：下一动作菜单（提问、提高采样、单导 ECG、家庭试剂、临床升级）。
- 一句话：主动确认能把被动监测变成证据获取，但依从性和人工确认是闭环性能的一部分。

### P25｜方向三：检测—支持—再评估生态

- 主体为 ecosystem 图：患者/家庭—设备—临床团队—实验室—紧急服务。
- 每条连接标注失败模式：延迟、缺失、冲突、误报、无法接触患者。
- 右下安全卡：bounded action、safe degraded state、override、offline fallback。
- 自动胰岛素等可作成熟控制参照，但必须注明其主要是治疗系统，不代表一般诊断生态已成熟。

## Synthesis

### P26｜跨领域比较：闭环闭在哪里

- 全页 5×3 矩阵：行=感知/状态/动作/反馈/人类角色；列=临床、实验室、日常。
- 每格最多两行；用红点标最常见断点：主动观察的 next-view、采样的 adequacy、实验室的 cross-instrument recovery、日常的 confirmation adherence。
- 数据：`application_evidence.csv` 与 `domain_coverage_audit.csv`。

### P27｜优先研究切入点

- 主体二维气泡图：横轴 12–24 个月可验证性，纵轴 consequential uncertainty reduction；气泡大小为所需硬件/临床协作负担的反向编码。
- 推荐四项：超声质量驱动复扫、主动触诊、活检充分性、实验室异常恢复；日常主动确认作为第五项临床合作方向。
- 右侧小卡写选择标准，不把判断称为客观排名。

### P28｜阶段性研究路线

- 横向四阶段：数据回放/仿真 → 幻模/离体 → 人体可行性 → 前瞻工作流试验。
- 每阶段下方同时放技术终点、临床终点、安全门槛和退出条件。
- 顶部加“权限随证据递增”，底部加日志、人工接管和失败病例库贯穿全程。

### P29｜结论

- 中央只放一句主结论：Embodied diagnostics = adaptive evidence acquisition, not a device category.
- 下方三短句：闭环分析单位；证据成熟度不均；评价 consequential uncertainty 与患者相关决策。
- 右下二维码可指向私有仓库；公开前替换为 release/DOI 链接。

## 逐页材料索引

- 一手证据表：`data/presentation/application_evidence.csv`
- 任务覆盖审计：`data/presentation/domain_coverage_audit.csv`
- 检索式登记：`data/presentation/search_strategy_registry.csv`
- 候选计量：`outputs/application_landscape/*.csv`
- 自绘图：`figures/application_support/`
- 研究工作簿：`outputs/application_landscape/application_research_workspace.xlsx`
- 详细内容稿：`docs/PRESENTATION_SLIDE_SUPPORT.md`

