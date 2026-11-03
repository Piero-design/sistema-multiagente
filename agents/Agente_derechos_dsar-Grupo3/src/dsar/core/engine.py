"""Motor determinista: construye el expediente DSAR a partir de entradas sintéticas.

Función pura: no lee archivos, red ni la fecha del sistema. La fecha de recepción va en la
solicitud y el instante de generación se recibe como parámetro.
"""

from __future__ import annotations

import copy
from datetime import date, datetime, timedelta
from typing import Any

from .calendar import add_days
from .errors import CaseInputError
from .policy import apply_org_deadlines, ensure_valid_org_policy, org_policy_hash
from .profiles import MUTATING_RIGHTS, RIGHT_ORDER, RIGHTS, holidays, legal_days, resolve_profile
from .states import check_transition

DISCLAIMER = (
    "Demostracion academica con datos sinteticos. No ejecuta cambios ni envia comunicaciones "
    "por su cuenta: un correo al titular solo sale cuando una persona lo envia. "
    "No constituye asesoramiento legal."
)
DEFAULT_APPROVER = "Responsable de privacidad (DPO)"
ACTION_DESCRIPTIONS = {
    "information": "Preparar la informacion sobre finalidades, destinatarios, conservacion y derechos.",
    "access": "Preparar una copia revisada de la PII localizada.",
    "portability": "Preparar una exportacion estructurada y legible por maquina.",
    "rectification": "Proponer correcciones; no actualizar sistemas sin aprobacion y evidencia.",
    "erasure": "Proponer supresion o desidentificacion tras revisar retencion y excepciones.",
    "objection": "Proponer restriccion o cese de la finalidad objetada tras revision.",
}
EMPTY_RAG = {
    "enabled": False,
    "method": "No configurado",
    "query": "",
    "documents_indexed": 0,
    "chunks_indexed": 0,
    "retrieved_chunks": [],
}


def require_text(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise CaseInputError(f"Campo obligatorio invalido: {field}")
    return value.strip()


def parse_date(value: str, field: str = "received_at") -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CaseInputError(f"{field} debe usar YYYY-MM-DD") from exc


def format_instant(value: datetime) -> str:
    if value.tzinfo is None:
        raise CaseInputError("El instante debe incluir zona horaria")
    return value.replace(microsecond=0).isoformat()


def event(sequence: int, state: str, description: str) -> dict[str, Any]:
    return {"sequence": sequence, "state": state, "description": description}


def append_event(package: dict[str, Any], state: str, description: str) -> None:
    trail = package["audit_trail"]
    trail.append(event(len(trail) + 1, state, description))


def resolve_rights(request: dict[str, Any]) -> list[str]:
    """Normaliza `request_types` (lista) o `request_type` (texto) a una lista ordenada."""
    raw = request.get("request_types")
    if raw is None:
        raw = [require_text(request, "request_type")]
    if not isinstance(raw, list) or not raw:
        raise CaseInputError("request_types debe ser una lista no vacia")
    rights: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise CaseInputError("request_types contiene un valor invalido")
        right = item.strip().lower()
        if right not in RIGHTS:
            raise CaseInputError(f"request_type no admitido: {right}")
        if right not in rights:
            rights.append(right)
    return sorted(rights, key=RIGHT_ORDER.index)


def compute_deadlines(
    rights: list[str], profile: dict[str, Any], received: date
) -> dict[str, dict[str, Any]]:
    day_type = profile.get("day_type", "calendar")
    deadlines: dict[str, dict[str, Any]] = {}
    for right in rights:
        days = legal_days(profile, right)
        if not isinstance(days, int) or days <= 0:
            raise CaseInputError(f"La politica no define un plazo valido para {right}")
        deadlines[right] = {
            "days": days,
            "day_type": day_type,
            "deadline_at": add_days(received, days, day_type, holidays(profile)).isoformat(),
            "legal_basis": (profile.get("legal_basis") or {}).get(right),
        }
    return deadlines


def nearest_deadline(deadlines: dict[str, dict[str, Any]]) -> str:
    # El plazo global del expediente es el más cercano de los derechos solicitados.
    return min(item["deadline_at"] for item in deadlines.values())


def standalone_deadlines(
    request_types: list[str] | tuple[str, ...],
    policy_id: str,
    profiles: dict[str, Any],
    received: date,
    organization: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plazos de una solicitud hipotética, sin expediente."""
    rights = resolve_rights({"request_types": list(request_types)})
    profile = resolve_profile(profiles, policy_id, rights)
    deadlines = compute_deadlines(rights, profile, received)
    applied = bool(organization) and organization.get("legal_profile") == policy_id
    if applied:
        ensure_valid_org_policy(organization, profiles)
        apply_org_deadlines(deadlines, organization, profile, received)
    return {
        "policy_id": policy_id,
        "request_types": rights,
        "received_at": received.isoformat(),
        "counted_from": (received + timedelta(days=1)).isoformat(),
        "day_type": profile.get("day_type", "calendar"),
        "deadlines": deadlines,
        "deadline_at": nearest_deadline(deadlines),
        "organization_applied": applied,
        "warnings": [],
        "disclaimer": profile.get("disclaimer", "Politica sin nota explicativa."),
    }


def redact_record(record: dict[str, Any], confidential_fields: set[str] | None = None) -> dict[str, Any]:
    """Prepara un registro entregable: retira campos de terceros y confidenciales."""
    prepared = {
        "record_id": require_text(record, "record_id"),
        "source_system": require_text(record, "source_system"),
        "category": require_text(record, "category"),
        "sensitive": bool(record.get("sensitive", False)),
        "data": copy.deepcopy(record.get("data", {})),
        "redacted_fields": [],
        "restrictions": list(record.get("restrictions", [])),
    }
    if not isinstance(prepared["data"], dict):
        raise CaseInputError(f"data debe ser un objeto en {prepared['record_id']}")
    for field in record.get("third_party_fields", []):
        if field in prepared["data"]:
            prepared["data"].pop(field)
            prepared["redacted_fields"].append(field)
    prepared["confidential_fields"] = []
    for field in sorted(confidential_fields or set()):
        if field in prepared["data"]:
            prepared["data"].pop(field)
            prepared["redacted_fields"].append(field)
            prepared["confidential_fields"].append(field)
    return prepared


def discover_records(
    records: list[dict[str, Any]], principal_id: str, org: dict[str, Any] | None
) -> list[dict[str, Any]]:
    """Búsqueda exacta por titular; nunca por texto libre."""
    confidential = set((org or {}).get("always_confidential_fields", []))
    return [redact_record(record, confidential)
            for record in records if record.get("principal_id") == principal_id]


def choose_approver(rights: list[str], org: dict[str, Any] | None) -> str:
    approvers = (org or {}).get("approvers") or {}
    for right in rights:
        if right in MUTATING_RIGHTS and right in approvers:
            return approvers[right]
    return approvers.get("default", DEFAULT_APPROVER)


def proposed_action(right: str) -> dict[str, Any]:
    return {"type": right, "description": ACTION_DESCRIPTIONS[right], "executed": False}


def _organization_summary(
    organization: dict[str, Any], profiles: dict[str, Any], policy_id: str
) -> dict[str, Any]:
    ensure_valid_org_policy(organization, profiles)
    applied = organization["legal_profile"] == policy_id
    warnings = [] if applied else [
        f"La politica de la organizacion corresponde a {organization['legal_profile']}; "
        f"no se aplico al perfil {policy_id}."
    ]
    return {
        "org_id": organization["org_id"],
        "name": organization["name"],
        "version": organization["version"],
        "legal_profile": organization["legal_profile"],
        "sha256": org_policy_hash(organization),
        "applied": applied,
        "warnings": warnings,
    }


def _identity_summary(request: dict[str, Any]) -> dict[str, Any]:
    identity = request.get("identity_verification")
    if not isinstance(identity, dict):
        raise CaseInputError("Falta identity_verification")
    return {
        "status": require_text(identity, "status").lower(),
        "method": identity.get("method"),
        "reference": identity.get("reference"),
    }


def _coverage(matched: list[dict[str, Any]], org: dict[str, Any] | None) -> dict[str, Any]:
    found = sorted({item["source_system"] for item in matched})
    expected = sorted(set((org or {}).get("systems_to_query", [])))
    return {
        "expected_systems": expected,
        "found_systems": found,
        "missing_systems": [item for item in expected if item not in found],
    }


def hitl_reasons(package: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    """Motivos de aprobación humana de un expediente con identidad verificada."""
    rights = package["request_types"]
    matched = package["discovered_records"]
    reasons: list[str] = []
    if any(right in MUTATING_RIGHTS for right in rights):
        reasons.append("El derecho solicitado puede modificar o restringir el tratamiento.")
    if len(rights) > 1:
        reasons.append("Solicitud combinada: confirmar el orden de atencion y cada plazo.")
    if any(item["sensitive"] for item in matched):
        reasons.append("El expediente contiene categorias marcadas como sensibles.")
    if any(item["redacted_fields"] for item in matched):
        reasons.append("Se detectaron campos de terceros que requieren revision.")
    if any(item["restrictions"] for item in matched):
        reasons.append("Existen restricciones o conflictos de retencion pendientes de evaluar.")
    if any(item["confidential_fields"] for item in matched):
        reasons.append("Se retiraron campos confidenciales segun la politica de la organizacion.")
    if package["coverage"]["missing_systems"]:
        reasons.append(
            "Sistemas declarados sin registros del titular: "
            + ", ".join(package["coverage"]["missing_systems"])
            + ". Confirmar cobertura con el Agente de Inventario."
        )
    if bool(profile.get("legal_review_required", False)):
        reasons.append("La politica configurada exige revision especializada.")
    return reasons


def build_case(
    request: dict[str, Any],
    records: list[dict[str, Any]],
    profiles: dict[str, Any],
    *,
    generated_at: datetime,
    source_hashes: dict[str, str] | None = None,
    rag_context: dict[str, Any] | None = None,
    organization: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request_id = require_text(request, "request_id")
    principal_id = require_text(request, "principal_id")
    rights = resolve_rights(request)
    request_type = rights[0]
    policy_id = require_text(request, "policy_id")
    received_at = parse_date(require_text(request, "received_at"))

    profile = resolve_profile(profiles, policy_id, rights)
    deadlines = compute_deadlines(rights, profile, received_at)
    org_summary = None
    if organization is not None:
        org_summary = _organization_summary(organization, profiles, policy_id)
    active_org = organization if org_summary and org_summary["applied"] else None
    if active_org:
        apply_org_deadlines(deadlines, active_org, profile, received_at)
    identity = _identity_summary(request)
    approver = choose_approver(rights, active_org)

    package: dict[str, Any] = {
        "case_id": request_id,
        "principal_id": principal_id,
        "request_type": request_type,
        "request_types": rights,
        "received_at": received_at.isoformat(),
        "policy": {
            "policy_id": policy_id,
            "label": profile.get("label", policy_id),
            "jurisdiction": profile.get("jurisdiction", "LAB"),
            "day_type": profile.get("day_type", "calendar"),
            "response_days": deadlines[request_type]["days"],
            "extension": profile.get("extension"),
            "disclaimer": profile.get("disclaimer", "Politica sin nota explicativa."),
        },
        "deadlines": deadlines,
        "deadline_at": nearest_deadline(deadlines),
        "organization": org_summary,
        "identity_verification": identity,
        "status": "TRIAGED",
        "discovered_records": [],
        "source_systems": [],
        "hitl": {"required": False, "reasons": [], "approver": approver},
        "proposed_action": proposed_action(request_type),
        "proposed_actions": [proposed_action(right) for right in rights],
        "audit_trail": [
            event(1, "RECEIVED", "Solicitud registrada."),
            event(2, "TRIAGED", f"Derechos clasificados ({', '.join(rights)}) con la politica {policy_id}."),
        ],
        "source_hashes": dict(source_hashes or {}),
        "rag": copy.deepcopy(rag_context) if rag_context else copy.deepcopy(EMPTY_RAG),
        "generated_at": format_instant(generated_at),
        "disclaimer": DISCLAIMER,
    }

    if identity["status"] != "verified":
        # Invariante 1: sin identidad verificada no se busca ningún registro.
        package["status"] = "IDENTITY_PENDING"
        package["hitl"] = {
            "required": True,
            "reasons": ["La identidad no ha sido verificada por un mecanismo autorizado."],
            "approver": approver,
        }
        append_event(package, "IDENTITY_PENDING", "Descubrimiento bloqueado hasta verificar identidad.")
        return package

    append_event(package, "VERIFIED", "Verificacion externa confirmada.")
    _discover_and_route(package, records, profile, active_org)
    return package


def _discover_and_route(
    package: dict[str, Any], records: list[dict[str, Any]], profile: dict[str, Any], active_org: dict[str, Any] | None
) -> None:
    matched = discover_records(records, package["principal_id"], active_org)
    package["discovered_records"] = matched
    package["source_systems"] = sorted({item["source_system"] for item in matched})
    package["coverage"] = _coverage(matched, active_org)
    append_event(package, "DISCOVERY", f"Se localizaron {len(matched)} registros sinteticos.")

    approver = package["hitl"]["approver"]
    reasons = hitl_reasons(package, profile)
    if reasons:
        package["status"] = "APPROVAL_REQUIRED"
        package["hitl"] = {"required": True, "reasons": reasons, "approver": approver}
        append_event(package, "APPROVAL_REQUIRED", "El caso requiere decision humana.")
    else:
        package["status"] = "REVIEW"
        package["hitl"] = {"required": False, "reasons": [], "approver": approver}
        append_event(package, "REVIEW", "Borrador preparado para revision humana.")


def verify_identity(
    package: dict[str, Any],
    records: list[dict[str, Any]],
    profiles: dict[str, Any],
    *,
    verified_by: str,
    method: str,
    reference: str,
    verified_at: datetime,
    organization: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Una persona verifica la identidad de un caso en IDENTITY_PENDING y el motor continúa el trámite."""
    verified_by = require_text({"verified_by": verified_by}, "verified_by")
    method = require_text({"method": method}, "method")
    check_transition(package["status"], "VERIFIED")
    summary = package.get("organization") or {}
    active_org = None
    if summary.get("applied"):
        if organization is None or org_policy_hash(organization) != summary.get("sha256"):
            raise CaseInputError(
                "La politica de la organizacion cambio desde el registro; registra la solicitud de nuevo.")
        active_org = organization
    profile = resolve_profile(profiles, package["policy"]["policy_id"], package["request_types"])

    verified = copy.deepcopy(package)
    verified["identity_verification"] = {
        "status": "verified", "method": method, "reference": (reference or "").strip() or None,
        "verified_by": verified_by, "verified_at": format_instant(verified_at),
    }
    append_event(verified, "VERIFIED", f"Identidad verificada por {verified_by} ({method}).")
    _discover_and_route(verified, records, profile, active_org)
    return verified
