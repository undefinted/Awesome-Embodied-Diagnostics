"""Fail when a current Chinese presentation SVG/PNG lacks an English sibling."""
from pathlib import Path
import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--figure-dir", type=Path, default=ROOT / "figures" / "public_evidence")
FIG = parser.parse_args().figure_dir.resolve()
errors = []
superseded_basenames = {
    "p5_active_public_landscape",
    "p5_public_visible_available_extended",
}
for base in sorted(superseded_basenames):
    for suffix in (".svg", ".png", "_en.svg", "_en.png"):
        obsolete = FIG / f"{base}{suffix}"
        if obsolete.exists():
            errors.append(f"Superseded figure must not remain in current outputs: {obsolete}")
for suffix in (".svg", ".png"):
    for source in sorted(FIG.glob(f"*{suffix}")):
        if source.stem.endswith("_en"):
            continue
        sibling = source.with_name(f"{source.stem}_en{suffix}")
        if not sibling.exists():
            errors.append(f"Missing English counterpart: {sibling}")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("Bilingual figure validation passed: every current SVG/PNG has an _en counterpart.")
