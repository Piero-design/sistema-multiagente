"""
Script de ingesta de documentos para el RAG.
Lee los PDFs de knowledge_base/ y los vectoriza en ChromaDB.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_BASE = Path(os.getenv("KNOWLEDGE_BASE_DIR", "../knowledge_base"))
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

COLECCIONES = {
    "normativas_iso": KNOWLEDGE_BASE / "normativas" / "iso",
    "normativas_unsa": KNOWLEDGE_BASE / "normativas" / "reglamentos_unsa",
    "politicas_seguridad": KNOWLEDGE_BASE / "politicas" / "seguridad_informacion",
    "politicas_rrhh": KNOWLEDGE_BASE / "politicas" / "rrhh",
    "politicas_formacion": KNOWLEDGE_BASE / "politicas" / "formacion",
    "plantillas": KNOWLEDGE_BASE / "plantillas",
    "faq": KNOWLEDGE_BASE / "faq",
}


def ingestar_coleccion(nombre, carpeta):
    if not carpeta.exists():
        print(f"  Carpeta no existe: {carpeta}")
        return 0

    pdfs = list(carpeta.glob("**/*.pdf"))
    if not pdfs:
        print(f"  No hay PDFs en: {carpeta}")
        return 0

    print(f"\nIngestando coleccion: {nombre}")
    print(f"  Carpeta: {carpeta}")
    print(f"  PDFs encontrados: {len(pdfs)}")

    docs = []
    for pdf in pdfs:
        try:
            loader = PyPDFLoader(str(pdf))
            docs.extend(loader.load())
            print(f"  OK: {pdf.name}")
        except Exception as e:
            print(f"  ERROR en {pdf.name}: {e}")

    if not docs:
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("RAG_CHUNK_SIZE", 1000)),
        chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", 200)),
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"  Chunks creados: {len(chunks)}")

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=nombre,
        persist_directory=CHROMA_DIR,
    )

    print(f"  Coleccion '{nombre}' guardada")
    return len(chunks)


def main():
    print("=" * 60)
    print("  INGESTA DE BASE DE CONOCIMIENTOS - AGENTE UNSA")
    print("=" * 60)

    total = 0
    for nombre, carpeta in COLECCIONES.items():
        total += ingestar_coleccion(nombre, carpeta)

    print("\n" + "=" * 60)
    print(f"  INGESTA COMPLETADA: {total} chunks totales")
    print("=" * 60)


if __name__ == "__main__":
    main()
