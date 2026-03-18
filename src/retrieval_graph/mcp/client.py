"""
Cliente MCP asíncrono para ejecutar herramientas en un MCP Server.

Usa el protocolo MCP oficial (JSON-RPC).
Compatible con FastMCP servers.

"""

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from typing import Any


class MCPClient:
    """
    Cliente MCP asíncrono para invocar tools de un MCP Server.
    """

    def __init__(self, server_command: list[str] | None = None):
        """
        Inicializa el cliente MCP.

        Args:
            server_command: comando para arrancar el MCP server
        """

        self.server_command = server_command or [
            "python",
            "services/mcp_server/server.py"
        ]

        self.session: ClientSession | None = None
        self._client_ctx = None

    async def __aenter__(self):
        """
        Inicia el MCP server y crea la sesión MCP.
        """

        self._client_ctx = stdio_client(self.server_command)
        read, write = await self._client_ctx.__aenter__()

        self.session = ClientSession(read, write)

        await self.session.__aenter__()

        # Handshake MCP
        await self.session.initialize()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)

        if self._client_ctx:
            await self._client_ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tools(self) -> list:
        """
        Obtiene las tools disponibles en el servidor MCP.
        """

        if not self.session:
            raise RuntimeError("MCPClient no inicializado")

        tools = await self.session.list_tools()

        return [tool.name for tool in tools.tools]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict:
        """
        Ejecuta una tool del MCP server.

        Args:
            tool_name: nombre de la tool
            arguments: argumentos de la tool

        Returns:
            dict con resultado
        """

        if not self.session:
            raise RuntimeError("MCPClient no inicializado")

        try:

            result = await self.session.call_tool(
                tool_name,
                arguments
            )

            return {
                "tool": tool_name,
                "ok": True,
                "result": result.content
            }

        except Exception as e:

            return {
                "tool": tool_name,
                "ok": False,
                "error": f"{type(e).__name__}: {str(e)}"
            }