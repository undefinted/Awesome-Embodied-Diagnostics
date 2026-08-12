# Figure captions / 中英文图注

## Figure 1. Action-defined taxonomy of embodied clinical detection / 具身医学检测的动作定义型分类

**EN.** The taxonomy distinguishes three embodied diagnostic modes by the physical action that generates evidence. Active observational sensing changes sensor configuration to obtain a new observation; response-based interactive diagnosis applies a controlled stimulus and interprets the response; sample-based interactive diagnosis obtains tissue or body fluid for ex vivo analysis. Each work is assigned to its primary evidence-generating action.

**中.** 本分类依据产生诊断证据的物理动作区分三类具身医学检测。主动观察式检测改变传感器配置以获得新观察；响应式交互检测施加可控刺激并解释响应；采样式交互检测获取组织或体液供离体分析。每项工作按主要证据生成动作唯一归类。

## Figure 2. Cumulative literature workload by major class / 三大方向的累计文献工作量

**EN.** Filled markers show the strict title-explicit retrieval set and open markers show the broad title/abstract sensitivity set. Counts for active observational sensing, response-based interactive diagnosis and sample-based interactive diagnosis were 436/1,015, 98/143 and 278/317, respectively (strict/broad). The two sets reflect retrieval specificity and sensitivity; they are not confidence limits.

**中.** 实心点表示严格题名集，空心点表示宽题名-摘要敏感性集。主动观察式检测、响应式交互检测和采样式交互检测的严格/宽检索计数分别为 436/1,015、98/143 和 278/317。两组计数反映检索特异性与敏感性的差异，并非统计置信限。

## Figure 3. Workload across 24 task families / 24 个细分任务的累计工作量

**EN.** Workload across seven active-observation, eight response-based and nine sample-based task families. Filled and open markers denote strict and broad retrieval sets, respectively; exact strict/broad counts are printed at right. A common log10(n+1) axis supports cross-class comparison while retaining zero and low-count families. Counts are deduplicated publication records, not clinical trials, products or deployed systems.

**中.** 七个主动观察式、八个响应式和九个采样式任务的累计工作量。实心点与空心点分别表示严格集和宽检索集，右侧列出精确的严格/宽检索计数。三个大类共用 log10(n+1) 坐标，以便跨类比较并保留零值和低计数任务。计数单位为去重文献记录，并非临床试验、产品或已部署系统。

## Figure 4. Closed-loop active observational sensing / 主动观察式检测闭环

**EN.** The agent evaluates target visibility, coverage, image or signal quality and uncertainty from the current observation; selects the next viewpoint, pose, contact state or scan path; passes a safety gate; executes the action; acquires and registers a new observation; and then continues, rescans, stops or hands control to a human. The objective is to increase diagnostic value subject to safety constraints.

**中.** 智能体根据当前观察评估目标可见性、覆盖度、图像或信号质量和不确定性，选择下一视点、位姿、接触状态或扫描路径，通过安全门控后执行，获取并配准新观察，随后继续、复扫、停止或转交人工。其目标是在满足安全约束的前提下提高诊断价值。

## Figure 5. Active observational sensing landscape / 主动观察式检测的工作量、轨迹与结构

**EN.** (a) Strict and broad retrieval counts for seven active-observation tasks on a log10(n+1) axis. (b) Annual strict-set records from 1995 to 2026; the dashed final segment marks partial-year 2026. Each deduplicated work contributes once to its primary task and earliest plausible public year. (c) Exact strict-set counts by publication period; zero is white and larger ordered bins are strictly darker. (d) Field concentration and recency. A1 robotic ultrasound and A2 robotic endoscopy jointly account for 94.7% of the 436-record strict set. Five-year activity increased from 77 records in 2016–2020 to 260 in 2021–2025 (3.38×). The broad sensitivity set contains 1,015 records.

**中.** （a）七个主动观察式任务在 log10(n+1) 坐标上的严格集与宽检索集计数。（b）1995–2026 年的严格集年度轨迹；最后虚线段表示 2026 年为不完整年度。每篇跨库去重文献仅按主要任务和最早合理公开年份计数一次。（c）各发表时期的严格集精确计数；0 为白色，数量等级越高颜色严格越深。（d）领域集中度与时间结构。A1 机器人超声和 A2 机器人内镜合计占 436 篇严格集文献的 94.7%。五年期工作量由 2016–2020 年的 77 篇增至 2021–2025 年的 260 篇（3.38 倍）；宽检索敏感性集为 1,015 篇。

**Common methods / 共同方法.** OpenAlex, Europe PMC and arXiv; DOI-first then canonical-title deduplication; one primary task per work; search cutoff 6 August 2026. The broad set is retained as sensitivity analysis rather than interpreted as a statistical upper bound.
