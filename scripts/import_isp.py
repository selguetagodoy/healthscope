#!/usr/bin/env python3
"""Merge an official ISP export saved as CSV (Excel: CSV UTF-8). Explicit scope required."""
import argparse,csv,json,re,unicodedata
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def norm(x):
    return "".join(c for c in unicodedata.normalize("NFD",x.lower().strip()) if not unicodedata.combining(c))
def parse(path,status,sale,checked,query):
    with path.open(encoding="utf-8-sig",newline="") as fp:
        sample=fp.read(4096);fp.seek(0)
        reader=csv.DictReader(fp,dialect=csv.Sniffer().sniff(sample,delimiters=",;\t"))
        fields={norm(x):x for x in reader.fieldnames or []}
        def col(*names):
            for n in names:
                if n in fields:return fields[n]
            raise ValueError("Missing column: "+repr(names))
        columns={"registration":col("registro","numero de registro","n° registro"),"name":col("nombre","nombre producto"),"registration_date":col("fecha registro","fecha de registro"),"holder":col("empresa","titular","empresa(titular)"),"active_ingredients":col("principio activo")}
        rows=[]
        for r in reader:
            x={k:(r.get(v) or "").strip() for k,v in columns.items()}
            if not any(x.values()):continue
            if not x["registration"] or not x["name"] or not x["holder"]:raise ValueError("Incomplete ISP row")
            x.update(status=status,sale_condition=sale,checked_at=checked,query=query,legal_control=(r.get(fields.get("control legal","")) or "").strip())
            rows.append(x)
        return rows
def main():
    p=argparse.ArgumentParser();p.add_argument("csv",type=Path);p.add_argument("--status",required=True,choices=["Vigente","No Vigente","Vigente con suspensión voluntaria de distribución"]);p.add_argument("--sale",required=True);p.add_argument("--checked",required=True);p.add_argument("--query",required=True);p.add_argument("--expected",type=int,required=True);args=p.parse_args();date.fromisoformat(args.checked)
    rows=parse(args.csv,args.status,args.sale,args.checked,args.query)
    if len(rows)!=args.expected or len({r["registration"] for r in rows})!=len(rows):raise ValueError("Export count/uniqueness does not match official query")
    target=ROOT/"data/isp-registry.json";data=json.loads(target.read_text(encoding="utf-8"));merged={r["registration"]:r for r in data["rows"]};merged.update({r["registration"]:r for r in rows});data["rows"]=sorted(merged.values(),key=lambda r:r["registration"]);data["count"]=len(merged);data["checked_at"]=args.checked;data["scope"]="Selección de consultas oficiales importadas; no exhaustiva";data["queries"].append({"filter":args.query,"total_reported":args.expected,"imported":len(rows)})
    tmp=target.with_suffix(".tmp");tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");tmp.replace(target);print("ISP:",len(merged),"unique registrations")
if __name__=="__main__":main()
