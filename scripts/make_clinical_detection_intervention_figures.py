#!/usr/bin/env python3
"""Render bilingual, publication-style figures from the frozen CDI tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PURPLE = "#642176"
GREEN = "#2F8A70"
INK = "#24172A"
MUTED = "#746B79"
GRID = "#E9E3EA"


def style() -> None:
    plt.rcParams.update({
        "font.family": ["Arial", "Microsoft YaHei", "DejaVu Sans"],
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "axes.titlecolor": INK,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "svg.fonttype": "none",
    })


def save(fig, out: Path, stem: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def nested_bar(ax, labels, visible, available, title, xlabel, series_labels, note=None):
    y = range(len(labels))
    ax.barh(y, visible, color=PURPLE, height=0.58, label=series_labels[0])
    ax.barh(y, available, color=GREEN, height=0.23, label=series_labels[1])
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=14)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    for yi, (v, a) in enumerate(zip(visible, available)):
        ax.text(v + max(visible) * 0.018, yi, f"{int(v)}", va="center", color=INK, fontsize=9)
        if a:
            ax.text(a - max(visible) * 0.012, yi, f"{int(a)}", va="center", ha="right", color="white", fontsize=8, fontweight="bold")
    if note:
        ax.text(0, -0.16, note, transform=ax.transAxes, fontsize=8, color=MUTED, va="top")


def mechanism_figure(counts: pd.DataFrame, out: Path, lang: str):
    cn = lang == "cn"
    labels = counts["mechanism_cn" if cn else "mechanism_en"].tolist()
    visible = counts["public_visible_unique_title_candidates"].astype(int).tolist()
    available = counts["public_available_location_identified"].astype(int).tolist()
    title = "临床检测与干预：互斥证据机制统计" if cn else "Clinical detection and intervention: mutually exclusive evidence mechanisms"
    xlabel = "去重论文候选数" if cn else "Deduplicated title-level candidate works"
    note = (
        "同一冻结公开索引语料、同一题名规则；主分类按终点证据动作互斥。不是系统综述最终纳入数。"
        if cn else
        "One frozen public-index corpus and one title-screen protocol; primary mechanisms are mutually exclusive. Not systematic-review inclusion counts."
    )
    fig, ax = plt.subplots(figsize=(10.8, 4.5))
    series_labels = ("公开可见题名候选", "已识别公开全文位置") if cn else ("Public-visible title candidates", "Public full-text location identified")
    nested_bar(ax, labels, visible, available, title, xlabel, series_labels, note)
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, -0.32), ncol=2, fontsize=8)
    save(fig, out, f"clinical_detection_intervention_mechanisms_{lang}")


def subtask_figure(counts: pd.DataFrame, out: Path, mechanism: str, lang: str):
    cn = lang == "cn"
    d = counts[counts["mechanism_code"] == mechanism].copy()
    d = d.sort_values("public_visible_unique_title_candidates", ascending=False)
    labels = d["task_cn" if cn else "task_en"].tolist()
    visible = d["public_visible_unique_title_candidates"].astype(int).tolist()
    available = d["public_available_location_identified"].astype(int).tolist()
    mech_name = d.iloc[0]["mechanism_code"] + " " + ({"1.1":"主动观察式检测","1.2":"响应式交互诊断","1.3":"采样式交互诊断"}[mechanism] if cn else {
        "1.1":"Active observational sensing","1.2":"Response-based interactive diagnosis","1.3":"Sample-based interactive diagnosis"}[mechanism])
    title = f"{mech_name}：互斥主任务统计" if cn else f"{mech_name}: mutually exclusive primary subtasks"
    xlabel = "去重论文候选数" if cn else "Deduplicated title-level candidate works"
    note = "零值保留，以显示当前公开索引题名筛选的证据空白。" if cn else "Zero-valued tasks are retained to show gaps in the current public-index title screen."
    height = max(4.2, 0.58 * len(d) + 2.3)
    fig, ax = plt.subplots(figsize=(11.5, height))
    series_labels = ("公开可见题名候选", "已识别公开全文位置") if cn else ("Public-visible title candidates", "Public full-text location identified")
    nested_bar(ax, labels, visible, available, title, xlabel, series_labels, note)
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, -0.24), ncol=2, fontsize=8)
    save(fig, out, f"clinical_detection_intervention_{mechanism.replace('.', '')}_subtasks_{lang}")


def annual_figure(annual: pd.DataFrame, out: Path, lang: str):
    cn = lang == "cn"
    d = annual[(annual["year"] >= 2000) & (annual["year"] <= 2026)].copy()
    fig, ax = plt.subplots(figsize=(11.2, 5.2))
    colors = {"1.1": PURPLE, "1.2": "#C07A35", "1.3": GREEN}
    names = {
        "1.1": "1.1 主动观察式检测" if cn else "1.1 Active observational sensing",
        "1.2": "1.2 响应式交互诊断" if cn else "1.2 Response-based interactive diagnosis",
        "1.3": "1.3 采样式交互诊断" if cn else "1.3 Sample-based interactive diagnosis",
    }
    for code in ["1.1", "1.2", "1.3"]:
        ax.plot(d["year"], d[f"{code}_public_visible"], color=colors[code], linewidth=2.2, marker="o", markersize=3.5, label=names[code])
    ax.set_title("临床检测与干预题名候选的年度分布" if cn else "Annual distribution of title-level candidates in clinical detection and intervention", loc="left", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("发表年份" if cn else "Publication year")
    ax.set_ylabel("去重论文候选数" if cn else "Candidate works")
    ax.grid(color=GRID, linewidth=0.8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.legend(frameon=False, ncol=1, loc="upper left", fontsize=8)
    note = "2026 年为截至 2026-08-15 的不完整年度；曲线反映冻结公开索引题名候选，不代表真实发表率。" if cn else "2026 is incomplete through 15 Aug 2026; curves describe a frozen public-index title screen, not true publication incidence."
    ax.text(0, -0.18, note, transform=ax.transAxes, fontsize=8, color=MUTED, va="top")
    save(fig, out, f"clinical_detection_intervention_annual_{lang}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    style()
    mechanisms = pd.read_csv(args.input_dir / "clinical_detection_intervention_mechanism_counts.csv", dtype={"mechanism_code": str})
    subtasks = pd.read_csv(args.input_dir / "clinical_detection_intervention_subtask_counts.csv", dtype={"mechanism_code": str})
    annual = pd.read_csv(args.input_dir / "clinical_detection_intervention_annual_counts.csv")
    for lang in ["cn", "en"]:
        mechanism_figure(mechanisms, args.output_dir, lang)
        for mechanism in ["1.1", "1.2", "1.3"]:
            subtask_figure(subtasks, args.output_dir, mechanism, lang)
        annual_figure(annual, args.output_dir, lang)


if __name__ == "__main__":
    main()
