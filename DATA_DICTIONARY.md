# Diccionario de datos

## `events.json`

| Campo | Descripción |
|---|---|
| `id` | Identificador estable del registro |
| `date` | Fecha del hecho o publicación pertinente en formato `YYYY-MM-DD` |
| `published` | Fecha de publicación indicada por la fuente |
| `category` | Materia editorial: actualidad, legislación, farmacéutico, compras, acceso, datos, actores o investigación |
| `authority` | Organismo o autoridad responsable |
| `title` | Titular factual |
| `summary` | Síntesis de la fuente |
| `implications` | Contexto o alcance documentado, separado del hecho |
| `medication` | Medicamento o materia farmacéutica asociada, si corresponde |
| `topics` | Etiquetas descriptivas |
| `status` | Estado de verificación editorial |
| `source_type` | Tipo de documento o comunicación original |
| `metric` | Valor, unidad y calificación, cuando aplica |
| `url` | Enlace directo HTTPS a la evidencia primaria |

## `data/pending.json`

Usa `source_id`, `authority`, `date`, `published`, `category`, `title`, `summary`, `captured_at`, `status` y `url`. Todos los registros se mantienen como `Pendiente de revisión` hasta que la fuente sea contrastada.

## Otros conjuntos

- `data/sources.json`: directorio de fuentes y configuración del método de seguimiento.
- `data/medications.json`: alertas farmacéuticas seleccionadas; no es un registro sanitario completo.
- `data/indicators.json`: cifras con periodo, fecha de referencia, calificación y evidencia.
- `data/institutions.json`: institución, ámbito de competencia, tipo y sitio oficial.
- `data/research.json`: documento o repositorio, institución, tipo y enlace público.
- `data/monitoring.json`: cortes locales y resultado de la última ejecución.

## Normalización

Las fechas se guardan en ISO 8601. El monitor normaliza URLs HTTPS y elimina parámetros de seguimiento y fragmentos antes de deduplicar. Las unidades monetarias y clínicas deben conservar moneda, unidad y periodo en campos separados cuando se incorporen nuevas series.
