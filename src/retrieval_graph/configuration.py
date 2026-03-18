"""
Configuración del agente

Define parámetros configurables sin instanciar modelos.
La carga real ocurre en nodes.py o utils.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config

from retrieval_graph import prompts
from retrieval_graph.models import ChatModel


#----
# CONFIGURACIÓN DE INDEXADO
#----
@dataclass(kw_only=True)
class IndexConfiguration:
    """
    Configuración para operaciones de indexado y retrieval.
    
    Atributos:
        user_id: Identificador único del usuario (para filtrado)
        embedding_model: Modelo de embeddings (formato: provider/model)
        retriever_provider: Proveedor de vector store (elastic)
        search_kwargs: Parámetros adicionales para búsqueda
    """
    user_id: str = field(
        default="default_user",
        metadata={"description": "Unique identifier for the user."}
    )

    embedding_model: Annotated[
        str,
        {"__template_metadata__": {"kind": "embeddings"}},
    ] = field(
        default="openai/text-embedding-3-small",
        metadata={"description": "Embedding model name."},
    )

    retriever_provider: str = field(
        default="elastic",
        metadata={"description": "Vector store provider."},
    )

    search_kwargs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_runnable_config(
        cls: Type[T],
        config: RunnableConfig | None = None,
    ) -> T:
        """
        Construye configuración desde RunnableConfig de LangGraph.
        
        Extrae valores de config["configurable"] y crea instancia.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}

        _fields = {f.name for f in fields(cls) if f.init}

        return cls(**{k: v for k, v in configurable.items() if k in _fields})


T = TypeVar("T", bound=IndexConfiguration)


#-----
# CONFIGURACIÓN DEL AGENTE
#-----

@dataclass(kw_only=True)
class Configuration(IndexConfiguration):
    """
    Configuración completa del agente conversacional.
    
    Extiende IndexConfiguration con parámetros de modelos y prompts.
    """

    # SELECCIÓN DE MODELOS
    response_model: Annotated[
        ChatModel,
        {"__template_metadata__": {"kind": "llm"}},
    ] = field(
        default=ChatModel.GPT5_BALANCED,
        metadata={"description": "Model used for response generation."},
    )

    query_model: Annotated[
        ChatModel,
        {"__template_metadata__": {"kind": "llm"}},
    ] = field(
        default=ChatModel.GPT5_FAST,
        metadata={"description": "Model used for query rewriting."},
    )

    
    # TEMPERATURA
    response_temperature: float = field(
        default=0.0,
        metadata={"description": "Temperature used for response model."},
    )

    query_temperature: float = field(
        default=0.0,
        metadata={"description": "Temperature used for query model."},
    )


    # PROMPTS DEL SISTEMA
    response_system_prompt: str = field(
        default=prompts.RESPONSE_SYSTEM_PROMPT
    )

    query_system_prompt: str = field(
        default=prompts.QUERY_SYSTEM_PROMPT
    )