"""
Definición del grafo

Estructura el flujo de procesamiento mediante un StateGraph
que conecta nodos especializados en diferentes tareas.

FLUJO PRINCIPAL:
1. classify_route → Decide estrategia (RAG/Tools/Both/None)
2. generate_query → Genera query de búsqueda (si RAG)
3. retrieve → Recupera documentos (si RAG)
4. execute_tools → Ejecuta herramientas MCP (si Tools)
5. respond → Genera respuesta final
"""

from langgraph.graph import StateGraph, END

from retrieval_graph.configuration import Configuration
from retrieval_graph.state import InputState, State
from retrieval_graph.nodes import (
    classify_route,
    generate_query,
    retrieve,
    execute_tools,
    respond,
    handle_none_route,
)


#----
# FUNCIONES DE ENRUTAMIENTO CONDICIONAL
#----

def route_after_classification(state: State) -> str:
    """
    Decide el siguiente nodo tras la clasificación.
    
    Lógica:
    - "none" → handle_none (rechazar pregunta)
    - "tool" → execute_tools (solo herramientas)
    - "rag" → generate_query (solo RAG)
    - "both" → generate_query (primero RAG, luego tools)
    
    Args:
        state: Estado actual con route_decision
        
    Returns:
        Nombre del siguiente nodo
    """
    route = state.route_decision
    
    if route == "none":
        return "handle_none"
    elif route == "tool":
        return "execute_tools"
    elif route in ["rag", "both"]:
        return "generate_query"
    else:
        # Fallback seguro
        return "generate_query"


def route_after_retrieve(state: State) -> str:
    """
    Decide si ejecutar tools después de RAG.
    
    Solo ejecuta tools si la decisión fue "both"
    y existen tool_calls pendientes.
    
    Args:
        state: Estado actual con route_decision y tool_calls
        
    Returns:
        Nombre del siguiente nodo
    """
    if state.route_decision == "both" and state.tool_calls:
        return "execute_tools"
    else:
        return "respond"


#----
# CONSTRUCCIÓN DEL GRAFO
#----

# Inicializar builder con schema de estado y configuración
builder = StateGraph(
    State, 
    input_schema=InputState, 
    config_schema=Configuration
)

# Añadir todos los nodos
builder.add_node("classify_route", classify_route)
builder.add_node("generate_query", generate_query)
builder.add_node("retrieve", retrieve)
builder.add_node("execute_tools", execute_tools)
builder.add_node("respond", respond)
builder.add_node("handle_none", handle_none_route)

# Definir punto de entrada
builder.add_edge("__start__", "classify_route")

# Enrutamiento condicional tras clasificación
builder.add_conditional_edges(
    "classify_route",
    route_after_classification,
    {
        "generate_query": "generate_query",
        "execute_tools": "execute_tools",
        "handle_none": "handle_none",
    }
)

# Flujo lineal: query → retrieve
builder.add_edge("generate_query", "retrieve")

# Enrutamiento condicional tras retrieve
builder.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {
        "execute_tools": "execute_tools",
        "respond": "respond",
    }
)

# Flujos finales
builder.add_edge("execute_tools", "respond")
builder.add_edge("handle_none", END)
builder.add_edge("respond", END)

# Compilar el grafo
graph = builder.compile()
graph.name = "RetrievalGraph"