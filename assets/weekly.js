(function(){
'use strict';
const $=id=>document.getElementById(id);
const b=$('weeklyCopy'),r=$('weeklyReport');if(!b||!r||b.hidden)return;
let report;try{report=JSON.parse(r.textContent)}catch{return}
b.disabled=false;
b.onclick=async()=>{try{await navigator.clipboard.writeText(report);$('weeklyCopyStatus').textContent='Copiado al portapapeles.'}catch{const a=document.createElement('textarea');a.value=report;a.setAttribute('aria-label','Texto del briefing');$('weeklyCopyStatus').replaceChildren(a);a.select()}};
})();