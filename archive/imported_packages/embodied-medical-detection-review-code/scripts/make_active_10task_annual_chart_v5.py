#!/usr/bin/env python3
"""Draw publication-style annual heatmaps for ten active-observation tasks."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "active_observational_10task_annual_v5_2026-08-07"
)
ANNUAL = pd.read_csv(OUT_DIR / "source_data_active_annual_counts_10task_bilingual.csv")
TOTALS = pd.read_csv(OUT_DIR / "source_data_active_cumulative_totals_10task_bilingual.csv")

YEARS = list(range(1995, 2027))
CODES = [f"A{i}" for i in range(1, 11)]
CUTOFF = "6 Aug 2026"


def mm(value: float) -> float:
    return value / 25.4


FONT_DIR = ROOT / "tmp" / "08e9490e7d8f" / "fonts" / "merged"
FONT_REGULAR = FONT_DIR / "NotoSansSC-Regular.ttf"
FONT_MEDIUM = FONT_DIR / "NotoSansSC-Medium.ttf"
for font_path in (FONT_REGULAR, FONT_MEDIUM):
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
        "font.size": 7.0,
        "axes.titlesize": 9.2,
        "axes.titleweight": "semibold",
        "axes.labelsize": 7.0,
        "xtick.labelsize": 5.2,
        "ytick.labelsize": 6.4,
        "axes.linewidth": 0.6,
        "axes.edgecolor": "#333333",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
    }
)

INK = "#202428"
MUTED = "#626B73"
GRID = "#DCE2E6"
ACCENT = "#0B5C8E"

# Monotonic blue scale matched to the cleaner reference figure.  Zero is
# white; every larger bin is strictly darker.
HEAT_COLORS = [
    "#FFFFFF",
    "#EAF2F8",
    "#CFE1EF",
    "#9FC5DF",
    "#6AA6CF",
    "#337FB8",
    "#0B4F8A",
]
HEAT_BOUNDS = [-0.5, 0.5, 2.5, 5.5, 10.5, 20.5, 40.5, 1000]
HEAT_TICKS = [0, 1.5, 4, 8, 15, 30, 60]
HEAT_LABELS = ["0", "1–2", "3–5", "6–10", "11–20", "21–40", "≥41"]
CMAP = mcolors.ListedColormap(HEAT_COLORS)
NORM = mcolors.BoundaryNorm(HEAT_BOUNDS, CMAP.N)


LABELS = {
    "EN": {
        "A1": "Ultrasound",
        "A2": "Endoscopy",
        "A3": "OCT / ophthalmic imaging",
        "A4": "Dermoscopy",
        "A5": "Auscultation",
        "A6": "Otoscopy / oral–ENT",
        "A7": "Optical / spectral / thermal",
        "A8": "X-ray / CT / nuclear",
        "A9": "Microscopy / endomicroscopy",
        "A10": "Vital-sign acquisition",
    },
    "ZH": {
        "A1": "超声",
        "A2": "内镜",
        "A3": "OCT / 眼科成像",
        "A4": "皮肤镜",
        "A5": "听诊",
        "A6": "耳镜 / 口腔–耳鼻喉",
        "A7": "光谱 / 热成像扫描",
        "A8": "X-ray / CT / 核医学",
        "A9": "显微 / 内显微",
        "A10": "生命体征采集",
    },
}


def matrix() -> np.ndarray:
    pivot = (
        ANNUAL.pivot(index="task_code", columns="year", values="publication_records")
        .reindex(index=CODES, columns=YEARS, fill_value=0)
        .fillna(0)
    )
    return pivot.to_numpy(dtype=int)


MATRIX = matrix()
TOTAL_MAP = TOTALS.set_index("task_code")["cumulative_records"].to_dict()


def wrap_label(label: str, lang: str) -> str:
    if lang == "ZH":
        # Chinese labels are already compact; keep meaningful slash groups intact.
        return label
    return "\n".join(
        textwrap.wrap(label, width=31, break_long_words=False, break_on_hyphens=False)
    )


def atomic_savefig(fig: plt.Figure, path: Path, *, fmt: str, **kwargs) -> None:
    tmp = path.with_name(f".{path.name}.writing")
    with tmp.open("wb") as handle:
        fig.savefig(handle, format=fmt, **kwargs)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)


def save_bundle(fig: plt.Figure, stem: str) -> list[Path]:
    paths = []
    for ext, kwargs in (
        ("pdf", {"metadata": {"Creator": "Python/Matplotlib", "Title": stem}}),
        ("svg", {"metadata": {"Creator": "Python/Matplotlib"}}),
        ("png", {"dpi": 600, "metadata": {"Title": stem}}),
        ("tiff", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}}),
    ):
        path = OUT_DIR / f"{stem}.{ext}"
        atomic_savefig(fig, path, fmt=ext, **kwargs)
        paths.append(path)
    plt.close(fig)
    return paths


def draw_heatmap(lang: str) -> list[Path]:
    is_en = lang == "EN"
    # The height grows relative to the seven-row reference so all ten rows keep
    # a comfortable physical pitch.  The main panel remains visually wide.
    fig = plt.figure(figsize=(mm(180), mm(101)))
    left = 0.205 if is_en else 0.153
    right = 0.985
    ax = fig.add_axes([left, 0.335, right - left, 0.535])

    image = ax.imshow(
        MATRIX,
        cmap=CMAP,
        norm=NORM,
        aspect="auto",
        interpolation="none",
    )

    row_labels = [f"{code}  {LABELS[lang][code]}" for code in CODES]
    ax.set_yticks(np.arange(len(CODES)), row_labels)
    ax.tick_params(axis="y", length=0, pad=7.0, labelsize=5.85 if is_en else 6.15)

    year_labels = [str(year) if year != 2026 else "2026\nYTD" for year in YEARS]
    ax.set_xticks(np.arange(len(YEARS)), year_labels, rotation=90, ha="center", va="top")
    ax.tick_params(axis="x", length=0, pad=2.0, labelsize=4.25)

    # Light-grey zero labels make every annual cell legible without introducing
    # a visible background grid, exactly as in the reference figure.
    for row in range(MATRIX.shape[0]):
        for col in range(MATRIX.shape[1]):
            value = int(MATRIX[row, col])
            if value == 0:
                color = "#B4B9BD"
                weight = "normal"
            elif value >= 11:
                color = "white"
                weight = "semibold"
            else:
                color = INK
                weight = "normal"
            ax.text(
                col,
                row,
                str(value),
                ha="center",
                va="center",
                fontsize=3.55 if value == 0 else 3.75,
                fontweight=weight,
                color=color,
            )

    ax.set_xticks(np.arange(-0.5, len(YEARS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(CODES), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.65)
    ax.tick_params(which="minor", bottom=False, left=False)
    for boundary_year in (2000, 2005, 2010, 2015, 2020, 2025):
        ax.axvline(YEARS.index(boundary_year) - 0.5, color="#71808A", lw=0.55, alpha=0.82)
    for spine in ax.spines.values():
        spine.set_visible(False)

    title = (
        "Annual strict-set publication workload  (1995–2026; 2026 year-to-date)"
        if is_en
        else "严格集逐年文献工作量（1995–2026 年，2026 为年内截至）"
    )
    fig.text(left, 0.956, title, ha="left", va="top", fontsize=9.0, fontweight="semibold", color=INK)
    fig.text(0.024, 0.922, "c", ha="left", va="top", fontsize=10.2, fontweight="semibold", color=INK)

    # A generous gap between year labels and legend keeps the panel airy.
    cax = fig.add_axes([left, 0.090, right - left, 0.027])
    cbar = fig.colorbar(
        image,
        cax=cax,
        orientation="horizontal",
        ticks=HEAT_TICKS,
        spacing="uniform",
    )
    cbar.ax.set_xticklabels(HEAT_LABELS)
    cbar.ax.tick_params(labelsize=5.2, length=0, pad=1.7)
    cbar.outline.set_linewidth(0.45)
    cbar.outline.set_edgecolor("#8A959D")
    cbar.set_label(
        "Records per task-year, n"
        if is_en
        else "每任务-年度文献数，n",
        fontsize=6.0,
        labelpad=2.5,
    )

    stem = f"Fig5c_active_annual_workload_10tasks_{lang}"
    return save_bundle(fig, stem)


def draw_annual_total(lang: str) -> list[Path]:
    """A compact companion figure showing the total annual trajectory."""
    is_en = lang == "EN"
    total_by_year = (
        ANNUAL.groupby("year")["publication_records"].sum().reindex(YEARS, fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(mm(180), mm(68)))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.80, bottom=0.29)
    colors = ["#4C91B8" if year < 2026 else "#B66950" for year in YEARS]
    ax.bar(YEARS, total_by_year.values, width=0.78, color=colors, edgecolor="white", linewidth=0.3)
    ax.plot(YEARS, total_by_year.values, color=ACCENT, lw=0.8, marker="o", ms=1.8, zorder=3)
    for year, value in total_by_year.items():
        if value > 0:
            ax.text(year, value + max(total_by_year.max() * 0.018, 0.7), str(int(value)),
                    ha="center", va="bottom", fontsize=4.3, color=INK)
    ax.axvline(2025.5, color="#A14B36", lw=0.9)
    ax.set_xlim(1994.35, 2026.65)
    ax.set_ylim(0, total_by_year.max() * 1.16)
    ax.set_xticks(YEARS, [str(year) if year != 2026 else "2026†" for year in YEARS], rotation=90)
    ax.tick_params(axis="x", length=0, labelsize=4.5)
    ax.set_ylabel("Records, n" if is_en else "文献数，n")
    ax.grid(axis="y", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_title(
        "Annual publication trajectory — all 10 active-observation tasks"
        if is_en
        else "年度发表轨迹——主动观察式检测全部 10 类任务",
        loc="left",
        pad=8,
    )
    fig.text(
        0.985,
        0.055,
        "†2026 YTD through 6 Aug" if is_en else "†2026 截至 8 月 6 日",
        ha="right",
        va="bottom",
        fontsize=5.2,
        color=MUTED,
    )
    stem = f"Fig5b_active_annual_total_10tasks_{lang}"
    return save_bundle(fig, stem)


def write_caption() -> None:
    text = """# Revised figure captions / 修订图注

**English — Fig. 5c.** Annual publication workload across ten active observational sensing task families. Cells report deduplicated publication records assigned to the earliest plausible public year; darker blue indicates a larger count, while zero-count cells are white with light-grey labels. Searches covered OpenAlex, Europe PMC, and arXiv. Inclusion required an embodied system to control the diagnostic sensor, viewpoint/contact, or acquisition trajectory. Linked preprint and journal versions were counted once. Data were current through 6 August 2026; therefore, 2026 is year-to-date.

**中文——图 5c。** 主动观察式检测十类任务的逐年文献工作量。单元格为按最早合理公开年份归入的跨库去重文献记录；蓝色越深表示数量越多，零值单元格为白色并以浅灰数字标示。检索覆盖 OpenAlex、Europe PMC 和 arXiv。纳入要求具身系统控制诊断传感器、视点/接触或采集轨迹；关联的预印本与期刊版本仅计一次。数据截至 2026 年 8 月 6 日，因此 2026 为年内截至数据。

**English — Fig. 5b.** Total annual publication trajectory for the same ten-family corpus. The 2026 bar is year-to-date and should not be compared directly with complete calendar years.

**中文——图 5b。** 同一十类任务语料的年度总发表轨迹。2026 柱为年内截至数据，不宜与完整年度直接比较。
"""
    (OUT_DIR / "figure_captions_bilingual.md").write_text(text, encoding="utf-8")


def main() -> None:
    for lang in ("EN", "ZH"):
        draw_heatmap(lang)
        draw_annual_total(lang)
    write_caption()
    print("Created bilingual 10-row heatmaps and annual-total companion figures")


if __name__ == "__main__":
    main()
