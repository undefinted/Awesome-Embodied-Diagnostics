#!/usr/bin/env python3
"""Query Crossref for metadata suggestions without mutating the source catalog."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def query(title: str, mailto: str, timeout: float) -> dict:
    params = {"query.title": title, "rows": 1, "select": "DOI,title,author,published,container-title,volume,page,type,URL"}
    if mailto:
        params["mailto"] = mailto
    url = "https://api.crossref.org/works?" + urlencode(params)
    request = Request(url, headers={"User-Agent": f"embodied-diagnostic-agents-review/0.1 (mailto:{mailto or 'not-provided'})"})
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    items = payload.get("message", {}).get("items", [])
    return items[0] if items else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="data/references.csv")
    parser.add_argument("--output", default="results/crossref_suggestions.json")
    parser.add_argument("--mailto", default="")
    parser.add_argument("--all", action="store_true", help="Query records that already have a DOI too")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()

    with Path(args.catalog).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    suggestions = []
    for row in rows:
        if row["doi"] and not args.all:
            continue
        try:
            candidate = query(row["title"], args.mailto, args.timeout)
            suggestions.append({"record_id": row["record_id"], "catalog_title": row["title"], "candidate": candidate})
        except Exception as exc:  # retain errors in the audit output
            suggestions.append({"record_id": row["record_id"], "catalog_title": row["title"], "error": str(exc)})
        time.sleep(args.delay)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(suggestions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

