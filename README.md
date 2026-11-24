# HealthScope Chile

Observatorio público independiente de inteligencia sanitaria y farmacéutica. V0.1.

Sitio estático sin dependencias. Activar GitHub Pages: Settings → Pages → Deploy from a branch → main / (root). Prueba local: `python -m http.server 8000`.

`events.json` contiene exclusivamente novedades públicas verificadas. Campos: `date` (fecha del hecho ISO), `published` (fecha de publicación ISO), `category` (legislacion, farmaceutico, compras, acceso, datos, actores), `authority`, `title`, `summary`, `medication`, `status` (Verificado), `url` (HTTPS oficial). Revisar URL y evidencia antes de publicar. El registro inicial está vacío; la captura automática está pendiente.

El proyecto no incorpora información confidencial ni materiales de clientes.
