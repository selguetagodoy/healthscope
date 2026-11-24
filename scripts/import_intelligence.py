#!/usr/bin/env python3
"""Refresh public HealthScope datasets. No patient identifiers, contact fields or private social data."""
import csv, io, json, re, time, zipfile, tempfile, argparse, concurrent.futures
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from collections import Counter
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
NOW=datetime.now(timezone.utc).isoformat(timespec="seconds")
UA="HealthScopeChile/1.0 (public data catalogue)"
def get(url,max_bytes=25_000_000):
    for attempt in range(2):
        try:
            with urlopen(Request(url,headers={"User-Agent":UA}),timeout=60) as r:
                body=r.read(max_bytes+1)
            if len(body)>max_bytes:raise ValueError("Download exceeds size limit")
            return body
        except Exception:
            if attempt:raise
            time.sleep(2)
def jget(url):return json.loads(get(url))
def write(name,obj):
    p=DATA/(name+".json");tmp=p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    tmp.replace(p)
def fmt(v):
    if v is None:return ""
    if isinstance(v,datetime):return v.date().isoformat()
    return str(v).strip()
def clinical():
    endpoint="https://clinicaltrials.gov/api/v2/studies"
    params={"query.locn":"Chile","countTotal":"true","pageSize":500,"fields":"NCTId,BriefTitle,OverallStatus,StudyType,Phase,Condition,LeadSponsorName,InterventionName,StartDate,PrimaryCompletionDate,LastUpdatePostDate,LocationCountry,LocationCity,LocationFacility"}
    rows={};reported=None;token=None;pages=0;excluded=0
    while True:
        if token:params["pageToken"]=token
        d=jget(endpoint+"?"+urlencode(params));pages+=1
        if reported is None:reported=d.get("totalCount")
        for s in d["studies"]:
            p=s["protocolSection"];i=p.get("identificationModule",{});st=p.get("statusModule",{});des=p.get("designModule",{})
            loc=[x for x in p.get("contactsLocationsModule",{}).get("locations",[]) if x.get("country","").casefold()=="chile"]
            if not loc:excluded+=1;continue
            nct=i["nctId"]
            rows[nct]={"id":nct,"title":i.get("briefTitle",""),"status":st.get("overallStatus",""),"type":des.get("studyType",""),"phase":", ".join(des.get("phases",[])),"sponsor":p.get("sponsorCollaboratorsModule",{}).get("leadSponsor",{}).get("name",""),"conditions":"; ".join(p.get("conditionsModule",{}).get("conditions",[])),"interventions":"; ".join(x.get("name","") for x in p.get("armsInterventionsModule",{}).get("interventions",[])),"start":st.get("startDateStruct",{}).get("date",""),"completion":st.get("primaryCompletionDateStruct",{}).get("date",""),"updated":st.get("lastUpdatePostDateStruct",{}).get("date",""),"cities":"; ".join(sorted({x.get("city","") for x in loc if x.get("city")})),"sites_chile":len(loc),"url":"https://clinicaltrials.gov/study/"+nct}
        token=d.get("nextPageToken")
        if not token:break
        if pages>40:raise ValueError("Unexpected clinical page count")
        time.sleep(.3)
    if not rows:raise ValueError("Empty clinical dataset")
    write("clinical-trials",{"source":"ClinicalTrials.gov","source_url":"https://clinicaltrials.gov/search?locStr=Chile&country=Chile","scope":"Estudios registrados con al menos una localización cuyo país es Chile; incluye estudios observacionales e intervencionales, históricos y activos. No equivale a autorizaciones ISP.","checked_at":NOW,"reported_query_total":reported,"excluded_no_chile_location":excluded,"count":len(rows),"rows":list(rows.values())})
    print("CLINICAL",len(rows),"reported",reported,"excluded",excluded,flush=True)
def patent_file(task):
    kind,year,r=task;w=load_workbook(io.BytesIO(get(r["url"],10_000_000)),read_only=True,data_only=True)
    sheet=w.worksheets[0];it=sheet.values;head=[fmt(x) for x in next(it)]
    required={"ApplicationNumber","RegistrationNumber","Title","IPC","Status","FilingDate","RegistrationDate","ExpirationDate"}
    if not required.issubset(head):raise ValueError("Unknown INAPI schema "+r["name"])
    out=[];scanned=0
    for vals in it:
        x=dict(zip(head,vals));scanned+=1;ipc=fmt(x.get("IPC")).upper()
        # A61P therapeutic activity; A61K medicinal preparations except cosmetics, dental preparations, apparatus, inactive carriers alone.
        codes=re.findall(r"A61[KP]\s*\d+(?:/\d+)?",ipc)
        match=any(c.startswith("A61P") or (c.startswith("A61K") and not re.match(r"A61K\s*(?:6|8|9|47)(?:/|$)",c)) for c in codes)
        if not match or not x.get("ApplicationNumber"):continue
        applicant=fmt(x.get("Applicants"))
        # Public patent applicants can be individuals. Expose organizational applicants only.
        orgs=[part.strip() for part in applicant.split(".BR.") if re.search(r"\b(?:AG|LTD|LIMITED|INC|CORP|GMBH|S\.A\.|SPA|LLC|UNIVERSIDAD|UNIVERSITY|COMPANY|CO\.|FOUNDATION|PHARMA|LABORATORI|INSTITUTE|SAS|BV|PLC|KK)\b",part,re.I)]
        out.append({"application":fmt(x["ApplicationNumber"]),"registration":fmt(x.get("RegistrationNumber")),"title":fmt(x.get("Title")),"ipc":ipc,"status":fmt(x.get("Status")),"applicant":"; ".join(orgs),"filing":fmt(x.get("FilingDate")),"grant":fmt(x.get("RegistrationDate")),"expiration":fmt(x.get("ExpirationDate")),"country":fmt(x.get("Country")),"kind":kind,"year":year,"url":r["url"]})
    w.close()
    return out,{"kind":kind,"year":year,"source_url":r["url"],"source_rows":scanned,"matches":len(out)}
def patents():
    tasks=[]
    for kind,pkg in [("Solicitud","solicitudes-de-patentes"),("Registro","registros-de-patentes")]:
        resources=jget("https://datos.gob.cl/api/3/action/package_show?"+urlencode({"id":pkg}))["result"]["resources"]
        years={}
        for r in resources:
            m=re.search(r"(20\d\d)\.xlsx$",r.get("name",""),re.I)
            if not m or not r.get("url","").startswith("https://datos.gob.cl/"):continue
            y=int(m[1])
            if y not in years or (r.get("last_modified") or "")>(years[y].get("last_modified") or ""):years[y]=r
        tasks.extend((kind,y,r) for y,r in sorted(years.items()))
    out={};coverage=[];errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(patent_file,t):t for t in tasks}
        for future in concurrent.futures.as_completed(futures):
            kind,year,r=futures[future]
            try:
                rows,meta=future.result();coverage.append(meta)
                for x in rows:
                    key=x["kind"]+":"+x["application"]+":"+x["registration"]
                    x["id"]=key
                    out[key]=x
            except Exception as e:errors.append({"kind":kind,"year":year,"error":str(e)[:250]})
    if not out:raise ValueError("No INAPI records imported")
    write("patents",{"source":"INAPI · datos.gob.cl","source_url":"https://tramites.inapi.cl/OpenData/PatentOpenData","scope":"Selección IPC A61P y A61K medicinal (excluye A61K6/8/9/47 como único criterio). Solicitud y registro son hitos distintos, no familias únicas. Expiración informada no certifica vigencia ni libertad de operación.","checked_at":NOW,"files":sorted(coverage,key=lambda r:(r["kind"],r["year"])),"errors":errors,"count":len(out),"rows":sorted(out.values(),key=lambda x:(x["year"],x["id"]),reverse=True)})
    print("PATENTS",len(out),"files",len(coverage),"errors",len(errors),flush=True)
def oc_month(period):
    y,m=period.split("-");url=f"https://transparenciachc.blob.core.windows.net/oc-da/{y}-{int(m)}.zip"
    raw=get(url,180_000_000);z=zipfile.ZipFile(io.BytesIO(raw));members=[i for i in z.infolist() if i.filename.lower().endswith(".csv")]
    if len(members)!=1 or members[0].file_size>2_000_000_000:raise ValueError("Unexpected ChileCompra ZIP layout")
    rows=[];orders=set();buyers=Counter();states=Counter();total=0;seen=set()
    with z.open(members[0]) as binary:
        rd=csv.DictReader(io.TextIOWrapper(binary,encoding="cp1252",errors="replace",newline=""),delimiter=";")
        required={"Codigo","IDItem","codigoProductoONU","OrganismoPublico","NombreroductoGenerico","cantidad","precioNeto","monedaItem","totalLineaNeto","Estado"}
        if not required.issubset(set(rd.fieldnames or [])):raise ValueError("Unknown ChileCompra schema")
        for r in rd:
            code=(r.get("codigoProductoONU") or "").strip()
            if not re.fullmatch(r"51\d{6}",code):continue
            key=(r["Codigo"],r["IDItem"])
            if not all(key) or key in seen:continue
            seen.add(key);total+=1;orders.add(key[0]);buyers[r["OrganismoPublico"]]+=1;states[r["Estado"]]+=1
            supplier=r.get("NombreProveedor","")
            if not re.search(r"\b(?:SPA|LTDA|LIMITADA|S\.A\.|SOCIEDAD|EIRL|CORP|INC|GMBH|FUNDACION|LABORATORIO|UNIVERSIDAD)\b",supplier,re.I):supplier="Proveedor no publicado en esta vista"
            # Preserve raw currency and quantity; never treat order total as line total.
            rows.append({"id":key[0]+":"+key[1],"period":period,"order":key[0],"tender":r.get("CodigoLicitacion",""),"status":r["Estado"],"sent":r.get("FechaEnvio",""),"buyer":r["OrganismoPublico"],"supplier":supplier,"product":r["NombreroductoGenerico"],"description":(r.get("EspecificacionComprador") or "")[:220],"unspsc":code,"quantity":r["cantidad"],"unit":r.get("UnidadMedida",""),"currency":r["monedaItem"],"net_unit":r["precioNeto"],"net_line":r["totalLineaNeto"],"url":r.get("Link","") if (r.get("Link") or "").startswith("https://") else "https://www.mercadopublico.cl/"})
    if not total:raise ValueError("No segment 51 items found")
    return rows,{"period":period,"source_url":url,"lines":total,"orders":len(orders),"buyers":dict(buyers.most_common(12)),"states":dict(states)}
def procurement(months):
    history=[];detail=[];errors=[]
    # Store detailed latest successful month, plus full counts for all imported periods.
    for month in sorted(set(months),reverse=True):
        try:
            rows,meta=oc_month(month);history.append(meta)
            if not detail:detail=rows
            print("PROCUREMENT",month,meta["lines"],flush=True)
        except Exception as e:errors.append({"period":month,"error":str(e)[:250]});print("PROCUREMENT ERROR",month,str(e)[:200],flush=True)
    if not history:raise ValueError("No procurement period imported")
    # Split source detail to avoid excessively large page payload; publish complete month as CSV and compact records as JSON.
    fields=list(detail[0])
    p=DATA/"procurement-lines.csv"
    with p.open("w",encoding="utf-8-sig",newline="") as fp:
        w=csv.DictWriter(fp,fieldnames=fields);w.writeheader()
        for r in detail:w.writerow({k:("'"+v if isinstance(v,str) and v.startswith(("=","+","-","@","\t","\r")) else v) for k,v in r.items()})
    compact=detail[:10000]
    write("procurement",{"source":"Dirección ChileCompra · datos abiertos","source_url":"https://datos-abiertos.chilecompra.cl/descargas","scope":"Órdenes de compra, líneas UNSPSC segmento 51. Estados de origen, no todas son adjudicaciones ni gastos ejecutados. CSV contiene todas las líneas del mes más reciente importado; vista JSON limitada a 10.000. Montos y unidades crudos, no sumables sin normalización.","checked_at":NOW,"periods":history,"errors":errors,"detail_period":detail[0]["period"],"detail_total":len(detail),"count":len(compact),"rows":compact})
def main():
    p=argparse.ArgumentParser();p.add_argument("--months",nargs="+",default=["2026-10","2026-09","2026-08"]);p.add_argument("--only",choices=["all","clinical","patents","procurement"],default="all");a=p.parse_args()
    jobs={"clinical":clinical,"patents":patents,"procurement":lambda:procurement(a.months)}
    selected=jobs if a.only=="all" else {a.only:jobs[a.only]}
    errors={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        fs={pool.submit(fn):name for name,fn in selected.items()}
        for x in concurrent.futures.as_completed(fs):
            try:x.result()
            except Exception as e:errors[fs[x]]=str(e)[:350];print(fs[x],"ERROR",str(e)[:350],flush=True)
    write("bulk-status",{"checked_at":NOW,"errors":errors})
    return 0 if len(errors)<len(selected) else 1
if __name__=="__main__":raise SystemExit(main())
