import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "/workspace/scratch/08e9490e7d8f";
const outputDir = path.join(
  root,
  "outputs/08e9490e7d8f/embodied_detection_annual_heatmap_taxonomy_audit_v4_2026-08-07",
);
const payload = JSON.parse(
  await fs.readFile(path.join(outputDir, "workbook_payload.json"), "utf8"),
);
const previewDir = path.join(root, "tmp/08e9490e7d8f/artifact_workbook/previews");
await fs.mkdir(previewDir, { recursive: true });

const workbook = Workbook.create();
const readme = workbook.worksheets.add("README");
const revisedSheet = workbook.worksheets.add("Revised_33_Tasks");
const auditSheet = workbook.worksheets.add("Gap_Audit");
const annualLongSheet = workbook.worksheets.add("Annual_Long");
const annualMatrixSheet = workbook.worksheets.add("Annual_Matrix");

const navy = "#17365D";
const blue = "#0072B2";
const green = "#009E73";
const orange = "#B35C00";
const paleBlue = "#EAF2F8";
const paleOrange = "#FFF2CC";
const light = "#F3F5F7";
const grid = "#D9E0E6";
const ink = "#222222";
const muted = "#666666";
const heatColors = ["#FFFFFF", "#EAF2F8", "#CFE1EF", "#9FC5DF", "#6AA6CF", "#337FB8", "#0B4F8A"];
const bodyFont = "Noto Sans CJK SC";

function writeBlock(sheet, startCell, rows) {
  const start = sheet.getRange(startCell);
  start.writeValues(rows);
}

function styleTitle(sheet, range, title) {
  const target = sheet.getRange(range);
  target.merge();
  target.values = [[title]];
  target.format = {
    fill: navy,
    font: { name: bodyFont, bold: true, color: "#FFFFFF", size: 16 },
    verticalAlignment: "center",
    horizontalAlignment: "left",
  };
  target.format.rowHeight = 32;
}

function styleHeader(range, fill = navy) {
  range.format = {
    fill,
    font: { name: bodyFont, bold: true, color: "#FFFFFF", size: 10 },
    verticalAlignment: "center",
    horizontalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: grid },
  };
  range.format.rowHeight = 28;
}

function styleBody(range) {
  range.format = {
    font: { name: bodyFont, color: ink, size: 9 },
    verticalAlignment: "top",
    wrapText: true,
    borders: {
      insideHorizontal: { style: "thin", color: grid },
      bottom: { style: "thin", color: grid },
    },
  };
}

// README ---------------------------------------------------------------------
readme.showGridLines = false;
styleTitle(readme, "A1:G1", "Taxonomy Audit and Annual Workload / 分类审计与逐年工作量");
readme.getRange("A3:G3").merge();
readme.getRange("A3").values = [[
  "Conclusion / 结论：the current 24-task set is a high-precision working taxonomy, not an exhaustive list. " +
    "A minimum evidence-supported revision contains 33 families (A=10, R=12, S=11). / " +
    "当前 24 任务为偏高精度的工作分类，并非穷尽式清单；基于证据的最小修订为 33 个任务族（A=10、R=12、S=11）。",
]];
readme.getRange("A3:G3").format = {
  fill: paleOrange,
  font: { name: bodyFont, bold: true, color: orange, size: 10 },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#E6C36A" },
};
readme.getRange("A3:G3").format.rowHeight = 54;

writeBlock(readme, "A6", [
  ["Class", "Current tasks", "Revised tasks", "Net change", "Class (English)", "大类（中文）", "Interpretation / 解释"],
  ...payload.summary.slice(0, 3).map((row) => [
    row.class_code,
    row.current_task_families,
    row.revised_task_families,
    null,
    row.class_en,
    row.class_zh,
    row.class_code === "A"
      ? "Three net additions after one split: radiation/nuclear acquisition, microscopy/endomicroscopy, and embodied vital signs. / 拆分一项并净增三项。"
      : row.class_code === "R"
        ? "Adds tone/strength, sensorimotor, balance perturbation and vestibular provocation. / 新增肌张力力量、感觉运动、平衡扰动和前庭激发。"
        : "Adds stereotactic CNS biopsy and separates body-cavity fluid aspiration from marrow sampling. / 新增中枢立体定向活检，并拆分体腔液体与骨髓采样。",
  ]),
  ["Total", null, null, null, "Total", "合计", "Evidence-supported minimum working framework / 证据支持的最小工作框架"],
]);
styleHeader(readme.getRange("A6:G6"));
styleBody(readme.getRange("A7:G10"));
readme.getRange("A7:G9").format.rowHeight = 54;
readme.getRange("D7").formulas = [["=C7-B7"]];
readme.getRange("D7:D9").fillDown();
readme.getRange("B10").formulas = [["=SUM(B7:B9)"]];
readme.getRange("C10").formulas = [["=SUM(C7:C9)"]];
readme.getRange("D10").formulas = [["=C10-B10"]];
readme.getRange("A10:G10").format = {
  fill: paleBlue,
  font: { name: bodyFont, bold: true, color: navy, size: 9 },
  borders: { top: { style: "medium", color: blue }, bottom: { style: "thin", color: grid } },
};
readme.getRange("B7:D10").format.numberFormat = "0";
readme.getRange("B7:D10").format.horizontalAlignment = "right";

writeBlock(readme, "A13", [
  ["Annual-data QC / 逐年数据校验", "Value / 数值", "Expected / 预期", "Difference / 差值", "Status / 状态", "Scope / 口径", "Source / 来源"],
  ["Strict-set A1–A7 total / 严格集 A1–A7 合计", null, 436, null, null,
    "1995–2026; 2026 YTD; one primary task per deduplicated work / 1995–2026；2026 年内截至；每篇去重工作唯一归类",
    "OpenAlex + Europe PMC + arXiv"],
]);
styleHeader(readme.getRange("A13:G13"), blue);
styleBody(readme.getRange("A14:G14"));
readme.getRange("A14:G14").format.rowHeight = 48;
readme.getRange("B14").formulas = [["=SUM('Annual_Matrix'!D2:AI8)"]];
readme.getRange("D14").formulas = [["=B14-C14"]];
readme.getRange("E14").formulas = [["=IF(D14=0,\"PASS\",\"CHECK\")"]];
readme.getRange("B14:D14").format.numberFormat = "0";
readme.getRange("E14").format = { fill: "#E2F0D9", font: { name: bodyFont, bold: true, color: "#2E6B2E" }, horizontalAlignment: "center" };

readme.getRange("A17:G17").merge();
readme.getRange("A17").values = [[
  "Counting rule / 计数规则：the annual figures quantify only the completed A1–A7 screened corpus. " +
    "Proposed A8–A10 tasks must undergo the same retrospective search, deduplication and screening before quantitative integration. / " +
    "逐年图仅量化已完成筛选的 A1–A7；建议新增的 A8–A10 必须按同一协议回溯检索、去重和筛选后才能纳入。",
]];
readme.getRange("A17:G17").format = { fill: light, font: { name: bodyFont, color: muted, italic: true, size: 9 }, wrapText: true };
readme.getRange("A17:G17").format.rowHeight = 44;
readme.freezePanes.freezeRows(1);
readme.getRange("A1:A17").format.columnWidth = 24;
readme.getRange("B1:D17").format.columnWidth = 13;
readme.getRange("E1:F17").format.columnWidth = 25;
readme.getRange("G1:G17").format.columnWidth = 52;

// Revised 33-task framework --------------------------------------------------
revisedSheet.showGridLines = false;
const revisedHeaders = ["Code", "Class code", "Class (English)", "大类（中文）", "Task family (English)", "任务族（中文）", "Revision status (English)", "修订状态（中文）"];
const revisedRows = payload.revised_tasks.map((row) => [
  row.code,
  row.class_code,
  row.class_en,
  row.class_zh,
  row.task_en,
  row.task_zh,
  row.revision_status_en,
  row.revision_status_zh,
]);
writeBlock(revisedSheet, "A1", [revisedHeaders, ...revisedRows]);
styleHeader(revisedSheet.getRange("A1:H1"));
styleBody(revisedSheet.getRange(`A2:H${revisedRows.length + 1}`));
revisedSheet.getRange(`A2:B${revisedRows.length + 1}`).format.horizontalAlignment = "center";
revisedSheet.getRange(`A2:H${revisedRows.length + 1}`).format.rowHeight = 36;
revisedSheet.getRange(`A2:H11`).format.fill = "#F2F8FC";
revisedSheet.getRange(`A12:H23`).format.fill = "#FFF7F0";
revisedSheet.getRange(`A24:H34`).format.fill = "#F2FAF7";
revisedSheet.tables.add(`A1:H${revisedRows.length + 1}`, true, "RevisedTasksTable");
revisedSheet.freezePanes.freezeRows(1);
revisedSheet.freezePanes.freezeColumns(2);
revisedSheet.getRange("A1:A34").format.columnWidth = 9;
revisedSheet.getRange("B1:B34").format.columnWidth = 10;
revisedSheet.getRange("C1:D34").format.columnWidth = 27;
revisedSheet.getRange("E1:F34").format.columnWidth = 43;
revisedSheet.getRange("G1:H34").format.columnWidth = 27;

// Gap audit ------------------------------------------------------------------
auditSheet.showGridLines = false;
const auditHeaders = [
  "Class", "Gap type (EN)", "缺口类型", "Decision (EN)", "决策", "Task/issue (EN)", "任务/问题",
  "Assessment (EN)", "判断（中文）", "Evidence (EN)", "证据（中文）", "Source URL(s)",
];
const auditRows = payload.audit.map((row) => [
  row.class_code,
  row.gap_type_en,
  row.gap_type_zh,
  row.decision_en,
  row.decision_zh,
  row.task_or_issue_en,
  row.task_or_issue_zh,
  row.assessment_en,
  row.assessment_zh,
  row.evidence_en,
  row.evidence_zh,
  row.source_urls,
]);
writeBlock(auditSheet, "A1", [auditHeaders, ...auditRows]);
styleHeader(auditSheet.getRange("A1:L1"));
styleBody(auditSheet.getRange(`A2:L${auditRows.length + 1}`));
auditSheet.getRange(`A2:A${auditRows.length + 1}`).format.horizontalAlignment = "center";
auditSheet.getRange(`A2:L${auditRows.length + 1}`).format.rowHeight = 76;
auditSheet.tables.add(`A1:L${auditRows.length + 1}`, true, "GapAuditTable");
auditSheet.freezePanes.freezeRows(1);
auditSheet.freezePanes.freezeColumns(1);
auditSheet.getRange("A1:A20").format.columnWidth = 8;
auditSheet.getRange("B1:E20").format.columnWidth = 18;
auditSheet.getRange("F1:G20").format.columnWidth = 36;
auditSheet.getRange("H1:K20").format.columnWidth = 48;
auditSheet.getRange("L1:L20").format.columnWidth = 55;

// Annual long source ---------------------------------------------------------
annualLongSheet.showGridLines = false;
const annualHeaders = ["Year", "Year status", "Task code", "Task (English)", "任务（中文）", "Strict-set records", "Broad-set records"];
const annualRows = payload.annual_long.map((row) => [
  row.year,
  row.year_status,
  row.task_code,
  row.task_en,
  row.task_zh,
  row.core_records,
  row.expanded_upper_records,
]);
writeBlock(annualLongSheet, "A1", [annualHeaders, ...annualRows]);
styleHeader(annualLongSheet.getRange("A1:G1"), blue);
styleBody(annualLongSheet.getRange(`A2:G${annualRows.length + 1}`));
annualLongSheet.getRange(`A2:C${annualRows.length + 1}`).format.horizontalAlignment = "center";
annualLongSheet.getRange(`F2:G${annualRows.length + 1}`).format.horizontalAlignment = "right";
annualLongSheet.getRange(`A2:A${annualRows.length + 1}`).format.numberFormat = "0";
annualLongSheet.getRange(`F2:G${annualRows.length + 1}`).format.numberFormat = "0";
annualLongSheet.tables.add(`A1:G${annualRows.length + 1}`, true, "AnnualLongTable");
annualLongSheet.freezePanes.freezeRows(1);
annualLongSheet.freezePanes.freezeColumns(3);
annualLongSheet.getRange("A1:A230").format.columnWidth = 10;
annualLongSheet.getRange("B1:B230").format.columnWidth = 14;
annualLongSheet.getRange("C1:C230").format.columnWidth = 11;
annualLongSheet.getRange("D1:E230").format.columnWidth = 42;
annualLongSheet.getRange("F1:G230").format.columnWidth = 18;

// Annual matrix --------------------------------------------------------------
annualMatrixSheet.showGridLines = false;
const years = Array.from({ length: 32 }, (_, i) => String(1995 + i));
const matrixHeaders = ["Task code", "Task (English)", "任务（中文）", ...years.slice(0, 31), "2026 YTD"];
const matrixRows = payload.annual_matrix.map((row) => [
  row.task_code,
  row.task_en,
  row.task_zh,
  ...years.map((year) => row[year]),
]);
writeBlock(annualMatrixSheet, "A1", [matrixHeaders, ...matrixRows]);
styleHeader(annualMatrixSheet.getRange("A1:AI1"), blue);
styleBody(annualMatrixSheet.getRange("A2:AI8"));
annualMatrixSheet.getRange("A2:AI8").format.rowHeight = 28;
annualMatrixSheet.getRange("D2:AI8").format = {
  numberFormat: "0",
  horizontalAlignment: "center",
  verticalAlignment: "center",
  font: { name: bodyFont, size: 8, color: ink },
  borders: { preset: "all", style: "thin", color: "#FFFFFF" },
};
for (let i = 0; i < matrixRows.length; i += 1) {
  for (let j = 0; j < years.length; j += 1) {
    const value = matrixRows[i][3 + j];
    const idx = value === 0 ? 0 : value <= 2 ? 1 : value <= 5 ? 2 : value <= 10 ? 3 : value <= 20 ? 4 : value <= 40 ? 5 : 6;
    const cell = annualMatrixSheet.getCell(1 + i, 3 + j);
    cell.format.fill = heatColors[idx];
    if (value >= 11) cell.format.font = { name: bodyFont, size: 8, color: "#FFFFFF", bold: true };
    if (value === 0) cell.format.font = { name: bodyFont, size: 8, color: "#A0A0A0" };
  }
}
annualMatrixSheet.freezePanes.freezeRows(1);
annualMatrixSheet.freezePanes.freezeColumns(3);
annualMatrixSheet.getRange("A1:A8").format.columnWidth = 10;
annualMatrixSheet.getRange("B1:C8").format.columnWidth = 28;
annualMatrixSheet.getRange("D1:AI8").format.columnWidth = 8;

// Compact audit checks and previews -----------------------------------------
const summaryInspection = await workbook.inspect({
  kind: "table",
  range: "README!A1:G17",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 8,
  maxChars: 8000,
});
console.log(summaryInspection.ndjson);
const errorScan = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errorScan.ndjson);

for (const [sheetName, range] of [
  ["README", "A1:G17"],
  ["Revised_33_Tasks", "A1:H34"],
  ["Gap_Audit", "A1:L14"],
  ["Annual_Long", "A1:G225"],
  ["Annual_Matrix", "A1:AI8"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 0.8, format: "png" });
  await fs.writeFile(
    path.join(previewDir, `${sheetName}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const outputPath = path.join(outputDir, "Taxonomy_Audit_and_Annual_Workload_Bilingual_2026-08-07.xlsx");
await xlsx.save(outputPath);
console.log(JSON.stringify({ outputPath, previewDir }, null, 2));
