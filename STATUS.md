# Estado · HealthScope Chile

**Versión:** V0.3 · **Fecha:** 24-11-2026 · **Zona horaria del proyecto:** America/Santiago

## Despliegue

- Repositorio: https://github.com/selguetagodoy/healthscope
- URL objetivo: https://selguetagodoy.github.io/healthscope/
- Estado comprobado inicialmente: HTTP 503.
- GitHub Pages: sin habilitar. La intervención pendiente es seleccionar **GitHub Actions** en [Settings → Pages](https://github.com/selguetagodoy/healthscope/settings/pages).
- Workflow de despliegue: `.github/workflows/deploy.yml` preparado para validar, compilar y publicar cuando Pages esté configurado.

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

## Próximas tareas

1. Activar la fuente GitHub Actions en Settings → Pages.
2. Ejecutar el workflow de despliegue y comprobar la URL HTTPS sin autenticación.
3. Ejecutar el monitor manualmente y confirmar la consulta de las tres fuentes.
4. Revisar el sitio publicado en escritorio, tablet y teléfono; documentar consola, enlaces y accesibilidad.
5. Ampliar registros legislativos, farmacéuticos y compras a partir de datasets oficiales.
