"""Build a conservative public-index landscape for PPT use.

Unit: one deduplicated paper record whose TITLE satisfies a task-specific rule.
Sources are the saved public-index snapshot (Europe PMC, OpenAlex, Crossref,
arXiv). The output is deliberately a conservative title-screened candidate
map, not a systematic-review inclusion count. OpenAlex is queried only to
record whether a legal public full-text location is identified.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/standalone_snapshots/2026-08-12/literature_multisource_deduplicated.csv"
OUT = ROOT / "outputs/public_landscape"
CACHE = OUT / "openalex_cache"


def rx(pattern: str):
    return re.compile(pattern, re.I)


RULES = [
    # code, domain, label, required concepts in the title
    ("A1", "Active observational sensing", "Robotic ultrasound", rx(r"robot|autonom|automated"), rx(r"ultrasound|sonograph")),
    ("A2", "Active observational sensing", "Robotic endoscopy inspection", rx(r"robot|autonom|self[- ]propell|active"), rx(r"endoscop|colonoscop")),
    ("A3", "Active observational sensing", "Active/magnetic capsule endoscopy", rx(r"capsule"), rx(r"magnet|active|robot|autonom")),
    ("A4", "Active observational sensing", "Robotic bronchoscopy navigation", rx(r"robot|autonom"), rx(r"bronchoscop")),
    ("A5", "Active observational sensing", "Robotic OCT", rx(r"robot|autonom|automated|contactless"), rx(r"optical coherence|\bOCT\b")),
    ("A6", "Active observational sensing", "Robotic auscultation", rx(r"robot|autonom|automated"), rx(r"auscultat|stethoscop")),
    ("R1", "Response-based interactive diagnosis", "Robotic palpation", rx(r"robot|autonom"), rx(r"palpat|tactile.*(tumou?r|mass|tissue)|stiffness.*tissue")),
    ("R2", "Response-based interactive diagnosis", "Robotic elastography/stiffness mapping", rx(r"robot|autonom"), rx(r"elastograph|elasticity|stiffness map|mechanical imaging")),
    ("R3", "Response-based interactive diagnosis", "Robotic joint laxity/provocation", rx(r"robot|automated"), rx(r"laxity|provocation|joint examination|knee testing")),
    ("R4", "Response-based interactive diagnosis", "Robotic tone/spasticity assessment", rx(r"robot|automated|exoskeleton"), rx(r"spastic|muscle tone|passive stretch")),
    ("R5", "Response-based interactive diagnosis", "Robotic percussion/reflex examination", rx(r"robot|autonom|automated"), rx(r"percussion|reflex examination")),
    ("R6", "Response-based interactive diagnosis", "Closed-loop TMS response mapping", rx(r"robot|closed[- ]loop|automated|active learning"), rx(r"transcranial magnetic|\bTMS\b|motor cortex mapping")),
    ("S1", "Sample-based interactive diagnosis", "Robotic percutaneous/core biopsy", rx(r"robot|autonom"), rx(r"biopsy|fine needle aspiration|core needle")),
    ("S2", "Sample-based interactive diagnosis", "Robotic endoscopic/bronchoscopic biopsy", rx(r"robot|autonom"), rx(r"endoscop|bronchoscop"), rx(r"biopsy|sampling|specimen")),
    ("S3", "Sample-based interactive diagnosis", "Capsule tissue/fluid sampling", rx(r"capsule"), rx(r"biopsy|sampling|sample collection|microbiome collection")),
    ("S4", "Sample-based interactive diagnosis", "Robotic venipuncture/phlebotomy", rx(r"robot|autonom|automated"), rx(r"venipuncture|phlebotom|blood draw|blood collection")),
    ("S5", "Sample-based interactive diagnosis", "Robotic swab/specimen collection", rx(r"robot|autonom"), rx(r"swab|nasopharyngeal|oropharyngeal|specimen collection")),
]

EXCLUDE = rx(r"review|survey|editorial|commentary|protocol|simulator|training system|education")

# Task-specific exclusions prevent neighbouring robotic tasks from being
# counted together merely because their titles share a generic word.
TASK_EXCLUDE = {
    "A1": rx(r"pedicle screw|needle|biopsy|ablation|excision|surgery|surgical|intraoperative|therapy|therapeutic|catheter"),
    "A2": rx(r"capsule|bronchoscop|thoracic surgery|surgical|surgery|ultrasound"),
    "A3": rx(r"review|correction|ultrasound 3d tracking"),
    "A4": rx(r"biopsy|sampling|pathologic|cell imaging|confocal"),
    "R1": rx(r"resection|surgical training|teleoperation|tele-palpation|haptic feedback"),
    "S1": rx(r"bronchoscop|endoscop|capsule|tool presence|skull base"),
    "S2": rx(r"capsule"),
}


def matches(title: str, rule) -> bool:
    if EXCLUDE.search(title):
        return False
    if TASK_EXCLUDE.get(rule[0]) and TASK_EXCLUDE[rule[0]].search(title):
        return False
    return all(p.search(title) for p in rule[3:])


def normalized_title_key(title: str) -> str:
    """Collapse punctuation/spacing variants missed by the upstream snapshot."""
    return re.sub(r"[^a-z0-9]+", "", title.casefold())


def oa_lookup(key: str, doi: str, title: str):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    if doi:
        url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi.lower(), safe="/")
    else:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": title, "per-page": 1})
    req = urllib.request.Request(url, headers={"User-Agent": "awesome-embodied-diagnostics-public-landscape/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.load(response)
        if "results" in data:
            data = data["results"][0] if data["results"] else {}
    except Exception as exc:
        data = {"_error": str(exc)}
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    time.sleep(0.08)
    return data


with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    source_rows = list(csv.DictReader(f))

screened = []
seen_task_titles = set()
for row in source_rows:
    title = row["title"].strip()
    for rule in RULES:
        if not matches(title, rule):
            continue
        code, domain, task = rule[:3]
        task_title_key = (code, normalized_title_key(title))
        if task_title_key in seen_task_titles:
            continue
        seen_task_titles.add(task_title_key)
        data = oa_lookup(re.sub(r"[^a-zA-Z0-9]+", "_", row["paper_key"])[-100:], row["doi"], title)
        oa = data.get("open_access") or {}
        best = data.get("best_oa_location") or {}
        public_url = best.get("pdf_url") or best.get("landing_page_url") or ""
        public_hint = any(x in (row["url"] or "").lower() for x in ["arxiv.org", "pmc.ncbi.nlm.nih.gov", "biorxiv.org", "medrxiv.org"])
        fulltext = "yes" if oa.get("is_oa") is True or public_hint else ("no" if oa.get("is_oa") is False else "unresolved")
        screened.append({
            "task_code": code, "domain": domain, "task": task,
            "paper_key": row["paper_key"], "title": title, "year": row["year"],
            "doi": row["doi"], "sources": row["sources"], "record_url": row["url"],
            "public_full_text_identified": fulltext, "best_public_url": public_url,
            "screening_level": "conservative automated title screen",
        })

OUT.mkdir(parents=True, exist_ok=True)
fields = list(screened[0])
with (OUT / "public_title_screened_records.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(screened)

summary = []
for rule in RULES:
    code, domain, task = rule[:3]
    rows = [r for r in screened if r["task_code"] == code]
    summary.append({
        "task_code": code, "domain": domain, "task": task,
        "public_index_title_screened_candidates": len(rows),
        "oa_or_repository_location_identified_automatically": sum(r["public_full_text_identified"] == "yes" for r in rows),
        "full_text_not_identified": sum(r["public_full_text_identified"] == "no" for r in rows),
        "access_unresolved": sum(r["public_full_text_identified"] == "unresolved" for r in rows),
        "since_2021": sum((r["year"].isdigit() and int(r["year"]) >= 2021) for r in rows),
        "counting_unit": "unique deduplicated paper satisfying task-specific title rule",
    })
with (OUT / "public_title_screened_task_counts.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)

domain_summary = []
for domain in sorted({r["domain"] for r in summary}):
    rows = [r for r in screened if r["domain"] == domain]
    domain_summary.append({
        "domain": domain,
        "unique_public_index_candidates": len({r["paper_key"] for r in rows}),
        "unique_with_oa_or_repository_location_identified_automatically": len({r["paper_key"] for r in rows if r["public_full_text_identified"] == "yes"}),
        "counting_unit": "unique paper across task rules within domain",
    })
with (OUT / "public_title_screened_domain_counts.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(domain_summary[0])); w.writeheader(); w.writerows(domain_summary)

(OUT / "METHODS.md").write_text(
    "# Public title-screened landscape\n\n"
    "This is a conservative, reproducible TITLE-level screen of the saved public-index corpus "
    "(Europe PMC, OpenAlex, Crossref and arXiv), deduplicated by DOI or normalized title. "
    "Counts are candidate records, not manually included studies and not global publication totals. "
    "The automated access indicator is taken from OpenAlex OA metadata plus explicit public-repository URLs; "
    "it is a discovery aid and must not be interpreted as a manually verified licence audit. "
    "False negatives are expected because relevant titles may not contain both the embodiment and task concepts. "
    "False positives must be removed by human full-text screening before journal publication.\n",
    encoding="utf-8",
)
print(json.dumps({"source_records": len(source_rows), "screened_task_records": len(screened), "summary": summary}, ensure_ascii=False))
