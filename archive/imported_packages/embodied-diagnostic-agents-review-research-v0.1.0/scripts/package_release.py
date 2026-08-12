#!/usr/bin/env python3
"""Create a deterministic GitHub-ready ZIP archive."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", "__pycache__", "node_modules"}
FIXED_TIME = (2026, 8, 12, 0, 0, 0)


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        path.is_file()
        and not any(part in EXCLUDED_PARTS or part.startswith("workbook_tmp.") for part in relative.parts)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(ROOT.parent / "embodied-diagnostic-agents-review-research-v0.1.0.zip"),
    )
    args = parser.parse_args()
    output = Path(args.output).resolve()
    prefix = ROOT.name

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((item for item in ROOT.rglob("*") if included(item)), key=lambda item: item.as_posix()):
            arcname = f"{prefix}/{path.relative_to(ROOT).as_posix()}"
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(output)


if __name__ == "__main__":
    main()

