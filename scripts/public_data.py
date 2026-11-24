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
