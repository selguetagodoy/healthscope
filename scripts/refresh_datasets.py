"""Refresh public datasets with bounded backfill and preserve successful snapshots."""
import argparse,concurrent.futures,csv,gzip,json
from datetime import datetime,date,timezone
from pathlib import Path
from import_intelligence import oc_month,clinical,patents
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"
def read(p,default):return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
def write(p,d):
    tmp=p.with_suffix(".tmp");tmp.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8");tmp.replace(p)
def months(n):
    now=date.today();y,m=now.year,now.month
    for _ in range(n):
        m-=1
        if not m:y-=1;m=12
        yield f"{y:04d}-{m:02d}"
def get_month(p):
    rows,meta=oc_month(p)
    if len(rows)!=meta["lines"] or len({r["id"] for r in rows})!=len(rows):raise ValueError("Duplicate or inconsistent lines")
    meta["checked_at"]=datetime.now(timezone.utc).isoformat()
    return p,rows,meta
def main():
    p=argparse.ArgumentParser();p.add_argument("--batch",type=int,default=6);p.add_argument("--refresh-recent",action="store_true");p.add_argument("--refresh-clinical",action="store_true");p.add_argument("--refresh-patents",action="store_true");a=p.parse_args()
    index=DATA/"procurement-index.json";folder=DATA/"procurement-months";folder.mkdir(exist_ok=True)
    old=read(index,{"periods":[]});known={x["period"]:x for x in old["periods"] if (folder/(x["period"]+".json.gz")).exists()}
    target=list(months(60));missing=[m for m in target if m not in known]
    selected=list(dict.fromkeys((target[:3] if a.refresh_recent else [])+missing[:a.batch]))
    errors={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs={pool.submit(get_month,m):m for m in selected}
        for future in concurrent.futures.as_completed(jobs):
            month=jobs[future]
            try:
                p,rows,meta=future.result()
                path=folder/(p+".json.gz");tmp=path.with_suffix(".tmp");tmp.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,separators=(",",":")).encode(),mtime=0));tmp.replace(path);known[p]=meta
                print("OK",p,len(rows),flush=True)
            except Exception as e:errors[month]=str(e)[:250];print("ERROR",month,errors[month],flush=True)
    if known:
        periods=sorted(known.values(),key=lambda r:r["period"],reverse=True);latest=periods[0]["period"]
        rows=json.loads(gzip.decompress((folder/(latest+".json.gz")).read_bytes()))
        d=read(DATA/"procurement.json",{});d.update({"source":"Dirección ChileCompra · datos abiertos","source_url":"https://datos-abiertos.chilecompra.cl/descargas","scope":"Órdenes de compra UNSPSC 51; detalle mensual","checked_at":known[latest]["checked_at"],"periods":periods,"errors":[],"detail_period":latest,"detail_total":len(rows),"count":len(rows),"rows":rows})
        tmp=DATA/"procurement-lines.tmp"
        with tmp.open("w",encoding="utf-8-sig",newline="") as fp:
            wr=csv.DictWriter(fp,fieldnames=list(rows[0]));wr.writeheader()
            for r in rows:wr.writerow({k:("'"+v if isinstance(v,str) and v.startswith(("=","+","-","@","\t","\r")) else v) for k,v in r.items()})
        tmp.replace(DATA/"procurement-lines.csv");write(DATA/"procurement.json",d);write(index,{"target_months":60,"periods":periods})
    for enabled,name,fn in [(a.refresh_clinical,"clinical-trials",clinical),(a.refresh_patents,"patents",patents)]:
        if not enabled:continue
        dest=DATA/(name+".json");backup=dest.read_bytes() if dest.exists() else None
        try:
            fn()
            current=read(dest,{})
            if name=="patents" and current.get("errors"):raise ValueError("Partial patent import")
            if not current.get("rows"):raise ValueError("Empty snapshot")
        except Exception as e:
            if backup:dest.write_bytes(backup)
            errors[name]=str(e)[:250];print("Preserved previous",name,errors[name],flush=True)
    print("Historical months available:",len(known),"/60",flush=True)
    if errors: print("Source errors:",json.dumps(errors,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
