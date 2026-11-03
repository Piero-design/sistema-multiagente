"""Recuperación híbrida: BM25 + embeddings densos con fusión por rangos (RRF), y CLI.

Uso (desde backend/):
    python -m dsar.rag.retrieve --query "identidad pendiente" --top-k 3 [--json] [--method auto]
    python -m dsar.rag.retrieve --download-model
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dsar.paths import display_path
from dsar.rag import dense
from dsar.rag.corpus import DEFAULT_CORPUS
from dsar.rag.dense import DenseUnavailable
from dsar.rag.relevance import annotate
from dsar.rag.lexical import (
    LEXICAL_DEFAULT,
    LEXICAL_MODEL_NAME,
    LEXICAL_VARIANTS,
    TFIDF_MODEL_NAME,
    format_hit,
    lexical_search,
    tfidf_model,
    tfidf_search,
)
from dsar.rag.store import DEFAULT_STORE, dense_vectors, file_sha256, load_index, store_paths

RRF_K = 60
CANDIDATES = 20
DEFAULT_METHOD = "auto"  # hybrid si hay modelo denso; si no, BM25 con el motivo registrado
METHODS = ("auto", "tfidf", *LEXICAL_VARIANTS, "dense", "hybrid")
METHOD_LABELS = {
    "tfidf": "Busqueda vectorial TF-IDF con similitud coseno",
    "dense": "Busqueda densa con embeddings multilingues (similitud coseno)",
    "hybrid": "Busqueda hibrida: BM25 (raices, sinonimos, titulos) + embeddings densos, fusion RRF",
}
LEXICAL_LABEL = "Busqueda lexica BM25 con raices, sinonimos del dominio y titulos de seccion"


def chunk_similarities(query: str, index: dict[str, Any]) -> dict[str, float]:
    """Coseno de la consulta con cada fragmento (absoluto: sirve para decir si un fragmento responde)."""
    scores = dense_vectors(index) @ dense.encode_query(query)
    return {chunk["chunk_id"]: float(score) for chunk, score in zip(index["chunks"], scores)}


def dense_ranking(query: str, index: dict[str, Any],
                  similarities: dict[str, float] | None = None) -> list[tuple[float, dict[str, Any]]]:
    """Fragmentos por similitud; `similarities` (de `chunk_similarities`) evita volver a codificar la consulta."""
    similarities = similarities if similarities is not None else chunk_similarities(query, index)
    ranked = sorted(((round(similarities[chunk["chunk_id"]], 6), chunk) for chunk in index["chunks"]),
                    key=lambda item: (-item[0], item[1]["chunk_id"]))
    return [item for item in ranked if item[0] >= dense.DENSE_MIN_SIMILARITY]


def dense_relevance(query: str, corpus_dir: Path = DEFAULT_CORPUS, store_dir: Path = DEFAULT_STORE) -> float:
    """Mayor coseno entre la consulta y el corpus, sin umbral (lo usa el control de alcance)."""
    index = load_index(corpus_dir, store_dir)
    return round(float((dense_vectors(index) @ dense.encode_query(query)).max()), 6)


def dense_search(query: str, index: dict[str, Any], top_k: int = 3) -> list[dict[str, Any]]:
    if top_k <= 0:
        raise ValueError("top_k debe ser positivo")
    similarities = chunk_similarities(query, index)
    hits = [format_hit(rank, score, chunk)
            for rank, (score, chunk) in enumerate(dense_ranking(query, index, similarities)[:top_k], 1)]
    return annotate(hits, similarities)


def hybrid_search(query: str, index: dict[str, Any], top_k: int = 3) -> list[dict[str, Any]]:
    """Fusión RRF de BM25 y embeddings densos: conserva las coincidencias exactas."""
    if top_k <= 0:
        raise ValueError("top_k debe ser positivo")
    by_id = {chunk["chunk_id"]: chunk for chunk in index["chunks"]}
    lexical_hits = lexical_search(query, index, CANDIDATES, LEXICAL_DEFAULT)
    lexical = [hit["chunk_id"] for hit in lexical_hits]
    best_lexical = max((hit["score"] for hit in lexical_hits), default=0.0)
    lexical_relative = {hit["chunk_id"]: hit["score"] / best_lexical for hit in lexical_hits} if best_lexical > 0 else {}
    similarities = chunk_similarities(query, index)  # se codifica la consulta una sola vez
    semantic = [chunk["chunk_id"] for _, chunk in dense_ranking(query, index, similarities)[:CANDIDATES]]
    fused: dict[str, float] = {}
    for ranking in (lexical, semantic):
        for position, chunk_id in enumerate(ranking, 1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (RRF_K + position)
    ordered = sorted(fused.items(), key=lambda item: (-round(item[1], 6), item[0]))
    hits = [format_hit(rank, score, by_id[chunk_id]) for rank, (chunk_id, score) in enumerate(ordered[:top_k], 1)]
    return annotate(hits, similarities, lexical_relative)


def search(query: str, index: dict[str, Any], top_k: int = 3, method: str = "hybrid") -> list[dict[str, Any]]:
    """Despacha al recuperador pedido: `tfidf`, una variante BM25, `dense` o `hybrid`."""
    if method == "tfidf":
        return annotate(tfidf_search(query, index, top_k))
    if method in LEXICAL_VARIANTS:
        return annotate(lexical_search(query, index, top_k, method))
    if method == "dense":
        return dense_search(query, index, top_k)
    if method == "hybrid":
        return hybrid_search(query, index, top_k)
    raise ValueError(f"Metodo de recuperacion desconocido: {method}")


def _model_name(used: str) -> str:
    return {"tfidf": TFIDF_MODEL_NAME, "dense": dense.DENSE_MODEL,
            "hybrid": f"{dense.DENSE_MODEL}+{LEXICAL_MODEL_NAME}"}.get(used, LEXICAL_MODEL_NAME)


def retrieve(
    query: str,
    top_k: int = 3,
    corpus_dir: Path = DEFAULT_CORPUS,
    store_dir: Path = DEFAULT_STORE,
    rebuild: bool = False,
    method: str = DEFAULT_METHOD,
) -> dict[str, Any]:
    """Fragmentos más relevantes con su procedencia. `auto` cae a BM25 dejando `fallback_reason`."""
    if method not in METHODS:
        raise ValueError(f"Metodo de recuperacion desconocido: {method}")
    index = load_index(corpus_dir, store_dir, rebuild)
    used, fallback = method, None
    if method == "auto":
        try:
            hits, used = hybrid_search(query, index, top_k), "hybrid"
        except DenseUnavailable as exc:
            # No es un cambio silencioso: el motivo queda en el resultado y en el expediente.
            hits, used, fallback = (annotate(lexical_search(query, index, top_k, LEXICAL_DEFAULT)), LEXICAL_DEFAULT,
                                    str(exc))
    else:
        hits = search(query, index, top_k, method)
    dense_meta = index.get("dense") if used in ("dense", "hybrid") else None
    chunks_path = store_paths(store_dir)[0]
    return {
        "enabled": True,
        "method": LEXICAL_LABEL if used in LEXICAL_VARIANTS else METHOD_LABELS[used],
        "retrieval_method": used,
        "requested_method": method,
        "fallback_reason": fallback,
        "embedding_model": _model_name(used),
        "model_revision": dense_meta["revision"] if dense_meta else None,
        "vectors_sha256": dense_meta["vectors_sha256"] if dense_meta else None,
        "query": query,
        "corpus": index["corpus"],
        "vector_store": display_path(chunks_path),
        "vector_store_sha256": file_sha256(chunks_path),
        "vector_dimensions": dense_meta["dimension"] if dense_meta else len(tfidf_model(index)["vocabulary"]),
        "documents_indexed": len({chunk["source"] for chunk in index["chunks"]}),
        "chunks_indexed": len(index["chunks"]),
        "retrieved_chunks": hits,
    }


def fallback_reason(corpus_dir: Path = DEFAULT_CORPUS, store_dir: Path = DEFAULT_STORE) -> str | None:
    """None si el RAG híbrido está disponible; si no, por qué se usará BM25."""
    try:
        dense.embedder()
        dense_vectors(load_index(corpus_dir, store_dir))
    except DenseUnavailable as exc:
        return str(exc)
    return None


def format_context(result: dict[str, Any]) -> str:
    return "\n\n".join(
        f"[Fuente: {item['source']} | Seccion: {item['section']} | Chunk: {item['chunk_id']} | "
        f"Puntaje: {item['score']}]\n{item['excerpt']}"
        for item in result["retrieved_chunks"]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--query", help="Consulta de recuperacion")
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--json", action="store_true", help="Mostrar resultado JSON")
    parser.add_argument("--rebuild-index", action="store_true",
                        help="Regenerar chunks.json y vectors.npy (puede descargar el modelo la primera vez)")
    parser.add_argument("--download-model", action="store_true",
                        help=f"Descargar el modelo denso ({dense.DENSE_MODEL}) a la cache local y salir")
    parser.add_argument("--method", default=DEFAULT_METHOD, choices=METHODS,
                        help="auto = hibrido si hay modelo denso; si no, BM25 (se informa el motivo)")
    args = parser.parse_args(argv)
    if args.download_model or args.rebuild_index:
        dense.enable_download()
    if args.download_model:
        try:
            dense.embedder()
        except DenseUnavailable as exc:
            print(f"No se pudo preparar el modelo: {exc}", file=sys.stderr)
            return 1
        print(f"Modelo listo: {dense.DENSE_MODEL} (revision {dense.DENSE_REVISION})")
        return 0
    if not args.query:
        parser.error("--query es obligatorio salvo con --download-model")
    result = retrieve(args.query, args.top_k, rebuild=args.rebuild_index, method=args.method)
    if result["fallback_reason"]:
        print(f"AVISO: se uso BM25 sin embeddings densos: {result['fallback_reason']}", file=sys.stderr)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    print(f"Consulta: {result['query']}")
    print(f"Metodo: {result['retrieval_method']} ({result['embedding_model']}) | "
          f"{result['documents_indexed']} documentos, {result['chunks_indexed']} fragmentos, "
          f"{result['vector_dimensions']} dimensiones")
    print("\n" + (format_context(result) or "Sin resultados."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
