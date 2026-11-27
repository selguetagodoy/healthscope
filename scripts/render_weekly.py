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
    replace("strong","weeklyCut",esc("Edición: "+timestamp(d.get("generated_at"))))
    last_scan=timestamp(d.get("last_monitor_at"))
    replace("span","weeklyHealth",esc("Última consulta de fuentes: "+last_scan) if last_scan else "")
    page=page.replace('<div class="weekly-kpis" id="weeklyKpis"></div>',"",1)
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
    # Respect the current edition ranking: publication date, editorial score and title.
    # Never pin a historic event to the front page.
    ordered=sorted(verified,key=lambda x:(x.get("published") or "",x.get("score") or 0,x.get("title") or ""),reverse=True)
    # Select across themes, not five versions of the same budget story.
    selected=[];topics=set()
    for x in ordered:
        key=x.get("topic","")
        if key in topics:continue
        selected.append(x);topics.add(key)
    selected.extend(x for x in ordered if x not in selected)

    # Front page uses actual verified headlines and tracked bills, not mockup content.
    if not full:
        lead=selected[0] if selected else None
        lead_html='<p class="lead-label">HECHO DESTACADO</p>'
        if lead:
            meta=" · ".join(filter(None,[lead.get("topic"),day(lead.get("published")),lead.get("authority")]))
            lead_html+='<p class="lead-meta">'+esc(meta)+'</p><h2>'+esc(lead["title"])+'</h2>'
            if lead.get("summary"):lead_html+='<p class="lead-summary">'+esc(lead["summary"])+'</p>'
            if lead.get("implications"):lead_html+='<div class="lead-impact"><strong>Por qué importa</strong><p>'+esc(lead["implications"])+'</p></div>'
            lead_html+='<a class="lead-source" href="'+safe(lead["url"])+'" target="_blank" rel="noopener noreferrer">Consultar fuente original ↗</a>'
        else:
            lead_html+='<h2>Decisiones y evidencia para entender la salud en Chile.</h2><a class="lead-source" href="./radar/">Explorar el radar →</a>'
        from collections import Counter
        distribution=Counter(x.get("topic") or "Otros" for x in verified)
        if distribution:
            maximum=max(distribution.values())
            lead_html+='<figure class="edition-mini-chart"><h3>Hechos documentados por materia</h3>'+''.join('<div class="chart-row"><span>'+esc(k)+'</span><div class="chart-track" aria-hidden="true"><span style="width:'+str(100*v/maximum)+'%"></span></div><span class="chart-number">'+str(v)+'</span></div>' for k,v in distribution.most_common())+'<figcaption>Fuente: registros verificados de la edición · '+esc(day(d.get("window_start"))+'–'+day(d.get("window_end")))+'</figcaption></figure>'
        replace("div","editorialLead",lead_html)
        secondary='<p class="column-label">EN FOCO</p>'
        for r in selected[1:3]:
            secondary+='<article class="secondary-story"><small>'+esc(" · ".join(filter(None,[r.get("topic"),day(r.get("published"))])))+'</small><h3>'+esc(r["title"])+'</h3><p>'+esc(r.get("summary",""))+'</p><a class="text-link" href="'+safe(r["url"])+'" target="_blank" rel="noopener noreferrer">Fuente directa ↗</a></article>'
        if len(selected)<2:secondary+='<a class="text-link" href="./actualidad/">Consultar actualidad →</a>'
        replace("div","editorialSecondary",secondary)
        tracked='<p class="column-label">SEGUIMIENTO LEGISLATIVO</p>'
        for p in tracker.get("projects",[]):
            if not safe(p.get("url")):continue
            tracked+='<article class="tracker-mini"><span class="tracker-status">'+esc(p.get("status",""))+'</span><h3>'+esc(p.get("title",""))+'</h3><small>BOLETÍN '+esc(p.get("bulletin",""))+'</small>'
            if p.get("metric"):tracked+='<strong>'+esc(p["metric"])+'</strong><p class="editorial-caption">'+esc(p.get("metric_label",""))+'</p>'
            tracked+='<a href="'+safe(p["url"])+'" target="_blank" rel="noopener noreferrer">Tramitación oficial ↗</a></article>'
        tracked+='<a class="text-link" href="./normativa/">Todos los proyectos →</a>'
        replace("aside","editorialTracker",tracked)
    else:
        page=page.replace('class="weekly-brief section-rule','class="weekly-brief section-rule full-edition',1)

    shown=ordered if full else [r for r in ordered if r not in selected[:3]]
    replace("div","weeklyVerified","".join(item(r,True) for r in shown) or '<p><a href="./radar/">Ver agenda sanitaria →</a></p>')
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
