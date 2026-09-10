"""Re-resolve the manuscript evidence seed against authoritative public records."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "review" / "manuscript_evidence_seed.csv"
USER_AGENT = "Awesome-Embodied-Diagnostics/1.0 (evidence-audit; https://github.com/undefinted/Awesome-Embodied-Diagnostics)"


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def title_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, title_key(left), title_key(right)).ratio()


def identifiers(url: str) -> tuple[str, str, str]:
    doi = ""
    pmcid = ""
    pmid = ""
    doi_match = re.search(r"doi\.org/(10\.\d{4,9}/[^?#]+)", url, flags=re.I)
    pmc_match = re.search(r"/(PMC\d+)/?", url, flags=re.I)
    pmid_match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url, flags=re.I)
    if doi_match:
        doi = doi_match.group(1).rstrip("/").lower()
    if pmc_match:
        pmcid = pmc_match.group(1).upper()
    if pmid_match:
        pmid = pmid_match.group(1)
    return doi, pmcid, pmid


def get(url: str, *, params: dict | None = None) -> requests.Response:
    last: Exception | None = None
    for attempt in range(5):
        try:
            response = requests.get(
                url,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=45,
            )
            if response.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last = exc
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(str(last or "request failed"))


def crossref(doi: str) -> tuple[str, str, bytes, str]:
    endpoint = f"https://api.crossref.org/works/{quote(doi, safe='')}"
    response = get(endpoint)
    message = response.json()["message"]
    title = clean((message.get("title") or [""])[0])
    resolved_doi = clean(message.get("DOI")).lower()
    return title, resolved_doi, response.content, endpoint


def europe_pmc(identifier: str, field: str) -> tuple[str, str, bytes, str]:
    query = f"{field}:{identifier}"
    endpoint = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    response = get(endpoint, params={"query": query, "format": "json", "pageSize": 1, "resultType": "core"})
    results = response.json().get("resultList", {}).get("result", [])
    if not results:
        raise RuntimeError(f"Europe PMC returned no record for {query}")
    item = results[0]
    resolved = clean(item.get("pmcid") if field == "PMCID" else item.get("pmid"))
    request_url = response.url
    return clean(item.get("title")), resolved, response.content, request_url


def verification_status(*, stable_identifier: bool, identifier_match: bool, title_score: float) -> tuple[str, str]:
    """Keep bibliographic identity and title-quality control as separate decisions."""
    if stable_identifier and identifier_match:
        relation = "exact_or_close" if title_score >= 0.84 else "shorthand_or_alias_reviewed"
        return "verified_identifier", relation
    if not stable_identifier and identifier_match and title_score >= 0.84:
        return "verified_title_only", "exact_or_close"
    return "unverified", "unresolved_or_mismatched"


def publisher_page(url: str) -> tuple[str, str, bytes, str]:
    response = get(url)
    content = response.content
    text = response.text
    match = re.search(
        r'<meta[^>]+(?:name|property)=["\'](?:citation_title|og:title)["\'][^>]+content=["\']([^"\']+)',
        text,
        flags=re.I,
    )
    if not match:
        match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.I | re.S)
    return clean(match.group(1) if match else ""), url, content, response.url


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/review/evidence_synthesis")
    args = parser.parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    with SEED.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    audit = []
    snapshots = []
    for seed in rows:
        doi, pmcid, pmid = identifiers(seed["public_url"])
        source_type = ""
        resolved_title = ""
        resolved_identifier = ""
        source_url = ""
        payload = b""
        error = ""
        try:
            if doi:
                source_type = "Crossref DOI record"
                resolved_title, resolved_identifier, payload, source_url = crossref(doi)
                identifier_match = resolved_identifier.lower() == doi.lower()
            elif pmcid:
                source_type = "Europe PMC record"
                resolved_title, resolved_identifier, payload, source_url = europe_pmc(pmcid, "PMCID")
                identifier_match = resolved_identifier.upper() == pmcid.upper()
            elif pmid:
                source_type = "Europe PMC record"
                resolved_title, resolved_identifier, payload, source_url = europe_pmc(pmid, "EXT_ID")
                identifier_match = resolved_identifier == pmid
            else:
                source_type = "publisher page"
                resolved_title, resolved_identifier, payload, source_url = publisher_page(seed["public_url"])
                identifier_match = bool(source_url)
        except Exception as exc:  # preserve failures instead of inferring metadata
            identifier_match = False
            error = f"{type(exc).__name__}: {exc}"

        score = similarity(seed["study"], resolved_title) if resolved_title else 0.0
        stable_identifier = bool(doi or pmcid or pmid)
        status, title_relation = verification_status(
            stable_identifier=stable_identifier,
            identifier_match=identifier_match,
            title_score=score,
        )
        snapshot_hash = hashlib.sha256(payload).hexdigest() if payload else ""
        checked = datetime.now(timezone.utc).isoformat()
        audit.append({
            "study": seed["study"],
            "seed_url": seed["public_url"],
            "source_type": source_type,
            "source_url": source_url,
            "resolved_title": resolved_title,
            "resolved_identifier": resolved_identifier,
            "identifier_match": identifier_match,
            "title_similarity": f"{score:.3f}",
            "title_relation": title_relation,
            "metadata_status": status,
            "response_sha256": snapshot_hash,
            "checked_at": checked,
            "error": error,
            "claim_boundary": "Bibliographic identity only; numerical claims retain the manual article-level audit status.",
        })
        snapshots.append({
            "study": seed["study"],
            "retrieved_at": checked,
            "source_url": source_url,
            "response_sha256": snapshot_hash,
            "resolved_title": resolved_title,
            "resolved_identifier": resolved_identifier,
            "metadata_status": status,
        })
        time.sleep(0.25)

    fields = list(audit[0])
    with (output_dir / "source_verification.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audit)
    with (output_dir / "source_snapshot_manifest.jsonl").open("w", encoding="utf-8") as handle:
        for row in snapshots:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    summary = {
        "records": len(audit),
        "verified_identifier": sum(row["metadata_status"] == "verified_identifier" for row in audit),
        "verified_title_only": sum(row["metadata_status"] == "verified_title_only" for row in audit),
        "unverified": sum(row["metadata_status"] == "unverified" for row in audit),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": "This audit verifies bibliographic identity, not every extracted result.",
    }
    (output_dir / "source_verification_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
