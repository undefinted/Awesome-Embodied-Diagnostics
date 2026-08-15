import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const args = Object.fromEntries(process.argv.slice(2).reduce((a,v,i,x)=>{if(v.startsWith("--"))a.push([v.slice(2),x[i+1]]);return a;},[]));
const repo = path.resolve(args.repo || path.join(path.dirname(fileURLToPath(import.meta.url)), "../.."));
const inputDir = path.resolve(args.input || path.join(repo, "outputs/clinical_detection_intervention"));
const output = path.resolve(args.output || path.join(inputDir, "clinical_detection_intervention_evidence_map_2026-08-15.xlsx"));

function parseCsv(text) {
  text=text.replace(/^\uFEFF/,""); const rows=[]; let row=[], field="", quoted=false;
  for(let i=0;i<text.length;i++){const c=text[i];if(quoted){if(c==='"'&&text[i+1]==='"'){field+='"';i++;}else if(c==='"')quoted=false;else field+=c;}else if(c==='"')quoted=true;else if(c===','){row.push(field);field="";}else if(c==='\n'){row.push(field.replace(/\r$/,"") );rows.push(row);row=[];field="";}else field+=c;}
  if(field.length||row.length){row.push(field);rows.push(row);} return rows.filter(r=>r.length>1);
}
async function readCsv(name){return parseCsv(await fs.readFile(path.join(inputDir,name),"utf8"));}
function colName(n){let s="";while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}
function numeric(rows, columns){for(const row of rows.slice(1))for(const c of columns){if(row[c]!=="")row[c]=Number(row[c]);}return rows;}

const sources = {
  Summary: numeric(await readCsv("clinical_detection_intervention_summary.csv"),[2,3,4,5,6,7]),
  Mechanisms: numeric(await readCsv("clinical_detection_intervention_mechanism_counts.csv"),[3,4,5,6,7]),
  Subtasks: numeric(await readCsv("clinical_detection_intervention_subtask_counts.csv"),[4,5,6,7]),
  Annual: numeric(await readCsv("clinical_detection_intervention_annual_counts.csv"),[0,1,2,3,4,5,6,7,8]),
  Unique_Records: numeric(await readCsv("clinical_detection_intervention_unique_records.csv"),[2,14,15]),
  Overlap_Audit: numeric(await readCsv("clinical_detection_intervention_overlap_audit.csv"),[2]),
  Retrieval_Audit: numeric(await readCsv("clinical_detection_intervention_retrieval_audit.csv"),[3,4,5]),
  Taxonomy: await readCsv("clinical_detection_intervention_taxonomy.csv"),
};
const qc=JSON.parse(await fs.readFile(path.join(inputDir,"clinical_detection_intervention_qc.json"),"utf8"));

const wb=Workbook.create();
const purple="#642176", green="#2F8A70", ink="#24172A", pale="#F4EFF6", grid="#E6DFE8", amber="#F5E7D2";

function addSheet(name, rows, widths={}){
  const sh=wb.worksheets.add(name); sh.showGridLines=false;
  sh.getRangeByIndexes(0,0,rows.length,rows[0].length).values=rows;
  sh.getRangeByIndexes(0,0,1,rows[0].length).format={fill:purple,font:{bold:true,color:"#FFFFFF"},wrapText:true,verticalAlignment:"center"};
  if(rows.length>1) sh.getRangeByIndexes(1,0,rows.length-1,rows[0].length).format={font:{color:ink},verticalAlignment:"top",wrapText:true};
  sh.freezePanes.freezeRows(1);
  if(rows.length>1){const t=sh.tables.add(`A1:${colName(rows[0].length)}${rows.length}`,true,`${name.replace(/[^A-Za-z0-9]/g,"")}Table`);t.showFilterButton=true;t.showBandedRows=true;}
  for(const [c,w] of Object.entries(widths)) sh.getRange(`${c}:${c}`).format.columnWidth=Number(w);
  return sh;
}

addSheet("Mechanism_Counts",sources.Mechanisms,{A:12,B:42,C:28,D:19,E:20,F:16,G:14,H:16,I:55});
addSheet("Subtask_Counts",sources.Subtasks,{A:12,B:12,C:52,D:36,E:19,F:20,G:16,H:14,I:54});
addSheet("Annual_Counts",sources.Annual,{A:12,B:16,C:16,D:16,E:16,F:16,G:16,H:18,I:18});
addSheet("Unique_Records",sources.Unique_Records,{A:42,B:80,C:10,D:25,E:15,F:38,G:28,H:12,I:48,J:38,K:30,L:34,M:10,N:12,O:65,P:55,Q:55,R:28});
addSheet("Overlap_Audit",sources.Overlap_Audit,{A:42,B:82,C:10,D:25,E:28,F:14,G:14,H:72,I:22});
addSheet("Retrieval_Audit",sources.Retrieval_Audit,{A:12,B:42,C:22,D:20,E:22,F:72});
addSheet("Taxonomy",sources.Taxonomy,{A:12,B:42,C:28,D:62,E:62,F:75,G:75,H:70});

const readme=wb.worksheets.add("README"); readme.showGridLines=false;
readme.getRange("A1:H1").merge(); readme.getRange("A1").values=[["Clinical Detection and Intervention | reproducible evidence map"]];
readme.getRange("A1:H1").format={fill:purple,font:{bold:true,color:"#FFFFFF",size:20},verticalAlignment:"center"}; readme.getRange("A1:H1").format.rowHeight=36;
readme.getRange("A3:B3").values=[["Comparable-core KPI","Value"]];
readme.getRange("A4:A10").values=[["Unique title-level candidates"],["Public full-text locations identified"],["Public availability share"],["Candidates since 2021"],["Cross-rule records resolved"],["Unscreened retrieval union"],["QC status"]];
readme.getRange("B4:B10").formulas=[["='Mechanism_Counts'!D2+'Mechanism_Counts'!D3+'Mechanism_Counts'!D4"],["='Mechanism_Counts'!E2+'Mechanism_Counts'!E3+'Mechanism_Counts'!E4"],["=B5/B4"],["='Mechanism_Counts'!G2+'Mechanism_Counts'!G3+'Mechanism_Counts'!G4"],[`=${qc.overlap_records_resolved}`],[`=${qc.retrieval_unique_union_unscreened}`],[`="${Object.values(qc.checks).every(Boolean)?"PASS":"CHECK"}"`]];
readme.getRange("A3:B10").format.borders={preset:"inside",style:"thin",color:grid}; readme.getRange("A3:B3").format={fill:pale,font:{bold:true,color:ink}}; readme.getRange("B4:B10").format={font:{bold:true,color:purple},numberFormat:"#,##0"}; readme.getRange("B6").format.numberFormat="0.0%";
readme.getRange("D3:F3").values=[["Mechanism","Public visible","Public available"]];
for(let i=0;i<3;i++)readme.getRange(`D${4+i}:F${4+i}`).formulas=[[`='Mechanism_Counts'!B${2+i}`,`='Mechanism_Counts'!D${2+i}`,`='Mechanism_Counts'!E${2+i}`]];
readme.getRange("D3:F6").format.borders={preset:"inside",style:"thin",color:grid}; readme.getRange("D3:F3").format={fill:pale,font:{bold:true,color:ink}}; readme.getRange("E4:F6").format.numberFormat="#,##0";
readme.getRange("A12:H12").merge(); readme.getRange("A12").values=[["Scope and interpretation"]]; readme.getRange("A12:H12").format={fill:pale,font:{bold:true,color:purple}};
const notes=[
  "• Primary mechanism is defined by the terminal diagnostic evidence action, not by robot morphology.",
  "• Assignment is mutually exclusive for counting: sample acquisition > elicited response > active observation. Secondary stage hits remain in Overlap_Audit.",
  "• The 322-work comparable core uses one frozen public-index corpus and one title-screen protocol across all three mechanisms.",
  "• The 1,111-work retrieval union is an unscreened coverage denominator; it is not a publication count and is not directly comparable across mechanisms.",
  "• Public available means an automated public location was identified; licences and full-text eligibility remain to be checked manually.",
  "• These are title-level candidates, not systematic-review inclusions. Full-text dual screening is required for publication-grade totals."
];
for(let i=0;i<notes.length;i++){readme.getRange(`A${13+i}:H${13+i}`).merge();readme.getRange(`A${13+i}`).values=[[notes[i]]];}
readme.getRange("A13:H18").format={wrapText:true,font:{color:ink,size:11}};
readme.getRange("A:A").format.columnWidth=35;readme.getRange("B:B").format.columnWidth=18;readme.getRange("C:C").format.columnWidth=3;readme.getRange("D:D").format.columnWidth=44;readme.getRange("E:F").format.columnWidth=18;readme.getRange("G:H").format.columnWidth=16;
const chart=readme.charts.add("bar",readme.getRange("D3:F6")); chart.title="Mutually exclusive mechanisms";chart.hasLegend=true;chart.xAxis={axisType:"textAxis",textStyle:{fontSize:9}};chart.yAxis={numberFormatCode:"#,##0"};chart.setPosition("H3","P18");
if(chart.series.items[0]) chart.series.items[0].fill=purple;
if(chart.series.items[1]) chart.series.items[1].fill=green;

const validation=wb.worksheets.add("Validation");validation.showGridLines=false;
const valRows=[["Validation field","Value"],...Object.entries(qc).map(([k,v])=>[k,typeof v==="object"?JSON.stringify(v):String(v)])];
validation.getRangeByIndexes(0,0,valRows.length,2).values=valRows;validation.getRange("A1:B1").format={fill:purple,font:{bold:true,color:"#FFFFFF"}};validation.getRange("A:A").format.columnWidth=42;validation.getRange("B:B").format.columnWidth=90;validation.getRange("A1:B20").format.wrapText=true;

await fs.mkdir(path.dirname(output),{recursive:true});
const preview=await wb.render({sheetName:"README",range:"A1:P19",scale:1.25,format:"png"});await fs.writeFile(path.join(path.dirname(output),"clinical_detection_intervention_workbook_preview.png"),new Uint8Array(await preview.arrayBuffer()));
const overview=await wb.inspect({kind:"sheet,table",maxChars:5000,tableMaxRows:5,tableMaxCols:8});console.log(overview.ndjson);
const errors=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:100},summary:"formula error scan"});console.log(errors.ndjson);
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(output);
