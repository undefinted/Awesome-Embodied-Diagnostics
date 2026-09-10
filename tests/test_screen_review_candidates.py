from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from screen_review_candidates import classify  # noqa: E402


class ScreeningRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = yaml.safe_load(
            (ROOT / "data" / "review" / "screening_rules.yaml").read_text(encoding="utf-8")
        )

    def test_core_signal_remains_a_screening_suggestion(self) -> None:
        row = {
            "title": "Closed-loop robotic ultrasound with image-quality feedback",
            "abstract": "The robot adapts probe motion for diagnostic screening.",
        }
        result = classify(row, self.rules)
        self.assertEqual(result["machine_screening_suggestion"], "priority_core_screen")
        self.assertEqual(result["adjudicated_decision"], "")

    def test_review_is_not_treated_as_primary_evidence(self) -> None:
        row = {
            "title": "A review of autonomous robotic ultrasound",
            "abstract": "Diagnostic imaging systems are summarized.",
        }
        result = classify(row, self.rules)
        self.assertEqual(result["machine_screening_suggestion"], "exclude_non_primary")

    def test_nonmedical_active_sensing_is_flagged(self) -> None:
        row = {
            "title": "Active sensing for bolt looseness monitoring",
            "abstract": "A robotic structural health monitoring method.",
        }
        result = classify(row, self.rules)
        self.assertEqual(result["machine_screening_suggestion"], "exclude_nonmedical_context")


if __name__ == "__main__":
    unittest.main()
