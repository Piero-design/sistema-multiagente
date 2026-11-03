"""Registro y consulta de expedientes."""

from __future__ import annotations

import json
from datetime import date
from typing import Any
from uuid import uuid4

from dsar.assistant.facts import case_facts
from dsar.assistant.guided import RIGHT_LABELS
from dsar.assistant.query import CASE_CANDIDATES
from dsar.core.engine import build_case, resolve_rights, standalone_deadlines, verify_identity as engine_verify_identity
from dsar.core.errors import CaseInputError
from dsar.core.procedures import upgrade_legacy_extensions
from dsar.core.hashing import sha256_file, sha256_text
from dsar.core.render import render_response
from dsar.core.states import ALLOWED_STATES, TERMINAL_STATES
from dsar.core.validator import validate
from dsar.paths import SKILL_PATH, display_path
from dsar.rag.applicability import applicable_chunks
from dsar.rag.relevance import visible_chunks
from dsar.services.context import ServiceContext
from dsar.services.errors import NotFoundError, check_case_id

ORIGINS = frozenset({"API", "MCP", "EMAIL"})
SKILL_CONTROLS = ["Verificación de identidad", "Minimización y datos de terceros", "Plazo desde política",
                  "Acción propuesta no ejecutada", "Revisión humana"]


def new_case_id(origin: str = "API") -> str:
    if origin not in ORIGINS:
        raise ValueError(f"Origen desconocido: {origin}")
    return f"DSAR-{origin}-{uuid4().hex[:12].upper()}"


def json_hash(payload: Any) -> str:
    return sha256_text(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def rag_query(request: dict[str, Any]) -> str:
    """Consulta estructurada (derechos + identidad): el texto libre nunca orienta la recuperación."""
    rights = resolve_rights(request)
    labels = " ".join(RIGHT_LABELS.get(right, right) for right in rights)
    verified = (request.get("identity_verification") or {}).get("status") == "verified"
    identity = "identidad verificada" if verified else "identidad pendiente bloqueo"
    return f"{labels} solicitud derechos titular {identity} revisión humana"


def skill_applied(package: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "dsar-rights",
        "path": display_path(SKILL_PATH),
        "sha256": sha256_file(SKILL_PATH),
        "steps": [item["description"] for item in package["audit_trail"]],
        "controls": SKILL_CONTROLS,
    }


CASE_SOURCES = 3


def _case_rag_context(ctx: ServiceContext, payload: dict[str, Any]) -> dict[str, Any]:
    """Fundamento del expediente: solo los de relevancia alta (y el primero). En el chat basta «media»; aquí se queda
    en el expediente y en el borrador, y un fragmento a medias (p. ej. la tabla de estados) es ruido."""
    policy_id = payload.get("policy_id")
    organization = ctx.organization()
    applied = bool(organization) and organization.get("legal_profile") == policy_id
    # Se recupera de más para que, al quitar los fragmentos de otro perfil, queden tres que aplican.
    context = ctx.retrieve(rag_query(payload), top_k=CASE_CANDIDATES)
    applicable = applicable_chunks(context["retrieved_chunks"], policy_id, applied)
    context["retrieved_chunks"] = visible_chunks(applicable, minimum="alta")[:CASE_SOURCES]
    return context


def register(ctx: ServiceContext, request: dict[str, Any], origin: str = "API") -> dict[str, Any]:
    """Valida la solicitud, construye el expediente con el motor, lo valida y lo guarda."""
    payload = dict(request) | {"request_id": new_case_id(origin)}
    settings = ctx.settings
    package = build_case(
        payload, ctx.records(), ctx.profiles,
        generated_at=ctx.now(),
        source_hashes={"request": json_hash(payload), "data": sha256_file(settings.records_path),
                       "policies": sha256_file(settings.profiles_path)},
        rag_context=_case_rag_context(ctx, payload),
        organization=ctx.organization(),
    )
    package["skill_applied"] = skill_applied(package)
    errors = validate(package)
    if errors:
        raise CaseInputError("Expediente invalido: " + "; ".join(errors))
    ctx.repository.save_case(package, payload)
    return {"case": package, "draft": render_response(package)}


def get(ctx: ServiceContext, case_id: str) -> dict[str, Any]:
    package = ctx.repository.get_case(check_case_id(case_id))
    if package is None:
        raise NotFoundError(f"No existe el expediente {case_id}.")
    # Prórrogas anteriores a la corrección del art. 71.1: se completan al leer (se guardan al próximo trámite).
    return upgrade_legacy_extensions(package, ctx.profiles)


def payload(ctx: ServiceContext, case_id: str) -> dict[str, Any] | None:
    return ctx.repository.get_payload(check_case_id(case_id))


def list_cases(ctx: ServiceContext, status: str | None = None) -> list[dict[str, Any]]:
    if status is not None and status not in ALLOWED_STATES:
        raise CaseInputError(f"Estado desconocido: {status}")
    # `open`: el expediente aún espera una resolución (la interfaz solo cuenta días restantes en esos casos).
    return [row | {"open": row["status"] not in TERMINAL_STATES, "origin": origin_of(row["case_id"])}
            for row in ctx.repository.list_cases(status)]


def origin_of(case_id: str) -> str:
    return case_id.split("-")[1]


def verify_identity(ctx: ServiceContext, case_id: str, verified_by: str, method: str,
                    reference: str = "") -> dict[str, Any]:
    """Una persona verifica la identidad; el motor busca los registros y deja el caso listo para decidir."""
    package = get(ctx, case_id)
    verified = engine_verify_identity(
        package, ctx.records(), ctx.profiles, verified_by=verified_by, method=method, reference=reference,
        verified_at=ctx.now(), organization=ctx.organization())
    request = (payload(ctx, case_id) or {}) | {"identity_verification": verified["identity_verification"]}
    verified["rag"] = _case_rag_context(ctx, request)
    verified["skill_applied"] = skill_applied(verified)
    errors = validate(verified)
    if errors:
        raise CaseInputError("Expediente invalido: " + "; ".join(errors))
    ctx.repository.save_case(verified, request)
    return {"case": verified, "draft": render_response(verified)}


def save(ctx: ServiceContext, package: dict[str, Any]) -> dict[str, Any]:
    """Guarda un expediente modificado por un trámite; antes lo pasa por el validador."""
    errors = validate(package)
    if errors:
        raise CaseInputError("Expediente invalido: " + "; ".join(errors))
    ctx.repository.save_case(package)
    return package


def deadlines(ctx: ServiceContext, rights: list[str], received: date, profile_id: str | None) -> dict[str, Any]:
    """Plazos sin expediente; sin perfil, el de la política de la organización."""
    organization = ctx.organization()
    profile_id = profile_id or (organization or {}).get("legal_profile")
    if not profile_id:
        raise CaseInputError("Indica el perfil de jurisdiccion.")
    return standalone_deadlines(rights, profile_id, ctx.profiles, received, organization)


def summary(package: dict[str, Any]) -> dict[str, Any]:
    """Hechos minimizados + aprobador, decisión, handoffs y cobertura; nunca registros ni valores."""
    return case_facts(package) | {
        "approver": package["hitl"].get("approver"),
        "human_decision": package.get("human_decision"),
        "handoffs": package.get("handoffs", []),
        "coverage": package.get("coverage"),
        "organization": package.get("organization"),
    }
