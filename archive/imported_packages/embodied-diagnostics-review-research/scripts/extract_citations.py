#!/usr/bin/env python3
"""Extract LaTeX citation keys and their locations from all manuscript files."""

from __future__ import annotations

import csv
import re
from collections import defaultdict

from common import REPO_ROOT, manuscript_paths, relative


CITE_RE = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^{}]+)\}")
OUTPUT = REPO_ROOT / "results" / "citation_usage.csv"


def citations_in_text(text: str) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    for match in CITE_RE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        for key in match.group(1).split(","):
            cleaned = key.strip()
            if cleaned:
                found.append((cleaned, line))
    return found


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    usage: dict[tuple[str, str], list[int]] = defaultdict(list)
    for path in manuscript_paths():
        text = path.read_text(encoding="utf-8", errors="replace")
        for key, line in citations_in_text(text):
            usage[(relative(path), key)].append(line)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "citation_key", "count", "line_numbers"])
        for (file_name, key), lines in sorted(usage.items()):
            writer.writerow([file_name, key, len(lines), ";".join(map(str, lines))])
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(usage)} file-key records")


if __name__ == "__main__":
    main()

