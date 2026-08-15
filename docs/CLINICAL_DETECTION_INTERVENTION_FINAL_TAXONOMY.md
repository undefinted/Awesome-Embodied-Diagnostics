# Clinical Detection and Intervention: final working taxonomy

Status: **taxonomy v1.0 (final working version for the review and presentation)**  
Scope: diagnostic evidence acquired through physical interaction with a patient, tissue or clinically connected device.  
Unit of classification: **one evaluated diagnostic evidence-acquisition episode**, not a robot, platform, sensing modality or paper.

## Core principle

The three primary classes are defined by the causal role of the physical action in producing the terminal diagnostic evidence:

1. **1.1 Active observational sensing / 主动观察式感知** — feedback changes sensor pose, viewpoint, contact, coverage, trajectory or acquisition settings; the evidence remains an in-vivo observation.
2. **1.2 Response-eliciting interactive diagnosis / 诱发响应式交互诊断** — the system deliberately perturbs tissue or physiology; the elicited response is the diagnostic evidence.
3. **1.3 Diagnostic sample acquisition / 诊断性样本获取** — the system obtains material for ex-vivo analysis; acquisition or sample adequacy participates in the evaluated loop.

This wording replaces the former mixed hierarchy in which modalities (ultrasound and OCT), access routes (bronchoscopy), carriers (capsules) and clinical sites (skin or wound) appeared at the same level.

## Mandatory assignment sequence

Apply the following questions in order:

1. Was material obtained for ex-vivo analysis, and was acquisition or adequacy evaluated? If yes, assign the sampling episode to **1.3**.
2. Otherwise, was tissue or physiology deliberately perturbed and was the elicited response interpreted? If yes, assign the episode to **1.2**.
3. Otherwise, did feedback change acquisition configuration to obtain a new in-vivo observation? If yes, assign the episode to **1.1**.
4. If none applies, do not label the work as a complete embodied diagnostic system. It may be retained as a supporting technology.

The sequence prevents double counting of a single episode. It does **not** force an entire multistage platform into one class. For example, robotic bronchoscopy may contain a 1.1 navigation episode and a 1.3 biopsy episode; if both are evaluated, the evidence table contains two linked task rows.

## Final subtask families

### 1.1 Active observational sensing / 主动观察式感知

- **A1 External contact scanning and sensor placement / 体表接触式扫描与传感器布置**
- **A2 External non-contact alignment and scanning / 体表非接触式对准与扫描**
- **A3 Tethered endoluminal or intracavitary observation and navigation / 有缆腔内或腔道内观察与导航**
- **A4 Untethered internal observation and navigation / 无缆体内观察与导航**
- **A5 Catheter-based, intravascular, intraductal or percutaneous in-vivo sensing / 导管、血管内、管道内或经皮探头在体感知**

Ultrasound, OCT, Raman, DRS, photoacoustic imaging, hyperspectral imaging, RGB vision and auscultation are **modality tags**. Ophthalmic, thyroid, carotid, gastrointestinal, pulmonary, dermatological and wound applications are **anatomical or clinical-context tags**. Robot arms, motorized probes, endoscopes, capsules and catheters are **carrier tags**.

### 1.2 Response-eliciting interactive diagnosis / 诱发响应式交互诊断

- **R1 Quasi-static contact, palpation and indentation / 准静态接触、触诊与压入**
- **R2 Dynamic mechanical or acoustic excitation / 动态机械或声学激励**
- **R3 Imposed motion, loading and functional provocation / 施加运动、载荷与功能激发**
- **R4 Electrical, magnetic or neurophysiological stimulation-response mapping / 电、磁或神经生理刺激—响应映射**
- **R5 Physiological challenge and controlled modulation / 生理挑战与受控调制**

Force control does not automatically make a study response-based. If force only maintains safe sensor coupling, the task remains 1.1. Compression or excitation moves the task to 1.2 only when the induced deformation, wave or physiological response is itself interpreted as diagnostic evidence.

### 1.3 Diagnostic sample acquisition / 诊断性样本获取

- **S1 Percutaneous needle-based tissue sampling / 经皮针式组织采样**
- **S2 Vascular blood sampling / 血管血液采样**
- **S3 Tethered endoluminal or intracavitary tissue/fluid sampling / 有缆腔内或腔道内组织/体液采样**
- **S4 Untethered or capsule-based internal sampling / 无缆或胶囊式体内采样**
- **S5 Surface or mucosal specimen collection / 体表或黏膜标本采集**
- **S6 Other adaptive body-fluid or excretion collection / 其他自适应体液或排泄物采集**

Needle placement, navigation or targeting alone is not sufficient for 1.3. The study must evaluate diagnostic material acquisition, diagnostic yield, specimen quality or adequacy, or a feedback step that changes sampling. Pure infusion, ablation, drainage, implantation and other therapeutic needle actions are excluded.

## Separate tags required for every evidence-table row

- sensing modality;
- anatomical site and clinical indication;
- access route;
- physical carrier;
- action authority (human, shared control or system);
- feedback closure (open loop, local control, evidence-adaptive or end-to-end);
- terminal evidence type;
- validation setting and evidence maturity.

These tags must not be promoted into competing primary classes.

## Counting policy

The previous paper-level primary-class bar charts are withdrawn. Their task labels were not ontologically parallel and their input was an automated title screen rather than a completed full-text review.

Future quantitative figures must report:

1. unique studies in the domain;
2. unique studies per mechanism;
3. task-study pairs per subtask family;
4. cross-mechanism overlap explicitly;
5. separately, the number of full-text-verified closed-loop systems.

The sum of mechanism counts may exceed the number of unique studies when a paper evaluates more than one diagnostic episode. A mutually exclusive figure may be created only for a clearly declared primary-endpoint sensitivity analysis, not as the main ontology.

## Evidence status

The taxonomy is stable enough for the review and PPT. Numerical corpus claims remain provisional until uniform public-source searching, abstract/full-text screening, recorded exclusion reasons and duplicate publication merging are complete. Publicly visible records and automatically discovered open-access locations are discovery layers, not evidence of eligibility or clinical maturity.
