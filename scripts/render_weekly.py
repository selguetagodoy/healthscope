"""Render a complete public briefing at build time; no browser fetch required."""
import html
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

def esc(v):
    return html.escape(str(v if v is not None else ""),quote=True)

def day(v):
    return v[8:10]+"/"+v[5:7] if v and len(v)>=10 else ""

def timestamp(v):
    try:
        d=datetime.fromisoformat(v)
        return d.astimezone(ZoneInfo('America/Santiago')).strftime("%d/%m/%Y · %H:%M")
    except (ValueError,TypeError):
        return ""

def safe(v):
    try:
        u=urlsplit(v)
        return esc(v) if u.scheme=="https" and u.hostname else ""
    except (ValueError,TypeError):
        return ""

def item(r,verified):
    link=safe(r.get("url"))
    if not link or not r.get("title"):
        return ""
    meta=" · ".join(filter(None,[r.get("topic"),day(r.get("published")),"NUEVO" if r.get("new_since_previous") else ""]))
    author=" · ".join(dict.fromkeys(filter(None,[r.get("authority"),r.get("source_type")])))
    body=""
    if r.get("source_type")=="Votación de Sala":
        if r.get("vote_result"):body+="<p><strong>Resultado: </strong>"+esc(r["vote_result"])+"</p>"
        if r.get("vote_totals"):body+="<p>"+esc(r["vote_totals"])+"</p>"
    elif verified:
        if r.get("summary"):body+="<p>"+esc(r["summary"])+"</p>"
        if r.get("implications"):body+='<p class="weekly-impact"><strong>Implicancias:</strong> '+esc(r["implications"])+"</p>"
    return '<article class="weekly-item"><small>'+esc(meta)+'</small><h3>'+esc(r["title"])+'</h3><p class="weekly-author">'+esc(author)+'</p>'+body+'<a class="text-link" target="_blank" rel="noopener noreferrer" href="'+link+'">Fuente directa ↗</a></article>'

def render(page,d,full=False):
    verified=[r for r in d.get("verified",[]) if r.get("title") and safe(r.get("url"))]
    candidates=[r for r in d.get("candidates",[]) if r.get("title") and safe(r.get("url"))]
    sources=[s for s in d.get("sources",[]) if s.get("status") in ("ok","partial") and safe(s.get("url"))]
    def replace(tag,id,value):
        nonlocal page
        pattern=r'(<'+tag+r'\b[^>]*\bid="'+id+r'"[^>]*>).*?(</'+tag+r'>)'
        page,n=re.subn(pattern,lambda m:m[1]+value+m[2],page,count=1,flags=re.S)
        if n!=1:raise ValueError("Briefing element absent: "+id)
    replace("span","weeklyWindow",esc(day(d.get("window_start"))+"–"+day(d.get("window_end"))+" · últimos siete días"))
    replace("strong","weeklyCut",esc("Actualización: "+timestamp(d.get("last_monitor_at") or d.get("generated_at"))))
    kpis=[("Destacados",len(verified)),("Publicaciones",len(candidates)),("Fuentes de la edición",len(sources))]
    replace("div","weeklyKpis","".join("<div><strong>"+esc(v)+"</strong><span>"+esc(k)+"</span></div>" for k,v in kpis))
    tracker=d.get("legislative_tracker",{})
    if tracker.get("projects"):
        cards=[]
        for p in tracker["projects"]:
            if not safe(p.get("url")):continue
            timeline="".join('<li><a href="'+safe(t["url"])+'" target="_blank" rel="noopener noreferrer"><time>'+esc(day(t["date"]))+'</time> '+esc(t["title"])+'</a></li>' for t in p.get("timeline",[]) if safe(t.get("url")))
            metric=('<div class="leg-metric"><strong>'+esc(p["metric"])+'</strong><small>'+esc(p["metric_label"])+'</small></div>') if p.get("metric") else ""
            cards.append('<article class="leg-card"><small>BOLETÍN '+esc(p["bulletin"])+'</small><h3>'+esc(p["title"])+'</h3><p class="leg-status">'+esc(p["status"])+'</p>'+metric+'<p>'+esc(p["summary"])+'</p>'+('<ol class="leg-timeline">'+timeline+'</ol>' if timeline else '')+'<p class="leg-next"><strong>Próximo hito:</strong> '+esc(p["next"])+'</p><a class="text-link" href="'+safe(p["url"])+'" target="_blank" rel="noopener noreferrer">Tramitación oficial ↗</a></article>')
        block='<div class="leg-brief"><p class="eyebrow">CONGRESO · SEGUIMIENTO DE PROYECTOS</p><h2>Estado de la agenda legislativa</h2><p class="editorial-caption">Estado documentado al '+esc(day(tracker.get("updated")))+' · Cámara, Senado y Comisión Mixta</p><div class="leg-grid">'+''.join(cards)+'</div></div>'
        page=page.replace('<div class="weekly-body">',block+'<div class="weekly-body">',1)
    # Prioritize the latest budget outcome and represent each chamber before other headlines.
    leading=[x for x in verified if x.get("id")=="camara-presupuesto-2027-salud-2026-11-23"]
    ordered=leading+[x for x in verified if x not in leading]
    # Select across themes, not five versions of the same budget story.
    selected=[];topics=set()
    for x in ordered:
        key=x.get("topic","")
        if key in topics:continue
        selected.append(x);topics.add(key)
    selected.extend(x for x in ordered if x not in selected)
    replace("div","weeklyVerified","".join(item(r,True) for r in (ordered if full else selected[:5])) or '<p><a href="./radar/">Ver agenda sanitaria →</a></p>')
    votes=[x for x in candidates if x.get("source_type")=="Votación de Sala"]
    other=[x for x in candidates if x not in votes]
    publications="".join(item(r,False) for r in (other if full else other[:6]))
    if votes:
        publications='<h3 class="weekly-subtitle">Votaciones de la Cámara</h3>'+''.join(item(r,False) for r in (votes if full else votes[:5]))+'<h3 class="weekly-subtitle">Otras publicaciones</h3>'+publications
    replace("div","weeklyCandidates",publications or '<p><a href="./prensa/">Ver publicaciones →</a></p>')
    replace("div","weeklySourceList","".join('<div class="weekly-source"><a href="'+safe(s["url"])+'" target="_blank" rel="noopener noreferrer">'+esc(s.get("name"))+"</a></div>" for s in sources))
    report=["HEALTHSCOPE CHILE · BRIEFING","Ventana: "+day(d.get("window_start"))+"–"+day(d.get("window_end"))]
    for r in ordered:
        report.extend(["","*"+r["title"]+"*",day(r.get("published"))+" · "+r.get("authority",""),r.get("summary","")])
        if r.get("implications"):report.append("Implicancias: "+r["implications"])
        report.append(r["url"])
    payload=json.dumps("\n".join(report),ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    page=page.replace('</section>\n    <section class="masthead"', '<script type="application/json" id="weeklyReport">'+payload+'</script></section>\n    <section class="masthead"',1)
    if not verified:page=page.replace('id="weeklyCopy"','id="weeklyCopy" hidden')
    return page
