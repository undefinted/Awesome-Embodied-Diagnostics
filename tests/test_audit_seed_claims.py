from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_seed_claims import numeric_tokens, support  # noqa: E402


class ClaimStringAuditTest(unittest.TestCase):
    def test_numeric_tokens_preserve_decimals_and_remove_commas(self) -> None:
        self.assertEqual(numeric_tokens("1,633 participants; 94.5% success"), ["1633", "94.5"])

    def test_support_does_not_confuse_substrings(self) -> None:
        status, missing = support(["13"], "the report included 130 cases")
        self.assertEqual(status, "numeric_strings_not_found")
        self.assertEqual(missing, ["13"])


if __name__ == "__main__":
    unittest.main()
