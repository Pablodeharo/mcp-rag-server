"""
Grafo de indexación de documentos.

Expone endpoint para que usuarios indexen documentos en el vector store.

FLUJO:
1. Recibe documentos en IndexState
2. Añade user_id a metadata
3. Los indexa en el retriever configurado
4. Limpia el estado
"""

from typing import Sequence

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph

from retrieval_graph import retrieval
from retrieval_graph.configuration import IndexConfiguration
from retrieval_graph.state import IndexState


#----
# FUNCIONES AUXILIARES
#----

def ensure_docs_have_user_id(
    docs: Sequence[Document], config: RunnableConfig
) -> list[Document]:
    """
    Asegura que todos los documentos tengan user_id en metadata.
    
    Necesario para filtrado por usuario en retrieval multi-tenant.
    
    Args:
        docs: Documentos a procesar
        config: Configuración con user_id
        
    Returns:
        Lista de documentos con metadata actualizada
    """
    user_id = config["configurable"]["user_id"]
    return [
        Document(
            page_content=doc.page_content, 
            metadata={**doc.metadata, "user_id": user_id}
        )
        for doc in docs
    ]


#----
# NODO DE INDEXACIÓN
#----

async def index_docs(
    state: IndexState, *, config: RunnableConfig | None = None
) -> dict[str, str]:
    """
    Indexa documentos en el retriever configurado de forma asíncrona.
    
    Proceso:
    1. Añade user_id a todos los documentos
    2. Los indexa en el vector store
    3. Señaliza borrado del estado
    
    Args:
        state: Estado con documentos a indexar
        config: Configuración del retriever
        
    Returns:
        dict señalizando limpieza de documentos
        
    Raises:
        ValueError: Si no se proporciona configuración
    """
    if not config:
        raise ValueError("Configuration required to run index_docs.")
    
    async with retrieval.make_retriever(config) as retriever:
        stamped_docs = ensure_docs_have_user_id(state.docs, config)
        await retriever.aadd_documents(stamped_docs)
    
    return {"docs": "delete"}


#----
# CONSTRUCCIÓN DEL GRAFO
#----

builder = StateGraph(IndexState, config_schema=IndexConfiguration)
builder.add_node(index_docs)
builder.add_edge("__start__", "index_docs")

# Compilar
graph = builder.compile()
graph.name = "IndexGraph"