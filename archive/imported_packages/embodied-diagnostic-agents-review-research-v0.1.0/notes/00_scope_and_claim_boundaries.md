# Scope and claim boundaries

## Object of review

An embodied diagnostic agent is treated as a system—not merely a classifier—that can combine:

1. sensing or measurement;
2. state estimation and diagnostic reasoning;
3. evidence acquisition, sampling, manipulation, workflow action, or physical action;
4. feedback from the patient, specimen, instrument, user, or environment;
5. stopping, retrying, escalating, or replanning.

This definition does not imply unrestricted autonomy. Action permissions and reversibility are explicit dimensions of system risk.

## Evidence hierarchy used in the notes

The archive distinguishes:

- policy, regulation, technical standards, and reporting guidance;
- conceptual or implementation frameworks;
- preclinical and engineering demonstrations;
- retrospective or simulated clinical evaluations;
- prospective early clinical studies;
- comparative and randomized trials;
- real-world deployment and postmarket evidence.

Statements must not be promoted upward in this hierarchy. In particular, simulated consultations and virtual EHR benchmarks support capability evaluation but not autonomous clinical deployment.

## Core evaluation distinctions

### Detection layer

Scientific validity, analytical performance, clinical performance, precision, repeatability, reproducibility, limits of detection or quantification, interference, calibration, and subgroup performance.

### Embodied-capability layer

Perception, state estimation, sampling and manipulation accuracy, action selection, latency, task completion, failure detection, recovery, constraint violations, and adaptation to patient, specimen, device, and environmental variation.

### System layer

End-to-end success, cross-module error accumulation, uncertainty handling, safe stopping, time and resource consumption, generalization, human–agent performance, clinical utility, and patient outcomes.

## Terminology discipline

- **Human in the loop** is not automatically meaningful oversight. Oversight requires knowledge, cognitive space, authority, and an effective intervention path.
- **Self-optimizing** means evidence-responsive workflow replanning, not unconstrained online self-modification.
- **Patient-specific model** requires longitudinal individual state updating; it is not a synonym for any personalized risk score.
- **Digital twin** is an advanced implementation class, not a generic label for personalization.
- **Resilience** means safe degradation, continuity, recovery, and cybersecurity at system and service levels; it is not merely resistance to model perturbations.

