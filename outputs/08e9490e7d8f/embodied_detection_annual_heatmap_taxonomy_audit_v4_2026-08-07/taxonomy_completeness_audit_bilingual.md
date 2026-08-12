# Taxonomy completeness audit / 细分任务完整性审计

## Conclusion / 结论

**EN.** The current 24-task set is not exhaustive. It is a high-precision searched working set whose rows mix sensing modality, anatomy and access route. A minimum evidence-supported revision expands the framework to 33 task families: A=10, R=12 and S=11. This is a defensible working taxonomy, not a claim that all future embodied diagnostic actions have been exhausted.

**中.** 当前 24 个任务并不全面。它是一个偏高精度的已检索工作集，且任务行混合了传感模态、解剖部位和进入路径。基于现有证据的最小修订为 33 个任务族：A=10、R=12、S=11。这是一套可辩护的工作分类，而非声称已经穷尽未来所有具身诊断动作。

## Recommended hierarchy / 建议层级

1. **Level 1 / 一级：** evidence-generating action — observe, stimulate-and-read-response, or acquire a sample. / 证据生成动作——观察、刺激并读取响应、或获取样本。
2. **Level 2 / 二级：** task family defined by the controlled action and evidence channel. / 由受控动作与证据通道定义的任务族。
3. **Level 3 / 三级：** anatomy, access route, disease and clinical setting. / 解剖部位、进入路径、疾病与临床场景。

This prevents the same paper from being duplicated merely because the anatomy or sensor modality differs. / 这样可避免仅因解剖部位或传感器模态不同而重复计入同一工作。

## Revision summary / 修订汇总

| Class / 大类 | Current / 当前 | Revised / 修订 | Net / 净增 |
|---|---:|---:|---:|
| A — Active observational sensing / 主动观察式检测 | 7 | 10 | +3 |
| R — Response-based interactive diagnosis / 响应式交互检测 | 8 | 12 | +4 |
| S — Sample-based interactive diagnosis / 采样式交互检测 | 9 | 11 | +2 |
| **Total / 合计** | **24** | **33** | **+9** |

## Major additions and corrections / 主要新增与修正

| Class | Decision / 决策 | Task or issue / 任务或问题 | Evidence status / 证据判断 |
|---|---|---|---|
| A | Add A8 / 新增 A8 | Robotic X-ray/CT and gamma/SPECT acquisition / 机器人 X-ray/CT 与 gamma/SPECT 采集 | Confirmed; combine at the action-family level and separate by modality at the application level. / 已证实；动作层合并，成像模态作为应用层细分。 |
| A | Split A3 → A3 + A9 / 拆分 A3 → A3 + A9 | Robotic microscopy / confocal endomicroscopy / 机器人显微 / 共聚焦内显微扫描 | Confirmed split: the present A3 label is ophthalmic/OCT-specific but its corpus already contains microscopy and non-ophthalmic work. / 已证实需拆分：当前 A3 标签偏眼科/OCT，但语料已含显微及非眼科工作。 |
| A | Add A10 / 新增 A10 | Embodied non-contact vital-sign monitoring / 具身式非接触生命体征监测 | Confirmed, with both mobile clinical prototypes and active geometry regulation. / 已证实，已有移动临床原型和主动几何调节工作。 |
| A | Refine A7 / 收紧 A7 | Optical/spectral/thermal surface sensing / 光学/光谱/热成像表面感知 | Retain, but exclude fluorescence-guided treatment/navigation papers that do not actively seek diagnostic observations. / 保留，但排除仅用于治疗/导航且不主动搜索诊断观察的荧光引导工作。 |
| A | Hold / 暂缓独立成类 | Automated ECG electrode placement / 自动化 ECG 电极放置 | Insufficient patient-side robotic literature to justify an independent family at present. / 当前患者侧机器人文献不足以支持独立任务族。 |
| R | Add R9 / 新增 R9 | Tone, spasticity, ROM and strength assessment / 肌张力、痉挛、关节活动度与力量评估 | Confirmed and clinically distinct from joint laxity provocation. / 已证实，且临床上不同于关节松弛度激发。 |
| R | Add R10 / 新增 R10 | Sensorimotor / proprioceptive robot assessment / 感觉运动 / 本体感觉机器人评估 | Confirmed; uses controlled target/force/position perturbations and quantitative responses. / 已证实；通过受控目标、力或位置扰动并量化响应。 |
| R | Add R11 / 新增 R11 | Balance / gait perturbation assessment / 平衡 / 步态扰动评估 | Confirmed, with a dedicated device taxonomy and clinical assessment literature. / 已证实，已有专门的设备分类和临床评估文献。 |
| R | Add R12 / 新增 R12 | Vestibular / oculomotor provocation / 前庭 / 眼动激发检测 | Confirmed but niche; the defining action is controlled head motion followed by eye-response measurement. / 已证实但较小众；核心动作为受控头部运动并测量眼动响应。 |
| R | Hold / 暂缓独立成类 | Quantitative sensory and pupillary stimulus-response testing / 定量感觉及瞳孔刺激-响应检测 | Conceptually fits response-based diagnosis, but robotic embodiment evidence is currently too sparse or device-only. / 概念上属于响应式检测，但机器人具身证据目前过少或仅为设备自动化。 |
| S | Add S11 / 新增 S11 | Stereotactic CNS biopsy / 立体定向中枢神经系统活检 | Confirmed and mature enough to require a separate family from generic percutaneous core biopsy. / 已证实，且成熟到应与通用经皮粗针活检分开。 |
| S | Split S9 → S9 + S10 / 拆分 S9 → S9 + S10 | Bone marrow versus body-cavity fluid aspiration / 骨髓采样与体腔液体穿刺抽吸 | Confirmed split: tissue/marrow acquisition and pleural/peritoneal/synovial fluid aspiration differ in target, access and evidence. / 已证实需拆分：骨髓/组织获取与胸腹腔或关节液抽吸的目标、路径和证据不同。 |
| S | Merge into S6/S7/S1 / 并入 S6/S7/S1 | Capsule liquid sampling, EUS-FNA/FNB, capillary blood / 胶囊液体采样、EUS-FNA/FNB、毛细血管采血 | Do not create separate action families yet; represent them as route/anatomy subtypes unless evidence volume and control architecture justify a split. / 暂不设独立动作任务族；先作为进入路径/解剖亚型，待证据量和控制架构支持后再拆分。 |

## Counting implication / 对计数的影响

**EN.** The annual heatmap in this package remains an A1–A7 figure because those seven families have a completed deduplication and screening workflow. Adding estimated counts for A8–A10 would create a non-comparable denominator. The correct next step is a retrospective rerun of the full search and screening protocol for all revised families.

**中.** 本包中的逐年热力图仍为 A1–A7，因为只有这七个任务完成了统一的去重和筛选流程。若临时估算 A8–A10 并直接加入，会造成分母不可比。正确做法是按修订后的所有任务重新回溯检索和筛选。

## Important current-corpus findings / 当前语料的重要发现

- A3 contains microscopy and non-ophthalmic records although its label is OCT/ophthalmic; this is a label-boundary problem. / A3 的标签为 OCT/眼科，但已有显微和非眼科记录，说明边界需拆分。
- R3 currently contains only a small knee-laxity cluster and misses spasticity, strength, balance and KINARM-style assessment. / R3 当前主要是少量膝关节松弛度工作，漏掉痉挛、力量、平衡及 KINARM 类评估。
- S5 contains generic breast/lung/percutaneous biopsy work but did not retrieve the established stereotactic brain-biopsy literature. / S5 包含乳腺、肺和经皮活检，但未检出已成规模的立体定向脑活检文献。
- Zero rows are not evidence of absence: several zeros reflect missing synonyms or route terms. / 零计数不等于不存在：若干零值来自同义词或进入路径检索词不足。

## Representative primary/review evidence / 代表性原始研究与综述证据

- Robotic X-ray viewfinding and collimation: https://arxiv.org/abs/2412.08020
- Robotic gamma/SPECT acquisition: https://pmc.ncbi.nlm.nih.gov/articles/PMC4209015/
- Semi-autonomous confocal endomicroscopy: https://pmc.ncbi.nlm.nih.gov/articles/PMC7906249/
- Mobile contactless vital signs: https://pmc.ncbi.nlm.nih.gov/articles/PMC9096356/
- Active geometry-aware vital signs: https://arxiv.org/abs/2606.30275
- Robot-aided spasticity assessment: https://pmc.ncbi.nlm.nih.gov/articles/PMC4667530/
- Robot-supported balance assessment: https://pubmed.ncbi.nlm.nih.gov/28806995/
- Automated vestibular head impulse testing: https://pmc.ncbi.nlm.nih.gov/articles/PMC6136842/
- Robot-assisted stereotactic brain-biopsy meta-analysis: https://pubmed.ncbi.nlm.nih.gov/39627622/
- Autonomous robotic thoracentesis: https://researchportal.hw.ac.uk/en/publications/ultrasound-guided-robotic-aspirator-for-autonomous-thoracentesis-/

Audit date / 审计日期: 2026-08-07.
