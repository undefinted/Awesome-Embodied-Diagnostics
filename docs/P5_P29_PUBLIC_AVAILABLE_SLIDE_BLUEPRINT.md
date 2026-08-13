# P5–P29 public-available evidence slide blueprint

Updated: 2026-08-13. Intended canvas: 16:9. Use the existing Tsinghua-purple title rail, Chinese primary narrative and English secondary labels. All counts below are frozen public-index workflow outputs, not global publication totals.

## Global placement rules

- Title zone: 0–12%; body: 12–91%; source and page-number rail: 91–100%.
- Purple = sensing/state; blue = physical action; green = feedback/evidence; orange = boundary or gap.
- Every slide has one take-home sentence and no more than three visual anchors.
- Put DOI or stable public link in the footer; put complete claim and asset citations in speaker notes.
- On all landscape slides, write exactly: `公开索引题名筛选候选（冻结快照；非系统综述纳入数）`.

## Clinical detection and intervention

### P5 | 主动观察式检测：公开研究版图与证据边界

- Take-home: 机器人超声形成最大的公开研究集群；研究数量与临床成熟度必须分开判断。
- Layout: left 7–62% use `figures/public_evidence/p5_active_public_landscape.svg`; right 65–96% use three vertically aligned evidence markers.
- Right markers: robotic ultrasound—human autonomous acquisition; robotic OCT—human autonomous alignment; magnetic capsule—multicentre randomized quality-control assistance.
- Exact count labels: ultrasound 181/114; active or magnetic capsule 23/13; robotic endoscopy 20/11; robotic bronchoscopy navigation 15/11; OCT 8/6; auscultation 4/3. Format is `title-screened candidates / OA-or-repository location automatically identified`.
- Boundary strip: `数量 ≠ 全文纳入 ≠ 闭环完整度 ≠ 临床成熟度`.
- Sources: 10.1038/s41467-024-48421-y; 10.1038/s41467-025-62865-w; PMC10038849; 10.1186/s12916-026-04901-0.

### P6 | 方向一：不确定性驱动的机器人超声

- Take-home: 下一步应从固定轨迹转向由切面质量、风险和信息增益共同决定的动作与停止。
- Layout: left 8–60% closed loop: image/contact → quality and uncertainty → pose/force action → new view; right 63–96% two evidence blocks.
- Evidence block 1: autonomous thyroid ultrasound, 70 participants, paired comparison in 13, 213±85.3 s per lobe; UR3, linear probe, 6-axis F/T and Kinect.
- Evidence block 2: UltraBot, 247,000 expert demonstrations, >90% task success, up to 5.5× reproducibility; 7-DOF Panda, clinical ultrasound and external camera.
- Hardware footer: collaborative arm; clinical probe; F/T; RGB-D or patient tracking; capture interface; emergency stop.
- Data note: UltraBot data are controlled access; code is public. Do not label the dataset public download.

### P7 | 方向二：质量与覆盖驱动的光学/内镜扫描

- Take-home: meaningful closure occurs when quality or lesion uncertainty changes the next viewpoint, rescan or stopping decision.
- Layout: left 8–42% two scenarios—robotic OCT alignment and magnetic capsule coverage; centre 45–70% capability ladder; right 73–96% evidence and caveat.
- Capability ladder: alignment → quality/coverage estimation → human rescan prompt → autonomous rescan/stop.
- Evidence: contactless robotic OCT in freestanding people; ED robotic OCT pilot with 38 patients/72 eyes; AQCS capsule RCT randomized 200 participants.
- Caveat: RobOCTNet classification did not drive rescan; AQCS feedback was acted on by a human operator.
- Data/hardware: OCT image streams or capsule videos, 6-DOF alignment, eye or anatomy tracking, coverage map, image-quality model.

### P8 | 响应式交互诊断：刺激使隐匿状态可观测

- Take-home: the action is diagnostic because controlled stimulation creates a measurable tissue or physiological response.
- Layout: central loop occupying 12–78%; bottom three examples: palpation/stiffness, joint/tone, TMS–MEP/EEG.
- Boundary card: sensor repositioning alone is active observation; deliberate compression or stimulation followed by response measurement is response-based interaction.

### P9 | 响应式交互诊断：公开工作数量与成熟度

- Take-home: palpation dominates the strict public-title landscape, yet most response-based systems remain preclinical or small human validation.
- Layout: left 6–56% `p9_response_public_landscape.svg`; right-top 59–96% `p9_response_maturity.svg`; right-bottom a two-line interpretation.
- Counts: palpation 19/13; stiffness mapping 5/2; closed-loop TMS mapping 4/2; joint laxity 1/0; tone/spasticity 1/1; percussion/reflex 0/0.
- Maturity anchors: palpation—phantom/animal/ex vivo; TMS—8 healthy participants in automated hotspot hunting; joint laxity—human reliability measurement but fixed protocol; spasticity—19-patient automated QMR classification; percussion/reflex—no strict title candidate located.
- Required zero disclaimer: `0 = 当前冻结语料与检索规则未定位，不等于该任务不存在`.

### P10 | 方向一：多模态机器人触诊与弹性测绘

- Take-home: uncertainty-guided sparse palpation is more informative than uniformly scanning every point.
- Layout: left 8–60% sequential search image: sparse contacts → posterior stiffness map → next point; right 63–96% two evidence cards.
- Evidence: bimodal tactile tomography, phantom localization within ≤30 iterations, F1>0.976 and centroid error <0.032 mm; minimally invasive palpation, ex vivo and animal tissues including a 2-cm tumour mimic 5 mm deep in swine lung.
- Experiment package: tissue phantoms with blinded inclusions, F/T or tactile/OCT probe, respiratory-motion platform, US/MRI ground truth, preregistered stopping rule.
- Endpoints: contacts to localization; boundary error; peak force; missed lesion rate; acquisition time.

### P11 | 方向二：神经刺激—响应的主动映射

- Take-home: robotic placement alone is not the loop; MEP/EMG/EEG must change the next stimulation locus, orientation or intensity.
- Layout: left 8–62% scalp map with response-driven sampling; right 65–96% evidence and safety rail.
- Evidence: automated hotspot hunting in 8 participants, inter-session CoG shift 1.4 mm versus 7.0 and 9.6 mm comparators; GP active-learning study is efficient but does not by itself prove prospective robotic clinical integration; 2023 closed-loop robotic mapping is a meeting abstract.
- Hardware/data: robotic TMS, neuronavigation, individual MRI, EMG/MEP or EEG, coil tracking, stimulation safety limits.
- Safety rail: intensity limits, inter-pulse interval, motion detection, operator abort and audit log.

### P12 | 采样式交互诊断：从到达目标到获得可诊断样本

- Take-home: acquisition success and diagnostic success are different endpoints.
- Layout: central flow: localize → insert/collect → rapid adequacy or quality → accept/reposition/resample → laboratory result.
- Bottom examples: tissue; cells; blood or swab. Use an orange adequacy gate between collection and acceptance.

### P13 | 采样式交互诊断：公开工作数量、成熟度与断点

- Take-home: venipuncture has a small strict literature cluster but comparatively mature human workflow evidence; biopsy has more candidates but usually lacks adequacy-driven resampling.
- Layout: left 6–55% `p13_sample_public_landscape.svg`; right-top 58–96% `p13_sample_maturity.svg`; bottom 10–96% chain `targeting | collection | adequacy | result return`, highlight the last two gaps.
- Counts: percutaneous/core biopsy 22/14; venipuncture 12/6; swab 10/5; endoscopic/bronchoscopic biopsy 4/2; capsule sampling 2/0.
- Maturity anchors: ADOPT 1,633 routine-use participants and 153 analytical-equivalence participants; swab controlled human study n=80 and autonomous paired study n=52; TARGET robotic bronchoscopy n=679; capsule biopsy remains ex vivo/animal prototype.
- Important caveat: TARGET represents robot-assisted navigation and clinical sampling, not autonomous pathology-driven resampling.

### P14 | 方向一：样本充分性感知的机器人活检

- Take-home: the highest-value missing sensor is often not needle position but whether the acquired material is diagnostically adequate.
- Layout: left 8–60% proposed loop; right 63–96% existing evidence versus proposed experiment.
- Existing boundary: clinical robotic bronchoscopy can reach and sample lesions, but diagnostic yield and pathology are usually assessed after the action sequence.
- Proposed evidence channel: rapid optical microscopy, dynamic cell imaging, spectroscopy or ROSE-compatible adequacy score.
- Study ladder: phantom targeting → ex vivo tissue → animal → supervised human feasibility.
- Endpoints: adequate-sample rate, passes, procedure time, complications, nondiagnostic rate and human intervention count.

### P15 | 方向二：机器人采血与感染性标本采集

- Take-home: these tasks are near-term translational platforms, but full embodied diagnosis requires specimen-quality and test-result feedback.
- Layout: split 50:50. Left ADOPT phlebotomy; right robotic swabbing.
- Phlebotomy evidence: analytical equivalence n=153; routine use n=1,633; first-stick success 94.5% where a suitable vein was identified; mild adverse events 0.6%; NIR+US+Doppler.
- Additional public comparator: MagicNurse 154 paired volunteers and 6,255 willing users; reported puncture success 94.3%.
- Swab evidence: controlled n=80, robot success 92.5%, 201 s versus manual 29 s; autonomous SR-NOCS paired studies total n=52.
- Boundary: do not claim autonomous loading, disinfection, laboratory processing or result-triggered repeat unless the study implemented it.

## Laboratory diagnostics and assay development

### P16 | 实验室具身诊断：样本—仪器—结果闭环

- Take-home: fixed automation becomes embodied diagnosis only when sample or result state changes a subsequent physical test action.
- Layout: three layers: physical execution; state and quality; bounded decision. Add four subtask labels: reflex/retest; programmable microfluidics; self-driving assay development; active microscopy/culture.
- Boundary: software-only report release is decision support; physical retesting or rerouting closes the laboratory loop.

### P17 | 结果驱动的复检、反射检测与异常恢复

- Take-home: the most implementable clinical-laboratory loop is bounded recovery, not unconstrained autonomous ordering.
- Layout: left decision tree: release/review/retest/reflex/escalate; right evidence blocks and architecture requirements.
- Evidence: LIS validation reported 833 rules across 30 assays and >3.5 million reports since 2019; smart ferritin reflex model was retrospective (AUC 0.731); ML autoverification evidence available only at abstract level in the public scope unless full text is acquired.
- Physical closure mark: solid arrow only when analyser or track actually repeats/routes a sample; dashed arrow for software suggestion.
- Required hardware: LIS/middleware, analyser APIs, sample track, barcode identity, QC state, bounded action list and human exception queue.

### P18 | 可编程微流控：从动作纠错到检测协议闭环

- Take-home: microfluidic systems clearly demonstrate physical feedback, but clinical test-selection utility is still a separate claim.
- Layout: left droplet failure → visual/impedance detection → retry/reroute; right compare EWOD feedback, ferrobotic swarms and magnetic DMF.
- Evidence: all-electronic EWOD feedback improved droplet volume uniformity; ferrobots implemented programmable NAAT operations and prevalence-based pooled testing; current evidence is platform/assay validation rather than clinical outcome trial.
- Hardware: actuation board, disposable chip, camera/capacitance/impedance sensing, thermal control, assay readout and error log.

### P19 | 自驱动检测开发：选择下一实验

- Take-home: self-driving laboratories supply an architecture precedent, not proof of autonomous clinical diagnosis.
- Layout: goal → protocol → robotic execution → readout → Bayesian update → next experiment.
- Evidence: SAMPLE fully automated protein engineering; four agents found enzymes ≥12 °C more stable while searching <2% of the landscape; one design-to-result cycle took about 9 h.
- Translation questions: clinical sample heterogeneity, reference methods, lot effects, failure recovery, cross-platform reproducibility and prospective clinical utility.

### P20 | 实验室研究优先级

- Take-home: prioritize tasks that have bounded actions, observable failure and direct clinical value.
- Layout: 2×2 qualitative matrix: clinical value versus physical-loop testability. Plot reflex/retest recovery, cross-instrument exception recovery, DMF error recovery, self-driving assay and active microscopy.
- Recommended top-right: cross-instrument exception recovery and result-driven reflex/retest.
- Label the matrix `evidence-informed prioritization`, not a quantitative meta-analysis.

## Everyday embodied monitoring and adaptive support

### P21 | 日常具身监测：从连续感知到主动确认

- Take-home: continuous sensing alone is not a complete diagnostic loop; an anomaly must trigger a bounded action that produces new evidence.
- Layout: sensing → personal state/context → anomaly/uncertainty → question, denser sampling, home test or escalation → feedback.
- Bottom examples: wearable/implant; ambient/contactless; home diagnostic/support.

### P22 | 证据版图：规模不等于闭环

- Take-home: everyday sensing has the largest cohorts, but closed-loop confirmation is much less common.
- Layout: three trajectories rather than counts: Apple Heart; nocturnal-breathing PD; DETECT-AHEAD.
- Evidence: Apple Heart n=419,297; 0.52% notified and 84% of subsequent notifications concordant with AF among returned simultaneous patches; PD one-night wireless AUC 0.906, belt AUC 0.889; DETECT-AHEAD randomized n=450.
- Boundary: PD classification did not change acquisition; Apple Heart and DETECT-AHEAD contain human-mediated confirmation actions.
- Risk footer: adherence, privacy/bystanders, device drift and unequal access.

### P23 | 方向一：个人基线驱动的动态状态估计

- Take-home: within-person deviation can detect change missed by population thresholds, but it is the state layer rather than embodied action.
- Layout: large time-series showing population threshold and personal baseline; right cards for infection and nocturnal breathing.
- Evidence: retrospective COVID smartwatch cohort 5,262 participants, 32 infected, 26 with alterations; 22 of 25 with timing data detected before or at symptom onset.
- Confounder strip: behaviour, treatment, sensor drift, seasonality, missingness and device change.
- Required validation: prospective within-person calibration and decision improvement.

### P24 | 方向二：异常后的主动确认

- Take-home: adherence to the requested confirmation is part of closed-loop performance.
- Layout: left DETECT-AHEAD funnel; right confirmation-action menu and Apple Heart comparator.
- Exact funnel: 450 randomized → 118 of 300 intervention participants prompted → 61 completed home testing. Do not display 19 positives unless reverified directly from the results table.
- Actions: targeted question, denser sampling, single-lead ECG, home test, telehealth or clinical escalation.
- Metrics: completion, time to confirmation, false escalation, patient burden and staff contacts.

### P25 | 检测—支持—再评估生态

- Take-home: connected-care value depends on reliable handoffs and recovery from missing or contradictory feedback.
- Layout: patient/home ↔ device ↔ clinical team ↔ laboratory ↔ emergency service; annotate delay, missingness, conflict and unreachable patient.
- Safety footer: bounded actions, safe degraded state, human override, offline fallback and audit trail.
- Use automated insulin delivery only as a mature control comparator; label it therapeutic and do not imply general diagnostic maturity.

## Synthesis

### P26 | 跨领域比较：闭环闭在哪里

- Take-home: the common bottleneck is feedback failing to change the next evidence-acquisition action.
- Layout: 5×3 matrix: sensing, state, action, feedback, human role × clinical, laboratory, everyday.
- Red markers: next-view selection; sample adequacy; cross-instrument recovery; confirmation adherence.

### P27 | 优先研究切入点

- Take-home: choose projects by consequential-uncertainty reduction and testability, not novelty or autonomy alone.
- Layout: qualitative portfolio. Recommended: US quality-driven rescan; uncertainty-guided palpation; biopsy adequacy; lab exception recovery; everyday active confirmation.
- Selection criteria: data/hardware availability, loop measurability, clinical need, reversible actions, prospective endpoint and translation burden.

### P28 | 分阶段研究路线

- Take-home: system permissions should increase only as loop-level evidence accumulates.
- Layout: replay/simulation → phantom/ex vivo → supervised human feasibility → prospective workflow trial.
- Under every phase: technical endpoint, clinical endpoint, safety gate and stop/rollback condition.

### P29 | 结论

- Main statement: `Embodied diagnostics = adaptive evidence acquisition, not a device category.`
- Three short lines: analyse the whole loop; separate maturity from autonomy; judge feedback by whether it reduces consequential uncertainty and improves patient-relevant decisions.

## Reproducible support files

- Public counting method: `docs/PUBLIC_COUNTING_METHOD.md`
- Task counts and maturity: `data/presentation/public_evidence_maturity_matrix.csv`
- Screened records: `outputs/public_landscape/public_title_screened_records.csv`
- Reproduction scripts: `scripts/build_public_title_screened_landscape.py`; `scripts/make_public_presentation_figures.mjs`
- Editable SVG and PNG charts: `figures/public_evidence/`
