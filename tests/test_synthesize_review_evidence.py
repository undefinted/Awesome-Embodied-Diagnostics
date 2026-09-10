from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from synthesize_review_evidence import denominator_summary  # noqa: E402


class EvidenceTableTest(unittest.TestCase):
    def test_denominator_types_remain_labelled(self) -> None:
        row = {
            "participant_n": "38",
            "specimen_or_measurement_n": "72 eyes",
            "procedure_n": "NR",
            "development_data": "",
        }
        self.assertEqual(denominator_summary(row), "participants: 38; measures: 72 eyes")

    def test_missing_denominators_are_not_zero(self) -> None:
        row = {
            "participant_n": "NR",
            "specimen_or_measurement_n": "NR",
            "procedure_n": "NR",
            "development_data": "",
        }
        self.assertEqual(denominator_summary(row), "NR")


if __name__ == "__main__":
    unittest.main()
