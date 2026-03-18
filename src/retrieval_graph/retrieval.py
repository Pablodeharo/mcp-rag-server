"""
Gestión de retriev para vector stores.

Proporciona funciones para crear y configurar retrievers
con soporte para Elasticsearch.

CARACTERÍSTICAS:
✔ Filtrado por user_id para multi-tenancy
✔ Context managers asíncronos
✔ Cache de modelos de embeddings
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_elasticsearch import ElasticsearchStore

from retrieval_graph.configuration import IndexConfiguration


#----
# CONSTRUCTORES DE EMBEDDINGS
#---- 

@lru_cache
def make_text_encoder(model: str) -> Embeddings:
    """
    Crea un modelo de embeddings desde string "provider/model".
    
    Usa cache para evitar recargar modelos repetidamente.
    
    Args:
        model: String en formato "provider/model" (ej: "openai/text-embedding-3-small")
        
    Returns:
        Instancia de Embeddings
        
    Raises:
        ValueError: Si el proveedor no está soportado
    
    Proveedores soportados:
    - openai: OpenAIEmbeddings
    - cohere: CohereEmbeddings
    """
    provider, model_name = model.split("/", maxsplit=1)
    
    match provider:
        case "openai":
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(model=model_name)
        case "cohere":
            from langchain_cohere import CohereEmbeddings
            return CohereEmbeddings(model=model_name)  # type: ignore
        case _:
            raise ValueError(f"Proveedor de embeddings no soportado: {provider}")


#----
# ELASTICSEARCH RETRIEVER
#----

@asynccontextmanager
async def make_elastic_retriever(
    configuration: IndexConfiguration,
    embedding_model: Embeddings
) -> AsyncGenerator:
    """
    Crea un retriever de Elasticsearch con filtrado por user_id.
    
    Context manager asíncrono que gestiona el ciclo de vida del retriever.
    
    Args:
        configuration: Configuración con user_id y search_kwargs
        embedding_model: Modelo de embeddings a usar
        
    Yields:
        VectorStoreRetriever configurado
    """
    es_url = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
    index_name = "rag_index"

    # Crear vector store
    vstore = ElasticsearchStore(
        es_url=es_url,
        index_name=index_name,
        embedding=embedding_model
    )

    # Construir search_kwargs con filtro de user
    search_kwargs = configuration.search_kwargs.copy() if configuration.search_kwargs else {}

    if configuration.user_id:
        # Añadir filtro de Elasticsearch para user_id
        search_kwargs.setdefault("filter", [])
        search_kwargs["filter"].append(
            {"term": {"metadata.user_id": configuration.user_id}}
        )
    retriever = vstore.as_retriever(search_kwargs=search_kwargs)
    
    try:
        yield retriever
    finally:

        pass


#----
# RETRIEVER FACTORY
#----

@asynccontextmanager
async def make_retriever(config):
    """
    Crea un retriever basado en la configuración.
    
    Factory principal que selecciona el tipo de retriever según
    configuration.retriever_provider.
    
    Args:
        config: RunnableConfig con configuración del retriever
        
    Yields:
        VectorStoreRetriever configurado
        
    Ejemplos:
        async with make_retriever(config) as retriever:
            docs = await retriever.ainvoke("mi query")
    """
    configuration = IndexConfiguration.from_runnable_config(config)
    embedding_model = make_text_encoder(configuration.embedding_model)

    # Por ahora solo soportamos Elasticsearch
    # Aquí se puede añadir lógica para otros proveedores
    async with make_elastic_retriever(configuration, embedding_model) as retriever:
        yield retriever