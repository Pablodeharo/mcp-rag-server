"""
MCP Server - Cyber Incident Tools (STDIO)
----------------------------------------

Servidor MCP puro usando FastMCP.
- Comunicación: STDIO (no HTTP)
- Compatible con MCP Inspector
- Ideal para integración con agentes (LangGraph)

IMPORTANTE:
Este servidor NO se levanta como API.
Se ejecuta como proceso hijo desde el cliente MCP.
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from tools.incident import incident_severity
from tools.notification import notification_required
from tools.csirt import csirt_availability

# Crear servidor MCP
mcp = FastMCP("cyber-incident-tools")


# -----------------------------
# TOOLS
# -----------------------------

@mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
)
def severity_classifier(description: str):
    """
    Clasifica la severidad de un incidente.

    Args:
        description: descripción libre del incidente
    """
    return incident_severity(description)


@mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
)
def check_notification(
    incident_type: str,
    affected_entity: str,
    data_breach: bool = False
):
    """
    Determina si hay obligación de notificación legal.
    """
    return notification_required(
        incident_type,
        affected_entity,
        data_breach
    )


@mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
)
def csirt_status(csirt_name: str):
    """
    Consulta disponibilidad de un CSIRT.
    """
    return csirt_availability(csirt_name)


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    print("\n🚀 MCP Server (STDIO) iniciado")
    print("Tools disponibles:")
    print("- severity_classifier")
    print("- check_notification")
    print("- csirt_status\n")

    # IMPORTANTE:
    # Esto arranca el servidor MCP en modo STDIO.
    # Se queda escuchando stdin/stdout.
    mcp.run()