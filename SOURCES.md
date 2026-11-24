# Política de fuentes

## Fuentes primarias

HealthScope prioriza publicaciones, tablas, normas y conjuntos de datos de organismos responsables. El directorio clasifica las fuentes por materia y distingue las consultadas directamente de las capturadas por un proceso programado.

## Fuentes monitorizadas

| Fuente | Método | URL consultada | Uso |
|---|---|---|---|
| ISP · alertas ANAMED | Tabla HTML pública | https://www.ispch.gob.cl/categorias-alertas/anamed/ | Alertas de seguridad, retiros y productos sin registro; el runner registra error TLS |
| MINSAL | Feed RSS público | https://www.minsal.cl/feed/ | Comunicados y noticias del Ministerio |
| Cenabast | Feed RSS público | https://www.cenabast.cl/feed/ | Abastecimiento, compras y actividad institucional |
| DIPRECE | Feed RSS público | https://diprece.minsal.cl/feed/ | Prevención, prestaciones, guías y programas sanitarios |

El monitor realizó su primer corte real el 24 de noviembre de 2026. En el último corte registrado, MINSAL, Cenabast y DIPRECE respondieron con HTTP 200; el endpoint de alertas del ISP falló la verificación de su certificado TLS en el runner de GitHub. La verificación TLS permanece activa.

## Registro editorial

Cada novedad confirmada debe conservar título, fecha del hecho, fecha de publicación, institución, clasificación, síntesis, implicancias y una URL primaria HTTPS. Si una fuente solo informa una previsión, el registro la identifica como estimación. Si una agenda incluye un proyecto, la ficha evita presentar esa inclusión como aprobación.

## Capturas automáticas

El monitor guarda títulos, fechas, extractos y enlaces en `data/pending.json`. Las capturas se etiquetan **Pendiente de revisión** y quedan fuera de la agenda verificada. La revisión editorial compara el registro con la fuente original, corrige su clasificación y decide si se incorpora a `events.json`.

## Uso de información

Se utilizan recursos de acceso público sin eludir controles. No se publica información confidencial, credenciales ni datos personales ajenos a funciones profesionales e institucionales. Los datos de notificación farmacovigilante se describen como sospechas y no se interpretan como causalidad clínica.
