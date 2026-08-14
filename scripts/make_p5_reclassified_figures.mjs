/** Generate P5 SVG figures from the reclassified task and modality tables. */
import fs from "node:fs";
import path from "node:path";

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, arr) => {
  if (value.startsWith("--")) pairs.push([value.slice(2), arr[index + 1]]);
  return pairs;
}, []));
for (const required of ["counts", "matrix", "output-dir"]) {
  if (!args[required]) throw new Error(`Missing --${required}`);
}

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(field); field = ""; }
    else if (ch === '\n') { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += ch;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  const headers = rows.shift();
  return rows.filter(r => r.length > 1).map(r => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
}

const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&apos;"}[c]));
const counts = parseCsv(fs.readFileSync(args.counts, "utf8"));
const matrixRows = parseCsv(fs.readFileSync(args.matrix, "utf8"));
fs.mkdirSync(args["output-dir"], { recursive: true });

const C = { purple: "#5F1B73", purple2: "#7B3B8D", green: "#2C8068", text: "#25152B", muted: "#6D6470", grid: "#E8E1EA", pale: "#F5F1F7", gray: "#A69DA8", white: "#FFFFFF" };
const font = "Microsoft YaHei, Noto Sans CJK SC, Arial, sans-serif";

function mainFigure() {
  const W = 1920, H = 1080;
  const sorted = counts.filter(r => r.primary_task_code !== "T9").sort((a,b) => Number(b.public_visible_unique_title_candidates) - Number(a.public_visible_unique_title_candidates));
  const generic = counts.find(r => r.primary_task_code === "T9");
  const clinicalTotal = sorted.reduce((sum, r) => sum + Number(r.public_visible_unique_title_candidates), 0);
  const clinicalAvailable = sorted.reduce((sum, r) => sum + Number(r.public_available_location_identified), 0);
  const max = Math.max(...sorted.map(r => Number(r.public_visible_unique_title_candidates)));
  const left = 420, chartRight = 1300, top = 170, bottom = 185;
  const chartW = chartRight - left, rowH = (H - top - bottom) / sorted.length;
  const s = [`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`, `<rect width="${W}" height="${H}" fill="white"/>`];
  s.push(`<text x="60" y="66" font-family="${font}" font-size="38" font-weight="700" fill="${C.text}">主动观察式检测｜公开索引证据版图</text>`);
  s.push(`<text x="60" y="108" font-family="${font}" font-size="22" fill="${C.muted}">按题名可核验的临床检查程序统计；模态与载体作为独立属性</text>`);
  for (let i = 0; i <= 4; i++) {
    const x = left + chartW * i / 4, val = Math.round(max * i / 4);
    s.push(`<line x1="${x}" y1="${top-18}" x2="${x}" y2="${H-bottom+10}" stroke="${C.grid}" stroke-width="1"/>`);
    s.push(`<text x="${x}" y="${H-bottom+42}" text-anchor="middle" font-family="Arial" font-size="18" fill="${C.muted}">${val}</text>`);
  }
  sorted.forEach((r, i) => {
    const y = top + i * rowH + rowH * .15, h = rowH * .56;
    const v = Number(r.public_visible_unique_title_candidates), a = Number(r.public_available_location_identified);
    const wv = chartW * v / max, wa = chartW * a / max;
    s.push(`<text x="${left-24}" y="${y+h*.70}" text-anchor="end" font-family="${font}" font-size="21" fill="${C.text}">${esc(r.primary_task_cn)}</text>`);
    s.push(`<rect x="${left}" y="${y}" width="${wv}" height="${h}" rx="7" fill="${C.purple}"/>`);
    s.push(`<rect x="${left}" y="${y+h*.30}" width="${wa}" height="${h*.40}" rx="4" fill="${C.green}"/>`);
    s.push(`<text x="${left+wv+12}" y="${y+h*.70}" font-family="Arial" font-size="20" fill="${C.text}">${v}</text>`);
    if (a) s.push(`<text x="${left+Math.max(wa-7,12)}" y="${y+h*.60}" text-anchor="end" font-family="Arial" font-size="14" font-weight="700" fill="white">${a}</text>`);
  });
  const x0 = 1390;
  s.push(`<text x="${x0}" y="180" font-family="${font}" font-size="25" font-weight="700" fill="${C.text}">证据语料范围</text>`);
  const scope = [["题名可定位检查程序", sorted.length, C.text], ["任务已定位候选", clinicalTotal, C.purple], ["其中已定位公开全文", clinicalAvailable, C.green], ["任务未定/跨任务技术", Number(generic.public_visible_unique_title_candidates), C.gray]];
  scope.forEach((d,i) => {
    const y=235+i*82;
    s.push(`<text x="${x0}" y="${y}" font-family="${font}" font-size="19" fill="${C.muted}">${d[0]}</text><text x="1815" y="${y}" text-anchor="end" font-family="Arial" font-size="30" font-weight="700" fill="${d[2]}">${d[1]}</text>`);
    if(i<scope.length-1) s.push(`<line x1="${x0}" y1="${y+24}" x2="1815" y2="${y+24}" stroke="${C.grid}"/>`);
  });
  s.push(`<rect x="${x0}" y="580" width="425" height="1" fill="${C.grid}"/>`);
  s.push(`<text x="${x0}" y="628" font-family="${font}" font-size="22" font-weight="700" fill="${C.text}">范围说明</text>`);
  s.push(`<text x="${x0}" y="674" font-family="${font}" font-size="17" fill="${C.muted}">题名未明确临床检查程序者不强行归类，</text><text x="${x0}" y="704" font-family="${font}" font-size="17" fill="${C.muted}">单列为 T9 并保留在补充审计表。</text>`);
  s.push(`<rect x="1050" y="966" width="24" height="17" rx="3" fill="${C.purple}"/><text x="1086" y="981" font-family="${font}" font-size="17" fill="${C.muted}">公开索引题名候选</text>`);
  s.push(`<rect x="1415" y="966" width="24" height="17" rx="3" fill="${C.green}"/><text x="1451" y="981" font-family="${font}" font-size="17" fill="${C.muted}">已定位公开全文</text>`);
  s.push(`<text x="60" y="1025" font-family="${font}" font-size="15" fill="${C.muted}">公开索引冻结：2026-08-13；重分类：2026-08-14。按 DOI 与规范化题名去重。计数为题名级候选，不是系统综述全文纳入数；公开全文位置未经逐篇许可证审计。</text>`);
  s.push(`</svg>`);
  return s.join("");
}

const modalityGroups = [
  ["超声", ["ultrasound"]], ["OCT", ["OCT"]], ["内镜/腔道影像*", ["endoscopic_imaging_unspecified","capsule_endoscopic_imaging_unspecified","bronchoscopic_imaging_unspecified","cavity_visual_imaging_unspecified"]],
  ["共聚焦/内镜显微", ["confocal_endomicroscopy"]], ["光声", ["photoacoustic"]], ["Raman/DRS", ["Raman_DRS_spectroscopy"]],
  ["其他光学/RGB", ["white_light_RGB_video","other_optical","ophthalmic_imaging_unspecified","surface_imaging_unspecified"]], ["生理声音", ["acoustic_physiological_sound"]]
];

function matrixFigure() {
  const W=1920,H=1080,left=430,top=210,cellW=165,cellH=74;
  const ordered=["T1","T2","T3","T4","T5","T6","T7","T8","T9"];
  const lookup=new Map(matrixRows.map(r=>[`${r.primary_task_code}|${r.modality_tag}`,r]));
  const s=[`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="white"/>`];
  s.push(`<text x="60" y="68" font-family="${font}" font-size="38" font-weight="700" fill="${C.text}">主动观察式检测｜临床检查程序 × 传感模态</text>`);
  s.push(`<text x="60" y="110" font-family="${font}" font-size="22" fill="${C.muted}">模态是可多选标签；单元格为 public visible / public available，不能跨列求和</text>`);
  modalityGroups.forEach((g,j)=>{
    const x=left+j*cellW+cellW/2;
    const lines=g[0].split("/");
    s.push(`<text x="${x}" y="165" text-anchor="middle" font-family="${font}" font-size="17" font-weight="700" fill="${C.text}">${esc(lines[0])}</text>`);
    if(lines[1])s.push(`<text x="${x}" y="188" text-anchor="middle" font-family="${font}" font-size="16" font-weight="700" fill="${C.text}">${esc(lines[1])}</text>`);
  });
  ordered.forEach((code,i)=>{
    const task=counts.find(r=>r.primary_task_code===code); const y=top+i*cellH;
    s.push(`<text x="${left-25}" y="${y+45}" text-anchor="end" font-family="${font}" font-size="20" fill="${code==='T9'?C.muted:C.text}">${esc(task.primary_task_cn)}</text>`);
    modalityGroups.forEach((g,j)=>{
      let v=0,a=0;
      g[1].forEach(tag=>{const r=lookup.get(`${code}|${tag}`);if(r){v+=Number(r.public_visible_unique_title_candidates);a+=Number(r.public_available_location_identified);}});
      const x=left+j*cellW; const alpha=v?Math.min(.10+.55*Math.log10(v+1)/2.6, .65):0;
      s.push(`<rect x="${x+5}" y="${y+5}" width="${cellW-10}" height="${cellH-10}" rx="7" fill="${C.purple}" fill-opacity="${alpha.toFixed(3)}" stroke="${C.grid}"/>`);
      if(v) s.push(`<text x="${x+cellW/2}" y="${y+35}" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700" fill="${C.text}">${v}<tspan fill="${C.muted}" font-size="16"> / </tspan><tspan fill="${C.green}" font-size="18">${a}</tspan></text>`);
      else s.push(`<text x="${x+cellW/2}" y="${y+39}" text-anchor="middle" font-family="Arial" font-size="18" fill="#C9C2CB">–</text>`);
    });
  });
  s.push(`<text x="60" y="938" font-family="${font}" font-size="17" fill="${C.muted}">*“内镜/腔道影像”表示题名未进一步指明 OCT、共聚焦、光声等具体模态；它不是对所有内镜论文的成像方式推断。</text>`);
  s.push(`<text x="60" y="978" font-family="${font}" font-size="17" fill="${C.muted}">OCT、共聚焦、光声和光谱是跨任务模态；T9 保留题名无法确定检查程序的采集技术，不解释为临床应用量。</text>`);
  s.push(`<text x="60" y="1025" font-family="${font}" font-size="15" fill="${C.muted}">来源与范围同主图。模态来自题名显式术语；缺少明确模态时使用“unspecified”任务级标签。模态多标签计数不等于唯一论文总数。</text></svg>`);
  return s.join("");
}

fs.writeFileSync(path.join(args["output-dir"], "p5_reclassified_clinical_tasks.svg"), mainFigure(), "utf8");
fs.writeFileSync(path.join(args["output-dir"], "p5_task_modality_matrix.svg"), matrixFigure(), "utf8");
console.log(path.resolve(args["output-dir"]));
