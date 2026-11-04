"""Herramientas que el Agente DSAR expone por MCP a otros agentes del PIMS o a Claude Code.

Seguridad:
- Ninguna herramienta aprueba, rechaza ni ejecuta: la decisión humana solo existe en el panel.
- Las respuestas llevan hechos minimizados; el borrador con datos del titular solo sale cuando el
  expediente está APPROVED por una persona.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError

from dsar.services import cases, chat, controls, drafting, system
from dsar.services.context import ServiceContext
from dsar.services.errors import CaseInputError, LLMError, NotFoundError, TransitionError

IDENTITY_STATES = frozenset({"verified", "pending"})
EXPECTED_ERRORS = (CaseInputError, TransitionError, NotFoundError, ValueError, LLMError)
# Lo que sale del asistente por MCP: sin el borrador (lleva datos del titular; lo pide el DPO por la plataforma).
ANSWER_FIELDS = ("question", "answer", "task", "scope", "scope_basis", "mode", "model", "warnings")
SOURCE_FIELDS = ("chunk_id", "source", "section")
DRAFT_ELSEWHERE = ("El borrador de un caso contiene datos del titular: lo prepara una persona en el panel del agente "
                   "(en la plataforma, la pestaña «Gestión (DPO)» de G3). Tras la aprobación, usa dsar_borrador.")


def _guard(call):
    """Convierte los errores esperados en ToolError: el cliente recibe el mensaje sin traza."""
    def wrapper(*args, **kwargs):
        try:
            return call(*args, **kwargs)
        except EXPECTED_ERRORS as exc:
            raise ToolError(str(exc)) from exc
    wrapper.__name__, wrapper.__doc__ = call.__name__, call.__doc__
    return wrapper


@_guard
def crear_caso(ctx: ServiceContext, principal_id: str, request_types: list[str], policy_id: str = "PE-LEY29733",
               received_at: str | None = None, identity_status: str = "pending", identity_reference: str = "",
               request_text: str = "") -> dict[str, Any]:
    """T1: registra y tramita una solicitud. Devuelve el resumen minimizado del expediente."""
    if identity_status not in IDENTITY_STATES:
        raise CaseInputError("identity_status debe ser 'verified' o 'pending'.")
    request = {
        "principal_id": principal_id,
        "request_types": request_types,
        "received_at": received_at or ctx.today().isoformat(),
        "policy_id": policy_id,
        "request_text": request_text[:2000],
        "identity_verification": {
            "status": identity_status,
            "method": "declarado por el cliente MCP (sistema de verificacion externo)",
            "reference": identity_reference[:200] or "sin-referencia",
        },
    }
    return cases.summary(cases.register(ctx, request, origin="MCP")["case"])


@_guard
def estado(ctx: ServiceContext, case_id: str) -> dict[str, Any]:
    """T5: estado, motivos de revisión humana, aprobador y handoffs de un expediente."""
    return cases.summary(cases.get(ctx, case_id))


@_guard
def plazos(ctx: ServiceContext, case_id: str) -> dict[str, Any]:
    """T4: plazos por derecho de un expediente guardado."""
    package = cases.get(ctx, case_id)
    return {"case_id": case_id, "deadline_at": package["deadline_at"], "deadlines": package["deadlines"],
            "policy_id": package["policy"]["policy_id"]}


@_guard
def calcular_plazos(ctx: ServiceContext, request_types: list[str], received_at: str,
                    policy_id: str = "PE-LEY29733") -> dict[str, Any]:
    """T4: calcula plazos sin crear expediente (sin datos personales)."""
    return cases.deadlines(ctx, request_types, date.fromisoformat(received_at), policy_id)


@_guard
def controles(ctx: ServiceContext, case_id: str) -> dict[str, Any]:
    """Controles del Anexo A y cláusulas de ISO/IEC 27701:2025 que evidencia un expediente (solo lectura)."""
    package = cases.get(ctx, case_id)
    return {"case_id": case_id, "status": package["status"], "controls": controls.applied_controls(package)}


@_guard
def asistente(ctx: ServiceContext, pregunta: str, case_id: str | None = None, modo: str = "guided") -> dict[str, Any]:
    """Asistente DSAR: control de alcance y filtro de evasión antes del modelo; el modelo explica, no decide."""
    result = chat.ask(ctx, pregunta[:2000], case_id or None, modo)
    if result.get("draft"):
        # El borrador de un caso lleva sus registros: no sale por MCP antes de la aprobación humana.
        result["answer"] = DRAFT_ELSEWHERE
    return {key: result.get(key) for key in ANSWER_FIELDS} | {
        "case_id": case_id or None,
        "sources": [{key: item.get(key) for key in SOURCE_FIELDS} for item in result.get("sources") or []],
    }


@_guard
def listar(ctx: ServiceContext, status: str | None = None) -> list[dict[str, Any]]:
    """Bandeja: expedientes guardados, ordenados por plazo."""
    return cases.list_cases(ctx, status)


@_guard
def borrador(ctx: ServiceContext, case_id: str) -> dict[str, Any]:
    """T3: borrador de respuesta. Solo disponible tras la aprobación humana."""
    return drafting.approved_draft(ctx, case_id)


@_guard
def consultar_norma(ctx: ServiceContext, pregunta: str, top_k: int = 3) -> dict[str, Any]:
    """T2: fragmentos de ISO/IEC 27701, Ley 29733 y política interna, con procedencia."""
    result = system.search_knowledge(ctx, pregunta, max(1, min(top_k, system.MAX_TOP_K)))
    return {"fragments": [{key: item[key] for key in ("chunk_id", "source", "section", "score", "excerpt")}
                          for item in result["retrieved_chunks"]],
            "fallback_reason": result["fallback_reason"]}


@_guard
def handoffs(ctx: ServiceContext, case_id: str | None = None) -> list[dict[str, Any]]:
    """Entregas para los agentes de Evidencia, Terceros e Inventario (sin datos personales)."""
    return system.handoffs(ctx, case_id)
