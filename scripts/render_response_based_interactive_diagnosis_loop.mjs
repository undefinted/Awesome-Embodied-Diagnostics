import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const modulesRoot = process.env.RUNTIME_NODE_MODULES;
if (!modulesRoot) {
  throw new Error('RUNTIME_NODE_MODULES must point to the bundled Node.js package directory.');
}
const sharp = require(path.join(modulesRoot, 'sharp'));

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..');
const defaultOut = path.join(repoRoot, 'outputs', 'response_based_interactive_diagnosis_loop');
const outIndex = process.argv.indexOf('--out');
const outDir = outIndex >= 0 ? path.resolve(process.argv[outIndex + 1]) : defaultOut;
fs.mkdirSync(outDir, { recursive: true });

const W = 1920;
const H = 1080;
const C = {
  ink: '#24182B',
  muted: '#6F6874',
  purple: '#642078',
  purpleDark: '#481456',
  purplePale: '#F5EFF8',
  teal: '#2F8974',
  tealDark: '#216555',
  tealPale: '#EDF7F4',
  gold: '#B9781B',
  goldPale: '#FCF5E8',
  line: '#DCD7E0',
  lineDark: '#B9B1BE',
  white: '#FFFFFF',
  bg: '#FCFBFD'
};

const esc = (s) => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');

function textBlock(x, y, lines, opts = {}) {
  const {
    size = 24, weight = 400, fill = C.ink, anchor = 'start', lineHeight = 32,
    family = 'Arial, Helvetica, sans-serif', italic = false
  } = opts;
  const tspans = lines.map((line, i) =>
    `<tspan x="${x}" dy="${i === 0 ? 0 : lineHeight}">${esc(line)}</tspan>`
  ).join('');
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="${family}" font-size="${size}" font-weight="${weight}" font-style="${italic ? 'italic' : 'normal'}" fill="${fill}">${tspans}</text>`;
}

function roundedCard(x, y, w, h, title, body, accent, pale, opts = {}) {
  const titleSize = opts.titleSize ?? 24;
  const bodySize = opts.bodySize ?? 19;
  const titleLines = Array.isArray(title) ? title : [title];
  const headerHeight = 44 + (titleLines.length - 1) * 27;
  const bodyStart = y + 80 + (titleLines.length - 1) * 25;
  return `
    <g>
      <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="16" fill="${C.white}" stroke="${C.line}" stroke-width="2"/>
      <rect x="${x}" y="${y}" width="8" height="${h}" rx="4" fill="${accent}"/>
      <rect x="${x + 8}" y="${y}" width="${w - 8}" height="${headerHeight}" rx="14" fill="${pale}"/>
      ${textBlock(x + 24, y + 32, titleLines, { size: titleSize, weight: 700, fill: accent, lineHeight: 27 })}
      ${textBlock(x + 24, bodyStart, body, { size: bodySize, fill: C.ink, lineHeight: 29 })}
    </g>`;
}

function arrowLine(x1, y1, x2, y2, color = C.purple, width = 4) {
  return `<path d="M ${x1} ${y1} L ${x2} ${y2}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" marker-end="url(#arrow-${color === C.teal ? 'teal' : color === C.gold ? 'gold' : 'purple'})"/>`;
}

const connectors = `
  ${arrowLine(350, 283, 380, 283)}
  ${arrowLine(700, 283, 730, 283)}
  ${arrowLine(1080, 283, 1110, 283)}
  ${arrowLine(1450, 283, 1480, 283)}
  ${arrowLine(1660, 430, 1660, 535, C.purple)}
  ${arrowLine(1480, 635, 1450, 635, C.teal)}
  ${arrowLine(1110, 635, 1080, 635, C.teal)}
  ${arrowLine(730, 635, 660, 635, C.teal)}
  <path d="M 450 555 C 405 470, 470 405, 540 382" fill="none" stroke="${C.gold}" stroke-width="4" stroke-linecap="round" stroke-dasharray="10 9" marker-end="url(#arrow-gold)"/>
  <path d="M 450 715 C 380 785, 300 790, 300 825" fill="none" stroke="${C.gold}" stroke-width="4" stroke-linecap="round" marker-end="url(#arrow-gold)"/>
`;

const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    <marker id="arrow-purple" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="${C.purple}"/></marker>
    <marker id="arrow-teal" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="${C.teal}"/></marker>
    <marker id="arrow-gold" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="${C.gold}"/></marker>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="5" stdDeviation="8" flood-color="#2D1834" flood-opacity="0.10"/></filter>
  </defs>
  <rect width="${W}" height="${H}" fill="${C.bg}"/>
  <rect x="0" y="0" width="16" height="${H}" fill="${C.purple}"/>

  ${textBlock(72, 76, ['Response-based interactive diagnosis'], { size: 42, weight: 750, fill: C.ink })}
  ${textBlock(72, 118, ['Closed-loop acquisition of diagnostic evidence from controlled physical or physiological responses'], { size: 23, fill: C.muted })}
  <line x1="72" y1="145" x2="1848" y2="145" stroke="${C.line}" stroke-width="2"/>

  <rect x="72" y="166" width="325" height="34" rx="17" fill="${C.purplePale}"/>
  ${textBlock(234, 190, ['COGNITIVE ADAPTATION'], { size: 16, weight: 700, fill: C.purple, anchor: 'middle' })}
  <rect x="1480" y="166" width="368" height="34" rx="17" fill="${C.tealPale}"/>
  ${textBlock(1664, 190, ['EMBODIED INTERACTION'], { size: 16, weight: 700, fill: C.teal, anchor: 'middle' })}

  ${connectors}

  <g filter="url(#shadow)">
    ${roundedCard(80, 210, 270, 190, 'Clinical objective', ['Patient context', 'Prior tests & records', 'Decision requirements'], C.purple, C.purplePale, { titleSize: 22, bodySize: 18 })}
    ${roundedCard(380, 210, 320, 190, ['State estimation', '& working memory'], ['Latent tissue / functional state', 'Patient-specific baseline', 'Prior actions and responses'], C.purple, C.purplePale, { titleSize: 21, bodySize: 17 })}
    ${roundedCard(730, 210, 350, 190, ['Uncertainty- and', 'risk-aware policy'], ['Expected diagnostic value', 'Uncertainty reduction', 'Burden, risk & reversibility'], C.purple, C.purplePale, { titleSize: 21, bodySize: 17 })}
    ${roundedCard(1110, 210, 340, 190, ['Stimulus planning', '& embodied control'], ['Site and modality', 'Amplitude, duration & trajectory', 'Contact and device state'], C.purple, C.purplePale, { titleSize: 21, bodySize: 17 })}
    ${roundedCard(1480, 210, 360, 220, 'Controlled perturbation', ['Palpation / indentation', 'Mechanical or acoustic excitation', 'Imposed motion / loading', 'Electrical, magnetic or', 'physiological challenge'], C.purple, C.purplePale, { titleSize: 21, bodySize: 16 })}

    ${roundedCard(1480, 535, 360, 225, ['Patient • tissue', '• physiology'], ['The controlled action elicits', 'a measurable mechanical,', 'neurophysiological or functional', 'response as new evidence.'], C.teal, C.tealPale, { titleSize: 23, bodySize: 18 })}
    ${roundedCard(1110, 535, 340, 225, ['Multimodal response', 'sensing'], ['Force–displacement & tactile maps', 'Deformation, strain & waves', 'EMG / EEG / MEP / reflexes', 'Physiological dynamics'], C.teal, C.tealPale, { titleSize: 21, bodySize: 17 })}
    ${roundedCard(730, 535, 350, 225, ['Evidence fusion', '& state update'], ['Response feature extraction', 'Model-based or learned inference', 'Calibrated confidence update', 'Contradiction / failure detection'], C.teal, C.tealPale, { titleSize: 21, bodySize: 17 })}
  </g>

  <g filter="url(#shadow)">
    <path d="M 450 550 L 660 635 L 450 720 L 240 635 Z" fill="${C.goldPale}" stroke="${C.gold}" stroke-width="3"/>
    ${textBlock(450, 608, ['Is the evidence'], { size: 23, weight: 700, fill: C.ink, anchor: 'middle' })}
    ${textBlock(450, 640, ['sufficient, safe'], { size: 23, weight: 700, fill: C.ink, anchor: 'middle' })}
    ${textBlock(450, 672, ['and actionable?'], { size: 23, weight: 700, fill: C.ink, anchor: 'middle' })}
  </g>
  ${textBlock(414, 515, ['NO — adapt'], { size: 16, weight: 700, fill: C.gold, anchor: 'middle' })}
  ${textBlock(334, 776, ['YES'], { size: 16, weight: 700, fill: C.gold, anchor: 'middle' })}

  <g filter="url(#shadow)">
    <rect x="80" y="825" width="440" height="132" rx="18" fill="${C.white}" stroke="${C.gold}" stroke-width="3"/>
    <rect x="80" y="825" width="440" height="42" rx="16" fill="${C.goldPale}"/>
    ${textBlock(300, 854, ['DIAGNOSTIC OUTPUT'], { size: 17, weight: 750, fill: C.gold, anchor: 'middle' })}
    ${textBlock(300, 900, ['Response-derived diagnostic evidence'], { size: 22, weight: 700, fill: C.ink, anchor: 'middle' })}
    ${textBlock(300, 934, ['Report • confirm • escalate • defer'], { size: 18, fill: C.muted, anchor: 'middle' })}
  </g>

  <g>
    <rect x="560" y="825" width="1280" height="132" rx="18" fill="${C.white}" stroke="${C.lineDark}" stroke-width="2"/>
    <rect x="560" y="825" width="16" height="132" rx="8" fill="${C.ink}"/>
    ${textBlock(605, 866, ['SAFETY, OVERSIGHT AND GOVERNANCE'], { size: 19, weight: 750, fill: C.ink })}
    ${textBlock(605, 906, ['Human oversight  •  bounded operational domain  •  force / dose limits  •  real-time abort or confirmation'], { size: 19, fill: C.ink })}
    ${textBlock(605, 938, ['Device self-checks  •  failure-aware fallback  •  traceable observations, actions and model updates'], { size: 19, fill: C.ink })}
  </g>

  <line x1="72" y1="995" x2="1848" y2="995" stroke="${C.line}" stroke-width="2"/>
  ${textBlock(72, 1027, ['Boundary condition: stimulus delivery alone is not sufficient; the elicited response must update diagnostic inference and subsequent action selection.'], { size: 17, fill: C.muted, italic: true })}
  ${textBlock(1848, 1027, ['Conceptual framework'], { size: 16, weight: 700, fill: C.purple, anchor: 'end' })}
</svg>`;

const svgPath = path.join(outDir, 'response_based_interactive_diagnosis_closed_loop_en.svg');
const pngPath = path.join(outDir, 'response_based_interactive_diagnosis_closed_loop_en.png');
fs.writeFileSync(svgPath, svg, 'utf8');
await sharp(Buffer.from(svg)).png({ compressionLevel: 9 }).toFile(pngPath);

const metadata = {
  title: 'Response-based interactive diagnosis: closed-loop evidence acquisition',
  language: 'English',
  dimensions: { width: W, height: H },
  generated_by: path.relative(repoRoot, fileURLToPath(import.meta.url)).replaceAll('\\', '/'),
  outputs: [path.basename(svgPath), path.basename(pngPath)],
  conceptual_boundary: 'The elicited response must update diagnostic inference and subsequent action selection; stimulus delivery alone is insufficient.',
  categories_of_perturbation: [
    'palpation or indentation',
    'mechanical or acoustic excitation',
    'imposed motion or loading',
    'electrical or magnetic stimulation',
    'physiological challenge'
  ]
};
fs.writeFileSync(path.join(outDir, 'figure_metadata.json'), JSON.stringify(metadata, null, 2), 'utf8');
console.log(`Wrote ${svgPath}`);
console.log(`Wrote ${pngPath}`);
