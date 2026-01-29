# Service 3 - notifier / MCP

Responsabilidades:
- Recibir resultados del Service 2.
- Notificar a dispositivos externos (WhatsApp / otros).
- Exponer interfaz MCP para agentes de IA (GitHub Copilot Chat).

## Características

### API FastAPI
- `POST /process-event` - Procesa eventos de imágenes del Service 2
- `POST /send-notification` - Envía notificaciones manuales
- `GET /notifications` - Consulta historial de notificaciones
- `GET /recent-images` - Obtiene imágenes recientes procesadas
- `GET /` - Estado del servicio

### Servidor MCP
Permite interacción con GitHub Copilot Chat mediante herramientas:
- `get_recent_images` - Consultar imágenes recientes
- `get_notifications` - Ver historial de notificaciones
- `send_notification` - Enviar notificaciones
- `get_camera_status` - Estado de cámaras

Ver `docs/copilot-chat-integration.md` para detalles de configuración.
