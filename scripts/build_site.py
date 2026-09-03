"""Generate the static research-atlas homepage."""
from __future__ import annotations

import html
import json
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)


def load_candidates() -> list[dict]:
    path = ROOT / "data" / "inbox.jsonl"
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return sorted(records, key=lambda item: (item.get("relevance_score", 0), str(item.get("year") or "")), reverse=True)


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


items = load_candidates()
audited = []
audited_path = ROOT / "data" / "audited_candidates.csv"
if audited_path.exists():
    with audited_path.open(encoding="utf-8-sig", newline="") as handle:
        audited = list(csv.DictReader(handle))
    items = [{"title": item["title"], "url": item["url"], "source": item["source"], "year": item["reported_year"], "relevance_score": item["scope_status"], "query_focus": item["scope_reason"]} for item in audited if item.get("identifier_verified") == "True" and item.get("scope_status") in {"core_candidate", "adjacent"}]
query_data = yaml.safe_load((ROOT / "data" / "discovery_queries.yaml").read_text(encoding="utf-8")) or {}
queries = query_data.get("queries", [])
source_counts = Counter(item.get("source", "Unknown") for item in items)
latest_year = max((str(item.get("year")) for item in items if item.get("year")), default="--")
generated = datetime.now(timezone.utc)
audit_counts = Counter(item.get("scope_status", "") for item in audited)

query_cards = "".join(
    f'''<article class="domain-card">
      <span class="domain-index">{index:02d}</span>
      <div><h3>{esc(query.get("focus"))}</h3><p>{esc(query.get("id", "").replace("-", " ").title())}</p></div>
    </article>'''
    for index, query in enumerate(queries, 1)
)

rows = "".join(
    f'''<tr data-search="{esc((item.get('title', '') + ' ' + item.get('source', '') + ' ' + item.get('query_focus', '')).lower())}" data-source="{esc(item.get('source'))}">
      <td class="paper-cell"><a href="{esc(item.get('url'))}" target="_blank" rel="noreferrer">{esc(item.get('title', 'Untitled'))}</a><span>{esc(item.get('query_focus', 'Candidate for manual review'))}</span></td>
      <td><span class="source-tag">{esc(item.get('source', 'Unknown'))}</span></td>
      <td>{esc(item.get('year', '--'))}</td>
      <td><span class="score">{esc(item.get('relevance_score', 0))}</span></td>
    </tr>'''
    for item in items[:300]
)

source_options = "".join(f'<option value="{esc(source)}">{esc(source)} ({count})</option>' for source, count in sorted(source_counts.items()))
empty_message = "" if items else '''<div class="empty-state"><strong>The radar is warming up.</strong><p>The searchable table will appear after the first candidate pull request is merged. The taxonomy and retrieval coverage below are already live.</p></div>'''

page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A living evidence atlas for embodied intelligence in medical diagnostics.">
  <title>Awesome-Embodied-Diagnostics</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="#top" aria-label="Awesome Embodied Diagnostics home"><span class="brand-mark">ED</span><span>Awesome-Embodied-Diagnostics</span></a>
    <nav><a href="#landscape">Landscape</a><a href="#papers">Paper radar</a><a href="https://github.com/undefinted/Awesome-Embodied-Diagnostics">GitHub</a></nav>
  </header>

  <main id="top">
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Living evidence atlas</p>
        <h1>Awesome-Embodied-Diagnostics</h1>
        <p class="lede">From interpreting medical data to actively acquiring diagnostic evidence through physical interaction.</p>
        <div class="hero-actions"><a class="primary" href="#papers">Explore papers</a><a class="secondary" href="https://github.com/undefinted/Awesome-Embodied-Diagnostics/blob/main/docs/DAILY_PAPER_RADAR.md">How the radar works</a></div>
      </div>
      <div class="loop-visual" role="img" aria-label="Embodied diagnostic loop: observe, decide, act, acquire, evaluate, adapt">
        <div class="loop-title"><span>Embodied diagnostic loop</span><b>Closed-loop evidence acquisition</b></div>
        <div class="loop-track">
          <div class="loop-node"><i>01</i><strong>Observe</strong><span>patient or target</span></div><span class="arrow">&#8594;</span>
          <div class="loop-node"><i>02</i><strong>Decide</strong><span>next best action</span></div><span class="arrow">&#8594;</span>
          <div class="loop-node action"><i>03</i><strong>Act</strong><span>contact or navigate</span></div>
        </div>
        <div class="return-line"><span>feedback and adaptation</span></div>
        <div class="loop-track reverse">
          <div class="loop-node"><i>06</i><strong>Interpret</strong><span>diagnostic endpoint</span></div><span class="arrow">&#8592;</span>
          <div class="loop-node"><i>05</i><strong>Evaluate</strong><span>evidence quality</span></div><span class="arrow">&#8592;</span>
          <div class="loop-node evidence"><i>04</i><strong>Acquire</strong><span>new evidence</span></div>
        </div>
      </div>
    </section>

    <section class="metrics" aria-label="Atlas metrics">
      <div><strong>{len(items)}</strong><span>Verified scope candidates</span></div>
      <div><strong>{len(source_counts) or 4}</strong><span>Scholarly source families</span></div>
      <div><strong>{audit_counts.get("core_candidate", 0)}</strong><span>Core candidates</span></div>
    </section>

    <section id="landscape" class="section">
      <div class="section-heading"><div><p class="eyebrow">Clinical landscape</p><h2>Where embodiment creates diagnostic evidence</h2></div><p>Organized by examination and evidence-acquisition capability, rather than by whichever model family is fashionable this month.</p></div>
      <div class="domain-grid">{query_cards}</div>
    </section>

    <section class="principles">
      <div><p class="eyebrow light">Curation model</p><h2>High recall. Visible uncertainty. Human review.</h2></div>
      <ol><li><b>Discover</b><span>Daily queries across arXiv, OpenAlex, Crossref, and Europe PMC.</span></li><li><b>Audit</b><span>Every query records source counts, failures, and provenance.</span></li><li><b>Review</b><span>Candidates enter a pull request, never the curated collection directly.</span></li></ol>
    </section>

    <section id="papers" class="section papers-section">
      <div class="section-heading"><div><p class="eyebrow">Daily paper radar</p><h2>Latest discovery candidates</h2></div><p>These records are proposals for review, not endorsements or claims of clinical readiness.</p></div>
      <div class="toolbar"><label><span>Search title or topic</span><input id="search" type="search" placeholder="Try robotic ultrasound or biopsy"></label><label><span>Source</span><select id="source"><option value="">All sources</option>{source_options}</select></label><div class="result-count"><strong id="visible-count">{len(items[:300])}</strong><span>visible records</span></div></div>
      {empty_message}
      <div class="table-wrap" {'hidden' if not items else ''}><table><thead><tr><th>Paper and retrieval focus</th><th>Source</th><th>Year</th><th>Signal</th></tr></thead><tbody id="paper-body">{rows}</tbody></table></div>
    </section>
  </main>

  <footer><div><span class="brand-mark small">ED</span><b>Awesome-Embodied-Diagnostics</b></div><p>Generated {generated:%B %d, %Y at %H:%M UTC}. Open data, explicit boundaries, living review.</p><a href="https://github.com/undefinted/Awesome-Embodied-Diagnostics">View repository &#8599;</a></footer>
  <script src="app.js"></script>
</body>
</html>'''

css = r''':root{--ink:#172026;--muted:#617079;--paper:#f6f7f5;--white:#fff;--line:#d9dfdc;--navy:#17324a;--teal:#087f73;--red:#c8433b;--yellow:#e9b949}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:0}.topbar{height:68px;display:flex;align-items:center;justify-content:space-between;padding:0 clamp(20px,5vw,72px);background:rgba(246,247,245,.96);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}.brand{display:flex;align-items:center;gap:11px;color:var(--ink);font-weight:750;text-decoration:none}.brand-mark{width:34px;height:34px;display:grid;place-items:center;background:var(--red);color:white;font-size:12px;font-weight:800}.topbar nav{display:flex;gap:28px}.topbar nav a{color:#40515a;text-decoration:none;font-size:14px}.topbar nav a:hover{color:var(--teal)}main{overflow:hidden}.hero{min-height:620px;padding:72px clamp(20px,6vw,88px) 78px;display:grid;grid-template-columns:minmax(300px,.8fr) minmax(560px,1.35fr);align-items:center;gap:64px;background:var(--white);border-bottom:1px solid var(--line)}.eyebrow{text-transform:uppercase;font-size:12px;font-weight:800;letter-spacing:.13em;color:var(--teal);margin:0 0 15px}.hero h1{font-family:Georgia,serif;font-size:clamp(48px,6vw,84px);line-height:.96;overflow-wrap:anywhere;margin:0;max-width:760px;font-weight:500}.lede{font-size:20px;line-height:1.55;color:#4a5b64;max-width:650px;margin:27px 0 32px}.hero-actions{display:flex;gap:12px;flex-wrap:wrap}.hero-actions a{padding:13px 18px;text-decoration:none;font-weight:700;font-size:14px;border:1px solid var(--navy)}.primary{background:var(--navy);color:white}.secondary{color:var(--navy);background:white}.loop-visual{background:var(--navy);color:white;padding:28px;min-height:410px;box-shadow:14px 14px 0 #dce8e5}.loop-title{display:flex;justify-content:space-between;align-items:end;border-bottom:1px solid #ffffff35;padding-bottom:18px;margin-bottom:28px}.loop-title span{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#a9c5d7}.loop-title b{font-family:Georgia,serif;font-size:19px;font-weight:500}.loop-track{display:grid;grid-template-columns:1fr 28px 1fr 28px 1fr;align-items:center}.loop-node{min-height:108px;padding:16px;background:#234b65;border-top:3px solid var(--teal);display:flex;flex-direction:column}.loop-node.action{border-color:var(--red)}.loop-node.evidence{border-color:var(--yellow)}.loop-node i{font-style:normal;font-size:11px;color:#b9ceda;margin-bottom:auto}.loop-node strong{font-size:16px}.loop-node span{font-size:12px;color:#b9ceda;margin-top:5px}.arrow{text-align:center;color:#8eb1c3}.return-line{height:62px;margin:5px 10%;border-left:1px solid #66869a;border-right:1px solid #66869a;border-bottom:1px solid #66869a;display:grid;place-items:end center;color:#9fbdcc;font-size:11px;text-transform:uppercase;letter-spacing:.1em}.metrics{display:grid;grid-template-columns:repeat(4,1fr);background:#e9efec;border-bottom:1px solid var(--line);padding:0 clamp(20px,6vw,88px)}.metrics div{padding:27px 24px;border-right:1px solid #cad4cf}.metrics div:first-child{border-left:1px solid #cad4cf}.metrics strong{font-family:Georgia,serif;font-size:35px;font-weight:500;display:block;color:var(--navy)}.metrics span{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}.section{padding:86px clamp(20px,6vw,88px)}.section-heading{display:grid;grid-template-columns:1.3fr .7fr;gap:60px;align-items:end;margin-bottom:38px}.section-heading h2,.principles h2{font-family:Georgia,serif;font-size:clamp(34px,4vw,54px);font-weight:500;line-height:1.08;margin:0}.section-heading>p{color:var(--muted);line-height:1.65;margin:0;max-width:500px}.domain-grid{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line)}.domain-card{background:white;min-height:150px;padding:24px;display:flex;gap:22px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.domain-index{font-family:Georgia,serif;color:var(--red);font-size:16px}.domain-card h3{font-size:17px;line-height:1.35;margin:0 0 14px}.domain-card p{text-transform:uppercase;color:var(--muted);font-size:10px;letter-spacing:.1em;margin:0}.principles{padding:70px clamp(20px,6vw,88px);background:#1b514d;color:white;display:grid;grid-template-columns:.8fr 1.2fr;gap:80px}.eyebrow.light{color:#9fd4c8}.principles ol{padding:0;margin:0;list-style:none}.principles li{display:grid;grid-template-columns:120px 1fr;gap:20px;padding:18px 0;border-top:1px solid #ffffff33}.principles li:last-child{border-bottom:1px solid #ffffff33}.principles li b{color:#bde1d9}.principles li span{color:#dcebe7;line-height:1.5}.papers-section{background:white}.toolbar{display:grid;grid-template-columns:2fr 1fr 150px;gap:14px;padding:18px;background:#edf1ef;border:1px solid var(--line);margin-bottom:18px}.toolbar label{display:flex;flex-direction:column;gap:7px}.toolbar label span,.result-count span{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);font-weight:700}.toolbar input,.toolbar select{height:42px;border:1px solid #bfc9c4;background:white;padding:0 12px;font:inherit;color:var(--ink);border-radius:0}.result-count{border-left:1px solid #c7d0cc;padding-left:20px;display:flex;flex-direction:column;justify-content:center}.result-count strong{font-family:Georgia,serif;font-size:25px;color:var(--navy)}.table-wrap{overflow:auto;border:1px solid var(--line)}table{width:100%;border-collapse:collapse;min-width:780px}th{padding:12px 15px;background:var(--navy);color:white;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.09em}td{padding:15px;border-bottom:1px solid var(--line);vertical-align:top;font-size:13px}.paper-cell a{color:var(--ink);font-weight:700;text-decoration:none;line-height:1.35}.paper-cell a:hover{color:var(--teal)}.paper-cell span{display:block;color:var(--muted);font-size:11px;margin-top:6px}.source-tag{display:inline-block;padding:5px 7px;background:#e6efec;color:#23645e;font-size:10px;font-weight:800;text-transform:uppercase}.score{display:grid;place-items:center;width:27px;height:27px;background:#f5e5d5;color:#8b3d1c;font-weight:800}.empty-state{border:1px solid var(--line);border-left:4px solid var(--yellow);padding:24px;background:#fffdf6}.empty-state p{color:var(--muted);margin:7px 0 0}footer{padding:30px clamp(20px,6vw,88px);background:#111f29;color:#c8d3d9;display:grid;grid-template-columns:1fr 1fr auto;align-items:center;gap:30px;font-size:12px}footer div{display:flex;align-items:center;gap:10px;color:white}.brand-mark.small{width:28px;height:28px;font-size:10px}footer a{color:white;text-decoration:none}@media(max-width:950px){.hero{grid-template-columns:1fr;padding-top:50px}.loop-visual{min-height:auto}.domain-grid{grid-template-columns:repeat(2,1fr)}.principles,.section-heading{grid-template-columns:1fr;gap:30px}.metrics{grid-template-columns:repeat(2,1fr)}footer{grid-template-columns:1fr}}@media(max-width:620px){.topbar{height:60px}.brand span:last-child{display:none}.topbar nav{gap:16px}.topbar nav a:first-child{display:none}.hero{padding:42px 18px 55px;gap:42px}.hero h1{font-size:46px}.lede{font-size:17px}.loop-visual{padding:18px;box-shadow:8px 8px 0 #dce8e5}.loop-title{align-items:start;gap:12px;flex-direction:column}.loop-track{grid-template-columns:1fr}.loop-node{min-height:82px}.arrow{padding:4px;transform:rotate(90deg)}.reverse .arrow{transform:rotate(-90deg)}.return-line{height:36px}.metrics{padding:0}.metrics div{padding:20px 18px}.metrics strong{font-size:28px}.section{padding:62px 18px}.domain-grid{grid-template-columns:1fr}.principles{padding:58px 18px}.principles li{grid-template-columns:82px 1fr}.toolbar{grid-template-columns:1fr}.result-count{border-left:0;border-top:1px solid #c7d0cc;padding:12px 0 0}.section-heading h2,.principles h2{font-size:36px}footer{padding:28px 18px}}'''

js = r'''const search=document.querySelector('#search');const source=document.querySelector('#source');const rows=[...document.querySelectorAll('#paper-body tr')];const count=document.querySelector('#visible-count');function filter(){const q=(search?.value||'').trim().toLowerCase();const s=source?.value||'';let visible=0;rows.forEach(row=>{const show=(!q||row.dataset.search.includes(q))&&(!s||row.dataset.source===s);row.hidden=!show;if(show)visible++});if(count)count.textContent=visible}search?.addEventListener('input',filter);source?.addEventListener('change',filter);'''

(SITE / "index.html").write_text(page, encoding="utf-8")
(SITE / "styles.css").write_text(css, encoding="utf-8")
(SITE / "app.js").write_text(js, encoding="utf-8")
print(f"site generated: {len(items)} candidates, {len(queries)} directions")
