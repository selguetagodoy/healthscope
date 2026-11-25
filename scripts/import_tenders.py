#!/usr/bin/env python3
"""Import public tender index; metadata and links are sourced, not inferred as awards."""
import argparse, json, re, html
from datetime import datetime, date
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.gestorpublico.cl/licitaciones-organismo/"
NATIONAL="https://www.gestorpublico.cl/licitaciones-de/salud-e-insumos-medicos"
NATIONAL_API="https://www.gestorpublico.cl/api/rubro?slug=salud-e-insumos-medicos&desde="
SOURCES={"cenabast":"Cenabast","hospital-sotero-del-rio":"Hospital Sótero del Río","hospital-guillermo-grant-benavente":"Hospital Guillermo Grant Benavente"}
MONTHS={x:i+1 for i,x in enumerate("ene feb mar abr may jun jul ago sep oct nov dic".split())}
def clean(s):return html.unescape(re.sub(r"<[^>]+>","",s)).strip()
def extract(doc,slug,buyer,snapshot_override=None):
    today=datetime.now(ZoneInfo("America/Santiago")).date()
    m=re.search(r'"dateModified":"(\d{4}-\d\d-\d\d)"',doc)
    snapshot=snapshot_override or (date.fromisoformat(m[1]) if m else today)
    out=[]
    for match in re.finditer(r'<li\b[^>]*data-codigo="([^"]+)"[^>]*>.*?</li>',doc,re.S):
        raw=match[0];code=match[1]
        if not re.fullmatch(r"\d+-\d+-[A-Z0-9]+",code):continue
        def get(pattern):
            v=re.search(pattern,raw,re.S|re.I)
            return clean(v[1]) if v else ""
        name=get(r"<h3>(.*?)</h3>")
        amt=get(r"<span>Monto estimado</span>\s*<b[^>]*>(.*?)</b>")
        close=get(r"<span>Cierre de ofertas</span>\s*<b[^>]*>(.*?)</b>")
        category=get(r'<div class="ancha"><span>.*?</span><b>(.*?)</b>')
        rubros=get(r'data-rubros="([^"]*)"')
        url=get(r'href="(https://www\.mercadopublico\.cl/fichaLicitacion\.html\?idLicitacion=[^"]+)"')
        dm=re.search(r"(\d{1,2})\s+(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\b",close,re.I)
        iso=""
        if dm:
            month=MONTHS[dm[2].lower()];year=snapshot.year+(month<snapshot.month)
            try:iso=date(year,month,int(dm[1])).isoformat()
            except ValueError:pass
        if not name or not url:continue
        if slug not in ("cenabast","national") and "salud-e-insumos-medicos" not in rubros:continue
        actual_buyer=get(r'<p class="bl-meta pv-org"><span>(.*?)</span>') if slug=="national" else buyer
        if not actual_buyer:continue
        if "central de abastecimiento del sistema nacional" in actual_buyer.lower():actual_buyer="Cenabast"
        amount=int(re.sub(r"\D","",amt)) if re.fullmatch(r"\$\s*[\d.]+",amt) else None
        out.append({"code":code,"name":name,"buyer":actual_buyer,"amount":amount,"close":iso,"close_text":close,"category":category,"url":url,"source":NATIONAL if slug=="national" else BASE+slug,"snapshot":snapshot.isoformat()})
    if not out:raise ValueError("No valid records: "+slug)
    return out
def fetch():
    rows={};errors=[]
    for slug,buyer in SOURCES.items():
        try:
            with urlopen(Request(BASE+slug,headers={"User-Agent":"HealthScopeChile/1.2 public procurement monitor"}),timeout=25) as resp:doc=resp.read().decode("utf-8")
            for row in extract(doc,slug,buyer):rows[row["code"]]=row
        except Exception as e:errors.append(slug+": "+str(e))
    try:
        import time
        def geturl(url):
            with urlopen(Request(url,headers={"User-Agent":"HealthScopeChile/1.2 public procurement monitor"}),timeout=30) as resp:return resp.read().decode("utf-8")
        doc=geturl(NATIONAL)
        dm=re.search(r'"dateModified":"(\d{4}-\d\d-\d\d)"',doc)
        snapshot=date.fromisoformat(dm[1]) if dm else datetime.now(ZoneInfo("America/Santiago")).date()
        tm=re.search(r'data-total="(\d+)"',doc)
        total=int(tm[1]) if tm else 0
        national={r["code"]:r for r in extract(doc,"national","",snapshot)}
        offset=len(re.findall(r'data-codigo="',doc))
        while total and offset<total and offset<5000:
            part=json.loads(geturl(NATIONAL_API+str(offset))).get("html","")
            count=len(re.findall(r'data-codigo="',part))
            if not count:break
            for row in extract(part,"national","",snapshot):national[row["code"]]=row
            offset+=count
            time.sleep(.3)
        if total and offset<total:raise ValueError("National index incomplete: "+str(offset)+"/"+str(total))
        for code,row in national.items():rows.setdefault(code,row)
    except Exception as e:errors.append("national: "+str(e))
    if len([r for r in rows.values() if r["buyer"]=="Cenabast"])<1:raise RuntimeError("Cenabast import unavailable: "+str(errors))
    if errors and (ROOT/"data/tenders.json").exists():
        previous=json.loads((ROOT/"data/tenders.json").read_text(encoding="utf-8"))
        if len(previous.get("rows",[]))>len(rows):raise RuntimeError("Partial import; previous snapshot retained: "+str(errors))
    return {"checked_at":datetime.now(ZoneInfo("America/Santiago")).isoformat(timespec="seconds"),"source":"Gestor Público · índice de datos de ChileCompra","scope":"Procesos abiertos de Cenabast y del rubro salud e insumos médicos indexados por Gestor Público; no equivale a todas las licitaciones nacionales ni acredita adjudicaciones.","errors":errors,"rows":sorted(rows.values(),key=lambda r:(r["close"] or "9999",r["code"]))}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--stdout",action="store_true");a=p.parse_args()
    data=fetch()
    if a.stdout:print(json.dumps(data,ensure_ascii=True,separators=(",",":")))
    else:
        path=ROOT/"data/tenders.json";tmp=path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");tmp.replace(path)
        print("Tender rows:",len(data["rows"]))
