#!/usr/bin/env python3
"""Build reproducible application-landscape summaries from frozen curation snapshots.

The script deliberately separates bibliometric task-candidate counts from the
claim-level representative evidence ledger. It does not infer clinical maturity
from publication volume.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "standalone_snapshots" / "2026-08-12" / "literature_task_assignments_all_snapshots.csv"
EVIDENCE = ROOT / "data" / "presentation" / "application_evidence.csv"
OUT = ROOT / "outputs" / "application_landscape"


CATEGORY_MAP = {
    "Active observational sensing": "Active observational sensing",
    "主动观察式检测": "Active observational sensing",
    "Response-based interactive diagnosis": "Response-based interactive diagnosis",
    "响应式交互检测": "Response-based interactive diagnosis",
    "Sample-based interactive diagnosis": "Sample-based interactive diagnosis",
    "采样式交互检测": "Sample-based interactive diagnosis",
}


TASK_ALIASES = {
    "机器人超声扫描": "机器人超声",
    "支气管镜": "机器人支气管镜",
    "机器人胃肠柔性内镜巡检": "内镜搜索/自主巡检",
    "机器人触诊/肿块搜索": "机器人触诊",
    "机器人经皮/芯针活检": "机器人穿刺/芯针活检",
    "静脉穿刺/采血": "机器人采血/静脉穿刺",
    "拭子": "机器人拭子采样",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read_csv(SNAPSHOT)
    # A paper can appear in multiple saved snapshots. Count unique task-paper pairs.
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        category = CATEGORY_MAP.get(row.get("category", ""), row.get("category", "").strip())
        task = TASK_ALIASES.get(row.get("task", "").strip(), row.get("task", "").strip())
        paper = row.get("doi") or row.get("paper_key") or row.get("title")
        if not category or not task or not paper:
            continue
        normalized = dict(row)
        normalized["normalized_category"] = category
        normalized["normalized_task"] = task
        unique[(task, paper.lower().strip())] = normalized

    task_counts: dict[tuple[str, str], Counter] = defaultdict(Counter)
    category_papers: dict[str, set[str]] = defaultdict(set)
    for (_, paper), row in unique.items():
        category = row["normalized_category"]
        task = row["normalized_task"]
        try:
            year = int(float(row.get("year", "") or 0))
        except ValueError:
            year = 0
        task_counts[(category, task)]["all"] += 1
        if year >= 2021:
            task_counts[(category, task)]["since_2021"] += 1
        category_papers[category].add(paper)

    task_output = []
    for (category, task), count in sorted(task_counts.items(), key=lambda item: (-item[1]["all"], item[0][1])):
        task_output.append(
            {
                "category": category,
                "task": task,
                "unique_closed_loop_candidates": count["all"],
                "candidates_since_2021": count["since_2021"],
                "recent_share": round(count["since_2021"] / count["all"], 3) if count["all"] else 0,
                "interpretation": "research-volume signal only; not maturity or clinical-effectiveness evidence",
            }
        )

    category_output = [
        {
            "category": category,
            "unique_candidate_papers": len(papers),
            "counting_unit": "unique normalized paper identifier within category",
        }
        for category, papers in sorted(category_papers.items(), key=lambda item: -len(item[1]))
    ]

    evidence = read_csv(EVIDENCE)
    stages = Counter(row.get("evidence_stage", "Unspecified") for row in evidence)
    stage_output = [
        {"evidence_stage": stage, "representative_systems": n, "note": "claim-level curated ledger, not systematic prevalence"}
        for stage, n in stages.most_common()
    ]

    write_csv(
        OUT / "clinical_task_candidate_counts.csv",
        task_output,
        ["category", "task", "unique_closed_loop_candidates", "candidates_since_2021", "recent_share", "interpretation"],
    )
    write_csv(
        OUT / "clinical_category_candidate_counts.csv",
        category_output,
        ["category", "unique_candidate_papers", "counting_unit"],
    )
    write_csv(
        OUT / "representative_evidence_stage_counts.csv",
        stage_output,
        ["evidence_stage", "representative_systems", "note"],
    )

    report = [
        "# Application landscape analysis",
        "",
        f"Frozen source: `{SNAPSHOT.relative_to(ROOT)}` ({len(rows):,} saved assignment rows).",
        f"Unique normalized task-paper pairs: {len(unique):,}.",
        "",
        "## Interpretation rules",
        "",
        "- Candidate counts describe the curated search workflow, not the global literature.",
        "- A task-paper pair is counted once across saved snapshots; a multi-task paper may appear under several tasks.",
        "- Category totals deduplicate papers inside each category.",
        "- Evidence-stage counts come from a small representative primary-study ledger and must not be read as prevalence.",
        "- Clinical maturity must be assessed independently from participants, prospective design, workflow integration, safety and diagnostic/decision outcomes.",
        "",
        "## Largest normalized task clusters",
        "",
    ]
    for row in task_output[:15]:
        report.append(
            f"- {row['task']}: {row['unique_closed_loop_candidates']} candidates; "
            f"{row['candidates_since_2021']} since 2021 (recent share {row['recent_share']:.1%})."
        )
    (OUT / "analysis_summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
