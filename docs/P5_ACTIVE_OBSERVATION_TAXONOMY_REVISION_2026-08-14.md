# P5 active-observation taxonomy: objective revision (2026-08-14)

## Conclusion

The retrieval buckets are not a scientific classification. They combine at
least four different axes: clinical examination procedure, anatomical access,
sensing modality and physical carrier. The presentation figure therefore uses
one conservative primary axis—**title-verifiable clinical examination
procedure**—and records modality and carrier separately.

This is a pragmatic evidence-map taxonomy, not a claim that the eight
procedures form a universal or exhaustive ontology of active sensing.

## Primary procedure axis

The mutually exclusive task-resolved groups are:

1. ultrasound examination and active scanning;
2. flexible gastrointestinal endoscopic examination;
3. active or magnetically controlled capsule endoscopy;
4. bronchoscopic observation and navigation;
5. actively aligned ophthalmic examination;
6. cutaneous and exposed-tissue surface imaging;
7. active auscultation and acoustic examination;
8. ENT and oral-cavity examination.

T9 is not a ninth clinical application. It is an audit residual for
task-unresolved or cross-cutting acquisition technology. T9 records are kept in
the dataset and modality matrix but excluded from the clinical-procedure bars.

## Corrections to the former rules

- Retrieval source buckets no longer substitute for title evidence.
- Bare `eye`, `eyes`, `gaze` and `hand-eye` no longer imply ophthalmology.
- Bare `kidney` no longer implies exposed-tissue imaging.
- Bare `lung nodule` no longer implies bronchoscopy.
- Generic `endoscopic robot` no longer implies gastrointestinal endoscopy.
- Explicit capsule terminology takes precedence over generic endoscopy.
- A specific access route takes precedence over ultrasound as the primary
  procedure; ultrasound remains a modality tag (for example, endobronchial
  ultrasound is classified under bronchoscopy).
- “Wound” was removed from the T6 label because the frozen title corpus does
  not support a distinct wound-imaging cluster. The revised label is
  “cutaneous and exposed-tissue surface imaging”.

These corrections are encoded in
`scripts/reclassify_p5_active_observation.py`; the exact rule vocabulary is
also exposed in
`data/presentation/p5_active_observation_two_axis_taxonomy_2026-08-14.csv`.

## Why optical/spectral scanning is not a clinical task

OCT, Raman/DRS, hyperspectral imaging, confocal endomicroscopy and
photoacoustic imaging describe how evidence is measured. Skin, ophthalmic,
gastrointestinal and bronchoscopic examination describe where and through
which clinical procedure it is acquired. A skin OCT study is therefore T6 +
OCT, whereas an endoscopic OCT study is assigned to its explicit access route
+ OCT. If the title contains no clinical procedure, it remains T9.

## Embodiment boundary

“Robot” is not an inclusion requirement. Eligible physical carriers can
include manipulators, dedicated mechatronic scanners, flexible or continuum
endoscopes, magnetic or self-propelled capsules, actuated probe holders and
other controllable devices. However, the current bibliometric map is a
title-level candidate map: full text is still required to establish whether a
paper contains a sensing–decision–action–feedback loop rather than open-loop
automation or supporting hardware.

## Interpretation

Counts are DOI-first/title-second deduplicated public-index candidates. They
are not full-text systematic-review inclusions, clinical maturity scores or
evidence that each record is a complete embodied diagnostic system. Public
available means that a public full-text/preprint location was identified; it
does not assert an item-level licence audit.
