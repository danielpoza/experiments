# Service 1 - Orchestrator

Responsabilidades:
- Recibir imágenes desde la cámara (FTP u otro protocolo de ingesta).
- Subir imágenes a GCS siguiendo la convención de paths.
- Emitir eventos hacia Service 2 (vision-ia).

Implementación inicial:
- VM con vsftpd + watcher en Python.
