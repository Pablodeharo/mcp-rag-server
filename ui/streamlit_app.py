"""
RAG Assistant 
"""

import streamlit as st
from datetime import datetime
import time
import os
from utils import (
    stream_graph,
    extract_response_data,
    format_tool_result,
    format_doc_preview,
)

# Configuración de página
st.set_page_config(
    page_title="Asistente de Ciberincidentes",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PERSONALIZADO 

st.markdown("""
<style>
    /* Reset de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general oscuro */
    .stApp {
        background-color: #1e1e2f;
        color: #e0e0e0;
    }

    /* Contenedor principal centrado con ancho máximo */
    .main .block-container {
        max-width: 900px;
        padding-top: 1rem;
        padding-bottom: 2rem;
        background-color: #1e1e2f;
    }

    /* Sidebar oscuro */
    [data-testid="stSidebar"] {
        background-color: #2d2d3a;
        border-right: 1px solid #3e3e4e;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }

    /* Botón nueva conversación */
    .new-chat-btn {
        background: linear-gradient(135deg, #10a37f 0%, #0d8c6d 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 500;
        width: 100%;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .new-chat-btn:hover {
        background: linear-gradient(135deg, #0d8c6d 0%, #0a7459 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.2);
    }

    /* Items de conversación en sidebar */
    .thread-item {
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 14px;
        border: 1px solid transparent;
        color: #e0e0e0;
    }
    .thread-item:hover {
        background-color: #3a3a4a;
    }
    .thread-item.active {
        background-color: #2a4a4a;
        border-color: #10a37f;
    }

    /* Input de chat oscuro */
    .stChatInput {
        border-radius: 24px !important;
        border: 1px solid #3e3e4e !important;
        background-color: #2d2d3a !important;
        color: #e0e0e0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
        padding: 12px 20px !important;
        font-size: 15px !important;
    }
    .stChatInput:focus {
        border-color: #10a37f !important;
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.2) !important;
    }

    /* Mensajes */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Mensaje del usuario */
    [data-testid="chatMessageUser"] {
        background-color: #2d2d3a;
        border: 1px solid #3e3e4e;
    }

    /* Mensaje del asistente */
    [data-testid="chatMessageAssistant"] {
        background-color: #2a2a3a;
        border: 1px solid #3e3e4e;
    }

    /* Panel de herramientas - estilo moderno oscuro */
    .tools-container {
        background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3a 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid #4a4a6a;
    }
    .tools-header {
        color: #b0b0ff;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .tool-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.2s;
    }
    .tool-item:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    .tool-name {
        color: white;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .tool-status {
        padding: 4px 8px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    .tool-status.success {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    .tool-status.error {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }

    /* Panel de documentos */
    .docs-container {
        background: linear-gradient(135deg, #1a3a4a 0%, #0a2a3a 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid #3a6a7a;
    }
    .docs-header {
        color: #9fc7e0;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .doc-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.2s;
    }
    .doc-item:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    .doc-content {
        color: #e0e0e0;
        font-size: 14px;
        line-height: 1.5;
    }
    .doc-meta {
        color: #a0a0c0;
        font-size: 12px;
        margin-top: 8px;
        display: flex;
        gap: 16px;
    }

    /* Indicador de escritura */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 12px 16px;
        background: #2d2d3a;
        border-radius: 24px;
        width: fit-content;
        margin: 8px 0;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #10a37f;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
        30% { transform: translateY(-8px); opacity: 1; }
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        background: #3a3a4a;
        color: #c0c0e0;
        margin: 2px;
    }
    .badge-primary {
        background: #2a4a4a;
        color: #a0f0e0;
    }

    /* Divider personalizado */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #3e3e4e, transparent);
        margin: 24px 0;
    }

    /* Estilos para texto en sidebar */
    .sidebar-text {
        color: #e0e0e0;
    }

    /* Header minimalista */
    .app-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .app-header h1 {
        font-size: 2.5rem;
        margin: 0;
        color: #10a37f;
    }
    .app-header p {
        color: #a0a0c0;
        font-size: 0.9rem;
        margin: 4px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# INICIALIZACIÓN DE ESTADO
if "threads" not in st.session_state:
    st.session_state.threads = {}

if "current_thread" not in st.session_state:
    thread_id = f"thread_{int(time.time())}"
    st.session_state.threads[thread_id] = {
        "name": "Nueva conversación",
        "created": datetime.now(),
        "messages": [],
        "preview": ""
    }
    st.session_state.current_thread = thread_id

# ----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------------------------------------------
def create_new_thread():
    thread_id = f"thread_{int(time.time())}"
    st.session_state.threads[thread_id] = {
        "name": "Nueva conversación",
        "created": datetime.now(),
        "messages": [],
        "preview": ""
    }
    st.session_state.current_thread = thread_id
    st.rerun()

def delete_thread(thread_id):
    if thread_id in st.session_state.threads and len(st.session_state.threads) > 1:
        del st.session_state.threads[thread_id]
        if st.session_state.current_thread == thread_id:
            st.session_state.current_thread = next(iter(st.session_state.threads.keys()))
        st.rerun()

def update_thread_preview(thread_id):
    thread = st.session_state.threads.get(thread_id, {})
    messages = thread.get("messages", [])
    if messages:
        last_msg = messages[-1]
        content = last_msg["content"]
        thread["preview"] = (content[:50] + "...") if len(content) > 50 else content

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 0;">
        <h2 style="margin: 0; color: #10a37f;">🛡️ Asistente</h2>
        <p style="color: #a0a0c0; font-size: 14px; margin-top: 4px;">RAG Asisted</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ Nueva conversación", use_container_width=True):
        create_new_thread()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Búsqueda
    search = st.text_input("🔍 Buscar conversación", placeholder="Filtrar...", label_visibility="collapsed")

    st.markdown("### 💬 Conversaciones")

    # Ordenar threads
    sorted_threads = sorted(
        st.session_state.threads.items(),
        key=lambda x: x[1]["created"],
        reverse=True
    )

    for thread_id, thread_data in sorted_threads:
        if search and search.lower() not in thread_data["preview"].lower() and search.lower() not in thread_data["name"].lower():
            continue

        is_active = (thread_id == st.session_state.current_thread)
        active_class = "active" if is_active else ""

        date_str = thread_data["created"].strftime("%d/%m/%Y %H:%M" if thread_data["created"].date() == datetime.now().date() else "%d/%m/%Y")
        preview = thread_data["preview"] if thread_data["preview"] else "Conversación nueva"

        col1, col2 = st.columns([20, 1])
        with col1:
            if st.button(
                f"💬 {preview}",
                key=f"thread_{thread_id}",
                use_container_width=True,
                help=f"Creado: {date_str}"
            ):
                st.session_state.current_thread = thread_id
                st.rerun()
        with col2:
            if len(st.session_state.threads) > 1:
                if st.button("🗑️", key=f"delete_{thread_id}", help="Eliminar conversación"):
                    delete_thread(thread_id)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Capacidades
    st.markdown("### 🎯 Normativas")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="badge badge-primary">📚 INCIBE</span>', unsafe_allow_html=True)
        st.markdown('<span class="badge badge-primary">📋 ENS</span>', unsafe_allow_html=True)
        st.markdown('<span class="badge badge-primary">🔒 RGPD</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="badge badge-primary">🏛️ NIS2</span>', unsafe_allow_html=True)
        st.markdown('<span class="badge badge-primary">🚨 CSIRT</span>', unsafe_allow_html=True)
        st.markdown('<span class="badge badge-primary">📢 Notificaciones</span>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Estadísticas
    current_thread_data = st.session_state.threads[st.session_state.current_thread]
    st.markdown(f"""
    <div style="background: #2d2d3a; padding: 16px; border-radius: 12px;">
        <p style="margin: 0; color: #a0a0c0; font-size: 13px;">CONVERSACIÓN ACTUAL</p>
        <p style="margin: 8px 0 0 0; font-weight: 600; color: #e0e0e0;">📊 {len(current_thread_data['messages'])} mensajes</p>
        <p style="margin: 4px 0 0 0; color: #a0a0c0; font-size: 12px;">🆔 {st.session_state.current_thread[:8]}...</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# HEADER PRINCIPAL (solo uno, minimalista)
# ----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1>🛡️</h1>
    <p>Asistente de Ciberincidentes</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# CONTENEDOR DE MENSAJES
# ----------------------------------------------------------------------------
chat_container = st.container()

with chat_container:
    current_thread_data = st.session_state.threads[st.session_state.current_thread]
    messages = current_thread_data["messages"]

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Mostrar tools
            if msg.get("tools"):
                st.markdown("""<div class="tools-container"><div class="tools-header">🔧 Herramientas ejecutadas</div>""", unsafe_allow_html=True)
                for tool in msg["tools"]:
                    formatted = format_tool_result(tool)
                    status_class = "success" if formatted["status"] == "success" else "error"
                    status_icon = "✅" if formatted["status"] == "success" else "❌"

                    st.markdown(f'''
                    <div class="tool-item">
                        <div class="tool-name">
                            {status_icon} {formatted["name"]}
                            <span class="tool-status {status_class}">{formatted["status"].upper()}</span>
                        </div>
                    ''', unsafe_allow_html=True)

                    if formatted["status"] == "success" and formatted["summary"]:
                        for line in formatted["summary"]:
                            st.markdown(f'<div style="color: #c0c0e0; margin-top: 8px;">{line}</div>', unsafe_allow_html=True)
                    elif formatted["status"] == "error" and formatted["error"]:
                        st.markdown(f'<div style="color: #ffb4b4; margin-top: 8px;">⚠️ {formatted["error"]}</div>', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Mostrar documentos
            if msg.get("docs"):
                st.markdown("""<div class="docs-container"><div class="docs-header">📚 Fuentes consultadas</div>""", unsafe_allow_html=True)
                for i, doc in enumerate(msg["docs"][:3], 1):
                    preview = format_doc_preview(doc)
                    st.markdown(f'''
                    <div class="doc-item">
                        <div class="doc-content">
                            <span style="font-weight: 600;">📄 Fuente {i}</span><br>
                            {preview["content"]}
                        </div>
                        <div class="doc-meta">
                            <span>📑 Página {preview["page"]}</span>
                            <span>📁 {preview["source"]}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                if len(msg["docs"]) > 3:
                    st.markdown(f'<div style="color: #a0a0c0; margin-top: 8px;">+ {len(msg["docs"]) - 3} fuentes más</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# INPUT DEL USUARIO
# ----------------------------------------------------------------------------
if prompt := st.chat_input("Pregunta sobre gestión de ciberincidentes..."):
    # Guardar mensaje usuario
    current_thread_data["messages"].append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now()
    })
    update_thread_preview(st.session_state.current_thread)

    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del asistente
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        response_placeholder = st.empty()
        tools_placeholder = st.empty()
        docs_placeholder = st.empty()

        try:
            with status_placeholder.container():
                st.markdown("""
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                """, unsafe_allow_html=True)

            events = []
            for event in stream_graph(prompt, st.session_state.current_thread):
                events.append(event)

            status_placeholder.empty()
            response_data = extract_response_data(events)

            response_placeholder.markdown(response_data["message"])

            if response_data["tools"]:
                with tools_placeholder.container():
                    st.markdown("""<div class="tools-container"><div class="tools-header">🔧 Herramientas ejecutadas</div>""", unsafe_allow_html=True)
                    for tool in response_data["tools"]:
                        formatted = format_tool_result(tool)
                        status_class = "success" if formatted["status"] == "success" else "error"
                        status_icon = "✅" if formatted["status"] == "success" else "❌"
                        st.markdown(f'''
                        <div class="tool-item">
                            <div class="tool-name">
                                {status_icon} {formatted["name"]}
                                <span class="tool-status {status_class}">{formatted["status"].upper()}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                        if formatted["status"] == "success" and formatted["summary"]:
                            for line in formatted["summary"]:
                                st.markdown(f'<div style="color: #c0c0e0; margin-top: 8px;">{line}</div>', unsafe_allow_html=True)
                        elif formatted["status"] == "error" and formatted["error"]:
                            st.markdown(f'<div style="color: #ffb4b4; margin-top: 8px;">⚠️ {formatted["error"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            if response_data["docs"]:
                with docs_placeholder.container():
                    st.markdown("""<div class="docs-container"><div class="docs-header">📚 Fuentes consultadas</div>""", unsafe_allow_html=True)
                    for i, doc in enumerate(response_data["docs"][:3], 1):
                        preview = format_doc_preview(doc)
                        st.markdown(f'''
                        <div class="doc-item">
                            <div class="doc-content">
                                <span style="font-weight: 600;">📄 Fuente {i}</span><br>
                                {preview["content"]}
                            </div>
                            <div class="doc-meta">
                                <span>📑 Página {preview["page"]}</span>
                                <span>📁 {preview["source"]}</span>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    if len(response_data["docs"]) > 3:
                        st.markdown(f'<div style="color: #a0a0c0; margin-top: 8px;">+ {len(response_data["docs"]) - 3} fuentes más</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            # Guardar respuesta
            current_thread_data["messages"].append({
                "role": "assistant",
                "content": response_data["message"],
                "tools": response_data["tools"],
                "docs": response_data["docs"],
                "timestamp": datetime.now()
            })
            update_thread_preview(st.session_state.current_thread)

        except Exception as e:
            status_placeholder.empty()
            response_placeholder.error(f"❌ Error: {str(e)}")
            current_thread_data["messages"].append({
                "role": "assistant",
                "content": f"❌ Error: {str(e)}",
                "timestamp": datetime.now()
            })
