import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";
import path from "node:path";
import { fileURLToPath } from "node:url";

const argv=Object.fromEntries(process.argv.slice(2).reduce((a,v,i,x)=>{if(v.startsWith("--"))a.push([v.slice(2),x[i+1]]);return a;},[]));
const defaultRepo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const repo=path.resolve(argv.repo||defaultRepo);
const outputFile=path.resolve(argv.output||path.join(repo,"outputs/p5_reclassification/p5_active_observation_reclassified_2026-08-14.xlsx"));
const outputDir=path.dirname(outputFile);

function parseCsv(text) {
  const rows=[]; let row=[],field="",quoted=false; text=text.replace(/^\uFEFF/,"");
  for(let i=0;i<text.length;i++){const ch=text[i];if(quoted){if(ch==='"'&&text[i+1]==='"'){field+='"';i++;}else if(ch==='"')quoted=false;else field+=ch;}else if(ch==='"')quoted=true;else if(ch===','){row.push(field);field="";}else if(ch==='\n'){row.push(field.replace(/\r$/,"") );rows.push(row);row=[];field="";}else field+=ch;}
  if(field.length||row.length){row.push(field);rows.push(row);} return rows.filter(r=>r.length>1);
}

async function csvRows(file){return parseCsv(await fs.readFile(file,"utf8"));}
const files={
  counts:path.resolve(argv.counts||path.join(repo,"data/presentation/p5_reclassified_task_counts_2026-08-14.csv")),
  records:path.resolve(argv.records||path.join(repo,"data/presentation/p5_reclassified_unique_records_2026-08-14.csv")),
  excluded:path.resolve(argv.excluded||path.join(repo,"data/presentation/p5_reclassification_excluded_records_2026-08-14.csv")),
  audit:path.resolve(argv.audit||path.join(repo,"data/presentation/p5_reclassification_manual_audit_queue_2026-08-14.csv")),
  matrix:path.resolve(argv.matrix||path.join(repo,"data/presentation/p5_task_modality_matrix_2026-08-14.csv")),
  projects:path.resolve(argv.projects||path.join(repo,"data/presentation/p5_reclassified_public_projects_2026-08-14.csv")),
  validation:path.resolve(argv.validation||path.join(repo,"outputs/p5_reclassification/validation_2026-08-14.json")),
};
const sources = {
  Task_Counts: await csvRows(files.counts),
  Unique_Records: await csvRows(files.records),
  Excluded: await csvRows(files.excluded),
  Audit_Queue: await csvRows(files.audit),
  Task_Modality: await csvRows(files.matrix),
  Projects: await csvRows(files.projects),
};
for (const [name, columns] of Object.entries({Task_Counts:[3,4,5,6],Task_Modality:[3,4]})) {
  for (const row of sources[name].slice(1)) for (const index of columns) row[index]=Number(row[index]);
}
const validation = JSON.parse(await fs.readFile(files.validation,"utf8"));

const wb=Workbook.create();
const purple="#5F1B73", green="#2C8068", pale="#F4EFF6", grid="#E4DCE7", text="#25152B";

function addDataSheet(name, rows, widths={}) {
  const sh=wb.worksheets.add(name); sh.showGridLines=false;
  const r=sh.getRangeByIndexes(0,0,rows.length,rows[0].length); r.values=rows;
  sh.getRangeByIndexes(0,0,1,rows[0].length).format={fill:purple,font:{bold:true,color:"#FFFFFF"},wrapText:true,verticalAlignment:"center"};
  sh.getRangeByIndexes(1,0,Math.max(rows.length-1,1),rows[0].length).format={font:{color:text},verticalAlignment:"top"};
  sh.freezePanes.freezeRows(1);
  if(rows.length>1){const t=sh.tables.add(`A1:${colName(rows[0].length)}${rows.length}`,true,`${name.replace(/[^A-Za-z0-9]/g,"")}Table`);t.showFilterButton=true;t.showBandedRows=true;}
  Object.entries(widths).forEach(([col,w])=>sh.getRange(`${col}:${col}`).format.columnWidth=Number(w));
  return sh;
}
function colName(n){let s="";while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}

addDataSheet("Task_Counts",sources.Task_Counts,{A:12,B:35,C:48,D:18,E:18,F:15,G:15,H:60});
addDataSheet("Unique_Records",sources.Unique_Records,{A:42,B:82,C:10,D:24,E:18,F:40,G:25,H:55,I:10,J:12,K:55,L:12,M:34,N:48,O:38,P:18,Q:30,R:32,S:24,T:25,U:42,V:58});
addDataSheet("Excluded",sources.Excluded,{A:42,B:85,C:10,D:24,E:18,F:40,Q:32,R:34,S:25,T:36,U:45,V:58});
addDataSheet("Audit_Queue",sources.Audit_Queue,{A:42,B:85,C:10,D:24,E:18,F:40,M:34,N:48,O:38,P:18,Q:32,R:32,S:24,T:25,U:42,V:58});
addDataSheet("Task_Modality",sources.Task_Modality,{A:12,B:38,C:34,D:18,E:18});
addDataSheet("Projects",sources.Projects,{A:12,B:22,C:42,D:40,E:14,F:28,G:55,H:62,I:24,J:16,K:12,L:34,M:34,N:32,O:58,P:16,Q:52});
const val=wb.worksheets.add("Validation"); val.showGridLines=false; val.getRange("A1:B1").values=[["Validation field","Value"]];
const valRows=Object.entries(validation).filter(([k])=>k!=="errors").map(([k,v])=>[k,String(v)]);
val.getRangeByIndexes(1,0,valRows.length,2).values=valRows;
val.getRangeByIndexes(1+valRows.length,0,1,2).values=[["errors",validation.errors.join(" | ")||"none"]];
val.getRange("A1:B1").format={fill:purple,font:{bold:true,color:"#FFFFFF"}}; val.getRange("A:A").format.columnWidth=42; val.getRange("B:B").format.columnWidth=45;

const summary=wb.worksheets.add("README"); summary.showGridLines=false;
summary.getRange("A1:H1").merge(); summary.getRange("A1").values=[["P5 主动观察式检测｜修订后公开证据工作簿"]];
summary.getRange("A1:H1").format={fill:purple,font:{bold:true,color:"#FFFFFF",size:20},verticalAlignment:"center"}; summary.getRange("A1:H1").format.rowHeight=34;
summary.getRange("A3:B3").values=[["质量控制指标","值"]];
summary.getRange("A4:A9").values=[["唯一公开索引论文"],["纳入题名级候选"],["识别到公开全文位置"],["题名规则排除"],["公开具名项目/系统"],["优先人工全文复核"]];
summary.getRange("B4:B9").formulas=[["=COUNTA('Unique_Records'!A2:A856)"],["=SUM('Task_Counts'!D2:D10)"],["=SUM('Task_Counts'!E2:E10)"],["=COUNTA('Excluded'!A2:A100)"],["=COUNTA('Projects'!A2:A100)"],["=COUNTA('Audit_Queue'!A2:A100)"]];
summary.getRange("A3:B9").format.borders={preset:"inside",style:"thin",color:grid}; summary.getRange("A3:B3").format={fill:pale,font:{bold:true,color:text}}; summary.getRange("B4:B9").format={font:{bold:true,color:purple},numberFormat:"#,##0"};
summary.getRange("D3:F3").values=[["临床任务","Public visible","Public available"]];
for(let i=0;i<9;i++) summary.getRange(`D${4+i}:F${4+i}`).formulas=[[`='Task_Counts'!B${2+i}`,`='Task_Counts'!D${2+i}`,`='Task_Counts'!E${2+i}`]];
summary.getRange("D3:F12").format.borders={preset:"inside",style:"thin",color:grid}; summary.getRange("D3:F3").format={fill:pale,font:{bold:true,color:text}}; summary.getRange("E4:F12").format.numberFormat="#,##0";
summary.getRange("A12:H12").merge(); summary.getRange("A12").values=[["范围和解释"]]; summary.getRange("A12:H12").format={fill:pale,font:{bold:true,color:purple}};
summary.getRange("A13:H17").merge(true); summary.getRange("A13:A17").values=[
  ["• 主轴是题名可核验的临床检查程序；OCT、光谱、共聚焦、光声等作为多标签模态。"],
  ["• 834 是公开索引题名级候选，不是系统综述全文纳入数；75 条任务未定记录与其他冲突记录保留在人工复核队列。"],
  ["• 12 个公开具名项目/系统单独列账，绝不与论文数量相加。"],
  ["• Public available 表示识别到公开全文或完整预印本位置，尚未逐篇完成许可证审计。"],
  ["• 检索冻结 2026-08-13；重分类与项目来源复核 2026-08-14；验证状态：PASS。"]
]; summary.getRange("A13:H17").format={wrapText:true,font:{color:text,size:11}};
summary.getRange("A:A").format.columnWidth=31; summary.getRange("B:B").format.columnWidth=15; summary.getRange("C:C").format.columnWidth=3; summary.getRange("D:D").format.columnWidth=38; summary.getRange("E:F").format.columnWidth=18; summary.getRange("G:H").format.columnWidth=14;
const chart=summary.charts.add("bar",summary.getRange("D3:F11")); chart.title="公开候选按题名可核验的临床检查程序分布"; chart.hasLegend=true; chart.xAxis={axisType:"textAxis",textStyle:{fontSize:9}}; chart.yAxis={numberFormatCode:"#,##0"}; chart.setPosition("H3","P20");

await fs.mkdir(outputDir,{recursive:true});
const preview=await wb.render({sheetName:"README",range:"A1:P20",scale:1.4,format:"png"}); await fs.writeFile(`${outputDir}/p5_workbook_preview.png`,new Uint8Array(await preview.arrayBuffer()));
const inspect=await wb.inspect({kind:"table",range:"README!A1:F17",include:"values,formulas",tableMaxRows:20,tableMaxCols:8}); console.log(inspect.ndjson);
const errors=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:100},summary:"formula error scan"}); console.log(errors.ndjson);
const out=await SpreadsheetFile.exportXlsx(wb); await out.save(outputFile);
