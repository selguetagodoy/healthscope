#!/usr/bin/env python3
"""Import the public Chilean EPOF nomenclature, never patient records."""
import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PAGE = "https://diprece.minsal.cl/enfermedades-poco-frecuentes/"
PDF = "https://diprece.minsal.cl/wp-content/uploads/2026/01/08012026-Listado-EPOF-documento-web.pdf"
RESOLUTION = "https://diprece.minsal.cl/wp-content/uploads/2026/01/Aprueba-listado-nacional-de-epof-establecido-en-la-ley-21.743.pdf"
EXPECTED = 9784

def download(url, maximum=8_000_000):
    req = Request(url, headers={"User-Agent": "HealthScopeChile/0.8 public nomenclature catalog", "Accept": "*/*"})
    with urlopen(req, timeout=40) as response:
        raw = response.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("Source exceeds size limit")
    return raw

def fold(value):
    return "".join(c for c in unicodedata.normalize("NFD", value.lower()) if not unicodedata.combining(c))

def public_csv(page):
    match = re.search(r'csvUrl\s*:\s*["\']([^"\']+)["\']', page)
    if not match:
        raise ValueError("DIPRECE no longer exposes csvUrl")
    import html
    url = html.unescape(match.group(1))
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "docs.google.com" or not parts.path.startswith("/spreadsheets/d/e/") or not parts.path.endswith("/pub") or "output=csv" not in parts.query:
        raise ValueError("Unexpected public CSV source")
    return url

def parse_csv(raw):
    text = raw.decode("utf-8-sig")
    try: dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error: dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    fields = reader.fieldnames or []
    code_key = next((x for x in fields if "codigo" in fold(x) or "orpha" in fold(x)), None)
    name_key = next((x for x in fields if "nombre" in fold(x) or "patologia" in fold(x) or "enfermedad" in fold(x)), None)
    if not code_key or not name_key or code_key == name_key:
        raise ValueError("Unknown CSV columns: " + repr(fields))
    result = {}
    for row in reader:
        code = (row.get(code_key) or "").strip()
        name = " ".join((row.get(name_key) or "").split())
        if not code and not name: continue
        if not re.fullmatch(r"\d+", code) or not name:
            raise ValueError("Invalid ORPHA row: "+repr((code,name)))
        n = int(code)
        if n < 1 or n in result: raise ValueError("Duplicate or invalid ORPHA code "+code)
        result[n] = name
    return [{"code": c, "name": result[c]} for c in sorted(result)]

def main():
    p=argparse.ArgumentParser();p.add_argument("--output", type=Path, default=ROOT/"data"/"epof.json");p.add_argument("--allow-count-change",action="store_true");args=p.parse_args()
    source=public_csv(download(PAGE).decode("utf-8","replace"))
    raw=download(source)
    rows=parse_csv(raw)
    if len(rows)!=EXPECTED and not args.allow_count_change:
        raise ValueError(f"Expected {EXPECTED} rows; obtained {len(rows)}. Review source before publication.")
    if not rows: raise ValueError("Empty catalogue")
    obj={"schema_version":1,"source":"Ministerio de Salud · DIPRECE","source_url":PAGE,"document_url":PDF,"resolution_url":RESOLUTION,"source_csv_url":source,"source_sha256":hashlib.sha256(raw).hexdigest(),"retrieved_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"declared_count":EXPECTED,"count":len(rows),"rows":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8");tmp.replace(args.output)
    print(f"Validated national nomenclature: {len(rows)} unique codes; sha256={obj['source_sha256']}")

if __name__=="__main__": main()
