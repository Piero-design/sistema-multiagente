"""Embeddings densos BAAI/bge-m3 (opcionales: numpy y sentence-transformers del extra `dense`).

El modelo se carga solo desde la caché local, con revisión fijada y sin código remoto. Si falta
algo, se lanza `DenseUnavailable` y el RAG recupera con BM25 dejando el motivo registrado.
"""

from __future__ import annotations

import os
from typing import Any

# Sin telemetría ni conexiones al cargar modelos: la descarga solo ocurre al pedirla por la CLI.
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
_HUB_OFFLINE_DEFAULTED = "HF_HUB_OFFLINE" not in os.environ
os.environ.setdefault("HF_HUB_OFFLINE", "1")

DENSE_MODEL = "BAAI/bge-m3"
# Revisión exacta (hash de Hugging Face): sin ella, una actualización del autor cambiaría los vectores.
DENSE_REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
QUERY_PREFIX = ""
PASSAGE_PREFIX = ""
MAX_SEQ_LENGTH = 1024
# Medido en v4 con 65 consultas del dominio (mínimo 0,38; p5 0,48) y 14 ajenas (máximo 0,445).
DENSE_MIN_SIMILARITY = 0.46
DEPENDENCIES_MISSING = ("faltan dependencias densas (numpy, sentence-transformers); "
                        "instala el extra dense: pip install -e \".[dense]\"")


class DenseUnavailable(RuntimeError):
    """Faltan numpy, sentence-transformers, el modelo local o los vectores del almacén."""


_allow_download = False
_EMBEDDERS: dict[str, Any] = {}
_FAILURES: dict[str, str] = {}  # evita reintentar en el mismo proceso una carga que ya falló
_QUERY_VECTORS: dict[tuple[str, str], Any] = {}


def enable_download() -> None:
    """Solo la CLI lo llama (--download-model, --rebuild-index)."""
    global _allow_download
    _allow_download = True
    if _HUB_OFFLINE_DEFAULTED:
        os.environ.pop("HF_HUB_OFFLINE", None)


def numpy_module() -> Any:
    try:
        import numpy
    except ImportError as exc:
        raise DenseUnavailable(DEPENDENCIES_MISSING) from exc
    return numpy


def embedder() -> Any:
    if DENSE_MODEL in _FAILURES and not _allow_download:
        raise DenseUnavailable(_FAILURES[DENSE_MODEL])
    if DENSE_MODEL not in _EMBEDDERS:
        try:
            import numpy  # noqa: F401
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            _FAILURES[DENSE_MODEL] = DEPENDENCIES_MISSING
            raise DenseUnavailable(DEPENDENCIES_MISSING) from exc
        try:
            model = SentenceTransformer(DENSE_MODEL, device="cpu", local_files_only=not _allow_download,
                                        revision=DENSE_REVISION, trust_remote_code=False)
        except Exception as exc:  # noqa: BLE001 - la biblioteca lanza OSError, ValueError, etc.
            reason = (f"el modelo {DENSE_MODEL} no esta descargado ({type(exc).__name__}); "
                      "ejecuta: python -m dsar.rag.retrieve --download-model y reinicia")
            _FAILURES[DENSE_MODEL] = reason
            raise DenseUnavailable(reason) from exc
        model.max_seq_length = MAX_SEQ_LENGTH
        _EMBEDDERS[DENSE_MODEL] = model
        _FAILURES.pop(DENSE_MODEL, None)
    return _EMBEDDERS[DENSE_MODEL]


def available() -> str | None:
    """None si el modelo denso se puede usar; si no, el motivo."""
    try:
        embedder()
    except DenseUnavailable as exc:
        return str(exc)
    return None


def encode(texts: list[str]) -> Any:
    matrix = embedder().encode(texts, normalize_embeddings=True, convert_to_numpy=True,
                               batch_size=8, show_progress_bar=False)
    return matrix.astype("float32")


def encode_one(text: str) -> Any:
    """Embedding de un texto con caché acotada: la misma pregunta pasa por varios controles."""
    key = (DENSE_MODEL, text)
    if key not in _QUERY_VECTORS:
        if len(_QUERY_VECTORS) >= 512:
            _QUERY_VECTORS.pop(next(iter(_QUERY_VECTORS)))
        _QUERY_VECTORS[key] = encode([text])[0]
    return _QUERY_VECTORS[key]


def encode_query(text: str) -> Any:
    return encode_one(QUERY_PREFIX + text)


def chunk_passage(chunk: dict[str, Any]) -> str:
    return PASSAGE_PREFIX + f"{chunk['section']}\n{chunk['text']}"
