# 📘 Cyber Incident RAG Assistant

Sistema RAG avanzado para asistencia en gestión de ciberincidentes, combinando recuperación semántica, orquestación de agentes y herramientas externas mediante **Model Context Protocol (MCP)**.

---

## 🧠 Arquitectura

```text
┌───────────────────────┐
│   Streamlit UI        │
└──────────┬────────────┘
           │ HTTP
┌──────────▼────────────┐
│   RAG Agent           │
│   (LangGraph)         │
│                       │
│   MCP Client          │
└──────────┬────────────┘
           │ STDIO
┌──────────▼────────────┐
│   MCP Server          │
│   (subprocess)        │
│   tools:              │
│   - severity          │
│   - notification      │
│   - csirt             │
└───────────────────────┘
```

---

## 🔥 Características principales

- RAG jerárquico (semántico + estructural)
- Orquestación de agentes con LangGraph
- Integración real con MCP vía STDIO
- Herramientas externas desacopladas
- Elasticsearch como vector store
- Interfaz web con Streamlit

---

## 📦 Gestión de dependencias (Poetry)

Este proyecto utiliza [Poetry](https://python-poetry.org/) para la gestión de dependencias y entornos virtuales.

```bash
# Instalar Poetry
pip install poetry

# Instalar dependencias del proyecto
poetry install

# Activar el entorno virtual
poetry shell
```

---

## 🔌 MCP Server

El sistema incluye un servidor MCP ejecutado como subprocess mediante STDIO (no HTTP).

📄 Documentación técnica completa: [`services/mcp_server/README.md`](services/mcp_server/README.md)

---

## 🚀 Ejecución

### 🐳 Docker (recomendado)

```bash
docker compose up --build
```

### 💻 Desarrollo local con Poetry

**1. Instalar dependencias**

```bash
poetry install
```

**2. Activar entorno**

```bash
poetry shell
```

**3. Ejecutar servicios individualmente**

```bash
# Elasticsearch (Docker)
docker compose up elasticsearch

# LangGraph
langgraph dev --host 0.0.0.0 --port 8123

# Streamlit UI
cd ui
streamlit run streamlit_app.py
```

---

## 🌐 Servicios

| Servicio       | URL                          |
|----------------|------------------------------|
| UI             | http://localhost:8501        |
| LangGraph      | http://localhost:8123        |
| Elasticsearch  | http://localhost:9200        |

---

## ⚙️ Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=your_api_key
LANGSMITH_API_KEY=your_api_key
ELASTICSEARCH_URL=http://elasticsearch:9200
```

---

## 📚 Pipeline RAG

### Nivel 1 — Recuperación Semántica

- Chunking semántico
- Embeddings con `text-embedding-3-small`
- Búsqueda vectorial en Elasticsearch

### Nivel 2 — Contexto Jerárquico

- Reconstrucción del documento completo
- Contexto por secciones
- Citas precisas con metadatos

---

## 📄 Procesamiento de documentos

**Parsing estructural**
- Librería: `unstructured`
- Salida: `structured_sections.json`

**Chunking semántico**
- Salida: `semantic_chunks.json`
- Incluye metadatos jerárquicos

---

## 🧰 Integración con MCP

El agente utiliza MCP para ejecutar herramientas externas en tiempo de inferencia:

- **Clasificación de severidad** del incidente
- **Evaluación regulatoria** (ENS, RGPD, NIS2)
- **Consulta de disponibilidad** de CSIRT

La comunicación se realiza vía STDIO, ejecutando el servidor como subprocess del agente.

### LangGraph — Agent Graph (LangSmith)

> Trazas del grafo de agente capturadas en LangSmith, mostrando los nodos de retrieve, rerank y generate.

![LangGraph Agent Graph](assets/langsmith_graph.png)

<!-- Añade aquí más capturas de LangSmith si las tienes -->

---

## 🏗️ Estructura del proyecto

```
.
├── services/
│   └── mcp_server/       # MCP Server + tools
├── src/
│   └── retrieval_graph/  # LangGraph Agent
├── ui/                   # Streamlit UI
├── assets/               # Capturas y recursos visuales
├── pyproject.toml
└── docker-compose.yml
```

---

## 🧪 Testing con MCP Inspector

```bash
npx @modelcontextprotocol/inspector \
  --command "poetry run python services/mcp_server/server.py"
```

---

## 🧠 Decisiones de diseño

### MCP vía STDIO

| Ventaja | Detalle |
|---|---|
| ✅ Simplicidad | Sin servidor HTTP adicional |
| ✅ Sin red | Ejecución local como subprocess |
| ✅ Compatible con Inspector | Testing y debug visual |
| ✅ Integración directa | El agente controla el ciclo de vida |

### Poetry

| Ventaja | Detalle |
|---|---|
| ✅ Reproducibilidad | `poetry.lock` garantiza versiones exactas |
| ✅ Dependencias limpias | Separación dev/prod |
| ✅ Entornos aislados | Sin conflictos con el sistema |

---

## 🔮 Futuras mejoras

- [ ] MCP sobre HTTP (streamable transport)
- [ ] Autenticación de herramientas MCP
- [ ] Observabilidad avanzada con LangSmith
- [ ] Nuevas tools de ciberseguridad (threat intel, IOC lookup)