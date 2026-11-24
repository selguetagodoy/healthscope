# HealthScope Chile

Observatorio independiente de inteligencia sanitaria y farmacéutica. HealthScope organiza información pública sobre decisiones sanitarias, medicamentos, compras, cobertura y datos de Chile, con enlaces a las fuentes originales.

**Versión:** 1.1 · **Idioma:** español de Chile · **Arquitectura:** HTML, CSS, JavaScript y JSON estáticos.

## Sitio público

https://selguetagodoy.github.io/healthscope/

GitHub Pages está habilitado con GitHub Actions. El repositorio es público y el sitio se publica desde la rama `main` mediante `.github/workflows/deploy.yml`.

## Funciones disponibles

- Agenda editorial, once módulos con rutas independientes y fichas con URL estable generadas durante el build.
- Buscador transversal del radar y filtros por fecha, autoridad y materia.
- Radar con búsqueda, filtro por materia, ordenamiento, paginación y descarga CSV/JSON.
- Vigilancia farmacéutica basada en alertas públicas seleccionadas del ISP.
- Catálogo consultable y exportable de 90 problemas GES y 27 LRS, con fichas oficiales; tratamientos GES parciales.
- Accesos a compras públicas y registro sanitario.
- Indicadores con fecha, calificación y fuente.
- Directorios de instituciones y documentos públicos con filtros.
- Transparencia sobre fuentes automatizadas, cortes y capturas pendientes de revisión.
- Pipelines para seguir MINSAL, Cenabast, DIPRECE, ChileCompra e ISP en los cortes locales establecidos; las capturas del ISP quedan identificadas como error mientras su endpoint no complete TLS en GitHub Actions.

## Desarrollo local

```bash
python -m http.server 8000
```

Abre `http://localhost:8000/healthscope/` si ejecutas el servidor desde la carpeta superior, o `http://localhost:8000/` si lo ejecutas dentro de este directorio.

## Validación y publicación

```bash
python -m unittest discover -s tests
python scripts/validate_data.py
python scripts/build_site.py
```

Los workflows de GitHub Actions ejecutan estas validaciones y publican el contenido estático. La captura automática crea registros en `data/pending.json`; el estado “Pendiente de revisión” impide que una captura aparezca como noticia verificada.

## Estructura

- `events.json`: agenda editorial revisada.
- `data/`: fuentes, medicamentos, indicadores, instituciones, documentos y estado del monitor.
- `assets/`: marca y estilos originales.
- `scripts/`: captura, validación y preparación de la publicación.
- `tests/`: pruebas del parser de fuentes y de horarios locales.
- `.github/workflows/`: validación, monitoreo y publicación.

## Independencia

HealthScope es un proyecto personal e independiente. Usa información pública y no representa a organismos, empleadores ni clientes. Su contenido no es orientación médica.

- Directorio de stakeholders institucionales, canales sociales enlazados por sitios oficiales y monitor de medios RSS. Publicaciones sociales: registro editorial manual; no se scrapean perfiles.

## Nomenclatura EPOF

`python scripts/import_epof.py` importa el CSV público enlazado por DIPRECE y valida 9.784 códigos únicos antes de generar `data/epof.json`. No se consultan registros personales. La copia es opcional para la compilación; si falta, la interfaz remite al catálogo oficial. La publicación indica el estado real de importación.

## Registro sanitario ISP

Muestra inicial de 27 registros verificados: 2 Trikafta y 25 de la primera página de venta directa vigente (1.178 resultados informados). El importador `scripts/import_isp.py` acepta exportaciones oficiales convertidas a CSV UTF-8, con estado, condición, fecha, criterio y total esperado explícitos. No confundir autorización con cobertura ni disponibilidad.

## V1.0 · Bases estructuradas

Presupuesto BCN 2017–2026, estudios ClinicalTrials.gov con sede Chile, solicitudes y registros INAPI seleccionados por IPC, líneas de órdenes ChileCompra UNSPSC 51. `pip install -r requirements-intelligence.txt` y `python scripts/import_intelligence.py --months 2026-10 2026-09 2026-08`. Los archivos y sus estados se documentan en cada dataset. LinkedIn/X: fuentes y perfiles públicos; publicaciones sociales manuales, sin acceso API autorizado.

## Briefing semanal

La portada y `/semana/` presentan siete días móviles de novedades farmacéuticas verificadas y capturas separadas. Cortes GitHub Actions: 11:17, 14:17, 17:17, 20:17 y 23:17 UTC en días hábiles; 15:17 UTC fines de semana. La hora local cambia con horario estacional. `scripts/weekly_brief.py` consulta ediciones del Diario Oficial, Senado y Cámara y expone fallos. `--offline` recompone la selección con los datos disponibles. No se publica información interna de clientes ni se automatiza la aprobación editorial. Publicaciones sociales sin fecha exacta se muestran por separado.

## Seguimiento gratuito de conversación pública

Prensa ofrece diez búsquedas temáticas de publicaciones indexadas en LinkedIn y X, web y Google Alerts. El directorio ofrece consultas semanales por actor. No se automatizan consultas de Google Search ni se extraen perfiles de redes sociales. Cuatro RSS adicionales (ISP, SOCHICAR, Clínicas de Chile, Colegio de Enfermeras) se integran al corte periódico y al briefing. Google Alerts requiere activar la alerta en la cuenta personal.

## Auditoría y actualización

Búsqueda transversal por registro, páginas independientes, detalle íntegro del último mes de compras, enlaces HTTPS de la ficha original, prestaciones LRS contrastadas individualmente y filtros de estados clínicos y años de patentes. El flujo Refresh public health datasets recupera hasta seis meses faltantes por ejecución (objetivo móvil 60 meses), reconsulta los últimos tres meses y ensayos semanalmente, y actualiza patentes mensualmente. No es garantía de acceso histórico completo: la interfaz muestra solo periodos importados. El comando editorial_review.py permite registrar revisiones de fuentes públicas; el repositorio es público y no admite notas confidenciales. Las publicaciones sociales se consultan en el buscador original, sin API de pago.

La proyección pública de patentes excluye títulos exclusivamente cosméticos mediante una regla textual conservadora y etiqueta usos mixtos. La selección IPC sigue siendo un universo documental, no una certificación de patentes de medicamentos.
