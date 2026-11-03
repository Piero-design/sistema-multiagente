"""Corpus del RAG: referencias Markdown fragmentadas por encabezados."""

from __future__ import annotations

import hashlib
from pathlib import Path

from dsar.paths import REFERENCES_DIR

DEFAULT_CORPUS = REFERENCES_DIR
# Las referencias "tarea-*.md" son instrucciones de procedimiento para el modelo, no conocimiento
# normativo: se excluyen del índice para no desplazar a la norma y la ley.
PROCEDURAL_PREFIX = "tarea-"
# Una sección más larga que MAX_CHARS se parte en ventanas que repiten ~OVERLAP_CHARS del final de la
# anterior, para que una idea no quede cortada entre dos fragmentos. Subir la versión invalida el índice.
CHUNKING_VERSION = "2"
MAX_CHARS = 1200
OVERLAP_CHARS = 240


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def corpus_files(corpus_dir: Path) -> list[Path]:
    return [path for path in sorted(corpus_dir.rglob("*.md")) if not path.name.startswith(PROCEDURAL_PREFIX)]


def corpus_signature(corpus_dir: Path) -> str:
    digest = hashlib.sha256(f"{CHUNKING_VERSION}:{MAX_CHARS}:{OVERLAP_CHARS}".encode("utf-8"))
    for path in corpus_files(corpus_dir):
        digest.update(path.relative_to(corpus_dir).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _sections(text: str, default_heading: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    heading, body = default_heading, []
    for line in text.splitlines():
        if line.startswith("#"):
            if any(item.strip() for item in body):
                sections.append((heading, body))
            heading, body = line.lstrip("#").strip() or heading, []
        else:
            body.append(line)
    if any(item.strip() for item in body):
        sections.append((heading, body))
    return sections


def _units(content: str) -> list[tuple[str, str]]:
    """Piezas que no se parten: párrafos, bloques de código y tablas completas. Devuelve (texto, tipo)."""
    units: list[tuple[str, str]] = []
    block: list[str] = []
    kind = "text"
    fence = False

    def flush() -> None:
        if block:
            units.append(("\n".join(block), kind))
            block.clear()

    for line in content.splitlines():
        stripped = line.strip()
        if fence:
            block.append(line)
            if stripped.startswith("```"):
                flush()
                fence = False
        elif stripped.startswith("```"):
            flush()
            kind, fence = "code", True
            block.append(line)
        elif stripped.startswith("|"):
            if kind != "table":
                flush()
            kind = "table"
            block.append(line)
        elif stripped:
            if kind != "text":
                flush()
            kind = "text"
            block.append(line)
        else:
            flush()
            kind = "text"
    flush()
    return units


def _windows(content: str) -> list[str]:
    """Una sola ventana si cabe; si no, ventanas de unidades completas que repiten el final de la anterior."""
    if len(content) <= MAX_CHARS:
        return [content]
    windows: list[list[str]] = []
    current: list[str] = []
    for text, _ in _units(content):
        if current and len("\n\n".join([*current, text])) > MAX_CHARS:
            windows.append(current)
            tail: list[str] = []
            for previous in reversed(current):
                if len("\n\n".join([previous, *tail])) > OVERLAP_CHARS:
                    break
                tail.insert(0, previous)
            current = tail
        current.append(text)
    if current and (not windows or any(item not in windows[-1] for item in current)):
        windows.append(current)
    return ["\n\n".join(window) for window in windows]


def _suffix(position: int) -> str:
    """La primera ventana conserva el identificador de la sección; las siguientes añaden b, c…"""
    return "" if position == 0 else chr(ord("a") + position)


def split_markdown(path: Path, root: Path) -> list[dict[str, str]]:
    """Un fragmento por sección (o varias ventanas solapadas); `chunk_id` = archivo + posición + sufijo."""
    relative = path.relative_to(root).as_posix()
    sections = _sections(path.read_text(encoding="utf-8"), path.stem.replace("-", " ").title())
    chunks = []
    for index, (section, lines) in enumerate(sections, start=1):
        content = "\n".join(lines).strip()
        if not content:
            continue
        for position, text in enumerate(_windows(content)):
            chunks.append({"chunk_id": f"{path.stem}-{index:02d}{_suffix(position)}", "source": relative,
                           "section": section, "text": text, "sha256": sha256_text(text)})
    return chunks


def load_chunks(corpus_dir: Path = DEFAULT_CORPUS) -> list[dict[str, str]]:
    if not corpus_dir.is_dir():
        raise ValueError(f"No existe el corpus RAG: {corpus_dir}")
    chunks = [chunk for path in corpus_files(corpus_dir) for chunk in split_markdown(path, corpus_dir)]
    if not chunks:
        raise ValueError("El corpus RAG no contiene documentos Markdown")
    return chunks
