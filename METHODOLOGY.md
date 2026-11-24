# Metodología editorial y de datos

## Propósito

HealthScope transforma información pública dispersa en registros consultables y trazables sobre salud, regulación, acceso, medicamentos, compras y financiamiento en Chile.

## Estados

- **Verificado:** título, fecha, institución y enlace fueron contrastados con una fuente primaria.
- **Pendiente de revisión:** captura automatizada que todavía no pasó por revisión editorial.
- **Estimación:** cifra prospectiva atribuida explícitamente a la institución que la comunicó.
- **Agenda:** asunto citado para una comisión o sesión; su inclusión no demuestra deliberación, votación ni aprobación.
- **Implementado:** solo se usa cuando una fuente competente confirma que la medida comenzó a regir o ejecutarse.

## Fechas

`date` registra la fecha del hecho o publicación institucional pertinente. `published` registra la fecha indicada por la fuente. El monitor conserva fecha local de la publicación en `America/Santiago` y hora de captura en el campo `captured_at`.

## Datos e indicadores

Cada cifra debe tener unidad, periodo, fecha de referencia y URL. Las cifras de anuncios institucionales reflejan el alcance de esa comunicación. Las proyecciones no se describen como resultados realizados. Las notificaciones RAM/ESAVI son reportes de sospecha y no acreditan por sí mismas una relación causal.

## Farmacovigilancia y productos

Las alertas del ISP se presentan con el producto y presentación indicados en la publicación oficial. El observatorio inicial es una selección de alertas; no representa la totalidad del registro sanitario ni reemplaza una consulta de ANAMED.

## Comparación de compras

Los precios solo se compararán cuando se encuentren disponibles medicamento, concentración, presentación, unidad, proveedor, institución, periodo, modalidad y monto. Los valores se normalizan antes de calcular precios unitarios y se mantienen separados los datos que no tengan un perímetro comparable.

## Automatización

El workflow consulta el archivo público de alertas ANAMED y los feeds RSS de MINSAL y Cenabast. Se ejecuta como objetivo a las 08:00, 12:00 y 16:30 de lunes a viernes, hora de Santiago. Debido a que GitHub Actions programa en UTC, el monitor valida la zona local antes de descargar fuentes. La disponibilidad y latencia del servicio de Actions pueden desplazar un corte.

Los contenidos recogidos de fuentes oficiales ingresan a revisión. La automatización organiza y compara información pública; el análisis y la publicación editorial siguen siendo decisiones humanas.

## Límites

La disponibilidad de una página no implica que ofrezca una API ni que el conjunto sea exhaustivo. Las conexiones dependen de estabilidad, permisos, formatos y licencias. HealthScope señala cobertura real y mantiene pendiente cualquier recurso cuya extracción no esté validada.
