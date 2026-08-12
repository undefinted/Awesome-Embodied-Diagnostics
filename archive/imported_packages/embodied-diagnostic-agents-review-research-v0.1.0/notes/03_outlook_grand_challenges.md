# Outlook: three grand challenges

The three challenges progress from **workflow adaptation → patient-specific modelling → ecosystem-level closure**.

## Self-optimizing diagnostic workflows

Self-optimization means:

> diagnostic objective → evidence or experiment selection → execution → quality and uncertainty assessment → workflow replanning → next acquisition or experiment

At the laboratory level, a system may choose conditions, repeat tests, quality-control steps, or subsequent experiments. At the clinical level, it may select the next question, test, image, or laboratory measurement based on current uncertainty.

Complete autonomous loops are established mainly in chemistry, materials, and laboratory demonstrations (`tom2024sdl`, `hase2019sdl`, `burger2020chemist`, `macleod2020sdl`, `angello2022optimization`). Clinical evidence is mainly simulated diagnostic dialogue and virtual-EHR benchmarking (`tu2025amie`, `jiang2025medagentbench`, `nori2025sequential`). These do not prove safe clinical autonomy.

The outlook should emphasize constrained optimization, quality-aware execution, and human oversight rather than unrestricted online model modification.

## Patient-specific diagnostic models

Recommended conceptual sequence:

> population model → individual baseline → longitudinal state estimation → patient-specific deviation prediction → counterfactual evaluation of diagnostic or intervention options

Such a model should use individual longitudinal baselines, integrate physiological, biochemical, behavioural, imaging, omics, and clinical-record data, update with new observations and interventions, and represent uncertainty, time variation, and missing data.

Sources: `chen2012ipop`, `rose2019precision`, `zhou2019multiomics`, `dunn2021wearable`, `mishra2020presymptomatic`, `acosta2022multimodal`, and `katsoulakis2024twins`.

Digital twins are one possible advanced implementation and should not be used as a synonym for any patient-specific predictor.

## Integrated detection–intervention ecosystems

Distinguish three scales:

- **Device loop:** sensing, control, and intervention in one device.
- **Care-workflow loop:** detection triggers repeat testing, referral, medication, or escalation.
- **Ecosystem loop:** home, hospital, laboratory, wearables, EHR, and intervention devices coordinate across time and use response data to recalibrate the system.

Ideal sequence:

> sensing → patient-state estimation → diagnostic reasoning → proportional intervention → response monitoring → model and policy updating

Mature or informative device-level examples include closed-loop insulin control (`brown2019closedloop`), patient-specific neurostimulation (`scangos2021closedloop`), integrated biochemical sensing and delivery (`lee2016graphene`), and wearable recording and stimulation (`topalovic2023neurostack`). `mcdonald2024lhs` supports the health-system learning loop and `fda2023pclc` supplies device-level control guidance.

Distributed ecosystem closure remains prospective because interoperability, latency, security, accountability, alert fatigue, and cross-institutional governance remain unresolved.

