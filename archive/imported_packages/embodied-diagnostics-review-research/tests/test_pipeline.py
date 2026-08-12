from __future__ import annotations

import csv
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from count_words import clean_latex
from extract_citations import citations_in_text


class CitationExtractionTests(unittest.TestCase):
    def test_multiple_keys_and_optional_argument(self) -> None:
        text = "Alpha \\citep[see][]{KeyA, KeyB}.\nBeta \\cite{KeyA}."
        self.assertEqual(citations_in_text(text), [("KeyA", 1), ("KeyB", 1), ("KeyA", 2)])

    def test_latex_cleaning(self) -> None:
        cleaned = clean_latex(r"\section{Title} Alpha beta % hidden")
        self.assertNotIn("section", cleaned)
        self.assertNotIn("hidden", cleaned)
        self.assertIn("Alpha beta", cleaned)


class RegistryTests(unittest.TestCase):
    def test_registry_keys_are_unique(self) -> None:
        with (ROOT / "literature" / "references.csv").open(newline="", encoding="utf-8") as handle:
            keys = [row["citation_key"] for row in csv.DictReader(handle)]
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_citation_has_registry_row(self) -> None:
        with (ROOT / "literature" / "references.csv").open(newline="", encoding="utf-8") as handle:
            keys = {row["citation_key"] for row in csv.DictReader(handle)}
        cited = set()
        for path in (ROOT / "manuscript").rglob("*.tex"):
            cited.update(key for key, _ in citations_in_text(path.read_text(encoding="utf-8", errors="replace")))
        self.assertFalse(cited - keys, f"Missing registry keys: {sorted(cited - keys)}")


if __name__ == "__main__":
    unittest.main()

