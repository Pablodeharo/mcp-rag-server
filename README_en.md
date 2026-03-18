# 📘 Cyber Incident RAG Assistant

An advanced RAG system for cyber incident management, combining semantic retrieval, agent orchestration, and external tools via **Model Context Protocol (MCP)**.

---

## 🧠 Architecture

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

## 🔥 Key Features

- Hierarchical RAG (semantic + structural)
- Agent orchestration with LangGraph
- Native MCP integration via STDIO
- Decoupled external tools
- Elasticsearch as vector store
- Web interface with Streamlit

---

## 📦 Dependency Management (Poetry)

This project uses [Poetry](https://python-poetry.org/) for dependency management and virtual environments.

```bash
# Install Poetry
pip install poetry

# Install project dependencies
poetry install

# Activate virtual environment
poetry shell
```

---

## 🔌 MCP Server

The system includes an MCP server running as a subprocess over STDIO (not HTTP).

📄 Full technical documentation: [`services/mcp_server/README.md`](services/mcp_server/README.md)

---

## 🚀 Running the Project

### 🐳 Docker (recommended)

```bash
docker compose up --build
```

### 💻 Local development with Poetry

**1. Install dependencies**

```bash
poetry install
```

**2. Activate environment**

```bash
poetry shell
```

**3. Run services individually**

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

## 🌐 Services

| Service        | URL                          |
|----------------|------------------------------|
| UI             | http://localhost:8501        |
| LangGraph      | http://localhost:8123        |
| Elasticsearch  | http://localhost:9200        |

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key
LANGSMITH_API_KEY=your_api_key
ELASTICSEARCH_URL=http://elasticsearch:9200
```

---

## 📚 RAG Pipeline

### Level 1 — Semantic Retrieval

- Semantic chunking
- Embeddings with `text-embedding-3-small`
- Vector search in Elasticsearch

### Level 2 — Hierarchical Context

- Full document reconstruction
- Section-level context
- Precise citations with metadata

---

## 📄 Document Processing

**Structural parsing**
- Library: `unstructured`
- Output: `structured_sections.json`

**Semantic chunking**
- Output: `semantic_chunks.json`
- Includes hierarchical metadata

---

## 🧰 MCP Integration

The agent uses MCP to invoke external tools at inference time:

- **Severity classification** of the incident
- **Regulatory assessment** (ENS, GDPR, NIS2)
- **CSIRT availability** lookup

Communication happens via STDIO, with the server running as a subprocess of the agent.

### LangGraph — Agent Graph (LangSmith)

> Agent graph traces captured in LangSmith, showing the retrieve, rerank, and generate nodes.

![LangGraph Agent Graph](assets/langsmith_graph.png)

<!-- Add additional LangSmith screenshots here if available -->

---

## 🏗️ Project Structure

```
.
├── services/
│   └── mcp_server/       # MCP Server + tools
├── src/
│   └── retrieval_graph/  # LangGraph Agent
├── ui/                   # Streamlit UI
├── assets/               # Screenshots and visual assets
├── pyproject.toml
└── docker-compose.yml
```

---

## 🧪 Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector \
  --command "poetry run python services/mcp_server/server.py"
```

---

## 🧠 Design Decisions

### MCP via STDIO

| Advantage | Details |
|---|---|
| ✅ Simplicity | No additional HTTP server needed |
| ✅ No network | Runs locally as a subprocess |
| ✅ Inspector-compatible | Visual testing and debugging |
| ✅ Direct integration | The agent controls the lifecycle |

### Poetry

| Advantage | Details |
|---|---|
| ✅ Reproducibility | `poetry.lock` guarantees exact versions |
| ✅ Clean dependencies | dev/prod separation |
| ✅ Isolated environments | No system-level conflicts |

---

## 🔮 Future Improvements

- [ ] MCP over HTTP (streamable transport)
- [ ] MCP tool authentication
- [ ] Advanced observability with LangSmith
- [ ] New cybersecurity tools (threat intel, IOC lookup)