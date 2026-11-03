"""Chat del asistente: única vía al modelo de lenguaje; registra cada llamada en la bitácora."""

from __future__ import annotations

from typing import Any

from dsar.assistant.answer import Answer, answer
from dsar.assistant.llm import LLMError
from dsar.assistant.llm.base import Message
from dsar.rag.guide import retrieve_guide
from dsar.services import cases
from dsar.services.controls import applied_controls
from dsar.services.context import ServiceContext


def run_answer(ctx: ServiceContext, question: str, package: dict[str, Any] | None, mode: str,
               model: str | None, history: list[Message] | None) -> Answer:
    """Aplica el flujo del asistente y registra la llamada al modelo, también si falla."""
    try:
        result = answer(question, package, mode, model, history, profiles=ctx.profiles,
                        organization=ctx.organization(), providers=ctx.providers, today=ctx.today(),
                        semantic=ctx.semantic, retriever=ctx.retrieve,
                        controls=applied_controls(package) if package else None,
                        guide_retriever=lambda query, top_k=2: retrieve_guide(query, top_k=top_k, method=ctx.rag_method),
                        utc_now=ctx.now())
    except LLMError as exc:
        if exc.entry:
            ctx.repository.log_llm_call(exc.entry | {"case_id": (package or {}).get("case_id")})
        raise
    if result.llm_call:
        ctx.repository.log_llm_call(result.llm_call)
    return result


def ask(ctx: ServiceContext, question: str, case_id: str | None = None, mode: str = "guided",
        model: str | None = None, history: list[Message] | None = None) -> dict[str, Any]:
    package = cases.get(ctx, case_id) if case_id else None
    return run_answer(ctx, question, package, mode, model, history).to_dict()
