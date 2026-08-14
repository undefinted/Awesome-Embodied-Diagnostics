# P5 active-observation taxonomy revision (2026-08-14)

## Decision

The 11 labels used in the 2026-08-13 public-index search are retrieval
buckets, not mutually exclusive scientific application categories. They mix
clinical examination tasks/access routes, sensing modalities, and physical
carriers.

Consequently, robotic optical/spectroscopic scanning overlaps with skin/wound
surface scanning. OCT also overlaps with ophthalmic, skin, gastrointestinal and
bronchoscopic tasks. The old bars must not be summed or interpreted as
exclusive application-domain sizes.

## Evidence from the frozen records

Auditing the frozen task-assignment table by DOI and then normalized title
found 861 task assignments representing 855 unique works. Six works occurred
in two retrieval buckets. Observed combinations include GI endoscopy + OCT,
bronchoscopy + optical/confocal imaging, skin/wound + OCT, and GI endoscopy +
photoacoustic/optical imaging. Run `scripts/audit_p5_taxonomy_overlap.py` to
reproduce the audit.

## Revised two-axis framework

Use a mutually exclusive primary clinical acquisition task for P5 counts:

1. ultrasound examination and active scanning;
2. flexible gastrointestinal endoscopic inspection;
3. active or magnetically controlled capsule endoscopy;
4. bronchoscopic observation and navigation;
5. actively aligned ophthalmic examination;
6. skin, wound and exposed-tissue surface mapping;
7. active auscultation and acoustic examination;
8. ENT and oral-cavity examination;
9. generic active-scanning platforms without a defined clinical site, reported
   as a separate technical corpus.

Record sensing modality as a non-exclusive secondary tag: ultrasound,
white-light/RGB video, OCT, Raman/DRS, HSI/MSI, confocal/endomicroscopy,
photoacoustic, acoustic/physiological sound, or another specified signal.

For example, skin OCT is assigned to skin/wound surface mapping and tagged
`OCT`; endoscopic OCT is assigned to the relevant endoscopic task and tagged
`OCT`.

## Physical embodiment is broader than “robot”

The review should include algorithmically controlled physical acquisition
systems that alter sensor pose, contact, viewpoint or trajectory and use new
observations to guide subsequent evidence acquisition. Embodiments may include
robotic manipulators, dedicated mechatronic scanners, continuum/flexible/soft
endoscopes, magnetic or self-propelled capsules, actuated probe holders, mobile
platforms, bedside systems and body-mounted controllable devices.

A robotic arm is therefore one embodiment, not an inclusion requirement.
However, fixed open-loop motion alone remains supporting automation rather than
a complete embodied diagnostic loop.

## Figure status

The 2026-08-13 chart is retained for search-coverage and rule auditing. It must
not be used as a final exclusive application count until the 855 unique works
have been reassigned to primary clinical tasks. The revised P5 should show
exclusive task counts and place OCT, spectroscopy and other modalities in a
small multi-label matrix or annotation panel.

## Evidence anchors

- Autonomous thyroid ultrasound: Nature Communications (2024), DOI
  `10.1038/s41467-024-48421-y`.
- LARA-OCT surface tracking and skin imaging: Biomedical Optics Express (2024),
  PMC11166428.
- Endoscopic OCT path scanning: IEEE Robotics and Automation Letters (2021),
  DOI `10.1109/LRA.2021.3087085`.

