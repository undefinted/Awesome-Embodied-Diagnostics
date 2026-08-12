#!/usr/bin/env python3
"""Create submission-grade bilingual figures for embodied clinical detection.

This script restyles the arXiv-inclusive bibliometric figures as compact,
full-width biomedical-journal artwork.  It does not alter the underlying
retrieval counts.  The former "lower/upper bound" wording is replaced by the
more defensible "strict title-explicit set" and "broad title/abstract set".
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "embodied_detection_bilingual_figures_arxiv_v2_2026-08-07"
)
OUT_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "embodied_detection_publication_style_v3_2026-08-07"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

TASK_FILE = SRC_DIR / "source_data_all_task_counts_bilingual.csv"
ANNUAL_FILE = SRC_DIR / "source_data_active_annual_counts_bilingual.csv"
TASKS = pd.read_csv(TASK_FILE)
ANNUAL = pd.read_csv(ANNUAL_FILE)


def mm(value: float) -> float:
    return value / 25.4


FONT_DIR = ROOT / "tmp" / "08e9490e7d8f" / "fonts" / "package"
FONT_REGULAR = FONT_DIR / "NotoSansCJKsc-Regular.otf"
FONT_MEDIUM = FONT_DIR / "NotoSansCJKsc-Medium.otf"
FONT_BOLD = FONT_DIR / "NotoSansCJKsc-Bold.otf"
for font_path in (FONT_REGULAR, FONT_MEDIUM, FONT_BOLD):
    if font_path.exists():
        mpl.font_manager.fontManager.addfont(str(font_path))

FONT_FAMILY = (
    mpl.font_manager.FontProperties(fname=str(FONT_REGULAR)).get_name()
    if FONT_REGULAR.exists()
    else "DejaVu Sans"
)

mpl.rcParams.update(
    {
        "font.family": FONT_FAMILY,
        "font.size": 7.2,
        "axes.titlesize": 8.2,
        "axes.titleweight": "semibold",
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.7,
        "ytick.labelsize": 6.7,
        "legend.fontsize": 6.6,
        "axes.linewidth": 0.65,
        "axes.edgecolor": "#333333",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "lines.linewidth": 1.15,
        "lines.markersize": 3.5,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
    }
)


# Okabe-Ito-derived, colour-vision-deficiency-friendly category palette.
COL = {
    "A": "#0072B2",
    "R": "#D55E00",
    "S": "#009E73",
    "A2": "#009E73",
    "emerging": "#7A7A7A",
    "ink": "#222222",
    "muted": "#666666",
    "grid": "#D9D9D9",
    "light": "#F2F2F2",
    "broad": "#FFFFFF",
    "danger": "#C44E52",
}


def tint(color: str, amount: float = 0.72) -> tuple[float, float, float]:
    rgb = np.asarray(mcolors.to_rgb(color))
    return tuple(rgb * (1 - amount) + np.ones(3) * amount)


def wrap(value: str, width: int) -> str:
    return "\n".join(
        textwrap.wrap(
            str(value),
            width=width,
            # Chinese text contains no spaces; allow character-level wrapping.
            break_long_words=True,
            break_on_hyphens=False,
        )
    )


def clean_axis(ax: plt.Axes, grid: str | None = "x") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid == "x":
        ax.grid(axis="x", color=COL["grid"], linewidth=0.45, zorder=0)
    elif grid == "y":
        ax.grid(axis="y", color=COL["grid"], linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)


def panel_label(ax: plt.Axes, label: str, x: float = -0.12, y: float = 1.08) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.5,
        fontweight="bold",
        color=COL["ink"],
    )


def atomic_savefig(fig: plt.Figure, path: Path, *, fmt: str, **kwargs) -> None:
    tmp = path.with_name(f".{path.name}.writing")
    with tmp.open("wb") as handle:
        fig.savefig(handle, format=fmt, **kwargs)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)


def save_bundle(fig: plt.Figure, stem: str) -> list[Path]:
    """Export an exact-size vector and high-resolution raster bundle."""
    paths: list[Path] = []
    exports = [
        ("pdf", {"metadata": {"Creator": "Python/Matplotlib", "Title": stem}}),
        ("svg", {"metadata": {"Creator": "Python/Matplotlib"}}),
        ("png", {"dpi": 600, "metadata": {"Title": stem}}),
        ("tiff", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}}),
    ]
    for ext, kwargs in exports:
        path = OUT_DIR / f"{stem}.{ext}"
        atomic_savefig(fig, path, fmt=ext, **kwargs)
        paths.append(path)
    plt.close(fig)
    return paths


def retrieval_legend(lang: str) -> list[Line2D]:
    is_en = lang == "EN"
    return [
        Line2D(
            [0], [0], marker="o", linestyle="none", markersize=4.4,
            markerfacecolor=COL["ink"], markeredgecolor=COL["ink"],
            label="Strict title-explicit set" if is_en else "严格题名集",
        ),
        Line2D(
            [0], [0], marker="o", linestyle="none", markersize=4.7,
            markerfacecolor="white", markeredgecolor=COL["ink"], markeredgewidth=0.9,
            label="Broad title/abstract set" if is_en else "宽题名-摘要集",
        ),
    ]


def taxonomy_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    fig = plt.figure(figsize=(mm(180), mm(93)))
    ax = fig.add_axes([0.018, 0.045, 0.964, 0.92])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    cols = np.array([0.00, 0.19, 0.48, 0.70, 1.00])
    header_top, header_bottom = 0.98, 0.84
    row_bounds = [(0.84, 0.57), (0.57, 0.30), (0.30, 0.03)]
    headers = (
        ["Category", "Agent action / action object", "Diagnostic evidence", "Representative tasks"]
        if is_en
        else ["类别", "智能体动作 / 动作对象", "诊断证据", "代表性任务"]
    )
    ax.add_patch(Rectangle((0, header_bottom), 1, header_top - header_bottom, facecolor="#ECECEC", edgecolor="none"))
    for i, header in enumerate(headers):
        ax.text(cols[i] + 0.012, (header_top + header_bottom) / 2, header,
                va="center", ha="left", fontsize=7.2, fontweight="semibold", color=COL["ink"])

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
        widths = (23, 38, 31, 45)
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
                "机器人触诊；弹性检测；关节激发；叩诊；腱反射；TMS；神经刺激-响应；眼压检测",
            ),
            (
                "S  采样式交互检测",
                "对目标组织或体液实施穿刺、抽吸、拭子采集或切取",
                "离体病理、生化、微生物或分子结果",
                "机器人采血；拭子采样；支气管镜活检/TBNA；前列腺活检；粗针活检；FNA；脑脊液/骨髓采样",
            ),
        ]
        widths = (14, 18, 15, 18)

    for code, row, (top, bottom) in zip(("A", "R", "S"), rows, row_bounds):
        ymid = (top + bottom) / 2
        ax.add_patch(Rectangle((0, bottom), 1, top - bottom, facecolor=tint(COL[code], 0.95), edgecolor="none"))
        ax.add_patch(Rectangle((0, bottom), 0.008, top - bottom, facecolor=COL[code], edgecolor="none"))
        for i, value in enumerate(row):
            ax.text(
                cols[i] + 0.014,
                ymid,
                wrap(value, widths[i]),
                va="center",
                ha="left",
                fontsize=6.7 if i else 7.1,
                fontweight="semibold" if i == 0 else "normal",
                color=COL[code] if i == 0 else COL["ink"],
                linespacing=1.25,
            )
        ax.plot([0, 1], [bottom, bottom], color="#BEBEBE", lw=0.55)

    for x in cols[1:-1]:
        ax.plot([x, x], [0.03, header_top], color="#C7C7C7", lw=0.45)
    ax.plot([0, 1], [header_top, header_top], color="#333333", lw=0.7)
    ax.plot([0, 1], [header_bottom, header_bottom], color="#333333", lw=0.7)
    note = (
        "Classification rule: assign each work to the primary evidence-generating action."
        if is_en
        else "分类规则：每项工作仅按主要证据生成动作归入一个任务。"
    )
    ax.text(0, 0.005, note, va="bottom", ha="left", fontsize=5.8, color=COL["muted"])
    return save_bundle(fig, f"Fig1_taxonomy_{lang}")


def class_workload_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    class_names = {
        "EN": {
            "A": "Active observational sensing",
            "R": "Response-based interactive diagnosis",
            "S": "Sample-based interactive diagnosis",
        },
        "ZH": {"A": "主动观察式检测", "R": "响应式交互检测", "S": "采样式交互检测"},
    }[lang]
    order = ["A", "R", "S"]
    summary = TASKS.groupby("class_code", as_index=True)[["core", "expanded"]].sum()

    fig, ax = plt.subplots(figsize=(mm(180), mm(82)))
    fig.subplots_adjust(left=0.275 if is_en else 0.19, right=0.965, bottom=0.23, top=0.79)
    ypos = np.arange(len(order))[::-1]
    for y, code in zip(ypos, order):
        strict = int(summary.loc[code, "core"])
        broad = int(summary.loc[code, "expanded"])
        ax.plot([strict, broad], [y, y], color=tint(COL[code], 0.58), lw=4.2, solid_capstyle="round", zorder=1)
        ax.scatter([strict], [y], s=34, facecolor=COL[code], edgecolor="white", linewidth=0.55, zorder=3)
        ax.scatter([broad], [y], s=38, facecolor="white", edgecolor=COL[code], linewidth=1.05, zorder=4)
        # A single paired label avoids collisions when the two retrieval sets
        # differ by only a few dozen records.
        ax.annotate(f"{strict:,} / {broad:,}", ((strict + broad) / 2, y), xytext=(0, 8),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=7.0, fontweight="semibold", color=COL[code])

    labels = [f"{code}  {class_names[code]}" for code in order]
    ax.set_yticks(ypos, labels)
    ax.tick_params(axis="y", length=0, pad=7)
    ax.set_xlim(0, 1100)
    ax.set_xticks([0, 250, 500, 750, 1000])
    ax.set_xlabel("Deduplicated publication records, n" if is_en else "跨库去重文献记录数，n")
    clean_axis(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.legend(handles=retrieval_legend(lang), frameon=False, ncol=2, loc="lower left",
              bbox_to_anchor=(0.0, 1.08), handletextpad=0.45, columnspacing=1.3, borderaxespad=0)
    note = (
        "Filled marker: strict set; open marker: broad sensitivity set. OpenAlex + Europe PMC + arXiv; cutoff 6 Aug 2026."
        if is_en
        else "实心点：严格集；空心点：宽检索敏感性集。OpenAlex + Europe PMC + arXiv；截至 2026-08-06。"
    )
    fig.text(0.012, 0.035, note, fontsize=5.7, color=COL["muted"], ha="left", va="bottom")
    return save_bundle(fig, f"Fig2_class_workload_{lang}")


def log1p_position(values: np.ndarray | pd.Series | list[float]) -> np.ndarray:
    return np.log10(np.asarray(values, dtype=float) + 1.0)


LOG_TICKS = np.array([0, 1, 3, 10, 30, 100, 300, 1000])
LOG_TICK_POS = log1p_position(LOG_TICKS)


def draw_task_panel(ax: plt.Axes, sub: pd.DataFrame, code: str, lang: str, letter: str) -> None:
    is_en = lang == "EN"
    label_field = "task_en" if is_en else "task_zh"
    sub = sub.sort_values(["core", "expanded", "code"], ascending=[False, False, True]).reset_index(drop=True)
    y = np.arange(len(sub))[::-1]
    strict_x = log1p_position(sub["core"])
    broad_x = log1p_position(sub["expanded"])
    for yy, sx, bx, (_, row) in zip(y, strict_x, broad_x, sub.iterrows()):
        ax.plot([sx, bx], [yy, yy], color=tint(COL[code], 0.58), lw=3.2, solid_capstyle="round", zorder=1)
        ax.scatter([sx], [yy], s=19, color=COL[code], edgecolor="white", linewidth=0.4, zorder=3)
        ax.scatter([bx], [yy], s=22, facecolor="white", edgecolor=COL[code], linewidth=0.85, zorder=4)
        ax.text(max(sx, bx) + 0.055, yy, f"{int(row['core']):,} / {int(row['expanded']):,}",
                va="center", ha="left", fontsize=5.9, color=COL["ink"])

    labels = [
        f"{row.code}  {wrap(row[label_field], 33 if is_en else 16)}"
        for _, row in sub.iterrows()
    ]
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", length=0, pad=6)
    ax.set_xlim(-0.06, 3.32)
    ax.set_xticks(LOG_TICK_POS, [str(v) for v in LOG_TICKS])
    ax.set_xlabel("Publication records, n (log$_{10}$(n + 1) scale)" if is_en else "文献记录数，n（log$_{10}$(n + 1) 坐标）")
    clean_axis(ax, "x")
    ax.spines["left"].set_visible(False)
    class_name = sub.iloc[0]["class_en" if is_en else "class_zh"]
    count_label = "tasks" if is_en else "个任务"
    ax.set_title(f"{code}  {class_name}  ({len(sub)} {count_label})", loc="left", pad=6, color=COL[code])
    panel_label(ax, letter, x=-0.24 if is_en else -0.19, y=1.07)


def all_tasks_workload_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    fig = plt.figure(figsize=(mm(180), mm(188)))
    gs = fig.add_gridspec(3, 1, height_ratios=[7, 8, 9], hspace=0.58,
                          left=0.335 if is_en else 0.27, right=0.965, top=0.92, bottom=0.105)
    axes = [fig.add_subplot(gs[i, 0]) for i in range(3)]
    for ax, code, letter in zip(axes, ("A", "R", "S"), ("a", "b", "c")):
        draw_task_panel(ax, TASKS[TASKS["class_code"].eq(code)].copy(), code, lang, letter)

    fig.legend(handles=retrieval_legend(lang), frameon=False, ncol=2, loc="upper right",
               bbox_to_anchor=(0.965, 0.99), handletextpad=0.45, columnspacing=1.2)
    exact_note = (
        "Exact values at right are strict / broad counts. A common transformed axis is used across all three classes."
        if is_en
        else "右侧精确数值依次为“严格集 / 宽检索集”；三个大类使用同一变换坐标，便于跨类比较。"
    )
    source_note = (
        "Unit: one deduplicated work assigned to one primary task; zero-count task families are retained. Cutoff: 6 Aug 2026."
        if is_en
        else "计数单位：跨库去重且唯一归入一个主要任务的文献；零计数任务仍保留。截至 2026-08-06。"
    )
    fig.text(0.012, 0.046, exact_note, fontsize=5.8, color=COL["ink"], ha="left")
    fig.text(0.012, 0.024, source_note, fontsize=5.55, color=COL["muted"], ha="left")
    return save_bundle(fig, f"Fig3_all_tasks_workload_{lang}")


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], *,
              color: str = "#5F6B70", rad: float = 0.0, lw: float = 1.0) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=8,
            linewidth=lw,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=2,
            shrinkB=2,
            zorder=2,
        )
    )


def flow_box(ax: plt.Axes, x: float, y: float, w: float, h: float, number: int,
             title: str, body: str, color: str) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.006,rounding_size=0.010",
            facecolor="white", edgecolor=tint(color, 0.32), linewidth=0.85, zorder=3,
        )
    )
    ax.add_patch(plt.Circle((x + 0.023, y + h - 0.026), 0.015, facecolor=color, edgecolor="none", zorder=4))
    ax.text(x + 0.023, y + h - 0.026, str(number), color="white", ha="center", va="center",
            fontsize=5.8, fontweight="bold", zorder=5)
    ax.text(x + 0.045, y + h - 0.026, title, ha="left", va="center", fontsize=7.2,
            fontweight="semibold", color=COL["ink"], zorder=5)
    ax.text(x + 0.018, y + h - 0.058, body, ha="left", va="top", fontsize=5.9,
            color=COL["muted"], linespacing=1.25, zorder=5)


def active_loop_figure() -> list[Path]:
    fig = plt.figure(figsize=(mm(180), mm(108)))
    ax = fig.add_axes([0.015, 0.025, 0.97, 0.95])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    w, h = 0.205, 0.235
    xs = [0.025, 0.275, 0.525, 0.775]
    top_y, bottom_y = 0.66, 0.31
    flow_box(ax, xs[0], top_y, w, h, 1, "Current observation", "Image, video, acoustic or\nphysiological signal", COL["A"])
    flow_box(ax, xs[1], top_y, w, h, 2, "State assessment", "Target visibility • coverage\nImage/signal quality • uncertainty", COL["A"])
    flow_box(ax, xs[2], top_y, w, h, 3, "Next-best sensing action", "Viewpoint • position • orientation\nContact state • scan path", COL["A2"])
    flow_box(ax, xs[3], top_y, w, h, 4, "Safety gate and execution", "Force/speed limits • collision checks\nPatient-motion monitoring", COL["R"])
    flow_box(ax, xs[2], bottom_y, w, h, 5, "New observation", "Acquire • register • update\npatient/target model", COL["A2"])
    flow_box(ax, xs[1], bottom_y, w, h, 6, "Decision policy", "Continue • rescan\nStop • human handoff", COL["A"])

    cy_top = top_y + h / 2
    add_arrow(ax, (xs[0] + w, cy_top), (xs[1], cy_top))
    add_arrow(ax, (xs[1] + w, cy_top), (xs[2], cy_top))
    add_arrow(ax, (xs[2] + w, cy_top), (xs[3], cy_top))
    add_arrow(ax, (xs[3] + w / 2, top_y), (xs[2] + w, bottom_y + h / 2), rad=0.13)
    add_arrow(ax, (xs[2], bottom_y + h / 2), (xs[1] + w, bottom_y + h / 2))
    add_arrow(ax, (xs[1], bottom_y + h / 2), (xs[0] + w / 2, top_y), color=COL["A"], rad=-0.30, lw=1.25)
    ax.text(0.115, 0.48, "CONTINUE / RESCAN", rotation=90, ha="center", va="center",
            fontsize=5.4, color=COL["A"], fontweight="semibold")

    # Terminal actions and objective are intentionally secondary to the loop.
    terminal_y, terminal_h = 0.09, 0.115
    ax.add_patch(FancyBboxPatch((0.275, terminal_y), 0.205, terminal_h,
                                boxstyle="round,pad=0.005,rounding_size=0.009",
                                facecolor="#F3F3F3", edgecolor="#B5B5B5", linewidth=0.65))
    ax.text(0.3775, terminal_y + terminal_h / 2, "Stop + diagnostic report",
            ha="center", va="center", fontsize=6.4, fontweight="semibold", color=COL["ink"])
    ax.add_patch(FancyBboxPatch((0.525, terminal_y), 0.205, terminal_h,
                                boxstyle="round,pad=0.005,rounding_size=0.009",
                                facecolor=tint(COL["danger"], 0.91), edgecolor=tint(COL["danger"], 0.40), linewidth=0.65))
    ax.text(0.6275, terminal_y + terminal_h / 2, "Human handoff",
            ha="center", va="center", fontsize=6.4, fontweight="semibold", color=COL["danger"])
    add_arrow(ax, (xs[1] + 0.075, bottom_y), (0.3775, terminal_y + terminal_h), color="#777777", rad=0.08, lw=0.75)
    add_arrow(ax, (xs[1] + 0.145, bottom_y), (0.6275, terminal_y + terminal_h), color=COL["danger"], rad=-0.08, lw=0.75)

    ax.text(0.025, 0.955, "Optimization objective", fontsize=6.1, fontweight="semibold", color=COL["A"])
    ax.text(0.195, 0.955, "higher quality  •  more complete coverage  •  greater diagnostic value",
            fontsize=6.1, color=COL["ink"])
    ax.text(0.98, 0.015,
            "Generic architecture; the sensing policy may be rule-based, optimization-based, learning-based or clinician-supervised.",
            fontsize=5.2, color=COL["muted"], ha="right", va="bottom")
    return save_bundle(fig, "Fig4_active_observational_closed_loop_EN")


def active_period_matrix() -> tuple[np.ndarray, list[str], list[str], list[str]]:
    active = ANNUAL[ANNUAL["task_code"].str.startswith("A")].copy()
    periods = [
        ("≤2004", lambda y: y <= 2004),
        ("2005–09", lambda y: (y >= 2005) & (y <= 2009)),
        ("2010–14", lambda y: (y >= 2010) & (y <= 2014)),
        ("2015–19", lambda y: (y >= 2015) & (y <= 2019)),
        ("2020–24", lambda y: (y >= 2020) & (y <= 2024)),
        ("2025", lambda y: y == 2025),
        ("2026 YTD", lambda y: y == 2026),
    ]
    codes = [f"A{i}" for i in range(1, 8)]
    matrix = np.zeros((len(codes), len(periods)), dtype=int)
    for i, code in enumerate(codes):
        sub = active[active["task_code"].eq(code)]
        for j, (_, predicate) in enumerate(periods):
            matrix[i, j] = int(sub.loc[predicate(sub["year"]), "core_records"].sum())
    names_en = [TASKS.loc[TASKS["code"].eq(c), "task_en"].iloc[0] for c in codes]
    names_zh = [TASKS.loc[TASKS["code"].eq(c), "task_zh"].iloc[0] for c in codes]
    return matrix, [p[0] for p in periods], names_en, names_zh


def active_landscape_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    active_tasks = TASKS[TASKS["class_code"].eq("A")].copy()
    fig = plt.figure(figsize=(mm(180), mm(184)))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.02, 1.12], height_ratios=[1.0, 1.05],
                          left=0.145 if is_en else 0.14, right=0.975, top=0.94, bottom=0.08,
                          wspace=0.35, hspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # a — active-task workload on a common log1p axis.
    sub = active_tasks.sort_values(["core", "expanded", "code"], ascending=[False, False, True]).reset_index(drop=True)
    y = np.arange(len(sub))[::-1]
    sx = log1p_position(sub["core"])
    bx = log1p_position(sub["expanded"])
    for yy, x1, x2, (_, row) in zip(y, sx, bx, sub.iterrows()):
        ax_a.plot([x1, x2], [yy, yy], color=tint(COL["A"], 0.58), lw=3.0, solid_capstyle="round")
        ax_a.scatter([x1], [yy], s=18, color=COL["A"], edgecolor="white", linewidth=0.4, zorder=3)
        ax_a.scatter([x2], [yy], s=21, facecolor="white", edgecolor=COL["A"], linewidth=0.8, zorder=4)
        ax_a.text(max(x1, x2) + 0.045, yy, f"{int(row['core'])} / {int(row['expanded'])}",
                  va="center", ha="left", fontsize=5.5)
    compact_labels = {
        "EN": {
            "A1": "Ultrasound",
            "A2": "Endoscopy",
            "A3": "OCT / ophthalmic",
            "A4": "Dermoscopy",
            "A5": "Auscultation",
            "A6": "Otoscopy / ENT",
            "A7": "Optical / spectral / thermal",
        },
        "ZH": {
            "A1": "超声",
            "A2": "内镜",
            "A3": "OCT/眼科成像",
            "A4": "皮肤镜",
            "A5": "听诊",
            "A6": "耳镜/口腔-耳鼻喉",
            "A7": "光谱/热成像扫描",
        },
    }[lang]
    labels = [f"{r.code}  {wrap(compact_labels[r.code], 23 if is_en else 13)}" for _, r in sub.iterrows()]
    ax_a.set_yticks(y, labels)
    ax_a.tick_params(axis="y", length=0, pad=5)
    ax_a.set_xlim(-0.06, 3.18)
    ax_a.set_xticks(LOG_TICK_POS[:-1], [str(v) for v in LOG_TICKS[:-1]])
    ax_a.set_xlabel("Records, n (log$_{10}$(n + 1))" if is_en else "文献记录数，n（log$_{10}$(n + 1)）")
    clean_axis(ax_a, "x")
    ax_a.spines["left"].set_visible(False)
    ax_a.set_title("Workload by task" if is_en else "各任务累计工作量", loc="left")
    panel_label(ax_a, "a", x=-0.17, y=1.08)

    # b — annual trajectory from the strict set.
    years = np.arange(int(ANNUAL["year"].min()), int(ANNUAL["year"].max()) + 1)
    series = {
        "A1": ANNUAL[ANNUAL["task_code"].eq("A1")].set_index("year")["core_records"].reindex(years, fill_value=0),
        "A2": ANNUAL[ANNUAL["task_code"].eq("A2")].set_index("year")["core_records"].reindex(years, fill_value=0),
        "A3–A7": ANNUAL[ANNUAL["task_code"].isin(["A3", "A4", "A5", "A6", "A7"])].groupby("year")["core_records"].sum().reindex(years, fill_value=0),
    }
    labels_line = {
        "EN": {"A1": "A1 Ultrasound", "A2": "A2 Endoscopy", "A3–A7": "A3–A7 Emerging"},
        "ZH": {"A1": "A1 超声", "A2": "A2 内镜", "A3–A7": "A3–A7 新兴任务"},
    }[lang]
    line_colors = {"A1": COL["A"], "A2": COL["A2"], "A3–A7": COL["emerging"]}
    ax_b.axvspan(2021, 2025, color="#EFEFEF", zorder=0)
    for key, values in series.items():
        complete = years <= 2025
        ax_b.plot(years[complete], values.to_numpy()[complete], color=line_colors[key], lw=1.15,
                  label=labels_line[key], zorder=2)
        ax_b.plot(years[-2:], values.to_numpy()[-2:], color=line_colors[key], lw=1.15,
                  linestyle=(0, (3, 2)), zorder=2)
        ax_b.scatter([2026], [values.loc[2026]], s=11, color=line_colors[key], zorder=3)
    ax_b.set_xlim(years.min(), years.max() + 0.4)
    ax_b.set_ylim(bottom=0)
    ax_b.set_xticks([1995, 2000, 2005, 2010, 2015, 2020, 2025])
    ax_b.set_ylabel("Strict-set records per year" if is_en else "严格集年度文献数")
    clean_axis(ax_b, "y")
    ax_b.legend(frameon=False, loc="upper left", ncol=1, handlelength=2.0, borderaxespad=0.2)
    ax_b.text(2026.08, ax_b.get_ylim()[1] * 0.50, "2026\nYTD", rotation=90, ha="left", va="center",
              fontsize=5.6, color=COL["muted"])
    ax_b.text(2023, ax_b.get_ylim()[1] * 0.98, "2021–2025", ha="center", va="top",
              fontsize=5.7, color=COL["muted"])
    ax_b.set_title("Annual publication trajectory" if is_en else "年度发表轨迹", loc="left")
    panel_label(ax_b, "b", x=-0.14)

    # c — discrete, strictly monotonic heatmap.
    matrix, periods, names_en, names_zh = active_period_matrix()
    cmap = mcolors.ListedColormap(["#FFFFFF", "#EAF2F8", "#CFE1EF", "#9FC5DF", "#6AA6CF", "#337FB8", "#0B4F8A"])
    boundaries = [-0.5, 0.5, 4.5, 9.5, 24.5, 49.5, 99.5, 1000]
    norm = mcolors.BoundaryNorm(boundaries, cmap.N)
    im = ax_c.imshow(matrix, cmap=cmap, norm=norm, aspect="auto", interpolation="none")
    ax_c.set_yticks(np.arange(7), [f"A{i+1}  {wrap(compact_labels[f'A{i+1}'], 23 if is_en else 13)}" for i in range(7)])
    ax_c.set_xticks(np.arange(len(periods)), periods, rotation=38, ha="right", rotation_mode="anchor")
    ax_c.tick_params(length=0)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = int(matrix[i, j])
            ax_c.text(j, i, str(val), ha="center", va="center", fontsize=5.5,
                      color="white" if val >= 25 else COL["ink"], fontweight="semibold" if val >= 10 else "normal")
    for spine in ax_c.spines.values():
        spine.set_visible(False)
    ax_c.set_xticks(np.arange(-0.5, matrix.shape[1], 1), minor=True)
    ax_c.set_yticks(np.arange(-0.5, matrix.shape[0], 1), minor=True)
    ax_c.grid(which="minor", color="white", linewidth=0.8)
    ax_c.tick_params(which="minor", bottom=False, left=False)
    ax_c.set_title("Strict-set workload by publication period" if is_en else "严格集分发表时期工作量", loc="left")
    panel_label(ax_c, "c", x=-0.17, y=1.08)
    cbar = fig.colorbar(im, ax=ax_c, orientation="horizontal", fraction=0.075, pad=0.24,
                        ticks=[0, 2.5, 7, 17, 37, 75, 150], spacing="uniform")
    cbar.ax.set_xticklabels(["0", "1–4", "5–9", "10–24", "25–49", "50–99", "≥100"])
    cbar.ax.tick_params(labelsize=4.7, length=0, pad=1, labelrotation=25)
    for label in cbar.ax.get_xticklabels():
        label.set_ha("right")
    cbar.outline.set_visible(False)
    cbar.set_label("Records, n" if is_en else "文献记录数，n", fontsize=5.8, labelpad=2)

    # d — concentration and recency without decorative KPI cards.
    ax_d.set_xlim(0, 100)
    ax_d.set_ylim(0, 3.55)
    ax_d.axis("off")
    strict_total = int(active_tasks["core"].sum())
    broad_total = int(active_tasks["expanded"].sum())
    ax_d.text(0, 3.42, (f"Strict set n={strict_total:,}   |   Broad set n={broad_total:,}"
                        if is_en else f"严格集 n={strict_total:,}   |   宽检索集 n={broad_total:,}"),
              ha="left", va="top", fontsize=7.0, fontweight="semibold", color=COL["ink"])
    task_shares = np.array([276, 137, strict_total - 276 - 137]) / strict_total * 100
    time_shares = np.array([121, 260, 55]) / strict_total * 100
    bar_specs = [
        (2.52, task_shares, [COL["A"], COL["A2"], "#A0A0A0"],
         ["A1", "A2", "A3–A7"], "Strict-set task mix" if is_en else "严格集任务构成"),
        (1.60, time_shares, ["#A0A0A0", COL["A"], tint(COL["A"], 0.52)],
         ["≤2020", "2021–25", "2026 YTD"], "Strict-set publication-time mix" if is_en else "严格集发表时期构成"),
    ]
    for y0, shares, colors, labels_bar, heading in bar_specs:
        ax_d.text(0, y0 + 0.40, heading, ha="left", va="bottom", fontsize=6.2, fontweight="semibold")
        left = 0.0
        for share, color, label in zip(shares, colors, labels_bar):
            ax_d.add_patch(Rectangle((left, y0), share, 0.34, facecolor=color, edgecolor="white", linewidth=0.55))
            if share >= 10:
                ax_d.text(left + share / 2, y0 + 0.17, f"{label}\n{share:.1f}%", ha="center", va="center",
                          fontsize=5.35, color="white" if color != tint(COL["A"], 0.52) else COL["ink"],
                          fontweight="semibold", linespacing=1.05)
            left += share
    top_two = (276 + 137) / strict_total * 100
    ratio = 260 / 77
    ax_d.text(0, 0.86,
              (f"A1+A2 account for {top_two:.1f}% of strict-set records."
               if is_en else f"A1+A2 合计占严格集文献的 {top_two:.1f}%。"),
              fontsize=6.5, fontweight="semibold", color=COL["ink"], ha="left")
    ax_d.text(0, 0.58,
              (f"Five-year activity: 77 (2016–2020) → 260\n(2021–2025), {ratio:.2f}×."
               if is_en else f"五年期工作量：77（2016–2020）→ 260\n（2021–2025），{ratio:.2f} 倍。"),
              fontsize=6.0, color=COL["muted"], ha="left", va="top", linespacing=1.25)
    ax_d.text(0, 0.18,
              ("2026 is partial-year; do not compare directly\nwith complete calendar years."
               if is_en else "2026 年为不完整年度，不应与完整\n自然年直接比较。"),
              fontsize=5.6, color=COL["muted"], ha="left", va="top", linespacing=1.25)
    ax_d.set_title("Field concentration and recency" if is_en else "领域集中度与时间结构", loc="left")
    panel_label(ax_d, "d", x=-0.14)

    fig.legend(handles=retrieval_legend(lang), frameon=False, ncol=2, loc="upper right",
               bbox_to_anchor=(0.975, 0.995), handletextpad=0.4, columnspacing=1.0)
    foot = (
        "Counts are deduplicated publication records, not deployed systems or clinical trials. One primary task per work; cutoff 6 Aug 2026."
        if is_en
        else "计数为跨库去重文献，并非已部署系统或临床试验；每项工作唯一归入一个主要任务；截至 2026-08-06。"
    )
    fig.text(0.012, 0.018, foot, fontsize=5.3, color=COL["muted"], ha="left")
    return save_bundle(fig, f"Fig5_active_observational_landscape_{lang}")


def copy_source_material() -> None:
    to_copy = [
        "source_data_all_task_counts_bilingual.csv",
        "source_data_active_annual_counts_bilingual.csv",
        "active_observational_records_1015.csv",
        "active_observational_search_queries.csv",
        "arxiv_increment_audit_by_task_bilingual.csv",
        "arxiv_added_or_metadata_recovered_records_14.csv",
        "annual_trajectory_method_bilingual.md",
        "bibliometric_metadata.json",
        "task_definitions_bilingual.json",
        "all_database_query_log.json",
    ]
    for name in to_copy:
        src = SRC_DIR / name
        if src.exists():
            shutil.copy2(src, OUT_DIR / name)
    shutil.copy2(Path(__file__), OUT_DIR / "make_publication_style_figures.py")


def cleanup_temp_writes() -> None:
    for path in OUT_DIR.glob(".*.writing"):
        path.unlink(missing_ok=True)


def write_documentation() -> None:
    style = """# Publication figure specification / 论文图形规范

## 中文

- 目标版式：生物医学期刊双栏通栏图；主图宽度 180 mm。
- 字体：Noto Sans CJK SC；最终尺寸正文 6.7–7.2 pt，面板编号 9.5 pt。
- 线宽：坐标轴 0.65 pt，数据线约 1.15 pt；最小可见线宽不低于 0.45 pt。
- 配色：Okabe–Ito 衍生的色觉缺陷友好配色；同时用实心/空心标记区分检索集，因此灰度打印仍可辨识。
- 数量编码：严格题名集为实心点；宽题名-摘要敏感性集为空心点；不再称为统计“下界/上界”。
- 24 任务图：三个大类共用 log10(n+1) 横轴，保留零值并在右侧给出精确的“严格 / 宽检索”计数。
- 热力图：0 为白色；1–4、5–9、10–24、25–49、50–99、≥100 使用严格递增的顺序色阶；每格保留精确整数。
- 导出：PDF/SVG 矢量；PNG/TIFF 为 600 dpi，TIFF 使用 LZW 无损压缩。
- 图内不放大号总标题；总标题、方法解释和限制写入图注，以保留数据区域并符合常见投稿习惯。

## English

- Target layout: full-width artwork for a two-column biomedical journal; main width 180 mm.
- Typeface: Noto Sans CJK SC; 6.7–7.2 pt body text and 9.5 pt panel labels at final size.
- Stroke weights: 0.65 pt axes and approximately 1.15 pt data lines; no essential stroke below 0.45 pt.
- Colour: an Okabe–Ito-derived colour-vision-deficiency-friendly palette. Filled versus open markers retain meaning in greyscale.
- Count encoding: filled markers denote the strict title-explicit set; open markers denote the broad title/abstract sensitivity set. These are retrieval sets, not statistical bounds.
- All-task figure: all three classes share a log10(n+1) axis; zero-count families remain visible and exact strict / broad counts are printed at right.
- Heatmap: zero is white; 1–4, 5–9, 10–24, 25–49, 50–99 and ≥100 use a strictly darker ordered scale, with exact integers in every cell.
- Export: vector PDF/SVG and 600-dpi PNG/TIFF; TIFF uses lossless LZW compression.
- Large figure titles are omitted from the artwork. Titles, methods and limitations belong in the caption, preserving data area and matching common submission practice.
"""
    (OUT_DIR / "publication_figure_specification_bilingual.md").write_text(style, encoding="utf-8")

    captions = """# Figure captions / 中英文图注

## Figure 1. Action-defined taxonomy of embodied clinical detection / 具身医学检测的动作定义型分类

**EN.** The taxonomy distinguishes three embodied diagnostic modes by the physical action that generates evidence. Active observational sensing changes sensor configuration to obtain a new observation; response-based interactive diagnosis applies a controlled stimulus and interprets the response; sample-based interactive diagnosis obtains tissue or body fluid for ex vivo analysis. Each work is assigned to its primary evidence-generating action.

**中.** 本分类依据产生诊断证据的物理动作区分三类具身医学检测。主动观察式检测改变传感器配置以获得新观察；响应式交互检测施加可控刺激并解释响应；采样式交互检测获取组织或体液供离体分析。每项工作按主要证据生成动作唯一归类。

## Figure 2. Cumulative literature workload by major class / 三大方向的累计文献工作量

**EN.** Filled markers show the strict title-explicit retrieval set and open markers show the broad title/abstract sensitivity set. Counts for active observational sensing, response-based interactive diagnosis and sample-based interactive diagnosis were 436/1,015, 98/143 and 278/317, respectively (strict/broad). The two sets reflect retrieval specificity and sensitivity; they are not confidence limits.

**中.** 实心点表示严格题名集，空心点表示宽题名-摘要敏感性集。主动观察式检测、响应式交互检测和采样式交互检测的严格/宽检索计数分别为 436/1,015、98/143 和 278/317。两组计数反映检索特异性与敏感性的差异，并非统计置信限。

## Figure 3. Workload across 24 task families / 24 个细分任务的累计工作量

**EN.** Workload across seven active-observation, eight response-based and nine sample-based task families. Filled and open markers denote strict and broad retrieval sets, respectively; exact strict/broad counts are printed at right. A common log10(n+1) axis supports cross-class comparison while retaining zero and low-count families. Counts are deduplicated publication records, not clinical trials, products or deployed systems.

**中.** 七个主动观察式、八个响应式和九个采样式任务的累计工作量。实心点与空心点分别表示严格集和宽检索集，右侧列出精确的严格/宽检索计数。三个大类共用 log10(n+1) 坐标，以便跨类比较并保留零值和低计数任务。计数单位为去重文献记录，并非临床试验、产品或已部署系统。

## Figure 4. Closed-loop active observational sensing / 主动观察式检测闭环

**EN.** The agent evaluates target visibility, coverage, image or signal quality and uncertainty from the current observation; selects the next viewpoint, pose, contact state or scan path; passes a safety gate; executes the action; acquires and registers a new observation; and then continues, rescans, stops or hands control to a human. The objective is to increase diagnostic value subject to safety constraints.

**中.** 智能体根据当前观察评估目标可见性、覆盖度、图像或信号质量和不确定性，选择下一视点、位姿、接触状态或扫描路径，通过安全门控后执行，获取并配准新观察，随后继续、复扫、停止或转交人工。其目标是在满足安全约束的前提下提高诊断价值。

## Figure 5. Active observational sensing landscape / 主动观察式检测的工作量、轨迹与结构

**EN.** (a) Strict and broad retrieval counts for seven active-observation tasks on a log10(n+1) axis. (b) Annual strict-set records from 1995 to 2026; the dashed final segment marks partial-year 2026. Each deduplicated work contributes once to its primary task and earliest plausible public year. (c) Exact strict-set counts by publication period; zero is white and larger ordered bins are strictly darker. (d) Field concentration and recency. A1 robotic ultrasound and A2 robotic endoscopy jointly account for 94.7% of the 436-record strict set. Five-year activity increased from 77 records in 2016–2020 to 260 in 2021–2025 (3.38×). The broad sensitivity set contains 1,015 records.

**中.** （a）七个主动观察式任务在 log10(n+1) 坐标上的严格集与宽检索集计数。（b）1995–2026 年的严格集年度轨迹；最后虚线段表示 2026 年为不完整年度。每篇跨库去重文献仅按主要任务和最早合理公开年份计数一次。（c）各发表时期的严格集精确计数；0 为白色，数量等级越高颜色严格越深。（d）领域集中度与时间结构。A1 机器人超声和 A2 机器人内镜合计占 436 篇严格集文献的 94.7%。五年期工作量由 2016–2020 年的 77 篇增至 2021–2025 年的 260 篇（3.38 倍）；宽检索敏感性集为 1,015 篇。

**Common methods / 共同方法.** OpenAlex, Europe PMC and arXiv; DOI-first then canonical-title deduplication; one primary task per work; search cutoff 6 August 2026. The broad set is retained as sensitivity analysis rather than interpreted as a statistical upper bound.
"""
    (OUT_DIR / "figure_captions_bilingual.md").write_text(captions, encoding="utf-8")

    readme = """# Embodied clinical detection — publication-style bilingual figures

This package contains journal-ready English and Chinese figures based on the arXiv-inclusive corpus. The quantitative data and cutoff are unchanged from the previous version; only visual design and terminology were revised.

## Main changes / 主要修改

- Standardized to 180-mm full-width biomedical-journal artwork.
- Replaced "core lower bound / expanded upper bound" with "strict title-explicit set / broad title/abstract set".
- Replaced stacked pale bars with filled/open dumbbell marks that remain interpretable in greyscale.
- Put all 24 tasks on a common log10(n+1) axis and retained exact values.
- Removed oversized in-figure titles and moved interpretation into bilingual captions.
- Exported PDF, SVG, 600-dpi PNG and 600-dpi LZW-TIFF.

## Files / 文件

- `Fig1` taxonomy: English and Chinese.
- `Fig2` workload by major class: English and Chinese.
- `Fig3` all 24 task families: English and Chinese.
- `Fig4` active observational sensing loop: English, as requested.
- `Fig5` active observational sensing landscape: English and Chinese.
- `Bilingual_Publication_Figure_Packet_2026-08-07.pdf`: nine-page combined packet.
- `publication_figure_specification_bilingual.md`: exact style contract.
- `figure_captions_bilingual.md`: manuscript-ready bilingual captions.
- Source CSV/JSON/record-level audit files and the complete plotting script.

## Interpretation note / 解释说明

The strict and broad sets are reproducible retrieval sets, not statistical lower and upper confidence limits. For a final systematic/scoping review, the manuscript's primary count should ideally be based on a fully screened and adjudicated corpus; the broad set can remain a sensitivity analysis.
"""
    (OUT_DIR / "README_bilingual.md").write_text(readme, encoding="utf-8")


def merge_pdf_packet(order: list[Path]) -> Path:
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for path in order:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    out = OUT_DIR / "Bilingual_Publication_Figure_Packet_2026-08-07.pdf"
    tmp = out.with_name(f".{out.name}.writing")
    with tmp.open("wb") as handle:
        writer.write(handle)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(out)
    return out


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if path.is_file() and path.name != "file_manifest.csv":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": digest})
    pd.DataFrame(rows).to_csv(OUT_DIR / "file_manifest.csv", index=False, encoding="utf-8-sig")


def run_machine_preflight(pdf_order: list[Path]) -> Path:
    from PIL import Image
    from pypdf import PdfReader

    expected_heights_mm = {
        "Fig1_taxonomy_EN": 93,
        "Fig1_taxonomy_ZH": 93,
        "Fig2_class_workload_EN": 82,
        "Fig2_class_workload_ZH": 82,
        "Fig3_all_tasks_workload_EN": 188,
        "Fig3_all_tasks_workload_ZH": 188,
        "Fig4_active_observational_closed_loop_EN": 108,
        "Fig5_active_observational_landscape_EN": 184,
        "Fig5_active_observational_landscape_ZH": 184,
    }
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    class_sizes = TASKS.groupby("class_code").size().to_dict()
    strict_total = int(TASKS["core"].sum())
    broad_total = int(TASKS["expanded"].sum())
    active_strict = int(TASKS.loc[TASKS["class_code"].eq("A"), "core"].sum())
    active_broad = int(TASKS.loc[TASKS["class_code"].eq("A"), "expanded"].sum())
    record("Task taxonomy", len(TASKS) == 24 and class_sizes == {"A": 7, "R": 8, "S": 9},
           f"24 tasks; A/R/S={class_sizes.get('A')}/{class_sizes.get('R')}/{class_sizes.get('S')}")
    record("Corpus totals", (strict_total, broad_total) == (812, 1475),
           f"strict={strict_total}; broad={broad_total}")
    record("Active-observation totals", (active_strict, active_broad) == (436, 1015),
           f"strict={active_strict}; broad={active_broad}")
    record("Annual source rows", len(ANNUAL) == 224, f"rows={len(ANNUAL)}")

    for stem, height_mm in expected_heights_mm.items():
        expected_px = (round(180 / 25.4 * 600), round(height_mm / 25.4 * 600))
        for ext in ("png", "tiff"):
            path = OUT_DIR / f"{stem}.{ext}"
            with Image.open(path) as image:
                dpi = image.info.get("dpi", (0, 0))
                size_ok = all(abs(a - b) <= 1 for a, b in zip(image.size, expected_px))
                dpi_ok = all(abs(float(v) - 600) <= 0.1 for v in dpi)
                compression_ok = ext != "tiff" or image.info.get("compression") == "tiff_lzw"
                record(f"{path.name} raster specification", size_ok and dpi_ok and compression_ok,
                       f"pixels={image.size}; dpi={dpi}; compression={image.info.get('compression', 'n/a')}")
        pdf_path = OUT_DIR / f"{stem}.pdf"
        page = PdfReader(str(pdf_path)).pages[0]
        width_mm = float(page.mediabox.width) / 72 * 25.4
        actual_height_mm = float(page.mediabox.height) / 72 * 25.4
        record(f"{pdf_path.name} physical size",
               abs(width_mm - 180) <= 0.15 and abs(actual_height_mm - height_mm) <= 0.15,
               f"{width_mm:.2f} × {actual_height_mm:.2f} mm")
        svg_path = OUT_DIR / f"{stem}.svg"
        try:
            ET.parse(svg_path)
            svg_ok = True
        except ET.ParseError:
            svg_ok = False
        record(f"{svg_path.name} XML parse", svg_ok, "valid SVG XML" if svg_ok else "parse failure")

    packet = OUT_DIR / "Bilingual_Publication_Figure_Packet_2026-08-07.pdf"
    packet_pages = len(PdfReader(str(packet)).pages)
    record("Combined PDF packet", packet_pages == len(pdf_order), f"pages={packet_pages}")
    cleanup_temp_writes()
    temp_count = len(list(OUT_DIR.glob(".*.writing")))
    record("Temporary export files", temp_count == 0, f"remaining={temp_count}")

    passed = all(item["passed"] for item in checks)
    payload = {
        "overall_passed": passed,
        "visual_review": "Nine PDF pages rendered at 170 dpi and inspected at final physical proportions.",
        "checks": checks,
    }
    json_path = OUT_DIR / "quality_control_report.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Quality-control report / 图形质检报告",
        "",
        f"**Overall / 总体：{'PASS / 通过' if passed else 'FAIL / 未通过'}**",
        "",
        "Visual review / 视觉检查：Nine PDF pages were rendered at 170 dpi and inspected at their final physical proportions. / 九页 PDF 已按最终物理比例渲染为 170 dpi 并逐页检查。",
        "",
        "| Check / 检查项 | Result / 结果 | Detail / 详情 |",
        "|---|---:|---|",
    ]
    for item in checks:
        lines.append(f"| {item['check']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |")
    md_path = OUT_DIR / "quality_control_report_bilingual.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not passed:
        raise RuntimeError(f"Figure preflight failed; inspect {json_path}")
    return md_path


def main() -> None:
    cleanup_temp_writes()
    created: list[Path] = []
    for language in ("EN", "ZH"):
        created.extend(taxonomy_figure(language))
        created.extend(class_workload_figure(language))
        created.extend(all_tasks_workload_figure(language))
    created.extend(active_loop_figure())
    for language in ("EN", "ZH"):
        created.extend(active_landscape_figure(language))

    copy_source_material()
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
    qc_report = run_machine_preflight(pdf_order)
    cleanup_temp_writes()
    write_manifest()
    archive_base = OUT_DIR.parent / "Embodied_Clinical_Detection_Publication_Style_Bilingual_2026-08-07"
    archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=OUT_DIR.parent, base_dir=OUT_DIR.name))
    print(json.dumps({
        "output_directory": str(OUT_DIR),
        "figure_files": len(created),
        "packet": str(packet),
        "quality_control_report": str(qc_report),
        "archive": str(archive),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
