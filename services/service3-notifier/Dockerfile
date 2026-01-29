FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Crear usuario no-root para ejecutar la aplicación
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8080

# Comando por defecto (FastAPI server)
CMD ["python", "-m", "app.main"]
