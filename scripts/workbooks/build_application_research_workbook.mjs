import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const output = path.join(root, "outputs/application_landscape/application_research_workspace.xlsx");

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ""; }
    else if (c === '\n') { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const headers = rows.shift();
  return rows.filter(r => r.some(Boolean)).map(r => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

const readCsv = async rel => parseCsv(await fs.readFile(path.join(root, rel), "utf8"));
const evidence = await readCsv("data/presentation/application_evidence.csv");
const slides = await readCsv("data/presentation/slide_plan.csv");
const tasks = await readCsv("outputs/application_landscape/clinical_task_candidate_counts.csv");
const categories = await readCsv("outputs/application_landscape/clinical_category_candidate_counts.csv");

const wb = Workbook.create();
const purple = "#5B1A6E", purple2 = "#7A3E8E", pale = "#F4EDF7", grid = "#D9D2DC", ink = "#25212A", muted = "#6D6672", green = "#2E7D65", orange = "#B45F06";
const font = "Noto Sans CJK SC";

function title(sheet, range, text) {
  const r = sheet.getRange(range); r.merge(); r.values = [[text]];
  r.format = { fill: purple, font: { name: font, size: 16, bold: true, color: "#FFFFFF" }, verticalAlignment: "center" };
  r.format.rowHeight = 32;
}
function header(r) { r.format = { fill: purple2, font: { name: font, size: 10, bold: true, color: "#FFFFFF" }, wrapText: true, verticalAlignment: "center", horizontalAlignment: "center", borders: { preset: "all", style: "thin", color: grid } }; r.format.rowHeight = 34; }
function body(r) { r.format = { font: { name: font, size: 9, color: ink }, wrapText: true, verticalAlignment: "top", borders: { preset: "all", style: "thin", color: grid } }; }

const readme = wb.worksheets.add("README"); readme.showGridLines = false;
title(readme, "A1:F1", "Embodied Diagnostics Application Research Workspace");
readme.getRange("A3:F3").merge(); readme.getRange("A3").values = [["Purpose / 用途：支持综述 Application 部分和组会汇报，从 P5 起将逐页内容、代表性一手证据与可复现计量结果连接起来。候选量不等于临床成熟度。"]];
readme.getRange("A3:F3").format = { fill: pale, font: { name: font, size: 11, bold: true, color: purple }, wrapText: true, verticalAlignment: "center" }; readme.getRange("A3:F3").format.rowHeight = 52;
readme.getRange("A6:F6").values = [["Sheet", "Unit", "Rows", "Status", "Use", "Caution"]]; header(readme.getRange("A6:F6"));
readme.getRange("A7:F10").values = [
  ["Slide_Plan", "one planned slide", slides.length, "curated", "P5 onward narrative and supporting asset plan", "page plan can change with the manuscript"],
  ["Evidence_Ledger", "one representative system/study", evidence.length, "primary-source anchored", "sample size, action, feedback, hardware, boundary", "representative; not systematic prevalence"],
  ["Clinical_Tasks", "unique task-paper candidate", tasks.reduce((a,r)=>a+(Number(r.unique_closed_loop_candidates)||0),0), "reproducible snapshot", "research-volume comparison", "not global totals or maturity"],
  ["Clinical_Categories", "unique paper inside category", categories.reduce((a,r)=>a+(Number(r.unique_candidate_papers)||0),0), "reproducible snapshot", "category-level context", "multi-label papers can occur across categories"],
]; body(readme.getRange("A7:F10")); readme.getRange("A7:F10").format.rowHeight = 46;
readme.getRange("A13:F13").merge(); readme.getRange("A13").values = [["Evidence statement rule / 证据表述规则：Fact = paper-reported result; Inference = synthesis constrained by evidence; Research proposal = testable future loop. Do not merge these levels in prose or figures."]];
readme.getRange("A13:F13").format = { fill: "#FFF2CC", font: { name: font, size: 10, bold: true, color: orange }, wrapText: true }; readme.getRange("A13:F13").format.rowHeight = 46;
readme.getRange("A1:A15").format.columnWidth = 24; readme.getRange("B1:B15").format.columnWidth = 25; readme.getRange("C1:D15").format.columnWidth = 14; readme.getRange("E1:F15").format.columnWidth = 42;

function writeSheet(name, rows, headers, widths) {
  const s = wb.worksheets.add(name); s.showGridLines = false; title(s, `A1:${String.fromCharCode(64 + headers.length)}1`, name.replaceAll("_", " "));
  s.getRange(`A3:${String.fromCharCode(64 + headers.length)}3`).values = [headers]; header(s.getRange(`A3:${String.fromCharCode(64 + headers.length)}3`));
  if (rows.length) { s.getRange(`A4:${String.fromCharCode(64 + headers.length)}${rows.length + 3}`).values = rows; body(s.getRange(`A4:${String.fromCharCode(64 + headers.length)}${rows.length + 3}`)); s.getRange(`A4:${String.fromCharCode(64 + headers.length)}${rows.length + 3}`).format.rowHeight = 58; }
  widths.forEach((w,i)=>s.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${rows.length+4}`).format.columnWidth=w);
  s.freezePanes.freezeRows(3); return s;
}

writeSheet("Slide_Plan", slides.map(r=>[Number(r.slide),r.title,r.communication_job,r.layout,r.supporting_material]), ["Slide","Title","Communication job","Suggested layout","Supporting evidence / asset"], [9,34,48,38,50]);
writeSheet("Evidence_Ledger", evidence.map(r=>[Number(r.slide),r.domain,r.direction,r.representative_system,r.physical_action,r.feedback_or_evidence,r.evidence_stage,r.key_result,r.hardware_or_data,r.interpretation,r.source]), ["Slide","Domain","Direction","Representative system","Physical action","Feedback / evidence","Evidence stage","Paper-reported result","Hardware / data","Interpretation / non-extrapolation","Source URL"], [8,22,28,30,34,34,24,45,38,48,42]);
const taskSheet=writeSheet("Clinical_Tasks", tasks.map(r=>[r.category,r.task,Number(r.unique_closed_loop_candidates),Number(r.candidates_since_2021),Number(r.recent_share),r.interpretation]), ["Category","Normalized task","Unique candidates","Since 2021","Recent share","Interpretation"], [32,34,15,15,14,50]); taskSheet.getRange(`E4:E${tasks.length+3}`).format.numberFormat="0.0%";
writeSheet("Clinical_Categories", categories.map(r=>[r.category,Number(r.unique_candidate_papers),r.counting_unit]), ["Category","Unique papers","Counting unit"], [40,18,54]);

await fs.mkdir(path.dirname(output), { recursive: true });
const exported = await SpreadsheetFile.exportXlsx(wb); await exported.save(output);
const inspect = await wb.inspect({ kind: "table", range: "README!A1:F14", include: "values,formulas", tableMaxRows: 14, tableMaxCols: 6 });
console.log(inspect.ndjson);
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "final formula error scan" });
console.log(errors.ndjson);
for (const [sheetName, range] of [["README","A1:F14"],["Slide_Plan",`A1:E${Math.min(slides.length+3,14)}`],["Evidence_Ledger",`A1:K${Math.min(evidence.length+3,10)}`],["Clinical_Tasks",`A1:F${Math.min(tasks.length+3,15)}`],["Clinical_Categories",`A1:C${categories.length+3}`]]) {
  const png = await wb.render({ sheetName, range, scale: 1.4 });
  await fs.writeFile(path.join(root, `tmp-${sheetName}.png`), new Uint8Array(await png.arrayBuffer()));
}
console.log(output);
