from pathlib import Path
import csv
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "application_support"
OUT.mkdir(parents=True, exist_ok=True)

PURPLE = "#5B1A6E"
PURPLE2 = "#8A5A96"
GREEN = "#2E7D65"
ORANGE = "#D47A20"
GREY = "#B9B2BD"

for candidate in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]:
    if any(f.name == candidate for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [candidate, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


tasks = read_csv(ROOT / "outputs/application_landscape/clinical_task_candidate_counts.csv")
tasks = sorted(tasks, key=lambda r: int(float(r["unique_closed_loop_candidates"])), reverse=True)[:14]
labels = [r["task"] for r in tasks][::-1]
values = [int(float(r["unique_closed_loop_candidates"])) for r in tasks][::-1]

fig, ax = plt.subplots(figsize=(10, 6.4))
ax.barh(labels, values, color=PURPLE)
for y, v in enumerate(values):
    ax.text(v + max(values) * 0.012, y, str(v), va="center", fontsize=8)
ax.set_xlabel("Unique normalized task–paper candidates in the saved corpus")
ax.set_title("Clinical embodied-detection candidate landscape", loc="left", weight="bold")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.grid(axis="x", alpha=0.18)
fig.text(0.01, 0.01, "Candidate corpus after task normalization; not a global publication count or maturity score.", fontsize=8, color="#6D6672")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "clinical_task_candidate_counts.png", dpi=220, bbox_inches="tight")
fig.savefig(OUT / "clinical_task_candidate_counts.svg", bbox_inches="tight")
plt.close(fig)

coverage = read_csv(ROOT / "data/presentation/domain_coverage_audit.csv")
status_order = ["已系统计量", "已核验代表性证据", "待系统筛选"]
domains = ["Clinical", "Laboratory", "Everyday"]
counts = {d: Counter(r["status"] for r in coverage if r["domain"] == d) for d in domains}

fig, ax = plt.subplots(figsize=(9.5, 5.5))
bottom = [0] * len(domains)
colors = [PURPLE, GREEN, ORANGE]
for status, color in zip(status_order, colors):
    vals = [counts[d][status] for d in domains]
    ax.bar(domains, vals, bottom=bottom, label=status, color=color)
    for i, (b, v) in enumerate(zip(bottom, vals)):
        if v:
            ax.text(i, b + v / 2, str(v), ha="center", va="center", color="white", weight="bold")
    bottom = [b + v for b, v in zip(bottom, vals)]
ax.set_ylabel("Number of normalized tasks in the coverage audit")
ax.set_title("Research-completeness status by application domain", loc="left", weight="bold")
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.09))
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Status describes the current research package, not the maturity of the technology.", fontsize=8, color="#6D6672")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(OUT / "coverage_status_by_domain.png", dpi=220, bbox_inches="tight")
fig.savefig(OUT / "coverage_status_by_domain.svg", bbox_inches="tight")
plt.close(fig)

# Evidence-stage counts are intentionally descriptive of the representative ledger.
evidence = read_csv(ROOT / "data/presentation/application_evidence.csv")
domain_stage = defaultdict(Counter)
for row in evidence:
    domain_stage[row["domain"]][row["evidence_stage"]] += 1

summary_rows = []
for domain, counter in domain_stage.items():
    for stage, count in counter.most_common():
        summary_rows.append((domain, stage, count))
with (OUT / "representative_evidence_stage_summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["domain", "evidence_stage", "representative_rows"])
    w.writerows(summary_rows)
