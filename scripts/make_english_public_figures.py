"""Generate English counterparts for every current public-evidence presentation chart.

The English SVGs use the same frozen CSV/JSON inputs and counting fields as their
Chinese counterparts.  They are presentation translations, not independent
analyses.  PNG rendering is deliberately handled by ``rasterize_svg.mjs`` so the
editable SVG remains the canonical figure.
"""
from __future__ import annotations

import csv
import html
import json
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "presentation")
parser.add_argument("--output-dir", type=Path, default=ROOT / "figures" / "public_evidence")
cli = parser.parse_args()
DATA = cli.data_dir.resolve()
OUT = cli.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)

C = {
    "purple": "#5F1B73", "green": "#2C8068", "orange": "#D9782D",
    "text": "#25152B", "muted": "#6D6470", "grid": "#E8E1EA",
    "gray": "#A69DA8", "white": "#FFFFFF",
}
FONT = "Arial, Helvetica, sans-serif"


def read_csv(name: str) -> list[dict[str, str]]:
    path = DATA / name
    if not path.exists() and name == "public_evidence_maturity_matrix.csv":
        path = DATA / "证据成熟度矩阵.csv"
    if not path.exists():
        local_evidence = DATA.parent / "04_文献与证据" / name
        if local_evidence.exists():
            path = local_evidence
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def save(name: str, width: int, height: int, body: list[str]) -> None:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">' + "".join(body) + "</svg>"
    )
    (OUT / name).write_text(svg, encoding="utf-8")


def landscape(rows: list[dict[str, object]], name: str, title: str,
              visible_key: str, available_key: str, note: str) -> None:
    width, height, left, right, top, bottom = 1600, 820, 510, 105, 125, 120
    plot_w = width - left - right
    row_h = (height - top - bottom) / len(rows)
    maximum = max(int(r[visible_key]) for r in rows)
    body = [f'<rect width="{width}" height="{height}" fill="white"/>',
            f'<text x="60" y="66" font-family="{FONT}" font-size="34" font-weight="700" fill="{C["text"]}">{esc(title)}</text>']
    for tick in range(5):
        x = left + plot_w * tick / 4
        body += [f'<line x1="{x}" y1="{top-20}" x2="{x}" y2="{height-bottom+10}" stroke="{C["grid"]}"/>',
                 f'<text x="{x}" y="{height-bottom+45}" text-anchor="middle" font-family="{FONT}" font-size="19" fill="{C["muted"]}">{round(maximum*tick/4)}</text>']
    for i, row in enumerate(rows):
        y, bar_h = top + i * row_h + row_h * .18, row_h * .52
        visible, available = int(row[visible_key]), int(row[available_key])
        w_visible, w_available = plot_w * visible / maximum, plot_w * available / maximum
        body += [f'<text x="{left-24}" y="{y+bar_h*.72}" text-anchor="end" font-family="{FONT}" font-size="21" fill="{C["text"]}">{esc(row["label"])}</text>',
                 f'<rect x="{left}" y="{y}" width="{w_visible}" height="{bar_h}" rx="7" fill="{C["purple"]}"/>',
                 f'<rect x="{left}" y="{y+bar_h*.31}" width="{w_available}" height="{bar_h*.38}" rx="4" fill="{C["green"]}"/>',
                 f'<text x="{left+w_visible+14}" y="{y+bar_h*.72}" font-family="{FONT}" font-size="23" fill="{C["text"]}">{visible}</text>']
        if available:
            body.append(f'<text x="{left+w_available-8}" y="{y+bar_h*.59}" text-anchor="end" font-family="{FONT}" font-size="16" font-weight="700" fill="white">{available}</text>')
    body += [f'<rect x="720" y="{height-79}" width="24" height="17" rx="3" fill="{C["purple"]}"/><text x="756" y="{height-64}" font-family="{FONT}" font-size="16" fill="{C["muted"]}">public visible: title-screened candidates</text>',
             f'<rect x="1110" y="{height-79}" width="24" height="17" rx="3" fill="{C["green"]}"/><text x="1146" y="{height-64}" font-family="{FONT}" font-size="16" fill="{C["muted"]}">public available: public full-text location identified</text>',
             f'<text x="60" y="{height-28}" font-family="{FONT}" font-size="15" fill="{C["muted"]}">{esc(note)}</text>']
    save(name, width, height, body)


def maturity(rows: list[dict[str, object]], name: str, title: str) -> None:
    width, height, left, right, top, bottom = 1600, 650, 480, 70, 90, 115
    plot_w, row_h = width-left-right, (height-top-bottom)/len(rows)
    levels = ["Not located", "Prototype", "Phantom / in vitro", "Animal / ex vivo", "Human", "Multicentre / controlled", "Outcome / deployment"]
    body = [f'<rect width="{width}" height="{height}" fill="white"/>',
            f'<text x="45" y="52" font-family="{FONT}" font-size="31" font-weight="700" fill="{C["text"]}">{esc(title)}</text>']
    for i, label in enumerate(levels):
        x = left + plot_w*i/6
        body += [f'<line x1="{x}" y1="{top-12}" x2="{x}" y2="{height-bottom+15}" stroke="{C["grid"]}" stroke-dasharray="5 7"/>',
                 f'<text x="{x}" y="{height-bottom+48}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{C["muted"]}">{esc(label)}</text>']
    for i, row in enumerate(rows):
        level = int(row["maturity_level"]); y = top+i*row_h+row_h/2; x = left+plot_w*level/6
        color = C["orange"] if level <= 3 else C["green"]
        body += [f'<text x="{left-20}" y="{y+7}" text-anchor="end" font-family="{FONT}" font-size="21" fill="{C["text"]}">{esc(row["label"])}</text>',
                 f'<line x1="{left}" y1="{y}" x2="{x}" y2="{y}" stroke="{C["grid"]}" stroke-width="8" stroke-linecap="round"/>',
                 f'<circle cx="{x}" cy="{y}" r="16" fill="{color}" stroke="white" stroke-width="3"/>']
    body.append(f'<text x="45" y="{height-25}" font-family="{FONT}" font-size="15" fill="{C["muted"]}">Highest evidence level located in publicly verifiable primary studies; it does not imply full-loop autonomy and is not a publication-volume metric.</text>')
    save(name, width, height, body)


def old_public_figures() -> None:
    matrix = {r["task_code"]: r for r in read_csv("public_evidence_maturity_matrix.csv")}
    active = [("A1", "Robotic ultrasound"), ("A3", "Active / magnetically controlled capsule"),
              ("A2", "Robotic GI endoscopic inspection"), ("A4", "Robotic bronchoscopy navigation"),
              ("A5", "Robotic OCT"), ("A6", "Robotic auscultation")]
    response = [("R1", "Robotic palpation"), ("R2", "Elasticity / stiffness mapping"),
                ("R6", "Closed-loop TMS response mapping"), ("R3", "Joint laxity / provocation"),
                ("R4", "Tone / spasticity assessment"), ("R5", "Percussion / reflex examination")]
    sample = [("S1", "Percutaneous / core-needle biopsy"), ("S4", "Venipuncture / blood collection"),
              ("S5", "Swab / specimen collection"), ("S2", "Endoscopic / bronchoscopic biopsy"),
              ("S3", "Capsule tissue / fluid sampling")]
    def rows(spec):
        return [{**matrix[code], "label": label} for code, label in spec]
    note = "Deduplicated papers in frozen public-index snapshots (Europe PMC, OpenAlex, Crossref and arXiv); title-rule screening; not systematic-review inclusions."
    landscape(rows(active), "p5_active_public_landscape_en.svg", "Active observational sensing | Public-source research landscape", "public_index_title_screened_candidates", "oa_or_repository_location_identified_automatically", note)
    landscape(rows(response), "p9_response_public_landscape_en.svg", "Response-based interactive diagnosis | Public-source title-screened candidates", "public_index_title_screened_candidates", "oa_or_repository_location_identified_automatically", note)
    landscape(rows(sample), "p13_sample_public_landscape_en.svg", "Sample-based interactive diagnosis | Public-source title-screened candidates", "public_index_title_screened_candidates", "oa_or_repository_location_identified_automatically", note)
    maturity(rows(response), "p9_response_maturity_en.svg", "Highest publicly verifiable evidence maturity")
    maturity(rows(sample), "p13_sample_maturity_en.svg", "Highest publicly verifiable evidence maturity")


def extended_p5() -> None:
    source = read_csv("p5_public_visible_available_counts_2026-08-13.csv")
    labels = {
        "A1":"Robotic ultrasound", "A2":"Robotic GI endoscopic inspection", "A3":"Active / magnetically controlled capsule endoscopy",
        "A4":"Robotic bronchoscopy observation / navigation", "A5":"Robotic OCT", "A6":"Robotic auscultation",
        "A7":"Robotic fundus / slit-lamp imaging", "A8":"Robotic otoscopy", "A9":"Robotic skin / wound surface scanning",
        "A10":"Robotic spectroscopic / optical scanning", "A11":"Robotic laryngoscopy / oral examination",
    }
    rows = [{**r, "label": labels[r["task_code"]]} for r in sorted(source, key=lambda x:int(x["public_visible_precision_title_candidates"]), reverse=True)]
    landscape(rows, "p5_public_visible_available_extended_en.svg", "Active observational sensing | Public-visible and public-full-text candidate landscape", "public_visible_precision_title_candidates", "public_available_location_identified", "Public indexes: OpenAlex and Europe PMC, supplemented by Crossref/arXiv; 2000–13 Aug 2026. Deduplicated by DOI/title. Candidate counts are not full-text systematic-review inclusions; availability is not a licence audit.")


def reclassified_p5() -> None:
    counts = read_csv("p5_reclassified_task_counts_2026-08-14.csv")
    qc = json.loads((DATA / "p5_reclassification_qc_2026-08-14.json").read_text(encoding="utf-8"))
    projects = read_csv("p5_reclassified_public_projects_2026-08-14.csv")
    rows = sorted((r for r in counts if r["primary_task_code"] != "T9"), key=lambda x:int(x["public_visible_unique_title_candidates"]), reverse=True)
    generic = next(r for r in counts if r["primary_task_code"] == "T9")
    clinical_total = sum(int(r["public_visible_unique_title_candidates"]) for r in rows)
    width, height, left, chart_right, top, bottom = 1920, 1080, 520, 1320, 170, 185
    chart_w = chart_right-left; row_h=(height-top-bottom)/len(rows); maximum=max(int(r["public_visible_unique_title_candidates"]) for r in rows)
    body=[f'<rect width="{width}" height="{height}" fill="white"/>',
          f'<text x="60" y="66" font-family="{FONT}" font-size="38" font-weight="700" fill="{C["text"]}">Active observational sensing | Reclassified by clinical evidence-acquisition task</text>',
          f'<text x="60" y="108" font-family="{FONT}" font-size="22" fill="{C["muted"]}">Modality and embodiment are secondary tags; generic platforms without a clinical site are moved out of the main bars</text>']
    for i in range(5):
        x=left+chart_w*i/4
        body += [f'<line x1="{x}" y1="{top-18}" x2="{x}" y2="{height-bottom+10}" stroke="{C["grid"]}"/>',
                 f'<text x="{x}" y="{height-bottom+42}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="{C["muted"]}">{round(maximum*i/4)}</text>']
    for i,r in enumerate(rows):
        y=top+i*row_h+row_h*.15; bar_h=row_h*.56; visible=int(r["public_visible_unique_title_candidates"]); available=int(r["public_available_location_identified"])
        wv=chart_w*visible/maximum; wa=chart_w*available/maximum
        body += [f'<text x="{left-24}" y="{y+bar_h*.70}" text-anchor="end" font-family="{FONT}" font-size="19" fill="{C["text"]}">{esc(r["primary_task_en"])}</text>',
                 f'<rect x="{left}" y="{y}" width="{wv}" height="{bar_h}" rx="7" fill="{C["purple"]}"/>',
                 f'<rect x="{left}" y="{y+bar_h*.30}" width="{wa}" height="{bar_h*.40}" rx="4" fill="{C["green"]}"/>',
                 f'<text x="{left+wv+12}" y="{y+bar_h*.70}" font-family="{FONT}" font-size="20" fill="{C["text"]}">{visible}</text>']
        if available:
            body.append(f'<text x="{left+max(wa-7,12)}" y="{y+bar_h*.60}" text-anchor="end" font-family="{FONT}" font-size="14" font-weight="700" fill="white">{available}</text>')
    x0=1400
    body += [f'<text x="{x0}" y="180" font-family="{FONT}" font-size="24" font-weight="700" fill="{C["text"]}">Count reconciliation</text>']
    flow=[("Prior task assignments",qc["task_assignment_rows"]),("Unique papers",qc["unique_works"]),("Title-level exclusions",qc["excluded_by_title_scope_rules"]),("Reclassified candidates",qc["included_title_candidates"])]
    for i,(label,value) in enumerate(flow):
        y=220+i*66
        body += [f'<text x="{x0}" y="{y}" font-family="{FONT}" font-size="18" fill="{C["muted"]}">{label}</text>',
                 f'<text x="1815" y="{y}" text-anchor="end" font-family="{FONT}" font-size="27" font-weight="700" fill="{C["purple"] if i==3 else C["text"]}">{value}</text>']
        if i<3: body.append(f'<line x1="{x0}" y1="{y+18}" x2="1815" y2="{y+18}" stroke="{C["grid"]}"/>')
    body += [f'<line x1="{x0}" y1="505" x2="1815" y2="505" stroke="{C["grid"]}"/>',
             f'<text x="{x0}" y="552" font-family="{FONT}" font-size="22" font-weight="700" fill="{C["text"]}">Figure stratification</text>',
             f'<text x="{x0}" y="596" font-family="{FONT}" font-size="18" fill="{C["muted"]}">Eight site-resolved clinical tasks</text><text x="1815" y="596" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="700" fill="{C["purple"]}">{clinical_total}</text>',
             f'<text x="{x0}" y="642" font-family="{FONT}" font-size="18" fill="{C["muted"]}">Generic platforms; clinical site unresolved</text><text x="1815" y="642" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="700" fill="{C["gray"]}">{generic["public_visible_unique_title_candidates"]}</text>',
             f'<text x="{x0}" y="688" font-family="{FONT}" font-size="18" fill="{C["muted"]}">Separate ledger: named projects / systems</text><text x="1815" y="688" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="700" fill="{C["green"]}">{len(projects)}</text>',
             f'<text x="{x0}" y="734" font-family="{FONT}" font-size="18" fill="{C["muted"]}">Priority manual-review queue</text><text x="1815" y="734" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="700" fill="#7B3B8D">{qc["priority_manual_review"]}</text>',
             f'<rect x="1000" y="966" width="24" height="17" rx="3" fill="{C["purple"]}"/><text x="1036" y="981" font-family="{FONT}" font-size="16" fill="{C["muted"]}">public visible: public-index title candidates</text>',
             f'<rect x="1405" y="966" width="24" height="17" rx="3" fill="{C["green"]}"/><text x="1441" y="981" font-family="{FONT}" font-size="16" fill="{C["muted"]}">public available: public full-text location identified</text>',
             f'<text x="60" y="1025" font-family="{FONT}" font-size="14" fill="{C["muted"]}">Public-index freeze: 13 Aug 2026; reclassification: 14 Aug 2026. DOI-first/title-second deduplication. The 834 records are title-level candidates, not systematic-review inclusions; locations were not individually licence-audited.</text>']
    save("p5_reclassified_clinical_tasks_en.svg",width,height,body)

    matrix_rows=read_csv("p5_task_modality_matrix_2026-08-14.csv")
    lookup={(r["primary_task_code"],r["modality_tag"]):r for r in matrix_rows}
    groups=[("Ultrasound",["ultrasound"]),("OCT",["OCT"]),("Endoscopic / cavity imaging*",["endoscopic_imaging_unspecified","capsule_endoscopic_imaging_unspecified","bronchoscopic_imaging_unspecified","cavity_visual_imaging_unspecified"]),("Confocal / endomicroscopy",["confocal_endomicroscopy"]),("Photoacoustic",["photoacoustic"]),("Raman / DRS",["Raman_DRS_spectroscopy"]),("Other optical / RGB",["white_light_RGB_video","other_optical","ophthalmic_imaging_unspecified","surface_imaging_unspecified"]),("Physiological sound",["acoustic_physiological_sound"])]
    width,height,left,top,cell_w,cell_h=1920,1080,540,220,160,74
    body=[f'<rect width="{width}" height="{height}" fill="white"/>',f'<text x="60" y="68" font-family="{FONT}" font-size="38" font-weight="700" fill="{C["text"]}">Active observational sensing | Clinical task × sensing modality</text>',f'<text x="60" y="110" font-family="{FONT}" font-size="22" fill="{C["muted"]}">Modality is multi-label; cells show public visible / public available and must not be summed across columns</text>']
    for j,(label,_) in enumerate(groups):
        x=left+j*cell_w+cell_w/2; words=label.split(" / ")
        body.append(f'<text x="{x}" y="168" text-anchor="middle" font-family="{FONT}" font-size="15" font-weight="700" fill="{C["text"]}">{esc(words[0])}</text>')
        if len(words)>1: body.append(f'<text x="{x}" y="190" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="700" fill="{C["text"]}">{esc("/ ".join(words[1:]))}</text>')
    for i,code in enumerate([f"T{x}" for x in range(1,10)]):
        task=next(r for r in counts if r["primary_task_code"]==code); y=top+i*cell_h
        body.append(f'<text x="{left-25}" y="{y+45}" text-anchor="end" font-family="{FONT}" font-size="17" fill="{C["muted"] if code=="T9" else C["text"]}">{esc(task["primary_task_en"])}</text>')
        for j,(_,tags) in enumerate(groups):
            visible=available=0
            for tag in tags:
                r=lookup.get((code,tag))
                if r: visible+=int(r["public_visible_unique_title_candidates"]); available+=int(r["public_available_location_identified"])
            x=left+j*cell_w; alpha=min(.10+.55*(__import__("math").log10(visible+1))/2.6,.65) if visible else 0
            body.append(f'<rect x="{x+5}" y="{y+5}" width="{cell_w-10}" height="{cell_h-10}" rx="7" fill="{C["purple"]}" fill-opacity="{alpha:.3f}" stroke="{C["grid"]}"/>')
            if visible: body.append(f'<text x="{x+cell_w/2}" y="{y+35}" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="{C["text"]}">{visible}<tspan fill="{C["muted"]}" font-size="16"> / </tspan><tspan fill="{C["green"]}" font-size="18">{available}</tspan></text>')
            else: body.append(f'<text x="{x+cell_w/2}" y="{y+39}" text-anchor="middle" font-family="{FONT}" font-size="18" fill="#C9C2CB">–</text>')
    body += [f'<text x="60" y="938" font-family="{FONT}" font-size="16" fill="{C["muted"]}">* “Endoscopic / cavity imaging” means that the title did not specify OCT, confocal, photoacoustic or another modality; it is not an inferred modality for all endoscopy papers.</text>',f'<text x="60" y="978" font-family="{FONT}" font-size="16" fill="{C["muted"]}">OCT, confocal, photoacoustic and spectroscopic records are assigned to clinical tasks; T9 retains only generic platforms whose clinical site cannot be identified from the title.</text>',f'<text x="60" y="1025" font-family="{FONT}" font-size="14" fill="{C["muted"]}">Scope and sources match the main P5 chart. Modalities are title-explicit terms; “unspecified” tags are used when the title lacks a specific modality. Multi-label modality counts are not unique-paper totals.</text>']
    save("p5_task_modality_matrix_en.svg",width,height,body)


if __name__ == "__main__":
    old_public_figures()
    extended_p5()
    reclassified_p5()
    print("Generated English SVG counterparts in figures/public_evidence")
