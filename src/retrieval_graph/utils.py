"""
Funciones utilitarias.
---------------------

Funciones auxiliares para procesamiento de mensajes, documentos
y carga de modelos.
"""

from functools import lru_cache

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage

load_dotenv()


#----
# PROCESAMIENTO DE MENSAJES
#----

def get_message_text(msg: AnyMessage) -> str:
    """
    Extrae el texto de un mensaje en cualquier formato.
    
    Soporta:
    - str: "Hola"
    - dict: {"text": "Hola"}
    - list: [{"text": "Ho"}, "la"]
    
    Args:
        msg: Mensaje de LangChain
        
    Returns:
        Texto extraído como string
        
    Examples:
        >>> from langchain_core.messages import HumanMessage
        >>> get_message_text(HumanMessage(content="Hello"))
        'Hello'
        >>> get_message_text(HumanMessage(content=[{"text": "Hello"}, " World"]))
        'Hello World'
    """
    content = msg.content
    
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        # Contenido es una lista de partes
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


#----
# FORMATEO DE DOCUMENTOS
#----

def _format_doc(doc: Document) -> str:
    """
    Formatea un documento individual como XML.
    
    Incluye metadata como atributos XML.
    
    Args:
        doc: Documento a formatear
        
    Returns:
        String XML con el documento
    """
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"


def format_docs(docs: list[Document] | None) -> str:
    """
    Formatea una lista de documentos como XML.
    
    Usado en el nodo `respond` para construir el contexto
    que se envía al modelo.
    
    Args:
        docs: Lista de documentos o None
        
    Returns:
        String XML con todos los documentos
        
    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> print(format_docs(docs))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>
    """
    if not docs:
        return "<documents></documents>"
    
    formatted = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
{formatted}
</documents>"""


# =====================================================================
# CARGA DE MODELOS
# =====================================================================

@lru_cache
def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """
    Carga un modelo de chat desde string "provider/model".
    
    Usa cache para evitar recargar modelos repetidamente.
    
    Args:
        fully_specified_name: String en formato "provider/model"
                              Ej: "openai/gpt-5-nano"
        
    Returns:
        Instancia de BaseChatModel
        
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        # Fallback a OpenAI si no se especifica proveedor
        provider = "openai"
        model = fully_specified_name

    return init_chat_model(model, model_provider=provider)