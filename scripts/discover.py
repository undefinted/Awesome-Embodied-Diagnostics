"""Daily public-source candidate discovery; it never modifies reviewed papers."""
from __future__ import annotations
import argparse, hashlib, json, re, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import feedparser, requests, yaml

ROOT=Path(__file__).resolve().parents[1]
MEDICAL=("medical","clinical","diagnos","patient","healthcare","ultrasound","endoscop","biopsy","palpat","auscultat","phlebotomy")
ACTION=("robot","embodied","autonomous","active sensing","navigation","palpat","probe","contact","phlebotomy","vla")
def norm(s): return re.sub(r"\s+"," ",s or "").strip()
def key(x): return (x.get("doi") or hashlib.sha1(norm(x["title"]).lower().encode()).hexdigest()).lower()
def relevant(title,abstract=""):
    text=(title+" "+abstract).lower()
    return sum(x in text for x in MEDICAL)+sum(x in text for x in ACTION), any(x in text for x in ACTION)
def candidate(source,query,title,abstract,url,doi,year):
    score,action=relevant(title,abstract)
    return {"source":source,"query_id":query["id"],"query_focus":query["focus"],"title":norm(title),"abstract":norm(abstract),"url":url,"doi":doi or "","year":year,"relevance_score":score,"action_signal":action,"discovered_at":datetime.now(timezone.utc).isoformat()}
def arxiv(q,since):
    r=requests.get("https://export.arxiv.org/api/query",params={"search_query":q["arxiv"],"start":0,"max_results":100,"sortBy":"submittedDate","sortOrder":"descending"},timeout=40); r.raise_for_status(); out=[]
    for x in feedparser.parse(r.text).entries:
        date=datetime.fromisoformat(x.published.replace("Z","+00:00"))
        if date>=since: out.append(candidate("arXiv",q,x.title,x.summary,x.id,"",date.year))
    return out
def works(source,q,since):
    if source=="openalex":
        r=requests.get("https://api.openalex.org/works",params={"search":q["scholarly"],"filter":f"from_publication_date:{since.date()}","per-page":50},timeout=40); r.raise_for_status()
        return [candidate("OpenAlex",q,x.get("title",""),"",x.get("doi") or x.get("primary_location",{}).get("landing_page_url"),x.get("doi",""),x.get("publication_year")) for x in r.json().get("results",[])]
    r=requests.get("https://api.crossref.org/works",params={"query":q["scholarly"],"filter":f"from-pub-date:{since.date()}","rows":50},timeout=40); r.raise_for_status(); out=[]
    for x in r.json().get("message",{}).get("items",[]):
        parts=x.get("published",{}).get("date-parts",[[None]])[0]; out.append(candidate("Crossref",q," ".join(x.get("title",[])),"",x.get("URL"),x.get("DOI",""),parts[0] if parts else None))
    return out
def europepmc(q,since):
    r=requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",params={"query":q["scholarly"]+f" FIRST_PDATE:[{since.date()} TO 9999-12-31]","format":"json","pageSize":50,"resultType":"core"},timeout=40); r.raise_for_status(); out=[]
    for x in r.json().get("resultList",{}).get("result",[]): out.append(candidate("Europe PMC",q,x.get("title",""),x.get("abstractText","") or "",x.get("doi") and "https://doi.org/"+x["doi"] or x.get("fullTextUrlList",{}).get("fullTextUrl",[{}])[0].get("url","") if x.get("fullTextUrlList") else "",x.get("doi",""),x.get("pubYear")))
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--days",type=int,default=2); args=p.parse_args(); since=datetime.now(timezone.utc)-timedelta(days=args.days)
    queries=(yaml.safe_load((ROOT/"data/discovery_queries.yaml").read_text(encoding="utf-8")) or {})["queries"]; inbox=ROOT/"data/inbox.jsonl"; audit={"generated_at":datetime.now(timezone.utc).isoformat(),"since":since.isoformat(),"queries":[]}; found=[]
    for q in queries:
        row={"id":q["id"],"focus":q["focus"],"sources":{}}
        for name,fn in (("arxiv",lambda:arxiv(q,since)),("openalex",lambda:works("openalex",q,since)),("crossref",lambda:works("crossref",q,since)),("europepmc",lambda:europepmc(q,since))):
            try: records=fn(); found.extend(records); row["sources"][name]={"records":len(records)}
            except Exception as e: row["sources"][name]={"error":str(e)}
            time.sleep(1)
        audit["queries"].append(row)
    existing={}
    if inbox.exists():
        for line in inbox.read_text(encoding="utf-8").splitlines():
            try:
                x=json.loads(line)
                if x.get("action_signal") and x.get("relevance_score",0)>=2: existing[key(x)]=x
            except json.JSONDecodeError: pass
    kept=[x for x in found if x["action_signal"] and x["relevance_score"]>=2]
    for x in kept: existing.setdefault(key(x),x)
    inbox.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in existing.values())+("\n" if existing else ""),encoding="utf-8")
    audit["summary"]={"retrieved":len(found),"passed_filter":len(kept),"unique_inbox":len(existing)}; (ROOT/"data/search_audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
    print(f"retrieved={len(found)} kept={len(kept)} unique_inbox={len(existing)}")
if __name__=="__main__": main()
