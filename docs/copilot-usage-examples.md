# Ejemplo de Uso con GitHub Copilot Chat

Este documento muestra ejemplos prácticos de cómo interactuar con el sistema de cámaras Foscam a través de GitHub Copilot Chat usando el servidor MCP.

## Requisitos Previos

1. Servidor MCP configurado (ver `docs/copilot-chat-integration.md`)
2. GitHub Copilot Chat habilitado en tu IDE

## Ejemplos de Interacción

### 1. Consultar Imágenes Recientes

**Pregunta a Copilot:**
```
Muéstrame las últimas 5 imágenes capturadas por las cámaras
```

**Lo que Copilot hará:**
- Usará la herramienta `get_recent_images` con `limit: 5`
- Mostrará información sobre cada imagen: URI, cámara, timestamp, análisis

### 2. Verificar Estado de Cámaras

**Pregunta a Copilot:**
```
¿Cuál es el estado actual de todas las cámaras?
```

**Lo que Copilot hará:**
- Usará la herramienta `get_camera_status`
- Mostrará para cada cámara:
  - ID de la cámara
  - Última imagen capturada
  - Total de imágenes
  - Número de alertas

### 3. Filtrar por Cámara Específica

**Pregunta a Copilot:**
```
Muéstrame las últimas imágenes de la cámara cam001
```

**Lo que Copilot hará:**
- Usará `get_recent_images` con `camera_id: "cam001"`
- Filtrará solo las imágenes de esa cámara

### 4. Ver Historial de Notificaciones

**Pregunta a Copilot:**
```
¿Cuáles son las últimas notificaciones del sistema?
```

**Lo que Copilot hará:**
- Usará la herramienta `get_notifications`
- Mostrará las notificaciones recientes con timestamps y mensajes

### 5. Enviar Notificación Manual

**Pregunta a Copilot:**
```
Envía una notificación de prueba al sistema
```

**Lo que Copilot hará:**
- Usará `send_notification` con un mensaje apropiado
- Confirmará que la notificación fue enviada

### 6. Análisis y Resúmenes

**Pregunta a Copilot:**
```
¿Ha habido alguna alerta en las últimas horas?
```

**Lo que Copilot hará:**
- Consultará imágenes recientes
- Analizará el campo `analysis.alert`
- Resumirá las alertas encontradas

### 7. Operaciones Combinadas

**Pregunta a Copilot:**
```
Revisa si la cámara cam002 ha detectado movimiento hoy y envíame un resumen
```

**Lo que Copilot hará:**
- Consultará imágenes de cam002
- Analizará las detecciones
- Creará un resumen personalizado

## Herramientas Disponibles

El servidor MCP expone las siguientes herramientas:

### get_recent_images
- **Parámetros:**
  - `limit` (opcional): Número de imágenes (1-100, default: 10)
  - `camera_id` (opcional): Filtrar por cámara específica
- **Retorna:** Lista de imágenes con metadatos y análisis

### get_notifications
- **Parámetros:**
  - `limit` (opcional): Número de notificaciones (1-100, default: 10)
- **Retorna:** Historial de notificaciones

### send_notification
- **Parámetros:**
  - `message` (requerido): Mensaje a enviar
  - `channel` (opcional): Canal (console, whatsapp)
- **Retorna:** Confirmación de envío

### get_camera_status
- **Parámetros:** Ninguno
- **Retorna:** Estado de todas las cámaras

## Recursos MCP

El servidor también expone recursos que Copilot puede leer:

### foscam://images/recent
Acceso completo a todas las imágenes recientes

### foscam://notifications/history
Acceso completo al historial de notificaciones

## Tips de Uso

1. **Sé específico**: Copilot responde mejor a preguntas claras y específicas
2. **Usa lenguaje natural**: No necesitas conocer la API, habla naturalmente
3. **Combina consultas**: Puedes pedir análisis complejos que usen múltiples herramientas
4. **Experimenta**: Copilot puede realizar análisis y correlaciones que no habías pensado

## Ejemplo de Conversación

```
Usuario: ¿Qué cámaras están activas?
Copilot: [Consulta get_camera_status y muestra lista de cámaras]

Usuario: Muéstrame las últimas imágenes de la cámara con más alertas
Copilot: [Analiza estadísticas, identifica cámara, consulta sus imágenes]

Usuario: ¿Hay algún patrón en los horarios de las alertas?
Copilot: [Analiza timestamps y crea un resumen de patrones]

Usuario: Envía una notificación si hay más de 5 alertas
Copilot: [Verifica condición y envía notificación si se cumple]
```

## Notas de Seguridad

- Las herramientas MCP tienen validación de entrada
- Los canales de notificación están restringidos a valores válidos
- Los límites de consulta están acotados (1-100)
- En producción, considera agregar autenticación adicional

## Troubleshooting

### Copilot no encuentra las herramientas

1. Verifica que el servidor MCP esté ejecutándose
2. Revisa la configuración en `servers.json`
3. Reinicia tu IDE/Copilot Chat

### Las consultas no retornan datos

1. Asegúrate de que el servicio tenga datos
2. Prueba los endpoints REST directamente
3. Revisa los logs del servidor MCP

### Errores de validación

1. Verifica que los parámetros estén en rango válido
2. Comprueba que los canales sean válidos (console, whatsapp)
3. Revisa la documentación de esquemas de entrada
