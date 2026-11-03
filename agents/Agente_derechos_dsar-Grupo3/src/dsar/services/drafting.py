"""Borrador de respuesta: el modelo redacta solo la carta; el motor fija estructura y hechos."""

from __future__ import annotations

from typing import Any

from dsar.assistant.answer import GUIDED
from dsar.assistant.guard import executed_claims
from dsar.assistant.llm import LLMError
from dsar.core.errors import TransitionError
from dsar.core.render import guided_letter, render_response
from dsar.services import cases
from dsar.services.chat import run_answer
from dsar.services.context import ServiceContext

# La misma pregunta rápida del catálogo: la acepta el control de alcance también con la capa semántica.
# («Redacta la carta de respuesta al titular…» se bloqueaba como intento de envío y el modelo no se llamaba.)
DRAFT_QUESTION = "Redacta un borrador de respuesta para este caso."


def draft(ctx: ServiceContext, case_id: str, mode: str = GUIDED, model: str | None = None,
          letter: bool = False) -> dict[str, Any]:
    """`letter` añade, en modo guiado, la carta al titular que redacta el motor (sin LLM)."""
    package = cases.get(ctx, case_id)
    if mode == GUIDED:
        text, llm_call = render_response(package, letter=guided_letter(package) if letter else None), None
    else:
        result = run_answer(ctx, DRAFT_QUESTION, package, mode, model, None)
        if not result.draft:
            # Nunca se sustituye en silencio por la plantilla: la persona debe saber que el modelo no redactó.
            raise LLMError(f"El asistente no redactó la carta ({result.scope_basis}). El borrador no se modificó.")
        text, llm_call = result.draft, result.llm_call
    return {"case_id": package["case_id"], "draft": text, "warnings": executed_claims(text), "llm_call": llm_call}


def warnings(text: str) -> dict[str, Any]:
    """Avisos sobre un borrador editado por la persona: frases que afirman acciones ejecutadas."""
    return {"warnings": executed_claims(text)}


def approved_draft(ctx: ServiceContext, case_id: str) -> dict[str, Any]:
    """Borrador con datos del titular para otros agentes: solo tras la aprobación humana."""
    package = cases.get(ctx, case_id)
    if package["status"] != "APPROVED":
        raise TransitionError(
            f"El expediente está en {package['status']}. El borrador con datos del titular solo se entrega "
            "después de la aprobación humana en el panel del agente."
        )
    return {"case_id": case_id, "draft_markdown": render_response(package)}
