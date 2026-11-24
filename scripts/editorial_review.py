"""Review public captures; never store confidential notes in this public repo."""
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def save(path,rows):
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");tmp.replace(path)
def main():
    p=argparse.ArgumentParser();p.add_argument("id");p.add_argument("decision",choices=["discard","duplicate","promote"]);p.add_argument("--summary");p.add_argument("--implications");a=p.parse_args()
    pending=ROOT/"data/pending.json";events=ROOT/"events.json";ledger=ROOT/"data/editorial-decisions.json"
    rows=json.loads(pending.read_text(encoding="utf-8"));entry=next((r for r in rows if r["id"]==a.id),None)
    if not entry:raise ValueError("Unknown capture")
    decisions=json.loads(ledger.read_text(encoding="utf-8"))
    if a.decision=="promote":
        if not a.summary or not a.implications:raise ValueError("Reviewed summary and implications required")
        items=json.loads(events.read_text(encoding="utf-8"))
        if any(r["url"]==entry["url"] for r in items):raise ValueError("Already published")
        items.append({**entry,"status":"Verificado","summary":a.summary,"implications":a.implications})
        save(events,items)
    decisions.append({"id":entry["id"],"url":entry["url"],"decision":a.decision,"at":datetime.now(timezone.utc).isoformat()})
    save(ledger,decisions);save(pending,[r for r in rows if r["id"]!=a.id])
if __name__=="__main__":main()
