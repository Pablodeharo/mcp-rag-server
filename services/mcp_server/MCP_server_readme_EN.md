# 🔌 MCP Server — Cyber Incident Tools

An MCP server that exposes cybersecurity tools for use by LLM agents via **STDIO transport**.

---

## 🧠 What is MCP?

**Model Context Protocol (MCP)** is an open standard that allows language models to interact with external tools in a structured and strongly typed way.

In this project:

- The LangGraph agent acts as the **MCP client**
- This server exposes **cybersecurity tools**
- Communication happens via **STDIO**

---

## 🏗️ Architecture

```text
MCP Client (LangGraph)
        │
        │ STDIO
        ▼
MCP Server
        │
        ├── severity_classifier
        ├── check_notification
        └── csirt_status
```

---

## 🔄 Transport: STDIO

This server uses **Standard Input / Output** as its communication channel.

| Feature | Details |
|---|---|
| ✅ No network | No ports need to be opened |
| ✅ No exposure | No additional attack surface |
| ✅ Subprocess | The agent controls its lifecycle |

---

## 📦 Installation

This service is part of the main project managed with Poetry.

```bash
# From the project root
poetry install

# Run the server directly
poetry run python services/mcp_server/server.py
```

---

## 🤝 MCP Handshake

When the client connects to the server, an automatic initialization is performed:

```python
await session.initialize()
```

This process includes:

1. **Capability negotiation** between client and server
2. **Tool discovery** — listing available tools
3. **Schema validation** of each tool's Pydantic models

---

## 🧰 Available Tools

### 1. `severity_classifier`

Classifies the severity of a security incident based on its description.

**Output:** `critical` | `high` | `medium` | `low`

---

### 2. `check_notification`

Evaluates the legal obligation to report the incident under applicable regulations.

**Frameworks assessed:**
- ENS (National Security Framework)
- GDPR (General Data Protection Regulation)
- NIS2

---

### 3. `csirt_status`

Checks the operational availability of incident response teams.

**CSIRTs queried:**
- CCN-CERT
- INCIBE-CERT
- CSIRT-CV

---

### MCP Inspector — Tool Testing

> Manual execution of all three tools from the MCP Inspector, showing schemas, inputs, and responses.

![MCP Inspector — Tools](assets/mcp_inspector_tools.png)

<!-- Add separate per-tool screenshots here if available -->

---

## 📦 Pydantic Models

All tools use Pydantic models for:

- **Automatic validation** of inputs and outputs
- **Strong typing** at runtime
- **Schema generation** compatible with the MCP protocol

---

## 🧪 Testing with MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) allows interactive testing of tools without needing a full agent.

```bash
npx @modelcontextprotocol/inspector \
  --command "poetry run python services/mcp_server/server.py"
```

**Inspector features:**

- List all registered tools
- Visualize input/output schemas
- Manually invoke tools with custom parameters
- Real-time response debugging

---

## 💻 Client Usage Example

```python
async with MCPClient() as client:
    result = await client.call_tool(
        "severity_classifier",
        {"description": "Ransomware detected on critical systems of a public hospital"}
    )
    print(result)
    # → {"severity": "critical", "justification": "..."}
```