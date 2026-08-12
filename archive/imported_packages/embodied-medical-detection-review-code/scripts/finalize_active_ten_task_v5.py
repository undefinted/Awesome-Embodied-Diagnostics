#!/usr/bin/env python3
"""Finalize the ten-family active-observation corpus used in Figure 5c v5.

The script keeps the previously screened A1--A7 title-explicit records and
adds a manually adjudicated, title/abstract-verified extension for A8--A10.
It counts deduplicated publication records at the earliest public year and
does not extrapolate unobserved studies.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OLD_CORPUS = ROOT / "data" / "bibliometrics_v2_arxiv" / "included.csv"
EXT_CORPUS = ROOT / "data" / "active_extension_v5" / "included_auto_screened.csv"
OUT_DIR = (
    ROOT
    / "outputs"
    / "08e9490e7d8f"
    / "active_observational_10task_annual_v5_2026-08-07"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

START_YEAR = 1995
END_YEAR = 2026
CUTOFF = "2026-08-06"


TASKS = [
    (
        "A1",
        "Robotic ultrasound / sonography",
        "机器人超声 / 超声扫查",
        "Robot controls transducer pose, path, or contact to acquire diagnostic ultrasound.",
        "机器人控制探头位姿、路径或接触以采集诊断超声。",
    ),
    (
        "A2",
        "Robotic endoscopic search / navigation",
        "机器人内镜搜索 / 导航",
        "Robot changes endoscope pose or route to inspect a lumen and search for lesions.",
        "机器人改变内镜位姿或路径以检查腔道并搜索病灶。",
    ),
    (
        "A3",
        "Robotic OCT / ophthalmic scanning",
        "机器人 OCT / 眼科扫描",
        "Robot positions an OCT or ophthalmic sensor and executes an imaging scan.",
        "机器人定位 OCT 或眼科传感器并执行成像扫描。",
    ),
    (
        "A4",
        "Robotic dermoscopy / skin scanning",
        "机器人皮肤镜 / 皮肤扫描",
        "Robot acquires standardized dermoscopic or whole-skin views.",
        "机器人获取标准化皮肤镜或全身皮肤视图。",
    ),
    (
        "A5",
        "Robotic auscultation",
        "机器人听诊",
        "Robot selects and maintains auscultation sites and contact for acoustic signals.",
        "机器人选择并保持听诊位置与接触以获取声学信号。",
    ),
    (
        "A6",
        "Robotic otoscopy / oral-ENT examination",
        "机器人耳镜 / 口腔-耳鼻喉检查",
        "Robot positions a camera or scope for ear, oral, or ENT inspection.",
        "机器人定位摄像头或镜体以检查耳、口腔或耳鼻喉区域。",
    ),
    (
        "A7",
        "Robotic optical / spectral / thermal scanning",
        "机器人光学 / 光谱 / 热成像扫描",
        "Robot controls an optical, spectral, fluorescence, or thermal sensor scan.",
        "机器人控制光学、光谱、荧光或热传感器扫描。",
    ),
    (
        "A8",
        "Robotic X-ray / CT / nuclear-image acquisition",
        "机器人 X-ray / CT / 核医学成像采集",
        "Robot controls source-detector or gamma-camera geometry and acquisition trajectory.",
        "机器人控制射线源-探测器或 gamma 相机的几何关系与采集轨迹。",
    ),
    (
        "A9",
        "Robotic microscopy / confocal endomicroscopy",
        "机器人显微 / 共聚焦内显微扫描",
        "Robot positions, focuses, or scans an in-vivo microscope/endomicroscope.",
        "机器人定位、对焦或扫描在体显微镜 / 内显微探头。",
    ),
    (
        "A10",
        "Embodied vital-sign acquisition",
        "具身式生命体征采集",
        "A mobile robot or robot arm positions contact or non-contact sensors for vital signs.",
        "移动机器人或机械臂定位接触式或非接触式生命体征传感器。",
    ),
]

TASK_FRAME = pd.DataFrame(
    TASKS,
    columns=["task_code", "task_en", "task_zh", "definition_en", "definition_zh"],
)
TASK_META = TASK_FRAME.set_index("task_code").to_dict("index")


# Row identifiers in included_auto_screened.csv.  Each was adjudicated from
# title and abstract against the controlled-sensor inclusion rule above.
A8_INCLUDED = {
    181, 199, 312, 327, 329, 340, 342, 372, 379, 382, 389, 393, 412,
    415, 422, 424, 439, 443, 444, 456, 492, 507, 519, 527, 541, 544,
    546, 564, 577, 591, 608, 617, 678, 679, 685, 715, 723, 731, 759,
    763, 764, 801, 819, 827, 850, 854, 869, 920, 941, 944, 946, 949,
    952, 959, 972, 982, 983, 994, 1008, 1065, 1134, 1159, 1217,
    1218, 1220, 1245, 1275, 1288, 1329, 1420, 1447, 1552, 1574,
    1662, 1684, 1699, 1700,
}

A9_INCLUDED = {
    1782, 1784, 1789, 1790, 1791, 1796, 1798, 1802, 1803, 1806,
    1812, 1815, 1820, 1826, 1827, 1829, 1833, 1834, 1836, 1837,
    1865, 1866, 1870, 1873, 1878, 1881, 1882, 1893, 1896,
}

# Dr Spot's 2020 preprint (row 34) and 2022 journal article (row 52) are one
# work.  The journal row is retained as canonical and assigned the earliest
# public year, 2020.
A10_INCLUDED = {20, 49, 52, 58, 60, 81, 98, 103, 105}
VERSION_MERGES = {34: 52}
YEAR_OVERRIDES = {52: 2020}

MANUAL_INCLUDED = {
    "A8": A8_INCLUDED,
    "A9": A9_INCLUDED,
    "A10": A10_INCLUDED,
}


def normalize_title(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def exclusion_reason(code: str, title: str) -> str:
    lower = title.lower()
    if re.search(r"\b(review|meta-analysis|survey|comment|letter|errat|reply)\b", lower):
        return "Non-primary publication (review/comment/letter/erratum)"
    if code == "A8":
        if re.search(
            r"industrial|non[- ]destructive|ordnance|space[- ]borne|pulsar|wind turbine|"
            r"sample holder|powder x[- ]ray|porosit|large component|x[- ]ray fluorescence mapping",
            lower,
        ):
            return "Industrial, materials, or non-clinical acquisition"
        if re.search(
            r"radiographic (?:and |outcome|result|evaluation)|robot[- ]assisted (?:total|pedicle|"
            r"surgery|resection|needle|puncture|biopsy)|robotic (?:arthroplasty|surgery|bronchoscopy)",
            lower,
        ):
            return "Robot performs an intervention; imaging sensor is not the controlled diagnostic device"
        return "No explicit robot-controlled diagnostic acquisition geometry"
    if code == "A9":
        if re.search(r"telepathology|cytolog|frozen section|microscope slide|tuberculosis", lower):
            return "Ex-vivo laboratory/pathology microscopy, outside patient-side embodiment"
        return "Robot-sensor coupling is absent or not central to the diagnostic observation"
    if code == "A10":
        if re.search(r"resilience|calmness|heart rate variability enhancement|stimulation", lower):
            return "Physiological intervention or association study, not diagnostic acquisition"
        return "No embodied sensor positioning for vital-sign acquisition"
    return "Outside scope"


def verify_manual_ids(ext: pd.DataFrame) -> None:
    for code, ids in MANUAL_INCLUDED.items():
        missing = sorted(ids.difference(ext.index))
        if missing:
            raise RuntimeError(f"Missing adjudicated row ids for {code}: {missing}")
        wrong = ext.loc[sorted(ids), "primary_task"].ne(code)
        if wrong.any():
            bad = ext.loc[sorted(ids)].loc[wrong, ["primary_task", "title"]]
            raise RuntimeError(f"Task mismatch in adjudication for {code}:\n{bad}")


def build_extension_adjudication(ext: pd.DataFrame) -> pd.DataFrame:
    core = ext[ext["evidence_tier"].eq("Core (title-explicit)")].copy()
    core = core[core["primary_task"].isin(["A8", "A9", "A10"])]
    rows = []
    for idx, row in core.iterrows():
        code = row["primary_task"]
        if idx in MANUAL_INCLUDED[code]:
            status = "Included"
            reason = "Robot controls the diagnostic sensor, viewpoint, contact, or acquisition trajectory"
            canonical = idx
        elif idx in VERSION_MERGES:
            status = "Merged version"
            reason = "Preprint/journal versions counted once at the earliest public year"
            canonical = VERSION_MERGES[idx]
        else:
            status = "Excluded"
            reason = exclusion_reason(code, str(row["title"]))
            canonical = ""
        rows.append(
            {
                "candidate_row_id": idx,
                "task_code": code,
                "year_reported": int(row["year"]),
                "title": row["title"],
                "doi": row.get("doi", ""),
                "source_databases": row.get("source_dbs", ""),
                "adjudication_status": status,
                "adjudication_reason": reason,
                "canonical_row_id": canonical,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["task_code", "year_reported", "title"], kind="stable"
    )


def build_combined_records(old: pd.DataFrame, ext: pd.DataFrame) -> pd.DataFrame:
    old_active = old[
        old["primary_task"].isin([f"A{i}" for i in range(1, 8)])
        & old["evidence_tier"].eq("Core (title-explicit)")
    ].copy()
    old_active["count_year"] = old_active["year"].astype(int)
    old_active["screening_basis"] = "Previously screened title-explicit set"
    old_active["source_row_id"] = old_active.index

    selected_ids = sorted(set().union(*MANUAL_INCLUDED.values()))
    new_active = ext.loc[selected_ids].copy()
    new_active["count_year"] = [
        YEAR_OVERRIDES.get(idx, int(row["year"])) for idx, row in new_active.iterrows()
    ]
    new_active["screening_basis"] = "Manual title/abstract adjudication"
    new_active["source_row_id"] = new_active.index

    keep = [
        "primary_task", "title", "doi", "pmid", "source_dbs", "source_ids",
        "url", "publication_date", "work_type", "venue", "abstract",
        "count_year", "screening_basis", "source_row_id",
    ]
    combined = pd.concat([old_active[keep], new_active[keep]], ignore_index=True)
    combined = combined.rename(columns={"primary_task": "task_code"})

    # Cross-source duplicate guard.  Exact DOI has precedence; normalized title
    # catches records lacking DOI.  The Dr Spot linked version was handled above.
    combined["normalized_title"] = combined["title"].map(normalize_title)
    combined["dedupe_key"] = combined["doi"].fillna("").astype(str).str.lower().str.strip()
    empty_doi = combined["dedupe_key"].eq("") | combined["dedupe_key"].eq("nan")
    combined.loc[empty_doi, "dedupe_key"] = "title:" + combined.loc[empty_doi, "normalized_title"]
    before = len(combined)
    combined = combined.sort_values(
        ["count_year", "screening_basis", "title"], kind="stable"
    ).drop_duplicates(["dedupe_key"], keep="first")
    if before - len(combined) > 0:
        print(f"Removed {before - len(combined)} exact cross-corpus duplicates")

    combined["task_en"] = combined["task_code"].map(
        {code: values["task_en"] for code, values in TASK_META.items()}
    )
    combined["task_zh"] = combined["task_code"].map(
        {code: values["task_zh"] for code, values in TASK_META.items()}
    )
    combined["year_status"] = combined["count_year"].map(
        lambda year: "YTD through 2026-08-06" if int(year) == 2026 else "full year"
    )
    columns = [
        "task_code", "task_en", "task_zh", "count_year", "year_status",
        "title", "doi", "pmid", "source_dbs", "source_ids", "url",
        "publication_date", "work_type", "venue", "screening_basis",
        "source_row_id", "abstract",
    ]
    return combined[columns].sort_values(
        ["task_code", "count_year", "title"], kind="stable"
    )


def build_annual(records: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    years = list(range(START_YEAR, END_YEAR + 1))
    codes = [f"A{i}" for i in range(1, 11)]
    counts = records.groupby(["task_code", "count_year"]).size()
    rows = []
    for code in codes:
        for year in years:
            meta = TASK_META[code]
            rows.append(
                {
                    "year": year,
                    "year_status": "YTD through 2026-08-06" if year == 2026 else "full year",
                    "task_code": code,
                    "task_en": meta["task_en"],
                    "task_zh": meta["task_zh"],
                    "publication_records": int(counts.get((code, year), 0)),
                }
            )
    annual = pd.DataFrame(rows)
    matrix = (
        annual.pivot(index="task_code", columns="year", values="publication_records")
        .reindex(index=codes, columns=years, fill_value=0)
        .reset_index()
    )
    matrix.insert(1, "task_en", matrix["task_code"].map(TASK_FRAME.set_index("task_code")["task_en"]))
    matrix.insert(2, "task_zh", matrix["task_code"].map(TASK_FRAME.set_index("task_code")["task_zh"]))
    totals = (
        records.groupby("task_code").size().reindex(codes, fill_value=0).rename("cumulative_records").reset_index()
    )
    totals.insert(1, "task_en", totals["task_code"].map(TASK_FRAME.set_index("task_code")["task_en"]))
    totals.insert(2, "task_zh", totals["task_code"].map(TASK_FRAME.set_index("task_code")["task_zh"]))
    return annual, matrix, totals


def write_method_note(totals: pd.DataFrame, adjudication: pd.DataFrame) -> None:
    total = int(totals["cumulative_records"].sum())
    included_ext = int(adjudication["adjudication_status"].eq("Included").sum())
    candidate_ext = len(adjudication)
    text = f"""# Active observational sensing: 10-family annual workload / 主动观察式检测：10 类任务逐年工作量

## Correction / 修正

**EN.** The former figure contained only A1–A7. This version contains all ten evidence-supported active-observation task families, A1–A10. A10 is broadened from *non-contact vital-sign monitoring* to *embodied vital-sign acquisition* because a robot may actively place either a contact or non-contact sensor without stimulating the patient.

**中.** 旧图实际只含 A1–A7。本版纳入已有证据支持的全部十个主动观察任务族 A1–A10。A10 从“非接触生命体征监测”扩展为“具身式生命体征采集”，因为机器人可主动定位接触式或非接触式传感器，而不对患者施加诊断刺激。

## Counting rule / 计数规则

- **Unit / 单位：** one deduplicated publication record, not one robot, experiment, or clinical trial. / 1 条跨库去重文献记录，并非 1 台机器人、1 次实验或 1 项临床试验。
- **Databases / 数据库：** OpenAlex, Europe PMC, and arXiv. arXiv is explicitly included. / 明确包含 arXiv。
- **Time / 时间：** earliest plausible public year; 1995–2025 are full calendar years and 2026 is year-to-date through {CUTOFF}. / 采用最早合理公开年份；1995–2025 为完整年度，2026 截至 {CUTOFF}。
- **Inclusion / 纳入：** the robot or actuated mechanism must control the diagnostic sensor, its viewpoint/contact, or its acquisition trajectory. / 机器人或可驱动机构必须控制诊断传感器、视点/接触或采集轨迹。
- **Exclusion / 排除：** robotic intervention merely guided by a fixed imager; postoperative radiographic outcomes; treatment-source positioning; industrial imaging; ex-vivo laboratory/telepathology microscopy; reviews, comments, and duplicate versions. / 排除仅由固定影像引导的机器人介入、术后影像结局、治疗源定位、工业成像、离体实验室/远程病理显微以及综述、评论和重复版本。
- **Versions / 版本：** linked preprint and journal versions count once at the earliest public year. / 预印本与期刊版本合并，并计入最早公开年份。

## Screening provenance / 筛选来源

- A1–A7: previously screened, title-explicit high-precision set. / 既有题名明确的高精度筛选集。
- A8–A10: {candidate_ext} title-explicit candidates were retrospectively adjudicated from title/abstract; {included_ext} unique records were retained before the linked-version merge. / 回溯复核 {candidate_ext} 条题名明确候选，题名/摘要人工判定后保留 {included_ext} 条，再处理关联版本合并。
- Final ten-family total: **n={total}** publication records. / 十类最终合计 **n={total}** 条文献记录。

## Interpretation / 解读

The chart is a reproducible high-precision workload map, not a claim of perfect recall. A zero means no qualifying record was found under this rule, not proof that no work exists. Database indexing delay and the partial 2026 calendar year make the newest counts provisional.

该图是可复核的高精度工作量图，不声称召回全部文献。零值表示按本口径未发现合格记录，不等于该方向绝对不存在工作。数据库收录延迟与 2026 年未结束使最新年度数据仍属暂定。
"""
    (OUT_DIR / "method_and_correction_bilingual.md").write_text(text, encoding="utf-8")


def main() -> None:
    old = pd.read_csv(OLD_CORPUS)
    ext = pd.read_csv(EXT_CORPUS)
    verify_manual_ids(ext)
    adjudication = build_extension_adjudication(ext)
    records = build_combined_records(old, ext)
    annual, matrix, totals = build_annual(records)

    TASK_FRAME.to_csv(
        OUT_DIR / "active_task_definitions_10_bilingual.csv",
        index=False,
        encoding="utf-8-sig",
    )
    adjudication.to_csv(
        OUT_DIR / "extension_A8_A10_core_candidate_adjudication.csv",
        index=False,
        encoding="utf-8-sig",
    )
    records.to_csv(
        OUT_DIR / "included_active_10task_records.csv",
        index=False,
        encoding="utf-8-sig",
    )
    annual.to_csv(
        OUT_DIR / "source_data_active_annual_counts_10task_bilingual.csv",
        index=False,
        encoding="utf-8-sig",
    )
    matrix.to_csv(
        OUT_DIR / "source_data_active_annual_matrix_10task_bilingual.csv",
        index=False,
        encoding="utf-8-sig",
    )
    totals.to_csv(
        OUT_DIR / "source_data_active_cumulative_totals_10task_bilingual.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_method_note(totals, adjudication)

    print(totals.to_string(index=False))
    print(f"Final records: {len(records)}")
    print(
        "Extension adjudication:",
        adjudication.groupby(["task_code", "adjudication_status"]).size().to_dict(),
    )


if __name__ == "__main__":
    main()
