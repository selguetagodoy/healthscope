(function(){'use strict';
if(document.body.dataset.view!=='global-results')return;
const q=(new URLSearchParams(location.search).get('q')||'').trim(), input=document.getElementById('globalQuery'),target=document.getElementById('global-search-results'),summary=document.getElementById('global-search-summary');
if(input)input.value=q;
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
if(!q){summary.textContent='Busca un medicamento, enfermedad, organización, código o tema.';return}
summary.textContent='Buscando «'+q+'»…';
const words=norm(q).split(/\s+/).filter(Boolean);
const sources=[['events','Decisiones y noticias','radar'],['coverage','GES y Ley Ricarte Soto','cobertura'],['epof','Enfermedades raras','enfermedades-raras'],['isp','Registro sanitario ISP','medicamentos'],['actors','Actores sanitarios','stakeholders'],['social','Prensa y redes','prensa'],['budget','Presupuesto','presupuesto'],['clinical','Estudios clínicos','ensayos-clinicos'],['patents','Patentes','patentes'],['procurement','Compras','compras-farmaceuticas']];
const results=sources.map(()=>null);let count=0;
function draw(){target.innerHTML=results.filter(Boolean).join('');summary.textContent=count.toLocaleString('es-CL')+' coincidencias por registro para «'+q+'».'}
Promise.allSettled(sources.map(async([id,label,route],i)=>{const response=await fetch('./data/search/'+id+'.json');if(!response.ok)throw Error(id);const rows=await response.json(),hits=rows.filter(r=>words.every(w=>norm(r.join(' ')).includes(w)));if(!hits.length)return;count+=hits.length;results[i]='<article class="coverage-card search-result"><span class="coverage-tag">'+esc(label)+'</span><h3>'+hits.length.toLocaleString('es-CL')+' coincidencias</h3>'+hits.slice(0,5).map(r=>'<p>'+esc(r[0])+(r[1]?' · '+esc(r[1]):'')+'</p>').join('')+'<a class="text-link" href="./'+route+'/?q='+encodeURIComponent(q)+'">Explorar '+esc(label.toLowerCase())+' →</a></article>';draw()})).then(out=>{draw();if(!count)summary.textContent='Sin coincidencias para «'+q+'» en los catálogos consultados.';if(out.some(r=>r.status==='rejected'))summary.textContent+=' Resultados de los catálogos disponibles.'});
})();