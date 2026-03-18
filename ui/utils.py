import os
import json
from typing import List, Dict, Any, Generator
import requests

LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://rag_agent:8123")
USER_ID = "default_user"

def stream_graph(user_message: str, thread_id: str) -> Generator[dict, None, None]:
    payload = {
        "input": {
            "messages": [{"type": "human", "content": user_message}]
        },
        "config": {
            "configurable": {
                "user_id": USER_ID,
                "thread_id": thread_id
            }
        },
        "stream_mode": "values"
    }
    try:
        response = requests.post(
            f"{LANGGRAPH_URL}/stream",
            json=payload,
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        yield data
                    except json.JSONDecodeError:
                        continue
    except requests.Timeout as e:
        raise TimeoutError("La consulta tardó más de 2 minutos") from e
    except requests.RequestException as e:
        raise ConnectionError(f"Error de conexión: {str(e)}") from e

def extract_response_data(events: List[dict]) -> dict:
    result = {"message": "", "docs": [], "tools": []}
    if not events:
        result["message"] = "No se recibió respuesta del servidor."
        return result
    last_event = events[-1]
    messages = last_event.get("messages", [])
    for msg in reversed(messages):
        if msg.get("type") == "ai":
            result["message"] = msg.get("content", "")
            break
    result["docs"] = last_event.get("retrieved_docs", [])
    result["tools"] = last_event.get("tool_results", [])
    if not result["message"]:
        result["message"] = "Lo siento, no pude procesar tu consulta."
    return result

def format_tool_result(tool: Dict[str, Any]) -> Dict[str, Any]:
    name = tool.get("tool", "unknown")
    ok = tool.get("ok", False)
    result_data = tool.get("result", {})
    error = tool.get("error")
    formatted = {
        "name": name,
        "status": "success" if ok else "error",
        "result": result_data,
        "error": error,
        "summary": []
    }
    if name == "classify_incident":
        formatted["summary"] = [
            f"🎯 Severidad: {result_data.get('severity', 'N/A')}",
            f"📋 Tipo: {result_data.get('incident_type', 'N/A')}"
        ]
    elif name == "check_notification":
        formatted["summary"] = [
            f"📢 Notificación requerida: {'✅ Sí' if result_data.get('notification_required') else '❌ No'}",
            f"🏛️ Autoridades: {', '.join(result_data.get('authorities', ['Ninguna']))}"
        ]
    elif name == "contact_csirt":
        formatted["summary"] = [
            f"📞 Contacto: {result_data.get('contact', 'N/A')}",
            f"⏰ Disponibilidad: {'24/7' if result_data.get('is_available') else 'Horario laboral'}"
        ]
    return formatted

def format_doc_preview(doc: Any, max_length: int = 200) -> dict:
    if isinstance(doc, dict):
        content = doc.get("page_content", "")
        metadata = doc.get("metadata", {})
    else:
        content = getattr(doc, "page_content", str(doc))
        metadata = getattr(doc, "metadata", {})
    preview = content[:max_length] + "..." if len(content) > max_length else content
    return {
        "content": preview,
        "page": metadata.get("page", "N/A"),
        "source": metadata.get("source", "Documento")
    }