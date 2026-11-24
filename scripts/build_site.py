#!/usr/bin/env python3
"""Build static pages and stable event permalinks for GitHub Pages."""
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist"
BASE = "https://selguetagodoy.github.io/healthscope/"
MODULES = {"semana":("weekly","La semana en salud"),"compras-farmaceuticas":("bulk-procurement","Compras farmacéuticas"),"presupuesto":("bulk-budget","Presupuesto sanitario histórico"),"ensayos-clinicos":("bulk-trials","Estudios clínicos en Chile"),"patentes":("bulk-patents","Patentes farmacéuticas"),"medicamentos":("registro-isp","Registro sanitario de medicamentos"),"enfermedades-raras":("epof","Enfermedades poco frecuentes · ORPHA"),"stakeholders":("stakeholders","Stakeholders sanitarios"),"prensa":("prensa","Prensa, redes y comunicados"),"cobertura":("cobertura","Catálogo GES y Ley Ricarte Soto"),"normativa":("normativa","Leyes y proyectos prioritarios"),"actualidad":("actualidad","Actualidad sanitaria"),"radar":("radar","Radar de decisiones"),"farmaceutico":("pharma","Vigilancia farmacéutica"),"compras":("compras","Compras públicas"),"acceso":("acceso","Acceso y cobertura"),"datos":("datos","Datos y presupuesto"),"instituciones":("ecosistema","Instituciones"),"biblioteca":("investigacion","Biblioteca documental"),"fuentes":("fuentes","Fuentes y actualización")}
def esc(v):
    return html.escape(str(v or ""), quote=True)
def write_page(path, text):
    folder = DEST / path
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(text, encoding="utf-8")
def meta(page, title, url):
    page = re.sub(r"<title>.*?</title>", "<title>"+esc(title)+" | HealthScope Chile</title>", page, count=1)
    page = re.sub(r'(<link rel="canonical" href=")[^"]+(")', lambda m:m[1]+esc(url)+m[2], page, count=1)
    page = re.sub(r'(<meta property="og:url" content=")[^"]+(")', lambda m:m[1]+esc(url)+m[2], page, count=1)
    page = re.sub(r'(<meta property="og:title" content=")[^"]+(")', lambda m:m[1]+esc(title+" | HealthScope Chile")+m[2], page, count=1)
    return page
def main():
    if DEST.exists(): shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for name in ("index.html","events.json","robots.txt","sitemap.xml",".nojekyll","METHODOLOGY.md","SOURCES.md","DATA_DICTIONARY.md"):
        source=ROOT/name
        if source.exists(): shutil.copy2(source,DEST/name)
    for name in ("assets","data"): shutil.copytree(ROOT/name,DEST/name)
    from weekly_brief import make, write, TZ
    from datetime import datetime
    brief=make(datetime.now(TZ))
    # Only public editorial fields; execution diagnostics stay in the repository.
    brief.pop("undated_social",None)
    for source in brief["sources"]:
        source.pop("errors",None)
    write(DEST/"data"/"weekly-brief.json",brief)
    for internal in ("weekly-extra.json","bulk-status.json"):
        (DEST/"data"/internal).unlink(missing_ok=True)
    monitoring_path=DEST/"data"/"monitoring.json"
    if monitoring_path.exists():
        monitoring=json.loads(monitoring_path.read_text(encoding="utf-8"))
        for source in monitoring.get("sources",[]):
            source.pop("error",None)
        write(monitoring_path,monitoring)
    template=(ROOT/"index.html").read_text(encoding="utf-8")
    sitemap=[BASE]
    for route,(section,title) in MODULES.items():
        page=meta(template,title,BASE+route+"/").replace("<head>","<head>\n  <base href=\"../\">",1).replace("<body>",'<body data-view="'+section+'">',1)
        page=re.sub(r'<section ([^>]*\bid="'+re.escape(section)+r'"[^>]*)>',lambda m:'<section '+re.sub(r'class="([^"]*)"',r'class="\1 module-active"',m[1],count=1)+'>',page,count=1)
        page=page.replace('<div id="dataNotice"', '<div class="module-intro"><a href="./">Inicio</a> / '+esc(title)+'</div><div id="dataNotice"',1)
        page=page.replace('href="#contenido"','href="./'+route+'/#contenido"',1)
        write_page(route,page); sitemap.append(BASE+route+"/")
    events=json.loads((ROOT/"events.json").read_text(encoding="utf-8"))
    for e in events:
        eid=e.get("id","")
        if e.get("status")!="Verificado" or not re.fullmatch(r"[a-z0-9-]+",eid) or urlsplit(e.get("url","")).scheme!="https": continue
        path="fichas/"+eid+"/"; url=BASE+path
        title=esc(e.get("title")); source=esc(e.get("url"))
        page=meta(template,e.get("title"),url).replace("<head>","<head>\n  <base href=\"../../\">",1)
        main='<main id="contenido" class="shell"><article class="event-detail"><p class="module-intro"><a href="./">Inicio</a> / <a href="./radar/">Radar</a> / Ficha</p><p class="eyebrow">REGISTRO VERIFICADO · '+esc(e.get("category"))+'</p><h1>'+title+'</h1><p class="detail-meta">Fecha del hecho: '+esc(e.get("date"))+' · Publicación: '+esc(e.get("published"))+' · '+esc(e.get("authority"))+'</p><h2>Hecho documentado</h2><p>'+esc(e.get("summary"))+'</p><h2>Implicancias</h2><p>'+esc(e.get("implications"))+'</p><p class="detail-meta">Medicamento o tema: '+esc(e.get("medication"))+'</p><div class="detail-actions"><a class="button button-dark" href="'+source+'" target="_blank" rel="noopener noreferrer">Fuente oficial ↗</a><a class="button button-light" href="./radar/">Volver al radar</a></div></article></main>'
        if not e.get("implications"): main=main.replace("<h2>Implicancias</h2><p></p>","")
        if not e.get("medication"): main=main.replace('<p class="detail-meta">Medicamento o tema: </p>',"")
        page=re.sub(r'<main id="contenido".*?</main>',lambda _:main,page,flags=re.S,count=1)
        page=re.sub(r'<script[^>]*src="[^"]*(?:app|coverage|intelligence|epof|isp-registry|bulk|weekly)\.js"[^>]*></script>','',page)
        page=page.replace('href="#contenido"','href="'+esc(url)+'#contenido"',1)
        write_page(path,page); sitemap.append(url)
    (DEST/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(u)+'</loc></url>' for u in sitemap)+'</urlset>',encoding="utf-8")
    print(f"Publicación preparada: {len(MODULES)} módulos, {len(sitemap)-len(MODULES)-1} fichas.")
if __name__=="__main__": main()
