import json, html
from pathlib import Path
from datetime import datetime, timezone
root=Path(__file__).resolve().parents[1]; inbox=root/'data/inbox.jsonl'; papers=root/'data/papers.yaml'; site=root/'site'; site.mkdir(exist_ok=True)
items=[]
if inbox.exists():
  for line in inbox.read_text(encoding='utf-8').splitlines():
    try: items.append(json.loads(line))
    except json.JSONDecodeError: pass
items=sorted(items,key=lambda x:(x.get('relevance_score',0),x.get('year') or 0),reverse=True)
rows=''.join(f"<tr><td><a href='{html.escape(x.get('url') or '')}'>{html.escape(x.get('title','Untitled'))}</a></td><td>{html.escape(x.get('source',''))}</td><td>{x.get('year') or ''}</td><td>{x.get('relevance_score',0)}</td></tr>" for x in items[:200])
doc=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Awesome-Embodied-Diagnostics</title><style>body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;max-width:1120px;margin:0 auto;padding:32px;color:#202124;background:#f7f8fa}}header{{background:#102a43;color:white;padding:36px;border-radius:12px}}h1{{margin:0 0 8px}}.stats{{display:flex;gap:18px;margin:22px 0}}.stat{{background:white;border:1px solid #d9e2ec;padding:14px 18px;border-radius:8px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:10px;border-bottom:1px solid #e6e8eb;text-align:left}}th{{background:#eef2f6}}a{{color:#0b63ce;text-decoration:none}}small{{color:#52606d}}</style></head><body><header><h1>Awesome-Embodied-Diagnostics</h1><p>From analyzing medical data to actively acquiring diagnostic evidence.</p><small>Candidate radar; every record requires human review before promotion.</small></header><div class="stats"><div class="stat"><b>{len(items)}</b><br><small>candidates</small></div><div class="stat"><b>4</b><br><small>source families</small></div><div class="stat"><b>{datetime.now(timezone.utc):%Y-%m-%d}</b><br><small>last generated</small></div></div><h2>Latest Discovery Candidates</h2><table><thead><tr><th>Paper</th><th>Source</th><th>Year</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table><p><small>Sources: arXiv, OpenAlex, Crossref, Europe PMC. See the repository README and data/search_audit.json for scope and provenance.</small></p></body></html>'''
(site/'index.html').write_text(doc,encoding='utf-8')
