from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]; inbox=root/"data/inbox.jsonl"; items=[]
if inbox.exists():
  for line in inbox.read_text(encoding="utf-8").splitlines():
    try: items.append(json.loads(line))
    except json.JSONDecodeError: pass
today=datetime.now(timezone.utc).date().isoformat(); new=[x for x in items if x.get("discovered_at","").startswith(today)]
lines=["# Daily Discovery Digest","",f"Generated: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}","",f"New candidates: **{len(new)}**",""]
for source,count in sorted(Counter(x.get("source","Unknown") for x in new).items()): lines.append(f"- {source}: {count}")
lines += ["","## Candidates",""]
for x in sorted(new,key=lambda z:(z.get("relevance_score",0),str(z.get("year") or "")),reverse=True)[:80]: lines.append(f"- [{x['title']}]({x.get('url') or ''}) ({x.get('source')}, {x.get('year') or 'n.d.'})")
lines += ["","All entries require human triage before being added to the reviewed collection.",""]
(root/"data/daily-summary.md").write_text("\n".join(lines),encoding="utf-8")
