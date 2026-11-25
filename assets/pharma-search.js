/* Public pharmacological search vocabulary. Search relationships do not establish clinical interchangeability, award, authorization or availability. */
(function(root){
'use strict';
const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
const groups=[
[['privigen','octagam','kiovig','gamunex','flebogamma','intratect'],[['inmunoglobulina humana','intravenosa'],['inmunoglobulina','10%'],['ivig'],['immunoglobulin','intravenous']], [['inmunoglobulina humana'],['gamaglobulina'],['gamma globulina'],['igg']]],
[['hizentra','cuvitru','hyqvia'],[['inmunoglobulina','subcutanea'],['scig'],['immunoglobulin','subcutaneous']], [['inmunoglobulina humana'],['gamaglobulina'],['igg']]],
[['andembry'],[['garadacimab']],[['angioedema hereditario']]],
[['berinert','cinryze','ruconest'],[],[['inhibidor','c1','esterasa'],['c1','inhibidor'],['c1','inactivador'],['c1','esterase','inhibitor'],['angioedema hereditario']]],
[['ferinject','injectafer'],[['carboximaltosa ferrica'],['hierro carboximaltosa'],['ferric carboxymaltose']],[]],
[['afstyla'],[['lonoctocog alfa']],[['factor viii','recombinante'],['factor 8','recombinante']]],
[['haemate','humate p','voncento'],[['factor viii','von willebrand'],['factor 8','von willebrand']],[['von willebrand']]],
[['beriplex','kcentra','octaplex'],[['complejo protrombinico'],['complejo de protrombina'],['prothrombin complex']],[]],
[['rhophylac','rhogam'],[['inmunoglobulina','anti d'],['inmunoglobulina','rho'],['immunoglobulin','anti d']],[]],
[['alburex','albuminar','albúmina humana'],[['albumina humana'],['human albumin']],[]],
[['trikafta','kaftrio'],[['elexacaftor','tezacaftor','ivacaftor']],[['modulador','cftr']]],
[['alyftrek'],[['vanzacaftor','tezacaftor','deutivacaftor']],[['modulador','cftr']]],
[['casgevy'],[['exagamglogene autotemcel'],['exagamglogen autotemcel'],['exa cel']],[]],
[['journavx'],[['suzetrigina'],['suzetrigine']],[]],
[['kalydeco'],[['ivacaftor']],[]],
[['orkambi'],[['lumacaftor','ivacaftor']],[]],
[['symdeko','symkevi'],[['tezacaftor','ivacaftor']],[]],
[['takhzyro'],[['lanadelumab']],[['angioedema hereditario']]],
[['firazyr'],[['icatibant']],[['angioedema hereditario']]],
[['orladeyo'],[['berotralstat']],[['angioedema hereditario']]],
[['hemlibra'],[['emicizumab']],[['hemofilia a']]],
[['advate','kogenate','novoeight','elocta','adynovi'],[],[['factor viii','recombinante'],['hemofilia a']]],
[['benefix','alprolix','idelvion'],[],[['factor ix','recombinante'],['hemofilia b']]],
[['kadcyla'],[['trastuzumab emtansina'],['trastuzumab emtansine']],[]],
[['herceptin'],[['trastuzumab']],[]],
[['keytruda'],[['pembrolizumab']],[]],
[['opdivo'],[['nivolumab']],[]],
[['darzalex'],[['daratumumab']],[]],
[['velcade'],[['bortezomib']],[]],
[['mabthera','rituxan'],[['rituximab']],[]],
[['soliris'],[['eculizumab']],[]],
[['ultomiris'],[['ravulizumab']],[]],
[['spinraza'],[['nusinersen']],[]],
[['evrysdi'],[['risdiplam']],[]],
[['zolgensma'],[['onasemnogene abeparvovec']],[]],
[['pulmozyme'],[['dornasa alfa'],['dornase alfa']],[]],
[['tobi','bramitob'],[['tobramicina','inhalatoria'],['tobramicina','nebulizacion']],[['tobramicina']]],
[['ozempic','wegovy','rybelsus'],[['semaglutida'],['semaglutide']],[]],
[['mounjaro','zepbound'],[['tirzepatida'],['tirzepatide']],[]],
[['humira'],[['adalimumab']],[]],
[['enbrel'],[['etanercept']],[]],
[['remicade'],[['infliximab']],[]],
[['stelara'],[['ustekinumab']],[]],
[['xolair'],[['omalizumab']],[]],
[['dupixent'],[['dupilumab']],[]],
[['eliquis'],[['apixaban']],[]],
[['xarelto'],[['rivaroxaban']],[]],
[['lantus','toujeo'],[['insulina glargina']],[]]
];
function contains(t,p){return (' '+t+' ').includes(' '+norm(p)+' ');}
function all(t,terms){return terms.every(p=>contains(t,p));}
function match(value,query){
 const t=norm(value),q=norm(query);if(!q)return 'direct';
 if(q.split(' ').every(w=>t.includes(w)))return 'direct';
 let best='';
 for(const [brands,exact,related] of groups){
   for(const b of brands){
     if(!contains(q,b))continue;
     const rest=(' '+q+' ').replace(' '+norm(b)+' ',' ').trim();
     if(rest&&!rest.split(' ').every(w=>t.includes(w)))continue;
     if(b==='kalydeco' && /elexacaftor|tezacaftor|lumacaftor|vanzacaftor/.test(t)){best='related';continue;}
     if(exact.some(a=>all(t,a)))return 'ingredient';
     if(related.some(a=>all(t,a)))best='related';
   }
   // An ingredient query may match the commercial name, but not unrelated class names.
   if(exact.some(a=>all(q,a))&&brands.some(b=>contains(t,b))){
     const recognized=new Set(exact.flat().flatMap(p=>norm(p).split(' ')));
     if(q.split(' ').every(w=>recognized.has(w)||t.includes(w)))return 'ingredient';
   }
 }
 if(q==='hemofilia'&&/factor (viii|ix|8|9)|antihem/.test(t))return 'related';
 if(q==='fibrosis quistica'&&/tobramicina|dornasa|modulador cftr/.test(t))return 'related';
 if(q==='oncologia'&&/trastuzumab|bortezomib|fulvestrant|nilotinib|pembrolizumab|daratumumab/.test(t))return 'related';
 return best;
}
root.HealthScopePharma={match,label:k=>k==='ingredient'?'Coincidencia farmacológica; marca o presentación por confirmar.':k==='related'?'Coincidencia relacionada; revisar molécula, vía y presentación.':''};
})(globalThis);
