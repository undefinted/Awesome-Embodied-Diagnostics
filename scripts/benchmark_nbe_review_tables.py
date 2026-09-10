"""Extract table purposes and schemas from selected Nature BME reviews.

The benchmark uses PubMed metadata and NCBI PMC JATS XML. It stores table
captions and column headings, not publisher PDFs or full article text.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "review" / "nbe_table_benchmark_seed.csv"
OUT = ROOT / "data" / "review" / "nbe_table_benchmark"
USER_AGENT = "Awesome-Embodied-Diagnostics/1.0 (NBE table benchmark)"


def text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def get(url: str, params: dict[str, str]) -> requests.Response:
    last: Exception | None = None
    for attempt in range(4):
        try:
            response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=45)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(str(last or "request failed"))


def main() -> None:
    with SEED.open(encoding="utf-8-sig", newline="") as handle:
        seeds = list(csv.DictReader(handle))
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    manifest: list[dict[str, str]] = []
    for seed in seeds:
        response = get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            {"db": "pmc", "id": seed["pmcid"]},
        )
        root = ET.fromstring(response.content)
        title = text(root.find(".//article-title"))
        journal = text(root.find(".//journal-title"))
        tables = root.findall(".//table-wrap")
        if not tables:
            rows.append({
                **seed, "article_title": title, "journal": journal, "table_index": "0",
                "table_caption": "", "column_headings": "", "table_count_in_article": "0",
                "source_url": response.url,
            })
        for index, table_wrap in enumerate(tables, start=1):
            headings: list[str] = []
            table = table_wrap.find(".//table")
            if table is not None:
                first_header = table.find(".//thead/tr")
                if first_header is None:
                    first_header = table.find(".//tr")
                if first_header is not None:
                    headings = [text(cell) for cell in list(first_header) if text(cell)]
            rows.append({
                **seed, "article_title": title, "journal": journal, "table_index": str(index),
                "table_caption": text(table_wrap.find("caption")),
                "column_headings": " | ".join(headings),
                "table_count_in_article": str(len(tables)), "source_url": response.url,
            })
        manifest.append({
            "pmid": seed["pmid"], "doi": seed["doi"], "source_url": response.url,
            "response_sha256": hashlib.sha256(response.content).hexdigest(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        })
        time.sleep(0.34)
    with (OUT / "table_schemas.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUT / "source_manifest.jsonl").open("w", encoding="utf-8") as handle:
        for item in manifest:
            handle.write(json.dumps(item, ensure_ascii=True) + "\n")
    summary = {
        "articles": len(seeds),
        "articles_with_tables": len({row["pmid"] for row in rows if int(row["table_count_in_article"]) > 0}),
        "extracted_tables": sum(int(row["table_index"]) > 0 for row in rows),
        "interpretation": "Benchmark describes selected Nature BME review table patterns; it is not a census of the journal.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
