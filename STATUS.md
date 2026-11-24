# Estado · HealthScope Chile

**Versión:** V0.3 · **Fecha:** 24-11-2026 · **Zona horaria del proyecto:** America/Santiago

## Despliegue

- Repositorio: https://github.com/selguetagodoy/healthscope
- URL objetivo: https://selguetagodoy.github.io/healthscope/
- Estado comprobado inicialmente: HTTP 503.
- GitHub Pages: sin habilitar. La intervención pendiente es seleccionar **GitHub Actions** en [Settings → Pages](https://github.com/selguetagodoy/healthscope/settings/pages).
- Workflow de despliegue: `.github/workflows/deploy.yml` preparado para validar, compilar y publicar cuando Pages esté configurado.
- Repositorio: versión V0.3 subida a `main` en el commit `e242a8403755617e8571bd1e8c5e129376bfda3d`.
- GitHub Actions: validación aprobada; el workflow de publicación terminó con los pasos de despliegue omitidos porque Pages no está habilitado.

## Funcionalidades incluidas

- Portada editorial y navegación a ocho áreas.
- Agenda, búsqueda, filtros, ordenamiento, paginación y descargas CSV/JSON.
- Alertas farmacéuticas seleccionadas, acceso y cobertura, compras, indicadores, instituciones, documentos y directorio de fuentes.
- Seguimiento automatizado configurado para tres fuentes; las capturas quedan pendientes de revisión editorial.

## Inventario inicial

- Novedades verificadas: 10.
- Fuentes en el directorio: 33.
- Fuentes con consulta automática configurada: 3.
- Alertas farmacéuticas seleccionadas: 4.
- Indicadores con fuente: 4.
- Instituciones: 28.
- Documentos y repositorios: 12.
- Capturas pendientes: 0; el monitor aún no ha realizado su primera ejecución en GitHub Actions.

## Validación

- 4 pruebas unitarias aprobadas.
- Validador de datos aprobado con los conteos anteriores.
- Sintaxis JavaScript aprobada con `node --check`.
- Build estático local generado en `dist/`.
- Prueba visual del navegador pendiente: el Chromium del entorno administrado no pudo abrirse y la sesión de Desktop Commander en Windows expiró.

## Próximas tareas

1. En Settings → Pages, seleccionar **GitHub Actions** como fuente, siguiendo la [guía oficial de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
2. Reejecutar el workflow de publicación y comprobar la URL HTTPS sin autenticación.
3. Ejecutar el monitor manualmente y confirmar la consulta de las tres fuentes.
4. Revisar el sitio publicado en escritorio, tablet y teléfono; documentar consola, enlaces y accesibilidad.
5. Ampliar registros legislativos, farmacéuticos y compras a partir de datasets oficiales.
