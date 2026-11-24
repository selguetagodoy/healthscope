# Estado · HealthScope Chile

**Versión:** V0.4 · **Fecha:** 24-11-2026 · **Zona horaria del proyecto:** America/Santiago

## Despliegue

- Repositorio: https://github.com/selguetagodoy/healthscope
- URL objetivo: https://selguetagodoy.github.io/healthscope/
- GitHub Pages habilitado; HTTP 200 y carga en Chrome comprobados en V0.3.
- Workflow de publicación 45468881497 terminó correctamente.
- V0.4 incorpora módulos independientes, fichas, búsqueda y correcciones del monitor; validación del nuevo despliegue pendiente.

## Funcionalidades incluidas

- Portada editorial y navegación a ocho áreas.
- Agenda, búsqueda, filtros, ordenamiento, paginación y descargas CSV/JSON.
- Alertas farmacéuticas seleccionadas, acceso y cobertura, compras, indicadores, instituciones, documentos y directorio de fuentes.
- Seguimiento automatizado configurado para cuatro fuentes. En el último corte respondieron correctamente MINSAL, Cenabast y DIPRECE; el ISP registró error de verificación TLS en el runner de GitHub.

## Inventario actualizado

- Novedades verificadas: 16.
- Fuentes en el directorio: 33.
- Fuentes con consulta automática configurada: 4.
- Alertas farmacéuticas seleccionadas: 4.
- Indicadores con fuente: 4.
- Instituciones: 28.
- Documentos y repositorios: 12.
- Capturas pendientes de revisión: 11; seis registros fueron verificados y agregados a la agenda. El monitor realizó su primer corte el 24-11-2026 a las 14:25 (America/Santiago).

## Validación

- 4 pruebas unitarias aprobadas.
- Validación de datos CI aprobada tras la curaduría editorial (workflow 45459551239).
- Sintaxis JavaScript aprobada con `node --check`.
- Build estático local generado en `dist/`.
- Auditoría estructural HTML/JS aprobada: anclas internas, referencias DOM, etiquetas ARIA, assets locales y breakpoint móvil.
- V0.3: Chrome cargó la portada, búsquedas de Ricarte Soto y ondansetrón, sin errores de consola; pruebas completas V0.4 pendientes.

## Próximas tareas

1. Verificar despliegue V0.4 y rutas generadas.
2. Probar filtros, exportaciones y móvil.
3. Revisar la cadena TLS del endpoint ISP con una alternativa oficial que conserve la verificación de certificados.
4. Revisar y clasificar las 11 capturas restantes del primer corte sin publicarlas automáticamente como novedades verificadas.
5. Revisar el sitio publicado en escritorio, tablet y teléfono; documentar consola, enlaces y accesibilidad.
