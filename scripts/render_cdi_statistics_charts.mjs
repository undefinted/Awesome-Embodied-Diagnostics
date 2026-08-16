#!/usr/bin/env node
/** Render bilingual, publication/PPT-ready CDI statistics charts from CSV outputs.
 *
 * No numbers are embedded in this file.  All labels and values are read from
 * task_counts.csv, mechanism_counts.csv and domain_summary.csv created by
 * build_clinical_detection_intervention_public_statistics_v2.py.
 */

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const modulesRoot = process.env.RUNTIME_NODE_MODULES;
if (!modulesRoot) throw new Error("RUNTIME_NODE_MODULES is required");
const sharp = require(path.join(modulesRoot, "sharp"));

const inputDir = path.resolve(process.argv[2] || "outputs/clinical_detection_intervention_statistics_v2");
const outputDir = path.resolve(process.argv[3] || path.join(inputDir, "figures"));
fs.mkdirSync(outputDir, { recursive: true });

const COLORS = { purple: "#5C1A74", green: "#2D876F", gold: "#B7791F", ink: "#21152A", muted: "#6F6874", grid: "#E8E3EA", bg: "#FFFFFF" };
const W = 1920, H = 1080;

const mechanismNames = {
  "1.1": { en: "Active observational sensing", cn: "主动观察式感知" },
  "1.2": { en: "Response-eliciting interactive diagnosis", cn: "诱发响应式交互诊断" },
  "1.3": { en: "Diagnostic sample acquisition", cn: "诊断性样本获取" },
};

function parseCsv(text) {
  const rows = []; let row = [], field = "", quoted = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ""; }
    else if (c === '\n') { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const header = rows.shift();
  return rows.filter(r => r.some(Boolean)).map(r => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ""])));
}

function readCsv(name) { return parseCsv(fs.readFileSync(path.join(inputDir, name), "utf8")); }
function esc(s) { return String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;"); }
function num(v) { return Number(v || 0); }
function niceMax(v) {
  if (v <= 5) return 5; const p = 10 ** Math.floor(Math.log10(v));
  return Math.ceil(v / p) * p;
}
function wrap(text, max = 36) {
  text = String(text ?? "");
  if (/[\u3400-\u9FFF]/u.test(text)) {
    const chars = [...text]; const lines = [];
    for (let i = 0; i < chars.length; i += max / 2) lines.push(chars.slice(i, i + max / 2).join(""));
    return lines;
  }
  const words = text.split(/\s+/), lines = []; let line = "";
  for (const word of words) {
    if ((line + " " + word).trim().length > max && line) { lines.push(line); line = word; }
    else line = (line + " " + word).trim();
  }
  if (line) lines.push(line); return lines;
}
function textBlock(x, y, text, size, color, anchor = "start", weight = 400, max = 44, lineGap = 1.15) {
  const lines = wrap(text, max);
  return `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" text-anchor="${anchor}" font-weight="${weight}" font-family="Arial,'Microsoft YaHei','Noto Sans CJK SC',sans-serif">${lines.map((l, i) => `<tspan x="${x}" dy="${i ? size * lineGap : 0}">${esc(l)}</tspan>`).join("")}</text>`;
}
function frame(title, subtitle) {
  const hasCjk = /[\u3400-\u9FFF]/u.test(title);
  const titleSize = hasCjk ? ([...title].length > 28 ? 38 : 44) : (title.length > 62 ? 34 : 44);
  return `<rect width="${W}" height="${H}" fill="${COLORS.bg}"/>${textBlock(72, 80, title, titleSize, COLORS.ink, "start", 700, 110)}${textBlock(72, 132, subtitle, 22, COLORS.muted, "start", 400, 110)}`;
}
function footer(lang, unit) {
  const s = lang === "cn"
    ? `公开数据库检索快照截至 2026-08-15；DOI 优先、规范化题名次优去重。计数单位：${unit}。结果为可复现题名/摘要筛选候选，并非双人全文筛选后的纳入文献。`
    : `Public-database search snapshot to 2026-08-15; DOI-first, normalized-title-second deduplication. Unit: ${unit}. Reproducible title/abstract-screened candidates, not dual-reviewer full-text inclusions.`;
  return textBlock(72, 1018, s, 16, COLORS.muted, "start", 400, 165);
}
function legend(lang, y = 980, includeRecent = false) {
  const labels = lang === "cn"
    ? ["题名筛选后候选文献", "其中：可公开获取全文", "其中：2021–2026 年发表"]
    : ["Title-screened candidate records", "Of these: publicly accessible full text", "Of these: published in 2021–2026"];
  const colors = [COLORS.purple, COLORS.green, COLORS.gold];
  const start = includeRecent ? 555 : 760, gap = includeRecent ? 430 : 430;
  return labels.slice(0, includeRecent ? 3 : 2).map((label, i) => `<rect x="${start + i * gap}" y="${y - 16}" width="24" height="17" rx="3" fill="${colors[i]}"/>${textBlock(start + 35 + i * gap, y, label, 17, COLORS.muted, "start", 400, 40)}`).join("");
}
function groupedBars(rows, lang, title, subtitle, unit, valueKeys, labelKey, includeRecent = false) {
  const left = 535, right = 1820, top = 205, bottom = 890;
  const plotW = right - left, plotH = bottom - top;
  const allValues = rows.flatMap(r => valueKeys.map(k => num(r[k])));
  const max = niceMax(Math.max(1, ...allValues));
  const rowH = plotH / rows.length, colors = [COLORS.purple, COLORS.green, COLORS.gold];
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${frame(title, subtitle)}`;
  for (let i = 0; i <= 5; i++) {
    const x = left + plotW * i / 5, v = Math.round(max * i / 5);
    svg += `<line x1="${x}" y1="${top - 10}" x2="${x}" y2="${bottom}" stroke="${COLORS.grid}" stroke-width="1"/>${textBlock(x, bottom + 32, v, 17, COLORS.muted, "middle", 400, 12)}`;
  }
  rows.forEach((r, idx) => {
    const cy = top + rowH * idx + rowH / 2;
    svg += textBlock(left - 25, cy - (wrap(r[labelKey], 34).length - 1) * 11, r[labelKey], 21, COLORS.ink, "end", 400, 34);
    const n = valueKeys.length, totalH = Math.min(58, rowH * 0.72), barH = totalH / n;
    valueKeys.forEach((key, j) => {
      const v = num(r[key]), width = plotW * v / max, y = cy - totalH / 2 + j * barH;
      svg += `<rect x="${left}" y="${y}" width="${Math.max(width, v ? 3 : 0)}" height="${barH - 3}" rx="5" fill="${colors[j]}"/>`;
      if (v || j < 2) svg += textBlock(left + width + 12, y + barH - 9, v, 18, COLORS.ink, "start", 600, 12);
    });
  });
  svg += legend(lang, 972, includeRecent) + footer(lang, unit) + `</svg>`;
  return svg;
}
function metricBars(rows, lang, title, subtitle, unit) {
  const left = 520, right = 1760, top = 260, bottom = 820;
  const plotW = right - left, rowH = (bottom - top) / rows.length;
  const max = niceMax(Math.max(1, ...rows.map(r => num(r.value))));
  const colors = [COLORS.purple, COLORS.green, COLORS.gold];
  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${frame(title, subtitle)}`;
  for (let i = 0; i <= 5; i++) {
    const x = left + plotW * i / 5;
    svg += `<line x1="${x}" y1="${top - 20}" x2="${x}" y2="${bottom}" stroke="${COLORS.grid}" stroke-width="1"/>${textBlock(x, bottom + 35, Math.round(max * i / 5), 18, COLORS.muted, "middle", 400, 12)}`;
  }
  rows.forEach((r, i) => {
    const y = top + rowH * i + rowH * 0.28, v = num(r.value), width = plotW * v / max;
    svg += textBlock(left - 25, y + 31, r.label, 24, COLORS.ink, "end", 400, 38);
    svg += `<rect x="${left}" y="${y}" width="${Math.max(width, v ? 3 : 0)}" height="58" rx="8" fill="${r.color || colors[i]}"/>`;
    svg += textBlock(left + width + 16, y + 39, v, 24, COLORS.ink, "start", 700, 12);
  });
  svg += footer(lang, unit) + `</svg>`;
  return svg;
}
async function save(base, svg) {
  const svgPath = path.join(outputDir, `${base}.svg`), pngPath = path.join(outputDir, `${base}.png`);
  fs.writeFileSync(svgPath, svg, "utf8");
  await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toFile(pngPath);
  return [svgPath, pngPath];
}

const tasks = readCsv("task_counts.csv");
const mechanisms = readCsv("mechanism_counts.csv").map(r => ({
  ...r,
  mechanism_en: mechanismNames[r.mechanism_code].en,
  mechanism_cn: mechanismNames[r.mechanism_code].cn,
})).sort((a, b) =>
  num(b.public_visible_unique_screened_works) - num(a.public_visible_unique_screened_works)
  || num(b.public_available_unique_works) - num(a.public_available_unique_works)
  || a.mechanism_code.localeCompare(b.mechanism_code)
);
const summary = readCsv("domain_summary.csv")[0];
const manifest = [];

for (const lang of ["cn", "en"]) {
  const isCn = lang === "cn";
  const domainTitle = isCn ? "临床检测与干预：三种证据获取机制" : "Clinical Detection and Intervention: three evidence-acquisition mechanisms";
  const domainSub = isCn
    ? `题名筛选后唯一候选文献 ${summary.public_visible_unique_screened_works}；其中 ${summary.public_available_unique_works} 篇可公开获取全文；跨任务重叠单列审计`
    : `${summary.public_visible_unique_screened_works} unique title-screened candidates; ${summary.public_available_unique_works} with publicly accessible full text; overlaps audited separately`;
  const domainSvg = groupedBars(mechanisms, lang, domainTitle, domainSub,
    isCn ? "机制内唯一研究" : "unique work within mechanism",
    ["public_visible_unique_screened_works", "public_available_unique_works"], `mechanism_${lang}`);
  manifest.push(...(await save(`CDI_overall_by_mechanism_${lang}`, domainSvg)));

  for (const mech of ["1.1", "1.2", "1.3"]) {
    const rows = tasks.filter(r => r.mechanism_code === mech).sort((a, b) =>
      num(b.public_visible_screened_candidates) - num(a.public_visible_screened_candidates)
      || num(b.public_available_location_identified) - num(a.public_available_location_identified)
      || num(b.since_2021) - num(a.since_2021)
      || a.task_code.localeCompare(b.task_code)
    );
    const enMechanismTitle = {
      "1.1": "Active observational sensing: candidate literature by task",
      "1.2": "Response-eliciting diagnosis: candidate literature by task",
      "1.3": "Diagnostic sample acquisition: candidate literature by task",
    };
    const title = isCn ? `${mechanismNames[mech].cn}：子任务候选文献分布` : enMechanismTitle[mech];
    const subtitle = isCn ? "互斥任务定义；允许同一研究的不同证据获取阶段形成多个任务—研究对" : "Mutually exclusive task definitions; distinct evidence-acquisition stages may form multiple task–study pairs";
    const svg = groupedBars(rows, lang, title, subtitle, isCn ? "任务—研究对" : "task–study pair",
      ["public_visible_screened_candidates", "public_available_location_identified", "since_2021"], `task_${lang}`, true);
    manifest.push(...(await save(`CDI_${mech.replace('.', '_')}_subtasks_${lang}`, svg)));
  }

  for (const r of tasks) {
    const code = r.task_code;
    const title = r[`task_${lang}`];
    const subtitle = isCn ? `${mechanismNames[r.mechanism_code].cn}中的独立证据获取任务` : `A distinct evidence-acquisition task within ${mechanismNames[r.mechanism_code].en}`;
    const metricRows = isCn ? [
      { label: "题名筛选后候选文献", value: r.public_visible_screened_candidates, color: COLORS.purple, rank: 0 },
      { label: "其中：可公开获取全文", value: r.public_available_location_identified, color: COLORS.green, rank: 1 },
      { label: "其中：2021–2026 年发表", value: r.since_2021, color: COLORS.gold, rank: 2 },
    ] : [
      { label: "Title-screened candidate records", value: r.public_visible_screened_candidates, color: COLORS.purple, rank: 0 },
      { label: "Of these: publicly accessible full text", value: r.public_available_location_identified, color: COLORS.green, rank: 1 },
      { label: "Of these: published in 2021–2026", value: r.since_2021, color: COLORS.gold, rank: 2 },
    ];
    metricRows.sort((a, b) => num(b.value) - num(a.value) || a.rank - b.rank);
    const svg = metricBars(metricRows, lang, title, subtitle, isCn ? "任务—研究对" : "task–study pair");
    manifest.push(...(await save(`CDI_${code}_${lang}`, svg)));
  }
}

fs.writeFileSync(path.join(outputDir, "chart_manifest.json"), JSON.stringify({ generated_at: new Date().toISOString(), input_dir: inputDir, files: manifest }, null, 2));
console.log(JSON.stringify({ outputDir, chartFiles: manifest.length, charts: manifest.length / 2 }, null, 2));
