/** Create editable SVG figures from the public-source evidence matrix. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataPath = path.join(root, "data", "presentation", "public_evidence_maturity_matrix.csv");
const out = path.join(root, "figures", "public_evidence");
fs.mkdirSync(out, { recursive: true });

function parseCsv(text) {
  const lines = text.replace(/^\uFEFF/, "").trim().split(/\r?\n/);
  const split = (s) => { const a=[]; let v="", q=false; for(let i=0;i<s.length;i++){const c=s[i]; if(c==='"'&&s[i+1]==='"'){v+='"';i++;} else if(c==='"')q=!q; else if(c===','&&!q){a.push(v);v="";} else v+=c;} a.push(v); return a; };
  const h=split(lines[0]); return lines.slice(1).map(l=>Object.fromEntries(split(l).map((v,i)=>[h[i],v])));
}
const rows = parseCsv(fs.readFileSync(dataPath, "utf8"));
const byCode = Object.fromEntries(rows.map(r=>[r.task_code,r]));
const esc = s => String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
const P={purple:"#5B1A6E",green:"#2E7D65",orange:"#D9782D",grid:"#E7E1EA",text:"#2B1532",muted:"#6D6170"};

function writeLandscape(codes, labels, filename, title) {
  const W=1600,H=820, left=360,right=110,top=125,bottom=120, plotW=W-left-right, rowH=(H-top-bottom)/codes.length;
  const vals=codes.map(c=>+byCode[c].public_index_title_screened_candidates), max=Math.max(...vals);
  let body=`<rect width="${W}" height="${H}" fill="white"/><text x="60" y="66" font-family="Microsoft YaHei,Arial" font-size="34" font-weight="700" fill="${P.text}">${esc(title)}</text>`;
  for(let t=0;t<=4;t++){const x=left+plotW*t/4; body+=`<line x1="${x}" y1="${top-20}" x2="${x}" y2="${H-bottom+10}" stroke="${P.grid}"/><text x="${x}" y="${H-bottom+45}" text-anchor="middle" font-family="Arial" font-size="19" fill="${P.muted}">${Math.round(max*t/4)}</text>`;}
  codes.forEach((c,i)=>{const r=byCode[c], y=top+i*rowH+rowH*.18, h=rowH*.52, total=+r.public_index_title_screened_candidates, oa=+r.oa_or_repository_location_identified_automatically, wt=plotW*total/max, wo=plotW*oa/max;
    body+=`<text x="${left-24}" y="${y+h*.72}" text-anchor="end" font-family="Microsoft YaHei,Arial" font-size="24" fill="${P.text}">${esc(labels[i])}</text><rect x="${left}" y="${y}" width="${wt}" height="${h}" rx="7" fill="${P.purple}"/><rect x="${left}" y="${y+h*.31}" width="${wo}" height="${h*.38}" rx="4" fill="${P.green}"/><text x="${left+wt+14}" y="${y+h*.72}" font-family="Arial" font-size="23" fill="${P.text}">${total}</text>${oa?`<text x="${left+wo-8}" y="${y+h*.59}" text-anchor="end" font-family="Arial" font-size="16" font-weight="700" fill="white">${oa}</text>`:""}`;
  });
  body+=`<rect x="970" y="${H-79}" width="24" height="17" rx="3" fill="${P.purple}"/><text x="1006" y="${H-64}" font-family="Microsoft YaHei,Arial" font-size="18" fill="${P.muted}">公开索引题名筛选候选</text><rect x="1260" y="${H-79}" width="24" height="17" rx="3" fill="${P.green}"/><text x="1296" y="${H-64}" font-family="Microsoft YaHei,Arial" font-size="18" fill="${P.muted}">自动识别 OA/知识库位置</text><text x="60" y="${H-28}" font-family="Microsoft YaHei,Arial" font-size="16" fill="${P.muted}">计数单位：去重论文；冻结公开索引快照（Europe PMC/OpenAlex/Crossref/arXiv），题名规则筛选。不是系统综述纳入数。</text>`;
  fs.writeFileSync(path.join(out,filename),`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${body}</svg>`);
}

function writeMaturity(codes,labels,filename,title){const W=1500,H=650,left=300,right=90,top=90,bottom=115,rowH=(H-top-bottom)/codes.length,plotW=W-left-right; let b=`<rect width="${W}" height="${H}" fill="white"/><text x="45" y="52" font-family="Microsoft YaHei,Arial" font-size="31" font-weight="700" fill="${P.text}">${esc(title)}</text>`; for(let i=0;i<=6;i++){const x=left+plotW*i/6; b+=`<line x1="${x}" y1="${top-12}" x2="${x}" y2="${H-bottom+15}" stroke="${P.grid}" stroke-dasharray="5 7"/><text x="${x}" y="${H-bottom+48}" text-anchor="middle" font-family="Microsoft YaHei,Arial" font-size="16" fill="${P.muted}">${["未定位","原型","幻模/体外","动物/离体","人体","多中心/对照","结局/部署"][i]}</text>`;} codes.forEach((c,i)=>{const l=+byCode[c].maturity_level,y=top+i*rowH+rowH/2,x=left+plotW*l/6,col=l<=3?P.orange:P.green;b+=`<text x="${left-20}" y="${y+7}" text-anchor="end" font-family="Microsoft YaHei,Arial" font-size="22" fill="${P.text}">${esc(labels[i])}</text><line x1="${left}" y1="${y}" x2="${x}" y2="${y}" stroke="${P.grid}" stroke-width="8" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="16" fill="${col}" stroke="white" stroke-width="3"/>`;}); b+=`<text x="45" y="${H-25}" font-family="Microsoft YaHei,Arial" font-size="16" fill="${P.muted}">成熟度取当前可公开核验的一手研究最高层级；不代表完整闭环自治，也不与论文数量等价。</text>`; fs.writeFileSync(path.join(out,filename),`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${b}</svg>`);}

writeLandscape(["A1","A3","A2","A4","A5","A6"],["机器人超声","磁控/主动胶囊","机器人内镜巡检","机器人支气管镜导航","机器人 OCT","机器人听诊"],"p5_active_public_landscape.svg","主动观察式检测｜公开来源研究版图");
writeLandscape(["R1","R2","R6","R3","R4","R5"],["机器人触诊","弹性/刚度测绘","闭环 TMS 响应映射","关节松弛度/激发","肌张力/痉挛评估","叩诊/反射检查"],"p9_response_public_landscape.svg","响应式交互诊断｜公开来源题名筛选候选");
writeLandscape(["S1","S4","S5","S2","S3"],["经皮/芯针活检","静脉穿刺/采血","拭子/标本采集","内镜/支气管镜活检","胶囊组织/体液采样"],"p13_sample_public_landscape.svg","采样式交互诊断｜公开来源题名筛选候选");
writeMaturity(["R1","R2","R6","R3","R4","R5"],["触诊","弹性测绘","TMS 映射","关节激发","痉挛评估","叩诊/反射"],"p9_response_maturity.svg","可公开核验的最高证据成熟度");
writeMaturity(["S1","S4","S5","S2","S3"],["经皮活检","采血","拭子","内镜活检","胶囊采样"],"p13_sample_maturity.svg","可公开核验的最高证据成熟度");
console.log(out);

