# Ethics, safety, and governance

The chapter follows a three-step progression:

> individual rights → safe and accountable action → just and resilient systems

## Privacy and autonomy in continuous detection

Continuous detection changes privacy from a one-time protection problem into an ongoing negotiation of observation, inference, access, and control.

The section should address continuous and longitudinal sensing, ambient collection, bystanders, continuing consent, pause and exit rights, the right to know or not know, access to raw data, data minimization, purpose limitation, local computation, retention, third-party access, and secondary use.

Questions include whether a system infers information the patient did not provide, whether family or staff are also captured, whether monitoring or selected predictions can be paused, whether longitudinal data can be accessed or corrected, and whether agreeing to use a device implies consent to all subsequent inference or commercial use.

Sources: `martinezmartin2021ambient`, `cohen2020remote`, `gerke2020home`, `bietz2016personalhealth`, and `who2021ethics`.

## Safety and accountability in diagnostic action

Organize the section as **action risk → safety control → responsibility chain**. Distinguish measurement adjustment, repeat testing, specimen routing, clinical escalation, and therapeutic intervention. Greater authority and irreversibility require stronger evidence, oversight, and controls.

Meaningful oversight requires that a person can understand system state and uncertainty, has time to intervene, has actual authority to pause or alter action, and can intervene effectively. Systems need logs that connect sensing, reasoning, decisions, actions, and versions.

Central principle:

> Accountability should follow control: parties that design, authorize, update, or operationally control an action should bear corresponding and traceable responsibilities.

Sources: `yang2017medicalrobotics`, `liu2022audit`, `vandesande2026oversight`, `iso14971`, `eu2024aiact`, and `who2021ethics`.

## Equity and resilience of connected systems

Separate but connect:

1. measurement equity across skin tone, age, body characteristics, disability, and disease;
2. algorithmic and service equity across data, targets, access, language, literacy, and cost;
3. operational resilience under network, cloud, power, hardware, and cybersecurity failures.

A connected system is not equitable when benefits depend on uninterrupted broadband, recent hardware, specialist maintenance, or cloud access unavailable to populations with the greatest diagnostic need.

Requirements include subgroup measurement, connectivity and cost analysis, offline or edge operation, redundant pathways, manual workflows, explicit safe-degradation states, tested backup and recovery, incident response, and avoidance of long-term dependence on inaccessible proprietary interfaces.

Sources: `sjoding2020oximetry`, `obermeyer2019bias`, `chen2023fairness`, `ibrahim2021datapoverty`, `veinot2018inequality`, `lekadir2025futureai`, `ghafur2019wannacry`, and `fda2026cybersecurity`.

