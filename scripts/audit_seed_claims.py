"""Check whether numeric extraction strings occur in retrievable primary-source text.

String presence is a reproducible QC signal, not a judgement that the number is
correctly interpreted. Absence is treated as unresolved and never as zero.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

from verify_evidence_sources import USER_AGENT, identifiers

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data" / "review"
OUT = REVIEW / "evidence_synthesis"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def europe_pmc_search(query: str) -> requests.Response:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    response = requests.get(
        url,
        params={"query": query, "format": "json", "pageSize": 1, "resultType": "core"},
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    response.raise_for_status()
    return response


def full_text(pmcid: str) -> requests.Response:
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    return response


def retrieve(seed_url: str) -> tuple[str, bytes, str]:
    doi, pmcid, pmid = identifiers(seed_url)
    if pmcid:
        try:
            response = full_text(pmcid)
            return "Europe PMC full text XML", response.content, response.url
        except requests.RequestException:
            response = europe_pmc_search(f"PMCID:{pmcid}")
            results = response.json().get("resultList", {}).get("result", [])
            if not results:
                raise RuntimeError(f"No Europe PMC record for PMCID:{pmcid}")
            return "Europe PMC core record", response.content, response.url
    query = f'DOI:"{doi}"' if doi else f"EXT_ID:{pmid}"
    response = europe_pmc_search(query)
    results = response.json().get("resultList", {}).get("result", [])
    if not results:
        raise RuntimeError(f"No Europe PMC record for {query}")
    resolved_pmcid = str(results[0].get("pmcid") or "").strip()
    if resolved_pmcid:
        try:
            full_response = full_text(resolved_pmcid)
            return "Europe PMC full text XML", full_response.content, full_response.url
        except requests.RequestException:
            pass
    return "Europe PMC core record", response.content, response.url


def normalize_text(payload: bytes) -> str:
    text = payload.decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace(",", "").replace("−", "-").replace("–", "-").replace("×", "x")
    return re.sub(r"\s+", " ", text).lower()


def numeric_tokens(value: str) -> list[str]:
    normalized = value.replace(",", "").replace("−", "-").replace("–", "-")
    return list(dict.fromkeys(re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", normalized)))


def support(tokens: list[str], source_text: str) -> tuple[str, list[str]]:
    if not tokens:
        return "no_numeric_tokens", []
    missing = [token for token in tokens if not re.search(rf"(?<!\d){re.escape(token)}(?!\d)", source_text)]
    if not missing:
        return "all_numeric_strings_found", []
    if len(missing) < len(tokens):
        return "partial_numeric_string_support", missing
    return "numeric_strings_not_found", missing


def main() -> None:
    rows = read_csv(REVIEW / "manuscript_evidence_seed.csv")
    previous_path = OUT / "claim_string_audit.csv"
    previous = {row["study"]: row for row in read_csv(previous_path)} if previous_path.exists() else {}
    output: list[dict[str, str]] = []
    for row in rows:
        payload = b""
        source_type = source_url = error = ""
        try:
            source_type, payload, source_url = retrieve(row["public_url"])
            source_text = normalize_text(payload)
        except Exception as exc:
            source_text = ""
            error = f"{type(exc).__name__}: {exc}"
        sample_tokens = numeric_tokens(row["sample_or_setting"])
        result_tokens = numeric_tokens(row["key_publicly_verified_result"])
        sample_status, sample_missing = support(sample_tokens, source_text)
        result_status, result_missing = support(result_tokens, source_text)
        checked = datetime.now(timezone.utc).isoformat()
        audited = {
            "study": row["study"],
            "source_type": source_type,
            "source_url": source_url,
            "response_sha256": hashlib.sha256(payload).hexdigest() if payload else "",
            "sample_numeric_tokens": ";".join(sample_tokens),
            "sample_string_support": sample_status,
            "sample_missing_tokens": ";".join(sample_missing),
            "result_numeric_tokens": ";".join(result_tokens),
            "result_string_support": result_status,
            "result_missing_tokens": ";".join(result_missing),
            "checked_at": checked,
            "error": error,
            "interpretation_boundary": "String presence only; human context and denominator checking remain required.",
        }
        if not payload and row["study"] in previous and previous[row["study"]].get("response_sha256"):
            audited = previous[row["study"]]
            audited["error"] = "refresh_failed; retained prior hashed source snapshot: " + error
        output.append(audited)
        time.sleep(0.2)
    with (OUT / "claim_string_audit.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    summary = {
        "reports": len(output),
        "source_text_retrieved": sum(bool(row["response_sha256"]) for row in output),
        "sample_all_numeric_strings_found": sum(row["sample_string_support"] == "all_numeric_strings_found" for row in output),
        "sample_unresolved_or_partial": sum(row["sample_string_support"] in {"partial_numeric_string_support", "numeric_strings_not_found"} for row in output),
        "result_all_numeric_strings_found": sum(row["result_string_support"] == "all_numeric_strings_found" for row in output),
        "result_unresolved_or_partial": sum(row["result_string_support"] in {"partial_numeric_string_support", "numeric_strings_not_found"} for row in output),
        "claim_boundary": "Automated string QC does not replace independent human verification of context, denominators or interpretation.",
    }
    (OUT / "claim_string_audit_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
