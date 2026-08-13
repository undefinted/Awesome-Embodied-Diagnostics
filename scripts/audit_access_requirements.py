"""Audit public-access status of the curated review bibliography via OpenAlex.

This script does not download copyrighted full text. It combines the curated
manuscript bibliography and the application evidence ledger, deduplicates by DOI
or normalized title, and records whether OpenAlex exposes a legal OA location.
"""

from __future__ import annotations

import csv
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "access_audit"
CACHE = OUT / "openalex_cache"


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def norm_doi(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value


def norm_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").lower()
    return re.sub(r"[^a-z0-9]+", "", value)


def openalex(key: str, doi: str, title: str):
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    if doi:
        url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/")
    else:
        query = urllib.parse.urlencode({"search": title, "per-page": 1})
        url = "https://api.openalex.org/works?" + query
    req = urllib.request.Request(url, headers={"User-Agent": "awesome-embodied-diagnostics-access-audit/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.load(response)
        if "results" in data:
            data = data["results"][0] if data["results"] else {}
    except Exception as exc:  # preserve auditability; do not silently mark closed
        data = {"_error": str(exc)}
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    time.sleep(0.08)
    return data


records = []

for r in rows(ROOT / "archive/imported_packages/embodied-diagnostics-review-research/literature/references.csv"):
    records.append({
        "origin": "manuscript_bibliography",
        "priority": "P1" if r.get("citation_key") else "P2",
        "domain": "manuscript-wide",
        "title": r.get("title", ""), "year": r.get("year", ""),
        "doi": norm_doi(r.get("doi", "")), "url": r.get("url", ""),
        "citation_key": r.get("citation_key", ""), "role": r.get("source_note", ""),
    })

for r in rows(ROOT / "archive/imported_packages/embodied-diagnostic-agents-review-research-v0.1.0/data/references.csv"):
    records.append({
        "origin": "diagnostic_agents_bibliography",
        "priority": "P1" if r.get("core_reference") == "1" else "P2",
        "domain": r.get("sections", ""), "title": r.get("title", ""),
        "year": r.get("year", ""), "doi": norm_doi(r.get("doi", "")),
        "url": r.get("url", ""), "citation_key": r.get("citekey", ""),
        "role": r.get("evidence_role", ""),
    })

for r in rows(ROOT / "data/presentation/application_evidence.csv"):
    source = r.get("source", "")
    doi = norm_doi(source) if "doi.org/" in source else ""
    records.append({
        "origin": "application_evidence_ledger", "priority": "P1",
        "domain": r.get("domain", ""), "title": r.get("representative_system", ""),
        "year": "", "doi": doi, "url": source, "citation_key": "",
        "role": r.get("direction", ""),
    })

dedup = {}
for r in records:
    key = "doi:" + r["doi"] if r["doi"] else "title:" + norm_title(r["title"])
    if not key or key == "title:":
        continue
    if key not in dedup:
        dedup[key] = r | {"origins": r["origin"]}
    else:
        old = dedup[key]
        old["origins"] = "; ".join(sorted(set(old["origins"].split("; ") + [r["origin"]])))
        if old["priority"] != "P1" and r["priority"] == "P1":
            old["priority"] = "P1"
        for field in ["domain", "year", "url", "citation_key", "role"]:
            if not old.get(field) and r.get(field):
                old[field] = r[field]

output = []
for idx, (key, r) in enumerate(sorted(dedup.items()), start=1):
    data = openalex(f"{idx:04d}_{re.sub('[^a-z0-9]', '_', key)[:80]}", r["doi"], r["title"])
    oa = data.get("open_access") or {}
    best = data.get("best_oa_location") or {}
    is_oa = oa.get("is_oa")
    best_url = best.get("pdf_url") or best.get("landing_page_url") or ""
    source_lower = (r["url"] or "").lower()
    public_hint = any(x in source_lower for x in ["pmc.ncbi", "who.int", "fda.gov", "clinicaltrials.gov", "imdrf.org", "arxiv.org"])
    if is_oa is True:
        status, needed, route = "public_full_text_identified", "no", "use_best_public_location"
    elif public_hint:
        status, needed, route = "public_source_link_present_manual_check", "no", "open_recorded_public_url"
    elif is_oa is False:
        status, needed, route = "no_public_full_text_identified", "yes", "institutional_subscription_or_author_request"
    else:
        # Official guidance, trial registrations and public repository URLs do
        # not always map to OpenAlex. Keep them for a manual legal-access check.
        status, needed, route = "access_status_unresolved", "check", "manual_library_or_author_search"
    output.append({
        "access_id": f"ACC{idx:04d}", "priority": r["priority"], "domain": r["domain"],
        "title_or_system": r["title"], "year": r["year"], "doi": r["doi"],
        "citation_key": r["citation_key"], "evidence_role": r["role"],
        "origins": r["origins"], "recorded_url": r["url"],
        "openalex_id": data.get("id", ""), "oa_status": oa.get("oa_status", ""),
        "public_access_status": status, "best_public_url": best_url,
        "user_acquisition_needed": needed, "recommended_route": route,
        "audit_note": data.get("_error", ""),
    })

corrections_path = ROOT / "data/access/manual_public_access_corrections.csv"
if corrections_path.exists():
    corrections = {norm_doi(r["doi_or_identifier"]): r for r in rows(corrections_path)}
    for r in output:
        correction = corrections.get(norm_doi(r["doi"]))
        if correction:
            r["public_access_status"] = correction["corrected_status"]
            r["best_public_url"] = correction["public_url"]
            r["user_acquisition_needed"] = "no"
            r["recommended_route"] = "use_manually_verified_public_location"
            r["audit_note"] = correction["note"]

OUT.mkdir(parents=True, exist_ok=True)
fields = list(output[0])
with (OUT / "curated_literature_access_audit.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader(); writer.writerows(output)

needed = [r for r in output if r["user_acquisition_needed"] in {"yes", "check"}]
needed.sort(key=lambda r: (r["priority"] != "P1", r["domain"], r["title_or_system"]))
with (OUT / "user_acquisition_queue.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader(); writer.writerows(needed)

summary = {
    "curated_unique_records": len(output),
    "public_full_text_or_public_link": sum(r["user_acquisition_needed"] == "no" for r in output),
    "institutional_or_author_acquisition_needed": sum(r["user_acquisition_needed"] == "yes" for r in output),
    "manual_access_check_needed": sum(r["user_acquisition_needed"] == "check" for r in output),
    "p1_items_in_acquisition_queue": sum(r["priority"] == "P1" for r in needed),
}
(OUT / "access_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
