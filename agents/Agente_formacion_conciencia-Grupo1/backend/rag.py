import logging
import math
import hashlib
import json
import sqlite3
from typing import List, Dict, Any, Optional
import httpx
from pathlib import Path

from config import CHROMA_PATH, DB_PATH, OLLAMA_HOST, OLLAMA_EMBED_MODEL

logger = logging.getLogger("rag")

# ==============================================================================
# GENERACIÓN DE EMBEDDINGS RESILIENTE
# ==============================================================================
class ResilientOllamaEmbedding:
    """
    Función de Embeddings con caché en memoria y conexión keep-alive a Ollama (nomic-embed-text).
    """
    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_EMBED_MODEL):
        self.host = host.rstrip("/")
        self.model = model
        self.fallback_dim = 768
        self._cache = {}
        self._client = httpx.Client(timeout=3.0)

    def _fallback_embed(self, text: str) -> List[float]:
        vec = [0.0] * self.fallback_dim
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            slot = h % self.fallback_dim
            vec[slot] += 1.0 / (1.0 + math.log(idx + 1))
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = []
        for text in input:
            text_key = text.strip()
            if text_key in self._cache:
                embeddings.append(self._cache[text_key])
                continue

            emb = None
            try:
                resp = self._client.post(
                    f"{self.host}/api/embeddings",
                    json={"model": self.model, "prompt": text}
                )
                if resp.status_code == 200:
                    emb = resp.json().get("embedding")
            except Exception:
                pass

            if not emb:
                emb = self._fallback_embed(text)

            self._cache[text_key] = emb
            embeddings.append(emb)
        return embeddings

embed_fn = ResilientOllamaEmbedding()

# ==============================================================================
# MOTOR VECTORIAL CHROMA O FALLBACK SQLITE (Para Windows sin C++ Build Tools)
# ==============================================================================
CHROMA_DISPONIBLE = False
try:
    import chromadb
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    col_normas_iso = chroma_client.get_or_create_collection(
        name="normas_iso",
        metadata={"descripcion": "Normas ISO y Regulación Peruana"}
    )
    col_politicas_negocio = chroma_client.get_or_create_collection(
        name="politicas_negocio",
        metadata={"descripcion": "Políticas Internas UNSA"}
    )
    CHROMA_DISPONIBLE = True
    logger.info("ChromaDB nativo inicializado con éxito (Embeddings semánticos ONNX rápidos).")
except Exception as e:
    logger.warning(f"ChromaDB no disponible ({e}). Activando motor vectorial SQLite compatible.")

class SQLiteVectorCollection:
    """
    Emulador de colección vectorial sobre SQLite para entornos Windows
    sin Microsoft Visual C++ Build Tools instalado.
    """
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._init_table()

    def _init_table(self):
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id TEXT PRIMARY KEY,
                document TEXT NOT NULL,
                metadata_json TEXT,
                embedding_json TEXT
            );
            """)
            conn.commit()

    def count(self) -> int:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.execute(f"SELECT count(*) FROM {self.table_name}")
            return cursor.fetchone()[0]

    def add(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        self.upsert(documents, metadatas, ids)

    def upsert(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        embeddings = embed_fn(documents)
        with sqlite3.connect(str(DB_PATH)) as conn:
            for doc_id, doc, meta, emb in zip(ids, documents, metadatas, embeddings):
                conn.execute(
                    f"""
                    INSERT OR REPLACE INTO {self.table_name} (id, document, metadata_json, embedding_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (doc_id, doc, json.dumps(meta, ensure_ascii=False), json.dumps(emb))
                )
            conn.commit()

    def query(self, query_texts: List[str], n_results: int = 5) -> Dict[str, Any]:
        if not query_texts:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        def coseno(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            return dot / (na * nb) if na and nb else 0.0

        query_emb = embed_fn([query_texts[0]])[0]

        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.execute(f"SELECT id, document, metadata_json, embedding_json FROM {self.table_name}")
            rows = cursor.fetchall()

        if not rows:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        scored_docs = []
        for row in rows:
            doc_id, doc, meta_str, emb_str = row
            emb = json.loads(emb_str) if emb_str else []
            sim = coseno(query_emb, emb)
            meta = json.loads(meta_str) if meta_str else {}
            scored_docs.append((sim, doc, meta))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_k = scored_docs[:n_results]

        return {
            "documents": [[r[1] for r in top_k]],
            "metadatas": [[r[2] for r in top_k]],
            "distances": [[1.0 - r[0] for r in top_k]]
        }

if not CHROMA_DISPONIBLE:
    col_normas_iso = SQLiteVectorCollection("rag_normas_iso")
    col_politicas_negocio = SQLiteVectorCollection("rag_politicas_negocio")

# ==============================================================================
# HERRAMIENTAS RAG EXPUESTAS
# ==============================================================================
def buscar_normativa_iso(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    try:
        count = col_normas_iso.count()
        if count == 0:
            return [{"fuente": "Base de Conocimiento", "texto": "Colección normas_iso vacía. Ejecute ingesta.py", "score": 0.0}]

        results = col_normas_iso.query(query_texts=[query], n_results=min(n_results, count))
        docs = []
        if results and "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] else {}
                dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                docs.append({
                    "texto": doc,
                    "fuente": meta.get("fuente", "Normativa ISO / Ley 29733"),
                    "doc_id": meta.get("doc_id", ""),
                    "score": round(1.0 - float(dist), 3)
                })
        return docs
    except Exception as e:
        logger.error(f"Error en RAG ISO: {e}")
        return [{"texto": f"Error consultando RAG ISO: {e}", "fuente": "Error"}]

def buscar_politica_negocio(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    try:
        count = col_politicas_negocio.count()
        if count == 0:
            return [{"fuente": "Base de Conocimiento", "texto": "Colección politicas_negocio vacía. Ejecute ingesta.py", "score": 0.0}]

        results = col_politicas_negocio.query(query_texts=[query], n_results=min(n_results, count))
        docs = []
        if results and "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] else {}
                dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                docs.append({
                    "texto": doc,
                    "fuente": meta.get("fuente", "Política Interna UNSA"),
                    "doc_id": meta.get("doc_id", ""),
                    "score": round(1.0 - float(dist), 3)
                })
        return docs
    except Exception as e:
        logger.error(f"Error en RAG Negocio: {e}")
        return [{"texto": f"Error consultando RAG Negocio: {e}", "fuente": "Error"}]
