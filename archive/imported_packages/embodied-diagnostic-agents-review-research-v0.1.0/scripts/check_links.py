#!/usr/bin/env python3
"""Check catalog URLs concurrently and write an auditable CSV report."""

from __future__ import annotations

import argparse
import csv
import ssl
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check(row: dict[str, str], timeout: float) -> dict[str, str]:
    request = Request(
        row["url"],
        method="GET",
        headers={"User-Agent": "embodied-diagnostic-agents-review/0.1 (+research metadata check)", "Range": "bytes=0-1024"},
    )
    status = ""
    final_url = ""
    error = ""
    try:
        with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            status = str(response.status)
            final_url = response.geturl()
    except HTTPError as exc:
        status = str(exc.code)
        final_url = exc.geturl()
        error = str(exc.reason)
    except (URLError, TimeoutError, OSError) as exc:
        error = str(exc)
    return {
        "record_id": row["record_id"],
        "url": row["url"],
        "http_status": status,
        "final_url": final_url,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "error": error,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="data/references.csv")
    parser.add_argument("--output", default="results/link_check.csv")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    with Path(args.catalog).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda row: check(row, args.timeout), rows))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    main()

