# Response-based interactive diagnosis — closed-loop figure

This folder contains the English, publication-style diagram for the response-based interactive diagnosis branch of *Clinical Detection and Intervention*.

## Files

- `response_based_interactive_diagnosis_closed_loop_en.svg`: editable vector master.
- `response_based_interactive_diagnosis_closed_loop_en.png`: 1920 × 1080 raster export for slides and preview.
- `figure_metadata.json`: machine-readable provenance and scope notes.

## Conceptual boundary

Response-based interactive diagnosis requires a controlled physical or physiological perturbation whose elicited response is used to update diagnostic inference and subsequent action selection. Stimulus delivery, device positioning or preset motion alone is insufficient.

The figure covers:

- state estimation and working memory;
- uncertainty- and risk-aware stimulus selection;
- embodied stimulus planning and control;
- controlled mechanical, acoustic, motion-based, electrical, magnetic or physiological perturbation;
- multimodal response sensing and evidence fusion;
- explicit stopping, adaptation and clinical escalation criteria;
- human oversight, bounded operation and failure-aware safeguards.

## Reproduce

From the repository root, set `RUNTIME_NODE_MODULES` to a Node.js package directory containing `sharp`, then run:

```powershell
node scripts/render_response_based_interactive_diagnosis_loop.mjs
```

## Suggested figure caption

**Closed-loop response-based interactive diagnosis.** Patient context, prior observations and working memory inform an uncertainty- and risk-aware policy that selects the site, modality and parameters of a controlled perturbation. Mechanical, acoustic, neurophysiological or functional responses are sensed and fused to update the estimated state and diagnostic confidence. If the evidence is insufficient, unsafe or not yet actionable, the system adapts the next stimulus; otherwise, it reports, confirms, escalates or defers. Safety constraints and meaningful human oversight bound the entire sensing–decision–action–feedback loop.
