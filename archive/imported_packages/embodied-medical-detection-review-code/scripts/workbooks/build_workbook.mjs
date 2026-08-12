import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

process.on("uncaughtException", (error) => {
  console.error(`BUILD_ERROR: ${error?.message || error}`);
  process.exit(1);
});
process.on("unhandledRejection", (error) => {
  console.error(`BUILD_ERROR: ${error?.message || error}`);
  process.exit(1);
});

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "../..");
const dataDir = path.join(rootDir, "data", "bibliometrics");
const outputDir = path.join(rootDir, "outputs", "08e9490e7d8f");
const qaDir = path.join(scriptDir, "qa");
const outputPath = path.join(outputDir, "具身医学检测_任务与累计工作量_2026-08-06.xlsx");

const readJson = async (name) => JSON.parse(await fs.readFile(path.join(dataDir, name), "utf8"));
const readJsonl = async (name) => {
  const text = await fs.readFile(path.join(dataDir, name), "utf8");
  return text.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
};

const metadata = await readJson("metadata.json");
const tasks = await readJson("tasks.json");
const queryLog = await readJson("query_log.json");
const candidates = await readJsonl("candidates.jsonl");
const included = candidates.filter((record) => record.included);

const CLASS = {
  A: {
    zh: "主动观察式检测",
    en: "Active observational sensing",
    action: "改变传感器位置、视角、姿态或接触状态",
    evidence: "新的影像、视觉、声学或生理信号",
    color: "#2563EB",
  },
  R: {
    zh: "响应式交互检测",
    en: "Response-based interactive diagnosis",
    action: "对组织或人体施加可控刺激",
    evidence: "力学、生理或功能响应",
    color: "#D97706",
  },
  S: {
    zh: "采样式交互检测",
    en: "Sample-based interactive diagnosis",
    action: "穿刺、抽吸或切取目标组织/体液",
    evidence: "离体样本及病理、生化或分子结果",
    color: "#0F766E",
  },
};

const COLORS = {
  navy: "#0B1F33",
  navy2: "#163A5F",
  blue: "#2563EB",
  blueLight: "#DBEAFE",
  teal: "#0F766E",
  tealLight: "#CCFBF1",
  amber: "#D97706",
  amberLight: "#FEF3C7",
  slate: "#475569",
  slateLight: "#E2E8F0",
  gray50: "#F8FAFC",
  gray100: "#F1F5F9",
  gray200: "#E2E8F0",
  gray400: "#94A3B8",
  gray700: "#334155",
  white: "#FFFFFF",
};
const FONT_NAME = "Noto Sans CJK SC";

const clean = (value, max = 30000) => {
  if (value === null || value === undefined) return "";
  return String(value).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, " ").slice(0, max);
};

const asDate = (value) => {
  if (!value || !/^\d{4}-\d{2}-\d{2}/.test(String(value))) return null;
  const date = new Date(`${String(value).slice(0, 10)}T00:00:00Z`);
  return Number.isNaN(date.getTime()) ? null : date;
};

const joinList = (value) => Array.isArray(value) ? value.join("; ") : clean(value);
const taskIndex = Object.fromEntries(tasks.map((task, index) => [task.code, index]));

const coreRecords = included.filter((record) => record.evidence_tier === "Core (title-explicit)");
const coreTotal = coreRecords.length;
const expandedTotal = included.length;
const zeroCoreTasks = tasks.filter((task) => (metadata.core_task_counts[task.code] || 0) === 0).length;

if (coreTotal !== Object.values(metadata.core_class_counts).reduce((sum, value) => sum + value, 0)) {
  throw new Error("Core total reconciliation failed");
}
if (expandedTotal !== metadata.included_records) {
  throw new Error("Expanded total reconciliation failed");
}

const recordsByTask = new Map(tasks.map((task) => [task.code, []]));
for (const record of coreRecords) {
  if (recordsByTask.has(record.primary_task)) recordsByTask.get(record.primary_task).push(record);
}
for (const records of recordsByTask.values()) {
  records.sort((a, b) => Number(b.cited_by_count || 0) - Number(a.cited_by_count || 0) || Number(b.year || 0) - Number(a.year || 0));
}

const earliestByTask = {};
const latestByTask = {};
for (const task of tasks) {
  const years = recordsByTask.get(task.code).map((record) => Number(record.year)).filter(Number.isFinite);
  earliestByTask[task.code] = years.length ? Math.min(...years) : "";
  latestByTask[task.code] = years.length ? Math.max(...years) : "";
}

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("Dashboard");
const taxonomy = workbook.worksheets.add("任务分类");
const summary = workbook.worksheets.add("统计汇总");
const annual = workbook.worksheets.add("年度趋势");
const chartData = workbook.worksheets.add("图表数据");
const works = workbook.worksheets.add("纳入文献");
const screening = workbook.worksheets.add("筛选日志");
const queries = workbook.worksheets.add("检索式与来源");
const methods = workbook.worksheets.add("方法说明");

for (const sheet of [dashboard, taxonomy, summary, annual, chartData, works, screening, queries, methods]) {
  sheet.showGridLines = false;
}

const titleBand = (sheet, range, title, subtitle = "") => {
  const [titleRange, subtitleRange] = range;
  sheet.getRange(titleRange).merge();
  sheet.getRange(titleRange).values = [[title]];
  sheet.getRange(titleRange).format = {
    fill: COLORS.navy,
    font: { name: FONT_NAME, bold: true, color: COLORS.white, size: 18 },
    verticalAlignment: "center",
  };
  sheet.getRange(titleRange).format.rowHeight = 32;
  if (subtitleRange) {
    sheet.getRange(subtitleRange).merge();
    sheet.getRange(subtitleRange).values = [[subtitle]];
    sheet.getRange(subtitleRange).format = {
      fill: COLORS.navy2,
      font: { name: FONT_NAME, color: COLORS.white, size: 10 },
      wrapText: true,
      verticalAlignment: "center",
    };
    sheet.getRange(subtitleRange).format.rowHeight = 28;
  }
};

const styleHeader = (range, fill = COLORS.navy2) => {
  range.format = {
    fill,
    font: { name: FONT_NAME, bold: true, color: COLORS.white },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "inside", style: "thin", color: COLORS.gray200 },
  };
  range.format.rowHeight = 30;
};

const styleBody = (range) => {
  range.format = {
    font: { name: FONT_NAME, color: COLORS.gray700, size: 10 },
    verticalAlignment: "top",
    borders: { preset: "inside", style: "thin", color: COLORS.gray200 },
  };
};

const sectionLabel = (sheet, range, text, fill = COLORS.slate) => {
  sheet.getRange(range).merge();
  sheet.getRange(range).values = [[text]];
  sheet.getRange(range).format = {
    fill,
    font: { name: FONT_NAME, bold: true, color: COLORS.white, size: 11 },
    verticalAlignment: "center",
  };
  sheet.getRange(range).format.rowHeight = 24;
};

// ---------------- Dashboard ----------------
titleBand(
  dashboard,
  ["A1:Q1", "A2:Q2"],
  "具身医学检测：任务版图与累计工作量",
  `开放文献计量；检索截止 ${metadata.cutoff}。核心计数用于比较，扩展计数为敏感性上界；2026 为不完整年度。`,
);

const kpiCards = [
  { range: "A4:D7", label: "高精度核心工作", value: coreTotal, note: "题名显式出现具身动作与任务" },
  { range: "E4:H7", label: "扩展敏感性上界", value: expandedTotal, note: "题名—摘要规则通过的唯一工作" },
  { range: "I4:L7", label: "具体子任务", value: tasks.length, note: `${zeroCoreTasks} 个任务核心计数为 0` },
  { range: "M4:Q7", label: "时间与数据库", value: metadata.cutoff, note: "OpenAlex + Europe PMC；论文计数" },
];
for (const card of kpiCards) {
  const start = card.range.split(":")[0];
  const [col, row] = start.match(/([A-Z]+)(\d+)/).slice(1);
  const endCol = card.range.split(":")[1].match(/[A-Z]+/)[0];
  dashboard.getRange(card.range).format = {
    fill: COLORS.gray50,
    borders: { preset: "outside", style: "medium", color: COLORS.gray200 },
  };
  dashboard.getRange(`${col}${row}:${endCol}${row}`).merge();
  dashboard.getRange(`${col}${row}:${endCol}${row}`).values = [[card.label]];
  dashboard.getRange(`${col}${row}:${endCol}${row}`).format = {
    fill: COLORS.blueLight,
    font: { name: FONT_NAME, bold: true, color: COLORS.navy },
    verticalAlignment: "center",
  };
  const valueRow = Number(row) + 1;
  const noteRow = Number(row) + 3;
  dashboard.getRange(`${col}${valueRow}:${endCol}${valueRow + 1}`).merge();
  dashboard.getRange(`${col}${valueRow}:${endCol}${valueRow + 1}`).values = [[card.value]];
  dashboard.getRange(`${col}${valueRow}:${endCol}${valueRow + 1}`).format = {
    font: { name: FONT_NAME, bold: true, color: COLORS.navy, size: 20 },
    verticalAlignment: "center",
    horizontalAlignment: "center",
  };
  dashboard.getRange(`${col}${noteRow}:${endCol}${noteRow}`).merge();
  dashboard.getRange(`${col}${noteRow}:${endCol}${noteRow}`).values = [[card.note]];
  dashboard.getRange(`${col}${noteRow}:${endCol}${noteRow}`).format = {
    font: { name: FONT_NAME, color: COLORS.slate, size: 9 },
    wrapText: true,
    horizontalAlignment: "center",
  };
}
dashboard.getRange("A9:Q10").merge();
dashboard.getRange("A9:Q10").values = [[
  `读图结论：核心计数中，主动观察式检测 ${metadata.core_class_counts.A} 篇（${(metadata.core_class_counts.A / coreTotal * 100).toFixed(1)}%），` +
  `采样式交互检测 ${metadata.core_class_counts.S} 篇（${(metadata.core_class_counts.S / coreTotal * 100).toFixed(1)}%），` +
  `响应式交互检测 ${metadata.core_class_counts.R} 篇（${(metadata.core_class_counts.R / coreTotal * 100).toFixed(1)}%）。` +
  `规模最大的具体任务为机器人超声（${metadata.core_task_counts.A1}）、机器人支气管镜活检/TBNA（${metadata.core_task_counts.S3}）和机器人内镜搜索/导航（${metadata.core_task_counts.A2}）。`,
]];
dashboard.getRange("A9:Q10").format = {
  fill: COLORS.tealLight,
  font: { name: FONT_NAME, color: COLORS.navy, bold: true, size: 11 },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: COLORS.teal },
};

dashboard.getRange("A46:Q48").merge();
dashboard.getRange("A46:Q48").values = [[
  "解释边界：本表统计的是去重后的原创研究出版物，不是设备数、临床试验数或获批产品数。核心计数是高精度下界；扩展计数仍可能含少量边界文献，不能替代 PRISMA 式全文系统综述。核心为 0 表示在本检索与严格题名规则下未找到，不等于方向绝对不存在。",
]];
dashboard.getRange("A46:Q48").format = {
  fill: COLORS.amberLight,
  font: { name: FONT_NAME, color: COLORS.gray700, size: 9 },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: COLORS.amber },
};
dashboard.freezePanes.freezeRows(2);
for (const colRange of ["A1:A48", "B1:Q48"]) dashboard.getRange(colRange).format.columnWidth = 12;

// ---------------- Task taxonomy ----------------
titleBand(taxonomy, ["A1:M1", "A2:M2"], "任务分类与检索边界", "三大类下细分为 24 个可操作任务；末两列由统计汇总公式引用。" );
const taxonomyHeaders = [
  "大类代码", "大类", "动作对象/方式", "诊断证据", "任务代码", "具体任务", "Task (EN)",
  "纳入定义", "主要排除", "精确短语组", "定向宽检索", "核心计数", "扩展上界",
];
taxonomy.getRange("A4:M4").values = [taxonomyHeaders];
styleHeader(taxonomy.getRange("A4:M4"));
const taxonomyRows = tasks.map((task, index) => {
  const summaryRow = 4 + index;
  const broad = queryLog.find((row) => row.database === "OpenAlex" && row.task_code === task.code)?.query || "";
  const [exactPart, ...broadParts] = broad.split(" || ");
  return [
    task.class_code,
    CLASS[task.class_code].zh,
    CLASS[task.class_code].action,
    CLASS[task.class_code].evidence,
    task.code,
    task.task_zh,
    task.task_en,
    task.definition,
    task.exclusions,
    exactPart,
    broadParts.join(" || "),
    null,
    null,
  ];
});
taxonomy.getRange(`A5:M${4 + taxonomyRows.length}`).values = taxonomyRows;
taxonomy.getRange(`L5:L${4 + taxonomyRows.length}`).formulas = tasks.map((_, index) => [`='统计汇总'!E${4 + index}`]);
taxonomy.getRange(`M5:M${4 + taxonomyRows.length}`).formulas = tasks.map((_, index) => [`='统计汇总'!F${4 + index}`]);
styleBody(taxonomy.getRange(`A5:M${4 + taxonomyRows.length}`));
taxonomy.getRange(`A5:M${4 + taxonomyRows.length}`).format.wrapText = true;
taxonomy.getRange(`A5:A${4 + taxonomyRows.length}`).format.horizontalAlignment = "center";
taxonomy.getRange(`E5:E${4 + taxonomyRows.length}`).format.horizontalAlignment = "center";
taxonomy.getRange(`L5:M${4 + taxonomyRows.length}`).format.numberFormat = "#,##0";
taxonomy.tables.add(`A4:M${4 + taxonomyRows.length}`, true, "TaskTaxonomyTable");
taxonomy.freezePanes.freezeRows(4);
taxonomy.freezePanes.freezeColumns(5);
const taxonomyWidths = [8, 18, 32, 30, 9, 30, 34, 46, 46, 48, 34, 12, 12];
taxonomyWidths.forEach((width, i) => taxonomy.getRangeByIndexes(0, i, 4 + taxonomyRows.length, 1).format.columnWidth = width);

// ---------------- Included works: write before summary formulas ----------------
const worksHeaders = [
  "来源数据库", "来源ID", "DOI", "PMID", "年份", "发布日期", "大类代码", "大类", "任务代码", "具体任务",
  "证据层级", "题名", "期刊/载体", "文献类型", "被引次数", "证据URL", "命中任务", "匹配任务", "摘要",
];
works.getRange("A1:S1").values = [worksHeaders];
styleHeader(works.getRange("A1:S1"));
const worksRows = included.map((record) => [
  joinList(record.source_dbs),
  joinList(record.source_ids),
  clean(record.doi),
  clean(record.pmid),
  Number(record.year),
  asDate(record.publication_date),
  record.class_code,
  record.class_zh,
  record.primary_task,
  record.task_zh,
  record.evidence_tier,
  clean(record.title, 1000),
  clean(record.venue, 500),
  clean(record.work_type, 200),
  Number(record.cited_by_count || 0),
  clean(record.url, 1000),
  joinList(record.query_tasks),
  joinList(record.matched_tasks),
  clean(record.abstract, 30000),
]);
works.getRange(`A2:S${1 + worksRows.length}`).values = worksRows;
styleBody(works.getRange(`A2:S${1 + worksRows.length}`));
works.getRange(`F2:F${1 + worksRows.length}`).format.numberFormat = "yyyy-mm-dd";
works.getRange(`E2:E${1 + worksRows.length}`).format.numberFormat = "0";
works.getRange(`O2:O${1 + worksRows.length}`).format.numberFormat = "#,##0";
works.getRange(`L2:L${1 + worksRows.length}`).format.wrapText = true;
works.getRange(`S2:S${1 + worksRows.length}`).format.wrapText = true;
works.tables.add(`A1:S${1 + worksRows.length}`, true, "IncludedWorksTable");
works.freezePanes.freezeRows(1);
works.freezePanes.freezeColumns(5);
const worksWidths = [18, 24, 28, 12, 9, 13, 10, 20, 10, 34, 24, 62, 28, 18, 12, 42, 22, 22, 90];
worksWidths.forEach((width, i) => works.getRangeByIndexes(0, i, Math.min(worksRows.length + 1, 100), 1).format.columnWidth = width);

// ---------------- Statistical summary ----------------
titleBand(summary, ["A1:Q1", "A2:Q2"], "累计工作量统计汇总", "核心计数为主比较指标；扩展上界反映题名—摘要敏感性检索。所有数值均按唯一工作、唯一主任务计数。" );
const summaryHeaders = [
  "大类代码", "大类", "任务代码", "具体任务", "核心累计", "扩展上界", "扩展新增", "2016–2020 核心",
  "2021–2025 核心", "两期变化率", "2026 YTD 核心", "最早核心年份", "最新核心年份", "代表性证据", "证据URL", "纳入定义", "主要排除",
];
summary.getRange("A3:Q3").values = [summaryHeaders];
styleHeader(summary.getRange("A3:Q3"));
const worksEnd = 1 + worksRows.length;
const summaryRows = tasks.map((task) => {
  const reps = recordsByTask.get(task.code);
  const rep = reps[0] || {};
  return [
    task.class_code,
    CLASS[task.class_code].zh,
    task.code,
    task.task_zh,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    earliestByTask[task.code],
    latestByTask[task.code],
    clean(rep.title || "", 1000),
    clean(rep.url || "", 1000),
    task.definition,
    task.exclusions,
  ];
});
summary.getRange(`A4:Q${3 + tasks.length}`).values = summaryRows;
for (let i = 0; i < tasks.length; i++) {
  const row = 4 + i;
  summary.getRange(`E${row}:K${row}`).formulas = [[
    `=COUNTIFS('纳入文献'!$I$2:$I$${worksEnd},C${row},'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)")`,
    `=COUNTIF('纳入文献'!$I$2:$I$${worksEnd},C${row})`,
    `=F${row}-E${row}`,
    `=COUNTIFS('纳入文献'!$I$2:$I$${worksEnd},C${row},'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)",'纳入文献'!$E$2:$E$${worksEnd},">=2016",'纳入文献'!$E$2:$E$${worksEnd},"<=2020")`,
    `=COUNTIFS('纳入文献'!$I$2:$I$${worksEnd},C${row},'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)",'纳入文献'!$E$2:$E$${worksEnd},">=2021",'纳入文献'!$E$2:$E$${worksEnd},"<=2025")`,
    `=IF(H${row}=0,"",I${row}/H${row}-1)`,
    `=COUNTIFS('纳入文献'!$I$2:$I$${worksEnd},C${row},'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)",'纳入文献'!$E$2:$E$${worksEnd},2026)`,
  ]];
}
styleBody(summary.getRange(`A4:Q${3 + tasks.length}`));
summary.getRange(`D4:D${3 + tasks.length}`).format.wrapText = true;
summary.getRange(`N4:Q${3 + tasks.length}`).format.wrapText = true;
summary.getRange(`E4:I${3 + tasks.length}`).format.numberFormat = "#,##0";
summary.getRange(`J4:J${3 + tasks.length}`).format.numberFormat = "0.0%";
summary.getRange(`K4:M${3 + tasks.length}`).format.numberFormat = "0";
summary.tables.add(`A3:Q${3 + tasks.length}`, true, "TaskSummaryTable");

const classStart = 31;
sectionLabel(summary, `A${classStart}:G${classStart}`, "三大类汇总");
summary.getRange(`A${classStart + 1}:G${classStart + 1}`).values = [["大类代码", "大类", "核心累计", "扩展上界", "核心占比", "2021–2025 核心", "2026 YTD 核心"]];
styleHeader(summary.getRange(`A${classStart + 1}:G${classStart + 1}`));
for (let i = 0; i < 3; i++) {
  const row = classStart + 2 + i;
  const classCode = ["A", "R", "S"][i];
  summary.getRange(`A${row}:B${row}`).values = [[classCode, CLASS[classCode].zh]];
  summary.getRange(`C${row}:G${row}`).formulas = [[
    `=SUMIF($A$4:$A$${3 + tasks.length},A${row},$E$4:$E$${3 + tasks.length})`,
    `=SUMIF($A$4:$A$${3 + tasks.length},A${row},$F$4:$F$${3 + tasks.length})`,
    `=C${row}/SUM($C$${classStart + 2}:$C$${classStart + 4})`,
    `=SUMIF($A$4:$A$${3 + tasks.length},A${row},$I$4:$I$${3 + tasks.length})`,
    `=SUMIF($A$4:$A$${3 + tasks.length},A${row},$K$4:$K$${3 + tasks.length})`,
  ]];
}
styleBody(summary.getRange(`A${classStart + 2}:G${classStart + 4}`));
summary.getRange(`C${classStart + 2}:D${classStart + 4}`).format.numberFormat = "#,##0";
summary.getRange(`E${classStart + 2}:E${classStart + 4}`).format.numberFormat = "0.0%";
summary.getRange(`F${classStart + 2}:G${classStart + 4}`).format.numberFormat = "#,##0";
summary.freezePanes.freezeRows(3);
summary.freezePanes.freezeColumns(4);
const summaryWidths = [10, 20, 10, 34, 13, 13, 13, 15, 15, 13, 14, 13, 13, 62, 42, 50, 50];
summaryWidths.forEach((width, i) => summary.getRangeByIndexes(0, i, classStart + 5, 1).format.columnWidth = width);

// ---------------- Annual trends ----------------
titleBand(annual, ["A1:M1", "A2:M2"], "年度与累计趋势", "核心计数与扩展上界按发表年统计；2026 为截至 8 月 6 日的不完整年度。" );
const annualHeaders = [
  "年份", "主动观察_当年核心", "响应交互_当年核心", "采样交互_当年核心", "主动观察_累计核心", "响应交互_累计核心", "采样交互_累计核心",
  "全部_当年核心", "全部_累计核心", "主动观察_累计上界", "响应交互_累计上界", "采样交互_累计上界", "全部_累计上界",
];
annual.getRange("A3:M3").values = [annualHeaders];
styleHeader(annual.getRange("A3:M3"));
const firstYear = Math.min(...coreRecords.map((record) => Number(record.year)));
const years = Array.from({ length: 2026 - firstYear + 1 }, (_, index) => firstYear + index);
annual.getRange(`A4:A${3 + years.length}`).values = years.map((year) => [year]);
for (let i = 0; i < years.length; i++) {
  const row = 4 + i;
  annual.getRange(`B${row}:M${row}`).formulas = [[
    `=COUNTIFS('纳入文献'!$G$2:$G$${worksEnd},"A",'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)",'纳入文献'!$E$2:$E$${worksEnd},A${row})`,
    `=COUNTIFS('纳入文献'!$G$2:$G$${worksEnd},"R",'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)",'纳入文献'!$E$2:$E$${worksEnd},A${row})`,
    `=COUNTIFS('纳入文献'!$G$2:$G$${worksEnd},"S",'纳入文献'!$K$2:$K$${worksEnd},"Core (title-explicit)",'纳入文献'!$E$2:$E$${worksEnd},A${row})`,
    `=SUM($B$4:B${row})`,
    `=SUM($C$4:C${row})`,
    `=SUM($D$4:D${row})`,
    `=SUM(B${row}:D${row})`,
    `=SUM($H$4:H${row})`,
    `=COUNTIFS('纳入文献'!$G$2:$G$${worksEnd},"A",'纳入文献'!$E$2:$E$${worksEnd},"<="&A${row})`,
    `=COUNTIFS('纳入文献'!$G$2:$G$${worksEnd},"R",'纳入文献'!$E$2:$E$${worksEnd},"<="&A${row})`,
    `=COUNTIFS('纳入文献'!$G$2:$G$${worksEnd},"S",'纳入文献'!$E$2:$E$${worksEnd},"<="&A${row})`,
    `=SUM(J${row}:L${row})`,
  ]];
}
styleBody(annual.getRange(`A4:M${3 + years.length}`));
annual.getRange(`A4:M${3 + years.length}`).format.numberFormat = "#,##0";
annual.tables.add(`A3:M${3 + years.length}`, true, "AnnualTrendTable");
annual.freezePanes.freezeRows(3);
annual.getRange(`A1:M${3 + years.length}`).format.columnWidth = 18;

// ---------------- Chart helper data ----------------
titleBand(chartData, ["A1:L1", "A2:L2"], "图表数据（公式链接）", "以下辅助表均通过公式链接至统计汇总和年度趋势，供 Dashboard 原生图表审计。" );
sectionLabel(chartData, "A4:C4", "具体任务排名（核心 vs 扩展上界）");
chartData.getRange("A5:C5").values = [["任务", "核心计数", "扩展上界"]];
styleHeader(chartData.getRange("A5:C5"));
const rankedTasks = [...tasks].sort((a, b) => (metadata.core_task_counts[a.code] || 0) - (metadata.core_task_counts[b.code] || 0) || a.code.localeCompare(b.code));
for (let i = 0; i < rankedTasks.length; i++) {
  const task = rankedTasks[i];
  const sourceRow = 4 + taskIndex[task.code];
  const row = 6 + i;
  chartData.getRange(`A${row}:C${row}`).formulas = [[
    `='统计汇总'!C${sourceRow}&" "&'统计汇总'!D${sourceRow}`,
    `='统计汇总'!E${sourceRow}`,
    `='统计汇总'!F${sourceRow}`,
  ]];
}
styleBody(chartData.getRange(`A6:C${5 + tasks.length}`));
chartData.getRange(`B6:C${5 + tasks.length}`).format.numberFormat = "#,##0";

sectionLabel(chartData, "E4:G4", "三大类累计规模");
chartData.getRange("E5:G5").values = [["大类", "核心计数", "扩展上界"]];
styleHeader(chartData.getRange("E5:G5"));
for (let i = 0; i < 3; i++) {
  const row = 6 + i;
  const sourceRow = classStart + 2 + i;
  chartData.getRange(`E${row}:G${row}`).formulas = [[
    `='统计汇总'!B${sourceRow}`,
    `='统计汇总'!C${sourceRow}`,
    `='统计汇总'!D${sourceRow}`,
  ]];
}
styleBody(chartData.getRange("E6:G8"));
chartData.getRange("F6:G8").format.numberFormat = "#,##0";

sectionLabel(chartData, "E11:H11", "核心工作累计曲线");
chartData.getRange("E12:H12").values = [["年份", "主动观察式", "响应式交互", "采样式交互"]];
styleHeader(chartData.getRange("E12:H12"));
for (let i = 0; i < years.length; i++) {
  const row = 13 + i;
  const sourceRow = 4 + i;
  chartData.getRange(`E${row}:H${row}`).formulas = [[
    `='年度趋势'!A${sourceRow}`,
    `='年度趋势'!E${sourceRow}`,
    `='年度趋势'!F${sourceRow}`,
    `='年度趋势'!G${sourceRow}`,
  ]];
}
styleBody(chartData.getRange(`E13:H${12 + years.length}`));
chartData.getRange(`E13:H${12 + years.length}`).format.numberFormat = "#,##0";
chartData.freezePanes.freezeRows(5);
chartData.getRange("A1:A40").format.columnWidth = 44;
chartData.getRange("B1:C40").format.columnWidth = 14;
chartData.getRange("E1:E50").format.columnWidth = 20;
chartData.getRange("F1:H50").format.columnWidth = 16;

// Native charts on Dashboard.
const taskChart = dashboard.charts.add("bar", {
  chartType: "bar",
  title: "24 个具体任务累计工作量（核心 vs 扩展上界）",
  hasLegend: true,
  barOptions: { direction: "bar", grouping: "clustered", gapWidth: 45 },
});
const taskCoreSeries = taskChart.series.add("核心计数");
taskCoreSeries.categoryFormula = `'图表数据'!$A$6:$A$${5 + tasks.length}`;
taskCoreSeries.formula = `'图表数据'!$B$6:$B$${5 + tasks.length}`;
taskCoreSeries.fill = COLORS.blue;
const taskUpperSeries = taskChart.series.add("扩展上界");
taskUpperSeries.categoryFormula = `'图表数据'!$A$6:$A$${5 + tasks.length}`;
taskUpperSeries.formula = `'图表数据'!$C$6:$C$${5 + tasks.length}`;
taskUpperSeries.fill = COLORS.gray400;
taskChart.title = "24 个具体任务累计工作量（论文数）";
taskChart.titleTextStyle.fontSize = 12;
taskChart.titleTextStyle.fontFamily = FONT_NAME;
taskChart.hasLegend = true;
taskChart.xAxis = { numberFormatCode: "#,##0", textStyle: { fontSize: 9, fontFamily: FONT_NAME } };
taskChart.yAxis = { textStyle: { fontSize: 8, fontFamily: FONT_NAME } };
taskChart.setPosition("A12", "I44");

const classChart = dashboard.charts.add("bar", {
  chartType: "bar",
  title: "三大类累计规模",
  hasLegend: true,
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 80 },
  dataLabels: { showValue: true, position: "outEnd" },
});
const classCore = classChart.series.add("核心计数");
classCore.categoryFormula = `'图表数据'!$E$6:$E$8`;
classCore.formula = `'图表数据'!$F$6:$F$8`;
classCore.fill = COLORS.teal;
const classUpper = classChart.series.add("扩展上界");
classUpper.categoryFormula = `'图表数据'!$E$6:$E$8`;
classUpper.formula = `'图表数据'!$G$6:$G$8`;
classUpper.fill = COLORS.gray400;
classChart.title = "三大类累计规模（论文数）";
classChart.titleTextStyle.fontSize = 12;
classChart.titleTextStyle.fontFamily = FONT_NAME;
classChart.xAxis = { numberFormatCode: "#,##0", textStyle: { fontSize: 9, fontFamily: FONT_NAME } };
classChart.yAxis = { textStyle: { fontSize: 9, fontFamily: FONT_NAME } };
classChart.setPosition("J12", "Q28");

const trendChart = dashboard.charts.add("line", {
  chartType: "line",
  title: "三大类核心工作累计增长",
  hasLegend: true,
});
for (const [name, column, color] of [
  ["主动观察式", "F", CLASS.A.color],
  ["响应式交互", "G", CLASS.R.color],
  ["采样式交互", "H", CLASS.S.color],
]) {
  const series = trendChart.series.add(name);
  series.categoryFormula = `'图表数据'!$E$13:$E$${12 + years.length}`;
  series.formula = `'图表数据'!$${column}$13:$${column}$${12 + years.length}`;
  series.fill = color;
}
trendChart.title = "三大类核心工作累计增长（1995–2026 YTD）";
trendChart.titleTextStyle.fontSize = 12;
trendChart.titleTextStyle.fontFamily = FONT_NAME;
trendChart.hasLegend = true;
trendChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 8, fontFamily: FONT_NAME } };
trendChart.yAxis = { numberFormatCode: "#,##0", textStyle: { fontSize: 9, fontFamily: FONT_NAME } };
trendChart.setPosition("J30", "Q44");

// ---------------- Screening log ----------------
const screeningHeaders = ["来源数据库", "来源ID", "DOI", "年份", "题名", "命中任务", "是否纳入扩展集", "排除原因", "主任务", "证据层级", "证据URL"];
screening.getRange("A1:K1").values = [screeningHeaders];
styleHeader(screening.getRange("A1:K1"));
const screeningRows = candidates.map((record) => [
  joinList(record.source_dbs),
  joinList(record.source_ids),
  clean(record.doi),
  Number(record.year || 0) || "",
  clean(record.title, 1000),
  joinList(record.query_tasks),
  Boolean(record.included),
  clean(record.exclusion_reason, 500),
  clean(record.primary_task),
  clean(record.evidence_tier),
  clean(record.url, 1000),
]);
screening.getRange(`A2:K${1 + screeningRows.length}`).values = screeningRows;
styleBody(screening.getRange(`A2:K${1 + screeningRows.length}`));
screening.getRange(`E2:E${1 + screeningRows.length}`).format.wrapText = true;
screening.getRange(`H2:H${1 + screeningRows.length}`).format.wrapText = true;
screening.tables.add(`A1:K${1 + screeningRows.length}`, true, "ScreeningLogTable");
screening.freezePanes.freezeRows(1);
screening.freezePanes.freezeColumns(4);
const screeningWidths = [18, 24, 28, 10, 64, 22, 16, 34, 12, 24, 42];
screeningWidths.forEach((width, i) => screening.getRangeByIndexes(0, i, Math.min(screeningRows.length + 1, 100), 1).format.columnWidth = width);

// ---------------- Query log and sources ----------------
titleBand(queries, ["A1:J1", "A2:J2"], "检索式、命中数与数据来源", "搜索命中数仅用于审计，不能相加为工作量；工作量来自跨查询去重后的纳入集。" );
const queryHeaders = ["数据库", "大类", "任务代码", "具体任务", "查询式", "原始命中数", "实际抓取", "联合纳入（带该查询标签）", "检索日期", "API/来源URL"];
queries.getRange("A4:J4").values = [queryHeaders];
styleHeader(queries.getRange("A4:J4"));
const queryRows = queryLog.map((row) => {
  const task = tasks[taskIndex[row.task_code]];
  return [
    row.database,
    CLASS[row.class_code].zh,
    row.task_code,
    task.task_zh,
    clean(row.query, 20000),
    Number(row.raw_hit_count || 0),
    Number(row.retrieved_records || 0),
    Number(row.union_included_with_query_tag || 0),
    asDate(row.retrieved_on),
    row.database === "OpenAlex" ? "https://api.openalex.org/works" : "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
  ];
});
queries.getRange(`A5:J${4 + queryRows.length}`).values = queryRows;
styleBody(queries.getRange(`A5:J${4 + queryRows.length}`));
queries.getRange(`E5:E${4 + queryRows.length}`).format.wrapText = true;
queries.getRange(`F5:H${4 + queryRows.length}`).format.numberFormat = "#,##0";
queries.getRange(`I5:I${4 + queryRows.length}`).format.numberFormat = "yyyy-mm-dd";
queries.tables.add(`A4:J${4 + queryRows.length}`, true, "QueryLogTable");
queries.freezePanes.freezeRows(4);
const queryWidths = [16, 22, 10, 34, 72, 14, 14, 20, 14, 52];
queryWidths.forEach((width, i) => queries.getRangeByIndexes(0, i, 4 + queryRows.length, 1).format.columnWidth = width);

// ---------------- Methods ----------------
titleBand(methods, ["A1:H1", "A2:H2"], "口径、流程与局限", "这是一份可复现的开放文献计量，不是全文系统综述或监管产品清单。" );
sectionLabel(methods, "A4:H4", "计数口径");
const methodRows = [
  ["统计单位", "去重后的原创研究出版物（article / conference-indexed article / preprint / report / dissertation）；不是设备、专利、临床试验或产品数量。"],
  ["时间范围", `1900-01-01 至 ${metadata.cutoff}；2026 年为截至 8 月 6 日的不完整年度。`],
  ["主数据源", "OpenAlex：跨学科覆盖工程、医学、会议与预印本；Europe PMC：补充医学题名/摘要记录并作医学侧交叉验证。arXiv 预印本通过 OpenAlex 纳入，不单独叠加。"],
  ["检索单元", "每个具体任务使用机器人/自主性短语与任务短语的题名—摘要组合；对首次检索接近零的任务增加定向 robot + task 宽检索，再执行同一纳入规则。"],
  ["去重", "优先 DOI；随后使用去 HTML、统一 Unicode/标点并去除短尾注的规范化题名；同一工作命中多个查询时合并查询标签。"],
  ["任务归属", "每篇纳入工作仅指定一个主任务。实际取样动作优先于观察导航；响应式任务优先于仅观察；其余按任务特异度评分。"],
  ["核心计数", "题名同时明确出现机器人/自主具身动作与具体任务，且通过原创研究、临床场景和非治疗专属规则。用于主比较，是高精度下界。"],
  ["扩展上界", "题名或摘要满足确定性规则，但题名未必同时显式出现两要素。用于敏感性分析，可能包含少量边界工作。"],
];
methods.getRange(`A5:A${4 + methodRows.length}`).values = methodRows.map((row) => [row[0]]);
for (let i = 0; i < methodRows.length; i++) {
  const row = 5 + i;
  methods.getRange(`B${row}:H${row}`).merge();
  methods.getRange(`B${row}:H${row}`).values = [[methodRows[i][1]]];
}
methods.getRange(`A5:H${4 + methodRows.length}`).format = {
  fill: COLORS.gray50,
  font: { name: FONT_NAME, color: COLORS.gray700, size: 10 },
  wrapText: true,
  verticalAlignment: "top",
  borders: { preset: "inside", style: "thin", color: COLORS.gray200 },
};
methods.getRange(`A5:A${4 + methodRows.length}`).format.font = { name: FONT_NAME, bold: true, color: COLORS.navy };
methods.getRange(`A5:H${4 + methodRows.length}`).format.rowHeight = 46;

sectionLabel(methods, "A14:H14", "数据流与对账");
methods.getRange("A15:D15").values = [["阶段", "记录数", "说明", "对账"]];
styleHeader(methods.getRange("A15:D15"));
const flowRows = [
  ["跨查询原始抓取", metadata.raw_records, "含数据库与任务查询间重复", "非可加总工作量"],
  ["去重候选", metadata.deduplicated_candidates, "DOI + 规范化题名", `${metadata.raw_records - metadata.deduplicated_candidates} 条重复被合并`],
  ["扩展纳入", metadata.included_records, "通过题名—摘要任务规则", `${metadata.deduplicated_candidates - metadata.included_records} 条排除`],
  ["核心纳入", coreTotal, "题名显式高精度层", `等于三大类 ${metadata.core_class_counts.A}+${metadata.core_class_counts.R}+${metadata.core_class_counts.S}`],
];
methods.getRange("A16:D19").values = flowRows;
styleBody(methods.getRange("A16:D19"));
methods.getRange("B16:B19").format.numberFormat = "#,##0";

sectionLabel(methods, "A21:H21", "主要局限");
const limitations = [
  "开放数据库覆盖、语言、会议论文和摘要可得性并不均一；因此数字是可复现估计，不是全世界真实全集。",
  "扩展层是敏感性上界，尚未逐篇全文人工双人筛选；核心层以较高精度换取召回损失。",
  "预印本与正式版本仅在 DOI 或规范化题名一致时合并；题名变化较大的版本可能仍重复。",
  "2026 年不完整，不能与完整自然年直接比较；趋势判断应优先看截至 2025 年的五年窗。",
  "核心计数为 0 只表示严格检索未找到；建议在立项前对该任务做专项全文检索和专利/产品补充。",
];
for (let i = 0; i < limitations.length; i++) {
  const row = 22 + i;
  methods.getRange(`A${row}:H${row}`).merge();
  methods.getRange(`A${row}:H${row}`).values = [[`${i + 1}. ${limitations[i]}`]];
}
methods.getRange("A22:H26").format = {
  fill: COLORS.amberLight,
  font: { name: FONT_NAME, color: COLORS.gray700, size: 10 },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "inside", style: "thin", color: COLORS.amber },
};
methods.getRange("A22:H26").format.rowHeight = 34;

sectionLabel(methods, "A28:H28", "方法与数据库来源");
methods.getRange("A29:D29").values = [["来源", "用途", "URL", "访问日期"]];
styleHeader(methods.getRange("A29:D29"));
const sourceRows = [
  ["OpenAlex Developers Overview", "跨学科开放研究目录与 API 说明", "https://developers.openalex.org/", asDate(metadata.retrieved_on)],
  ["OpenAlex Works API", "主检索与题名/摘要记录", "https://api.openalex.org/works", asDate(metadata.retrieved_on)],
  ["OpenAlex methods paper", "数据集引用", "https://arxiv.org/abs/2205.01833", asDate(metadata.retrieved_on)],
  ["Europe PMC RESTful API", "医学文献补充与交叉验证", "https://europepmc.org/RestfulWebService", asDate(metadata.retrieved_on)],
  ["Europe PMC search endpoint", "题名/摘要检索", "https://www.ebi.ac.uk/europepmc/webservices/rest/search", asDate(metadata.retrieved_on)],
];
methods.getRange("A30:D34").values = sourceRows;
styleBody(methods.getRange("A30:D34"));
methods.getRange("D30:D34").format.numberFormat = "yyyy-mm-dd";
methods.freezePanes.freezeRows(2);
methods.getRange("A1:A40").format.columnWidth = 22;
methods.getRange("B1:B40").format.columnWidth = 28;
methods.getRange("C1:C40").format.columnWidth = 62;
methods.getRange("D1:D40").format.columnWidth = 16;
methods.getRange("E1:H40").format.columnWidth = 16;

// ---------------- Compact QA ----------------
const dashboardCheck = await workbook.inspect({
  kind: "table",
  range: "Dashboard!A1:Q10",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 18,
  maxChars: 7000,
});
console.log(dashboardCheck.ndjson);

const summaryCheck = await workbook.inspect({
  kind: "table",
  range: "统计汇总!A3:Q10",
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: 18,
  maxChars: 9000,
});
console.log(summaryCheck.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
  maxChars: 5000,
});
console.log(errors.ndjson);

await fs.mkdir(qaDir, { recursive: true });
const renderRanges = {
  Dashboard: "A1:Q48",
  "任务分类": "A1:M18",
  "统计汇总": "A1:Q20",
  "年度趋势": "A1:M20",
  "图表数据": "A1:H28",
  "纳入文献": "A1:S18",
  "筛选日志": "A1:K18",
  "检索式与来源": "A1:J18",
  "方法说明": "A1:H34",
};
for (const [sheetName, range] of Object.entries(renderRanges)) {
  const preview = await workbook.render({ sheetName, range, scale: sheetName === "Dashboard" ? 1.0 : 0.8, format: "png" });
  const safeName = sheetName.replace(/[^\p{L}\p{N}_-]+/gu, "_");
  await fs.writeFile(path.join(qaDir, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, coreTotal, expandedTotal, sheets: renderRanges }, null, 2));
