#!/usr/bin/env python3
"""Render bilingual figures for the final Clinical Detection and Intervention taxonomy.

The input CSV is the single source of truth. The figures contain no publication
counts because the superseded title-level corpus has not completed uniform
full-text eligibility screening under the final taxonomy.
"""

from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


PURPLE = "#642176"
GREEN = "#2F8A70"
ORANGE = "#B36A2E"
INK = "#24172A"
MUTED = "#706875"
PALE = "#F6F2F7"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def setup_fonts() -> None:
    plt.rcParams.update({
        "font.family": ["Microsoft YaHei", "Arial", "DejaVu Sans"],
        "svg.fonttype": "none",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def taxonomy_figure(rows: list[dict[str, str]], out: Path, lang: str) -> None:
    cn = lang == "cn"
    grouped = {code: [r for r in rows if r["mechanism_code"] == code] for code in ("1.1", "1.2", "1.3")}
    colours = {"1.1": PURPLE, "1.2": ORANGE, "1.3": GREEN}
    mech_names = {
        "1.1": "主动观察式感知" if cn else "Active observational sensing",
        "1.2": "诱发响应式交互诊断" if cn else "Response-eliciting interactive diagnosis",
        "1.3": "诊断性样本获取" if cn else "Diagnostic sample acquisition",
    }
    title = "临床检测与干预：最终任务分类" if cn else "Clinical detection and intervention: final task taxonomy"
    subtitle = (
        "主类按诊断证据生成机制定义；模态、解剖部位、载体和自主程度作为独立标签"
        if cn else
        "Primary classes follow the evidence-generation mechanism; modality, anatomy, carrier and autonomy remain separate tags"
    )

    fig, axes = plt.subplots(1, 3, figsize=(16, 8.8), gridspec_kw={"wspace": 0.08})
    fig.suptitle(title, x=0.045, y=0.97, ha="left", fontsize=22, fontweight="bold", color=INK)
    fig.text(0.045, 0.925, subtitle, ha="left", fontsize=11, color=MUTED)

    for ax, code in zip(axes, ("1.1", "1.2", "1.3")):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        colour = colours[code]
        ax.add_patch(FancyBboxPatch((0.02, 0.865), 0.96, 0.095, boxstyle="round,pad=0.012,rounding_size=0.02", facecolor=colour, edgecolor="none"))
        header = f"{code}  {mech_names[code]}"
        if not cn and code == "1.2":
            header = "1.2  Response-eliciting\ninteractive diagnosis"
        ax.text(0.055, 0.913, header, color="white", fontsize=11.3 if (not cn and code == "1.2") else 13, fontweight="bold", va="center")

        task_rows = grouped[code]
        top = 0.825
        card_h = min(0.125, 0.69 / max(len(task_rows), 1))
        gap = 0.018
        for idx, row in enumerate(task_rows):
            y = top - idx * (card_h + gap) - card_h
            ax.add_patch(FancyBboxPatch((0.02, y), 0.96, card_h, boxstyle="round,pad=0.012,rounding_size=0.015", facecolor=PALE, edgecolor="#E4DDE7", linewidth=0.8))
            name = row["task_family_cn" if cn else "task_family_en"]
            name = textwrap.fill(name, width=18 if cn else 31)
            ax.text(0.055, y + card_h * 0.65, row["task_code"], color=colour, fontsize=10.5, fontweight="bold", va="center")
            ax.text(0.15, y + card_h * 0.65, name, color=INK, fontsize=8.8 if not cn else 9.5, fontweight="bold", va="center", wrap=True)
            evidence = row["terminal_evidence_cn" if cn else "terminal_evidence_en"]
            evidence = textwrap.fill(evidence, width=25 if cn else 48)
            ax.text(0.055, y + card_h * 0.23, evidence, color=MUTED, fontsize=7.7, va="center", wrap=True)

    footer = (
        "分类单位：一项研究中被评价的一个诊断证据获取阶段；多阶段系统可产生多个相互关联的任务记录。"
        if cn else
        "Unit: one evaluated diagnostic evidence-acquisition episode; a multistage system may generate linked task records."
    )
    fig.text(0.045, 0.035, footer, color=MUTED, fontsize=9)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"clinical_detection_intervention_final_taxonomy_{lang}.svg", bbox_inches="tight")
    fig.savefig(out / f"clinical_detection_intervention_final_taxonomy_{lang}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def decision_figure(out: Path, lang: str) -> None:
    cn = lang == "cn"
    title = "临床检测与干预：互斥判定规则" if cn else "Clinical detection and intervention: assignment rules"
    questions = [
        ("1", "是否取得用于离体分析的诊断材料？" if cn else "Is diagnostic material acquired for ex-vivo analysis?", "1.3"),
        ("2", "是否有意施加扰动并解释诱发响应？" if cn else "Is a deliberate perturbation interpreted through its response?", "1.2"),
        ("3", "反馈是否改变下一次在体观察的采集配置？" if cn else "Does feedback change acquisition of the next in-vivo observation?", "1.1"),
    ]
    fig, ax = plt.subplots(figsize=(13.2, 6.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.04, 0.93, title, fontsize=21, fontweight="bold", color=INK)
    colours = {"1.1": PURPLE, "1.2": ORANGE, "1.3": GREEN}
    y_positions = [0.72, 0.46, 0.20]
    for (number, question, assignment), y in zip(questions, y_positions):
        ax.add_patch(FancyBboxPatch((0.04, y), 0.62, 0.15, boxstyle="round,pad=0.015,rounding_size=0.018", facecolor=PALE, edgecolor="#DED5E1"))
        ax.text(0.075, y + 0.075, number, fontsize=14, fontweight="bold", color=INK, va="center")
        ax.text(0.13, y + 0.075, question, fontsize=11, color=INK, va="center", wrap=True)
        ax.annotate("", xy=(0.73, y + 0.075), xytext=(0.66, y + 0.075), arrowprops={"arrowstyle": "->", "color": colours[assignment], "lw": 2})
        ax.add_patch(FancyBboxPatch((0.74, y + 0.015), 0.22, 0.12, boxstyle="round,pad=0.012,rounding_size=0.018", facecolor=colours[assignment], edgecolor="none"))
        ax.text(0.85, y + 0.075, assignment, color="white", fontsize=16, fontweight="bold", ha="center", va="center")
        if y != y_positions[-1]:
            ax.text(0.35, y - 0.055, "No ↓" if not cn else "否 ↓", color=MUTED, fontsize=9, ha="center")
    footer = (
        "若三个问题均为否：不作为完整具身诊断系统纳入；可保留为支撑技术。"
        if cn else
        "If all three answers are no, exclude from the complete embodied-system set or retain only as a supporting technology."
    )
    ax.text(0.04, 0.055, footer, fontsize=9.5, color=MUTED)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"clinical_detection_intervention_assignment_rules_{lang}.svg", bbox_inches="tight")
    fig.savefig(out / f"clinical_detection_intervention_assignment_rules_{lang}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    setup_fonts()
    rows = read_rows(args.taxonomy)
    for lang in ("cn", "en"):
        taxonomy_figure(rows, args.output_dir, lang)
        decision_figure(args.output_dir, lang)


if __name__ == "__main__":
    main()
