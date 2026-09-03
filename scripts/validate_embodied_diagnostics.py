from pathlib import Path
import sys,yaml
items=yaml.safe_load((Path(__file__).resolve().parents[1]/"data/papers.yaml").read_text(encoding="utf-8")) or []
required={"title","year","modality","diagnostic_stages","autonomy_level","clinical_validation_level","diagnostic_endpoint"}; seen=set(); errors=[]
for i,x in enumerate(items):
  missing=required-set(x); key=(x.get("doi") or x.get("title","")).lower()
  if missing: errors.append(f"{i}: missing {sorted(missing)}")
  if key in seen: errors.append(f"{i}: duplicate {key}")
  seen.add(key)
if errors: print("\n".join(errors)); sys.exit(1)
print(f"validated {len(items)} reviewed records")
