FROM python:3.12-slim

WORKDIR /app

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache eficiente)
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 👇 IMPORTANTE: copiar MCP SERVER
COPY services/mcp_server ./services/mcp_server

# Copiar código principal
COPY src/ ./src/
COPY pyproject.toml .
COPY langgraph.json .

# Instalar paquete
RUN pip install -e .

# Exponer puerto LangGraph
EXPOSE 8123

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8123/ok || exit 1

# Arranque
CMD ["langgraph", "dev", "--allow-blocking", "--host", "0.0.0.0", "--port", "8123"]