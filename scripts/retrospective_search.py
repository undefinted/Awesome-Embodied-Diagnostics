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


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_doi(value: str) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I).lower().rstrip(".,; ")


def title_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


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


def pubmed(query: dict, since: str, until: str, limit: int) -> list[dict]:
    term = f'({query["scholarly"]}) AND ("{since}"[Date - Publication] : "{until}"[Date - Publication])'
    search = get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params={"db": "pubmed", "term": term, "retmode": "json", "retmax": limit, "sort": "pub date"},
        timeout=60,
    )
    search.raise_for_status()
    ids = search.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    fetched = get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml"},
        timeout=90,
    )
    fetched.raise_for_status()
    return parse_pubmed_xml(fetched.content, query)


def parse_pubmed_xml(content: bytes, query: dict) -> list[dict]:
    """Parse identifiers only from the current article, never its references."""
    out = []
    for article in ET.fromstring(content).findall(".//PubmedArticle"):
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
    return out


def europepmc(query: dict, since: str, until: str, limit: int) -> list[dict]:
    response = get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        params={"query": f'({query["scholarly"]}) FIRST_PDATE:[{since} TO {until}]', "format": "json", "pageSize": limit, "resultType": "core"},
        timeout=60,
    )
    response.raise_for_status()
    return [record("Europe PMC", query, title=x.get("title"), abstract=x.get("abstractText"), year=x.get("pubYear"),
                   publication_date=x.get("firstPublicationDate"), authors=x.get("authorString"), venue=x.get("journalTitle"),
                   doi=x.get("doi"), pmid=x.get("pmid"), pmcid=x.get("pmcid"), url=(f"https://doi.org/{x['doi']}" if x.get("doi") else f"https://europepmc.org/article/{x.get('source','MED')}/{x.get('id','')}"))
            for x in response.json().get("resultList", {}).get("result", [])]


def invert_abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions = sorted((position, word) for word, values in index.items() for position in values)
    return " ".join(word for _, word in positions)


def openalex(query: dict, since: str, until: str, limit: int) -> list[dict]:
    params = {"search": query["scholarly"], "filter": f"from_publication_date:{since},to_publication_date:{until}", "per-page": min(limit, 200)}
    mailto = os.getenv("OPENALEX_MAILTO") or os.getenv("CROSSREF_MAILTO")
    if mailto:
        params["mailto"] = mailto
    response = get(
        "https://api.openalex.org/works",
        params=params, timeout=60,
    )
    response.raise_for_status()
    out = []
    for x in response.json().get("results", []):
        authors = "; ".join(clean(a.get("author", {}).get("display_name")) for a in x.get("authorships", []))
        location = x.get("primary_location") or {}
        source = location.get("source") or {}
        out.append(record("OpenAlex", query, title=x.get("title"), abstract=invert_abstract(x.get("abstract_inverted_index")),
                          year=x.get("publication_year"), publication_date=x.get("publication_date"), authors=authors,
                          venue=source.get("display_name"), doi=x.get("doi"), url=x.get("doi") or location.get("landing_page_url") or x.get("id")))
    return out


def arxiv(query: dict, since: str, until: str, limit: int) -> list[dict]:
    response = get(
        "https://export.arxiv.org/api/query",
        params={"search_query": query["arxiv"], "start": 0, "max_results": min(limit, 200), "sortBy": "submittedDate", "sortOrder": "descending"},
        timeout=60,
    )
    response.raise_for_status()
    out = []
    for x in feedparser.parse(response.text).entries:
        published = clean(x.get("published"))
        if published[:10] < since or published[:10] > until:
            continue
        arxiv_id = x.get("id", "").rstrip("/").split("/")[-1]
        authors = "; ".join(clean(a.get("name")) for a in x.get("authors", []))
        out.append(record("arXiv", query, title=x.get("title"), abstract=x.get("summary"), year=published[:4],
                          publication_date=published[:10], authors=authors, venue="arXiv", arxiv_id=arxiv_id, url=x.get("id")))
    return out


def identity(item: dict) -> str:
    if item["doi"]:
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
    all_records, log = [], []
    completed: set[tuple[str, str]] = set()
    if args.resume and (run_dir / "candidates.csv").exists():
        with (run_dir / "candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
            all_records = list(csv.DictReader(handle))
    if args.resume and (run_dir / "query_log.csv").exists():
        with (run_dir / "query_log.csv").open(encoding="utf-8-sig", newline="") as handle:
            previous_log = list(csv.DictReader(handle))
        for row in previous_log:
            row.setdefault("truncated_at_limit", str(int(row.get("retrieved", 0) or 0) >= args.max_results))
        completed = {(row["query_id"], row["source"]) for row in previous_log if row["status"] == "ok"}
        log = previous_log
    if args.force:
        selected_pairs = {(q["id"], source) for q in queries for source in requested}
        all_records = [item for item in all_records if (item.get("query_id"), item.get("source", "").lower().replace(" ", "")) not in selected_pairs]
        log = [row for row in log if (row["query_id"], row["source"]) not in selected_pairs]
        completed -= selected_pairs
    for query in queries:
        for source in requested:
            if (query["id"], source) in completed:
                continue
            log = [row for row in log if (row["query_id"], row["source"]) != (query["id"], source)]
            started = datetime.now(timezone.utc)
            try:
                records = functions[source](query, args.since, args.until, args.max_results)
                status, error = "ok", ""
                all_records.extend(records)
            except Exception as exc:
                records, status, error = [], "error", f"{type(exc).__name__}: {exc}"
            log.append({"query_id": query["id"], "source": source, "status": status, "retrieved": len(records),
                        "truncated_at_limit": len(records) >= args.max_results,
                        "error": error, "started_at": started.isoformat()})
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
    with (run_dir / "query_log.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(log[0]) if log else []); writer.writeheader(); writer.writerows(log)
    summary = {
        "run_id": args.run_id, "generated_at": datetime.now(timezone.utc).isoformat(), "since": args.since, "until": args.until,
        "sources": sorted({row["source"] for row in log}), "query_families": len({row["query_id"] for row in log}), "retrieved_source_query_records": sum(int(row["retrieved"]) for row in log if row["status"] == "ok"),
        "deduplicated_candidates": len(rows), "automated_signal_counts": {level: sum(x["automated_signal"] == level for x in rows) for level in ("high", "possible", "low")},
        "successful_source_queries": sum(row["status"] == "ok" for row in log),
        "failed_source_queries": sum(row["status"] != "ok" for row in log),
        "configured_source_query_pairs": len(all_queries) * len(functions),
        "unrun_source_queries": len(all_queries) * len(functions) - len({(row["query_id"], row["source"]) for row in log}),
        "source_queries_truncated_at_limit": sum(str(row.get("truncated_at_limit", "")).lower() == "true" for row in log),
        "claim_boundary": "Candidate retrieval counts only; no record is included without human screening.",
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
