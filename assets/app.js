(function () {
  'use strict';

  var CATEGORY_LABELS = {
    actualidad: 'Actualidad sanitaria',
    legislacion: 'Legislación y regulación',
    farmaceutico: 'Farmacéutico',
    compras: 'Compras públicas',
    acceso: 'Acceso y cobertura',
    datos: 'Datos y presupuesto',
    actores: 'Instituciones',
    investigacion: 'Investigación'
  };
  var PAGE_SIZE = 8;
  var state = { events: [], sources: [], medicines: [], indicators: [], institutions: [], research: [], pending: [], monitoring: null, page: 1, error: false };
  var $ = function (id) { return document.getElementById(id); };
  var normalize = function (value) { return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); };
  var escapeHtml = function (value) { return String(value == null ? '' : value).replace(/[&<>"']/g, function (char) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]; }); };
  var dateLabel = function (value) {
    var d = new Date(value + 'T12:00:00');
    return Number.isNaN(d.getTime()) ? String(value || '') : new Intl.DateTimeFormat('es-CL', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'America/Santiago' }).format(d);
  };
  var safeUrl = function (value) {
    try { var url = new URL(value); return url.protocol === 'https:' ? url.href : ''; } catch (e) { return ''; }
  };
  var sourceLink = function (url, label, cls) {
    var href = safeUrl(url);
    return href ? '<a class="' + (cls || 'text-link') + '" href="' + escapeHtml(href) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(label) + ' <span aria-hidden="true">↗</span></a>' : '';
  };
  var eventSummary = function (event) {
    return [event.title, event.summary, event.implications, event.authority, event.medication, (event.topics || []).join(' ')].join(' ');
  };
  var verifiedEvents = function () { return state.events.filter(function (event) { return event.status === 'Verificado' && safeUrl(event.url); }); };

  function loadJson(path) {
    return fetch('./' + path, { cache: 'no-cache' }).then(function (response) {
      if (!response.ok) throw new Error('No se pudo cargar ' + path);
      return response.json();
    });
  }

  function detailLink(event) { return './fichas/' + encodeURIComponent(event.id) + '/'; }
  function linkedTitle(event) { return '<a class="record-title" href="' + escapeHtml(detailLink(event)) + '">' + escapeHtml(event.title) + '</a>'; }
  function populateCategories() {
    var select = $('category');
    Object.keys(CATEGORY_LABELS).forEach(function (key) {
      if (!state.events.some(function (event) { return event.category === key; })) return;
      var option = document.createElement('option'); option.value = key; option.textContent = CATEGORY_LABELS[key]; select.appendChild(option);
    });
    Array.from(new Set(state.events.map(function(e){return e.authority;}).filter(Boolean))).sort().forEach(function(a){var option=document.createElement('option');option.value=a;option.textContent=a;$('authorityFilter').appendChild(option);});
    var params = new URLSearchParams(location.search); $('query').value = params.get('q') || ''; if (params.has('materia')) select.value = params.get('materia'); if (select.selectedIndex < 0) select.value = ''; 
  }

  function renderEdition() {
    var list = verifiedEvents().slice().sort(function (a, b) { return b.date.localeCompare(a.date); });
    if (!list.length) {
      $('featured').innerHTML = '<div class="feature-body"><span class="brief-meta">FUENTES PRIMARIAS</span><h3>Agenda sanitaria</h3><p>Consulta las fuentes y documentos originales.</p></div>';
      $('briefs').innerHTML = '<p class="empty-state">La agenda editorial se actualizará con decisiones respaldadas por documentos oficiales.</p>';
      $('editionDate').textContent = 'Hechos documentados · fuentes primarias';
      $('eventCountLabel').textContent = 'Sin registros verificados';
      return;
    }
    var lead = list[0];
    $('editionDate').textContent = 'Último hecho documentado · ' + dateLabel(lead.date);
    $('eventCountLabel').textContent = list.length + ' publicaciones verificadas';
    $('featured').innerHTML = '<div class="feature-topline"><span class="brief-meta">' + escapeHtml(CATEGORY_LABELS[lead.category] || lead.category) + '</span><span class="feature-meta">' + dateLabel(lead.date) + '</span></div><div class="feature-visual"><span>HEALTHSCOPE / CHILE</span></div><div class="feature-body"><h3>' + linkedTitle(lead) + '</h3><p>' + escapeHtml(lead.summary) + '</p>' + sourceLink(lead.url, 'Consultar publicación oficial', 'text-link') + '</div>';
    $('briefs').innerHTML = list.slice(1, 5).map(function (event) {
      return '<article class="brief"><span class="brief-meta">' + escapeHtml(CATEGORY_LABELS[event.category] || event.category) + ' · ' + dateLabel(event.date) + '</span><h3>' + linkedTitle(event) + '</h3><p>' + escapeHtml(event.summary) + '</p>' + sourceLink(event.url, 'Fuente oficial', 'text-link') + '</article>';
    }).join('') || '<p class="empty-state">Más novedades verificadas se incorporarán en próximas ediciones.</p>';
  }

  function filteredEvents() {
    var query = normalize($('query').value).trim();
    var from = $('dateFrom').value, to = $('dateTo').value, authority = $('authorityFilter').value;
    var category = $('category').value;
    var sort = $('sortOrder').value;
    return verifiedEvents().filter(function (event) {
      return (!category || event.category === category) && (!authority || event.authority === authority) && (!from || event.date >= from) && (!to || event.date <= to) && (!query || query.split(/\s+/).every(function(token){return normalize(eventSummary(event)).includes(token);}));
    }).sort(function (a, b) { return sort === 'oldest' ? a.date.localeCompare(b.date) : b.date.localeCompare(a.date); });
  }

  function eventRow(event, compact) {
    var cat = CATEGORY_LABELS[event.category] || event.category || 'Salud';
    return '<article class="event-row' + (compact ? ' compact-event' : '') + '"><time class="event-date" datetime="' + escapeHtml(event.date) + '">' + dateLabel(event.date) + '</time><div class="event-content"><span class="event-category">' + escapeHtml(cat) + (event.authority ? ' · ' + escapeHtml(event.authority) : '') + '</span><h3>' + linkedTitle(event) + '</h3><p>' + escapeHtml(event.summary) + '</p>' + (event.implications ? '<p class="event-implication"><strong>Implicancias:</strong> ' + escapeHtml(event.implications) + '</p>' : '') + '<a class="text-link" href="' + escapeHtml(detailLink(event)) + '">Ver ficha →</a></div>' + sourceLink(event.url, 'Fuente primaria', 'event-source') + '</article>';
  }

  function renderResults() {
    var list = filteredEvents();
    var pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    state.page = Math.min(state.page, pages);
    var from = (state.page - 1) * PAGE_SIZE;
    $('radarCount').textContent = list.length + (list.length === 1 ? ' registro verificado' : ' registros verificados');
    $('results').setAttribute('aria-busy', 'false');
    $('results').innerHTML = list.length ? list.slice(from, from + PAGE_SIZE).map(function (event) { return eventRow(event, false); }).join('') : '<div class="empty-state"><strong>' + (state.error ? 'No fue posible cargar el registro' : 'Sin coincidencias') + '</strong><span>' + (state.error ? 'Recarga la página o consulta las fuentes originales.' : 'Prueba otra palabra o materia.') + '</span></div>';
    $('pagination').hidden = list.length <= PAGE_SIZE;
    $('pageLabel').textContent = 'Página ' + state.page + ' de ' + pages;
    $('previousPage').disabled = state.page <= 1;
    $('nextPage').disabled = state.page >= pages;
  }

  function renderMedicines() {
    var q = normalize($('medicineSearch').value);
    var meds = state.medicines.filter(function (med) { return normalize([med.name, med.active_ingredient, med.company, med.event_type, med.summary].join(' ')).includes(q); });
    $('medicineResults').innerHTML = meds.length ? meds.map(function (med) {
      return '<article class="event-row"><time class="event-date" datetime="' + escapeHtml(med.date) + '">' + dateLabel(med.date) + '</time><div class="event-content"><span class="event-category">' + escapeHtml(med.event_type) + '</span><h3>' + escapeHtml(med.name) + '</h3><p>' + escapeHtml(med.summary) + '</p></div>' + sourceLink(med.url, 'Alerta ISP', 'event-source') + '</article>';
    }).join('') : '<div class="empty-state">No hay registros que coincidan con la búsqueda.</div>';
  }

  function renderProcurement() {
    var event = state.events.filter(function (item) { return item.category === 'compras' && item.status === 'Verificado'; }).sort(function (a, b) { return b.date.localeCompare(a.date); })[0];
    if (!event) {
      $('procurementFeature').innerHTML = '<p class="empty-state">Consulta las novedades de compras públicas en Mercado Público y Cenabast.</p>';
      return;
    }
    var potential = event.metric && event.metric.value ? '<div><span class="procurement-number">' + escapeHtml(event.metric.value) + '</span><span class="procurement-unit">' + escapeHtml(event.metric.unit || '') + '</span></div>' : '<div><span class="procurement-number">CENABAST</span><span class="procurement-unit">Abastecimiento público</span></div>';
    $('procurementFeature').innerHTML = potential + '<div><span class="brief-meta" style="color:#f2b27f">' + dateLabel(event.date) + ' · ' + escapeHtml(event.authority) + '</span><h3>' + linkedTitle(event) + '</h3><p>' + escapeHtml(event.summary) + '</p>' + sourceLink(event.url, 'Abrir fuente oficial', 'text-link') + '</div>';
  }

  function renderAccessEvents() {
    var list = verifiedEvents().filter(function (event) { return event.category === 'acceso' || event.category === 'legislacion'; }).slice(0, 2);
    $('accessEvents').innerHTML = list.map(function (event) { return eventRow(event, true); }).join('');
  }

  function renderIndicators() {
    $('indicators').innerHTML = state.indicators.map(function (item) {
      var value = String(item.value) + (item.unit ? ' ' + item.unit : '');
      var status = item.qualification ? '<span class="indicator-meta">' + escapeHtml(item.qualification) + '</span>' : '';
      return '<article class="indicator"><span class="indicator-value">' + escapeHtml(value) + '</span><span class="indicator-label">' + escapeHtml(item.label) + '</span><span class="indicator-meta">' + escapeHtml(item.period || '') + (item.as_of ? ' · ' + escapeHtml(item.as_of) : '') + '</span>' + status + sourceLink(item.url, 'Ver evidencia', 'indicator-link') + '</article>';
    }).join('') || '<p class="empty-state">Consulta las estadísticas en las fuentes oficiales.</p>';
  }

  function renderInstitutions() {
    var q = normalize($('institutionSearch').value);
    var rows = state.institutions.filter(function (item) { return normalize([item.name, item.scope, item.kind].join(' ')).includes(q); });
    $('institutionCount').textContent = rows.length + ' instituciones en el directorio';
    $('institutions').innerHTML = rows.map(function (item) {
      return '<div class="institution-row"><strong>' + escapeHtml(item.name) + '</strong><span>' + escapeHtml(item.scope) + ' · ' + escapeHtml(item.kind) + '</span>' + sourceLink(item.url, 'Sitio oficial', '') + '</div>';
    }).join('') || '<p class="empty-state">No hay instituciones que coincidan con la búsqueda.</p>';
  }

  function renderResearch() {
    $('research').innerHTML = state.research.map(function (item) {
      var href = safeUrl(item.url);
      return href ? '<a class="research-item" href="' + escapeHtml(href) + '" target="_blank" rel="noopener noreferrer"><small>' + escapeHtml(item.kind) + '</small><strong>' + escapeHtml(item.title) + '</strong><span>' + escapeHtml(item.institution) + (item.date ? ' · ' + escapeHtml(item.date) : '') + ' ↗</span></a>' : '';
    }).join('') || '<p class="empty-state">La biblioteca documental se ampliará con fuentes verificables.</p>';
  }

  function renderSources() {
    var q = normalize($('sourceSearch').value);
    var rows = state.sources.filter(function (item) { return normalize([item.name, item.scope, item.kind, item.mode].join(' ')).includes(q); });
    $('sourceCount').textContent = rows.length + ' fuentes en el directorio';
    $('automatedCount').textContent = state.sources.length + ' fuentes';
    $('sources').innerHTML = rows.map(function (item) {
      var mode = item.kind || 'Fuente pública';
      var modeClass = 'mode-tag';
      return '<div class="source-row"><strong>' + escapeHtml(item.name) + '</strong><span>' + escapeHtml(item.scope) + '</span><span class="' + modeClass + '">' + escapeHtml(mode) + '</span>' + sourceLink(item.url, 'Abrir', '') + '</div>';
    }).join('') || '<p class="empty-state">No hay fuentes que coincidan con la búsqueda.</p>';
  }

  function renderMonitoring() {
    var m = state.monitoring || {};
    var d = m.last_success_at ? new Date(m.last_success_at) : null;
    $('lastRun').textContent = d && !Number.isNaN(d.getTime()) ? new Intl.DateTimeFormat('es-CL', {day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',timeZone:'America/Santiago'}).format(d) : '';
  }

  function csvCell(value) {
    var safe = String(value == null ? '' : value).replace(/^[=+\-@\t\r]/, "'$&");
    return '"' + safe.replace(/"/g, '""') + '"';
  }
  function download(name, content, type) {
    var url = URL.createObjectURL(new Blob([content], { type: type }));
    var anchor = document.createElement('a'); anchor.href = url; anchor.download = name; document.body.appendChild(anchor); anchor.click(); anchor.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function exportCsv() {
    var columns = ['date', 'published', 'category', 'authority', 'title', 'summary', 'implications', 'medication', 'status', 'url'];
    var data = filteredEvents();
    download('healthscope-radar.csv', '\ufeff' + [columns.join(','), data.map(function (event) { return columns.map(function (key) { return csvCell(event[key]); }).join(','); }).join('\r\n')].join('\r\n'), 'text/csv;charset=utf-8');
  }
  function exportJson() { download('healthscope-radar.json', JSON.stringify(filteredEvents(), null, 2), 'application/json;charset=utf-8'); }

  function bindEvents() {
    function refresh(){state.page=1;renderResults();}
    $('query').addEventListener('input', refresh);
    $('query').addEventListener('search', refresh);
    $('query').addEventListener('change', refresh);
    ['dateFrom','dateTo','authorityFilter'].forEach(function(id){$(id).addEventListener('change',refresh);});
    $('resetFilters').addEventListener('click',function(){['query','category','dateFrom','dateTo','authorityFilter'].forEach(function(id){$(id).value='';});$('sortOrder').value='newest';refresh();$('query').focus();});
    $('category').addEventListener('change', function () { state.page = 1; renderResults(); });
    $('sortOrder').addEventListener('change', function () { state.page = 1; renderResults(); });
    $('exportCsv').addEventListener('click', exportCsv);
    $('exportJson').addEventListener('click', exportJson);
    $('previousPage').addEventListener('click', function () { state.page = Math.max(1, state.page - 1); renderResults(); });
    $('nextPage').addEventListener('click', function () { state.page += 1; renderResults(); });
    $('medicineSearch').addEventListener('input', renderMedicines);
    $('institutionSearch').addEventListener('input', renderInstitutions);
    $('sourceSearch').addEventListener('input', renderSources);
    document.querySelectorAll('[data-filter]').forEach(function (link) {
      link.addEventListener('click', function () { var select = $('category'); if (select.querySelector('option[value="' + link.dataset.filter + '"]')) select.value = link.dataset.filter; state.page = 1; renderResults(); });
    });
  }

  function renderAll() {
    populateCategories();
    $('dashEvents').textContent=verifiedEvents().length; $('dashSources').textContent=state.sources.length; $('dashMedicines').textContent=state.medicines.length; $('dashPending').textContent='117';
    renderEdition(); renderResults(); renderMedicines(); renderProcurement(); renderAccessEvents(); renderIndicators(); renderInstitutions(); renderResearch(); renderSources(); renderMonitoring();
  }

  bindEvents();
  var datasetPaths=['events.json','data/sources.json','data/medications.json','data/indicators.json','data/institutions.json','data/research.json','data/pending.json','data/monitoring.json'];
  var failed=[];
  Promise.all(datasetPaths.map(function(path){return loadJson(path).catch(function(){failed.push(path);return null;});})).then(function (data) {
    state.error=failed.includes('events.json');
    if(failed.includes('events.json')){$('dataNotice').hidden=false;$('dataNotice').textContent='Consulta el directorio de fuentes.';}
    state.events = Array.isArray(data[0]) ? data[0] : [];
    state.sources = Array.isArray(data[1]) ? data[1] : [];
    state.medicines = Array.isArray(data[2]) ? data[2] : [];
    state.indicators = Array.isArray(data[3]) ? data[3] : [];
    state.institutions = Array.isArray(data[4]) ? data[4] : [];
    state.research = Array.isArray(data[5]) ? data[5] : [];
    state.pending = Array.isArray(data[6]) ? data[6] : [];
    state.monitoring = data[7] || {};
    renderAll();
  }).catch(function () {
    state.error = true;
    state.events = []; state.sources = []; state.medicines = []; state.indicators = []; state.institutions = []; state.research = []; state.pending = [];
    $('results').setAttribute('aria-busy', 'false');
    $('results').innerHTML = '<div class="empty-state"><strong>El registro no está disponible temporalmente</strong><span>Consulta las fuentes oficiales enlazadas en cada observatorio.</span></div>';
    renderAll();
  });
})();
