#!/usr/bin/env python3
"""Build a reproducible public-source scoping map for Clinical Detection and Intervention.

The pipeline queries OpenAlex, Europe PMC, Crossref and arXiv with the same
date window for every final-taxonomy task family.  It exports raw retrievals,
DOI-first/title-second deduplicated records, title/abstract-screened candidates,
cross-task overlap and public-full-text discovery status.

Important: the screened layer is a reproducible *candidate evidence map*, not
a dual-reviewer systematic-review inclusion set.  Every chart generated from
these outputs must retain that qualification.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


START_DATE = "2000-01-01"
DEFAULT_END_DATE = "2026-08-15"
USER_AGENT = "awesome-embodied-diagnostics/1.0 (public scoping map; contact via GitHub repository)"


@dataclass(frozen=True)
class Task:
    mechanism: str
    code: str
    en: str
    cn: str
    # Short, auditable concept pairs. Each retrieved title/abstract must contain
    # every non-stopword query term before it can enter the candidate layer.
    queries: tuple[str, ...]
    concept_patterns: tuple[str, ...]
    action_patterns: tuple[str, ...]
    exclude_patterns: tuple[str, ...] = ()


COMMON_ACTION = (
    r"robot", r"motorized", r"motorised", r"actuat(?:e|ed|ion|or)",
    r"mechatronic", r"steerable", r"magnetically controlled", r"magnetic actuat",
    r"active capsule", r"physical manipulat", r"probe position", r"sensor position",
    r"scan path", r"scanning trajectory", r"active locomotion", r"visual servo",
    r"force control", r"closed[- ]loop control", r"feedback control",
    r"autonom(?:ous|ously).{0,24}(scan|acqui|position|navigat|sample|palpat|collect)",
    r"automat(?:ed|ic).{0,24}(scan|acqui|position|sample|collect|palpat|venipunct|phlebot)",
)


TASKS = (
    Task("1.1", "A1", "External contact scanning and sensor placement", "体表接触式扫描与传感器布置",
         ("robotic ultrasound", "autonomous ultrasound", "robot-assisted ultrasound", "robotic auscultation", "automated auscultation"),
         (r"(?=.*(?:ultrasound|sonograph|echograph))(?=.*(?:scan|acqui|exam|imag|diagnos|probe|view))|auscultat|stethoscop|contact optical coherence"), COMMON_ACTION,
         (r"biopsy|needle insertion|ablation|therapy|therapeutic|surgery training|undergoing robot|robotic versus laparoscop|after robotic surgery",)),
    Task("1.1", "A2", "External non-contact alignment and scanning", "体表非接触式对准与扫描",
         ("robotic fundus imaging", "automated fundus imaging", "robotic slit lamp", "robotic skin imaging", "robotic wound imaging", "robotic hyperspectral imaging", "robotic Raman spectroscopy"),
         (r"(?=.*(?:fundus|ophthalm|retina|slit lamp|skin|derma|wound|exposed tissue|hyperspectral|multispectral|raman|diffuse reflectance|optical coherence|thermograph))(?=.*(?:align|position|scan|acqui|imag|map|inspect|exam|diagnos))"), COMMON_ACTION,
         (r"biopsy|resection|ablation|laser therapy|photodynamic therapy",)),
    Task("1.1", "A3", "Tethered endoluminal or intracavitary observation and navigation", "有缆腔内或腔道内观察与导航",
         ("robotic endoscopy", "autonomous endoscopy", "robotic colonoscopy", "robotic bronchoscopy", "robotic otoscopy", "robotic laryngoscopy", "robotic cystoscopy"),
         (r"(?=.*(?:endoscop|colonoscop|gastroscop|bronchoscop|otoscop|laryngoscop|cystoscop|hysteroscop))(?=.*(?:observ|navigat|inspect|exam|imag|diagnos|detect|screen|visual))"), COMMON_ACTION,
         (r"biopsy|sampling|specimen|resection|ablation|surgery|therapeutic",)),
    Task("1.1", "A4", "Untethered internal observation and navigation", "无缆体内观察与导航",
         ("magnetically controlled capsule endoscopy", "active capsule endoscopy", "robotic capsule endoscopy", "wireless capsule robot", "diagnostic microrobot imaging"),
         (r"(?=.*(?:capsule endoscop|wireless capsule|untethered|microrobot))(?=.*(?:imag|diagnos|observ|inspect|navigat|locomot|visual))"), COMMON_ACTION,
         (r"biopsy|sampling|sample collection|drug delivery|therapy|therapeutic",)),
    Task("1.1", "A5", "Catheter-based, intravascular, intraductal or percutaneous in-vivo sensing", "导管、血管内、管道内或经皮探头在体感知",
         ("robotic intravascular ultrasound", "autonomous intravascular imaging", "robotic OCT catheter", "steerable imaging catheter", "robotic optical biopsy probe"),
         (r"(?=.*(?:intravascular|intraductal|catheter|percutaneous probe|needle[- ]based optical|endovascular))(?=.*(?:sens|imag|scan|acqui|spectroscop|ultrasound|optical coherence|OCT))"),
         COMMON_ACTION,
         (r"biopsy|sampling|ablation|stent|therapy|therapeutic|drug delivery",)),
    Task("1.2", "R1", "Quasi-static contact, palpation and indentation", "准静态接触、触诊与压入",
         ("robotic palpation", "autonomous palpation", "robotic indentation", "robotic tactile tumor detection", "robotic stiffness mapping"),
         (r"palpat|indentation|tactile.*(tumou?r|mass|lesion|tissue)|mechanical imaging|stiffness map"), COMMON_ACTION,
         (r"training|simulation only|resection|surgery assistance",)),
    Task("1.2", "R2", "Dynamic mechanical or acoustic excitation", "动态机械或声学激励",
         ("robotic elastography", "automated elastography", "robotic shear wave elastography", "robotic vibration imaging", "robotic percussion"),
         (r"elastograph|shear wave|acoustic radiation force|vibro|vibration|percussion|dynamic stiffness|mechanical wave"), COMMON_ACTION,
         (r"therapy|therapeutic|ablation|rehabilitation training",)),
    Task("1.2", "R3", "Imposed motion, loading and functional provocation", "施加运动、载荷与功能激发",
         ("robotic joint laxity", "robotic arthrometer", "robotic spasticity assessment", "robotic muscle tone assessment", "robotic passive stretch assessment"),
         (r"joint laxity|arthrometer|provocation test|passive stretch|passive movement|spastic|muscle tone|range of motion|functional provocation"), COMMON_ACTION,
         (r"rehabilitation training|therapy outcome only|surgery",)),
    Task("1.2", "R4", "Electrical, magnetic or neurophysiological stimulation-response mapping", "电、磁或神经生理刺激—响应映射",
         ("robotic TMS", "automated TMS mapping", "closed-loop TMS mapping", "robotic motor mapping", "automated nerve stimulation mapping"),
         (r"transcranial magnetic|\bTMS\b|nerve stimulation|neurostimulation|motor evoked|\bMEP\b|stimulation.response|reflex mapping"),
         COMMON_ACTION,
         (r"treatment|therapy|therapeutic|depression treatment|rehabilitation training",)),
    Task("1.2", "R5", "Physiological challenge and controlled modulation", "生理挑战与受控调制",
         ("automated physiological challenge test", "robotic vascular occlusion test", "adaptive respiratory challenge", "automated autonomic testing"),
         (r"physiological challenge|vascular occlusion|cuff occlusion|respiratory challenge|autonomic provocation|orthostatic challenge|thermal challenge"),
         COMMON_ACTION,
         (r"training|therapy|therapeutic",)),
    Task("1.3", "S1", "Percutaneous needle-based tissue sampling", "经皮针式组织采样",
         ("robotic percutaneous biopsy", "robot-assisted needle biopsy", "robotic fine needle aspiration", "robotic core needle biopsy"),
         (r"(?=.*(?:biopsy|fine needle aspiration|tissue acquisition|tissue sampling))(?=.*(?:percutaneous|needle|core biopsy|aspiration))"), COMMON_ACTION,
         (r"biopsy guidance only|needle placement only|training|ablation|brachytherapy|injection",)),
    Task("1.3", "S2", "Vascular blood sampling", "血管血液采样",
         ("robotic venipuncture", "automated venipuncture", "robotic phlebotomy", "automated blood draw", "robotic blood collection"),
         (r"venipuncture|phlebotom|blood draw|blood collection|blood sampling"), COMMON_ACTION,
         (r"intravenous injection|infusion|catheterization only|training",)),
    Task("1.3", "S3", "Tethered endoluminal or intracavitary tissue/fluid sampling", "有缆腔内或腔道内组织/体液采样",
         ("robotic bronchoscopy biopsy", "robotic endoscopic biopsy", "robot-assisted bronchoscopy sampling", "robotic endoluminal biopsy"),
         (r"bronchoscop|endoscop|colonoscop|gastroscop|cystoscop|hysteroscop"),
         COMMON_ACTION,
         (r"navigation only|observation only|resection|ablation|therapy",)),
    Task("1.3", "S4", "Untethered or capsule-based internal sampling", "无缆或胶囊式体内采样",
         ("capsule robot biopsy", "capsule microbiome sampling", "smart capsule sampling", "magnetic capsule sampling"),
         (r"capsule|untethered|microrobot"),
         COMMON_ACTION,
         (r"drug delivery|therapy|therapeutic|imaging only",)),
    Task("1.3", "S5", "Surface or mucosal specimen collection", "体表或黏膜标本采集",
         ("robotic nasopharyngeal swab", "robotic oropharyngeal swab", "robotic swab sampling", "automated specimen collection robot"),
         (r"swab|nasopharyngeal|oropharyngeal|mucosal|cervical brush|wound specimen|surface specimen"),
         COMMON_ACTION,
         (r"disinfection|cleaning|training",)),
    Task("1.3", "S6", "Other adaptive body-fluid or excretion collection", "其他自适应体液或排泄物采集",
         ("robotic saliva collection", "automated urine specimen collection", "robotic body fluid sampling", "adaptive sweat sampling"),
         (r"saliva|urine|sweat|drainage fluid|body fluid|excretion"),
         COMMON_ACTION,
         (r"wearable sensor only|passive monitoring|therapy|therapeutic",)),
)


REVIEW_RX = re.compile(r"\b(review|systematic review|meta-analysis|overview|state[- ]of[- ]the[- ]art|survey|perspective|editorial|commentary|protocol|challenges and perspectives)\b", re.I)
QUERY_STOPWORDS = {"and", "or", "the", "of", "for", "in", "with", "test"}


def norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def norm_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def norm_doi(value: str) -> str:
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", (value or "").strip().casefold())


def work_key(row: dict) -> str:
    doi = norm_doi(row.get("doi", ""))
    return f"doi:{doi}" if doi else f"title:{norm_title(row.get('title', ''))}"


def query_terms(query: str) -> list[str]:
    """Return the auditable AND terms used for source and local screening."""
    query = query.replace("-", " ")
    return [
        token.casefold() for token in re.findall(r"[A-Za-z0-9]+", query)
        if len(token) >= 3 and token.casefold() not in QUERY_STOPWORDS
    ]


def query_terms_present(query: str, text_value: str) -> bool:
    text_cf = text_value.casefold()
    return all(term in text_cf for term in query_terms(query))


def query_terms_near(query: str, text_value: str, max_span: int = 96) -> bool:
    """Require all auditable terms to occur within a compact text window."""
    text_cf = text_value.casefold().replace("-", " ")
    terms = query_terms(query)
    positions = []
    for term in terms:
        locs = [m.start() for m in re.finditer(re.escape(term), text_cf)]
        if not locs:
            return False
        positions.append(locs)
    for anchor in positions[0]:
        chosen = [anchor]
        for locs in positions[1:]:
            chosen.append(min(locs, key=lambda loc: abs(loc - anchor)))
        if max(chosen) - min(chosen) <= max_span:
            return True
    return False


def request_json(url: str, cache: Path, retries: int = 4) -> dict:
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.load(response)
            cache.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return data
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"request failed after {retries} attempts: {url}: {last}")


def inverted_abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions = []
    for word, locs in index.items():
        for loc in locs:
            positions.append((loc, word))
    return " ".join(word for _, word in sorted(positions))


def openalex_records(query: str, task: Task, cache_dir: Path, end_date: str) -> tuple[list[dict], int]:
    records = []
    cursor = "*"
    total = 0
    page = 0
    while cursor:
        # OpenAlex full-text search is relevance-ranked and intentionally broad.
        # We restrict discovery to title search, then enforce all query terms
        # locally against title/abstract before candidate screening.
        params = {
            "filter": f"title.search:{query},from_publication_date:{START_DATE},to_publication_date:{end_date}",
            "per-page": 200,
            "cursor": cursor,
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        data = request_json(url, cache_dir / f"openalex_{task.code}_{hashlib.sha1(query.encode()).hexdigest()[:10]}_{page}.json")
        if page == 0:
            total = int((data.get("meta") or {}).get("count") or 0)
        for item in data.get("results") or []:
            loc = item.get("best_oa_location") or {}
            records.append({
                "source": "OpenAlex", "source_id": item.get("id", ""),
                "title": norm_text(item.get("display_name", "")),
                "abstract": inverted_abstract(item.get("abstract_inverted_index")),
                "year": item.get("publication_year") or "",
                "doi": norm_doi(item.get("doi", "")),
                "record_url": item.get("id", ""),
                "public_full_text_url": loc.get("pdf_url") or loc.get("landing_page_url") or "",
                "public_full_text_identified": int(bool(loc) and ((item.get("open_access") or {}).get("is_oa") is True)),
                "publication_type": item.get("type", ""),
            })
        cursor = (data.get("meta") or {}).get("next_cursor")
        page += 1
        if not (data.get("results") or []) or page >= 15:
            break
        time.sleep(0.08)
    return records, total


def epmc_records(query: str, task: Task, cache_dir: Path, end_date: str) -> tuple[list[dict], int]:
    records = []
    cursor = "*"
    page = 0
    total = 0
    term_clause = " AND ".join(f'TITLE_ABS:"{term}"' for term in query_terms(query))
    epmc_query = f'({term_clause}) AND FIRST_PDATE:[{START_DATE} TO {end_date}]'
    while cursor:
        params = {"query": epmc_query, "format": "json", "pageSize": 1000, "cursorMark": cursor, "resultType": "core"}
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params)
        data = request_json(url, cache_dir / f"epmc_{task.code}_{hashlib.sha1(query.encode()).hexdigest()[:10]}_{page}.json")
        if page == 0:
            total = int(data.get("hitCount") or 0)
        result_list = (data.get("resultList") or {}).get("result") or []
        for item in result_list:
            pmcid = item.get("pmcid", "")
            full = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else ""
            records.append({
                "source": "Europe PMC", "source_id": item.get("id", ""),
                "title": norm_text(item.get("title", "")),
                "abstract": norm_text(item.get("abstractText", "")),
                "year": item.get("pubYear") or "",
                "doi": norm_doi(item.get("doi", "")),
                "record_url": f"https://europepmc.org/article/{item.get('source','MED')}/{item.get('id','')}",
                "public_full_text_url": full,
                "public_full_text_identified": int(bool(pmcid) or str(item.get("isOpenAccess", "")).upper() == "Y"),
                "publication_type": "; ".join(item.get("pubTypeList", {}).get("pubType", []) if isinstance(item.get("pubTypeList"), dict) else []),
            })
        next_cursor = data.get("nextCursorMark")
        if not result_list or not next_cursor or next_cursor == cursor or page >= 10:
            break
        cursor = next_cursor
        page += 1
        time.sleep(0.08)
    return records, total


def crossref_records(query: str, task: Task, cache_dir: Path, end_date: str) -> tuple[list[dict], int]:
    params = {
        "query.bibliographic": query,
        "filter": f"from-pub-date:{START_DATE},until-pub-date:{end_date}",
        "rows": 1000,
        "select": "DOI,title,abstract,published,URL,type,link",
    }
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = request_json(url, cache_dir / f"crossref_{task.code}_{hashlib.sha1(query.encode()).hexdigest()[:10]}.json")
    message = data.get("message") or {}
    records = []
    for item in message.get("items") or []:
        dates = ((item.get("published") or {}).get("date-parts") or [[""]])[0]
        links = item.get("link") or []
        public = next((link.get("URL", "") for link in links if "pdf" in (link.get("content-type", "")).lower()), "")
        title = (item.get("title") or [""])[0]
        abstract = re.sub(r"<[^>]+>", " ", item.get("abstract", ""))
        records.append({
            "source": "Crossref", "source_id": item.get("DOI", ""),
            "title": norm_text(title), "abstract": norm_text(abstract),
            "year": dates[0] if dates else "", "doi": norm_doi(item.get("DOI", "")),
            "record_url": item.get("URL", ""), "public_full_text_url": public,
            "public_full_text_identified": 0,
            "publication_type": item.get("type", ""),
        })
    return records, int(message.get("total-results") or 0)


def arxiv_records(query: str, task: Task, cache_dir: Path) -> tuple[list[dict], int]:
    # arXiv's Atom API is queried with a compact AND expression.  It is a
    # supplement for robotics/engineering records and is intentionally capped.
    tokens = query_terms(query)
    search = " AND ".join(f'all:"{t}"' for t in tokens)
    params = {"search_query": search, "start": 0, "max_results": 300, "sortBy": "relevance", "sortOrder": "descending"}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    cache = cache_dir / f"arxiv_{task.code}_{hashlib.sha1(query.encode()).hexdigest()[:10]}.xml"
    if cache.exists():
        xml = cache.read_bytes()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                xml = response.read()
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(xml)
        except Exception:
            return [], 0
    root = ET.fromstring(xml)
    ns = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/"}
    total_node = root.find("o:totalResults", ns)
    total = int(total_node.text) if total_node is not None and total_node.text else 0
    records = []
    for entry in root.findall("a:entry", ns):
        entry_id = entry.findtext("a:id", default="", namespaces=ns)
        year = entry.findtext("a:published", default="", namespaces=ns)[:4]
        doi = entry.findtext("a:doi", default="", namespaces={**ns, "a": "http://www.w3.org/2005/Atom"})
        records.append({
            "source": "arXiv", "source_id": entry_id,
            "title": norm_text(entry.findtext("a:title", default="", namespaces=ns)),
            "abstract": norm_text(entry.findtext("a:summary", default="", namespaces=ns)),
            "year": year, "doi": norm_doi(doi), "record_url": entry_id,
            "public_full_text_url": entry_id.replace("/abs/", "/pdf/"),
            "public_full_text_identified": 1, "publication_type": "preprint",
        })
    return records, total


def matches_any(patterns: Iterable[str], text: str) -> bool:
    if isinstance(patterns, str):
        patterns = (patterns,)
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def screen(task: Task, row: dict) -> tuple[bool, str]:
    text = f"{row.get('title','')} {row.get('abstract','')}"
    title = row.get("title", "")
    if not title:
        return False, "missing title"
    if REVIEW_RX.search(title) or "review" in (row.get("publication_type") or "").casefold():
        return False, "review/editorial/protocol"
    matched_queries = [q for q in str(row.get("queries", row.get("query", ""))).split(" || ") if q]
    if matched_queries and not any(query_terms_near(query, title) for query in matched_queries):
        return False, "auditable query terms not co-located within a 96-character title window"
    if not matches_any(task.concept_patterns, text):
        return False, "task-defining concept absent from title/abstract"
    if not matches_any(task.action_patterns, text):
        return False, "controllable physical action or carrier absent from title/abstract"
    if task.exclude_patterns and matches_any(task.exclude_patterns, title):
        return False, "title indicates neighbouring or excluded task"
    return True, "title/abstract supports task concept plus controllable physical action; full-text loop verification pending"


def merge_group(rows: list[dict]) -> dict:
    first = max(rows, key=lambda r: (len(r.get("abstract", "")), bool(r.get("doi"))))
    merged = dict(first)
    merged["sources"] = "; ".join(sorted({r["source"] for r in rows}))
    merged["source_ids"] = "; ".join(sorted({r["source_id"] for r in rows if r.get("source_id")}))
    merged["public_full_text_identified"] = int(any(int(r.get("public_full_text_identified") or 0) for r in rows))
    merged["public_full_text_url"] = next((r.get("public_full_text_url", "") for r in rows if r.get("public_full_text_url")), "")
    merged["record_url"] = next((r.get("record_url", "") for r in rows if r.get("record_url")), "")
    merged["queries"] = " || ".join(sorted({r.get("query", "") for r in rows if r.get("query")}))
    return merged


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--end-date", default=DEFAULT_END_DATE)
    parser.add_argument("--sources", default="openalex,epmc,arxiv")
    parser.add_argument("--quiet", action="store_true", help="suppress per-query progress JSON")
    args = parser.parse_args()
    enabled = {s.strip() for s in args.sources.split(",") if s.strip()}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    retrieval_rows = []
    query_log = []
    for task in TASKS:
        for query in task.queries:
            for source in ("openalex", "epmc", "crossref", "arxiv"):
                if source not in enabled:
                    continue
                start = time.time()
                error = ""
                try:
                    if source == "openalex":
                        rows, reported = openalex_records(query, task, args.cache_dir, args.end_date)
                    elif source == "epmc":
                        rows, reported = epmc_records(query, task, args.cache_dir, args.end_date)
                    elif source == "crossref":
                        rows, reported = crossref_records(query, task, args.cache_dir, args.end_date)
                    else:
                        rows, reported = arxiv_records(query, task, args.cache_dir)
                except Exception as exc:
                    rows, reported, error = [], 0, str(exc)
                for row in rows:
                    row.update({"mechanism_code": task.mechanism, "task_code": task.code, "query": query})
                    retrieval_rows.append(row)
                query_log.append({
                    "task_code": task.code, "mechanism_code": task.mechanism, "source": source,
                    "query": query, "start_date": START_DATE, "end_date": args.end_date,
                    "reported_hits": reported, "records_retrieved": len(rows),
                    "elapsed_seconds": round(time.time() - start, 2), "error": error,
                })
                if not args.quiet:
                    print(json.dumps(query_log[-1], ensure_ascii=True), flush=True)

    write_csv(args.output_dir / "retrieval_records.csv", retrieval_rows)
    write_csv(args.output_dir / "query_log.csv", query_log)

    # Deduplicate within each task first; the same work can legitimately appear
    # in multiple tasks and mechanisms and is retained for the overlap audit.
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in retrieval_rows:
        grouped[(row["task_code"], work_key(row))].append(row)
    dedup = []
    for (task_code, key), rows in grouped.items():
        merged = merge_group(rows)
        merged["work_key"] = key
        merged["task_code"] = task_code
        merged["mechanism_code"] = next(t.mechanism for t in TASKS if t.code == task_code)
        dedup.append(merged)

    screened = []
    excluded = []
    task_by_code = {t.code: t for t in TASKS}
    for row in dedup:
        task = task_by_code[row["task_code"]]
        include, reason = screen(task, row)
        out = dict(row)
        out["task_en"] = task.en
        out["task_cn"] = task.cn
        out["screening_decision"] = "candidate" if include else "exclude"
        out["screening_reason"] = reason
        out["screening_level"] = "deterministic title/abstract screen; full-text eligibility and loop verification pending"
        (screened if include else excluded).append(out)

    write_csv(args.output_dir / "screened_candidates.csv", screened)
    write_csv(args.output_dir / "excluded_records.csv", excluded)

    # Task counts use task-study pairs. Mechanism and umbrella counts use unique
    # works and retain overlap explicitly instead of forcing paper-level classes.
    task_counts = []
    for task in TASKS:
        rows = [r for r in screened if r["task_code"] == task.code]
        task_counts.append({
            "mechanism_code": task.mechanism, "task_code": task.code,
            "task_en": task.en, "task_cn": task.cn,
            "public_visible_screened_candidates": len(rows),
            "public_available_location_identified": sum(int(r["public_full_text_identified"]) for r in rows),
            "public_available_share": round(sum(int(r["public_full_text_identified"]) for r in rows) / len(rows), 4) if rows else "",
            "since_2021": sum(str(r.get("year", "")).isdigit() and int(r["year"]) >= 2021 for r in rows),
            "counting_unit": "one task-study pair after DOI-first/title-second deduplication within task",
        })

    mechanisms = []
    for code in ("1.1", "1.2", "1.3"):
        rows = [r for r in screened if r["mechanism_code"] == code]
        works = {r["work_key"]: r for r in rows}
        mechanisms.append({
            "mechanism_code": code,
            "public_visible_unique_screened_works": len(works),
            "public_available_unique_works": len({k for k, r in works.items() if int(r["public_full_text_identified"])}),
            "task_study_pairs": len(rows),
            "since_2021_unique_works": len({k for k, r in works.items() if str(r.get("year", "")).isdigit() and int(r["year"]) >= 2021}),
            "counting_unit": "unique work within mechanism; task-study pairs reported separately",
        })

    work_tasks: dict[str, set[str]] = defaultdict(set)
    work_mechs: dict[str, set[str]] = defaultdict(set)
    representative: dict[str, dict] = {}
    for row in screened:
        work_tasks[row["work_key"]].add(row["task_code"])
        work_mechs[row["work_key"]].add(row["mechanism_code"])
        representative.setdefault(row["work_key"], row)
    overlap = []
    for key in sorted(work_tasks):
        if len(work_tasks[key]) > 1 or len(work_mechs[key]) > 1:
            r = representative[key]
            overlap.append({
                "work_key": key, "title": r.get("title", ""), "year": r.get("year", ""), "doi": r.get("doi", ""),
                "mechanism_codes": ";".join(sorted(work_mechs[key])),
                "task_codes": ";".join(sorted(work_tasks[key])),
                "requires_manual_boundary_adjudication": "yes",
            })

    unique_works = set(work_tasks)
    summary = [{
        "domain": "Clinical Detection and Intervention", "snapshot_end_date": args.end_date,
        "public_visible_unique_screened_works": len(unique_works),
        "public_available_unique_works": len({k for k, r in representative.items() if int(r["public_full_text_identified"])}),
        "task_study_pairs": len(screened),
        "cross_task_or_mechanism_overlap_works": len(overlap),
        "retrieval_records_before_deduplication": len(retrieval_rows),
        "deduplicated_task_records_screened": len(dedup),
        "excluded_task_records": len(excluded),
        "scope_note": "public-source deterministic title/abstract-screened candidate map; not dual-reviewer full-text inclusion counts",
    }]
    write_csv(args.output_dir / "task_counts.csv", task_counts)
    write_csv(args.output_dir / "mechanism_counts.csv", mechanisms)
    write_csv(args.output_dir / "overlap_audit.csv", overlap)
    write_csv(args.output_dir / "domain_summary.csv", summary)

    qc = {
        "schema_version": "clinical-detection-intervention-public-statistics-v2",
        "date_window": [START_DATE, args.end_date],
        "sources": sorted(enabled),
        "tasks": len(TASKS),
        "query_runs": len(query_log),
        "query_errors": sum(bool(r["error"]) for r in query_log),
        "retrieval_records": len(retrieval_rows),
        "deduplicated_task_records": len(dedup),
        "screened_task_study_pairs": len(screened),
        "excluded_task_records": len(excluded),
        "unique_screened_works": len(unique_works),
        "overlap_works": len(overlap),
        "checks": {
            "task_count_sum_matches_screened_pairs": sum(r["public_visible_screened_candidates"] for r in task_counts) == len(screened),
            "public_available_not_above_visible": all(r["public_available_location_identified"] <= r["public_visible_screened_candidates"] for r in task_counts),
            "all_tasks_present": len(task_counts) == 16,
        },
        "interpretation_warning": "Candidate evidence map only. Full-text eligibility and feedback-loop verification require manual review before journal-grade inclusion counts.",
    }
    (args.output_dir / "qc.json").write_text(json.dumps(qc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary[0], "qc": qc["checks"]}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
