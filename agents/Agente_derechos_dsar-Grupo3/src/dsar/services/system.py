"""Estado del sistema, modelos disponibles, consulta al RAG y auditoría."""

from __future__ import annotations

from typing import Any

from dsar import __version__
from dsar.assistant import guard
from dsar.assistant.llm import LLMError
from dsar.assistant.llm.ollama import available_models
from dsar.core.hashing import sha256_file
from dsar.paths import SKILL_PATH, display_path
from dsar.rag import dense
from dsar.rag.retrieve import fallback_reason
from dsar.rag.store import load_index
from dsar.services.context import ServiceContext

MAX_TOP_K = 5
MAX_LOG = 500


def warm_up(ctx: ServiceContext) -> None:
    """Carga al arrancar, no en la primera petición: índice, modelo denso, vectores del corpus y
    ejemplos del filtro de evasión (codificarlos en CPU tarda decenas de segundos)."""
    load_index()
    if ctx.rag_method != "auto" or dense.available() is not None:
        return
    fallback_reason()
    if ctx.semantic:
        guard.example_vectors()


def health(ctx: ServiceContext) -> dict[str, Any]:
    reason = fallback_reason() if ctx.rag_method == "auto" else f"metodo fijado: {ctx.rag_method}"
    return {"status": "ok", "version": __version__, "environment": ctx.settings.environment,
            "now": ctx.now().isoformat(),
            "mail": {"source": ctx.settings.mail.source, "send_enabled": ctx.settings.mail.send_enabled},
            "rag": {"method": "hybrid" if reason is None else "bm25", "fallback_reason": reason}}


def models(ctx: ServiceContext) -> dict[str, Any]:
    """Proveedores configurados y modelos de Ollama; si Ollama no responde, lista vacía y motivo."""
    ollama: dict[str, Any] = {"available": True, "models": [], "reason": None}
    try:
        ollama["models"] = available_models()
    except LLMError as exc:
        ollama.update(available=False, reason=str(exc))
    providers = [{"id": "guided", "label": "Modo guiado (sin LLM)", "cloud": False, "default_model": None}]
    providers += [{"id": provider.name, "label": provider.label, "cloud": provider.cloud,
                   "default_model": provider.default_model} for provider in ctx.providers.values()]
    return {"providers": providers, "ollama": ollama}


def search_knowledge(ctx: ServiceContext, query: str, top_k: int = 3) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("Escribe una consulta.")
    if not 1 <= top_k <= MAX_TOP_K:
        raise ValueError(f"top_k debe estar entre 1 y {MAX_TOP_K}.")
    return ctx.retrieve(query.strip(), top_k)


def llm_log(ctx: ServiceContext, limit: int = 50) -> list[dict[str, Any]]:
    if not 1 <= limit <= MAX_LOG:
        raise ValueError(f"limite debe estar entre 1 y {MAX_LOG}.")
    return ctx.repository.list_llm_calls(limit)


def skill_fingerprint() -> dict[str, Any]:
    return {"name": "dsar-rights", "path": display_path(SKILL_PATH), "sha256": sha256_file(SKILL_PATH)}


def handoffs(ctx: ServiceContext, case_id: str | None = None) -> list[dict[str, Any]]:
    return ctx.repository.list_handoffs(case_id)
