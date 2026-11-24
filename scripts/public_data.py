"""Validate and prepare public projections with traceable original links."""
import csv,json,re
from collections import Counter
from pathlib import Path
from urllib.parse import quote
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
def order_url(code):
    if not re.fullmatch(r"\d+-\d+-[A-Z0-9]+",str(code or "")):return ""
    return "https://www.mercadopublico.cl/PurchaseOrder/Modules/PO/DetailsPurchaseOrder.aspx?codigoOC="+quote(code,safe="")
def prepare(dest):
    data=dest/"data";p=data/"procurement.json";d=read(p);detail=data/"procurement-lines.csv"
    if detail.exists():
        with detail.open(encoding="utf-8-sig",newline="") as fp:rows=list(csv.DictReader(fp))
        if len(rows)!=d["detail_total"] or len({r["id"] for r in rows})!=len(rows):raise ValueError("Procurement detail mismatch")
        for r in rows:
            r["url"]=order_url(r["order"]) or next(x["source_url"] for x in d["periods"] if x["period"]==r["period"])
        d["rows"]=rows;d["count"]=len(rows)
        d["scope"]="Detalle íntegro de "+d["detail_period"]+"; recuentos mensuales de periodos procesados. Órdenes de compra UNSPSC 51."
        with detail.open("w",encoding="utf-8-sig",newline="") as fp:
            wr=csv.DictWriter(fp,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
        write(p,d)
    pat=read(data/"patents.json");pat["unique_applications"]=len({r["application"] for r in pat["rows"]});pat["kind_counts"]=dict(Counter(r["kind"] for r in pat["rows"]))
    write(data/"patents.json",pat)
    trials=read(data/"clinical-trials.json");trials["type_counts"]=dict(Counter(r["type"] for r in trials["rows"]));write(data/"clinical-trials.json",trials)

def indexes(dest):
    data=dest/"data";idx=data/"search"
    def emit(name,rows,fn):write(idx/(name+".json"),[fn(r) for r in rows])
    emit("events",read(dest/"events.json"),lambda r:[r["title"],r.get("authority"),r.get("summary"),r.get("medication"),r.get("topics")])
    emit("coverage",read(data/"coverage.json"),lambda r:[r["name"],r["regime"],r["code"]])
    emit("epof",read(data/"epof.json")["rows"],lambda r:[r["name"],"ORPHA:"+str(r["code"])])
    emit("isp",read(data/"isp-registry.json")["rows"],lambda r:[r["name"],r["registration"],r.get("active_ingredients"),r.get("holder")])
    emit("actors",read(data/"stakeholders.json"),lambda r:[r["name"],r["group"],r.get("scope")])
    emit("social",read(data/"social-posts.json")+[r for r in read(data/"pending.json") if r.get("source_type") in ("Prensa","Comunicado institucional")],lambda r:[r["title"],r.get("authority"),r.get("topics")])
    emit("budget",read(data/"budget-history.json")["rows"],lambda r:[str(r["year"]),"Presupuesto Salud Partida 16"])
    emit("clinical",read(data/"clinical-trials.json")["rows"],lambda r:[r["title"],r["id"],r["conditions"],r["interventions"],r["sponsor"],r["status"]])
    pat=read(data/"patents.json")
    emit("patents",pat["rows"],lambda r:[r["title"],r["application"],r["registration"],r["applicant"],r["ipc"]])
    emit("procurement",read(data/"procurement.json")["rows"],lambda r:[r["product"],r["order"],r["description"],r["supplier"],r["buyer"]])
    write(data/"patents-meta.json",{k:v for k,v in pat.items() if k!="rows"})
    for year in sorted({r["year"] for r in pat["rows"]}):
        rows=[r for r in pat["rows"] if r["year"]==year]
        write(data/"patents-year"/(str(year)+".json"),{"count":len(rows),"rows":rows})
