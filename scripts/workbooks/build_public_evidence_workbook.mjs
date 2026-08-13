import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const outDir = path.join(root, "outputs", "public_landscape");
const output = path.join(outDir, "public_available_presentation_evidence.xlsx");

function parseCsv(text) {
  const rows=[]; let row=[], field="", quoted=false;
  for(let i=0;i<text.length;i++){const c=text[i]; if(quoted){if(c==='"'&&text[i+1]==='"'){field+='"';i++;}else if(c==='"')quoted=false;else field+=c;}else if(c==='"')quoted=true;else if(c===','){row.push(field);field="";}else if(c==='\n'){row.push(field.replace(/\r$/,""));rows.push(row);row=[];field="";}else field+=c;}
  if(field||row.length){row.push(field);rows.push(row);} const h=rows.shift(); return rows.filter(r=>r.some(Boolean)).map(r=>Object.fromEntries(h.map((x,i)=>[x,r[i]??""])));
}
const read = async rel => parseCsv(await fs.readFile(path.join(root, rel), "utf8"));
const taskCounts = await read("outputs/public_landscape/public_title_screened_task_counts.csv");
const domainCounts = await read("outputs/public_landscape/public_title_screened_domain_counts.csv");
const records = await read("outputs/public_landscape/public_title_screened_records.csv");
const maturity = await read("data/presentation/public_evidence_maturity_matrix.csv");
const evidence = await read("data/presentation/verified_public_primary_evidence_2026-08-13.csv");

const wb=Workbook.create(); const purple="#5B1A6E", purple2="#7A3E8E", pale="#F4EDF7", green="#2E7D65", grid="#DDD5E1", ink="#2B1532"; const font="Microsoft YaHei";
function title(s,last,text){const r=s.getRange(`A1:${last}1`);r.merge();r.values=[[text]];r.format={fill:purple,font:{name:font,size:16,bold:true,color:"#FFFFFF"},verticalAlignment:"center"};r.format.rowHeight=34;}
function hdr(r){r.format={fill:purple2,font:{name:font,size:9,bold:true,color:"#FFFFFF"},wrapText:true,verticalAlignment:"center",horizontalAlignment:"center",borders:{preset:"all",style:"thin",color:grid}};r.format.rowHeight=38;}
function body(r){r.format={font:{name:font,size:9,color:ink},wrapText:true,verticalAlignment:"top",borders:{preset:"all",style:"thin",color:grid}};}
function sheet(name,heading,headers,values,widths){const s=wb.worksheets.add(name);s.showGridLines=false;const last=String.fromCharCode(64+headers.length);title(s,last,heading);s.getRange(`A3:${last}3`).values=[headers];hdr(s.getRange(`A3:${last}3`));if(values.length){const rr=s.getRange(`A4:${last}${values.length+3}`);rr.values=values;body(rr);rr.format.rowHeight=42;}widths.forEach((w,i)=>s.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}${values.length+4}`).format.columnWidth=w);s.freezePanes.freezeRows(3);return s;}

const readme=wb.worksheets.add("README"); readme.showGridLines=false; title(readme,"F","公开来源证据工作簿 | Public-available evidence workspace");
readme.getRange("A3:F3").merge();readme.getRange("A3").values=[["口径：公开索引冻结快照中的保守题名筛选候选；不是全球论文总数，也不是系统综述全文纳入数。成熟度取当前可公开核验的一手研究最高层级，并与论文数量、闭环完整度分别评价。"]];readme.getRange("A3:F3").format={fill:pale,font:{name:font,size:11,bold:true,color:purple},wrapText:true,verticalAlignment:"center"};readme.getRange("A3:F3").format.rowHeight=56;
readme.getRange("A6:F6").values=[["Sheet","Unit","Rows","Use","Do not infer","Updated"]];hdr(readme.getRange("A6:F6"));readme.getRange("A7:F11").values=[["Task_Counts","task",taskCounts.length,"P5/P9/P13 volume landscape","global coverage or maturity","2026-08-13"],["Domain_Counts","unique paper within domain",domainCounts.length,"domain totals","sum of task rows when multi-label","2026-08-13"],["Maturity","task",maturity.length,"independent evidence stage","autonomy or deployment","2026-08-13"],["Verified_Evidence","primary study",evidence.length,"slide-level claims","systematic prevalence","2026-08-13"],["Screened_Records","task-paper candidate",records.length,"audit trail and manual screening","included-study status","2026-08-13"]];body(readme.getRange("A7:F11"));readme.getRange("A7:F11").format.rowHeight=42;[22,24,12,34,34,16].forEach((w,i)=>readme.getRange(`${String.fromCharCode(65+i)}1:${String.fromCharCode(65+i)}13`).format.columnWidth=w);

sheet("Task_Counts","公开索引题名筛选候选与开放位置发现",["Code","Domain","Task","Candidates","OA/repository located","No location","Unresolved","Since 2021","Counting unit"],taskCounts.map(r=>[r.task_code,r.domain,r.task,+r.public_index_title_screened_candidates,+r.oa_or_repository_location_identified_automatically,+r.full_text_not_identified,+r.access_unresolved,+r.since_2021,r.counting_unit]),[10,28,34,13,17,13,13,13,45]);
sheet("Domain_Counts","领域内唯一论文候选（避免任务多标签重复）",["Domain","Unique candidates","Unique OA/repository located","Counting unit"],domainCounts.map(r=>[r.domain,+r.unique_public_index_candidates,+r.unique_with_oa_or_repository_location_identified_automatically,r.counting_unit]),[34,18,24,54]);
sheet("Maturity","论文量、证据成熟度与闭环状态分开评价",["Code","Domain","Task","Candidates","OA located","Maximum evidence","Level","Loop status","Evidence anchor","Interpretation"],maturity.map(r=>[r.task_code,r.domain,r.task,+r.public_index_title_screened_candidates,+r.oa_or_repository_location_identified_automatically,r.maximum_publicly_verifiable_evidence,+r.maturity_level,r.loop_status,r.representative_public_evidence,r.interpretation]),[9,27,34,12,12,26,10,34,40,54]);
sheet("Verified_Evidence","逐页可公开核验的一手证据",["Slide","Domain","Task","Study","Year","Design","Sample/setting","Verified result","Loop boundary","Public URL"],evidence.map(r=>[r.slide,r.domain,r.task,r.study,+r.year,r.study_design,r.sample_or_setting,r.key_publicly_verified_result,r.loop_boundary,r.public_url]),[10,24,24,48,10,25,30,54,45,52]);
sheet("Screened_Records","保守自动题名筛选候选：需继续人工全文纳入筛选",["Code","Domain","Task","Title","Year","DOI","Sources","Public full text","Best public URL","Screening level"],records.map(r=>[r.task_code,r.domain,r.task,r.title,+r.year||r.year,r.doi,r.sources,r.public_full_text_identified,r.best_public_url,r.screening_level]),[9,25,30,70,10,32,24,16,55,34]);

await fs.mkdir(outDir,{recursive:true}); const blob=await SpreadsheetFile.exportXlsx(wb); await blob.save(output);
for(const [sn,range] of [["README","A1:F12"],["Task_Counts",`A1:I${taskCounts.length+3}`],["Maturity",`A1:J${maturity.length+3}`],["Verified_Evidence","A1:J12"]]){const png=await wb.render({sheetName:sn,range,scale:1.2});await fs.writeFile(path.join(outDir,`preview-${sn}.png`),new Uint8Array(await png.arrayBuffer()));}
const errors=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:100},summary:"formula error scan"});console.log(errors.ndjson);console.log(output);
