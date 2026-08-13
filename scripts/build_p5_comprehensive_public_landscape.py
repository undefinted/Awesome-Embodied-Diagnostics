"""Build a high-recall public-index evidence map for P5.

Counting unit: one deduplicated scholarly work (DOI, then normalized title).
Public-visible: bibliographic record is discoverable in at least one queried
public index and passes task-specific title/abstract screening.
Public-available: a lawful full-text or complete preprint location is identified
from Europe PMC/arXiv/OpenAlex metadata. This is not a licence audit.

Projects/systems are deliberately not counted in the publication bars because
one project may produce multiple publications. They are maintained separately.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "outputs" / "p5_comprehensive_public_landscape_2026-08-13"
OUT = DEFAULT_OUT
RAW = OUT / "raw"
YEAR_FROM, YEAR_TO = 2000, 2026
UA = "awesome-embodied-diagnostics/0.2 (public evidence-map research)"

TASKS = [
  {"code":"A1","task":"机器人超声","queries":["robotic ultrasound", "autonomous ultrasound scanning", "robot-assisted sonography", "robotized ultrasound", "ultrasound scanning robot"],"body":r"robot|autonom|automated|servo|force control|visual servo|scan planning|trajectory|reinforcement learning|shared control","mod":r"ultrasound|sonograph","exclude":r"needle|biopsy|ablation|therapy|therapeutic|surgical training|review"},
  {"code":"A2","task":"机器人胃肠内镜巡检","queries":["robotic endoscopy autonomous navigation", "autonomous colonoscopy robot", "robotic flexible endoscope navigation", "endoscopic robot visual servo"],"body":r"robot|autonom|self.?propell|active navigation|visual servo|navigation control","mod":r"endoscop|colonoscop|gastroscop","exclude":r"capsule|bronchoscop|biopsy|surgery|surgical|review"},
  {"code":"A3","task":"磁控/主动胶囊内镜","queries":["magnetic capsule endoscopy", "active capsule endoscopy", "robotic capsule endoscopy", "self-propelled capsule endoscopy"],"body":r"magnet|active|robot|autonom|self.?propell|locomotion|navigation|steer","mod":r"capsule","exclude":r"review|survey"},
  {"code":"A4","task":"机器人支气管镜观察/导航","queries":["robotic bronchoscopy navigation", "autonomous bronchoscopy navigation", "bronchoscope robot visual navigation", "robotic bronchoscope localization"],"body":r"robot|autonom|navigation|localization|visual servo|path planning","mod":r"bronchoscop","exclude":r"biopsy|sampling|specimen|patholog|review"},
  {"code":"A5","task":"机器人OCT","queries":["robotic optical coherence tomography", "autonomous OCT scanning", "contactless robotic OCT", "robot-assisted OCT"],"body":r"robot|autonom|automated|contactless|tracking|alignment|scan","mod":r"optical coherence|\bOCT\b","exclude":r"review"},
  {"code":"A6","task":"机器人听诊","queries":["robotic auscultation", "autonomous auscultation robot", "robotic stethoscope", "automated auscultation robot"],"body":r"robot|autonom|automated|mobile manipulator","mod":r"auscultat|stethoscop","exclude":r"review"},
  {"code":"A7","task":"机器人眼底/裂隙灯成像","queries":["robotic fundus imaging", "autonomous fundus camera", "robotic slit lamp", "automated robotic ophthalmic examination", "robotic ophthalmoscopy"],"body":r"robot|autonom|automated|self.?align|tracking","mod":r"fundus|retina|ophthalmoscop|slit.?lamp|ophthalmic","exclude":r"surgery|surgical|injection|review|OCT"},
  {"code":"A8","task":"机器人耳镜检查","queries":["robotic otoscopy", "autonomous otoscope", "robotic ear examination", "automated otoscopic imaging"],"body":r"robot|autonom|automated|self.?align|navigation","mod":r"otoscop|ear examination|tympanic membrane imaging","exclude":r"surgery|review"},
  {"code":"A9","task":"机器人皮肤/创面表面扫描","queries":["robotic skin scanning diagnosis", "autonomous wound imaging robot", "robotic dermatology imaging", "robotic skin lesion scanning", "robotic wound assessment"],"body":r"robot|autonom|automated scan|mobile manipulator|active vision","mod":r"skin|dermat|wound|ulcer|cutaneous","exclude":r"debrid|surgery|therapy|treatment|rehabilitation|review"},
  {"code":"A10","task":"机器人光谱/光学扫描","queries":["robotic Raman tissue scanning diagnosis", "robotic hyperspectral medical imaging", "robotic multispectral tissue scanning", "robotic diffuse reflectance spectroscopy tissue", "robotic confocal endomicroscopy scanning", "robotic photoacoustic scanning diagnosis"],"body":r"robot|autonom|automated scan|active sensing|scan planning","mod":r"raman|hyperspectral|multispectral|diffuse reflectance|spectroscop|confocal|endomicroscop|photoacoustic","exclude":r"surgery|ablation|therapy|treatment|review"},
  {"code":"A11","task":"机器人喉镜/口腔检查","queries":["robotic laryngoscopy examination", "autonomous laryngoscope", "robotic oral examination imaging", "robotic oral cavity inspection"],"body":r"robot|autonom|automated|navigation|active vision","mod":r"laryngoscop|oral cavity|oral examination|pharyngoscop","exclude":r"surgery|intubat|therapy|treatment|review"},
]

def cache_path(url, suffix):
    return RAW / (hashlib.sha256(url.encode()).hexdigest() + suffix)

def get_json(url, retries=2):
    p=cache_path(url,".json")
    if p.exists():return json.loads(p.read_text(encoding="utf-8"))
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=20) as f:data=json.load(f)
            p.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8"); return data
        except Exception:
            if i==retries-1: raise
            time.sleep(2**i)

def get_text(url, retries=2):
    p=cache_path(url,".xml")
    if p.exists():return p.read_text(encoding="utf-8")
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=20) as f:data=f.read().decode("utf-8","replace")
            p.write_text(data,encoding="utf-8"); return data
        except Exception:
            if i==retries-1: raise
            time.sleep(2**i)

def norm_title(s): return re.sub(r"[^a-z0-9]+","",(s or "").casefold())
def clean_doi(s): return re.sub(r"^https?://(dx\.)?doi\.org/","",(s or "").strip().lower())
def inv_abs(inv):
    if not inv:return ""
    a=[]
    for w,pos in inv.items():
        for p in pos:a.append((p,w))
    return " ".join(w for _,w in sorted(a))

def add(store, row):
    doi=clean_doi(row.get("doi","")); title=(row.get("title") or "").strip()
    if not title:return
    key="doi:"+doi if doi else "title:"+norm_title(title)
    if not norm_title(title):return
    if key not in store:store[key]={"paper_key":key,"doi":doi,"title":title,"year":row.get("year",""),"abstract":row.get("abstract","") or "","sources":set(),"record_urls":set(),"public_urls":set()}
    x=store[key]; x["sources"].add(row["source"])
    if row.get("record_url"):x["record_urls"].add(row["record_url"])
    if row.get("public_url"):x["public_urls"].add(row["public_url"])
    if len(row.get("abstract","") or "")>len(x["abstract"]):x["abstract"]=row["abstract"]
    if not x["year"] and row.get("year"):x["year"]=row["year"]

def openalex(q):
    url="https://api.openalex.org/works?"+urllib.parse.urlencode({"search":q,"filter":f"from_publication_date:{YEAR_FROM}-01-01,to_publication_date:{YEAR_TO}-12-31","per-page":200,"mailto":"research@example.org"})
    data=get_json(url); out=[]
    for w in data.get("results",[]):
        loc=w.get("best_oa_location") or {}; oa=w.get("open_access") or {}
        out.append({"source":"OpenAlex","title":w.get("title",""),"doi":w.get("doi","") or "","year":str(w.get("publication_year") or ""),"abstract":inv_abs(w.get("abstract_inverted_index")),"record_url":w.get("id",""),"public_url":(loc.get("pdf_url") or loc.get("landing_page_url") or "") if oa.get("is_oa") else ""})
    return out

def epmc(q):
    query=f'({q}) AND FIRST_PDATE:[{YEAR_FROM}-01-01 TO {YEAR_TO}-12-31]'
    url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode({"query":query,"format":"json","pageSize":1000,"resultType":"core"})
    data=get_json(url); out=[]
    for w in data.get("resultList",{}).get("result",[]):
        pmcid=w.get("pmcid",""); pub="https://pmc.ncbi.nlm.nih.gov/articles/"+pmcid+"/" if pmcid else ""
        out.append({"source":"Europe PMC","title":w.get("title",""),"doi":w.get("doi",""),"year":str(w.get("pubYear") or ""),"abstract":w.get("abstractText","") or "","record_url":"https://europepmc.org/article/"+(w.get("source","") or "MED")+"/"+(w.get("id","") or ""),"public_url":pub})
    return out

def crossref(q):
    url="https://api.crossref.org/works?"+urllib.parse.urlencode({"query.bibliographic":q,"filter":f"from-pub-date:{YEAR_FROM}-01-01,until-pub-date:{YEAR_TO}-12-31","rows":200,"select":"DOI,title,abstract,published,URL,license"})
    data=get_json(url); out=[]
    for w in data.get("message",{}).get("items",[]):
        dates=(w.get("published") or {}).get("date-parts") or [[]]; year=str(dates[0][0]) if dates and dates[0] else ""
        title=(w.get("title") or [""])[0]; lic=w.get("license") or []; pub=lic[0].get("URL","") if lic else ""
        out.append({"source":"Crossref","title":title,"doi":w.get("DOI",""),"year":year,"abstract":re.sub(r"<[^>]+>"," ",w.get("abstract","") or ""),"record_url":w.get("URL",""),"public_url":""})
    return out

def arxiv(q):
    url="https://export.arxiv.org/api/query?"+urllib.parse.urlencode({"search_query":"all:"+' AND all:'.join('"'+x+'"' for x in q.split()),"start":0,"max_results":100})
    root=ET.fromstring(get_text(url)); ns={"a":"http://www.w3.org/2005/Atom"}; out=[]
    for e in root.findall("a:entry",ns):
        title=" ".join((e.findtext("a:title",default="",namespaces=ns)).split()); ident=e.findtext("a:id",default="",namespaces=ns); year=(e.findtext("a:published",default="",namespaces=ns) or "")[:4]
        doi=e.findtext("{http://arxiv.org/schemas/atom}doi",default="")
        out.append({"source":"arXiv","title":title,"doi":doi,"year":year,"abstract":" ".join((e.findtext("a:summary",default="",namespaces=ns)).split()),"record_url":ident,"public_url":ident.replace("/abs/","/pdf/")})
    return out

def relevant(x,t):
    text=(x["title"]+" "+x["abstract"]).lower()
    return bool(re.search(t["body"],text,re.I) and re.search(t["mod"],text,re.I) and not re.search(t["exclude"],text,re.I))

def main():
    global OUT, RAW
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=DEFAULT_OUT,help="Directory for raw cache, query log, candidate records and counts")
    args=parser.parse_args()
    OUT=args.output_dir.resolve(); RAW=OUT/"raw"
    RAW.mkdir(parents=True,exist_ok=True); store={}; log=[]
    jobs=[]
    for t in TASKS:
      for q in t["queries"]:
        for name,fn in [("OpenAlex",openalex),("Europe PMC",epmc),("Crossref",crossref),("arXiv",arxiv)]: jobs.append((t,q,name,fn))
    def run(job):
      t,q,name,fn=job
      try:return t,q,name,fn(q),"ok"
      except Exception as e:return t,q,name,[],f"error:{type(e).__name__}:{e}"
    with ThreadPoolExecutor(max_workers=8) as ex:
      futures=[ex.submit(run,j) for j in jobs]
      for fut in as_completed(futures):
        t,q,name,rows,status=fut.result()
        for row in rows:add(store,row)
        log.append({"task_code":t["code"],"task":t["task"],"source":name,"query":q,"retrieved":len(rows),"status":status,"date":"2026-08-13"})
    candidates=[]
    for x in store.values():
      for t in TASKS:
        if relevant(x,t):
          candidates.append({"task_code":t["code"],"task":t["task"],"paper_key":x["paper_key"],"title":x["title"],"year":x["year"],"doi":x["doi"],"sources":"; ".join(sorted(x["sources"])),"record_urls":"; ".join(sorted(x["record_urls"])),"public_available":"yes" if x["public_urls"] else "no_location_identified","public_urls":"; ".join(sorted(x["public_urls"])),"screening":"title_abstract_rule_candidate"})
    # Within-task title dedup after DOI merge.
    keep=[]; seen=set()
    for x in sorted(candidates,key=lambda r:(r["task_code"],norm_title(r["title"]))):
      k=(x["task_code"],norm_title(x["title"]))
      if k not in seen:seen.add(k);keep.append(x)
    counts=[]
    for t in TASKS:
      rows=[x for x in keep if x["task_code"]==t["code"]]
      counts.append({"task_code":t["code"],"task":t["task"],"public_visible_title_abstract_candidates":len(rows),"public_available_fulltext_location_identified":sum(x["public_available"]=="yes" for x in rows),"since_2021":sum(str(x["year"]).isdigit() and int(x["year"])>=2021 for x in rows),"screening_status":"high-recall automated title/abstract candidate; human screening required"})
    OUT.mkdir(parents=True,exist_ok=True)
    for name,rows in [("query_log.csv",log),("p5_public_visible_available_records.csv",keep),("p5_public_visible_available_counts.csv",counts)]:
      with open(OUT/name,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (OUT/"METHODS.md").write_text(__doc__+"\n\nAutomated high-recall title/abstract candidates require human screening before presentation as included studies.\n",encoding="utf-8")
    print(json.dumps({"deduplicated_retrieved":len(store),"task_candidates":len(keep),"counts":counts,"query_errors":[x for x in log if x['status']!='ok']},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
