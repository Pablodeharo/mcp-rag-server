"""
Nodos del grafo.

Define las funciones de cada nodo en el pipeline:
1. classify_route: Clasifica intención del usuario
2. generate_query: Genera query de búsqueda
3. retrieve: Recupera documentos relevantes
4. execute_tools: Ejecuta herramientas MCP
5. respond: Genera respuesta final
6. handle_none_route: Maneja preguntas fuera de ámbito
"""

from datetime import datetime, timezone
from typing import cast

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from retrieval_graph import retrieval
from retrieval_graph.configuration import Configuration
from retrieval_graph.state import State
from retrieval_graph.utils import format_docs, get_message_text, load_chat_model
from retrieval_graph.mcp.client import MCPClient
from retrieval_graph.models import SearchQuery, RouteDecision
from retrieval_graph.prompts import ROUTE_CLASSIFIER_PROMPT


#----
# NODO: CLASIFICACIÓN DE RUTA
#----

async def classify_route(
    state: State, *, config: RunnableConfig
) -> dict:
    """
    Clasifica la intención del usuario y decide la estrategia.
    
    Analiza la pregunta y determina si:
    - Usar RAG (recuperar documentos)
    - Ejecutar tools MCP
    - Usar ambos enfoques
    - Rechazar (fuera de ámbito)
    
    Args:
        state: Estado actual con mensajes
        config: Configuración de ejecución
        
    Returns:
        dict con:
            - route_decision: "rag" | "tool" | "both" | "none"
            - tool_calls: Lista de tools a ejecutar (si decide)
    """
    configuration = Configuration.from_runnable_config(config)
    
    # Construir prompt con el clasificador
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTE_CLASSIFIER_PROMPT),
        ("human", "{question}"),
    ])
    
    # Modelo con temperatura 0 para decisiones deterministas
    model = (
        load_chat_model(configuration.query_model)
        .bind(temperature=0.0)
        .with_structured_output(RouteDecision)
    )
    
    question = get_message_text(state.messages[-1])
    
    # Invocación asíncrona del modelo
    message_value = await prompt.ainvoke({"question": question}, config)
    decision = cast(RouteDecision, await model.ainvoke(message_value, config))
    
    # Log para debugging (útil en desarrollo)
    print(f"[ROUTING] Decision: {decision.route} | Reasoning: {decision.reasoning}")
    
    # Construir lista de tool_calls si es necesario
    tool_calls = []
    if decision.route in ["tool", "both"] and decision.tool_name:
        # Filtrar valores None de los argumentos
        tool_args_dict = {}
        if decision.tool_args:
            tool_args_dict = {
                k: v for k, v in decision.tool_args.model_dump().items() 
                if v is not None
            }
        
        tool_calls.append({
            "name": decision.tool_name,
            "args": tool_args_dict,
        })
    
    return {
        "route_decision": decision.route,
        "tool_calls": tool_calls,
    }


#----
# NODO: GENERACIÓN DE QUERY
#----

async def generate_query(
    state: State, *, config: RunnableConfig
) -> dict[str, list[str]]:
    """
    Genera una query de búsqueda basada en el historial.
    
    - Primera pregunta: Usa el input del usuario directamente
    - Conversaciones siguientes: Usa LLM para refinar la query
      considerando el contexto previo
    
    Args:
        state: Estado actual con mensajes e historial de queries
        config: Configuración de ejecución
        
    Returns:
        dict con 'queries' conteniendo lista de queries generadas
    """
    messages = state.messages
    
    if len(messages) == 1:
        # Primera pregunta del usuario - usar directamente
        human_input = get_message_text(messages[-1])
        return {"queries": [human_input]}
    
    # Mensajes subsiguientes - generar query refinada
    configuration = Configuration.from_runnable_config(config)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", configuration.query_system_prompt),
        ("placeholder", "{messages}"),
    ])
    
    model = (
        load_chat_model(configuration.query_model)
        .bind(temperature=configuration.query_temperature)
        .with_structured_output(SearchQuery)
    )

    message_value = await prompt.ainvoke(
        {
            "messages": state.messages,
            "queries": "\n- ".join(state.queries),
            "system_time": datetime.now(tz=timezone.utc).isoformat(),
        },
        config,
    )
    
    generated = cast(SearchQuery, await model.ainvoke(message_value, config))
    
    return {"queries": [generated.query]}


#----
# NODO: RECUPERACIÓN DE DOCUMENTOS
#----

async def retrieve(
    state: State, *, config: RunnableConfig
) -> dict[str, list[Document]]:
    """
    Recupera documentos relevantes basados en la última query.
    
    Usa el retriever configurado (Elasticsearch) para buscar
    documentos que coincidan con la query más reciente.
    
    Args:
        state: Estado actual con queries
        config: Configuración de ejecución
        
    Returns:
        dict con 'retrieved_docs' conteniendo lista de Documents
    """
    async with retrieval.make_retriever(config) as retriever:
        response = await retriever.ainvoke(state.queries[-1], config)
        return {"retrieved_docs": response}


#----
# NODO: EJECUCIÓN DE HERRAMIENTAS
#----

# nodes.py

async def execute_tools(
    state: State, *, config: RunnableConfig
) -> dict:
    """
    Ejecuta las herramientas MCP marcadas en tool_calls.
    
    Usa context manager para garantizar cierre del cliente
    incluso si hay excepciones.
    """
    if not state.tool_calls:
        return {"tool_results": []}
    
    # Context manager garantiza cierre automático
    async with MCPClient() as mcp_client:
        results = []
        for tool_call in state.tool_calls:
            result = await mcp_client.call_tool(
                tool_name=tool_call["name"],
                arguments=tool_call["args"],
            )
            results.append(result)
            
            # Log para debugging
            print(f"[TOOL] {tool_call['name']} → {result.get('ok', False)}")
    
    # El cliente se cierra automáticamente aquí
    # incluso si hay excepciones dentro del bloque
    
    return {"tool_results": results}

#----
# NODO: GENERACIÓN DE RESPUESTA
#----

async def respond(
    state: State, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """
    Genera respuesta final combinando RAG y resultados de tools.
    """
    configuration = Configuration.from_runnable_config(config)
    
    # Construir contexto dinámico según lo disponible
    context_parts = []
    
    if state.retrieved_docs:
        retrieved_docs = format_docs(state.retrieved_docs)
        # Escapar llaves en los docs
        retrieved_docs_escaped = retrieved_docs.replace("{", "{{").replace("}", "}}")
        context_parts.append(f"DOCUMENTACIÓN RELEVANTE:\n{retrieved_docs_escaped}")
    
    if state.tool_results:
        # Construir texto de tools y escapar llaves
        tools_lines = []
        for r in state.tool_results:
            tool_name = r.get('tool', 'unknown')
            result_data = r.get('result', r.get('error', 'Sin resultado'))
            
            # Convertir dict a string si es necesario
            if isinstance(result_data, dict):
                import json
                result_str = json.dumps(result_data, indent=2, ensure_ascii=False)
            else:
                result_str = str(result_data)
            
            # Escapar llaves en el resultado
            result_str_escaped = result_str.replace("{", "{{").replace("}", "}}")
            tools_lines.append(f"Tool: {tool_name}\nResultado: {result_str_escaped}")
        
        tools_text = "\n\n".join(tools_lines)
        context_parts.append(f"RESULTADOS DE HERRAMIENTAS:\n{tools_text}")
    
    # Unir contexto escapado
    context = "\n\n---\n\n".join(context_parts) if context_parts else "Sin contexto adicional."
    
    # Timestamp actual
    current_time = datetime.now(tz=timezone.utc).isoformat()
    
    # Construir system prompt - el contexto ya tiene llaves escapadas
    system_prompt = f"""{configuration.response_system_prompt}

CONTEXTO DISPONIBLE:
{context}

System time: {current_time}

Usa toda la información anterior para dar una respuesta completa y precisa."""
    
    # Template con placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}"),  # Solo esta variable es válida
    ])
    
    model = load_chat_model(configuration.response_model).bind(
        temperature=configuration.response_temperature
    )

    # Invocar
    message_value = await prompt.ainvoke(
        {"messages": state.messages},
        config,
    )
    
    response = await model.ainvoke(message_value, config)
    
    return {"messages": [response]}

#----
# NODO: MANEJO DE PREGUNTAS FUERA DE ÁMBITO
#----

async def handle_none_route(
    state: State, *, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    """
    Maneja preguntas fuera del ámbito del sistema.
    
    Devuelve un mensaje educado indicando la especialización
    del agente y animando al usuario a hacer preguntas relevantes.
    
    Args:
        state: Estado actual
        config: Configuración de ejecución
        
    Returns:
        dict con 'messages' conteniendo mensaje de rechazo educado
    """
    response = AIMessage(
        content="Lo siento, mi especialidad es la gestión de ciberincidentes.¿Tienes alguna pregunta sobre ese tema?"
    )
    return {"messages": [response]}