# mi-sandbox-foscam

Proyecto dividido en 3 servicios:

1. service1-orchestrator: recibe imágenes de la cámara y las publica en GCS / eventos.
2. service2-vision-ia: procesa imágenes (IA / visión).
3. service3-notifier: envía notificaciones (WhatsApp / MCP / otros).

Ver `docs/architecture.md` para el diseño de alto nivel.
