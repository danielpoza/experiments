# Arquitectura alto nivel

- Cámara Foscam C2M → Service 1 (orchestrator) → GCS + evento.
- Service 2 (vision-ia) consume eventos / rutas GCS y genera interpretaciones.
- Service 3 (notifier / MCP) recibe resultados y los envía a canales externos.

Convenciones:
- Bucket imágenes: ${BUCKET_IMAGES}
- Path imágenes: gs://${BUCKET_IMAGES}/raw/{camera_id}/{yyyy}/{mm}/{dd}/{timestamp}_{filename}.jpg
