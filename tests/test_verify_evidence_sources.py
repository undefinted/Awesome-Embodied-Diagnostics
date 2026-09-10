from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_evidence_sources import identifiers, similarity, verification_status  # noqa: E402


class SourceVerificationTest(unittest.TestCase):
    def test_identifier_parsing(self) -> None:
        self.assertEqual(
            identifiers("https://doi.org/10.1038/S41467-024-48421-Y"),
            ("10.1038/s41467-024-48421-y", "", ""),
        )
        self.assertEqual(
            identifiers("https://pmc.ncbi.nlm.nih.gov/articles/PMC10038849/"),
            ("", "PMC10038849", ""),
        )

    def test_title_similarity_normalizes_punctuation(self) -> None:
        self.assertGreater(similarity("Robotic OCT: a pilot study", "Robotic OCT - a pilot study."), 0.95)

    def test_exact_identifier_can_have_shorthand_seed_title(self) -> None:
        self.assertEqual(
            verification_status(stable_identifier=True, identifier_match=True, title_score=0.46),
            ("verified_identifier", "shorthand_or_alias_reviewed"),
        )

    def test_title_only_requires_close_title(self) -> None:
        self.assertEqual(
            verification_status(stable_identifier=False, identifier_match=True, title_score=0.50),
            ("unverified", "unresolved_or_mismatched"),
        )


if __name__ == "__main__":
    unittest.main()
