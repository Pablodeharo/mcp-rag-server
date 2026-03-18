"""
Script de ingesta de documentos a Elasticsearch.

Carga chunks semánticos desde JSON y los indexa en Elasticsearch.

USO:
    python ingest_elastic.py [--reindex]

Opciones:
    --reindex   Fuerza la reindexación desde el JSON (crea/reemplaza el índice)
"""

import os
import json
import argparse
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_elasticsearch import ElasticsearchStore
from dotenv import load_dotenv

load_dotenv()

#----
# CONFIGURACIÓN
#----

ES_URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
INDEX_NAME = "rag_index"
# Ruta relativa al script
SEMANTIC_PATH = os.path.join(os.path.dirname(__file__), "data_procesor/semantic_chunks.json")
USER_ID = "default_user"


#----
# FUNCIÓN PRINCIPAL
#----

def run_ingestion(force_reindex: bool = False):
    """
    Ejecuta la ingesta de documentos desde JSON a Elasticsearch.
    
    Args:
        force_reindex (bool): Si True, recrea el índice.
    """
    # Verifica existencia del archivo
    if not os.path.exists(SEMANTIC_PATH):
        print(f"No se encuentra {SEMANTIC_PATH}")
        return

    # Carga chunks
    with open(SEMANTIC_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Construir documentos
    docs = []
    for chunk in chunks:
        metadata = {
            "chunk_id": chunk.get("chunk_id"),
            "page": chunk.get("page"),
            "source": chunk.get("source"),
            "section_title": chunk.get("section_title"),
            "section_id": chunk.get("section_id"),
            "page_start": chunk.get("page_start"),
            "page_end": chunk.get("page_end"),
            "parent_element_id": chunk.get("parent_element_id"),
            "user_id": USER_ID
        }

        docs.append(
            Document(
                page_content=chunk["text"],
                metadata=metadata
            )
        )

    # Crear embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Indexar documentos
    ElasticsearchStore.from_documents(
        documents=docs,
        embedding=embeddings,
        es_url=ES_URL,
        index_name=INDEX_NAME,
        recreate_index=force_reindex   # Esto fuerza reindexado si --reindex
    )

    print(f"{len(docs)} documentos indexados correctamente")


#----
# CLI
#----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexa documentos en Elasticsearch.")
    parser.add_argument("--reindex", action="store_true", help="Forzar reindexación del índice")
    args = parser.parse_args()

    run_ingestion(force_reindex=args.reindex)
