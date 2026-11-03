"""Revisión, prórroga y decisión humana. Nada se ejecuta: las acciones siguen con `executed: false`."""

from __future__ import annotations

import copy
from typing import Any

from dsar.core.errors import CaseInputError
from dsar.core.procedures import apply_human_decision, extend_deadline, extension_preview, resume_case
from dsar.core.validator import validate
from dsar.services import cases, outbox
from dsar.services.context import ServiceContext
from dsar.storage.handoffs import build_handoffs, summary, write_handoffs

REVIEW_OPTIONS = frozenset({"Observado", "Borrador revisado"})


def _text(value: str, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseInputError(message)
    return value.strip()


def review(ctx: ServiceContext, case_id: str, reviewer: str, note: str, decision: str) -> dict[str, Any]:
    """Revisión simulada del borrador: queda registrada, pero no cambia el estado."""
    reviewer = _text(reviewer, "Indica revisor y observacion.")
    note = _text(note, "Indica revisor y observacion.")
    if decision not in REVIEW_OPTIONS:
        raise CaseInputError("Revision desconocida.")
    reviewed = copy.deepcopy(cases.get(ctx, case_id))
    reviewed.setdefault("human_reviews", []).append({
        "reviewer": reviewer, "note": note, "decision": decision, "simulated": True, "at": ctx.now().isoformat(),
    })
    return cases.save(ctx, reviewed)


def decide(ctx: ServiceContext, case_id: str, reviewer: str, decision: str, note: str) -> dict[str, Any]:
    """Única vía a APPROVED, REJECTED o CANCELLED. Registra la decisión y genera los handoffs."""
    decided = apply_human_decision(cases.get(ctx, case_id), reviewer, decision, note, ctx.now())
    handoffs = build_handoffs(decided, ctx.now().isoformat())
    decided["handoffs"] = [summary(item) for item in handoffs]
    errors = validate(decided)
    if errors:
        raise CaseInputError("Expediente invalido: " + "; ".join(errors))
    # Caso, decisión y handoffs en una sola transacción; los archivos se escriben solo si la BD confirmó.
    ctx.repository.save_decision(decided, decided["human_decision"], handoffs)
    write_handoffs(handoffs, ctx.settings.handoff_dir)
    outbox.after_decision(ctx, decided)
    return {"case": decided, "handoffs": handoffs}


def extension_options(ctx: ServiceContext, case_id: str, right: str, days: int | None = None) -> dict[str, Any]:
    """Límites y fecha resultante de una prórroga, sin guardar nada: es lo que muestra el formulario."""
    return extension_preview(cases.get(ctx, case_id), ctx.profiles, right, ctx.today(), days)


def extend(ctx: ServiceContext, case_id: str, right: str, reason: str, reviewer: str,
           days: int | None = None) -> dict[str, Any]:
    """Prórroga del art. 71, decidida por una persona en la fecha de hoy."""
    extended = extend_deadline(cases.get(ctx, case_id), ctx.profiles, right, reason, reviewer, ctx.today(), days)
    # La fecha del núcleo es un día; el instante UTC permite a la interfaz mostrarlo en la zona de quien lo mira.
    extended["deadlines"][right]["extension"]["decided_at_utc"] = ctx.now().isoformat()
    return cases.save(ctx, extended)


def resume(ctx: ServiceContext, case_id: str, reviewer: str, note: str) -> dict[str, Any]:
    """Una persona reanuda un trámite suspendido (p. ej. el titular subsanó); el motor desplaza los plazos."""
    return cases.save(ctx, resume_case(cases.get(ctx, case_id), ctx.profiles, ctx.today(), reviewer, note))
