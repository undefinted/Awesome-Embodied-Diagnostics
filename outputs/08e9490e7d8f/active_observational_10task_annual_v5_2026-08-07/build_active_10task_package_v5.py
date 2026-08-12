#!/usr/bin/env python3
"""Build the bilingual workbook, PDF packet, QC report, and archive for v5."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd
from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "active_observational_10task_annual_v5_2026-08-07"
)

DEFS = OUT_DIR / "active_task_definitions_10_bilingual.csv"
ANNUAL = OUT_DIR / "source_data_active_annual_counts_10task_bilingual.csv"
MATRIX = OUT_DIR / "source_data_active_annual_matrix_10task_bilingual.csv"
TOTALS = OUT_DIR / "source_data_active_cumulative_totals_10task_bilingual.csv"
RECORDS = OUT_DIR / "included_active_10task_records.csv"
ADJUDICATION = OUT_DIR / "extension_A8_A10_core_candidate_adjudication.csv"


def build_workbook() -> Path:
    defs = pd.read_csv(DEFS)
    annual = pd.read_csv(ANNUAL)
    matrix = pd.read_csv(MATRIX)
    totals = pd.read_csv(TOTALS)
    records = pd.read_csv(RECORDS)
    adjudication = pd.read_csv(ADJUDICATION)

    path = OUT_DIR / "Active_Observational_10Task_Annual_Workload_Bilingual_v5.xlsx"
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        workbook = writer.book
        workbook.set_properties(
            {
                "title": "Active observational sensing — 10-task annual workload",
                "subject": "Bilingual bibliometric source data and screening audit",
                "author": "OpenAI Codex",
                "comments": "OpenAlex + Europe PMC + arXiv; cutoff 2026-08-06",
            }
        )
        header = workbook.add_format(
            {
                "bold": True,
                "font_color": "white",
                "bg_color": "#0B5C8E",
                "border": 0,
                "align": "center",
                "valign": "vcenter",
            }
        )
        section = workbook.add_format(
            {"bold": True, "font_color": "#0B5C8E", "font_size": 12}
        )
        wrap = workbook.add_format({"text_wrap": True, "valign": "top"})
        note = workbook.add_format({"font_color": "#5D6870", "text_wrap": True, "valign": "top"})
        integer = workbook.add_format({"num_format": "0", "align": "center"})
        link = workbook.add_format({"font_color": "#0563C1", "underline": 1})

        guide = workbook.add_worksheet("Guide_EN_ZH")
        writer.sheets["Guide_EN_ZH"] = guide
        guide.hide_gridlines(2)
        guide.set_column("A:A", 22)
        guide.set_column("B:B", 112)
        guide.set_row(0, 27)
        guide.write("A1", "Active observational sensing — corrected 10-task annual workload", section)
        guide.merge_range("A1:B1", "Active observational sensing — corrected 10-task annual workload / 主动观察式检测——修正后的 10 类任务逐年工作量", section)
        guide_rows = [
            ("Correction / 修正", "The former heatmap contained only A1–A7. This workbook and the revised figures contain A1–A10. / 旧热力图实际只有 A1–A7；本工作簿及修订图均含 A1–A10。"),
            ("Unit / 计数单位", "One deduplicated publication record, assigned to the earliest plausible public year; not one robot, trial, or system. / 1 条跨库去重文献，归入最早合理公开年份；并非 1 台机器人、1 项试验或 1 套系统。"),
            ("Databases / 数据库", "OpenAlex + Europe PMC + arXiv. arXiv is explicitly included. / 明确包含 arXiv。"),
            ("Cutoff / 截止时间", "6 Aug 2026. The 2026 values are year-to-date; 1995–2025 are complete calendar years. / 截至 2026-08-06；2026 为年内数据，1995–2025 为完整年度。"),
            ("Inclusion / 纳入", "The robot or actuated mechanism must control the diagnostic sensor, viewpoint/contact, or acquisition trajectory. / 机器人或可驱动机构必须控制诊断传感器、视点/接触或采集轨迹。"),
            ("Versions / 版本", "Linked preprint and journal versions count once at the earliest public year. / 关联预印本与期刊版本仅计一次，并归入最早公开年份。"),
            ("Interpretation / 解读", "A blank/zero means that no qualifying record was found under this high-precision rule; it is not proof that no work exists. / 空白或零表示按高精度口径未检出合格记录，不证明该方向绝对没有工作。"),
            ("Final corpus / 最终语料", f"n={len(records)} records across 10 task families / 10 类任务共 n={len(records)} 条记录。"),
        ]
        for row_idx, (key, value) in enumerate(guide_rows, start=2):
            guide.write(row_idx, 0, key, header if row_idx == 2 else wrap)
            guide.write(row_idx, 1, value, note)
            guide.set_row(row_idx, 38 if row_idx in (2, 3, 6, 8) else 29)

        data_sheets = [
            ("Task_definitions", defs),
            ("Annual_long", annual),
            ("Annual_matrix", matrix),
            ("Cumulative_totals", totals),
            ("Included_records", records),
            ("A8_A10_adjudication", adjudication),
        ]
        for sheet_name, frame in data_sheets:
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            ws.autofilter(0, 0, max(len(frame), 1), len(frame.columns) - 1)
            ws.set_row(0, 28, header)
            for col_idx, column in enumerate(frame.columns):
                sample = frame[column].fillna("").astype(str).head(250)
                max_len = max([len(str(column)), *(len(value) for value in sample)])
                if column in {"abstract", "title", "definition_en", "definition_zh", "adjudication_reason"}:
                    width = 54 if column != "abstract" else 76
                    ws.set_column(col_idx, col_idx, width, wrap)
                elif column in {"url", "source_ids", "source_databases", "source_dbs"}:
                    ws.set_column(col_idx, col_idx, min(max(max_len + 2, 20), 44), wrap)
                elif pd.api.types.is_numeric_dtype(frame[column]):
                    ws.set_column(col_idx, col_idx, max(11, min(max_len + 2, 17)), integer)
                else:
                    ws.set_column(col_idx, col_idx, min(max(max_len + 2, 12), 28))

        matrix_ws = writer.sheets["Annual_matrix"]
        # D:AI contains 1995--2026.  Zero maps to white and the largest values
        # to the same dark blue family used in the publication figure.
        matrix_ws.conditional_format(
            1,
            3,
            len(matrix),
            len(matrix.columns) - 1,
            {
                "type": "3_color_scale",
                "min_type": "num",
                "min_value": 0,
                "min_color": "#FFFFFF",
                "mid_type": "num",
                "mid_value": 10,
                "mid_color": "#7FB2CF",
                "max_type": "max",
                "max_color": "#08456F",
            },
        )
        matrix_ws.freeze_panes(1, 3)

        fig_ws = workbook.add_worksheet("Figures")
        writer.sheets["Figures"] = fig_ws
        fig_ws.hide_gridlines(2)
        fig_ws.set_column("A:A", 2)
        fig_ws.set_column("B:U", 11)
        fig_ws.write("B2", "English heatmap / 英文热力图", section)
        fig_ws.insert_image(
            "B4",
            str(OUT_DIR / "Fig5c_active_annual_workload_10tasks_EN.png"),
            {"x_scale": 0.29, "y_scale": 0.29},
        )
        fig_ws.write("B46", "Chinese heatmap / 中文热力图", section)
        fig_ws.insert_image(
            "B48",
            str(OUT_DIR / "Fig5c_active_annual_workload_10tasks_ZH.png"),
            {"x_scale": 0.29, "y_scale": 0.29},
        )

    return path


def build_pdf_packet() -> Path:
    order = [
        OUT_DIR / "Fig5c_active_annual_workload_10tasks_EN.pdf",
        OUT_DIR / "Fig5c_active_annual_workload_10tasks_ZH.pdf",
        OUT_DIR / "Fig5b_active_annual_total_10tasks_EN.pdf",
        OUT_DIR / "Fig5b_active_annual_total_10tasks_ZH.pdf",
    ]
    writer = PdfWriter()
    for path in order:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    writer.add_metadata(
        {
            "/Title": "Active observational sensing: 10-task annual workload — bilingual figure packet",
            "/Author": "OpenAI Codex",
            "/Subject": "OpenAlex, Europe PMC, and arXiv; cutoff 2026-08-06",
        }
    )
    out = OUT_DIR / "Active_Observational_10Task_Figure_Packet_Bilingual_v5.pdf"
    with out.open("wb") as handle:
        writer.write(handle)
    return out


def copy_reproducibility_files() -> None:
    source_files = {
        ROOT / "scripts" / "collect_active_extension_v5.py": "collect_active_extension_v5.py",
        ROOT / "scripts" / "finalize_active_ten_task_v5.py": "finalize_active_ten_task_v5.py",
        ROOT / "scripts" / "make_active_10task_annual_chart_v5.py": "make_active_10task_annual_chart_v5.py",
        ROOT / "scripts" / "build_active_10task_package_v5.py": "build_active_10task_package_v5.py",
        ROOT / "data" / "active_extension_v5" / "query_log.json": "extension_query_log.json",
        ROOT / "data" / "active_extension_v5" / "metadata.json": "extension_retrieval_metadata.json",
    }
    for source, name in source_files.items():
        if source.exists():
            shutil.copy2(source, OUT_DIR / name)


def build_qc() -> dict:
    annual = pd.read_csv(ANNUAL)
    totals = pd.read_csv(TOTALS)
    records = pd.read_csv(RECORDS)
    adjudication = pd.read_csv(ADJUDICATION)
    expected_codes = [f"A{i}" for i in range(1, 11)]
    annual_sums = annual.groupby("task_code")["publication_records"].sum().reindex(expected_codes, fill_value=0)
    total_sums = totals.set_index("task_code")["cumulative_records"].reindex(expected_codes, fill_value=0)
    duplicate_doi = (
        records["doi"].dropna().astype(str).str.lower().replace("nan", pd.NA).dropna().duplicated().sum()
    )
    duplicate_title = records["title"].astype(str).str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).duplicated().sum()
    checks = {
        "ten_task_codes_present": bool(set(annual["task_code"].unique().tolist()) == set(expected_codes)),
        "annual_rows_equal_10x32": bool(len(annual) == 320),
        "years_are_1995_through_2026": bool(sorted(annual["year"].unique().tolist()) == list(range(1995, 2027))),
        "annual_counts_nonnegative_integers": bool((annual["publication_records"] >= 0).all()),
        "annual_sums_match_cumulative_totals": bool(annual_sums.equals(total_sums)),
        "record_count_matches_total": bool(len(records) == int(total_sums.sum())),
        "no_duplicate_nonempty_doi": bool(int(duplicate_doi) == 0),
        "no_duplicate_normalized_title": bool(int(duplicate_title) == 0),
        "arxiv_present_in_final_records": bool(records["source_dbs"].astype(str).str.contains("arXiv", case=False).any()),
        "a8_a10_adjudication_complete": bool(len(adjudication) == 313),
        "2026_marked_ytd": bool(annual.loc[annual["year"].eq(2026), "year_status"].eq("YTD through 2026-08-06").all()),
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "final_records": len(records),
        "task_totals": {row.task_code: int(row.cumulative_records) for row in totals.itertuples()},
        "extension_candidate_status": {
            f"{code}:{status}": int(value)
            for (code, status), value in adjudication.groupby(["task_code", "adjudication_status"]).size().items()
        },
        "cutoff": "2026-08-06",
        "databases": ["OpenAlex", "Europe PMC", "arXiv"],
    }
    (OUT_DIR / "quality_control_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def write_readme(qc: dict) -> None:
    text = f"""# Corrected active-observation annual workload / 修正后的主动观察逐年工作量

This package corrects the previous seven-row heatmap. The revised heatmaps contain **A1–A10 (10 task families)** and show every calendar year from 1995 through 2026. / 本数据包修正了旧版七行热力图；新版包含 **A1–A10（10 类任务）**，并逐年展示 1995–2026。

## Main files / 主要文件

- `Fig5c_active_annual_workload_10tasks_EN.*` — English ten-row heatmap / 英文十行热力图
- `Fig5c_active_annual_workload_10tasks_ZH.*` — Chinese ten-row heatmap / 中文十行热力图
- `Fig5b_active_annual_total_10tasks_EN/ZH.*` — annual total trajectory / 年度总轨迹
- `Active_Observational_10Task_Figure_Packet_Bilingual_v5.pdf` — four-page bilingual PDF packet / 四页中英文图包
- `Active_Observational_10Task_Annual_Workload_Bilingual_v5.xlsx` — definitions, annual data, records, and adjudication log / 定义、逐年数据、文献及判定日志
- `included_active_10task_records.csv` — all {qc['final_records']} counted records / 全部 {qc['final_records']} 条计数记录
- `extension_A8_A10_core_candidate_adjudication.csv` — record-level A8–A10 inclusion/exclusion audit / A8–A10 逐条纳排审计
- `method_and_correction_bilingual.md` — reproducible counting rules and limitations / 可复核计数规则与局限

## Counts / 累计量

| Task | n |
|---|---:|
"""
    for code, value in qc["task_totals"].items():
        text += f"| {code} | {value} |\n"
    text += f"| **Total / 合计** | **{qc['final_records']}** |\n\n"
    text += (
        "Databases: OpenAlex, Europe PMC, and arXiv. Cutoff: 6 August 2026; 2026 is YTD. "
        "A zero means no qualifying high-precision record was found, not that the task is impossible or absent.\n\n"
        "数据库：OpenAlex、Europe PMC 与 arXiv。截止：2026-08-06；2026 为年内数据。"
        "零值表示按高精度口径未检出合格记录，不表示任务不可能或绝对不存在。\n\n"
        f"QC status / 质检状态：**{qc['status']}**\n"
    )
    (OUT_DIR / "README_bilingual.md").write_text(text, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest_and_zip() -> Path:
    archive = OUT_DIR.parent / "active_observational_10task_annual_v5_2026-08-07.zip"
    files = [path for path in sorted(OUT_DIR.iterdir()) if path.is_file() and not path.name.startswith(".")]
    manifest = pd.DataFrame(
        [
            {
                "filename": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ]
    )
    manifest.to_csv(OUT_DIR / "file_manifest.csv", index=False, encoding="utf-8-sig")
    files = [path for path in sorted(OUT_DIR.iterdir()) if path.is_file() and not path.name.startswith(".")]
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for path in files:
            handle.write(path, arcname=f"{OUT_DIR.name}/{path.name}")
    return archive


def main() -> None:
    copy_reproducibility_files()
    workbook = build_workbook()
    packet = build_pdf_packet()
    qc = build_qc()
    write_readme(qc)
    archive = build_manifest_and_zip()
    print(json.dumps(qc, ensure_ascii=False, indent=2))
    print("Workbook:", workbook)
    print("PDF packet:", packet)
    print("Archive:", archive)


if __name__ == "__main__":
    main()
