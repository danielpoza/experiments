# Integración con GitHub Copilot Chat

Este documento explica cómo conectar GitHub Copilot Chat con la aplicación Foscam a través del servidor MCP (Model Context Protocol).

## ¿Qué es MCP?

MCP (Model Context Protocol) es un protocolo estándar que permite a las aplicaciones exponer herramientas y recursos que pueden ser utilizados por asistentes de IA como GitHub Copilot Chat.

## Arquitectura

El **Service 3 (notifier/MCP)** actúa como servidor MCP, exponiendo:

### Herramientas (Tools)
1. **get_recent_images** - Obtiene imágenes recientes de las cámaras
2. **get_notifications** - Consulta historial de notificaciones
3. **send_notification** - Envía notificaciones manuales
4. **get_camera_status** - Obtiene estado de las cámaras

### Recursos (Resources)
1. **foscam://images/recent** - Lista de imágenes recientes
2. **foscam://notifications/history** - Historial de notificaciones

## Configuración

### 1. Ejecutar el Servidor MCP

El service3-notifier puede ejecutarse en dos modos:

#### Modo FastAPI (Producción)
```bash
cd services/service3-notifier
python -m app.main
```

#### Modo MCP (Para Copilot Chat)
```bash
cd services/service3-notifier
python -m app.main --mcp
```

### 2. Configurar GitHub Copilot Chat

Para conectar Copilot Chat con el servidor MCP, necesitas configurar el servidor en tu archivo de configuración de MCP.

Crea o edita el archivo de configuración de MCP (ubicación depende de tu sistema):

**macOS/Linux**: `~/.config/mcp/servers.json`
**Windows**: `%APPDATA%\mcp\servers.json`

Añade la siguiente configuración:

```json
{
  "mcpServers": {
    "foscam-notifier": {
      "command": "python",
      "args": [
        "-m",
        "app.main",
        "--mcp"
      ],
      "cwd": "/ruta/absoluta/a/services/service3-notifier",
      "env": {
        "PYTHONPATH": "/ruta/absoluta/a/services/service3-notifier"
      }
    }
  }
}
```

### 3. Reiniciar Copilot Chat

Después de configurar el servidor MCP, reinicia tu IDE o aplicación de Copilot Chat para que cargue la nueva configuración.

## Uso desde Copilot Chat

Una vez configurado, puedes interactuar con tu aplicación Foscam desde Copilot Chat:

### Ejemplos de Consultas

1. **Consultar imágenes recientes:**
   ```
   @foscam-notifier ¿Cuáles son las últimas imágenes capturadas?
   ```

2. **Ver estado de cámaras:**
   ```
   @foscam-notifier Muéstrame el estado de todas las cámaras
   ```

3. **Enviar notificación:**
   ```
   @foscam-notifier Envía una notificación de prueba
   ```

4. **Consultar historial:**
   ```
   @foscam-notifier ¿Cuáles son las últimas 5 notificaciones?
   ```

## Desarrollo Local

### Instalar Dependencias

```bash
cd services/service3-notifier
pip install -r requirements.txt
```

### Ejecutar Tests

```bash
# Modo FastAPI
python -m app.main

# Verificar endpoints
curl http://localhost:8080/
curl http://localhost:8080/recent-images
curl http://localhost:8080/notifications
```

### Probar MCP Server

```bash
# Modo MCP
python -m app.main --mcp

# El servidor espera comunicación por stdin/stdout
# según el protocolo MCP
```

## Despliegue en Producción

### Google Cloud Run

El service3 está configurado para desplegarse en Cloud Run:

```bash
# Build
cd services/service3-notifier
docker build -t gcr.io/${PROJECT_ID}/service3-notifier .

# Push
docker push gcr.io/${PROJECT_ID}/service3-notifier

# Deploy
gcloud run deploy service3-notifier \
  --image gcr.io/${PROJECT_ID}/service3-notifier \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated
```

**Nota**: El modo MCP (--mcp) está diseñado para ejecución local con Copilot Chat. En producción, el servicio se ejecuta como API FastAPI.

## Arquitectura del Sistema

```
┌─────────────────┐
│ Cámara Foscam   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Service 1: Orchestrator │
│  - Recibe imágenes      │
│  - Publica a GCS        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Service 2: Vision-IA    │
│  - Procesa imágenes     │
│  - Análisis con IA      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Service 3: Notifier/MCP │◄──── GitHub Copilot Chat
│  - Notificaciones       │      (vía MCP Protocol)
│  - Servidor MCP         │
└─────────────────────────┘
```

## Seguridad

- En producción, configura autenticación para los endpoints
- Usa variables de entorno para credenciales sensibles
- Implementa rate limiting para las herramientas MCP
- Valida todos los inputs del usuario

## Troubleshooting

### El servidor MCP no se conecta

1. Verifica la ruta en `servers.json`
2. Asegúrate de que Python esté en el PATH
3. Revisa los logs de Copilot Chat

### Los endpoints no responden

1. Verifica que el puerto 8080 esté disponible
2. Revisa los logs del servicio
3. Comprueba las variables de entorno

### Errores de dependencias

```bash
pip install --upgrade mcp fastapi uvicorn pydantic httpx
```

## Recursos Adicionales

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
