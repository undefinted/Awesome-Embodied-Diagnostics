"""Run a frozen, high-recall public-source search for review screening.

The output is a candidate pool. Automated signals never constitute inclusion.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import feedparser
import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
QUERY_FILE = ROOT / "data" / "discovery_queries.yaml"
OUT_ROOT = ROOT / "data" / "review" / "search_runs"
USER_AGENT = "Awesome-Embodied-Diagnostics/1.0 (evidence-map; https://github.com/undefinted/Awesome-Embodied-Diagnostics)"

DIRECTION = {
    "robotic-ultrasound": "active_observational_sensing",
    "embodied-endoscopy": "active_observational_sensing",
    "capsule-and-luminal-robots": "active_observational_sensing",
    "ophthalmic-examination": "active_observational_sensing",
    "dental-examination": "active_observational_sensing",
    "tactile-examination": "response_based_interactive_diagnosis",
    "diagnostic-sampling": "sample_based_interactive_diagnosis",
    "diagnostic-laboratory-loops": "laboratory_diagnostics",
    "active-diagnostic-agents": "cross_cutting_agents",
    "medical-vla": "technical_precedents",
    "adaptive-clinical-measurement": "cross_cutting_agents",
    "multimodal-physical-examination": "cross_cutting_agents",
    "robotic-oct-and-ophthalmic-acquisition": "active_observational_sensing",
    "stimulation-response-mapping": "response_based_interactive_diagnosis",
    "robotic-functional-examination": "response_based_interactive_diagnosis",
    "robotic-swabbing-and-blood-collection": "sample_based_interactive_diagnosis",
    "adaptive-microfluidic-diagnostics": "laboratory_diagnostics",
    "autonomous-assay-development": "laboratory_diagnostics",
    "wearable-triggered-testing": "everyday_monitoring",
    "ambient-adaptive-monitoring": "everyday_monitoring",
    "capsule-quality-feedback": "active_observational_sensing",
    "focused-tms-mapping": "response_based_interactive_diagnosis",
    "focused-robotic-blood-and-swab": "sample_based_interactive_diagnosis",
    "focused-robotic-bronchoscopy": "sample_based_interactive_diagnosis",
    "focused-feedback-microfluidics": "laboratory_diagnostics",
    "focused-robotic-assessment-devices": "response_based_interactive_diagnosis",
    "wearable-alert-confirmatory-testing": "everyday_monitoring",
    "ferrobotic-molecular-testing": "laboratory_diagnostics",
}
EXPLICIT = (
    "robotic ultrasound", "autonomous ultrasound", "ultrasound robot",
    "robotic palpation", "robotic auscultation", "robotic phlebotomy",
    "robotic biopsy", "autonomous biopsy", "robotic endoscopy",
    "autonomous endoscopy", "robotic optical coherence", "capsule robot",
    "active sensing", "adaptive examination", "closed-loop diagnosis",
)
DIAGNOSTIC = ("diagnos", "screen", "imaging", "examin", "sampling", "biopsy", "palpat", "ultrasound", "endoscop", "specimen")
ACTION = ("robot", "autonomous", "adaptive", "active sensing", "probe", "navigation", "contact force", "closed-loop", "closed loop")


@dataclass
class SearchResult:
    records: list[dict]
    total_hits: int | None


def retrieval_target(total_hits: int, limit: int) -> int:
    return total_hits if limit <= 0 else min(total_hits, limit)


def is_truncated(total_hits: int | None, retrieved: int, limit: int) -> bool:
    return total_hits is not None and limit > 0 and retrieved < total_hits


LOG_FIELDS = [
    "query_id", "source", "status", "retrieved", "total_hits",
    "retrieval_complete", "truncated_at_limit", "error", "started_at", "completed_at",
]


def write_checkpoint(run_dir: Path, log: list[dict], records: list[dict], last_pair: str) -> None:
    with (run_dir / "query_log.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(log)
    status = {
        "completed_source_query_pairs": sum(row.get("status") == "ok" for row in log),
        "failed_source_query_pairs": sum(row.get("status") != "ok" for row in log),
        "raw_records_checkpointed": len(records),
        "last_pair": last_pair,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "checkpoint_status.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_doi(value: str) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I).lower().rstrip(".,; ")


def valid_doi(value: str) -> bool:
    return bool(re.match(r"^10\.\d{4,9}/\S+$", value, flags=re.I))


def title_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def fielded_boolean_query(expression: str, source: str) -> str:
    """Translate the registered Boolean concepts to explicit platform fields."""
    tokens = re.findall(r'"[^"]+"|\(|\)|\bAND\b|\bOR\b|[^\s()]+', expression)
    translated = []
    for token in tokens:
        if token in {"(", ")", "AND", "OR"}:
            translated.append(token)
        elif source == "pubmed":
            translated.append(f"{token}[Title/Abstract]")
        elif source == "europepmc":
            translated.append(f"TITLE_ABS:{token}")
        else:
            raise ValueError(f"Unsupported fielded-query source: {source}")
    return " ".join(translated)


def signal(title: str, abstract: str) -> tuple[str, str]:
    text = f"{title} {abstract}".lower()
    title_l = title.lower()
    if any(term in title_l for term in EXPLICIT):
        return "high", "explicit embodied diagnostic phrase in title"
    if any(term in text for term in DIAGNOSTIC) and any(term in text for term in ACTION):
        return "possible", "diagnostic and action terms co-occur"
    return "low", "no conservative automated scope signal"


def get(url: str, *, params: dict, timeout: int = 60) -> requests.Response:
    headers = {"User-Agent": USER_AGENT}
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            if response.status_code == 429:
                wait = min(int(response.headers.get("Retry-After", "0") or 0), 30) or 2 ** attempt
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"request failed after retries: {last_error or 'HTTP 429'}")


def record(source: str, query: dict, **values: object) -> dict:
    title, abstract = clean(values.get("title")), clean(values.get("abstract"))
    level, reason = signal(title, abstract)
    return {
        "source": source,
        "query_id": query["id"],
        "direction": DIRECTION.get(query["id"], "unclassified"),
        "title": title,
        "abstract": abstract,
        "year": clean(values.get("year")),
        "publication_date": clean(values.get("publication_date")),
        "authors": clean(values.get("authors")),
        "venue": clean(values.get("venue")),
        "doi": normalize_doi(clean(values.get("doi"))),
        "pmid": clean(values.get("pmid")),
        "pmcid": clean(values.get("pmcid")),
        "arxiv_id": clean(values.get("arxiv_id")),
        "url": clean(values.get("url")),
        "automated_signal": level,
        "automated_reason": reason,
        "screening_status": "awaiting_human_title_abstract_screen",
    }


def pubmed(query: dict, since: str, until: str, limit: int) -> SearchResult:
    concepts = fielded_boolean_query(query["scholarly"], "pubmed")
    term = f'({concepts}) AND ("{since}"[Date - Publication] : "{until}"[Date - Publication])'
    count_response = get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params={"db": "pubmed", "term": term, "retmode": "json", "retmax": 0, "usehistory": "y"},
        timeout=60,
    )
    search_data = count_response.json().get("esearchresult", {})
    total = int(search_data.get("count", 0))
    query_key = search_data.get("querykey", "")
    webenv = search_data.get("webenv", "")
    if total and (not query_key or not webenv):
        raise RuntimeError("PubMed did not return a history-server query key")
    target = retrieval_target(total, limit)
    out: list[dict] = []
    for start in range(0, target, 200):
        size = min(200, target - start)
        fetched = get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "query_key": query_key, "WebEnv": webenv, "retstart": start, "retmax": size, "retmode": "xml"},
            timeout=90,
        )
        out.extend(parse_pubmed_xml(fetched.content, query))
        time.sleep(0.35)
    return SearchResult(out, total)


def parse_pubmed_xml(content: bytes, query: dict) -> list[dict]:
    """Parse identifiers only from the current article, never its references."""
    out = []
    root = ET.fromstring(content)
    for article in root.findall(".//PubmedArticle"):
        text = lambda path: clean("".join(article.findtext(path, default="")))
        title = clean("".join(article.find(".//ArticleTitle").itertext())) if article.find(".//ArticleTitle") is not None else ""
        abstract = " ".join(clean("".join(node.itertext())) for node in article.findall(".//Abstract/AbstractText"))
        ids_by_type = {
            node.attrib.get("IdType", ""): clean(node.text)
            for node in article.findall("./PubmedData/ArticleIdList/ArticleId")
        }
        current_pmid = text("./MedlineCitation/PMID") or ids_by_type.get("pubmed", "")
        year = text(".//PubDate/Year") or text(".//ArticleDate/Year") or text(".//PubDate/MedlineDate")[:4]
        authors = "; ".join(clean(f"{a.findtext('ForeName', '')} {a.findtext('LastName', '')}") for a in article.findall(".//Author"))
        out.append(record("PubMed", query, title=title, abstract=abstract, year=year, authors=authors,
                          venue=text(".//Journal/Title"), doi=ids_by_type.get("doi", ""), pmid=current_pmid, pmcid=ids_by_type.get("pmc", ""),
                          url=f"https://pubmed.ncbi.nlm.nih.gov/{current_pmid}/"))
    for article in root.findall(".//PubmedBookArticle"):
        document = article.find("./BookDocument")
        if document is None:
            continue
        current_pmid = clean(document.findtext("PMID", ""))
        title_node = document.find("ArticleTitle")
        title = clean("".join(title_node.itertext())) if title_node is not None else ""
        abstract = " ".join(clean("".join(node.itertext())) for node in document.findall(".//Abstract/AbstractText"))
        ids_by_type = {
            node.attrib.get("IdType", ""): clean(node.text)
            for node in article.findall("./PubmedBookData/ArticleIdList/ArticleId")
        }
        year = clean(document.findtext("./Book/PubDate/Year", ""))
        venue = clean(document.findtext("./Book/BookTitle", ""))
        out.append(record("PubMed", query, title=title, abstract=abstract, year=year, venue=venue,
                          doi=ids_by_type.get("doi", ""), pmid=current_pmid,
                          url=f"https://pubmed.ncbi.nlm.nih.gov/{current_pmid}/"))
    return out


def europepmc(query: dict, since: str, until: str, limit: int) -> SearchResult:
    out: list[dict] = []
    cursor = "*"
    total: int | None = None
    while total is None or len(out) < retrieval_target(total, limit):
        page_size = 1000 if total is None else min(1000, retrieval_target(total, limit) - len(out))
        response = get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": f'({fielded_boolean_query(query["scholarly"], "europepmc")}) FIRST_PDATE:[{since} TO {until}]', "format": "json", "pageSize": page_size, "resultType": "core", "cursorMark": cursor},
            timeout=90,
        )
        payload = response.json()
        total = int(payload.get("hitCount", 0))
        items = payload.get("resultList", {}).get("result", [])
        if not items:
            break
        out.extend(record("Europe PMC", query, title=x.get("title"), abstract=x.get("abstractText"), year=x.get("pubYear"),
                          publication_date=x.get("firstPublicationDate"), authors=x.get("authorString"), venue=x.get("journalTitle"),
                          doi=x.get("doi"), pmid=x.get("pmid"), pmcid=x.get("pmcid"), url=(f"https://doi.org/{x['doi']}" if x.get("doi") else f"https://europepmc.org/article/{x.get('source','MED')}/{x.get('id','')}"))
                   for x in items)
        next_cursor = payload.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
    target = retrieval_target(total or 0, limit)
    return SearchResult(out[:target], total)


def invert_abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions = sorted((position, word) for word, values in index.items() for position in values)
    return " ".join(word for _, word in positions)


def openalex(query: dict, since: str, until: str, limit: int) -> SearchResult:
    params = {"search": query["scholarly"], "filter": f"from_publication_date:{since},to_publication_date:{until}", "per-page": 200, "cursor": "*"}
    mailto = os.getenv("OPENALEX_MAILTO") or os.getenv("CROSSREF_MAILTO")
    if mailto:
        params["mailto"] = mailto
    out: list[dict] = []
    total: int | None = None
    while total is None or len(out) < retrieval_target(total, limit):
        if total is not None:
            params["per-page"] = min(200, retrieval_target(total, limit) - len(out))
        response = get("https://api.openalex.org/works", params=params, timeout=90)
        payload = response.json()
        total = int(payload.get("meta", {}).get("count", 0))
        items = payload.get("results", [])
        if not items:
            break
        for x in items:
            authors = "; ".join(clean(a.get("author", {}).get("display_name")) for a in x.get("authorships", []))
            location = x.get("primary_location") or {}
            source = location.get("source") or {}
            out.append(record("OpenAlex", query, title=x.get("title"), abstract=invert_abstract(x.get("abstract_inverted_index")),
                              year=x.get("publication_year"), publication_date=x.get("publication_date"), authors=authors,
                              venue=source.get("display_name"), doi=x.get("doi"), url=x.get("doi") or location.get("landing_page_url") or x.get("id")))
        cursor = payload.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        params["cursor"] = cursor
    target = retrieval_target(total or 0, limit)
    return SearchResult(out[:target], total)


def arxiv(query: dict, since: str, until: str, limit: int) -> SearchResult:
    out: list[dict] = []
    start = 0
    total_all: int | None = None
    exhausted_date_range = False
    while not exhausted_date_range and (limit <= 0 or len(out) < limit):
        page_size = 200 if limit <= 0 else min(200, limit - len(out))
        response = get(
            "https://export.arxiv.org/api/query",
            params={"search_query": query["arxiv"], "start": start, "max_results": page_size, "sortBy": "submittedDate", "sortOrder": "descending"},
            timeout=90,
        )
        feed = feedparser.parse(response.text)
        if total_all is None:
            total_all = int(feed.feed.get("opensearch_totalresults", 0) or 0)
        if not feed.entries:
            break
        for x in feed.entries:
            published = clean(x.get("published"))
            if published[:10] < since:
                exhausted_date_range = True
                continue
            if published[:10] > until:
                continue
            arxiv_id = x.get("id", "").rstrip("/").split("/")[-1]
            authors = "; ".join(clean(a.get("name")) for a in x.get("authors", []))
            out.append(record("arXiv", query, title=x.get("title"), abstract=x.get("summary"), year=published[:4],
                              publication_date=published[:10], authors=authors, venue="arXiv", arxiv_id=arxiv_id, url=x.get("id")))
        start += len(feed.entries)
        if start >= (total_all or 0):
            break
        time.sleep(3)
    if exhausted_date_range or start >= (total_all or 0):
        total_in_range: int | None = len(out)
    elif limit > 0 and len(out) >= limit:
        total_in_range = total_all  # Conservative upper bound when paging stopped at the configured limit.
    else:
        total_in_range = None
    return SearchResult(out[:limit] if limit > 0 else out, total_in_range)


def identity(item: dict) -> str:
    if item["doi"] and valid_doi(item["doi"]):
        return "doi:" + item["doi"]
    if item["pmid"]:
        return "pmid:" + item["pmid"]
    if item.get("pmcid"):
        return "pmcid:" + item["pmcid"].lower()
    if item["arxiv_id"]:
        return "arxiv:" + item["arxiv_id"].split("v")[0]
    return "title:" + title_key(item["title"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", default="2000-01-01")
    parser.add_argument("--until", default=date.today().isoformat())
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--sources", default="pubmed,europepmc,openalex,arxiv")
    parser.add_argument("--query-id", action="append")
    parser.add_argument("--run-id", default=date.today().isoformat())
    parser.add_argument("--resume", action="store_true", help="Keep prior records and retry only failed source-query pairs.")
    parser.add_argument("--force", action="store_true", help="With --resume, replace the selected source-query pairs.")
    args = parser.parse_args()
    all_queries=(yaml.safe_load(QUERY_FILE.read_text(encoding="utf-8")) or {}).get("queries", [])
    queries = all_queries
    if args.query_id:
        queries = [q for q in queries if q["id"] in set(args.query_id)]
    functions = {"pubmed": pubmed, "europepmc": europepmc, "openalex": openalex, "arxiv": arxiv}
    requested = [x.strip().lower() for x in args.sources.split(",") if x.strip()]
    unknown = set(requested) - set(functions)
    if unknown:
        raise SystemExit("Unknown sources: " + ", ".join(sorted(unknown)))
    run_dir = OUT_ROOT / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_records_path = run_dir / "raw_retrieval_records.jsonl"
    if raw_records_path.exists() and not args.resume:
        raise SystemExit(f"Run already has a raw checkpoint; use --resume or a new run id: {args.run_id}")
    strategy_rows = []
    for query in queries:
        for source in requested:
            if source == "pubmed":
                query_text = f'({fielded_boolean_query(query["scholarly"], "pubmed")}) AND ("{args.since}"[Date - Publication] : "{args.until}"[Date - Publication])'
            elif source == "europepmc":
                query_text = f'({fielded_boolean_query(query["scholarly"], "europepmc")}) FIRST_PDATE:[{args.since} TO {args.until}]'
            elif source == "openalex":
                query_text = f'search={query["scholarly"]}; filter=from_publication_date:{args.since},to_publication_date:{args.until}'
            else:
                query_text = query["arxiv"]
            strategy_rows.append({
                "run_id": args.run_id,
                "query_id": query["id"],
                "focus": query["focus"],
                "source": source,
                "query_text": query_text,
                "since": args.since,
                "until": args.until,
                "configured_result_limit": args.max_results,
                "validation_status": "programmatic platform translation; information-specialist peer review pending",
                "query_registry_sha256": hashlib.sha256(QUERY_FILE.read_bytes()).hexdigest(),
            })
    strategy_path = run_dir / "search_strategies.csv"
    if args.resume and strategy_path.exists():
        with strategy_path.open(encoding="utf-8-sig", newline="") as handle:
            prior_strategies = list(csv.DictReader(handle))
        merged = {(row["query_id"], row["source"]): row for row in prior_strategies}
        merged.update({(row["query_id"], row["source"]): row for row in strategy_rows})
        strategy_rows = list(merged.values())
    with strategy_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(strategy_rows[0]) if strategy_rows else [])
        writer.writeheader()
        writer.writerows(strategy_rows)
    all_records, log = [], []
    completed: set[tuple[str, str]] = set()
    if args.resume and raw_records_path.exists():
        with raw_records_path.open(encoding="utf-8") as handle:
            all_records = [json.loads(line) for line in handle if line.strip()]
    elif args.resume and (run_dir / "candidates.csv").exists():
        with (run_dir / "candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
            all_records = list(csv.DictReader(handle))
    if args.resume and (run_dir / "query_log.csv").exists():
        with (run_dir / "query_log.csv").open(encoding="utf-8-sig", newline="") as handle:
            previous_log = list(csv.DictReader(handle))
        for row in previous_log:
            row.setdefault("total_hits", "")
            if not row.get("retrieval_complete"):
                row["retrieval_complete"] = str(
                    row.get("status") == "ok"
                    and bool(row.get("total_hits"))
                    and int(row.get("retrieved", 0) or 0) == int(row.get("total_hits", 0) or 0)
                )
            row.setdefault("truncated_at_limit", str(int(row.get("retrieved", 0) or 0) >= args.max_results))
        completed = {(row["query_id"], row["source"]) for row in previous_log if row["status"] == "ok"}
        log = previous_log
    if args.force:
        selected_pairs = {(q["id"], source) for q in queries for source in requested}
        all_records = [item for item in all_records if (item.get("query_id"), item.get("source", "").lower().replace(" ", "")) not in selected_pairs]
        log = [row for row in log if (row["query_id"], row["source"]) not in selected_pairs]
        completed -= selected_pairs
        with raw_records_path.open("w", encoding="utf-8") as handle:
            for item in all_records:
                handle.write(json.dumps(item, ensure_ascii=True) + "\n")
    for query in queries:
        for source in requested:
            if (query["id"], source) in completed:
                continue
            log = [row for row in log if (row["query_id"], row["source"]) != (query["id"], source)]
            started = datetime.now(timezone.utc)
            try:
                result = functions[source](query, args.since, args.until, args.max_results)
                records = result.records
                expected = retrieval_target(result.total_hits, args.max_results) if result.total_hits is not None else None
                complete = expected is None or len(records) == expected
                status = "ok" if complete else "incomplete"
                error = "" if complete else f"retrieved {len(records)} of {expected} expected records"
                all_records.extend(records)
            except Exception as exc:
                result = SearchResult([], None)
                records, status, error = [], "error", f"{type(exc).__name__}: {exc}"
            log.append({"query_id": query["id"], "source": source, "status": status, "retrieved": len(records),
                        "total_hits": result.total_hits if result.total_hits is not None else "",
                        "retrieval_complete": status == "ok",
                        "truncated_at_limit": is_truncated(result.total_hits, len(records), args.max_results),
                        "error": error, "started_at": started.isoformat(),
                        "completed_at": datetime.now(timezone.utc).isoformat()})
            if records:
                with raw_records_path.open("a", encoding="utf-8") as handle:
                    for item in records:
                        handle.write(json.dumps(item, ensure_ascii=True) + "\n")
            write_checkpoint(run_dir, log, all_records, f"{query['id']}:{source}")
            print(
                f"checkpoint {len(log)}/{len(strategy_rows)} "
                f"{query['id']}:{source} status={status} retrieved={len(records)} "
                f"total={result.total_hits if result.total_hits is not None else 'unknown'}",
                flush=True,
            )
            time.sleep(0.4)
    unique = {}
    provenance = {}
    for item in all_records:
        key = identity(item)
        sources = {part for part in item.get("retrieval_provenance", "").split(";") if part}
        sources.add(f'{item["source"]}:{item["query_id"]}')
        provenance.setdefault(key, set()).update(sources)
        if key not in unique or len(item.get("abstract", "")) > len(unique[key].get("abstract", "")):
            unique[key] = item
    title_unique: dict[str, dict] = {}
    title_provenance: dict[str, set[str]] = {}
    for key, item in unique.items():
        merged_key = "title:" + title_key(item["title"]) if item.get("title") else key
        item_provenance = provenance.get(key, set())
        if merged_key not in title_unique:
            title_unique[merged_key] = item
            title_provenance[merged_key] = set(item_provenance)
            continue
        current = title_unique[merged_key]
        current_score = sum(bool(current.get(field)) for field in ("doi", "pmid", "pmcid", "arxiv_id")) * 100 + len(current.get("abstract", ""))
        item_score = sum(bool(item.get(field)) for field in ("doi", "pmid", "pmcid", "arxiv_id")) * 100 + len(item.get("abstract", ""))
        preferred, other = (item, current) if item_score > current_score else (current, item)
        preferred = dict(preferred)
        for field in ("doi", "pmid", "pmcid", "arxiv_id", "url", "abstract", "authors", "venue"):
            if not preferred.get(field) and other.get(field):
                preferred[field] = other[field]
        title_unique[merged_key] = preferred
        title_provenance[merged_key].update(item_provenance)
    unique, provenance = title_unique, title_provenance
    rows = []
    for key, item in unique.items():
        item = dict(item)
        if item.get("doi") and not valid_doi(item["doi"]):
            item["invalid_doi_as_received"] = item["doi"]
            item["doi"] = ""
        item["record_id"] = hashlib.sha1(key.encode()).hexdigest()[:16]
        item["retrieval_provenance"] = ";".join(sorted(provenance[key]))
        item["future_year_flag"] = bool(item.get("year", "").isdigit() and int(item["year"]) > int(args.until[:4]))
        rows.append(item)
    rows.sort(key=lambda x: (x["direction"], x["year"], x["title"]))
    preferred = ["record_id", "source", "query_id", "direction", "title", "abstract", "year", "publication_date",
                 "authors", "venue", "doi", "pmid", "pmcid", "arxiv_id", "url", "automated_signal",
                 "automated_reason", "screening_status", "future_year_flag", "retrieval_provenance"]
    observed = {key for row in rows for key in row}
    fields = [key for key in preferred if key in observed] + sorted(observed - set(preferred))
    with (run_dir / "candidates.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    write_checkpoint(run_dir, log, all_records, "complete")
    summary = {
        "run_id": args.run_id, "generated_at": datetime.now(timezone.utc).isoformat(), "since": args.since, "until": args.until,
        "sources": sorted({row["source"] for row in log}), "query_families": len({row["query_id"] for row in log}), "retrieved_source_query_records": sum(int(row["retrieved"]) for row in log if row["status"] == "ok"),
        "deduplicated_candidates": len(rows), "automated_signal_counts": {level: sum(x["automated_signal"] == level for x in rows) for level in ("high", "possible", "low")},
        "successful_source_queries": sum(row["status"] == "ok" for row in log),
        "failed_source_queries": sum(row["status"] != "ok" for row in log),
        "configured_source_query_pairs": len(strategy_rows),
        "unrun_source_queries": len(strategy_rows) - len({(row["query_id"], row["source"]) for row in log}),
        "source_queries_truncated_at_limit": sum(str(row.get("truncated_at_limit", "")).lower() == "true" for row in log),
        "query_registry_sha256": hashlib.sha256(QUERY_FILE.read_bytes()).hexdigest(),
        "claim_boundary": "Candidate retrieval counts only; no record is included without human screening.",
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
