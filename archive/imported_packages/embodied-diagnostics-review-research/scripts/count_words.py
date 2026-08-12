#!/usr/bin/env python3
"""Produce transparent approximate word counts for LaTeX manuscript files."""

from __future__ import annotations

import csv
import re

from common import REPO_ROOT, manuscript_paths, relative


OUTPUT = REPO_ROOT / "results" / "section_word_counts.csv"
COMMENT_RE = re.compile(r"(?<!\\)%.*$")
COMMAND_RE = re.compile(r"\\(?:begin|end)\{[^{}]+\}|\\[A-Za-z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*|[\u4e00-\u9fff]")


def clean_latex(text: str) -> str:
    text = "\n".join(COMMENT_RE.sub("", line) for line in text.splitlines())
    previous = None
    while previous != text:
        previous = text
        text = COMMAND_RE.sub(" ", text)
    return re.sub(r"[{}$^_~&]", " ", text)


def main() -> None:
    rows = []
    for path in manuscript_paths():
        raw = path.read_text(encoding="utf-8", errors="replace")
        cleaned = clean_latex(raw)
        words = WORD_RE.findall(cleaned)
        ascii_words = sum(bool(re.fullmatch(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", word)) for word in words)
        cjk_chars = sum(bool(re.fullmatch(r"[\u4e00-\u9fff]", word)) for word in words)
        rows.append([relative(path), ascii_words, cjk_chars, len(words), len(raw.encode("utf-8"))])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["file", "latin_word_count_approx", "cjk_character_count", "combined_token_count_approx", "bytes"])
        writer.writerows(rows)
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(rows)} manuscript files")


if __name__ == "__main__":
    main()

