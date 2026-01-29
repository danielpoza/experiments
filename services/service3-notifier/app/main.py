"""
Service 3 - notifier / MCP

FastAPI + MCP Server:
- Recibe eventos del Service 2.
- Envía notificaciones (WhatsApp / otros).
- Expone MCP server para interacción con Copilot Chat.
"""
import os
import json
from datetime import datetime
from typing import Any, Sequence
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Service 3 - Notifier/MCP")

# MCP Server
mcp_server = Server("foscam-notifier")

# Modelos de datos
class ImageEvent(BaseModel):
    """Evento de imagen procesada"""
    image_uri: str = Field(..., description="URI de la imagen en GCS")
    camera_id: str = Field(..., description="ID de la cámara")
    timestamp: str = Field(..., description="Timestamp del evento")
    analysis: dict = Field(default_factory=dict, description="Resultado del análisis de IA")
    
class NotificationRequest(BaseModel):
    """Solicitud de notificación"""
    message: str = Field(..., description="Mensaje a enviar")
    channel: str = Field(default="console", description="Canal de notificación (console, whatsapp)")
    metadata: dict = Field(default_factory=dict, description="Metadatos adicionales")

# Almacenamiento en memoria (en producción usar base de datos)
notifications_history = []
recent_images = []

# ===== ENDPOINTS FASTAPI =====

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": "service3-notifier",
        "status": "running",
        "mcp_enabled": True,
        "endpoints": {
            "process_event": "/process-event",
            "send_notification": "/send-notification",
            "notifications": "/notifications",
            "recent_images": "/recent-images"
        }
    }

@app.post("/process-event")
async def process_event(event: ImageEvent):
    """
    Procesa un evento de imagen del Service 2.
    Almacena la imagen y genera notificaciones si es necesario.
    """
    logger.info(f"Procesando evento: {event.camera_id} - {event.timestamp}")
    
    # Guardar en historial
    recent_images.append(event.model_dump())
    if len(recent_images) > 100:
        recent_images.pop(0)
    
    # Generar notificación si hay análisis relevante
    if event.analysis and event.analysis.get("alert", False):
        notification = {
            "timestamp": datetime.now().isoformat(),
            "message": f"Alerta de cámara {event.camera_id}: {event.analysis.get('description', 'Evento detectado')}",
            "channel": "console",
            "metadata": event.model_dump()
        }
        notifications_history.append(notification)
        logger.info(f"Notificación generada: {notification['message']}")
    
    return {"status": "processed", "event_id": event.timestamp}

@app.post("/send-notification")
async def send_notification(request: NotificationRequest):
    """
    Envía una notificación manual.
    """
    notification = {
        "timestamp": datetime.now().isoformat(),
        "message": request.message,
        "channel": request.channel,
        "metadata": request.metadata
    }
    notifications_history.append(notification)
    logger.info(f"Notificación enviada: {notification}")
    
    return {"status": "sent", "notification": notification}

@app.get("/notifications")
async def get_notifications(limit: int = 10):
    """
    Obtiene el historial de notificaciones.
    """
    return {
        "total": len(notifications_history),
        "notifications": notifications_history[-limit:]
    }

@app.get("/recent-images")
async def get_recent_images(limit: int = 10):
    """
    Obtiene las imágenes recientes procesadas.
    """
    return {
        "total": len(recent_images),
        "images": recent_images[-limit:]
    }

# ===== MCP SERVER TOOLS =====

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Define las herramientas disponibles para Copilot Chat.
    """
    return [
        Tool(
            name="get_recent_images",
            description="Obtiene las imágenes más recientes capturadas por las cámaras Foscam con su análisis de IA",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Número máximo de imágenes a retornar",
                        "default": 10
                    },
                    "camera_id": {
                        "type": "string",
                        "description": "Filtrar por ID de cámara específica (opcional)"
                    }
                }
            }
        ),
        Tool(
            name="get_notifications",
            description="Obtiene el historial de notificaciones enviadas por el sistema",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Número máximo de notificaciones a retornar",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="send_notification",
            description="Envía una notificación manual a través del sistema",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Mensaje de la notificación"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Canal de notificación (console, whatsapp)",
                        "default": "console"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="get_camera_status",
            description="Obtiene el estado actual de las cámaras monitoreadas",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """
    Ejecuta una herramienta solicitada por Copilot Chat.
    """
    try:
        if name == "get_recent_images":
            limit = arguments.get("limit", 10)
            camera_id = arguments.get("camera_id")
            
            images = recent_images[-limit:]
            if camera_id:
                images = [img for img in images if img.get("camera_id") == camera_id]
            
            result = {
                "total": len(images),
                "images": images
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "get_notifications":
            limit = arguments.get("limit", 10)
            
            result = {
                "total": len(notifications_history),
                "notifications": notifications_history[-limit:]
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "send_notification":
            message = arguments.get("message")
            channel = arguments.get("channel", "console")
            
            if not message:
                return [TextContent(
                    type="text",
                    text="Error: Se requiere un mensaje"
                )]
            
            notification = {
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "channel": channel,
                "metadata": {"source": "mcp_tool"}
            }
            notifications_history.append(notification)
            
            return [TextContent(
                type="text",
                text=f"Notificación enviada exitosamente: {json.dumps(notification, indent=2, ensure_ascii=False)}"
            )]
        
        elif name == "get_camera_status":
            # Calcular estado basado en imágenes recientes
            camera_stats = {}
            for img in recent_images:
                cam_id = img.get("camera_id", "unknown")
                if cam_id not in camera_stats:
                    camera_stats[cam_id] = {
                        "camera_id": cam_id,
                        "last_image": img.get("timestamp"),
                        "total_images": 0,
                        "alerts": 0
                    }
                camera_stats[cam_id]["total_images"] += 1
                if img.get("analysis", {}).get("alert", False):
                    camera_stats[cam_id]["alerts"] += 1
            
            result = {
                "cameras": list(camera_stats.values()),
                "total_cameras": len(camera_stats)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Herramienta desconocida: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error ejecutando herramienta {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

# ===== RECURSOS MCP =====

@mcp_server.list_resources()
async def list_resources() -> list[Any]:
    """
    Define los recursos disponibles para Copilot Chat.
    """
    resources = []
    
    # Recurso para imágenes recientes
    resources.append({
        "uri": "foscam://images/recent",
        "name": "Imágenes Recientes",
        "description": "Lista de imágenes recientes capturadas por las cámaras",
        "mimeType": "application/json"
    })
    
    # Recurso para notificaciones
    resources.append({
        "uri": "foscam://notifications/history",
        "name": "Historial de Notificaciones",
        "description": "Historial completo de notificaciones enviadas",
        "mimeType": "application/json"
    })
    
    return resources

@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """
    Lee un recurso solicitado por Copilot Chat.
    """
    if uri == "foscam://images/recent":
        return json.dumps({
            "total": len(recent_images),
            "images": recent_images
        }, indent=2, ensure_ascii=False)
    
    elif uri == "foscam://notifications/history":
        return json.dumps({
            "total": len(notifications_history),
            "notifications": notifications_history
        }, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"Recurso desconocido: {uri}")

# ===== FUNCIÓN PRINCIPAL =====

async def run_mcp_server():
    """
    Ejecuta el servidor MCP usando stdio.
    """
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    import sys
    import asyncio
    
    # Si se ejecuta con --mcp, iniciar servidor MCP
    if "--mcp" in sys.argv:
        asyncio.run(run_mcp_server())
    else:
        # Si no, iniciar servidor FastAPI
        import uvicorn
        port = int(os.getenv("PORT", "8080"))
        uvicorn.run(app, host="0.0.0.0", port=port)
