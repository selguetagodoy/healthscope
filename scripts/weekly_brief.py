#!/usr/bin/env python3
"""Build a transparent seven-day pharmaceutical intelligence brief."""
import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone, date
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
TZ=ZoneInfo("America/Santiago")
DO="https://www.diariooficial.interior.gob.cl/edicionelectronica/index.php"
SENATE="https://tramitacion.senado.cl/appsenado/index.php?ac=ultimos_vistos&mo=tramitacion"
CHAMBER="https://www.camara.cl/legislacion/proyectosdeley/leyes_promulgadas.aspx"
def read(name,default):
    path=ROOT/name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");tmp.replace(path)
def fold(v):
    return "".join(c for c in unicodedata.normalize("NFD",str(v or "").lower()) if not unicodedata.combining(c))
def safe(url):
    p=urlsplit(url or "")
    return p.scheme=="https" and bool(p.hostname)
def relevant(text):
    t=fold(text)
    return any(x in t for x in ("medicament","farmac","ricarte soto","trikafta","fibrosis quistica","enfermedades raras","enfermedades poco frecuentes","alto costo","hemofilia","angioedema","inmunoglobulina","oncolog","cancer","cenabast","anamed","farmacovigilancia","partida 16","presupuesto de salud","presupuesto sanitario","garantias explicitas","fonasa","isapre","bioequivalencia","instituto de salud publica","ley 20.850","ley 21.743","20.850","21.743","15047-11","15.047-11","17375-11","17.375-11")) or bool(re.search(r"\bges\b|\bisp\b|\bepof\b",t))
def classify(record):
    t=fold(" ".join(str(record.get(k,"")) for k in ("title","summary","medication","topics")))
    cat=record.get("category","")
    if cat=="legislacion" or record.get("source_type")=="Diario Oficial":return "Regulación y Congreso"
    if "presupuesto" in t or "partida 16" in t:return "Presupuesto y financiamiento"
    if cat=="compras" or "cenabast" in t:return "Compras y abastecimiento"
    if cat=="acceso" or any(x in t for x in ("ricarte","trikafta","fibrosis","enfermedades raras","enfermedades poco frecuentes","alto costo")) or re.search(r"\bges\b",t):return "Acceso y cobertura"
    if record.get("source_type") in ("LinkedIn","X","Comunicado institucional") or cat=="stakeholders":return "Stakeholders"
    if record.get("source_type")=="Prensa" or cat=="prensa":return "Prensa especializada"
    return "Medicamentos y seguridad"
def score(record):
    t=fold(" ".join(str(record.get(k,"")) for k in ("title","summary","medication","topics")))
    return sum(w for term,w in [("ricarte soto",8),("trikafta",9),("fibrosis quistica",7),("enfermedades raras",6),("enfermedades poco frecuentes",6),("alto costo",5),("presupuesto",4),("farmacovigilancia",4),("medicamento",3),("cenabast",3),("hemofilia",5),("angioedema",5)] if term in t)+(5 if re.search(r"\bges\b",t) else 0)+(2 if record.get("category")=="legislacion" else 0)
def fetch(url):
    from bs4 import BeautifulSoup
    with urlopen(Request(url,headers={"User-Agent":"HealthScopeChile/1.1 public-source-monitor"}),timeout=18) as r:
        data=r.read(3_000_001)
    if len(data)>3_000_000:raise ValueError("Source exceeds limit")
    return BeautifulSoup(data,"html.parser")
def capture(title,url,when,authority,source_type,category):
    return {"id":hashlib.sha256((url+when+title).encode()).hexdigest()[:22],"title":title,"url":url,"published":when,"date":when,"authority":authority,"source_type":source_type,"category":category,"status":"Pendiente de revisión","summary":""}
def do_rows(doc,when):
    result=[]
    for a in doc.select("a[href]"):
        u=urljoin(DO,a["href"])
        if not safe(u) or urlsplit(u).hostname!="www.diariooficial.interior.gob.cl" or not re.search(r"/publicaciones/"+when.replace("-","/")+r"/[^/]+/\d+/\d+\.pdf$",urlsplit(u).path):continue
        tr=a.find_parent("tr")
        if not tr:continue
        td=tr.find_all("td",recursive=False)
        title=" ".join(td[0].stripped_strings) if len(td)>1 else tr.get_text(" ",strip=True).replace(a.get_text(" ",strip=True),"").strip()
        if not title or not relevant(title):continue
        result.append(capture(title,u,when,"Diario Oficial","Diario Oficial","legislacion"))
    return result
def collect_do(today,prior):
    old={x["url"]:x for x in prior if x.get("published","")>=(today-timedelta(days=6)).isoformat()}
    # Backfill 7 days on first run; subsequently recheck today and yesterday for special editions.
    n=2 if prior else 7
    checked=[];errors=[]
    for i in range(n):
        day=today-timedelta(days=i);when=day.isoformat();u=DO+"?date="+day.strftime("%d-%m-%Y")
        try:
            doc=fetch(u);links=[]
            for a in doc.select("a[href]"):
                if "ver edici" in fold(a.get_text(" ",strip=True)):
                    v=urljoin(u,a["href"])
                    if safe(v) and urlsplit(v).hostname=="www.diariooficial.interior.gob.cl" and "edition=" in v:links.append(v)
            docs=[fetch(v) for v in dict.fromkeys(links)] if links else [doc]
            for d in docs:
                for x in do_rows(d,when):old[x["url"]]=x
            checked.append(when)
        except Exception as e:errors.append(when+": "+str(e)[:160])
    return list(old.values()),{"id":"diario-oficial-ediciones","name":"Diario Oficial · ediciones y extraordinarias","url":DO,"status":"ok" if not errors else "partial" if checked else "error","dates_checked":checked,"errors":errors,"items_seen":len(old)}
def legislative_rows(doc,authority,source_type,base,today):
    result=[]
    for tr in doc.select("tr"):
        cells=[" ".join(td.stripped_strings) for td in tr.find_all("td",recursive=False)]
        if len(cells)<4:continue
        text=" ".join(cells)
        if not relevant(text):continue
        date_text=cells[0] if authority.startswith("Senado") else cells[-2]
        m=re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})",date_text)
        if not m:continue
        try:day=date(int(m[3]),int(m[2]),int(m[1]))
        except ValueError:continue
        if not today-timedelta(days=6)<=day<=today:continue
        urls=[]
        for a in tr.select("a[href]"):
            u=urljoin(base,a["href"]);host=urlsplit(u).hostname or ""
            if safe(u) and (host.endswith(".senado.cl") or host.endswith(".camara.cl") or host.endswith(".bcn.cl")) and u!=base:urls.append(u)
        if not urls:continue
        title=cells[3] if authority.startswith("Senado") else " · ".join(cells[:4])
        if not title:continue
        r=capture(title[:450],urls[-1],day.isoformat(),authority,source_type,"legislacion")
        if authority.startswith("Senado") and len(cells)>4:r["summary"]=cells[4][:450]
        result.append(r)
    return result
def extra(now):
    today=now.date();prev=read("data/weekly-extra.json",{})
    do,status=collect_do(today,prev.get("diario",[]));statuses=[status];leg=[]
    for authority,url in [("Senado de Chile",SENATE),("Cámara de Diputadas y Diputados",CHAMBER)]:
        try:
            docs=legislative_rows(fetch(url),authority,"Actividad legislativa",url,today);leg.extend(docs)
            statuses.append({"id":authority,"name":authority,"url":url,"status":"ok","items_seen":len(docs),"errors":[]})
        except Exception as e:
            leg.extend(x for x in prev.get("legislative",[]) if x.get("authority")==authority and x.get("published","")>=(today-timedelta(days=6)).isoformat())
            statuses.append({"id":authority,"name":authority,"url":url,"status":"error","items_seen":0,"errors":[str(e)[:200]]})
    obj={"checked_at":now.isoformat(timespec="seconds"),"diario":do,"legislative":leg,"sources":statuses}
    write(DATA/"weekly-extra.json",obj)
    return obj
def make(now,extra_data=None):
    start=(now.date()-timedelta(days=6)).isoformat();end=now.date().isoformat()
    extra_data=extra_data if extra_data is not None else read("data/weekly-extra.json",{})
    monitor=read("data/monitoring.json",{});old=read("data/weekly-brief.json",{})
    seen=set();verified=[];candidates=[];undated=[]
    records=read("events.json",[])+read("data/pending.json",[])+extra_data.get("diario",[])+extra_data.get("legislative",[])+read("data/social-posts.json",[])
    previous=set(old.get("all_ids",[]))
    same_cut=bool(old) and old.get("last_monitor_at")==monitor.get("last_attempt_at") and old.get("extra_checked_at")==extra_data.get("checked_at")
    previous_new={r["id"] for r in old.get("verified",[])+old.get("candidates",[]) if r.get("new_since_previous")}
    for r in records:
        url=r.get("url","");title=r.get("title","");when=r.get("published") or r.get("date") or ""
        if not safe(url) or not title or not relevant(" ".join(str(r.get(k,"")) for k in ("title","summary","medication","topics"))) or url.rstrip("/") in seen:continue
        if not when:
            if r.get("source_type") in ("LinkedIn","X"):undated.append({"title":title,"url":url,"authority":r.get("authority",""),"source_type":r.get("source_type"),"captured_at":r.get("captured_at","")})
            continue
        if not start<=when<=end:continue
        seen.add(url.rstrip("/"))
        ok=r.get("status")=="Verificado"
        item={"id":r.get("id",url),"published":when,"title":title,"authority":r.get("authority",""),"source_type":r.get("source_type","Fuente oficial"),"url":url,"topic":classify(r),"score":score(r),"status":"Verificado" if ok else "Pendiente de revisión","summary":r.get("summary","") if ok else "","implications":r.get("implications","") if ok else "","new_since_previous":bool(old) and (r.get("id",url) not in previous or (same_cut and r.get("id",url) in previous_new))}
        (verified if ok else candidates).append(item)
    key=lambda x:(x["score"],x["published"],x["title"])
    verified.sort(key=key,reverse=True);candidates.sort(key=key,reverse=True)
    health_sources=[{"name":r.get("name",""),"url":r.get("monitor_url",""),"status":r.get("status",""),"items_seen":r.get("items_seen",0),"errors":[r["error"]] if r.get("error") else []} for r in monitor.get("sources",[])]
    health_sources.extend(extra_data.get("sources",[]))
    result={"window_start":start,"window_end":end,"generated_at":now.isoformat(timespec="seconds"),"last_monitor_at":monitor.get("last_attempt_at"),"extra_checked_at":extra_data.get("checked_at"),"schedule":"Cada 3 horas en jornada hábil; fin de semana, corte diario. Horario aproximado según UTC y estación.","verified":verified,"candidates":candidates,"undated_social":undated,"sources":health_sources,"all_ids":[r["id"] for r in verified+candidates]}
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--offline",action="store_true");a=p.parse_args();now=datetime.now(TZ)
    obj=make(now,None if a.offline else extra(now))
    write(DATA/"weekly-brief.json",obj)
    print("Weekly brief:",len(obj["verified"]),"verified,",len(obj["candidates"]),"review,",len(obj["undated_social"]),"undated social")
if __name__=="__main__":main()
