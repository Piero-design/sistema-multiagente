"""Guía de uso de la aplicación: corpus propio, separado del normativo.

Si estuviera en el mismo índice competiría con las fuentes normativas (empeoraba las mediciones de recuperación) y subiría la
similitud de cualquier pregunta sobre «usar» algo, debilitando el control de alcance. Por eso solo se consulta cuando la
pregunta es de procedimiento («¿cómo apruebo este expediente?»).
"""

from __future__ import annotations

import re
from typing import Any

from dsar.paths import GUIDE_DIR, GUIDE_STORE_DIR
from dsar.rag.lexical import normalize
from dsar.rag.retrieve import retrieve

HOW = re.compile(r"\b(como|donde|pasos|que boton|en que pantalla|que hago para|como se)\b")
ACTIONS = ("aprueb", "aprobar", "rechaz", "decid", "decision", "prorroga", "registr", "export", "borrador", "redact",
           "cargar", "crear", "verific", "politica", "editar", "pantalla", "boton", "panel", "formulario")


def asks_how_to(question: str) -> bool:
    """«¿Cómo apruebo…?», «¿dónde pido una prórroga?»: una pregunta sobre cómo se hace algo en la aplicación."""
    text = normalize(question)
    return bool(HOW.search(text)) and any(action in text for action in ACTIONS)


# Procedimientos inocuos: cómo exportar, redactar, cargar o editar. Aprobar, verificar o decidir NO están aquí (los pedidos de
# saltarse un control suelen empezar por «cómo»).
SAFE_ACTIONS = ("export", "borrador", "redact", "cargar", "crear", "editar", "politica", "nueva solicitud")


# Si la pregunta menciona a otras personas o «todo», no se trata como inocua aunque empiece por «cómo exporto».
UNSAFE_CONTEXT = ("otra", "otro", "tercero", "ajen", "todos los", "todas las", "confidencial", "sin ")


def asks_safe_how_to(question: str) -> bool:
    text = normalize(question)
    return (bool(HOW.search(text)) and any(action in text for action in SAFE_ACTIONS)
            and not any(term in text for term in UNSAFE_CONTEXT))


def retrieve_guide(query: str, top_k: int = 2, method: str = "auto") -> dict[str, Any]:
    return retrieve(query, top_k=top_k, corpus_dir=GUIDE_DIR, store_dir=GUIDE_STORE_DIR, method=method)
