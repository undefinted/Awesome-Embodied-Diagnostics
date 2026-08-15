# Clinical Detection and Intervention: integrated English summary

Version: 15 August 2026  
Scope: publicly visible bibliographic records and automatically identified legal public-full-text locations.

## 1. Classification principle

The classification unit is an evidence-acquisition task within a study, not an entire robot or device. A robotic arm, motorized probe, controllable endoscope, capsule robot or another mechatronic carrier can enter any mechanism if its action meets the definition.

| Class | Defining physical action | Terminal diagnostic evidence | Boundary with adjacent classes |
|---|---|---|---|
| 1.1 Active observational sensing | Move, orient, align or scan a sensor | In-vivo image, sound or physiological signal | Reassign to 1.2 if a perturbation and elicited response create the evidence; reassign to 1.3 if material is collected for ex-vivo analysis |
| 1.2 Response-based interactive diagnosis | Apply a controlled mechanical, acoustic, electrical or neurophysiological perturbation | Elicited deformation, force, physiological or functional response | Contact force used only for safe positioning remains in 1.1; a sample-based endpoint belongs to 1.3 |
| 1.3 Sample-based interactive diagnosis | Puncture, aspirate, cut, swab or collect material | Ex-vivo pathological, cytological, biochemical, microbiological or molecular result | In-vivo imaging without material collection belongs to 1.1; purely therapeutic actions are excluded |

Quantitative figures use one primary class per work: **sample acquisition (1.3) → elicited response (1.2) → active observation (1.1)**. This hierarchy prevents double counting; it is not a ranking of importance or maturity. Secondary stages remain available in the overlap audit.

## 2. Overall Clinical Detection and Intervention statistics

| Metric | Value |
|---|---:|
| Deduplicated title-level candidates in the comparable core | 322 |
| Public full-text locations identified automatically | 200 |
| Public-location identification rate | 62.1% |
| Candidates published since 2021 | 244 |
| Cross-rule works resolved | 9 |
| Unscreened high-recall retrieval union | 1,111 |

The 322-work set is the conservative core that can currently be compared across all three mechanisms. The 1,111-work union is a retrieval denominator containing false positives, legacy assignments and cross-mechanism duplicates; it is not a publication count.

## 3. Mechanism-level statistics

| Mechanism | Public-visible title candidates | Public full-text locations identified | Since 2021 | Share of comparable core |
|---|---:|---:|---:|---:|
| 1.1 Active observational sensing | 242 | 155 | 189 | 75.2% |
| 1.2 Response-based interactive diagnosis | 30 | 18 | 22 | 9.3% |
| 1.3 Sample-based interactive diagnosis | 50 | 27 | 33 | 15.5% |

These proportions describe the frozen public-index title screen. They do not measure clinical maturity, diagnostic performance, regulatory status or deployment.

## 4. Subtask statistics

### 1.1 Active observational sensing

| Subtask | Public visible | Public full text identified | Since 2021 |
|---|---:|---:|---:|
| Ultrasound examination and active scanning | 176 | 112 | 138 |
| Active or magnetically controlled capsule endoscopy | 21 | 13 | 14 |
| Flexible gastrointestinal endoscopic examination | 19 | 10 | 11 |
| Bronchoscopic observation and navigation | 15 | 11 | 15 |
| Optical coherence tomography acquisition | 7 | 6 | 7 |
| Active auscultation and acoustic examination | 4 | 3 | 4 |

The separately expanded P5 corpus also contains actively aligned ophthalmic imaging, cutaneous and exposed-tissue imaging, and ENT/oral examination. These records are not mixed into the three-mechanism comparison because 1.2 and 1.3 have not yet received equivalent high-recall expansion. They should be incorporated in the next uniform retrieval round.

### 1.2 Response-based interactive diagnosis

| Subtask | Public visible | Public full text identified | Since 2021 |
|---|---:|---:|---:|
| Robotic palpation | 19 | 13 | 13 |
| Elastography and stiffness mapping | 5 | 2 | 5 |
| Stimulation-response mapping | 4 | 2 | 3 |
| Joint laxity and provocation examination | 1 | 0 | 0 |
| Tone and spasticity assessment | 1 | 1 | 1 |
| Percussion and reflex examination | 0 | 0 | 0 |

A zero indicates that the present title rules identified no candidate; it does not establish that the task does not exist.

### 1.3 Sample-based interactive diagnosis

| Subtask | Public visible | Public full text identified | Since 2021 |
|---|---:|---:|---:|
| Percutaneous or core-needle biopsy | 22 | 14 | 14 |
| Venipuncture and phlebotomy | 12 | 6 | 4 |
| Swab and cavity-specimen collection | 10 | 5 | 10 |
| Endoscopic or bronchoscopic biopsy | 4 | 2 | 4 |
| Capsule-based tissue or fluid sampling | 2 | 0 | 1 |

## 5. Representative boundary resolutions

- Ultrasound-guided robotic venipuncture is primarily 1.3; ultrasound remains a guidance-modality tag.
- Optical coherence elastography is primarily 1.2 because controlled deformation and elasticity constitute the evidence.
- Endobronchial ultrasound observation is a 1.1 bronchoscopic observation/navigation task.
- A capsule that collects gut-microbiome material is primarily 1.3 rather than 1.1 capsule imaging.
- Endoscopic palpation belongs to 1.2 when controlled contact and force response generate mechanical evidence; view adjustment alone belongs to 1.1.

## 6. Statistical layers and permitted interpretation

| Layer | Current status | Appropriate use | Inappropriate use |
|---|---|---|---|
| Retrieval coverage | 1,111 uniformly unscreened records | Recall audit and screening workload | Publication totals or relative research activity |
| Comparable title-level core | 322 works | Cross-mechanism PPT comparison and methodological demonstration | Final systematic-review inclusion count |
| Public-location layer | 200 works | Full-text acquisition planning | Individually verified reuse licences |
| Full-text evidence layer | Dual screening incomplete | Future manuscript evidence and maturity analysis | Claims that the review is already exhaustive |

## 7. Recommended presentation use

- Clinical Detection and Intervention overview: use the mechanism chart and the three headline values 322, 200 and 244.
- Background slides for 1.1, 1.2 and 1.3: use the corresponding subtask chart with the caption “public-index title-level candidates, not systematic-review inclusions”.
- Annual chart: use only to describe the current indexed candidate distribution, not clinical maturity.
- Evaluate maturity separately using human validation, prospective studies, trials, deployment and regulatory evidence.

## 8. Work required for comprehensive publication-level counts

Publication-grade quantitative claims require synchronized high-recall searches for all three mechanisms, identical database and date coverage, dual abstract/full-text screening, recorded exclusion reasons, and linkage of conference, preprint and journal versions. Subscription databases fall outside the current public-only scope and should later be used as a sensitivity-search layer.

## 9. File map

- `clinical_detection_intervention_unique_records.csv`: one primary classification for each of 322 works.
- `clinical_detection_intervention_overlap_audit.csv`: nine cross-rule works and their resolution.
- `clinical_detection_intervention_retrieval_audit.csv`: gap between the unscreened retrieval pool and comparable core.
- `clinical_detection_intervention_taxonomy.csv`: bilingual definitions, boundaries and carrier scope.
- `clinical_detection_intervention_evidence_map_2026-08-15.xlsx`: Chinese and English summary sheets, statistics, records and validation information.

