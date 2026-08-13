"""Verify that current statistics and figures have declared provenance.

Run from any working directory:
    python verify_provenance.py
The script reads ../产物与代码映射.csv relative to its own location.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "provenance" / "ARTIFACT_CODE_MAP.csv"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

rows=list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig")))
errors=[]; report=[]
for r in rows:
    output=ROOT/r["output_path"]
    scripts=[ROOT/x.strip() for x in r["generator_code"].split(";") if x.strip()]
    inputs=[ROOT/x.strip() for x in r["input_paths"].split(";") if x.strip()]
    missing=[str(x.relative_to(ROOT)) for x in [output,*scripts,*inputs] if not x.exists()]
    if missing:errors.append({"artifact_id":r["artifact_id"],"missing":missing})
    if r["reproducibility_status"]=="reproducible" and not scripts:
        errors.append({"artifact_id":r["artifact_id"],"missing_generator":"reproducible item has no generator"})
    report.append({"artifact_id":r["artifact_id"],"output_exists":output.exists(),"sha256":sha256(output) if output.exists() else "","status":r["reproducibility_status"]})
print(json.dumps({"manifest_rows":len(rows),"errors":errors,"artifacts":report},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
