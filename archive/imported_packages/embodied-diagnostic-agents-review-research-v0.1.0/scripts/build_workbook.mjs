import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.env.RESEARCH_REPO_ROOT || path.resolve(import.meta.dirname, "..");
const csvText = await fs.readFile(path.join(root, "data", "references.csv"), "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "References" });
const references = workbook.worksheets.getItem("References");
const summary = workbook.worksheets.add("Summary");

// Preserve the CSV as the source of truth while coercing the binary core flag
// to a numeric value so downstream spreadsheet formulas remain auditable.
const imported = references.getRange("A1:Q59").values;
for (let row = 1; row < imported.length; row += 1) {
  imported[row][2] = Number(imported[row][2]);
}
references.getRange("A1:Q59").values = imported;
references.getRange("R1:Y1").values = [[
  "derived_has_doi",
  "derived_primary_verified",
  "derived_validation",
  "derived_human_centred",
  "derived_deployment",
  "derived_ethics",
  "derived_outlook",
  "derived_metadata_update",
]];
references.getRange("R2:Y2").formulas = [[
  "=IF(LEN(L2)>0,1,0)",
  '=IF(P2="verified_primary_2026-08-12",1,0)',
  '=IF(ISNUMBER(SEARCH("validation",D2)),1,0)',
  '=IF(ISNUMBER(SEARCH("human-centred-evaluation",D2)),1,0)',
  '=IF(ISNUMBER(SEARCH("deployment",D2)),1,0)',
  '=IF(ISNUMBER(SEARCH("ethics",D2)),1,0)',
  '=IF(ISNUMBER(SEARCH("outlook",D2)),1,0)',
  '=IF(ISNUMBER(SEARCH("metadata-update",D2)),1,0)',
]];
references.getRange("R2:Y59").fillDown();

references.showGridLines = false;
references.freezePanes.freezeRows(1);
references.getRange("A1:Y1").format = {
  fill: "#16324F",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  verticalAlignment: "center",
};
references.getRange("A1:Y59").format.font = { name: "Aptos", size: 10 };
references.getRange("A2:A59").format.columnWidth = 12;
references.getRange("B2:B59").format.columnWidth = 24;
references.getRange("C2:C59").format.columnWidth = 12;
references.getRange("D2:D59").format.columnWidth = 32;
references.getRange("E2:G59").format.columnWidth = 20;
references.getRange("H2:H59").format.columnWidth = 58;
references.getRange("I2:K59").format.columnWidth = 24;
references.getRange("L2:M59").format.columnWidth = 42;
references.getRange("N2:Q59").format.columnWidth = 34;
references.getRange("R2:Y59").format.columnWidth = 20;
references.getRange("A1:Y59").format.wrapText = true;
references.getRange("A1:Y59").format.verticalAlignment = "top";
references.getRange("A1:Y59").format.borders = { preset: "inside", style: "thin", color: "#D9E2EC" };
references.getRange("R1:Y59").format.fill = "#F2F5F7";
references.tables.add("A1:Y59", true, "ReferenceCatalog");

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["Embodied Diagnostic Agents — Literature Catalog"]];
summary.getRange("A1:H1").format = {
  fill: "#16324F",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "left",
};
summary.getRange("A3:D3").values = [["Catalog records", "Core references", "Records with DOI", "Primary-page verified"]];
summary.getRange("A4:D4").formulas = [[
  "=COUNTA('References'!$A$2:$A$200)",
  "=SUM('References'!$C$2:$C$200)",
  "=SUM('References'!$R$2:$R$200)",
  "=SUM('References'!$S$2:$S$200)",
]];
summary.getRange("A3:D3").format = { fill: "#D9EAF7", font: { bold: true, color: "#16324F" }, wrapText: true };
summary.getRange("A4:D4").format = { fill: "#F4F8FB", font: { bold: true, size: 15, color: "#0F766E" }, horizontalAlignment: "center" };
summary.getRange("A6:B6").values = [["Top-level section", "Reference count"]];
summary.getRange("A7:A12").values = [["validation"], ["human-centred-evaluation"], ["deployment"], ["ethics"], ["outlook"], ["metadata-update"]];
summary.getRange("B7:B12").formulas = [[
  "=SUM('References'!$T$2:$T$200)",
], [
  "=SUM('References'!$U$2:$U$200)",
], [
  "=SUM('References'!$V$2:$V$200)",
], [
  "=SUM('References'!$W$2:$W$200)",
], [
  "=SUM('References'!$X$2:$X$200)",
], [
  "=SUM('References'!$Y$2:$Y$200)",
]];
summary.getRange("A6:B6").format = { fill: "#16324F", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("A6:B12").format.borders = { preset: "outside", style: "thin", color: "#9FB3C8" };
summary.getRange("A14:H16").merge();
summary.getRange("A14").values = [["Interpretation boundary: reporting guidelines are not evidence of safety or effectiveness. Distinguish laboratory demonstrations, simulated evaluations, early clinical studies, randomized trials, and real-world deployment."]];
summary.getRange("A14:H16").format = { fill: "#FFF4D6", font: { color: "#5B4300" }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A1:H20").format.font = { name: "Aptos", size: 11 };
summary.getRange("A1:H20").format.columnWidth = 18;
summary.getRange("A1:A20").format.columnWidth = 28;

const chart = summary.charts.add("bar", summary.getRange("A6:B12"));
chart.title = "References by review section";
chart.hasLegend = false;
chart.setPosition("D6", "H13");

const outputDir = path.join(root, "outputs");
await fs.mkdir(outputDir, { recursive: true });
const preview = await workbook.render({ sheetName: "Summary", range: "A1:H16", scale: 1.5, format: "png" });
await fs.writeFile(path.join(outputDir, "literature_catalog_preview.png"), new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(path.join(outputDir, "literature_catalog.xlsx"));

const inspection = await workbook.inspect({
  kind: "table",
  range: "Summary!A1:H16",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 10,
});
await fs.writeFile(path.join(root, "results", "workbook_inspection.ndjson"), inspection.ndjson + "\n", "utf8");
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(root, "results", "workbook_formula_errors.ndjson"), errors.ndjson + "\n", "utf8");
