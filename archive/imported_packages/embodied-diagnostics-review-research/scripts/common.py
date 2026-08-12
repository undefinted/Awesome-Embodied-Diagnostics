"""Shared utilities for the review-repository scripts."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    with (REPO_ROOT / "config" / "project.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def manuscript_paths() -> list[Path]:
    config = load_config()
    paths: set[Path] = set()
    for pattern in config["manuscript_globs"]:
        paths.update(REPO_ROOT.glob(pattern))
    return sorted(path for path in paths if path.is_file())


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()

