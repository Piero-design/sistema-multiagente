"""Nivel de relevancia de un fragmento respecto de la pregunta.

El puntaje de la fusión RRF solo ordena (el primero y el segundo apenas se distinguen), así que no sirve para decir si
un fragmento responde la pregunta. Con embeddings se usa la similitud coseno, que es absoluta; sin ellos, el puntaje
BM25 relativo al mejor. Los umbrales se fijaron con `rag-eval.json` y se comprobaron sin ajustarlos con los conjuntos
reservados (`docs/rag-y-asistente.md`).
"""

from __future__ import annotations

from typing import Any

HIGH_SIMILARITY = 0.58   # ~93 % de los fragmentos de este nivel eran los etiquetados como respuesta
MEDIUM_SIMILARITY = 0.52  # con 0.50 se mostraban 15 fragmentos ajenos más y la misma cobertura (dev + reservados)
LEXICAL_AGREEMENT = 0.9   # un fragmento «media» sube a «alta» si además es (casi) el mejor por BM25
HIGH_RELATIVE = 0.85     # sin embeddings (BM25): fracción del mejor puntaje
MEDIUM_RELATIVE = 0.6
LEVELS = ("alta", "media", "baja")


def level_from_similarity(similarity: float, lexical: float = 0.0) -> str:
    """`lexical`: puntaje BM25 del fragmento relativo al mejor (0 a 1). Dos señales independientes que coinciden suben el nivel."""
    if similarity >= HIGH_SIMILARITY or (similarity >= MEDIUM_SIMILARITY and lexical >= LEXICAL_AGREEMENT):
        return "alta"
    return "media" if similarity >= MEDIUM_SIMILARITY else "baja"


def level_from_score(score: float, best: float, rank: int) -> str:
    ratio = score / best if best > 0 else 0.0
    return "alta" if rank == 1 or ratio >= HIGH_RELATIVE else "media" if ratio >= MEDIUM_RELATIVE else "baja"


def annotate(hits: list[dict[str, Any]], similarities: dict[str, float] | None = None,
             lexical: dict[str, float] | None = None) -> list[dict[str, Any]]:
    """Añade `similarity` (si hay embeddings) y `relevance` a cada fragmento recuperado."""
    best = max((hit["score"] for hit in hits), default=0.0)
    for hit in hits:
        similarity = (similarities or {}).get(hit["chunk_id"])
        hit["similarity"] = None if similarity is None else round(similarity, 6)
        hit["relevance"] = (level_from_similarity(similarity, (lexical or {}).get(hit["chunk_id"], 0.0))
                            if similarity is not None
                            else level_from_score(hit["score"], best, hit["rank"]))
    return hits


def visible_chunks(chunks: list[dict[str, Any]], minimum: str = "media") -> list[dict[str, Any]]:
    """Fragmentos que responden la pregunta: los de relevancia `minimum` o mayor y, siempre, el primero (con su nivel real)."""
    allowed = LEVELS[: LEVELS.index(minimum) + 1]
    return [chunk for chunk in chunks if chunk.get("relevance") in allowed or chunk["rank"] == 1]
