"""
Módulo de Grafo de Recuperación (Retrieval Graph).

Sistema RAG conversacional para gestión de ciberincidentes.

COMPONENTES PRINCIPALES:
- graph: Grafo principal de conversación y recuperación
- index_graph: Grafo para indexación de documentos

CARACTERÍSTICAS:
✔ Gestión de estado conversacional
✔ Generación adaptativa de queries
✔ Integración con Elastic
✔ Modelos configurables para query y respuesta
✔ Ejecución de herramientas MCP

USO:
    from retrieval_graph import graph, index_graph
    
    # Ejecutar conversación
    result = await graph.ainvoke({"messages": [...]}, config)
    
    # Indexar documentos
    await index_graph.ainvoke({"docs": [...]}, config)
"""

from .graph import graph
from .index_graph import graph as index_graph

__all__ = ["graph", "index_graph"]