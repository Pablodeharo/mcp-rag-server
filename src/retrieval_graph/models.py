"""
Definición de modelos de IA y datos del sistema.

PARTE 1: Modelos de LLM y Embeddings
PARTE 2: Modelos de datos Pydantic para el grafo
"""

from enum import Enum
from typing import Optional, Literal

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from retrieval_graph.utils import load_chat_model


#----
# PARTE 1: MODELOS DE IA (LLM y Embeddings)
#----

class ChatModel(str, Enum):
    """
    Modelos de chat soportados.
    
    Formato: provider/model-name
    """
    GPT5_SMART = "openai/gpt-5.2.2025-12-11"
    GPT5_BALANCED = "openai/gpt-5.1"
    GPT5_FAST = "openai/gpt-5-nano"

    @property
    def context_window(self) -> int:
        """Devuelve el tamaño máximo de contexto en tokens."""
        mapping = {
            self.GPT5_SMART: 128000,
            self.GPT5_BALANCED: 64000,
            self.GPT5_FAST: 32000,
        }
        return mapping.get(self, 4096)


class EmbeddingModel(str, Enum):
    """
    Modelos de embeddings soportados.
    """
    OPENAI_SMALL = "openai/text-embedding-3-small"
    OPENAI_ADA = "openai/text-embedding-ada-002"

    @property
    def dimensions(self) -> int:
        """
        Devuelve la dimensionalidad del vector.
        """
        mapping = {
            self.OPENAI_SMALL: 1536,
            self.OPENAI_ADA: 1536,
        }
        return mapping.get(self, 0)



#----
# MODELOS DE DATOS PYDANTIC (para el graph)
#----

class SearchQuery(BaseModel):
    """
    Query de búsqueda generada para el retriever.
    
    Se usa en el nodo `generate_query` para estructurar
    la consulta que se enviará al sistema RAG.
    """
    query: str


class ToolArguments(BaseModel):
    """
    Argumentos flexibles para herramientas del MCP server.
    
    Cada campo es opcional y se mapea a diferentes tools:
    - severity_classifier: usa `description`
    - check_notification: usa `incident_type`, `affected_entity`, `data_breach`
    - csirt_status: usa `csirt_name`
    
    IMPORTANTE: Se filtran valores None antes de enviar al MCP.
    """
    # Para severity_classifier
    description: str | None = None
    
    # Para check_notification
    incident_type: str | None = None
    affected_entity: str | None = None
    data_breach: bool | None = None
    
    # Para csirt_status
    csirt_name: str | None = None

    class Config:
        extra = "forbid"  # No permite campos no declarados


class RouteDecision(BaseModel):
    """
    Decisión de enrutamiento del clasificador.
    
    Determina qué estrategia usar para responder:
    - "rag": Solo recuperación de documentos
    - "tool": Solo ejecución de herramientas MCP
    - "both": RAG + Tools (secuencial)
    - "none": Pregunta fuera de ámbito
    
    Atributos:
        route: Estrategia seleccionada
        reasoning: Explicación de la decisión (para debugging)
        tool_name: Nombre de la tool a ejecutar (si aplica)
        tool_args: Argumentos para la tool (si aplica)
    """
    route: Literal["rag", "tool", "both", "none"]
    reasoning: str
    tool_name: str | None = None
    tool_args: ToolArguments | None = None
    
    class Config:
        extra = "forbid"