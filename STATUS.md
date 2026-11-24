# Estado · HealthScope Chile

**V1.0 · 24-11-2026 · America/Santiago**

- GitHub Pages operativo, V0.4 verificada con HTTP 200 y diez rutas (incluyendo ficha). Workflow 45473374019 exitoso.
- Monitor V0.4: ejecución 45473525744 exitosa; MINSAL, Cenabast y DIPRECE respondieron, ISP continúa con error TLS.
- V0.5: 24 novedades verificadas, 40 fuentes catalogadas, 5 configuradas para monitor automático, 9 indicadores y 20 referencias documentales. Se incorpora el módulo normativo con ocho instrumentos seleccionados.
- El RSS de ChileCompra respondió HTTP 200 en prueba desde Windows; su primer corte desde GitHub Actions está pendiente de verificación.
- Los enlaces a datos del ISP, ChileCompra y DIPRES son accesos oficiales; las bases de registros sanitarios, órdenes de compra y presupuesto aún no se han importado.
- Pendiente: TLS ISP sin desactivar validación, pruebas completas de interacción y móvil, bases transaccionales, series presupuestarias, control de decisiones editoriales.

- V0.6: 117 registros de cobertura extraídos de fichas de la Superintendencia de Salud (90 GES + 27 LRS). Catálogo con filtros, paginación y exportaciones; no equivale a un registro de medicamentos ni de beneficiarios. Despliegue y pruebas de navegador pendientes al momento del commit.

- V0.7: 41 actores institucionales, 14 canales sociales, 20 medios en directorio, 12 fuentes RSS/HTML configuradas. Los siete RSS nuevos devolvieron XML con ítems desde Windows; su ejecución CI está pendiente. LinkedIn/X: directorio manual, cero publicaciones sociales incorporadas. Pendiente incorporar cargos individuales con respaldo oficial.

- V0.8: buscador ORPHA, fuente nacional y resolución identificadas; importador reproducible con validación de 9.784 entidades, huella SHA-256 y exportación. La disponibilidad de la copia local depende del resultado de la importación CI. No se incorporan registros de personas.

- V0.9: muestra ISP de 27 registros, buscador, filtros, exportaciones e importador CSV oficial. Consulta directa vigente: 1.178 resultados, 25 importados; Trikafta: 2 de 2. La exportación Excel desde Playwright no concluyó; la extracción completa sigue pendiente. Despliegue pendiente al momento del commit.

- V1.0: serie BCN 2017–2026 (10 años); 4 nuevos observatorios y recolector de datos públicos para ClinicalTrials.gov, INAPI y ChileCompra. Los recuentos reales se registran tras cada importación; no se afirma cobertura completa sin resultados. Directorio social ampliado a 53 instituciones y 30 canales, ocho publicaciones LinkedIn identificadas editorialmente sin fecha exacta comprobada. API social no autorizada; ISP masivo sigue limitado.

- V1.0 publicada: 2.912 estudios con sede en Chile, 19.614 registros de solicitudes/concesiones farmacéuticas de 36 archivos anuales, compras agosto–octubre 2026 (13.561 líneas en octubre; 10.000 en vista web), 10 años de presupuesto, 53 actores y 30 canales sociales.
- V1.1: briefing semanal público, copia de reporte verificado y pendientes separados, cortes de tres horas hábiles y uno diario fines de semana. Diario Oficial (sumario), Senado y Cámara con estado por fuente. LinkedIn/X sin API autorizada. La generación y publicación de esta revisión se verifican por CI.
