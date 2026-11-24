# HealthScope Chile

Observatorio independiente de inteligencia sanitaria y farmacéutica. HealthScope organiza información pública sobre decisiones sanitarias, medicamentos, compras, cobertura y datos de Chile, con enlaces a las fuentes originales.

**Versión:** 0.4 · **Idioma:** español de Chile · **Arquitectura:** HTML, CSS, JavaScript y JSON estáticos.

## Sitio público

https://selguetagodoy.github.io/healthscope/

GitHub Pages está habilitado con GitHub Actions. El repositorio es público y el sitio se publica desde la rama `main` mediante `.github/workflows/deploy.yml`.

## Funciones disponibles

- Agenda editorial, nueve módulos con rutas independientes y fichas con URL estable generadas durante el build.
- Buscador transversal del radar y filtros por fecha, autoridad y materia.
- Radar con búsqueda, filtro por materia, ordenamiento, paginación y descarga CSV/JSON.
- Vigilancia farmacéutica basada en alertas públicas seleccionadas del ISP.
- Accesos a compras públicas, cobertura GES y Ley Ricarte Soto.
- Indicadores con fecha, calificación y fuente.
- Directorios de instituciones y documentos públicos con filtros.
- Transparencia sobre fuentes automatizadas, cortes y capturas pendientes de revisión.
- Pipelines para seguir MINSAL, Cenabast, DIPRECE e ISP en los cortes locales establecidos; las capturas del ISP quedan identificadas como error mientras su endpoint no complete TLS en GitHub Actions.

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
