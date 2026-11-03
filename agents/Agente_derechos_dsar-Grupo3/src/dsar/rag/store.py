"""Almacén versionado del RAG: `chunks.json` (texto y metadatos) y `vectors.npy` (embeddings)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from dsar.paths import RAG_STORE_DIR, display_path
from dsar.rag import dense
from dsar.rag.corpus import DEFAULT_CORPUS, corpus_signature, load_chunks

DEFAULT_STORE = RAG_STORE_DIR
CHUNKS_FILE = "chunks.json"
VECTORS_FILE = "vectors.npy"
STORE_FORMAT = 2
PERSISTED_KEYS = ("format_version", "corpus", "corpus_sha256", "dense", "chunks")
CHUNK_KEYS = ("chunk_id", "source", "section", "sha256", "text")

_VECTORS: dict[str, Any] = {}


def store_paths(store_dir: Path) -> tuple[Path, Path]:
    return store_dir / CHUNKS_FILE, store_dir / VECTORS_FILE


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_chunks_file(index: dict[str, Any], store_dir: Path) -> None:
    persisted = {key: index[key] for key in PERSISTED_KEYS}
    persisted["chunks"] = [{key: chunk[key] for key in CHUNK_KEYS} for chunk in index["chunks"]]
    store_dir.mkdir(parents=True, exist_ok=True)
    store_paths(store_dir)[0].write_text(json.dumps(persisted, indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8", newline="\n")


def build_index(corpus_dir: Path = DEFAULT_CORPUS, store_dir: Path = DEFAULT_STORE) -> dict[str, Any]:
    """Regenera `chunks.json`. Los vectores densos previos quedan obsoletos y se borran."""
    index = {
        "format_version": STORE_FORMAT,
        "corpus": display_path(corpus_dir),
        "corpus_sha256": corpus_signature(corpus_dir),
        "dense": None,
        "chunks": load_chunks(corpus_dir),
    }
    write_chunks_file(index, store_dir)
    vectors_path = store_paths(store_dir)[1]
    if vectors_path.is_file():
        vectors_path.unlink()
    return index


def build_dense(index: dict[str, Any], store_dir: Path) -> None:
    """Calcula `vectors.npy` (fragmentos x dimensión, float32, normalizado) y lo enlaza en chunks.json."""
    matrix = dense.encode([dense.chunk_passage(chunk) for chunk in index["chunks"]])
    numpy = dense.numpy_module()
    vectors_path = store_paths(store_dir)[1]
    store_dir.mkdir(parents=True, exist_ok=True)
    numpy.save(vectors_path, matrix, allow_pickle=False)
    index["dense"] = {
        "model": dense.DENSE_MODEL,
        "revision": dense.DENSE_REVISION,
        "dimension": int(matrix.shape[1]),
        "count": int(matrix.shape[0]),
        "vectors_file": VECTORS_FILE,
        "vectors_sha256": file_sha256(vectors_path),
    }
    write_chunks_file(index, store_dir)


def is_current(stored: dict[str, Any], corpus_dir: Path) -> bool:
    return stored.get("format_version") == STORE_FORMAT and stored.get("corpus_sha256") == corpus_signature(corpus_dir)


def load_index(corpus_dir: Path = DEFAULT_CORPUS, store_dir: Path = DEFAULT_STORE,
               rebuild: bool = False) -> dict[str, Any]:
    """Carga el almacén; si falta o no corresponde al corpus, lo regenera (y los vectores si hay modelo)."""
    chunks_path = store_paths(store_dir)[0]
    index = None
    if not rebuild and chunks_path.is_file():
        stored = json.loads(chunks_path.read_text(encoding="utf-8"))
        if is_current(stored, corpus_dir):
            index = stored
    if index is None:
        index = build_index(corpus_dir, store_dir)
        try:
            build_dense(index, store_dir)
        except dense.DenseUnavailable:
            pass  # Sin modelo local no hay vectores; la recuperación léxica sigue funcionando.
    index["store_dir"] = str(store_dir)
    return index


def _vectors_valid(meta: dict[str, Any] | None, vectors_path: Path) -> bool:
    return bool(
        meta and meta.get("model") == dense.DENSE_MODEL and meta.get("revision") == dense.DENSE_REVISION
        and vectors_path.is_file() and file_sha256(vectors_path) == meta.get("vectors_sha256")
    )


def dense_vectors(index: dict[str, Any]) -> Any:
    """Matriz de vectores verificada contra chunks.json (modelo, revisión, hash y forma)."""
    store_dir = Path(index["store_dir"])
    vectors_path = store_paths(store_dir)[1]
    meta = index.get("dense")
    if not _vectors_valid(meta, vectors_path):
        plain = {key: index[key] for key in PERSISTED_KEYS}
        build_dense(plain, store_dir)
        index["dense"] = meta = plain["dense"]
    if meta["vectors_sha256"] not in _VECTORS:
        matrix = dense.numpy_module().load(vectors_path, allow_pickle=False)
        if matrix.shape != (len(index["chunks"]), meta["dimension"]):
            raise dense.DenseUnavailable("vectors.npy no coincide con chunks.json; reconstruye el indice")
        _VECTORS[meta["vectors_sha256"]] = matrix
    return _VECTORS[meta["vectors_sha256"]]
