"""
Gestión de estado del grafo.

Define las estructuras de estado y funciones de reducción usadas en el grafo.
"""

import uuid
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Sequence, Union

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


#----
# ESTADO DE INDEXACIÓN
#----

def reduce_docs(
    existing: Sequence[Document] | None,
    new: Union[
        Sequence[Document],
        Sequence[dict[str, Any]],
        Sequence[str],
        str,
        Literal["delete"],
    ],
) -> Sequence[Document]:
    """
    Reduce y procesa documentos según el tipo de entrada.
    
    Soporta múltiples formatos de entrada:
    - "delete": Limpia todos los documentos
    - str: Crea un documento con ID único
    - list[str]: Crea múltiples documentos
    - list[dict]: Construye Documents desde dicts
    - list[Document]: Usa directamente
    
    Args:
        existing: Documentos actuales en el estado
        new: Nuevos documentos en cualquier formato soportado
        
    Returns:
        Secuencia de Documents procesados
    """
    if new == "delete":
        return []
    
    if isinstance(new, str):
        return [Document(page_content=new, metadata={"id": str(uuid.uuid4())})]
    
    if isinstance(new, list):
        coerced = []
        for item in new:
            if isinstance(item, str):
                coerced.append(
                    Document(page_content=item, metadata={"id": str(uuid.uuid4())})
                )
            elif isinstance(item, dict):
                coerced.append(Document(**item))
            else:
                coerced.append(item)
        return coerced
    
    return existing or []


@dataclass(kw_only=True)
class IndexState:
    """
    Estado para indexación de documentos.
    
    Usado por index_graph para gestionar documentos a indexar.
    """
    docs: Annotated[Sequence[Document], reduce_docs]


#----
# ESTADO DEL AGENTE
#----

@dataclass(kw_only=True)
class InputState:
    """
    Estado de entrada para el agente.
    
    Contiene solo los mensajes del usuario.
    """
    messages: Annotated[Sequence[AnyMessage], add_messages]


def add_queries(existing: Sequence[str], new: Sequence[str]) -> Sequence[str]:
    """
    Combina queries existentes con nuevas queries.
    
    Mantiene historial completo de queries para contexto.
    """
    return list(existing) + list(new)


@dataclass(kw_only=True)
class State(InputState):
    """
    Estado completo del grafo de conversación.
    
    Atributos:
        messages: Historial de mensajes (user + assistant)
        queries: Queries de búsqueda generadas
        retrieved_docs: Documentos recuperados del RAG
        route_decision: Decisión del clasificador ("rag"|"tool"|"both"|"none")
        tool_calls: Tools a ejecutar con sus argumentos
        tool_results: Resultados de ejecución de tools
    """
    
    # ----------------------------------------------------------------
    # CAMPOS RAG
    # ----------------------------------------------------------------
    
    queries: Annotated[list[str], add_queries] = field(default_factory=list)
    """Historial de queries de búsqueda generadas por el agente."""

    retrieved_docs: list[Document] = field(default_factory=list)
    """Documentos recuperados por el retriever."""

    # ----------------------------------------------------------------
    # CAMPOS DE ENRUTAMIENTO
    # ----------------------------------------------------------------
    
    route_decision: Literal["rag", "tool", "both", "none"] | None = None
    """Decisión del clasificador sobre qué ruta seguir."""
    
    # ----------------------------------------------------------------
    # CAMPOS DE EJECUCIÓN DE TOOLS
    # ----------------------------------------------------------------
    
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    """Tools a ejecutar. Formato: [{"name": "tool_name", "args": {...}}]"""
    
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    """Resultados de tools. Formato: [{"tool": "...", "ok": bool, "result": {...}}]"""