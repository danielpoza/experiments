# Service 3 - Notifier / MCP

Servicio de notificaciones con soporte para MCP (Model Context Protocol) que permite integración con GitHub Copilot Chat.

## Características

### API FastAPI
- Recibe eventos de imágenes procesadas
- Gestiona notificaciones
- Mantiene historial de eventos

### Servidor MCP
- Expone herramientas para interactuar con el sistema desde Copilot Chat
- Proporciona recursos de consulta
- Permite automatización mediante IA

## Inicio Rápido

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar Servidor FastAPI

```bash
# Modo producción (API REST)
python -m app.main
```

El servidor estará disponible en `http://localhost:8080`

### Ejecutar Servidor MCP

```bash
# Modo MCP (para Copilot Chat)
python -m app.main --mcp
```

## Endpoints API

- `GET /` - Estado del servicio
- `POST /process-event` - Procesar evento de imagen
- `POST /send-notification` - Enviar notificación
- `GET /notifications` - Historial de notificaciones
- `GET /recent-images` - Imágenes recientes

## Herramientas MCP

1. **get_recent_images** - Consultar imágenes recientes
2. **get_notifications** - Ver historial de notificaciones  
3. **send_notification** - Enviar notificaciones
4. **get_camera_status** - Estado de cámaras

## Configuración con Copilot Chat

Ver `/docs/copilot-chat-integration.md` para instrucciones completas de configuración.

Archivo de ejemplo: `config/mcp-server-config.example.json`

## Docker

```bash
# Build
docker build -t service3-notifier .

# Run
docker run -p 8080:8080 service3-notifier
```

## Variables de Entorno

- `PORT` - Puerto del servidor (default: 8080)

## Desarrollo

### Estructura

```
service3-notifier/
├── app/
│   └── main.py          # Aplicación principal
├── config/
│   ├── service3.config.yaml
│   └── mcp-server-config.example.json
├── Dockerfile
├── requirements.txt
└── README.md
```

### Testing

```bash
# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/recent-images
curl http://localhost:8080/notifications

# Send notification
curl -X POST http://localhost:8080/send-notification \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "channel": "console"}'
```
