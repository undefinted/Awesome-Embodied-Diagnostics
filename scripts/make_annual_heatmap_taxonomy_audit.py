#!/usr/bin/env python3
"""Create the annual active-observation heatmap and taxonomy gap audit.

The annual figures deliberately retain the already screened A1--A7 corpus.
Proposed additions from the taxonomy audit are documented separately and are
not assigned estimated publication counts.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "embodied_detection_publication_style_v3_2026-08-07"
)
OUT_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "embodied_detection_annual_heatmap_taxonomy_audit_v4_2026-08-07"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

TASKS = pd.read_csv(SRC_DIR / "source_data_all_task_counts_bilingual.csv")
ANNUAL = pd.read_csv(SRC_DIR / "source_data_active_annual_counts_bilingual.csv")


def mm(value: float) -> float:
    return value / 25.4


FONT_DIR = ROOT / "tmp" / "08e9490e7d8f" / "fonts" / "merged"
# TrueType-flavoured Noto Sans SC is used so Matplotlib can embed valid Type 42
# subsets in PDF.  The former CFF OTF face rendered correctly in raster/SVG but
# triggered a font-type mismatch in several PDF engines.
FONT_REGULAR = FONT_DIR / "NotoSansSC-Regular.ttf"
FONT_MEDIUM = FONT_DIR / "NotoSansSC-Medium.ttf"
FONT_BOLD = FONT_MEDIUM
for font_path in (FONT_REGULAR, FONT_MEDIUM, FONT_BOLD):
    if font_path.exists():
        try:
            mpl.font_manager.fontManager.addfont(str(font_path))
        except RuntimeError:
            # A damaged optional weight must not block the regular CJK face.
            pass

FONT_FAMILY = (
    mpl.font_manager.FontProperties(fname=str(FONT_REGULAR)).get_name()
    if FONT_REGULAR.exists()
    else "DejaVu Sans"
)

mpl.rcParams.update(
    {
        "font.family": FONT_FAMILY,
        "font.size": 7.0,
        "axes.titlesize": 8.1,
        "axes.titleweight": "semibold",
        "axes.labelsize": 7.0,
        "xtick.labelsize": 6.2,
        "ytick.labelsize": 6.2,
        "legend.fontsize": 6.3,
        "axes.linewidth": 0.65,
        "axes.edgecolor": "#333333",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.8,
        "ytick.major.size": 2.8,
        "lines.linewidth": 1.1,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
    }
)

COL = {
    "A": "#0072B2",
    "A2": "#009E73",
    "ink": "#222222",
    "muted": "#666666",
    "grid": "#D9D9D9",
    "light": "#F2F2F2",
    "emerging": "#7A7A7A",
    "warning": "#B35C00",
}

# Strictly darker sequential scale.  Zero is white.
HEAT_COLORS = [
    "#FFFFFF",
    "#EAF2F8",
    "#CFE1EF",
    "#9FC5DF",
    "#6AA6CF",
    "#337FB8",
    "#0B4F8A",
]
HEAT_BOUNDARIES = [-0.5, 0.5, 2.5, 5.5, 10.5, 20.5, 40.5, 1000]
HEAT_TICKS = [0, 1.5, 4, 8, 15, 30, 60]
HEAT_LABELS = ["0", "1–2", "3–5", "6–10", "11–20", "21–40", "≥41"]
HEAT_CMAP = mcolors.ListedColormap(HEAT_COLORS)
HEAT_NORM = mcolors.BoundaryNorm(HEAT_BOUNDARIES, HEAT_CMAP.N)

YEARS = list(range(1995, 2027))
CODES = [f"A{i}" for i in range(1, 8)]

COMPACT = {
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
        "A3": "OCT / 眼科成像",
        "A4": "皮肤镜",
        "A5": "听诊",
        "A6": "耳镜 / 口腔-耳鼻喉",
        "A7": "光谱 / 热成像扫描",
    },
}


def tint(color: str, amount: float = 0.72) -> tuple[float, float, float]:
    rgb = np.asarray(mcolors.to_rgb(color))
    return tuple(rgb * (1 - amount) + np.ones(3) * amount)


def wrap(value: str, width: int) -> str:
    return "\n".join(
        textwrap.wrap(
            str(value),
            width=width,
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


def panel_label(ax: plt.Axes, label: str, x: float = -0.10, y: float = 1.08) -> None:
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


def annual_matrix() -> np.ndarray:
    pivot = (
        ANNUAL.groupby(["task_code", "year"], as_index=False)["core_records"]
        .sum()
        .pivot(index="task_code", columns="year", values="core_records")
        .reindex(index=CODES, columns=YEARS, fill_value=0)
        .fillna(0)
    )
    return pivot.to_numpy(dtype=int)


MATRIX = annual_matrix()


def draw_annual_heatmap(
    ax: plt.Axes,
    lang: str,
    *,
    title: bool = True,
    panel: str | None = "c",
    label_zeros: bool = True,
) -> mpl.image.AxesImage:
    is_en = lang == "EN"
    image = ax.imshow(
        MATRIX,
        cmap=HEAT_CMAP,
        norm=HEAT_NORM,
        aspect="auto",
        interpolation="none",
    )
    row_labels = [f"{code}  {COMPACT[lang][code]}" for code in CODES]
    ax.set_yticks(np.arange(len(CODES)), row_labels)
    year_labels = [str(y) if y < 2026 else "2026\nYTD" for y in YEARS]
    ax.set_xticks(np.arange(len(YEARS)), year_labels, rotation=90, ha="center", va="top")
    ax.tick_params(axis="x", length=0, pad=1.6, labelsize=4.45)
    ax.tick_params(axis="y", length=0, pad=5.0, labelsize=6.0)

    for i in range(MATRIX.shape[0]):
        for j in range(MATRIX.shape[1]):
            value = int(MATRIX[i, j])
            if value == 0 and not label_zeros:
                continue
            if value == 0:
                color = "#A9A9A9"
                weight = "normal"
            elif value >= 11:
                color = "white"
                weight = "semibold"
            else:
                color = COL["ink"]
                weight = "semibold" if value >= 6 else "normal"
            ax.text(
                j,
                i,
                str(value),
                ha="center",
                va="center",
                fontsize=3.75,
                color=color,
                fontweight=weight,
            )

    # White cell boundaries and stronger five-year guides improve scanning.
    ax.set_xticks(np.arange(-0.5, MATRIX.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, MATRIX.shape[0], 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.62)
    ax.tick_params(which="minor", bottom=False, left=False)
    for boundary_year in (2000, 2005, 2010, 2015, 2020, 2025):
        x = YEARS.index(boundary_year) - 0.5
        ax.axvline(x, color="#6F7D86", linewidth=0.55, alpha=0.85)
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(
            "Annual strict-set publication workload (1995–2026 YTD)"
            if is_en
            else "严格集逐年文献工作量（1995–2026 年，2026 为年内截至）",
            loc="left",
            pad=7,
        )
    if panel:
        panel_label(ax, panel, x=-0.105 if is_en else -0.09, y=1.075)
    return image


def add_heat_colorbar(fig: plt.Figure, image, ax: plt.Axes, lang: str, *, pad: float) -> None:
    cbar = fig.colorbar(
        image,
        ax=ax,
        orientation="horizontal",
        fraction=0.085,
        pad=pad,
        aspect=55,
        ticks=HEAT_TICKS,
        spacing="uniform",
    )
    cbar.ax.set_xticklabels(HEAT_LABELS)
    cbar.ax.tick_params(labelsize=5.2, length=0, pad=1.2)
    cbar.outline.set_visible(True)
    cbar.outline.set_linewidth(0.45)
    cbar.outline.set_edgecolor("#8F9AA1")
    cbar.set_label("Records per task-year, n" if lang == "EN" else "每任务-年度文献数，n", fontsize=5.8, labelpad=2)


def annual_heatmap_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    fig = plt.figure(figsize=(mm(180), mm(103)))
    ax = fig.add_axes([0.185 if is_en else 0.165, 0.305, 0.79 if is_en else 0.81, 0.59])
    image = draw_annual_heatmap(ax, lang, title=True, panel="c", label_zeros=True)
    add_heat_colorbar(fig, image, ax, lang, pad=0.28)
    note = (
        "Current screened A1–A7 corpus only; proposed A8–A10 families require retrospective screening before counting. "
        "OpenAlex + Europe PMC + arXiv; deduplicated strict title-explicit set; cutoff 6 Aug 2026."
        if is_en
        else "仅展示当前已完成筛选的 A1–A7 语料；建议新增的 A8–A10 须完成回溯筛选后方可计数。"
        "OpenAlex + Europe PMC + arXiv；跨库去重严格题名集；截至 2026-08-06。"
    )
    fig.text(0.012, 0.025, note, fontsize=5.25, color=COL["muted"], ha="left", va="bottom", wrap=True)
    return save_bundle(fig, f"Fig5c_active_annual_workload_{lang}")


def log1p_position(values) -> np.ndarray:
    return np.log10(np.asarray(values, dtype=float) + 1.0)


LOG_TICKS = np.array([0, 1, 3, 10, 30, 100, 300])
LOG_TICK_POS = log1p_position(LOG_TICKS)


def retrieval_legend(lang: str) -> list[Line2D]:
    return [
        Line2D(
            [0], [0], marker="o", linestyle="none", markersize=4.2,
            markerfacecolor=COL["ink"], markeredgecolor=COL["ink"],
            label="Strict title-explicit set" if lang == "EN" else "严格题名集",
        ),
        Line2D(
            [0], [0], marker="o", linestyle="none", markersize=4.5,
            markerfacecolor="white", markeredgecolor=COL["ink"], markeredgewidth=0.9,
            label="Broad title/abstract set" if lang == "EN" else "宽题名-摘要集",
        ),
    ]


def active_landscape_annual_figure(lang: str) -> list[Path]:
    is_en = lang == "EN"
    active_tasks = TASKS[TASKS["class_code"].eq("A")].copy()
    fig = plt.figure(figsize=(mm(180), mm(218)))
    gs = fig.add_gridspec(
        3,
        2,
        height_ratios=[0.82, 1.24, 0.60],
        width_ratios=[1.02, 1.12],
        left=0.185 if is_en else 0.165,
        right=0.975,
        top=0.945,
        bottom=0.065,
        wspace=0.36,
        hspace=0.60,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])
    ax_d = fig.add_subplot(gs[2, :])

    # a — current seven searched task families.
    sub = active_tasks.sort_values(["core", "expanded", "code"], ascending=[False, False, True]).reset_index(drop=True)
    y = np.arange(len(sub))[::-1]
    sx = log1p_position(sub["core"])
    bx = log1p_position(sub["expanded"])
    for yy, x1, x2, (_, row) in zip(y, sx, bx, sub.iterrows()):
        ax_a.plot([x1, x2], [yy, yy], color=tint(COL["A"], 0.58), lw=3.0, solid_capstyle="round")
        ax_a.scatter([x1], [yy], s=18, color=COL["A"], edgecolor="white", linewidth=0.4, zorder=3)
        ax_a.scatter([x2], [yy], s=21, facecolor="white", edgecolor=COL["A"], linewidth=0.8, zorder=4)
        ax_a.text(max(x1, x2) + 0.045, yy, f"{int(row['core'])} / {int(row['expanded'])}",
                  va="center", ha="left", fontsize=5.25)
    labels = [f"{row.code}  {wrap(COMPACT[lang][row.code], 22 if is_en else 13)}" for _, row in sub.iterrows()]
    ax_a.set_yticks(y, labels)
    ax_a.tick_params(axis="y", length=0, pad=4.5, labelsize=5.7)
    ax_a.set_xlim(-0.06, 3.18)
    ax_a.set_xticks(LOG_TICK_POS, [str(v) for v in LOG_TICKS])
    ax_a.set_xlabel("Records, n (log$_{10}$(n + 1))" if is_en else "文献记录数，n（log$_{10}$(n + 1)）")
    clean_axis(ax_a, "x")
    ax_a.spines["left"].set_visible(False)
    ax_a.set_title("Current searched workload by task" if is_en else "当前已检索任务的累计工作量", loc="left")
    panel_label(ax_a, "a", x=-0.23 if is_en else -0.20, y=1.08)

    # b — annual trajectory.
    years_array = np.asarray(YEARS)
    series = {
        "A1": ANNUAL[ANNUAL["task_code"].eq("A1")].set_index("year")["core_records"].reindex(YEARS, fill_value=0),
        "A2": ANNUAL[ANNUAL["task_code"].eq("A2")].set_index("year")["core_records"].reindex(YEARS, fill_value=0),
        "A3–A7": ANNUAL[ANNUAL["task_code"].isin(CODES[2:])].groupby("year")["core_records"].sum().reindex(YEARS, fill_value=0),
    }
    line_labels = {
        "EN": {"A1": "A1 Ultrasound", "A2": "A2 Endoscopy", "A3–A7": "A3–A7 Other current tasks"},
        "ZH": {"A1": "A1 超声", "A2": "A2 内镜", "A3–A7": "A3–A7 其余当前任务"},
    }[lang]
    line_colors = {"A1": COL["A"], "A2": COL["A2"], "A3–A7": COL["emerging"]}
    for key, values in series.items():
        complete = years_array <= 2025
        ax_b.plot(years_array[complete], values.to_numpy()[complete], color=line_colors[key], lw=1.15,
                  label=line_labels[key], zorder=2)
        ax_b.plot(years_array[-2:], values.to_numpy()[-2:], color=line_colors[key], lw=1.15,
                  linestyle=(0, (3, 2)), zorder=2)
        ax_b.scatter([2026], [values.loc[2026]], s=11, color=line_colors[key], zorder=3)
    ax_b.axvline(2025.5, color="#A7A7A7", lw=0.6, linestyle=(0, (2, 2)))
    ax_b.set_xlim(1995, 2026.55)
    ax_b.set_ylim(bottom=0)
    ax_b.set_xticks([1995, 2000, 2005, 2010, 2015, 2020, 2025])
    ax_b.set_ylabel("Strict-set records per year" if is_en else "严格集年度文献数")
    clean_axis(ax_b, "y")
    ax_b.legend(frameon=False, loc="upper left", ncol=1, handlelength=2.0, borderaxespad=0.2)
    ax_b.text(2026.20, ax_b.get_ylim()[1] * 0.50, "2026\nYTD", rotation=90, ha="left", va="center",
              fontsize=5.3, color=COL["muted"])
    ax_b.set_title("Annual publication trajectory" if is_en else "年度发表轨迹", loc="left")
    panel_label(ax_b, "b", x=-0.16, y=1.08)

    # c — every calendar year, not publication periods.
    image = draw_annual_heatmap(ax_c, lang, title=True, panel="c", label_zeros=True)
    add_heat_colorbar(fig, image, ax_c, lang, pad=0.25)

    # d — scope and concentration notes.
    strict_total = int(active_tasks["core"].sum())
    broad_total = int(active_tasks["expanded"].sum())
    task_shares = np.array([276, 137, strict_total - 276 - 137]) / strict_total * 100
    annual_total = ANNUAL.groupby("year")["core_records"].sum()
    time_values = np.array([
        int(annual_total.loc[annual_total.index <= 2020].sum()),
        int(annual_total.loc[(annual_total.index >= 2021) & (annual_total.index <= 2025)].sum()),
        int(annual_total.loc[annual_total.index == 2026].sum()),
    ])
    time_shares = time_values / strict_total * 100
    ax_d.set_xlim(0, 100)
    ax_d.set_ylim(0, 2.85)
    ax_d.axis("off")
    ax_d.text(0, 2.77,
              f"Strict set n={strict_total:,}   |   Broad set n={broad_total:,}"
              if is_en else f"严格集 n={strict_total:,}   |   宽检索集 n={broad_total:,}",
              ha="left", va="top", fontsize=6.8, fontweight="semibold")
    specs = [
        (1.89, task_shares, [COL["A"], COL["A2"], "#9A9A9A"], ["A1", "A2", "A3–A7"],
         "Current A1–A7 task mix" if is_en else "当前 A1–A7 任务构成"),
        (1.06, time_shares, ["#9A9A9A", COL["A"], tint(COL["A"], 0.48)],
         ["≤2020", "2021–25", "2026 YTD"],
         "Publication-time mix" if is_en else "发表时间构成"),
    ]
    for y0, shares, colors, bar_labels, heading in specs:
        ax_d.text(0, y0 + 0.34, heading, ha="left", va="bottom", fontsize=5.9, fontweight="semibold")
        left = 0.0
        for share, color, label in zip(shares, colors, bar_labels):
            ax_d.add_patch(Rectangle((left, y0), share, 0.28, facecolor=color, edgecolor="white", linewidth=0.5))
            if share >= 9:
                text_color = COL["ink"] if color == tint(COL["A"], 0.48) else "white"
                ax_d.text(left + share / 2, y0 + 0.14, f"{label}  {share:.1f}%", ha="center", va="center",
                          fontsize=5.0, color=text_color, fontweight="semibold")
            left += share
    scope_note = (
        "Scope warning: panels a–d quantify the completed A1–A7 search only. The evidence-based taxonomy audit proposes A1–A10; "
        "A8–A10 must be searched and screened retrospectively before they can be added to this figure."
        if is_en
        else "口径提示：a–d 面板仅量化已完成的 A1–A7 检索。证据审计建议扩展为 A1–A10；"
        "A8–A10 必须完成回溯检索和筛选后才能加入本图。"
    )
    ax_d.text(0, 0.45, scope_note, ha="left", va="top", fontsize=5.55, color=COL["warning"], wrap=True)
    ax_d.set_title("Concentration and counting scope" if is_en else "集中度与计数口径", loc="left")
    panel_label(ax_d, "d", x=-0.105 if is_en else -0.09, y=1.08)

    fig.legend(handles=retrieval_legend(lang), frameon=False, ncol=2, loc="upper right",
               bbox_to_anchor=(0.975, 0.995), handletextpad=0.4, columnspacing=1.0)
    foot = (
        "Counts are deduplicated publication records, not systems or trials. One primary task and earliest plausible public year per work; cutoff 6 Aug 2026."
        if is_en
        else "计数为跨库去重文献，并非系统或临床试验；每项工作唯一归入主要任务并采用最早合理公开年份；截至 2026-08-06。"
    )
    fig.text(0.012, 0.018, foot, fontsize=5.2, color=COL["muted"], ha="left")
    return save_bundle(fig, f"Fig5_active_observational_landscape_annual_{lang}")


REVISED_TASKS = [
    # Active observational sensing: 10.
    ("A1", "A", "Robotic ultrasound / sonography", "机器人超声 / 超声扫查", "Retained", "保留"),
    ("A2", "A", "Robotic endoscopic search / navigation", "机器人内镜搜索 / 导航", "Retained", "保留"),
    ("A3", "A", "Robotic OCT / ophthalmic scanning", "机器人 OCT / 眼科扫描", "Narrowed after split", "拆分后收窄"),
    ("A4", "A", "Robotic dermoscopy / skin scanning", "机器人皮肤镜 / 皮肤扫描", "Retained", "保留"),
    ("A5", "A", "Robotic auscultation", "机器人听诊", "Retained", "保留"),
    ("A6", "A", "Robotic otoscopy / oral-ENT examination", "机器人耳镜 / 口腔-耳鼻喉检查", "Retained", "保留"),
    ("A7", "A", "Robotic optical / spectral / thermal scanning", "机器人光学 / 光谱 / 热成像扫描", "Boundary refinement", "边界收紧"),
    ("A8", "A", "Robotic ionizing-radiation / nuclear imaging acquisition", "机器人电离辐射 / 核医学成像采集", "New family", "新增任务"),
    ("A9", "A", "Robotic microscopy / confocal endomicroscopy", "机器人显微 / 共聚焦内显微扫描", "Split from over-broad A3", "由过宽的 A3 拆出"),
    ("A10", "A", "Embodied non-contact vital-sign monitoring", "具身式非接触生命体征监测", "New family", "新增任务"),
    # Response-based interactive diagnosis: 12.
    ("R1", "R", "Robotic palpation", "机器人触诊", "Retained", "保留"),
    ("R2", "R", "Robotic elastography / stiffness mapping", "机器人弹性检测 / 刚度成像", "Retained", "保留"),
    ("R3", "R", "Robotic joint provocation / laxity testing", "机器人关节激发 / 松弛度检测", "Retained", "保留"),
    ("R4", "R", "Robotic percussion", "机器人叩诊", "Retained", "保留"),
    ("R5", "R", "Robotic deep-tendon reflex testing", "机器人腱反射检测", "Retained", "保留"),
    ("R6", "R", "Robotic TMS motor-response testing", "机器人 TMS 运动响应检测", "Retained", "保留"),
    ("R7", "R", "Robotic nerve-conduction / electrical-response testing", "机器人神经传导 / 电刺激响应检测", "Retained", "保留"),
    ("R8", "R", "Robotic tonometry / indentation response", "机器人眼压 / 压入响应检测", "Retained", "保留"),
    ("R9", "R", "Robotic tone, spasticity, ROM and strength assessment", "机器人肌张力、痉挛、关节活动度与力量评估", "New family", "新增任务"),
    ("R10", "R", "Robot-based sensorimotor / proprioceptive assessment", "机器人感觉运动 / 本体感觉评估", "New family", "新增任务"),
    ("R11", "R", "Robot-supported balance / gait perturbation assessment", "机器人平衡 / 步态扰动评估", "New family", "新增任务"),
    ("R12", "R", "Automated vestibular / oculomotor provocation testing", "自动化前庭 / 眼动激发检测", "New family", "新增任务"),
    # Sample-based interactive diagnosis: 11.
    ("S1", "S", "Robotic vascular blood collection", "机器人血管采血", "Retained; broaden vocabulary", "保留并扩充检索词"),
    ("S2", "S", "Robotic swab / brush collection", "机器人拭子 / 刷检采样", "Retained", "保留"),
    ("S3", "S", "Robotic bronchoscopic biopsy / TBNA", "机器人支气管镜活检 / TBNA", "Retained", "保留"),
    ("S4", "S", "Robotic prostate biopsy", "机器人前列腺活检", "Retained", "保留"),
    ("S5", "S", "Robotic percutaneous core-needle biopsy", "机器人经皮粗针活检", "Retained; exclude CNS stereotaxy", "保留；排除中枢立体定向"),
    ("S6", "S", "Robotic GI endoscopic / capsule tissue sampling", "机器人消化内镜 / 胶囊组织采样", "Retained; broaden vocabulary", "保留并扩充检索词"),
    ("S7", "S", "Robotic FNA / FNB including EUS-guided sampling", "机器人 FNA / FNB（含 EUS 引导）", "Retained; broaden vocabulary", "保留并扩充检索词"),
    ("S8", "S", "Robotic lumbar puncture / CSF sampling", "机器人腰椎穿刺 / 脑脊液采样", "Retained", "保留"),
    ("S9", "S", "Robotic bone-marrow biopsy / aspiration", "机器人骨髓活检 / 抽吸", "Narrowed after split", "拆分后收窄"),
    ("S10", "S", "Robotic body-cavity fluid aspiration", "机器人体腔液体穿刺抽吸", "Split from S9", "由 S9 拆出"),
    ("S11", "S", "Robot-assisted stereotactic CNS biopsy", "机器人辅助立体定向中枢神经系统活检", "New family", "新增任务"),
]

AUDIT_ROWS = [
    (
        "A", "Missing family", "漏项", "Add A8", "新增 A8",
        "Robotic X-ray/CT and gamma/SPECT acquisition", "机器人 X-ray/CT 与 gamma/SPECT 采集",
        "Confirmed; combine at the action-family level and separate by modality at the application level.",
        "已证实；动作层合并，成像模态作为应用层细分。",
        "Robotic X-ray viewfinding/collimation achieved 84% end-to-end success in a cadaver study; robot-mounted gamma cameras also exist.",
        "机器人 X-ray 视点搜索/准直在尸体实验中端到端成功率为 84%；亦已有机器人臂搭载 gamma 相机。",
        "https://arxiv.org/abs/2412.08020 | https://pmc.ncbi.nlm.nih.gov/articles/PMC4209015/",
    ),
    (
        "A", "Mixed boundary", "边界混合", "Split A3 → A3 + A9", "拆分 A3 → A3 + A9",
        "Robotic microscopy / confocal endomicroscopy", "机器人显微 / 共聚焦内显微扫描",
        "Confirmed split: the present A3 label is ophthalmic/OCT-specific but its corpus already contains microscopy and non-ophthalmic work.",
        "已证实需拆分：当前 A3 标签偏眼科/OCT，但语料已含显微及非眼科工作。",
        "Semi-autonomous pCLE retinal scanning uses image-based control to optimize focus and mosaic coverage.",
        "半自主 pCLE 视网膜扫描利用图像控制优化对焦与拼接覆盖。",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC7906249/",
    ),
    (
        "A", "Missing family", "漏项", "Add A10", "新增 A10",
        "Embodied non-contact vital-sign monitoring", "具身式非接触生命体征监测",
        "Confirmed, with both mobile clinical prototypes and active geometry regulation.",
        "已证实，已有移动临床原型和主动几何调节工作。",
        "A mobile robot measured contactless vital signs; ActiveVital actively aligns robot-mounted mmWave radar and markedly reduced respiration/heart-rate error.",
        "移动机器人已实现非接触生命体征测量；ActiveVital 主动调整毫米波雷达几何并显著降低呼吸/心率误差。",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC9096356/ | https://arxiv.org/abs/2606.30275",
    ),
    (
        "A", "Search-boundary issue", "检索边界问题", "Refine A7", "收紧 A7",
        "Optical/spectral/thermal surface sensing", "光学/光谱/热成像表面感知",
        "Retain, but exclude fluorescence-guided treatment/navigation papers that do not actively seek diagnostic observations.",
        "保留，但排除仅用于治疗/导航且不主动搜索诊断观察的荧光引导工作。",
        "Manual corpus audit found a substantial surgical-guidance component in the current A7 records.",
        "人工语料审计发现当前 A7 中有较多手术引导工作。",
        "Local screened corpus audit",
    ),
    (
        "A", "Scope-dependent candidate", "依口径候选", "Hold", "暂缓独立成类",
        "Automated ECG electrode placement", "自动化 ECG 电极放置",
        "Insufficient patient-side robotic literature to justify an independent family at present.",
        "当前患者侧机器人文献不足以支持独立任务族。",
        "Reassess after defining whether actuated diagnostic devices without a robot platform are in scope.",
        "需先界定无机器人平台的自动化诊断设备是否纳入，再复核。",
        "No qualifying primary series identified in targeted search",
    ),
    (
        "R", "Missing family", "漏项", "Add R9", "新增 R9",
        "Tone, spasticity, ROM and strength assessment", "肌张力、痉挛、关节活动度与力量评估",
        "Confirmed and clinically distinct from joint laxity provocation.",
        "已证实，且临床上不同于关节松弛度激发。",
        "Robot-based spasticity pilots and systematic technology reviews document controlled passive movement and objective resistance measurement.",
        "机器人痉挛评估试验及技术综述已记录受控被动运动与客观阻力测量。",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC4667530/ | https://pmc.ncbi.nlm.nih.gov/articles/PMC7570987/",
    ),
    (
        "R", "Missing family", "漏项", "Add R10", "新增 R10",
        "Sensorimotor / proprioceptive robot assessment", "感觉运动 / 本体感觉机器人评估",
        "Confirmed; uses controlled target/force/position perturbations and quantitative responses.",
        "已证实；通过受控目标、力或位置扰动并量化响应。",
        "KINARM-based tasks quantify corrective responses, sensory processing and proprioception.",
        "KINARM 类任务可量化纠正响应、感觉处理与本体感觉。",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC6350318/",
    ),
    (
        "R", "Missing family", "漏项", "Add R11", "新增 R11",
        "Balance / gait perturbation assessment", "平衡 / 步态扰动评估",
        "Confirmed, with a dedicated device taxonomy and clinical assessment literature.",
        "已证实，已有专门的设备分类和临床评估文献。",
        "A review classified nine robotic device types and described perturbation-based balance assessments during walking.",
        "综述归纳了 9 类机器人设备，并描述步行中的扰动式平衡评估。",
        "https://pubmed.ncbi.nlm.nih.gov/28806995/",
    ),
    (
        "R", "Missing family", "漏项", "Add R12", "新增 R12",
        "Vestibular / oculomotor provocation", "前庭 / 眼动激发检测",
        "Confirmed but niche; the defining action is controlled head motion followed by eye-response measurement.",
        "已证实但较小众；核心动作为受控头部运动并测量眼动响应。",
        "An automated head-motion system improved reliability and reduced operator dependence for vestibular reflex testing.",
        "自动头动系统提高前庭反射检测可靠性并降低操作者依赖。",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC6136842/",
    ),
    (
        "R", "Scope-dependent candidate", "依口径候选", "Hold", "暂缓独立成类",
        "Quantitative sensory and pupillary stimulus-response testing", "定量感觉及瞳孔刺激-响应检测",
        "Conceptually fits response-based diagnosis, but robotic embodiment evidence is currently too sparse or device-only.",
        "概念上属于响应式检测，但机器人具身证据目前过少或仅为设备自动化。",
        "Keep as a candidate until the inclusion rule for actuated diagnostic devices is fixed.",
        "待明确自动化诊断设备纳入规则后再决定。",
        "Scope decision required",
    ),
    (
        "S", "Missing family", "漏项", "Add S11", "新增 S11",
        "Stereotactic CNS biopsy", "立体定向中枢神经系统活检",
        "Confirmed and mature enough to require a separate family from generic percutaneous core biopsy.",
        "已证实，且成熟到应与通用经皮粗针活检分开。",
        "A 2024 meta-analysis included 27 studies/2,605 patients and estimated 98% diagnostic yield; the 2018 review found 14 case series/reports plus one cohort.",
        "2024 年荟萃分析纳入 27 项研究/2,605 例，估计诊断率 98%；2018 年综述已发现 14 个病例系列/报告和 1 个队列。",
        "https://pubmed.ncbi.nlm.nih.gov/39627622/ | https://link.springer.com/article/10.1007/s00381-018-3821-y",
    ),
    (
        "S", "Mixed boundary", "边界混合", "Split S9 → S9 + S10", "拆分 S9 → S9 + S10",
        "Bone marrow versus body-cavity fluid aspiration", "骨髓采样与体腔液体穿刺抽吸",
        "Confirmed split: tissue/marrow acquisition and pleural/peritoneal/synovial fluid aspiration differ in target, access and evidence.",
        "已证实需拆分：骨髓/组织获取与胸腹腔或关节液抽吸的目标、路径和证据不同。",
        "A 2025 system integrated ultrasound, robotic needle insertion and aspiration for autonomous thoracentesis in a pleural phantom.",
        "2025 年系统在胸腔模型中整合超声、机器人进针与抽吸，实现自主胸腔穿刺。",
        "https://researchportal.hw.ac.uk/en/publications/ultrasound-guided-robotic-aspirator-for-autonomous-thoracentesis-/",
    ),
    (
        "S", "Nested candidate", "可嵌套候选", "Merge into S6/S7/S1", "并入 S6/S7/S1",
        "Capsule liquid sampling, EUS-FNA/FNB, capillary blood", "胶囊液体采样、EUS-FNA/FNB、毛细血管采血",
        "Do not create separate action families yet; represent them as route/anatomy subtypes unless evidence volume and control architecture justify a split.",
        "暂不设独立动作任务族；先作为进入路径/解剖亚型，待证据量和控制架构支持后再拆分。",
        "This preserves orthogonality and avoids duplicating the same evidence-generating action.",
        "这样可保持正交性，避免重复计算同一种证据生成动作。",
        "Taxonomic design decision",
    ),
]


def write_taxonomy_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    revised = pd.DataFrame(
        REVISED_TASKS,
        columns=["code", "class_code", "task_en", "task_zh", "revision_status_en", "revision_status_zh"],
    )
    class_names_en = {
        "A": "Active observational sensing",
        "R": "Response-based interactive diagnosis",
        "S": "Sample-based interactive diagnosis",
    }
    class_names_zh = {
        "A": "主动观察式检测",
        "R": "响应式交互检测",
        "S": "采样式交互检测",
    }
    revised.insert(2, "class_en", revised["class_code"].map(class_names_en))
    revised.insert(3, "class_zh", revised["class_code"].map(class_names_zh))
    revised.to_csv(OUT_DIR / "revised_33_task_framework_bilingual.csv", index=False, encoding="utf-8-sig")

    audit = pd.DataFrame(
        AUDIT_ROWS,
        columns=[
            "class_code", "gap_type_en", "gap_type_zh", "decision_en", "decision_zh",
            "task_or_issue_en", "task_or_issue_zh", "assessment_en", "assessment_zh",
            "evidence_en", "evidence_zh", "source_urls",
        ],
    )
    audit.to_csv(OUT_DIR / "taxonomy_gap_audit_bilingual.csv", index=False, encoding="utf-8-sig")

    current_counts = {"A": 7, "R": 8, "S": 9}
    revised_counts = revised.groupby("class_code").size().to_dict()
    summary = pd.DataFrame(
        [
            {
                "class_code": code,
                "class_en": class_names_en[code],
                "class_zh": class_names_zh[code],
                "current_task_families": current_counts[code],
                "revised_task_families": revised_counts[code],
                "net_change": revised_counts[code] - current_counts[code],
            }
            for code in ("A", "R", "S")
        ]
    )
    summary.loc[len(summary)] = {
        "class_code": "Total",
        "class_en": "Total",
        "class_zh": "合计",
        "current_task_families": sum(current_counts.values()),
        "revised_task_families": sum(revised_counts.values()),
        "net_change": sum(revised_counts.values()) - sum(current_counts.values()),
    }
    summary.to_csv(OUT_DIR / "taxonomy_revision_summary_bilingual.csv", index=False, encoding="utf-8-sig")
    return revised, audit, summary


def write_annual_sources() -> pd.DataFrame:
    matrix_df = pd.DataFrame(MATRIX, columns=[str(year) for year in YEARS])
    matrix_df.insert(0, "task_zh", [COMPACT["ZH"][code] for code in CODES])
    matrix_df.insert(0, "task_en", [COMPACT["EN"][code] for code in CODES])
    matrix_df.insert(0, "task_code", CODES)
    matrix_df.to_csv(OUT_DIR / "source_data_active_annual_matrix_bilingual.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(SRC_DIR / "source_data_active_annual_counts_bilingual.csv", OUT_DIR / "source_data_active_annual_counts_bilingual.csv")
    return matrix_df


def write_documentation(revised: pd.DataFrame, audit: pd.DataFrame, summary: pd.DataFrame) -> None:
    audit_lines = [
        "# Taxonomy completeness audit / 细分任务完整性审计",
        "",
        "## Conclusion / 结论",
        "",
        "**EN.** The current 24-task set is not exhaustive. It is a high-precision searched working set whose rows mix sensing modality, anatomy and access route. A minimum evidence-supported revision expands the framework to 33 task families: A=10, R=12 and S=11. This is a defensible working taxonomy, not a claim that all future embodied diagnostic actions have been exhausted.",
        "",
        "**中.** 当前 24 个任务并不全面。它是一个偏高精度的已检索工作集，且任务行混合了传感模态、解剖部位和进入路径。基于现有证据的最小修订为 33 个任务族：A=10、R=12、S=11。这是一套可辩护的工作分类，而非声称已经穷尽未来所有具身诊断动作。",
        "",
        "## Recommended hierarchy / 建议层级",
        "",
        "1. **Level 1 / 一级：** evidence-generating action — observe, stimulate-and-read-response, or acquire a sample. / 证据生成动作——观察、刺激并读取响应、或获取样本。",
        "2. **Level 2 / 二级：** task family defined by the controlled action and evidence channel. / 由受控动作与证据通道定义的任务族。",
        "3. **Level 3 / 三级：** anatomy, access route, disease and clinical setting. / 解剖部位、进入路径、疾病与临床场景。",
        "",
        "This prevents the same paper from being duplicated merely because the anatomy or sensor modality differs. / 这样可避免仅因解剖部位或传感器模态不同而重复计入同一工作。",
        "",
        "## Revision summary / 修订汇总",
        "",
        "| Class / 大类 | Current / 当前 | Revised / 修订 | Net / 净增 |",
        "|---|---:|---:|---:|",
    ]
    for _, row in summary.iloc[:3].iterrows():
        audit_lines.append(
            f"| {row['class_code']} — {row['class_en']} / {row['class_zh']} | {int(row['current_task_families'])} | "
            f"{int(row['revised_task_families'])} | +{int(row['net_change'])} |"
        )
    audit_lines.extend(
        [
            f"| **Total / 合计** | **24** | **33** | **+9** |",
            "",
            "## Major additions and corrections / 主要新增与修正",
            "",
            "| Class | Decision / 决策 | Task or issue / 任务或问题 | Evidence status / 证据判断 |",
            "|---|---|---|---|",
        ]
    )
    for _, row in audit.iterrows():
        audit_lines.append(
            f"| {row['class_code']} | {row['decision_en']} / {row['decision_zh']} | "
            f"{row['task_or_issue_en']} / {row['task_or_issue_zh']} | {row['assessment_en']} / {row['assessment_zh']} |"
        )
    audit_lines.extend(
        [
            "",
            "## Counting implication / 对计数的影响",
            "",
            "**EN.** The annual heatmap in this package remains an A1–A7 figure because those seven families have a completed deduplication and screening workflow. Adding estimated counts for A8–A10 would create a non-comparable denominator. The correct next step is a retrospective rerun of the full search and screening protocol for all revised families.",
            "",
            "**中.** 本包中的逐年热力图仍为 A1–A7，因为只有这七个任务完成了统一的去重和筛选流程。若临时估算 A8–A10 并直接加入，会造成分母不可比。正确做法是按修订后的所有任务重新回溯检索和筛选。",
            "",
            "## Important current-corpus findings / 当前语料的重要发现",
            "",
            "- A3 contains microscopy and non-ophthalmic records although its label is OCT/ophthalmic; this is a label-boundary problem. / A3 的标签为 OCT/眼科，但已有显微和非眼科记录，说明边界需拆分。",
            "- R3 currently contains only a small knee-laxity cluster and misses spasticity, strength, balance and KINARM-style assessment. / R3 当前主要是少量膝关节松弛度工作，漏掉痉挛、力量、平衡及 KINARM 类评估。",
            "- S5 contains generic breast/lung/percutaneous biopsy work but did not retrieve the established stereotactic brain-biopsy literature. / S5 包含乳腺、肺和经皮活检，但未检出已成规模的立体定向脑活检文献。",
            "- Zero rows are not evidence of absence: several zeros reflect missing synonyms or route terms. / 零计数不等于不存在：若干零值来自同义词或进入路径检索词不足。",
            "",
            "## Representative primary/review evidence / 代表性原始研究与综述证据",
            "",
            "- Robotic X-ray viewfinding and collimation: https://arxiv.org/abs/2412.08020",
            "- Robotic gamma/SPECT acquisition: https://pmc.ncbi.nlm.nih.gov/articles/PMC4209015/",
            "- Semi-autonomous confocal endomicroscopy: https://pmc.ncbi.nlm.nih.gov/articles/PMC7906249/",
            "- Mobile contactless vital signs: https://pmc.ncbi.nlm.nih.gov/articles/PMC9096356/",
            "- Active geometry-aware vital signs: https://arxiv.org/abs/2606.30275",
            "- Robot-aided spasticity assessment: https://pmc.ncbi.nlm.nih.gov/articles/PMC4667530/",
            "- Robot-supported balance assessment: https://pubmed.ncbi.nlm.nih.gov/28806995/",
            "- Automated vestibular head impulse testing: https://pmc.ncbi.nlm.nih.gov/articles/PMC6136842/",
            "- Robot-assisted stereotactic brain-biopsy meta-analysis: https://pubmed.ncbi.nlm.nih.gov/39627622/",
            "- Autonomous robotic thoracentesis: https://researchportal.hw.ac.uk/en/publications/ultrasound-guided-robotic-aspirator-for-autonomous-thoracentesis-/",
            "",
            "Audit date / 审计日期: 2026-08-07.",
        ]
    )
    (OUT_DIR / "taxonomy_completeness_audit_bilingual.md").write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    methods = """# Annual workload method / 逐年工作量统计方法

## English

- Source databases: OpenAlex, Europe PMC and arXiv.
- Counting unit: one deduplicated scholarly work, DOI-first and then canonical-title deduplication.
- Assignment: each work contributes once to one primary task family.
- Year: earliest plausible public year after reconciling preprint and published versions.
- Heatmap set: strict title-explicit A1–A7 records only; 436 records in total.
- Time axis: one column for every calendar year from 1995 through 2026. The 2026 column is year-to-date and is not directly comparable with complete years.
- Scope: proposed A8–A10 additions are shown in the taxonomy audit but are not counted until the same retrieval, deduplication and screening protocol is rerun retrospectively.
- The chart measures publication workload, not unique robot systems, clinical trials, regulatory approvals or clinical deployment.

## 中文

- 数据库：OpenAlex、Europe PMC 和 arXiv。
- 计数单位：一篇跨库去重学术工作；先按 DOI，再按规范化题名去重。
- 任务归属：每项工作只计入一个主要任务族一次。
- 年份：协调预印本与正式发表版本后采用最早合理公开年份。
- 热力图口径：仅使用严格题名集 A1–A7，共 436 篇。
- 时间轴：1995–2026 每个自然年一列；2026 为年内截至，不可与完整年份直接比较。
- 范围：建议新增的 A8–A10 仅在分类审计中展示；需按同一检索、去重和筛选协议回溯运行后才能计数。
- 图表反映发表工作量，而不是机器人系统数、临床试验数、监管批准数或临床部署数。
"""
    (OUT_DIR / "annual_workload_method_bilingual.md").write_text(methods, encoding="utf-8")

    captions = """# Revised figure captions / 修订图注

## Figure 5c. Annual active-observational-sensing workload / 主动观察式检测逐年工作量

**EN.** Exact annual counts in the strict title-explicit set for the seven currently screened active-observation task families, 1995–2026. Each deduplicated work contributes once to its primary task and earliest plausible public year. Zero is white and successively larger bins are strictly darker. The 2026 column is year-to-date. The proposed A8–A10 task families are excluded pending a retrospective search and screening rerun, so the figure retains a comparable denominator.

**中.** 1995–2026 年当前七个已完成筛选的主动观察式任务在严格题名集中的逐年精确计数。每篇去重工作只按主要任务和最早合理公开年份计数一次。0 为白色，数量等级越高颜色严格越深。2026 为年内截至。建议新增的 A8–A10 尚待回溯检索与筛选，因此暂不加入，以保持分母可比。

## Figure 5. Active-observation workload, annual trajectory and scope / 主动观察式检测工作量、年度轨迹与计数口径

**EN.** (a) Strict and broad retrieval counts for the seven currently searched task families. (b) Annual strict-set trajectory. (c) Exact task-by-year strict-set counts for every calendar year. (d) Task concentration, publication-time mix and the counting-scope warning. A1 robotic ultrasound and A2 robotic endoscopy jointly account for 94.7% of the current 436-record strict set. Counts quantify publications, not deployed systems or trials. The taxonomy audit proposes A1–A10; the new families require retrospective screening before quantitative integration.

**中.** （a）当前七个已检索任务的严格集与宽检索集计数。（b）严格集年度轨迹。（c）每个自然年的任务-年度精确计数。（d）任务集中度、发表时间结构及计数口径提示。A1 机器人超声与 A2 机器人内镜合计占当前 436 篇严格集的 94.7%。计数反映文献量而非部署系统数或临床试验数。分类审计建议扩展为 A1–A10；新增任务须完成回溯筛选后才能量化整合。
"""
    (OUT_DIR / "revised_figure_captions_bilingual.md").write_text(captions, encoding="utf-8")

    readme = """# Annual heatmap and taxonomy audit / 逐年热力图与分类审计

This focused correction package answers two questions: whether the current task taxonomy is complete, and how the publication-period heatmap changes when every year is shown.

本修订包集中回答两个问题：当前细分任务是否全面，以及把“发表时期”改为“逐年”后图表如何呈现。

## Key result / 核心结果

- The current 24-task set is not exhaustive. / 当前 24 任务并不全面。
- A minimum evidence-supported working revision contains 33 families: A=10, R=12, S=11. / 基于证据的最小工作修订为 33 个任务族：A=10、R=12、S=11。
- Annual figures keep the completed A1–A7 corpus and do not fabricate counts for proposed A8–A10. / 逐年图保留已完成的 A1–A7 语料，不为建议新增的 A8–A10 虚构计数。

## Main files / 主要文件

- `Fig5c_active_annual_workload_EN/ZH`: standalone annual heatmap, 180 mm, PDF/SVG/600-dpi PNG/TIFF.
- `Fig5_active_observational_landscape_annual_EN/ZH`: corrected full multi-panel figure.
- `taxonomy_completeness_audit_bilingual.md`: rationale and representative evidence.
- `revised_33_task_framework_bilingual.csv`: proposed A10/R12/S11 task framework.
- `taxonomy_gap_audit_bilingual.csv`: add/split/merge/hold decisions and source URLs.
- `source_data_active_annual_matrix_bilingual.csv`: exact 7 × 32 matrix used in the heatmap.
- `Taxonomy_Audit_and_Annual_Workload_Bilingual_2026-08-07.xlsx`: formatted audit workbook.
"""
    (OUT_DIR / "README_bilingual.md").write_text(readme, encoding="utf-8")

    payload = {
        "generated_at": "2026-08-07",
        "summary": summary.to_dict(orient="records"),
        "revised_tasks": revised.to_dict(orient="records"),
        "audit": audit.to_dict(orient="records"),
        "annual_long": ANNUAL.to_dict(orient="records"),
        "annual_matrix": [
            {
                "task_code": code,
                "task_en": COMPACT["EN"][code],
                "task_zh": COMPACT["ZH"][code],
                **{str(year): int(MATRIX[i, j]) for j, year in enumerate(YEARS)},
            }
            for i, code in enumerate(CODES)
        ],
    }
    (OUT_DIR / "workbook_payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def merge_pdf_packet(paths: list[Path]) -> Path:
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for path in paths:
        for page in PdfReader(str(path)).pages:
            writer.add_page(page)
    output = OUT_DIR / "Bilingual_Annual_Heatmap_and_Taxonomy_Audit_Figure_Packet_2026-08-07.pdf"
    tmp = output.with_name(f".{output.name}.writing")
    with tmp.open("wb") as handle:
        writer.write(handle)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(output)
    return output


def relative_luminance(color: str) -> float:
    channels = []
    for value in mcolors.to_rgb(color):
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def write_qc(pdf_paths: list[Path], revised: pd.DataFrame) -> None:
    from PIL import Image
    from pypdf import PdfReader

    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    record("Annual matrix shape", MATRIX.shape == (7, 32), f"shape={MATRIX.shape}")
    record("Annual strict-set total", int(MATRIX.sum()) == 436, f"total={int(MATRIX.sum())}")
    expected_rows = np.array([276, 137, 13, 1, 4, 0, 5])
    record("Annual row totals", np.array_equal(MATRIX.sum(axis=1), expected_rows),
           f"row_totals={MATRIX.sum(axis=1).tolist()}")
    class_counts = revised.groupby("class_code").size().to_dict()
    record("Revised taxonomy", len(revised) == 33 and class_counts == {"A": 10, "R": 12, "S": 11},
           f"tasks={len(revised)}; A/R/S={class_counts.get('A')}/{class_counts.get('R')}/{class_counts.get('S')}")
    luminance = [relative_luminance(c) for c in HEAT_COLORS]
    record("Heatmap darkness monotonicity", all(a > b for a, b in zip(luminance, luminance[1:])),
           "relative luminance=" + ", ".join(f"{v:.3f}" for v in luminance))

    specs = {
        "Fig5c_active_annual_workload_EN": (180, 103),
        "Fig5c_active_annual_workload_ZH": (180, 103),
        "Fig5_active_observational_landscape_annual_EN": (180, 218),
        "Fig5_active_observational_landscape_annual_ZH": (180, 218),
    }
    for stem, (width_mm, height_mm) in specs.items():
        expected_px = (round(width_mm / 25.4 * 600), round(height_mm / 25.4 * 600))
        for ext in ("png", "tiff"):
            path = OUT_DIR / f"{stem}.{ext}"
            with Image.open(path) as image:
                dpi = image.info.get("dpi", (0, 0))
                size_ok = all(abs(a - b) <= 1 for a, b in zip(image.size, expected_px))
                dpi_ok = all(abs(float(v) - 600) <= 0.1 for v in dpi)
                compression_ok = ext != "tiff" or image.info.get("compression") == "tiff_lzw"
                record(f"{path.name} raster", size_ok and dpi_ok and compression_ok,
                       f"pixels={image.size}; dpi={dpi}; compression={image.info.get('compression', 'n/a')}")
        pdf = OUT_DIR / f"{stem}.pdf"
        page = PdfReader(str(pdf)).pages[0]
        actual = (float(page.mediabox.width) / 72 * 25.4, float(page.mediabox.height) / 72 * 25.4)
        record(f"{pdf.name} physical size", abs(actual[0] - width_mm) <= 0.15 and abs(actual[1] - height_mm) <= 0.15,
               f"{actual[0]:.2f} × {actual[1]:.2f} mm")
        svg = OUT_DIR / f"{stem}.svg"
        try:
            ET.parse(svg)
            valid_svg = True
        except ET.ParseError:
            valid_svg = False
        record(f"{svg.name} XML", valid_svg, "valid SVG XML" if valid_svg else "parse failure")

    packet = OUT_DIR / "Bilingual_Annual_Heatmap_and_Taxonomy_Audit_Figure_Packet_2026-08-07.pdf"
    record("Combined PDF", len(PdfReader(str(packet)).pages) == len(pdf_paths),
           f"pages={len(PdfReader(str(packet)).pages)}")
    font_check = subprocess.run(
        ["pdffonts", str(packet)],
        capture_output=True,
        text=True,
        check=False,
    )
    font_ok = (
        font_check.returncode == 0
        and "Syntax Warning" not in font_check.stderr
        and "CID TrueType" in font_check.stdout
        and "yes yes yes" in font_check.stdout
    )
    record(
        "PDF font embedding",
        font_ok,
        "embedded, subsetted Unicode CID TrueType fonts; no parser warnings"
        if font_ok
        else (font_check.stderr.strip() or "unexpected pdffonts output"),
    )
    overall = all(item["passed"] for item in checks)
    payload = {"overall_passed": overall, "checks": checks}
    (OUT_DIR / "quality_control_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Quality control / 质量控制",
        "",
        f"**Overall / 总体: {'PASS / 通过' if overall else 'FAIL / 未通过'}**",
        "",
        "| Check / 检查 | Result / 结果 | Detail / 详情 |",
        "|---|---:|---|",
    ]
    for item in checks:
        lines.append(f"| {item['check']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |")
    (OUT_DIR / "quality_control_report_bilingual.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not overall:
        raise RuntimeError("Quality control failed")


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if path.is_file() and path.name != "file_manifest.csv":
            rows.append(
                {
                    "file": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    pd.DataFrame(rows).to_csv(OUT_DIR / "file_manifest.csv", index=False, encoding="utf-8-sig")


def cleanup() -> None:
    for path in OUT_DIR.glob(".*.writing"):
        path.unlink(missing_ok=True)


def main() -> None:
    cleanup()
    for lang in ("EN", "ZH"):
        annual_heatmap_figure(lang)
        active_landscape_annual_figure(lang)
    revised, audit, summary = write_taxonomy_tables()
    write_annual_sources()
    write_documentation(revised, audit, summary)
    shutil.copy2(Path(__file__), OUT_DIR / Path(__file__).name)
    pdf_paths = [
        OUT_DIR / "Fig5c_active_annual_workload_EN.pdf",
        OUT_DIR / "Fig5c_active_annual_workload_ZH.pdf",
        OUT_DIR / "Fig5_active_observational_landscape_annual_EN.pdf",
        OUT_DIR / "Fig5_active_observational_landscape_annual_ZH.pdf",
    ]
    packet = merge_pdf_packet(pdf_paths)
    write_qc(pdf_paths, revised)
    cleanup()
    write_manifest()
    print(json.dumps({"output_directory": str(OUT_DIR), "packet": str(packet)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
