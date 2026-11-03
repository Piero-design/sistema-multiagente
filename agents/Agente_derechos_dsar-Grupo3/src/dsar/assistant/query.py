"""Consulta al RAG con el contexto del expediente: solo hechos no personales, sin LLM."""

from __future__ import annotations

from typing import Any

RIGHT_TERMS = {
    "access": "acceso", "rectification": "rectificación", "erasure": "supresión cancelación",
    "portability": "portabilidad", "objection": "oposición", "information": "información",
}


RIGHT_LABELS = {
    "access": "Acceso", "rectification": "Rectificación", "erasure": "Supresión / cancelación",
    "portability": "Portabilidad", "objection": "Oposición", "information": "Información (solo PE)",
}
RIGHT_WORDS = {
    "access": ("acceso",), "rectification": ("rectific",), "erasure": ("supres", "cancelaci"),
    "portability": ("portabilidad",), "objection": ("oposici",), "information": ("informaci",),
}


# Con un expediente se recupera de más: los fragmentos de otro perfil se descartan y quedan tres.
CASE_CANDIDATES = 8


def mentioned_rights(question: str, rights: list[str]) -> list[str]:
    """Derechos del caso que la pregunta nombra (puede ser ninguno)."""
    from dsar.rag.lexical import normalize

    text = normalize(question)
    return [right for right in rights if any(word in text for word in RIGHT_WORDS.get(right, ()))]


def named_rights(question: str, rights: list[str]) -> list[str]:
    """Derechos que la pregunta nombra o, si no nombra ninguno, todos los del caso (su contexto)."""
    return mentioned_rights(question, rights) or rights


def case_terms(package: dict[str, Any] | None, question: str = "") -> list[str]:
    """Derechos y perfil del caso. Nunca registros, `request_text` ni datos del titular.

    Si la pregunta nombra un derecho («¿qué es la rectificación?») solo se añade ese: los demás derechos del caso
    desviarían la búsqueda hacia otros artículos.
    """
    if not package:
        return []
    rights = named_rights(question, package.get("request_types") or [package["request_type"]])
    terms = [RIGHT_TERMS.get(right, right) for right in rights]
    policy = (package.get("policy") or {}).get("policy_id")
    return [*terms, policy] if policy else terms


def build_query(question: str, package: dict[str, Any] | None) -> str:
    terms = case_terms(package, question)
    return f"{question} ({'; '.join(terms)})" if terms else question
