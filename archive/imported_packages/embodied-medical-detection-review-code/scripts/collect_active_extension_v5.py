#!/usr/bin/env python3
"""Retrieve and screen A8--A10 active-observation task families.

This focused extension uses the same three sources, cutoff, DOI/title
deduplication logic, original-research exclusion, and strict/broad evidence
tiers as the existing A1--A7 corpus.  It does not estimate missing counts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from collect_bibliometrics import (
    CUTOFF,
    START_DATE,
    Task,
    arxiv_to_record,
    arxiv_url,
    europepmc_to_record,
    fetch_json,
    fetch_xml,
    merge_records,
    normalize_title,
    openalex_to_record,
    phrase_query,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "active_extension_v5"
CACHE_DIR = OUT_DIR / "cache"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


TASKS = (
    Task(
        "A8", "A", "Active observational sensing", "主动观察式检测",
        "Robotic ionizing-radiation / nuclear imaging acquisition",
        "机器人电离辐射 / 核医学成像采集",
        (
            "robotic X-ray imaging", "robotic X-ray system", "robotic X-ray device",
            "robot-assisted X-ray imaging", "robotic radiography", "robot-assisted radiography",
            "autonomous radiography", "robotic fluoroscopy", "robotic C-arm imaging",
            "robotic cone-beam CT", "robotic cone beam CT", "robotic computed tomography",
            "robotic CT imaging", "robotic SPECT", "robotic gamma imaging",
            "robot-mounted gamma camera", "robotic nuclear imaging", "robotic freehand SPECT",
        ),
        r"x[- ]?ray|radiograph\w*|fluoroscop\w*|\bC[- ]?arm\b|cone[- ]?beam (?:CT|computed tomography)|"
        r"computed tomography|\bCT imag\w*|\bSPECT\b|gamma (?:camera|imag\w*)|nuclear imag\w*",
        "机器人改变 X-ray/CT/荧光透视或 gamma/SPECT 成像装置的位置、方向或轨迹以获取临床影像。",
        "排除放疗/消融等治疗源定位、工业检测，以及仅在机器人手术中使用固定影像而成像装置本身不具备机器人运动。",
    ),
    Task(
        "A9", "A", "Active observational sensing", "主动观察式检测",
        "Robotic microscopy / confocal endomicroscopy",
        "机器人显微 / 共聚焦内显微扫描",
        (
            "robotic endomicroscopy", "robot-assisted endomicroscopy",
            "robotic confocal endomicroscopy", "robotic confocal laser endomicroscopy",
            "robot-assisted confocal laser endomicroscopy", "robotic pCLE", "robot-assisted pCLE",
            "robotic microscopy scanning", "robot-assisted microscopy", "robotic microscopy",
            "robotic optical biopsy", "robotized operating microscope",
            "robotic operating microscope", "robotic surgical microscope",
        ),
        r"endomicroscop\w*|confocal laser endomicroscop\w*|\bpCLE\b|optical biops\w*|"
        r"(?:operating|surgical|neurosurgical) microscop\w*|microscop\w* scan\w*|robotic microscop\w*",
        "机器人主动移动显微/内显微探头、维持焦距并扫描组织，以获得细胞或微结构层面的诊断观察。",
        "排除离体实验室显微自动化、单纯显微外科器械操作，以及显微镜固定不动的机器人手术。",
    ),
    Task(
        "A10", "A", "Active observational sensing", "主动观察式检测",
        "Embodied non-contact vital-sign monitoring",
        "具身式非接触生命体征监测",
        (
            "robotic vital sign monitoring", "robotic vital signs monitoring",
            "robot vital sign monitoring", "robot vital signs monitoring",
            "mobile robot vital sign monitoring", "mobile robotic platform for contactless vital sign monitoring",
            "contactless vital sign monitoring robot", "robotic contactless vital signs",
            "robotic physiological monitoring", "robotic respiratory rate monitoring",
            "robotic heart rate monitoring", "robot-mounted radar vital signs",
            "embodied vital signs monitoring", "vital sign measurement robot",
            "autonomous vital sign measurement", "robotic patient monitoring vital signs",
        ),
        r"vital sign\w*|heart rate|respirat(?:ory|ion) rate|breathing rate|pulse rate|"
        r"oxygen saturation|\bSpO2\b|physiological monitor\w*",
        "移动机器人或可运动传感器主动调整与患者的距离、角度或视点并非接触测量生命体征。",
        "排除固定式摄像头/雷达、仅承担远程通话的遥现机器人、可穿戴设备及没有自主传感器定位的静态监护仪。",
    ),
)
TASK_BY_CODE = {task.code: task for task in TASKS}


OPENALEX_BLOCKS = {
    "A8": (
        "robot x-ray medical imaging", "robot radiography patient", "robot fluoroscopy imaging",
        "robot c-arm imaging", "robot cone beam computed tomography imaging",
        "robot gamma camera medical imaging", "robot SPECT imaging",
    ),
    "A9": (
        "robot endomicroscopy", "robot confocal laser endomicroscopy", "robot pCLE",
        "robot medical microscopy scanning", "robot operating microscope imaging",
    ),
    "A10": (
        "robot vital signs monitoring", "robot contactless physiological monitoring",
        "mobile robot heart respiratory rate monitoring", "robot contactless patient monitoring",
    ),
}


EUROPEPMC_QUERIES = {
    "A8": (
        'TITLE_ABS:"robotic X-ray" OR TITLE_ABS:"robot-assisted X-ray" OR '
        'TITLE_ABS:"robotic radiography" OR TITLE_ABS:"robot-assisted radiography" OR '
        'TITLE_ABS:"autonomous radiography" OR TITLE_ABS:"robotic fluoroscopy" OR '
        'TITLE_ABS:"robotic C-arm" OR TITLE_ABS:"robotic cone-beam CT" OR '
        'TITLE_ABS:"robotic computed tomography" OR TITLE_ABS:"robotic SPECT" OR '
        'TITLE_ABS:"robotic gamma imaging" OR TITLE_ABS:"robot-mounted gamma camera"'
    ),
    "A9": (
        '(TITLE_ABS:robot* OR TITLE_ABS:autonom*) AND '
        '(TITLE_ABS:endomicroscop* OR TITLE_ABS:"confocal laser endomicroscopy" OR '
        ' TITLE_ABS:pCLE OR TITLE_ABS:"operating microscope" OR TITLE_ABS:"robotic microscopy")'
    ),
    "A10": (
        '(TITLE_ABS:robot* OR TITLE_ABS:embodied OR TITLE_ABS:"mobile robotic") AND '
        '(TITLE_ABS:"vital sign" OR TITLE_ABS:"vital signs" OR TITLE_ABS:"heart rate" OR '
        ' TITLE_ABS:"respiratory rate" OR TITLE_ABS:"breathing rate" OR TITLE_ABS:SpO2)'
    ),
}


ARXIV_QUERIES = {
    "A8": '((ti:robot* OR abs:robot* OR ti:autonom* OR abs:autonom*) AND '
          '(ti:"x-ray" OR abs:"x-ray" OR ti:radiograph* OR abs:radiograph* OR '
          ' ti:fluoroscop* OR abs:fluoroscop* OR ti:"c-arm" OR abs:"c-arm" OR '
          ' ti:"cone beam ct" OR abs:"cone beam ct" OR ti:spect OR abs:spect OR '
          ' ti:"gamma camera" OR abs:"gamma camera"))',
    "A9": '((ti:robot* OR abs:robot* OR ti:autonom* OR abs:autonom*) AND '
          '(ti:endomicroscop* OR abs:endomicroscop* OR ti:"confocal laser endomicroscopy" OR '
          ' abs:"confocal laser endomicroscopy" OR ti:pcle OR abs:pcle OR '
          ' ti:"operating microscope" OR abs:"operating microscope" OR '
          ' ti:"robotic microscopy" OR abs:"robotic microscopy"))',
    "A10": '((ti:robot* OR abs:robot* OR ti:embodied OR abs:embodied OR '
           ' ti:"mobile robotic" OR abs:"mobile robotic") AND '
           '(ti:"vital sign" OR abs:"vital sign" OR ti:"vital signs" OR abs:"vital signs" OR '
           ' ti:"heart rate" OR abs:"heart rate" OR ti:"respiratory rate" OR abs:"respiratory rate" OR '
           ' ti:"breathing rate" OR abs:"breathing rate" OR ti:spo2 OR abs:spo2))',
}


REVIEW_RE = re.compile(
    r"\b(review|meta[- ]analysis|survey|overview|perspective|editorial|bibliometric)\b|"
    r"state[- ]of[- ]the[- ]art|current trends|recent advances",
    re.I,
)
ROBOT_RE = re.compile(r"\brobot\w*\b|\bautonom\w*\b|\bembodied\b|\btelerobot\w*\b", re.I)
INDUSTRIAL_RE = re.compile(
    r"industrial|manufactur|pipeline|weld|aerospace|airport|baggage|security screening|"
    r"non[- ]destructive|additive manufacturing|semiconductor|agricultur|food|fruit|"
    r"concrete|bridge|battery|cultural heritage|archaeolog|paleontolog|small animal|mouse|mice|rat\b",
    re.I,
)
TREATMENT_ONLY_RE = re.compile(
    r"radiotherap|radiosurg|radiation therap|proton therap|brachytherap|ablat\w*|"
    r"irradiat\w*|dose delivery|beam delivery|patient position\w* for treatment",
    re.I,
)
LAB_MICRO_RE = re.compile(
    r"cell cultur|microplate|high[- ]throughput|laboratory automation|microfluidic|"
    r"single[- ]cell|colony picking|wafer|semiconductor|materials? characteri[sz]ation|"
    r"microscope slide|histology slide scanning|pathology slide scanner",
    re.I,
)
CLINICAL_MICRO_RE = re.compile(
    r"patient|human|clinical|medical|surg\w*|retina|brain|neurosurg|tumou?r|cancer|"
    r"tissue|organ|intraoper|diagnos\w*|optical biops\w*|endoscop\w*|in vivo|porcine|animal model",
    re.I,
)
VITAL_RE = re.compile(
    r"vital sign\w*|heart rate|respirat(?:ory|ion) rate|breathing rate|pulse rate|"
    r"oxygen saturation|\bSpO2\b|body temperature|skin temperature",
    re.I,
)
FIXED_VITAL_RE = re.compile(
    r"fixed camera|stationary camera|bedside camera|wearable|smartwatch|smart phone|smartphone|"
    r"automotive|driver monitoring|infant incubator|radar sensor only",
    re.I,
)


def openalex_url(search_text: str, cursor: str) -> str:
    filters = ",".join(
        (
            f"title_and_abstract.search:{search_text}",
            f"from_publication_date:{START_DATE}",
            f"to_publication_date:{CUTOFF}",
            "type:article|preprint|report|dissertation",
        )
    )
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"filter": filters, "per-page": 200, "cursor": cursor}
    )


def collect_openalex(task: Task, refresh: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cache = CACHE_DIR / f"openalex_{task.code}.json"
    if cache.exists() and not refresh:
        data = json.loads(cache.read_text(encoding="utf-8"))
        return data["records"], data["blocks"]
    blocks = (phrase_query(task.phrases), *OPENALEX_BLOCKS[task.code])
    records: dict[str, dict[str, Any]] = {}
    block_log: list[dict[str, Any]] = []
    for search_text in blocks:
        cursor = "*"
        retrieved = 0
        hit_count = 0
        while cursor:
            payload = fetch_json(openalex_url(search_text, cursor))
            hit_count = int(payload.get("meta", {}).get("count", 0))
            page = payload.get("results", [])
            retrieved += len(page)
            for raw in page:
                key = raw.get("id") or hashlib.sha1(json.dumps(raw, sort_keys=True).encode()).hexdigest()
                records[key] = raw
            next_cursor = payload.get("meta", {}).get("next_cursor")
            if not page or not next_cursor:
                break
            cursor = next_cursor
            time.sleep(0.12)
        block_log.append({"query": search_text, "hit_count": hit_count, "retrieved": retrieved})
    result = list(records.values())
    cache.write_text(json.dumps({"records": result, "blocks": block_log}, ensure_ascii=False), encoding="utf-8")
    return result, block_log


def collect_europepmc(task: Task, refresh: bool = False) -> tuple[list[dict[str, Any]], int]:
    cache = CACHE_DIR / f"europepmc_{task.code}.json"
    if cache.exists() and not refresh:
        data = json.loads(cache.read_text(encoding="utf-8"))
        return data["records"], data["hit_count"]
    query = f'({EUROPEPMC_QUERIES[task.code]}) AND FIRST_PDATE:[{START_DATE[:4]} TO {CUTOFF[:4]}]'
    cursor = "*"
    records: list[dict[str, Any]] = []
    hit_count = 0
    while cursor:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": query, "format": "json", "resultType": "core", "pageSize": 1000, "cursorMark": cursor}
        )
        payload = fetch_json(url)
        hit_count = int(payload.get("hitCount", 0))
        page = payload.get("resultList", {}).get("result", [])
        records.extend(page)
        next_cursor = payload.get("nextCursorMark")
        if not page or not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.12)
    cache.write_text(json.dumps({"query": query, "hit_count": hit_count, "records": records}, ensure_ascii=False), encoding="utf-8")
    return records, hit_count


def collect_arxiv(task: Task, refresh: bool = False) -> tuple[list[dict[str, Any]], int]:
    cache = CACHE_DIR / f"arxiv_{task.code}.json"
    if cache.exists() and not refresh:
        data = json.loads(cache.read_text(encoding="utf-8"))
        return data["records"], data["hit_count"]
    query = ARXIV_QUERIES[task.code] + f" AND submittedDate:[{START_DATE.replace('-', '')}0000 TO {CUTOFF.replace('-', '')}2359]"
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "open": "http://a9.com/-/spec/opensearch/1.1/",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    records: list[dict[str, Any]] = []
    start = 0
    hit_count = 0
    while True:
        if start:
            time.sleep(3.1)
        root = fetch_xml(arxiv_url(query, start=start, max_results=2000))
        hit_count = int(root.findtext("open:totalResults", default="0", namespaces=ns) or 0)
        entries = root.findall("atom:entry", ns)
        for entry in entries:
            entry_id = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
            records.append(
                {
                    "id": entry_id.rsplit("/", 1)[-1],
                    "entry_id": entry_id,
                    "title": re.sub(r"\s+", " ", entry.findtext("atom:title", default="", namespaces=ns) or "").strip(),
                    "summary": re.sub(r"\s+", " ", entry.findtext("atom:summary", default="", namespaces=ns) or "").strip(),
                    "published": (entry.findtext("atom:published", default="", namespaces=ns) or "").strip(),
                    "updated": (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip(),
                    "doi": (entry.findtext("arxiv:doi", default="", namespaces=ns) or "").strip().lower(),
                    "journal_ref": (entry.findtext("arxiv:journal_ref", default="", namespaces=ns) or "").strip(),
                    "categories": [node.attrib.get("term", "") for node in entry.findall("atom:category", ns)],
                    "authors": [
                        (node.findtext("atom:name", default="", namespaces=ns) or "").strip()
                        for node in entry.findall("atom:author", ns)
                    ],
                }
            )
        start += len(entries)
        if not entries or start >= hit_count:
            break
    cache.write_text(json.dumps({"query": query, "hit_count": hit_count, "records": records}, ensure_ascii=False), encoding="utf-8")
    return records, hit_count


def screen(task: Task, rec: dict[str, Any]) -> dict[str, Any]:
    title = str(rec.get("title") or "")
    abstract = str(rec.get("abstract") or "")
    text = f"{title}. {abstract}"
    title_robot = bool(ROBOT_RE.search(title))
    text_robot = bool(ROBOT_RE.search(text))
    modality_title = bool(re.search(task.task_pattern, title, re.I))
    modality_text = bool(re.search(task.task_pattern, text, re.I))
    included = False
    reason = ""
    if REVIEW_RE.search(title):
        reason = "review / survey"
    elif not text_robot or not modality_text:
        reason = "embodied action or evidence modality not explicit"
    elif INDUSTRIAL_RE.search(text):
        reason = "industrial / non-patient application"
    elif task.code == "A8":
        if TREATMENT_ONLY_RE.search(title) and not re.search(r"imag\w*|view|locali[sz]|scan|tomograph|guidance|acquisition", title, re.I):
            reason = "treatment source positioning without diagnostic acquisition"
        elif re.search(r"robotic[- ]assisted (?:bronchoscop|surg|resection|biops|orthopedic|spine)", title, re.I) and not re.search(
            r"robotic (?:x[- ]?ray|radiograph|fluoroscop|c[- ]?arm|cone[- ]?beam|computed tomography|CT|SPECT|gamma)", title, re.I
        ):
            reason = "robot modifies another procedure; imaging platform not the primary task"
        else:
            included = True
    elif task.code == "A9":
        if LAB_MICRO_RE.search(text):
            reason = "laboratory microscopy automation"
        elif not CLINICAL_MICRO_RE.search(text):
            reason = "no clinical/in-vivo tissue context"
        elif re.search(r"microsurg\w*|micro[- ]?sut|needle|dissection|manipulat\w*", title, re.I) and not re.search(
            r"imag\w*|scan\w*|mosaic|focus|endomicroscop|microscope", title, re.I
        ):
            reason = "microsurgical manipulation without robotic sensing"
        else:
            included = True
    elif task.code == "A10":
        mobile_context = bool(re.search(r"mobile robot|robotic platform|quadruped|humanoid|embodied|robot-mounted|autonomous robot|healthcare robot", text, re.I))
        if not VITAL_RE.search(text):
            reason = "no vital-sign outcome"
        elif FIXED_VITAL_RE.search(title) and not mobile_context:
            reason = "fixed or wearable sensing"
        elif not mobile_context:
            reason = "no sensor-positioning/mobile embodiment"
        else:
            included = True
    tier = "Core (title-explicit)" if included and title_robot and modality_title else (
        "Expanded (abstract-supported)" if included else ""
    )
    rec = rec.copy()
    rec.update(
        {
            "included": included,
            "exclusion_reason": reason,
            "primary_task": task.code if included else "",
            "class_code": "A" if included else "",
            "class_en": task.class_en if included else "",
            "class_zh": task.class_zh if included else "",
            "task_en": task.task_en if included else "",
            "task_zh": task.task_zh if included else "",
            "evidence_tier": tier,
            "normalized_title": normalize_title(title),
        }
    )
    return rec


def serializable(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "source_dbs", "source_ids", "doi", "pmid", "title", "year", "publication_date",
        "work_type", "venue", "cited_by_count", "url", "query_tasks", "included",
        "exclusion_reason", "class_code", "class_en", "class_zh", "primary_task",
        "task_en", "task_zh", "evidence_tier", "abstract",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            cooked = {k: serializable(v) for k, v in row.items()}
            for key, value in cooked.items():
                if isinstance(value, (list, tuple)):
                    cooked[key] = "; ".join(str(item) for item in value)
            writer.writerow(cooked)


def main() -> None:
    all_raw: list[dict[str, Any]] = []
    query_log: list[dict[str, Any]] = []

    def collect_non_arxiv(task: Task):
        oa, oa_blocks = collect_openalex(task)
        ep, ep_hits = collect_europepmc(task)
        return task, oa, oa_blocks, ep, ep_hits

    completed = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(collect_non_arxiv, task): task.code for task in TASKS}
        for future in as_completed(futures):
            result = future.result()
            completed[result[0].code] = result
            task, oa, blocks, ep, ep_hits = result
            print(task.code, "OpenAlex", sum(b["hit_count"] for b in blocks), len(oa), "EuropePMC", ep_hits, len(ep), flush=True)

    arxiv_completed = {}
    for index, task in enumerate(TASKS):
        if index:
            time.sleep(3.1)
        ax, ax_hits = collect_arxiv(task)
        arxiv_completed[task.code] = (ax, ax_hits)
        print(task.code, "arXiv", ax_hits, len(ax), flush=True)

    for task in TASKS:
        _, oa, blocks, ep, ep_hits = completed[task.code]
        ax, ax_hits = arxiv_completed[task.code]
        all_raw.extend(openalex_to_record(raw, task.code) for raw in oa)
        all_raw.extend(europepmc_to_record(raw, task.code) for raw in ep)
        all_raw.extend(arxiv_to_record(raw, task.code) for raw in ax)
        query_log.extend(
            [
                {"database": "OpenAlex", "task_code": task.code, "raw_hit_count": sum(b["hit_count"] for b in blocks), "retrieved_records": len(oa), "query": json.dumps(blocks, ensure_ascii=False)},
                {"database": "Europe PMC", "task_code": task.code, "raw_hit_count": ep_hits, "retrieved_records": len(ep), "query": EUROPEPMC_QUERIES[task.code]},
                {"database": "arXiv", "task_code": task.code, "raw_hit_count": ax_hits, "retrieved_records": len(ax), "query": ARXIV_QUERIES[task.code]},
            ]
        )

    merged = merge_records(all_raw)
    screened: list[dict[str, Any]] = []
    for rec in merged:
        possible = [TASK_BY_CODE[code] for code in sorted(rec["query_tasks"]) if code in TASK_BY_CODE]
        decisions = [screen(task, rec) for task in possible]
        included_decisions = [item for item in decisions if item["included"]]
        if included_decisions:
            # Prefer title-explicit evidence; then choose the most specific task code.
            included_decisions.sort(key=lambda item: (item["evidence_tier"] != "Core (title-explicit)", item["primary_task"]))
            screened.append(included_decisions[0])
        else:
            base = decisions[0] if decisions else rec.copy()
            base["included"] = False
            base["exclusion_reason"] = " | ".join(sorted({item["exclusion_reason"] for item in decisions if item["exclusion_reason"]}))
            screened.append(base)

    included = [row for row in screened if row.get("included")]
    included.sort(key=lambda row: (row.get("primary_task", ""), int(row.get("year") or 0), row.get("title", "")))
    screened.sort(key=lambda row: (not row.get("included", False), row.get("primary_task", ""), int(row.get("year") or 0), row.get("title", "")))
    counts = Counter(row["primary_task"] for row in included)
    core_counts = Counter(row["primary_task"] for row in included if row["evidence_tier"] == "Core (title-explicit)")
    print("Included", dict(sorted(counts.items())))
    print("Core", dict(sorted(core_counts.items())))
    print("raw", len(all_raw), "merged", len(merged), "included", len(included))

    write_csv(OUT_DIR / "candidates_auto_screened.csv", screened)
    write_csv(OUT_DIR / "included_auto_screened.csv", included)
    (OUT_DIR / "query_log.json").write_text(json.dumps(query_log, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "tasks.json").write_text(json.dumps([asdict(task) for task in TASKS], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "metadata.json").write_text(
        json.dumps(
            {
                "cutoff": CUTOFF,
                "retrieved_on": date.today().isoformat(),
                "databases": ["OpenAlex", "Europe PMC", "arXiv"],
                "raw_records": len(all_raw),
                "deduplicated_candidates": len(merged),
                "auto_included": len(included),
                "task_counts": dict(sorted(counts.items())),
                "core_task_counts": dict(sorted(core_counts.items())),
                "status": "auto-screened; requires title/abstract adjudication before final counts",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
