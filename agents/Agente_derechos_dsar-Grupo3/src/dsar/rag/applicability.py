"""Qué fragmentos del corpus pueden fundamentar un expediente concreto.

El corpus reúne la normativa de todos los perfiles (Perú, laboratorio…) y el procedimiento de la organización. Un
expediente del perfil LAB-30 no debe citar los artículos de la Ley 29733, ni uno cuya política de la organización no se
aplicó debe citar el procedimiento interno: serían fuentes de otro marco.
"""

from __future__ import annotations

from typing import Any

PROFILE_PREFIX = "perfil-"
ORGANIZATION_SOURCE = "organizacion-politica-interna.md"


def _profile_of(source: str) -> str | None:
    """`perfil-pe-ley29733.md` -> `pe-ley29733`; los demás documentos no pertenecen a un perfil."""
    if not source.startswith(PROFILE_PREFIX):
        return None
    return source[len(PROFILE_PREFIX):].removesuffix(".md")


def applies(source: str, policy_id: str | None, organization_applied: bool) -> bool:
    if source == ORGANIZATION_SOURCE:
        return organization_applied
    profile = _profile_of(source)
    if profile is None or not policy_id:
        return True
    policy = policy_id.lower()
    return policy == profile or policy.startswith(profile + "-")


def applicable_chunks(chunks: list[dict[str, Any]], policy_id: str | None, organization_applied: bool,
                      limit: int | None = None) -> list[dict[str, Any]]:
    """Deja los fragmentos que aplican al expediente y vuelve a numerar `rank` desde 1."""
    kept = [dict(chunk) for chunk in chunks if applies(chunk["source"], policy_id, organization_applied)]
    for rank, chunk in enumerate(kept[:limit], 1):
        chunk["rank"] = rank
    return kept[:limit]


TECHNICAL_SOURCES = frozenset({"case-schema.md"})
TECHNICAL_TERMS = ("esquema", "campos", "json", "estructura", "formato", "schema", "atributo")


def drop_technical(chunks: list[dict[str, Any]], question: str) -> list[dict[str, Any]]:
    """`case-schema.md` documenta el JSON del caso (para quien programa): solo se cita si la pregunta es sobre su forma."""
    from dsar.rag.lexical import normalize

    text = normalize(question)
    if any(term in text for term in TECHNICAL_TERMS):
        return chunks
    kept = [dict(chunk) for chunk in chunks if chunk["source"] not in TECHNICAL_SOURCES]
    for rank, chunk in enumerate(kept, 1):
        chunk["rank"] = rank
    return kept
