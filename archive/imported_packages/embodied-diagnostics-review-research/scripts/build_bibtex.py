#!/usr/bin/env python3
"""Generate literature/references.bib from the auditable CSV registry."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from common import REPO_ROOT


INPUT = REPO_ROOT / "literature" / "references.csv"
OUTPUT = REPO_ROOT / "literature" / "references.bib"


def latex_escape(value: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
    }
    return "".join(replacements.get(char, char) for char in value.strip())


def author_field(raw: str) -> str:
    if not raw:
        return ""
    return " and ".join(part.strip() for part in raw.split(";") if part.strip())


def entry_type(raw: str) -> str:
    candidate = re.sub(r"[^A-Za-z]", "", raw or "misc").lower()
    return candidate if candidate in {"article", "book", "inproceedings", "misc", "techreport"} else "misc"


def render(row: dict[str, str]) -> str:
    key = row["citation_key"].strip()
    unresolved = row["metadata_status"].strip() == "unresolved"
    title = row["title"].strip() or f"Unresolved citation key: {key}"
    fields: list[tuple[str, str]] = [("title", title)]
    authors = author_field(row["authors"])
    if authors:
        fields.append(("author", authors))
    if row["year"].strip():
        fields.append(("year", row["year"].strip()))
    if row["journal"].strip():
        fields.append(("journal", row["journal"].strip()))
    if row["volume"].strip():
        fields.append(("volume", row["volume"].strip()))
    if row["pages_or_article"].strip():
        fields.append(("pages", row["pages_or_article"].strip()))
    if row["doi"].strip() and not row["doi"].startswith("http"):
        fields.append(("doi", row["doi"].strip()))
    if row["url"].strip():
        fields.append(("url", row["url"].strip()))
    note_bits = [row["metadata_status"].strip(), row["source_note"].strip()]
    if unresolved:
        note_bits.insert(0, "Metadata unresolved; do not cite without verification")
    note = "; ".join(bit for bit in note_bits if bit)
    if note:
        fields.append(("note", note))
    rendered = [f"@{entry_type(row['entry_type'])}{{{key},"]
    rendered.extend(f"  {name} = {{{latex_escape(value)}}}," for name, value in fields)
    rendered.append("}")
    return "\n".join(rendered)


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {"citation_key", "title", "metadata_status"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit("references.csv is empty or missing required columns")
    keys = [row["citation_key"] for row in rows]
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate citation keys: {', '.join(duplicates)}")
    content = "% Generated from literature/references.csv; do not edit by hand.\n\n"
    content += "\n\n".join(render(row) for row in rows)
    content += "\n"
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(rows)} entries")


if __name__ == "__main__":
    main()

