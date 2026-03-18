# 🔌 MCP Server — Cyber Incident Tools

Servidor MCP que expone herramientas de ciberseguridad para su uso por agentes LLM mediante **STDIO transport**.

---

## 🧠 ¿Qué es MCP?

**Model Context Protocol (MCP)** es un estándar abierto que permite a modelos de lenguaje interactuar con herramientas externas de forma estructurada y tipada.

En este proyecto:

- El agente LangGraph actúa como **cliente MCP**
- Este servidor expone **tools** de ciberseguridad
- La comunicación se realiza vía **STDIO**

---

## 🏗️ Arquitectura

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

## 🔄 Transporte: STDIO

Este servidor utiliza **Standard Input / Output** como canal de comunicación.

| Característica | Detalle |
|---|---|
| ✅ Sin red | No requiere abrir puertos |
| ✅ Sin exposición | No hay superficie de ataque adicional |
| ✅ Subprocess | El agente controla su ciclo de vida |

---

## 📦 Instalación

Este servicio forma parte del proyecto principal gestionado con Poetry.

```bash
# Desde la raíz del proyecto
poetry install

# Ejecutar el servidor directamente
poetry run python services/mcp_server/server.py
```

---

## 🤝 Handshake MCP

Cuando el cliente se conecta al servidor, se realiza una inicialización automática:

```python
await session.initialize()
```

Este proceso incluye:

1. **Negociación de capacidades** entre cliente y servidor
2. **Descubrimiento de herramientas** disponibles
3. **Validación de schemas** Pydantic de cada tool

---

## 🧰 Tools disponibles

### 1. `severity_classifier`

Clasifica la severidad de un incidente de seguridad a partir de su descripción.

**Salida:** `critical` | `high` | `medium` | `low`

---

### 2. `check_notification`

Evalúa la obligación legal de notificación del incidente según normativa vigente.

**Marcos evaluados:**
- ENS (Esquema Nacional de Seguridad)
- RGPD (Reglamento General de Protección de Datos)
- NIS2

---

### 3. `csirt_status`

Consulta la disponibilidad operativa de los equipos de respuesta a incidentes.

**CSIRTs consultados:**
- CCN-CERT
- INCIBE-CERT
- CSIRT-CV

---

### MCP Inspector — Test de herramientas

> Ejecución manual de las tres tools desde el MCP Inspector, mostrando schemas, inputs y respuestas.

![MCP Inspector — severity_classifier](assets/mcp_inspector_tools.png)

<!-- Si tienes capturas separadas por tool, añádelas aquí -->

---

## 📦 Modelos Pydantic

Todas las tools utilizan modelos Pydantic para:

- **Validación automática** de inputs y outputs
- **Tipado fuerte** en tiempo de ejecución
- **Generación de schemas** compatibles con el protocolo MCP

---

## 🧪 Testing con MCP Inspector

El [MCP Inspector](https://github.com/modelcontextprotocol/inspector) permite probar las herramientas de forma interactiva sin necesidad de un agente.

```bash
npx @modelcontextprotocol/inspector \
  --command "poetry run python services/mcp_server/server.py"
```

**Funcionalidades del Inspector:**

- Listado de tools registradas
- Visualización de schemas de entrada/salida
- Ejecución manual con parámetros personalizados
- Debug de respuestas en tiempo real

---

## 💻 Ejemplo de uso desde el cliente

```python
async with MCPClient() as client:
    result = await client.call_tool(
        "severity_classifier",
        {"description": "Ransomware detectado en sistemas críticos de hospital público"}
    )
    print(result)
    # → {"severity": "critical", "justification": "..."}
```