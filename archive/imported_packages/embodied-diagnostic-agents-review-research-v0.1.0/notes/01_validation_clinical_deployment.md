# Validation, human-centred evaluation, and lifecycle deployment

## Multilevel validation and benchmarking

The recommended structure is **detection layer → embodied-capability layer → end-to-end system layer**, rather than a single model-accuracy section.

### Detection and measurement validity

Assess scientific validity, analytical sensitivity and specificity, precision, repeatability, reproducibility, LoD/LoQ, linearity, interference, clinical sensitivity and specificity, PPV/NPV, calibration, and robustness across specimens, users, instruments, and environments. The principal framework sources are `ghtf2012ivd`, `sounderajah2025stardai`, and `who2021evidence`.

### Embodied capabilities

Evaluate perception and state estimation; sampling and manipulation; reasoning and action selection; latency and communications; task completion; failure detection and recovery; constraint violations; and robustness to patient movement, specimen differences, equipment variation, and environmental disturbance. Key sources are `marcus2024ideal`, `yang2017medicalrobotics`, and `mincu2022benchmarks`.

### End-to-end systems

Measure complete task success across sensing, reasoning, action, and re-sensing; accumulated module errors; uncertainty-aware stopping, retrying, or escalation; test count, time, cost, and resource use; and temporal, geographical, device, institutional, and domain generalization. See `dehond2023validation`.

## Human-centred clinical evaluation

The object of evaluation is the **human–agent team**. Required comparisons include clinician alone, agent alone, and clinician–agent team. Outcomes should include diagnostic performance, workload, usability, cognitive burden, workflow disruption, automation bias, error propagation, override and safe-stop effectiveness, escalation, patient acceptance, equity, and patient outcomes.

Use `vasey2022decideai`, `fda2016humanfactors`, `liu2020consortai`, `cruzrivera2020spiritai`, `chen2024workload`, and `who2021ethics`.

STARD-AI, CONSORT-AI, SPIRIT-AI, and DECIDE-AI are design and reporting guidance. Compliance improves transparency but does not establish safety or effectiveness. Validation still requires prespecified criteria, external testing, comparison, failure testing, and real-world evidence.

## Deployment and lifecycle monitoring

Recommended lifecycle:

> local validation → silent deployment → controlled rollout → routine monitoring → audit and corrective action → update, rollback, or retirement

Monitor input and sample quality; patient, sample, device, and environment shift; calibration; robotic or workflow failures; collisions, downtime, and recovery; override and escalation; subgroup equity; downstream testing, treatment, and outcomes; software, model, hardware, and interface versions; adverse events, near misses, and complaints.

Key sources are `lekadir2025futureai`, `you2025deployment`, `liu2022audit`, `koch2024shift`, `imdrf2017samd`, `imdrf2025gmlp`, `fda2025pccp`, and `kolbinger2024reporting`.

