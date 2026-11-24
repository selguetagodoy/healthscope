# Estado · HealthScope Chile

**Versión:** V0.3 · **Fecha:** 24-11-2026 · **Zona horaria del proyecto:** America/Santiago

## Despliegue

- Repositorio: https://github.com/selguetagodoy/healthscope
- URL objetivo: https://selguetagodoy.github.io/healthscope/
- Estado comprobado inicialmente: HTTP 503.
- GitHub Pages: sin habilitar. La intervención pendiente es seleccionar **GitHub Actions** en [Settings → Pages](https://github.com/selguetagodoy/healthscope/settings/pages).
- Workflow de despliegue: `.github/workflows/deploy.yml` preparado para validar, compilar y publicar cuando Pages esté configurado.
- Repositorio: V0.3 y sus correcciones están en la rama `main`.
- GitHub Actions: validación aprobada; el workflow de publicación terminó con los pasos de despliegue omitidos porque Pages no está habilitado.

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
- Validador de datos y pruebas CI de esta actualización: resultado por confirmar.
- Sintaxis JavaScript aprobada con `node --check`.
- Build estático local generado en `dist/`.
- Auditoría estructural HTML/JS aprobada: anclas internas, referencias DOM, etiquetas ARIA, assets locales y breakpoint móvil.
- Prueba visual del navegador pendiente: el Chromium del entorno administrado no pudo abrirse y la sesión de Desktop Commander en Windows expiró.

## Próximas tareas

1. En Settings → Pages, seleccionar **GitHub Actions** como fuente, siguiendo la [guía oficial de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
2. Reejecutar el workflow de publicación y comprobar la URL HTTPS sin autenticación.
3. Revisar la cadena TLS del endpoint ISP con una alternativa oficial que conserve la verificación de certificados.
4. Revisar y clasificar las 11 capturas restantes del primer corte sin publicarlas automáticamente como novedades verificadas.
5. Revisar el sitio publicado en escritorio, tablet y teléfono; documentar consola, enlaces y accesibilidad.
