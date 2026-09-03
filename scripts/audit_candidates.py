"""Verify candidate identity and apply conservative embodied-diagnostics triage."""
from __future__ import annotations
import csv, json, re, time
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import unquote
import requests

ROOT=Path(__file__).resolve().parents[1]; TODAY=date(2026,9,3)
CORE_PATTERNS=[r"robotic ultrasound",r"autonomous ultrasound",r"ultrasound robot",r"robotic palpation",r"robotic auscultation",r"robotic (?:needle )?biopsy",r"autonomous biopsy",r"robotic phlebotomy",r"robotic endoscop",r"autonomous endoscop",r"endoscopic robotic system",r"active sensing.*(?:medical|clinical|diagnos)",r"(?:medical|clinical|diagnos).*active sensing"]
DIAGNOSTIC=("diagnos","screen","examin","imaging","ultrasound","endoscop","palpat","auscultat","biopsy","phlebotomy","sampling","lesion","evidence")
PHYSICAL=("robot","embodied","autonomous","probe","needle","navigation","palpat","contact force","scan trajectory","physical interaction")
SURGERY_ONLY=("radical cystectomy","partial nephrectomy","arthroplasty","robot-assisted surgery","robotic surgery","surgical outcomes","complications","training programme","meta-analysis")

def norm_doi(raw):
    value=(raw or "").strip().lower(); value=re.sub(r"^https?://(?:dx\.)?doi\.org/","",value)
    return unquote(value)
def verify(item):
    doi=norm_doi(item.get("doi"))
    if doi:
        try:
            r=requests.get("https://api.crossref.org/works/"+doi,timeout=25)
            if r.status_code==200:
                msg=r.json()["message"]; title=" ".join(msg.get("title",[])).strip()
                return True,"Crossref DOI",title
            return False,f"Crossref HTTP {r.status_code}",""
        except Exception as exc:return False,"Crossref error: "+str(exc),""
    url=item.get("url","")
    if "arxiv.org/" in url:
        try:
            r=requests.get(url.replace("http://","https://"),timeout=25)
            return r.status_code==200,f"arXiv HTTP {r.status_code}",item.get("title","")
        except Exception as exc:return False,"arXiv error: "+str(exc),""
    return False,"No DOI or supported primary identifier",""
def classify(item,verified):
    text=(item.get("title","")+" "+item.get("abstract","")).lower(); title=item.get("title","").lower()
    if not verified:return "unverified","Identifier could not be verified"
    if any(x in title for x in SURGERY_ONLY) and not any(re.search(p,title) for p in CORE_PATTERNS):return "exclude","Surgery or training without diagnostic evidence-acquisition loop"
    if any(re.search(p,title) for p in CORE_PATTERNS):return "core_candidate","Title explicitly names diagnostic embodiment"
    if any(x in text for x in DIAGNOSTIC) and any(x in text for x in PHYSICAL):return "adjacent","Potential enabling or borderline embodied diagnostic work"
    return "exclude","No simultaneous diagnostic intent and controllable physical acquisition"
def main():
    items=[json.loads(x) for x in (ROOT/"data/inbox.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    rows=[]; cache={}
    for item in items:
        doi=norm_doi(item.get("doi")); k=doi or item.get("url","")
        if k not in cache:cache[k]=verify(item); time.sleep(.15)
        ok,method,canonical=cache[k]; status,reason=classify(item,ok); year=item.get("year"); future=False
        try:future=int(year)>TODAY.year
        except (TypeError,ValueError):pass
        rows.append({"title":item.get("title",""),"canonical_title":canonical,"doi":doi,"url":item.get("url",""),"source":item.get("source",""),"query_id":item.get("query_id",""),"reported_year":year,"identifier_verified":ok,"verification_method":method,"scope_status":status,"scope_reason":reason,"future_year_flag":future})
    unique={}
    for row in rows:
        key=row["doi"] or re.sub(r"\W+","",(row["canonical_title"] or row["title"]).lower())
        prev=unique.get(key)
        if not prev or (row["identifier_verified"] and not prev["identifier_verified"]):unique[key]=row
    out=list(unique.values()); fields=list(out[0]) if out else []
    with (ROOT/"data/audited_candidates.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(out)
    counts=Counter(x["scope_status"] for x in out); verified=sum(x["identifier_verified"] for x in out); future=sum(x["future_year_flag"] for x in out)
    report=["# Candidate Evidence Audit","",f"Audit date: {TODAY.isoformat()}","","> These counts describe the current automated candidate inbox, not the complete literature and not clinically validated systems.","","## Reconciled counts","",f"- Raw candidate records: {len(items)}",f"- Unique candidate works: {len(out)}",f"- Identifier-verified works: {verified}",f"- Core candidates: {counts['core_candidate']}",f"- Adjacent/borderline: {counts['adjacent']}",f"- Excluded after scope screening: {counts['exclude']}",f"- Unverified identifiers: {counts['unverified']}",f"- Future-year metadata flags: {future}","","## Rules","","- DOI records are checked against Crossref; arXiv-only records are checked against the primary arXiv page.","- Core candidate status requires explicit title-level evidence of diagnostic embodiment.","- General robotic surgery, static diagnostic AI, reviews without an acquisition agent, and keyword collisions are excluded.","- Core candidate is a screening decision, not final inclusion; full-text loop verification remains required.","","See `data/audited_candidates.csv` for every decision and reason.",""]
    (ROOT/"docs/CANDIDATE_EVIDENCE_AUDIT.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps({"raw":len(items),"unique":len(out),"verified":verified,**counts},indent=2))
if __name__=="__main__":main()
