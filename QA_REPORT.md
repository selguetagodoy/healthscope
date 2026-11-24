# Informe de control de calidad

## Corte inicial · 24-11-2026

- **Estado del sitio público:** la URL de GitHub Pages respondió HTTP 503 durante la revisión inicial.
- **Configuración de Pages:** la API pública devuelve 404 para el recurso Pages y el repositorio reporta `has_pages: false`.
- **Repositorio:** rama principal `main`; acceso de lectura y escritura confirmado por la integración de GitHub.
- **Fuentes automáticas examinadas:** ISP ANAMED, MINSAL RSS y Cenabast RSS respondieron HTTP 200 en la inspección inicial.
- **Datos editoriales:** diez registros iniciales enlazados a fuentes públicas; el conteo se valida con `scripts/validate_data.py`.
- **Suite local:** cuatro pruebas unitarias aprobadas; cubren normalización RSS, captura de alertas ISP, normalización segura de URL y cortes horarios con horario estacional.
- **Integridad de datos:** validación aprobada: 10 novedades, 33 fuentes, 4 alertas farmacéuticas, 4 indicadores, 28 instituciones, 12 documentos/repositorios y 0 capturas pendientes.
- **JavaScript:** comprobación de sintaxis con `node --check assets/app.js` aprobada.
- **Build estático:** compilación local ejecutada con `scripts/build_site.py`; el artefacto incluye portada, datos, marca, estilos y tarjeta Open Graph.
- **GitHub Actions:** el workflow de validación terminó correctamente para la versión V0.3. El workflow de publicación detectó que Pages sigue deshabilitado y omitió los pasos de despliegue.
- **Integración estática:** 58 identificadores HTML, 32 referencias DOM del JavaScript, anclas internas, etiquetas ARIA, recursos locales y breakpoint móvil comprobados; no se encontraron referencias rotas.
- **Responsive, consola y solicitudes HTTP:** pendiente de comprobación en navegador; la URL pública respondió HTTP 503 en la revisión inicial y el despliegue posterior quedó omitido por la configuración de Pages.
- **Ejecución de Playwright:** Chromium no pudo iniciar en el entorno administrado por una restricción de sockets; la sesión del computador Windows tampoco respondió. Por eso no se registran capturas de escritorio o móvil como evidencia de una prueba visual.
- **Accesibilidad y Lighthouse:** no ejecutados; documentarlos después de publicar.

## Alcance de la primera auditoría

La primera versión prioriza rutas, búsqueda, filtros, fuentes y captura sin dependencias externas. El despliegue público requiere configurar Settings → Pages → GitHub Actions en el repositorio. Hasta completar esa configuración no corresponde informar una prueba visual del sitio publicado.
