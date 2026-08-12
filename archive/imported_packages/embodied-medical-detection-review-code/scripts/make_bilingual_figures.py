#!/usr/bin/env python3
"""Create bilingual, publication-ready figures for embodied clinical detection.

The figures use the reproducible bibliometric corpus in data/bibliometrics.
Counts are shown as a high-precision core lower bound and a broader
abstract-supported sensitivity upper bound.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "bibliometrics"
OUT_DIR = ROOT / "outputs" / "08e9490e7d8f" / "embodied_detection_bilingual_figures_2026-08-06"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_DIR = ROOT / "tmp" / "08e9490e7d8f" / "fonts" / "package"
FONT_REGULAR = FONT_DIR / "NotoSansCJKsc-Regular.otf"
FONT_MEDIUM = FONT_DIR / "NotoSansCJKsc-Medium.otf"
FONT_BOLD = FONT_DIR / "NotoSansCJKsc-Bold.otf"

for font_path in (FONT_REGULAR, FONT_MEDIUM, FONT_BOLD):
    if font_path.exists():
        mpl.font_manager.fontManager.addfont(str(font_path))

FONT_FAMILY = mpl.font_manager.FontProperties(fname=str(FONT_REGULAR)).get_name() if FONT_REGULAR.exists() else "DejaVu Sans"

mpl.rcParams.update(
    {
        "font.family": FONT_FAMILY,
        "font.size": 9,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
        "grid.color": "#DCE3E8",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        # Convert SVG text to paths so Chinese labels remain portable.
        "svg.fonttype": "path",
    }
)


COLORS = {
    "A": "#157A8A",  # blue-teal
    "R": "#D9822B",  # amber
    "S": "#7357A6",  # violet
    "ink": "#1E2A32",
    "muted": "#60717C",
    "grid": "#DCE3E8",
    "paper": "#F7F9FA",
    "light": "#EEF3F5",
    "a1": "#176B87",
    "a2": "#2A9D8F",
    "other": "#8A99A3",
    "alert": "#C94C4C",
}


def mix_with_white(color: str, amount: float = 0.66) -> tuple[float, float, float]:
    rgb = np.array(mcolors.to_rgb(color))
    return tuple(rgb * (1 - amount) + np.ones(3) * amount)


def wrap(value: str, width: int) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False))


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    paths = []
    for ext, kwargs in (
        ("png", {"dpi": 600}),
        ("svg", {}),
        ("pdf", {}),
    ):
        path = OUT_DIR / f"{stem}.{ext}"
        tmp_path = path.with_name(f".{path.name}.writing")
        with tmp_path.open("wb") as handle:
            fig.savefig(handle, format=ext, bbox_inches="tight", pad_inches=0.08, **kwargs)
            handle.flush()
            os.fsync(handle.fileno())
        tmp_path.replace(path)
        paths.append(path)
    plt.close(fig)
    return paths


def footer(fig: plt.Figure, text: str, y: float = 0.012, size: float = 6.8) -> None:
    fig.text(0.015, y, text, ha="left", va="bottom", fontsize=size, color=COLORS["muted"])


def panel_label(ax: plt.Axes, label: str, x: float = -0.10, y: float = 1.08) -> None:
    ax.text(x, y, label, transform=ax.transAxes, ha="left", va="top", fontsize=13, fontweight="bold", color=COLORS["ink"])


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict, list[dict], list[dict]]:
    records = pd.read_csv(DATA_DIR / "included.csv")
    tasks = pd.read_json(DATA_DIR / "tasks.json")
    metadata = json.loads((DATA_DIR / "metadata.json").read_text(encoding="utf-8"))
    query_log = json.loads((DATA_DIR / "query_log.json").read_text(encoding="utf-8"))
    task_json = json.loads((DATA_DIR / "tasks.json").read_text(encoding="utf-8"))
    return records, tasks, metadata, query_log, task_json


RECORDS, TASKS, META, QUERY_LOG, TASK_JSON = load_data()
TASKS["core"] = TASKS["code"].map(META["core_task_counts"]).fillna(0).astype(int)
TASKS["expanded"] = TASKS["code"].map(META["task_counts"]).fillna(0).astype(int)
TASKS["expanded_only"] = TASKS["expanded"] - TASKS["core"]


def taxonomy_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    fig, ax = plt.subplots(figsize=(13.2, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    title = (
        "Action-defined taxonomy of embodied clinical detection"
        if is_en
        else "具身临床检测的动作定义型分类框架"
    )
    subtitle = (
        "The category is determined by what the agent physically changes to obtain diagnostic evidence."
        if is_en
        else "分类依据是智能体为获得诊断证据而主动改变的物理对象。"
    )
    ax.text(0.02, 0.958, title, fontsize=19, fontweight="bold", color=COLORS["ink"], va="top")
    ax.text(0.02, 0.905, subtitle, fontsize=9.5, color=COLORS["muted"], va="top")

    cols = [0.02, 0.235, 0.515, 0.745]
    widths = [0.195, 0.26, 0.21, 0.235]
    headers = (
        ["Category", "Agent action / action object", "Diagnostic evidence", "Representative tasks"]
        if is_en
        else ["类别", "智能体动作 / 动作对象", "诊断证据", "代表性任务"]
    )
    for x, w, header in zip(cols, widths, headers):
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.805), w, 0.065,
                boxstyle="round,pad=0.004,rounding_size=0.008",
                facecolor="#E7EDF0", edgecolor="none",
            )
        )
        ax.text(x + 0.012, 0.838, header, fontsize=9.1, fontweight="bold", color=COLORS["ink"], va="center")

    if is_en:
        rows = [
            (
                "A  Active observational\nsensing",
                "Change sensor viewpoint, position, orientation, contact state, or scan path",
                "New images, visual/acoustic observations, or physiological signals",
                "Robotic ultrasound; endoscopic search; OCT; dermoscopy; auscultation; otoscopy; optical/spectral/thermal scanning",
            ),
            (
                "R  Response-based\ninteractive diagnosis",
                "Apply a controlled mechanical, electromagnetic, or physiological stimulus",
                "Mechanical, physiological, or functional response",
                "Robotic palpation; elastography; joint provocation; percussion; reflex testing; TMS; nerve-response testing; tonometry",
            ),
            (
                "S  Sample-based\ninteractive diagnosis",
                "Puncture, aspirate, swab, or excise a target tissue or body fluid",
                "Ex vivo pathology, biochemical, microbiological, or molecular result",
                "Venipuncture; swab collection; bronchoscopic biopsy/TBNA; prostate biopsy; core-needle biopsy; FNA; CSF or marrow sampling",
            ),
        ]
    else:
        rows = [
            (
                "A  主动观察式检测",
                "改变传感器视点、位置、方向、接触状态或扫描路径",
                "新的影像、视觉/声学观察或生理信号",
                "机器人超声；内镜搜索；OCT；皮肤镜；听诊；耳镜；光谱/热成像扫描",
            ),
            (
                "R  响应式交互检测",
                "施加可控的机械、电磁或生理刺激",
                "力学、生理或功能响应",
                "机器人触诊；弹性检测；关节激发；叩诊；腱反射；TMS；神经刺激—响应；眼压检测",
            ),
            (
                "S  采样式交互检测",
                "对目标组织或体液实施穿刺、抽吸、拭子采集或切取",
                "离体病理、生化、微生物或分子结果",
                "机器人采血；拭子采样；支气管镜活检/TBNA；前列腺活检；粗针活检；FNA；脑脊液/骨髓采样",
            ),
        ]

    ys = [0.59, 0.355, 0.12]
    for code, row, y in zip(("A", "R", "S"), rows, ys):
        color = COLORS[code]
        ax.add_patch(
            FancyBboxPatch(
                (0.02, y), 0.96, 0.19,
                boxstyle="round,pad=0.006,rounding_size=0.012",
                facecolor=mix_with_white(color, 0.92), edgecolor=mix_with_white(color, 0.55), linewidth=0.9,
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (cols[0] + 0.004, y + 0.012), widths[0] - 0.008, 0.166,
                boxstyle="round,pad=0.006,rounding_size=0.010",
                facecolor=color, edgecolor="none",
            )
        )
        ax.text(cols[0] + 0.016, y + 0.095, row[0], fontsize=10.5, fontweight="bold", color="white", va="center")
        wrap_widths = [38 if is_en else 20, 32 if is_en else 17, 42 if is_en else 24]
        for col_idx, (value, ww) in enumerate(zip(row[1:], wrap_widths), start=1):
            ax.text(cols[col_idx] + 0.012, y + 0.095, wrap(value, ww), fontsize=8.6, color=COLORS["ink"], va="center", linespacing=1.35)
        for x in (cols[1] - 0.01, cols[2] - 0.01, cols[3] - 0.01):
            ax.plot([x, x], [y + 0.018, y + 0.172], color="#D5DEE3", lw=0.8)

    note = (
        "Boundary rule: classify by the primary evidence-generating action; assign one primary task per work when actions overlap."
        if is_en
        else "边界规则：按主要的证据生成动作分类；当一项工作包含多个动作时，仅分配一个主要任务。"
    )
    ax.text(0.02, 0.025, note, fontsize=7.5, color=COLORS["muted"], va="bottom")
    return save_figure(fig, f"Fig1_taxonomy_{lang}")


def class_workload_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    order = ["A", "S", "R"]
    core = [META["core_class_counts"][c] for c in order]
    expanded = [META["class_counts"][c] for c in order]
    added = [e - c for c, e in zip(core, expanded)]
    labels_en = {
        "A": "Active observational sensing",
        "R": "Response-based interactive diagnosis",
        "S": "Sample-based interactive diagnosis",
    }
    labels_zh = {"A": "主动观察式检测", "R": "响应式交互检测", "S": "采样式交互检测"}
    labels = [f"{c}  {(labels_en if is_en else labels_zh)[c]}" for c in order]

    fig, ax = plt.subplots(figsize=(10.6, 5.7))
    y = np.arange(len(order))[::-1]
    for idx, code in enumerate(order):
        yy = y[idx]
        ax.barh(yy, core[idx], height=0.48, color=COLORS[code], edgecolor="none")
        ax.barh(yy, added[idx], left=core[idx], height=0.48, color=mix_with_white(COLORS[code], 0.70), edgecolor="none")
        ax.text(core[idx] - 10, yy, f"{core[idx]:,}", ha="right", va="center", color="white", fontweight="bold", fontsize=9)
        ax.text(expanded[idx] + 18, yy, f"{expanded[idx]:,}", ha="left", va="center", color=COLORS["ink"], fontweight="bold", fontsize=9.5)
        ax.text(expanded[idx] + 18, yy - 0.16, "upper" if is_en else "上界", ha="left", va="center", color=COLORS["muted"], fontsize=6.8)

    ax.set_yticks(y, labels)
    ax.set_xlim(0, max(expanded) * 1.14)
    ax.set_xlabel("Number of deduplicated records" if is_en else "去重文献记录数")
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)
    title = "Cumulative literature workload by embodied diagnostic mode" if is_en else "具身医学检测三大方向的累计文献工作量"
    subtitle = (
        "High-precision core lower bound and abstract-supported sensitivity upper bound"
        if is_en
        else "高精度核心下界与摘要支持的敏感性上界"
    )
    ax.set_title(title, loc="left", fontsize=16, pad=30, color=COLORS["ink"])
    ax.text(0, 1.07, subtitle, transform=ax.transAxes, fontsize=9, color=COLORS["muted"], ha="left")

    legend = [
        Rectangle((0, 0), 1, 1, facecolor=COLORS["ink"], alpha=0.9, label="Core lower bound" if is_en else "核心下界"),
        Rectangle((0, 0), 1, 1, facecolor="#C9D4DA", label="Additional expanded records" if is_en else "扩展集新增记录"),
    ]
    ax.legend(handles=legend, frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(1, 1.16))
    note = (
        f"Core n={sum(core):,}; expanded upper bound n={sum(expanded):,}. Searches: OpenAlex + Europe PMC; cutoff 6 Aug 2026."
        if is_en
        else f"核心集 n={sum(core):,}；扩展上界 n={sum(expanded):,}。检索库：OpenAlex + Europe PMC；截至 2026-08-06。"
    )
    footer(fig, note)
    fig.subplots_adjust(left=0.27, right=0.93, top=0.78, bottom=0.17)
    return save_figure(fig, f"Fig2_class_workload_{lang}")


def all_tasks_workload_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    fig, axes = plt.subplots(1, 3, figsize=(16.4, 9.2), gridspec_kw={"wspace": 0.62})
    class_names = {
        "EN": {"A": "Active observational sensing", "R": "Response-based interactive diagnosis", "S": "Sample-based interactive diagnosis"},
        "ZH": {"A": "主动观察式检测", "R": "响应式交互检测", "S": "采样式交互检测"},
    }[lang]
    xlims = {"A": 560, "R": 78, "S": 245}
    for ax, code, letter in zip(axes, ("A", "R", "S"), ("a", "b", "c")):
        sub = TASKS[TASKS["class_code"].eq(code)].copy()
        sub = sub.sort_values(["core", "expanded", "code"], ascending=[False, False, True])
        ypos = np.arange(len(sub))[::-1]
        color = COLORS[code]
        ax.barh(ypos, sub["core"], height=0.56, color=color, edgecolor="none", zorder=3)
        ax.barh(ypos, sub["expanded_only"], left=sub["core"], height=0.56, color=mix_with_white(color, 0.70), edgecolor="none", zorder=2)
        label_field = "task_en" if is_en else "task_zh"
        labels = [f"{row.code}  {wrap(row[label_field], 27 if is_en else 15)}" for _, row in sub.iterrows()]
        ax.set_yticks(ypos, labels)
        ax.tick_params(axis="y", length=0, pad=5)
        ax.set_xlim(0, xlims[code])
        ax.xaxis.grid(True)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
        ax.set_xlabel("Records" if is_en else "文献记录数")
        totals = META["class_counts"][code]
        cores = META["core_class_counts"][code]
        ax.set_title(
            f"{code}  {class_names[code]}\n{('core' if is_en else '核心')} n={cores:,}  |  {('upper' if is_en else '上界')} n={totals:,}",
            loc="left", fontsize=11.2, color=COLORS["ink"], pad=14,
        )
        panel_label(ax, letter, x=-0.25, y=1.075)
        for yy, (_, row) in zip(ypos, sub.iterrows()):
            c, e = int(row["core"]), int(row["expanded"])
            x = e + xlims[code] * 0.014
            ax.text(x, yy, f"{c}–{e}" if c != e else f"{c}", va="center", ha="left", fontsize=7.2, color=COLORS["ink"])

    title = "Workload across all 24 embodied clinical detection tasks" if is_en else "具身医学检测 24 个细分任务的累计工作量"
    subtitle = (
        "Each label reports core lower bound–expanded upper bound; zero-count task families remain visible."
        if is_en
        else "每个标签表示“核心下界–扩展上界”；检索后为零的任务仍保留显示。"
    )
    fig.suptitle(title, x=0.02, y=0.965, ha="left", fontsize=18, fontweight="bold", color=COLORS["ink"])
    fig.text(0.02, 0.922, subtitle, ha="left", fontsize=9, color=COLORS["muted"])
    legend = [
        Rectangle((0, 0), 1, 1, facecolor="#485962", label="Core lower bound" if is_en else "核心下界"),
        Rectangle((0, 0), 1, 1, facecolor="#CFD9DE", label="Additional expanded records" if is_en else "扩展集新增记录"),
    ]
    fig.legend(handles=legend, frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(0.985, 0.957))
    note = (
        "Counts are search-derived publication records, not registered clinical trials or deployed systems. One primary task was assigned per work. Cutoff: 6 Aug 2026."
        if is_en
        else "计数单位为检索得到的文献记录，并非注册临床试验或已部署系统；每篇工作仅归入一个主要任务。截至 2026-08-06。"
    )
    footer(fig, note)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.84, bottom=0.12)
    return save_figure(fig, f"Fig3_all_tasks_workload_{lang}")


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#5D6D76", rad: float = 0.0, lw: float = 1.7) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=2,
        shrinkB=2,
        zorder=2,
    )
    ax.add_patch(arrow)


def flow_box(ax: plt.Axes, xy: tuple[float, float], wh: tuple[float, float], number: str, title: str, body: str, color: str) -> None:
    x, y = xy
    w, h = wh
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.008,rounding_size=0.018",
            facecolor="white", edgecolor=mix_with_white(color, 0.32), linewidth=1.35, zorder=3,
        )
    )
    ax.add_patch(plt.Circle((x + 0.028, y + h - 0.035), 0.020, facecolor=color, edgecolor="none", zorder=4))
    ax.text(x + 0.028, y + h - 0.035, number, color="white", ha="center", va="center", fontsize=8, fontweight="bold", zorder=5)
    ax.text(x + 0.057, y + h - 0.033, title, color=COLORS["ink"], ha="left", va="center", fontsize=10.2, fontweight="bold", zorder=5)
    ax.text(x + 0.020, y + h - 0.074, body, color=COLORS["muted"], ha="left", va="top", fontsize=7.8, linespacing=1.35, zorder=5)


def active_loop_figure() -> list[Path]:
    fig, ax = plt.subplots(figsize=(14.2, 8.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.035, 0.958, "Closed-loop active observational sensing", fontsize=20, fontweight="bold", color=COLORS["ink"], va="top")
    ax.text(
        0.035,
        0.903,
        "The agent actively changes how and where it senses to maximize diagnostic value under safety constraints.",
        fontsize=10,
        color=COLORS["muted"],
        va="top",
    )

    top_y, bottom_y = 0.57, 0.24
    w, h = 0.205, 0.205
    xs = [0.035, 0.282, 0.529, 0.776]
    flow_box(ax, (xs[0], top_y), (w, h), "1", "Current observation", "Image, video, acoustic or\nphysiological signal", COLORS["a1"])
    flow_box(ax, (xs[1], top_y), (w, h), "2", "State assessment", "Target visibility\nCoverage\nImage / signal quality\nUncertainty", COLORS["a1"])
    flow_box(ax, (xs[2], top_y), (w, h), "3", "Next-best sensing action", "Viewpoint • position • orientation\nContact state • scan path", COLORS["a2"])
    flow_box(ax, (xs[3], top_y), (w, h), "4", "Safety gate + execution", "Force / speed limits\nWorkspace and collision checks\nPatient motion monitoring", COLORS["R"])
    flow_box(ax, (xs[2], bottom_y), (w, h), "5", "New observation", "Acquire, register and update\nthe patient / target model", COLORS["a2"])
    flow_box(ax, (xs[1], bottom_y), (w, h), "6", "Decision policy", "Continue • rescan\nStop • hand off", COLORS["A"])

    add_arrow(ax, (xs[0] + w, top_y + h / 2), (xs[1], top_y + h / 2))
    add_arrow(ax, (xs[1] + w, top_y + h / 2), (xs[2], top_y + h / 2))
    add_arrow(ax, (xs[2] + w, top_y + h / 2), (xs[3], top_y + h / 2))
    add_arrow(ax, (xs[3] + w / 2, top_y), (xs[2] + w / 2, bottom_y + h), rad=0.16)
    add_arrow(ax, (xs[2], bottom_y + h / 2), (xs[1] + w, bottom_y + h / 2))
    add_arrow(ax, (xs[1], bottom_y + h / 2), (xs[0] + w / 2, top_y), rad=-0.34, color=COLORS["A"], lw=2.0)
    ax.text(0.102, 0.455, "CONTINUE / RESCAN", fontsize=7.2, fontweight="bold", color=COLORS["A"], rotation=90, ha="center", va="center")

    ax.add_patch(
        FancyBboxPatch((0.035, 0.10), 0.205, 0.082, boxstyle="round,pad=0.006,rounding_size=0.012", facecolor="#F2F5F6", edgecolor="#BAC7CD", linewidth=0.9)
    )
    ax.text(0.1375, 0.142, "Stop + diagnostic report", ha="center", va="center", fontsize=8.5, fontweight="bold", color=COLORS["ink"])
    ax.add_patch(
        FancyBboxPatch((0.282, 0.10), 0.205, 0.082, boxstyle="round,pad=0.006,rounding_size=0.012", facecolor=mix_with_white(COLORS["alert"], 0.90), edgecolor=mix_with_white(COLORS["alert"], 0.45), linewidth=0.9)
    )
    ax.text(0.3845, 0.142, "Human handoff", ha="center", va="center", fontsize=8.5, fontweight="bold", color=COLORS["alert"])
    add_arrow(ax, (xs[1] + w * 0.35, bottom_y), (0.1375, 0.182), rad=0.18, color="#7B8B94", lw=1.2)
    add_arrow(ax, (xs[1] + w * 0.68, bottom_y), (0.3845, 0.182), rad=-0.05, color=COLORS["alert"], lw=1.2)

    ax.add_patch(
        FancyBboxPatch((0.535, 0.088), 0.446, 0.095, boxstyle="round,pad=0.009,rounding_size=0.014", facecolor="#EAF4F4", edgecolor="#B8DADA", linewidth=0.8)
    )
    ax.text(0.557, 0.152, "Optimization objective", fontsize=8.2, fontweight="bold", color=COLORS["A"], va="center")
    ax.text(0.557, 0.119, "Higher quality  •  more complete coverage  •  greater diagnostic value", fontsize=8.4, color=COLORS["ink"], va="center")

    footer(fig, "Generic control architecture; task-specific implementations may use rule-based, optimization-based, learning-based, or clinician-supervised policies.")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.04)
    return save_figure(fig, "Fig4_active_observational_closed_loop_EN")


def active_period_matrix(core_active: pd.DataFrame) -> tuple[list[str], np.ndarray]:
    bins = [
        (1900, 2004, "≤2004"),
        (2005, 2009, "2005–09"),
        (2010, 2014, "2010–14"),
        (2015, 2019, "2015–19"),
        (2020, 2024, "2020–24"),
        (2025, 2025, "2025"),
        (2026, 2026, "2026 YTD"),
    ]
    matrix = np.zeros((7, len(bins)), dtype=int)
    for i, task in enumerate([f"A{x}" for x in range(1, 8)]):
        for j, (lo, hi, _) in enumerate(bins):
            matrix[i, j] = int(((core_active["primary_task"] == task) & core_active["year"].between(lo, hi)).sum())
    return [b[2] for b in bins], matrix


def active_landscape_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    active = RECORDS[RECORDS["class_code"].eq("A")].copy()
    core_active = active[active["evidence_tier"].str.startswith("Core")].copy()
    active_tasks = TASKS[TASKS["class_code"].eq("A")].set_index("code").loc[[f"A{x}" for x in range(1, 8)]].reset_index()

    fig = plt.figure(figsize=(14.8, 10.6))
    outer = fig.add_gridspec(2, 2, left=0.065, right=0.97, bottom=0.095, top=0.86, wspace=0.28, hspace=0.35)
    left_top = outer[0, 0].subgridspec(2, 1, height_ratios=[0.44, 0.56], hspace=0.15)
    ax_a1 = fig.add_subplot(left_top[0, 0])
    ax_a2 = fig.add_subplot(left_top[1, 0])
    ax_b = fig.add_subplot(outer[0, 1])
    ax_c = fig.add_subplot(outer[1, 0])
    ax_d = fig.add_subplot(outer[1, 1])

    title = "Active observational sensing: workload, trajectory and field structure" if is_en else "主动观察式检测：工作量、发展轨迹与领域结构"
    subtitle = (
        "Seven action-defined subtasks; high-precision core lower bound and abstract-supported sensitivity upper bound"
        if is_en
        else "7 个动作定义型子任务；高精度核心下界与摘要支持的敏感性上界"
    )
    fig.suptitle(title, x=0.04, y=0.975, ha="left", fontsize=19, fontweight="bold", color=COLORS["ink"])
    fig.text(0.04, 0.93, subtitle, ha="left", fontsize=9.5, color=COLORS["muted"])

    # Panel a: separate scales preserve visibility of emerging tasks.
    label_field = "task_en" if is_en else "task_zh"
    big = active_tasks.iloc[:2].copy()
    small = active_tasks.iloc[2:].copy()
    for ax, sub, xlim in ((ax_a1, big, 545), (ax_a2, small, 22)):
        ypos = np.arange(len(sub))[::-1]
        ax.barh(ypos, sub["core"], height=0.56, color=COLORS["A"], edgecolor="none", zorder=3)
        ax.barh(ypos, sub["expanded_only"], left=sub["core"], height=0.56, color=mix_with_white(COLORS["A"], 0.70), edgecolor="none", zorder=2)
        ax.set_yticks(ypos, [f"{row.code}  {wrap(row[label_field], 29 if is_en else 15)}" for _, row in sub.iterrows()])
        ax.set_xlim(0, xlim)
        ax.xaxis.grid(True)
        ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=5)
        for yy, (_, row) in zip(ypos, sub.iterrows()):
            c, e = int(row["core"]), int(row["expanded"])
            ax.text(e + xlim * 0.018, yy, f"{c}–{e}" if c != e else str(c), ha="left", va="center", fontsize=7.5, fontweight="bold", color=COLORS["ink"])
    ax_a1.set_title("Cumulative workload by subtask" if is_en else "各子任务累计工作量", loc="left", fontsize=12, pad=13)
    panel_label(ax_a1, "a", x=-0.12, y=1.28)
    ax_a1.set_xlabel("")
    ax_a1.tick_params(axis="x", labelbottom=False)
    ax_a1.spines["bottom"].set_visible(False)
    ax_a2.set_xlabel("Records (separate scales for established and emerging tasks)" if is_en else "文献记录数（成熟任务与新兴任务采用独立尺度）")
    legend = [
        Rectangle((0, 0), 1, 1, facecolor=COLORS["A"], label="Core lower bound" if is_en else "核心下界"),
        Rectangle((0, 0), 1, 1, facecolor=mix_with_white(COLORS["A"], 0.70), label="Additional expanded records" if is_en else "扩展集新增记录"),
    ]
    fig.legend(handles=legend, frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(0.968, 0.935), fontsize=7.2)

    # Panel b: annual core publication trajectory.
    years = np.arange(2005, 2027)
    series = {}
    for key, mask in {
        "A1": core_active["primary_task"].eq("A1"),
        "A2": core_active["primary_task"].eq("A2"),
        "A3–A7": core_active["primary_task"].isin(["A3", "A4", "A5", "A6", "A7"]),
    }.items():
        series[key] = np.array([int((mask & core_active["year"].eq(y)).sum()) for y in years])
    line_colors = {"A1": COLORS["a1"], "A2": COLORS["a2"], "A3–A7": COLORS["other"]}
    line_labels = {
        "A1": "A1 Ultrasound" if is_en else "A1 机器人超声",
        "A2": "A2 Endoscopy" if is_en else "A2 机器人内镜",
        "A3–A7": "A3–A7 Emerging tasks" if is_en else "A3–A7 新兴任务",
    }
    for key, values in series.items():
        ax_b.plot(years[:-1], values[:-1], color=line_colors[key], lw=2.2, marker="o", markersize=2.7, label=line_labels[key])
        ax_b.plot(years[-2:], values[-2:], color=line_colors[key], lw=1.8, ls="--", marker="o", markersize=3.2)
    ax_b.axvspan(2020.5, 2025.5, color="#EAF1F4", alpha=0.85, zorder=0)
    ax_b.text(2023, ax_b.get_ylim()[1] * 0.94, "2021–2025", ha="center", va="top", fontsize=7, color=COLORS["muted"])
    ax_b.axvline(2025.5, color="#A5B2B9", lw=0.9, ls=":")
    ax_b.text(2025.68, max(max(v) for v in series.values()) * 0.72, "2026 YTD", fontsize=7, color=COLORS["muted"], rotation=90, va="center")
    ax_b.set_xlim(2005, 2026.3)
    ax_b.set_xticks([2005, 2010, 2015, 2020, 2025, 2026])
    ax_b.set_ylabel("Core records per year" if is_en else "每年核心文献数")
    ax_b.yaxis.grid(True)
    ax_b.set_axisbelow(True)
    ax_b.set_title("Annual publication trajectory" if is_en else "年度发表轨迹", loc="left", fontsize=12, pad=13)
    panel_label(ax_b, "b", x=-0.10, y=1.12)
    ax_b.legend(frameon=False, loc="upper left", fontsize=7.5)

    # Panel c: exact period counts with log-scaled color to reveal sparse tasks.
    periods, matrix = active_period_matrix(core_active)
    log_matrix = np.log1p(matrix)
    im = ax_c.imshow(log_matrix, cmap="Blues", aspect="auto", vmin=0, vmax=np.log1p(matrix.max()))
    ylabels = [
        f"A{i}  {active_tasks.loc[active_tasks['code'].eq(f'A{i}'), label_field].iloc[0]}"
        for i in range(1, 8)
    ]
    ax_c.set_yticks(np.arange(7), [wrap(v, 29 if is_en else 16) for v in ylabels])
    ax_c.set_xticks(np.arange(len(periods)), periods, rotation=35, ha="right")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            color = "white" if log_matrix[i, j] > np.log1p(matrix.max()) * 0.52 else COLORS["ink"]
            ax_c.text(j, i, str(value), ha="center", va="center", fontsize=7.1, color=color, fontweight="bold" if value else "normal")
    ax_c.set_title("Core workload by publication period" if is_en else "按发表时期分解的核心工作量", loc="left", fontsize=12, pad=13)
    panel_label(ax_c, "c", x=-0.12, y=1.13)
    ax_c.tick_params(length=0)
    for spine in ax_c.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax_c, orientation="horizontal", fraction=0.055, pad=0.18, aspect=30)
    ticks = [0, 1, 5, 20, 50, 100]
    cbar.set_ticks([np.log1p(x) for x in ticks])
    cbar.set_ticklabels([str(x) for x in ticks])
    cbar.set_label("Core record count (log-scaled color; cell labels are exact)" if is_en else "核心文献数（颜色为对数尺度；单元格数字为精确计数）", fontsize=7.3)
    cbar.outline.set_visible(False)

    # Panel d: concentration and recency structure.
    ax_d.set_xlim(0, 100)
    ax_d.set_ylim(0, 1)
    ax_d.axis("off")
    ax_d.set_title("Field concentration and recency" if is_en else "领域集中度与时间结构", loc="left", fontsize=12, pad=13)
    panel_label(ax_d, "d", x=-0.10, y=1.13)
    n_core = len(core_active)
    n_upper = len(active)
    task_counts = core_active["primary_task"].value_counts()
    task_parts = [task_counts.get("A1", 0), task_counts.get("A2", 0), n_core - task_counts.get("A1", 0) - task_counts.get("A2", 0)]
    task_pcts = [x / n_core * 100 for x in task_parts]
    earlier = int((core_active["year"] <= 2020).sum())
    recent = int(core_active["year"].between(2021, 2025).sum())
    ytd = int(core_active["year"].eq(2026).sum())
    time_parts = [earlier, recent, ytd]
    time_pcts = [x / n_core * 100 for x in time_parts]

    ax_d.text(0, 0.92, f"{n_core:,}", fontsize=25, fontweight="bold", color=COLORS["A"], va="top")
    ax_d.text(16, 0.905, "core records" if is_en else "篇核心文献", fontsize=8.2, color=COLORS["muted"], va="top")
    ax_d.text(52, 0.92, f"{n_upper:,}", fontsize=25, fontweight="bold", color=mix_with_white(COLORS["A"], 0.10), va="top")
    ax_d.text(71, 0.905, "expanded upper" if is_en else "篇扩展上界", fontsize=8.2, color=COLORS["muted"], va="top")

    def stacked_bar(y: float, values: list[float], colors: list[str], labels: list[str], title_text: str) -> None:
        ax_d.text(0, y + 0.095, title_text, fontsize=8.4, fontweight="bold", color=COLORS["ink"], va="bottom")
        left = 0.0
        for value, color, label in zip(values, colors, labels):
            ax_d.add_patch(Rectangle((left, y), value, 0.105, facecolor=color, edgecolor="white", linewidth=0.8))
            if value >= 8:
                ax_d.text(left + value / 2, y + 0.0525, f"{label}\n{value:.1f}%", ha="center", va="center", fontsize=7.1, color="white" if mcolors.rgb_to_hsv(mcolors.to_rgb(color))[2] < 0.78 else COLORS["ink"], fontweight="bold")
            elif value >= 4:
                ax_d.text(left + value / 2, y + 0.0525, f"{value:.1f}%", ha="center", va="center", fontsize=6.2, color="white", fontweight="bold")
            left += value

    stacked_bar(
        0.50,
        task_pcts,
        [COLORS["a1"], COLORS["a2"], COLORS["other"]],
        ["A1", "A2", "A3–A7"],
        "Core task mix" if is_en else "核心集任务构成",
    )
    stacked_bar(
        0.22,
        time_pcts,
        ["#90A1AA", COLORS["A"], "#9CC9CD"],
        ["≤2020", "2021–25", "2026\nYTD"],
        "Core publication-time mix" if is_en else "核心集发表时间构成",
    )
    top2 = (task_parts[0] + task_parts[1]) / n_core * 100
    rec_share = recent / n_core * 100
    earlier_five = int(core_active["year"].between(2016, 2020).sum())
    recent_five = int(core_active["year"].between(2021, 2025).sum())
    five_year_ratio = recent_five / earlier_five
    ax_d.text(0, 0.04, f"Top two tasks = {top2:.1f}% of the core corpus" if is_en else f"前两项任务占核心集 {top2:.1f}%", fontsize=8.4, fontweight="bold", color=COLORS["ink"])
    ax_d.text(0, -0.015, f"Five-year workload: {earlier_five} → {recent_five} ({five_year_ratio:.2f}×)" if is_en else f"五年期工作量：{earlier_five} → {recent_five}（{five_year_ratio:.2f} 倍）", fontsize=7.6, color=COLORS["muted"])
    ax_d.text(0, -0.075, f"2021–2025 = {rec_share:.1f}%  |  2026 is partial-year" if is_en else f"2021–2025 占 {rec_share:.1f}%  |  2026 为不完整年度", fontsize=7.6, color=COLORS["muted"])

    note = (
        "Search-derived records, not deployed systems. Core: task and embodiment explicit in title; expanded upper: qualifying evidence may appear in abstract. OpenAlex + Europe PMC; DOI/title deduplication; one primary task/work; cutoff 6 Aug 2026."
        if is_en
        else "计数为检索文献而非已部署系统。核心集：标题明确包含具身动作与任务；扩展上界：符合条件的证据可位于摘要。OpenAlex + Europe PMC；DOI/规范化标题去重；每篇仅归一个主要任务；截至 2026-08-06。"
    )
    footer(fig, note, y=0.018, size=6.5)
    return save_figure(fig, f"Fig5_active_observational_landscape_{lang}")


def export_source_data() -> None:
    task_cols = [
        "code", "class_code", "class_en", "class_zh", "task_en", "task_zh",
        "core", "expanded", "expanded_only", "definition", "exclusions",
    ]
    TASKS[task_cols].to_csv(OUT_DIR / "source_data_all_task_counts_bilingual.csv", index=False, encoding="utf-8-sig")

    active = RECORDS[RECORDS["class_code"].eq("A")].copy()
    core = active[active["evidence_tier"].str.startswith("Core")].copy()
    years = range(int(active["year"].min()), 2027)
    rows = []
    for year in years:
        for task in [f"A{x}" for x in range(1, 8)]:
            rows.append(
                {
                    "year": year,
                    "year_status": "YTD through 2026-08-06" if year == 2026 else "full year",
                    "task_code": task,
                    "task_en": TASKS.loc[TASKS["code"].eq(task), "task_en"].iloc[0],
                    "task_zh": TASKS.loc[TASKS["code"].eq(task), "task_zh"].iloc[0],
                    "core_records": int(((core["year"] == year) & (core["primary_task"] == task)).sum()),
                    "expanded_upper_records": int(((active["year"] == year) & (active["primary_task"] == task)).sum()),
                }
            )
    pd.DataFrame(rows).to_csv(OUT_DIR / "source_data_active_annual_counts_bilingual.csv", index=False, encoding="utf-8-sig")

    record_cols = [
        "title", "year", "publication_date", "doi", "pmid", "url", "venue",
        "cited_by_count", "primary_task", "task_en", "task_zh", "evidence_tier",
        "source_dbs", "source_ids",
    ]
    active[record_cols].sort_values(["primary_task", "year", "title"]).to_csv(
        OUT_DIR / "active_observational_records_1002.csv", index=False, encoding="utf-8-sig"
    )

    active_queries = pd.DataFrame([row for row in QUERY_LOG if row["class_code"] == "A"])
    active_queries.to_csv(OUT_DIR / "active_observational_search_queries.csv", index=False, encoding="utf-8-sig")

    core_counts = core["primary_task"].value_counts()
    summary = pd.DataFrame(
        [
            ["Deduplicated candidates across all classes", "三大类去重候选记录", META["deduplicated_candidates"], "records"],
            ["All-class core corpus", "三大类核心文献集", sum(META["core_class_counts"].values()), "records"],
            ["All-class expanded upper bound", "三大类扩展上界", sum(META["class_counts"].values()), "records"],
            ["Active-observation core corpus", "主动观察核心文献集", len(core), "records"],
            ["Active-observation expanded upper bound", "主动观察扩展上界", len(active), "records"],
            ["A1+A2 share of active core", "A1+A2 占主动观察核心集比例", (core_counts.get("A1", 0) + core_counts.get("A2", 0)) / len(core) * 100, "%"],
            ["2021–2025 share of active core", "2021–2025 占主动观察核心集比例", core["year"].between(2021, 2025).mean() * 100, "%"],
            ["2016–2020 active core", "2016–2020 主动观察核心文献", int(core["year"].between(2016, 2020).sum()), "records"],
            ["2021–2025 active core", "2021–2025 主动观察核心文献", int(core["year"].between(2021, 2025).sum()), "records"],
            ["Five-year workload ratio (2021–2025 / 2016–2020)", "五年期工作量倍数（2021–2025 / 2016–2020）", core["year"].between(2021, 2025).sum() / core["year"].between(2016, 2020).sum(), "ratio"],
            ["2026 YTD active core", "2026 年截至检索日的主动观察核心文献", int(core["year"].eq(2026).sum()), "records"],
        ],
        columns=["metric_en", "metric_zh", "value", "unit"],
    )
    summary.to_csv(OUT_DIR / "summary_statistics_bilingual.csv", index=False, encoding="utf-8-sig")

    shutil.copy2(DATA_DIR / "metadata.json", OUT_DIR / "bibliometric_metadata.json")
    shutil.copy2(DATA_DIR / "tasks.json", OUT_DIR / "task_definitions_bilingual.json")


def write_documentation() -> None:
    captions = """# Figure captions / 图注

## Fig. 1 — Taxonomy

**EN.** Action-defined taxonomy of embodied clinical detection. Active observational sensing changes the sensor configuration to obtain a new observation; response-based interactive diagnosis applies a controlled stimulus and interprets the response; sample-based interactive diagnosis obtains tissue or body fluid for ex vivo analysis. When a work contains multiple actions, it is assigned to the primary evidence-generating task.

**中.** 具身临床检测的动作定义型分类。主动观察式检测改变传感器配置以获得新的观察；响应式交互检测施加可控刺激并解释响应；采样式交互检测获取组织或体液并进行离体分析。当一项工作包含多个动作时，按主要证据生成任务进行唯一归类。

## Fig. 2 — Workload by major class

**EN.** Cumulative literature workload across the three embodied diagnostic modes. Dark segments denote the high-precision title-explicit core lower bound; pale segments denote additional records in the abstract-supported sensitivity set, and the bar endpoint is the expanded upper bound. Core: active observation 427, response-based interaction 98, sample-based interaction 277 (total 802). Expanded upper bound: 1,002, 143 and 316, respectively (total 1,461).

**中.** 三类具身医学检测的累计文献工作量。深色部分表示标题明确的高精度核心下界；浅色部分表示摘要支持的扩展集新增记录，条形末端为扩展上界。核心集：主动观察 427、响应式交互 98、采样式交互 277（合计 802）；扩展上界分别为 1,002、143、316（合计 1,461）。

## Fig. 3 — All task families

**EN.** Cumulative workload across all 24 action-defined task families. Labels report the core lower bound–expanded upper bound. Zero-count families are retained to distinguish an empty search result from an omitted category. Panels use class-specific horizontal scales; cross-class totals should therefore be compared using Fig. 2.

**中.** 24 个动作定义型任务的累计工作量。标签显示“核心下界–扩展上界”；检索计数为零的任务仍予保留，以区分“无检索结果”和“未纳入分类”。三个分面使用各自的横轴尺度，跨大类总量比较应以图 2 为准。

## Fig. 4 — Active observational sensing loop

**EN.** Generic closed-loop architecture for active observational sensing. From the current image or signal, the agent assesses target visibility, coverage, image or signal quality and uncertainty; selects the next viewpoint, pose, contact state or scan path; passes a safety gate; executes the action; acquires and registers a new observation; and then continues, rescans, stops or hands control to a human. The policy objective is to increase diagnostic value while satisfying safety constraints.

**中.** 主动观察式检测的一般闭环架构。智能体根据当前影像或信号评估目标可见性、覆盖度、图像/信号质量和不确定性，选择下一视点、位姿、接触状态或扫描路径，通过安全门控后执行，获取并配准新观察，随后继续、复扫、停止或转交人工；策略目标是在满足安全约束的前提下提高诊断价值。

## Fig. 5 — Active observational sensing landscape

**EN.** Workload, trajectory and field structure of active observational sensing. (a) Core lower bound and expanded upper bound for all seven subtasks; separate horizontal scales preserve visibility of sparse emerging tasks. (b) Annual core records from 2005 to 2026; the dashed final segment and “YTD” label indicate that 2026 is incomplete. (c) Exact core counts by publication period; color is log-scaled only to reveal low-volume task families. (d) Concentration and recency: robotic ultrasound and robotic endoscopy jointly account for 94.6% of the 427-record core corpus, while 58.8% of core records appeared in 2021–2025. Equal-length five-year workload increased from 74 records in 2016–2020 to 251 in 2021–2025 (3.39×). The expanded sensitivity set contains 1,002 records.

**中.** 主动观察式检测的工作量、发展轨迹与领域结构。（a）七个子任务的核心下界与扩展上界；成熟任务和低数量新兴任务采用独立横轴尺度，以保持可见性。（b）2005–2026 年核心文献年度轨迹；最后一段虚线及“YTD”说明 2026 年为不完整年度。（c）各发表时期的精确核心计数；颜色采用对数尺度仅用于显示低数量任务。（d）集中度与时间结构：机器人超声与机器人内镜合计占 427 篇核心文献的 94.6%，2021–2025 年发表的核心文献占 58.8%。等长五年期工作量由 2016–2020 年的 74 篇增至 2021–2025 年的 251 篇（3.39 倍）；扩展敏感性集为 1,002 篇。
"""
    (OUT_DIR / "figure_captions_bilingual.md").write_text(captions, encoding="utf-8")

    readme = """# Embodied clinical detection — bilingual figure package

## 中文说明

本图件包用于论文中的具身医学检测分类与文献工作量展示。除用户明确要求全英文的主动观察闭环图外，其余主图均包含中文与英文两个版本。每张图提供 PNG（600 dpi）、SVG（文字已转路径，便于跨平台显示）和 PDF（矢量）三种格式。

计数采用双层证据设计：

- **核心下界（Core lower bound）**：具身动作与具体任务在标题中明确出现，优先保证精度。
- **扩展上界（Expanded upper bound）**：允许关键证据仅出现在摘要中，优先保证召回率。

因此，图中的区间不是统计置信区间，而是由纳入规则形成的“高精度下界—高召回上界”。建议论文正文以核心集作为主分析，以扩展集作敏感性分析。

## English notes

This package supports manuscript figures on the taxonomy and literature workload of embodied clinical detection. Every main quantitative figure is supplied in Chinese and English; the active-observation closed-loop schematic is English-only as requested. Each figure is exported as 600-dpi PNG, portable SVG (text converted to paths), and vector PDF.

The counts use two evidence tiers:

- **Core lower bound:** embodiment and the concrete task are explicit in the title, prioritizing precision.
- **Expanded upper bound:** qualifying evidence may appear only in the abstract, prioritizing recall.

The displayed range is therefore not a statistical confidence interval. It is a rule-based precision–recall sensitivity band. Use the core corpus for the primary manuscript analysis and the expanded set as a sensitivity analysis.

## Search protocol / 检索方法

- Databases: OpenAlex and Europe PMC.
- Search fields: title and abstract; exact task phrases plus targeted broad combinations for low-volume families.
- Deduplication: DOI first, then canonicalized title.
- Unit: deduplicated publication record, not clinical trial, product, or deployed system.
- Classification: one primary task per work.
- Cutoff: 2026-08-06; 2026 is year-to-date.
- Corpus: 4,977 raw records → 3,849 deduplicated candidates → 802 core / 1,461 expanded records across all classes.

## Reviewer-facing limitations / 审稿风险与限制

1. “All work” means all records captured within this reproducible search boundary; it is not a claim of universal bibliographic exhaustiveness. Subscription databases and non-English terminology may add records.
2. Expanded counts are intentionally sensitive and may include adjacent applications; they should not be interpreted as an exact prevalence estimate.
3. Sparse families are especially terminology-sensitive, so a zero count means “no eligible record retrieved under this protocol,” not proof that no prototype exists.
4. One-primary-task assignment avoids double counting but suppresses genuine multi-action systems.
5. Publication counts measure research activity, not clinical maturity, regulatory clearance, trial quality, or deployment scale.
6. The 2026 point is incomplete and must not be directly compared with full calendar years.

## Source files / 源数据

- `source_data_all_task_counts_bilingual.csv`: all 24 task counts and definitions.
- `source_data_active_annual_counts_bilingual.csv`: annual active-observation counts by task and evidence tier.
- `active_observational_records_1002.csv`: auditable record-level active-observation corpus.
- `active_observational_search_queries.csv`: database-specific search strings and retrieval counts.
- `summary_statistics_bilingual.csv`: headline derived statistics.
- `bibliometric_metadata.json` and `task_definitions_bilingual.json`: machine-readable protocol metadata.
"""
    (OUT_DIR / "README_bilingual.md").write_text(readme, encoding="utf-8")


def merge_pdf_packet(pdf_paths: list[Path]) -> Path | None:
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception:
        return None
    writer = PdfWriter()
    for path in pdf_paths:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    packet = OUT_DIR / "Bilingual_Figure_Packet_2026-08-06.pdf"
    with packet.open("wb") as handle:
        writer.write(handle)
    return packet


def main() -> None:
    created: list[Path] = []
    for language in ("EN", "ZH"):
        created.extend(taxonomy_figure(language))
        created.extend(class_workload_figure(language))
        created.extend(all_tasks_workload_figure(language))
    created.extend(active_loop_figure())
    for language in ("EN", "ZH"):
        created.extend(active_landscape_figure(language))

    export_source_data()
    write_documentation()
    pdf_order = [
        OUT_DIR / "Fig1_taxonomy_EN.pdf",
        OUT_DIR / "Fig1_taxonomy_ZH.pdf",
        OUT_DIR / "Fig2_class_workload_EN.pdf",
        OUT_DIR / "Fig2_class_workload_ZH.pdf",
        OUT_DIR / "Fig3_all_tasks_workload_EN.pdf",
        OUT_DIR / "Fig3_all_tasks_workload_ZH.pdf",
        OUT_DIR / "Fig4_active_observational_closed_loop_EN.pdf",
        OUT_DIR / "Fig5_active_observational_landscape_EN.pdf",
        OUT_DIR / "Fig5_active_observational_landscape_ZH.pdf",
    ]
    packet = merge_pdf_packet(pdf_order)
    if packet:
        created.append(packet)

    manifest_rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if path.is_file():
            manifest_rows.append({"file": path.name, "bytes": path.stat().st_size})
    pd.DataFrame(manifest_rows).to_csv(OUT_DIR / "file_manifest.csv", index=False, encoding="utf-8-sig")

    archive_base = ROOT / "outputs" / "08e9490e7d8f" / "Embodied_Clinical_Detection_Bilingual_Figures_2026-08-06"
    archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=OUT_DIR.parent, base_dir=OUT_DIR.name))
    print(json.dumps({"out_dir": str(OUT_DIR), "archive": str(archive), "created_figure_files": len(created)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
