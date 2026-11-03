"""Trámites posteriores al expediente: prórroga, suspensión, subsanación y decisión humana.

Ninguno se aplica solo: cada función exige a la persona que decide y devuelve una copia
del expediente con el cambio y su evento de auditoría. Las fechas se reciben como
parámetros; el núcleo no lee el reloj del sistema.
"""

from __future__ import annotations

import copy
from datetime import date, datetime
from typing import Any

from .calendar import add_days, count_days
from .engine import append_event, format_instant, nearest_deadline, parse_date
from .errors import CaseInputError, TransitionError
from .profiles import holidays
from .states import DECIDABLE_STATES, OPEN_STATES, check_transition

HUMAN_DECISIONS = frozenset({"APPROVED", "REJECTED", "CANCELLED"})
SUSPENSION_TYPES = frozenset({"additional_information", "request_correction"})
DECISION_LABELS = {"APPROVED": "aprobada", "REJECTED": "rechazada", "CANCELLED": "cancelada"}
CANCELLATION_REASON = (
    "La solicitud no se subsano en plazo (art. 66.2): se propone tenerla por no presentada."
)


def _require(value: str, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseInputError(message)
    return value.strip()


def _profile_for(package: dict[str, Any], profiles: dict[str, Any]) -> dict[str, Any]:
    profile = profiles.get(package["policy"]["policy_id"])
    if not isinstance(profile, dict):
        raise CaseInputError(f"Politica desconocida: {package['policy']['policy_id']}")
    return profile


def _require_open(package: dict[str, Any]) -> None:
    if package["status"] not in OPEN_STATES:
        raise TransitionError(f"No se admite este tramite en estado {package['status']}.")


def ensure_exportable(package: dict[str, Any]) -> None:
    """Un expediente con la identidad sin verificar no se exporta: aún no hay nada entregable."""
    if (package.get("identity_verification") or {}).get("status") != "verified":
        raise TransitionError("No se exporta un expediente con la identidad sin verificar.")


def _shift_deadlines(package: dict[str, Any], days: int, profile: dict[str, Any], right: str | None = None) -> None:
    calendar = holidays(profile)
    for name, item in package["deadlines"].items():
        if right is not None and name != right:
            continue
        item["deadline_at"] = add_days(parse_date(item["deadline_at"]), days, item["day_type"], calendar).isoformat()
        if "legal_deadline_at" in item:
            item["legal_deadline_at"] = add_days(
                parse_date(item["legal_deadline_at"]), days, item["day_type"], calendar
            ).isoformat()
        ceiling = (item.get("extension") or {}).get("legal_ceiling_at")
        if ceiling:
            # Una suspensión posterior a la prórroga desplaza también el tope legal (el plazo legal está suspendido).
            item["extension"]["legal_ceiling_at"] = add_days(
                parse_date(ceiling), days, item["day_type"], calendar).isoformat()
    package["deadline_at"] = nearest_deadline(package["deadlines"])


def extension_terms(package: dict[str, Any], profiles: dict[str, Any], right: str) -> dict[str, Any]:
    """Límites legales de la prórroga de un derecho (D.S. 016-2024-JUS, art. 71.1): una vez y por un plazo igual como máximo.

    El «plazo igual» es el plazo legal (20 días en acceso), no el interno de la organización: la política puede ser más
    estricta, pero la ley fija el tope. El plazo prorrogado nunca pasa del tope legal (plazo legal + plazo legal).
    """
    item = package["deadlines"].get(right)
    if item is None:
        raise CaseInputError(f"El expediente no incluye el derecho {right}.")
    calendar, day_type = holidays(_profile_for(package, profiles)), item["day_type"]
    legal_days = int(item.get("legal_days", item["days"]))
    legal_deadline = parse_date(item.get("legal_deadline_at", item["deadline_at"]))
    current = parse_date(item["deadline_at"])
    if item.get("extended"):
        # Ya prorrogado: el tope quedó guardado (volver a sumar el plazo igual saldría del calendario y no hay nada que decidir).
        ceiling = parse_date((item.get("extension") or {}).get("legal_ceiling_at") or item.get("legal_deadline_at", item["deadline_at"]))
        return {"item": item, "day_type": day_type, "calendar": calendar, "legal_days": legal_days,
                "legal_deadline": legal_deadline, "current": current, "ceiling": ceiling, "max_days": 0, "proposed_days": 0}
    ceiling = add_days(legal_deadline, legal_days, day_type, calendar)
    max_days = max(0, min(legal_days, count_days(current, ceiling, day_type, calendar)))
    return {"item": item, "day_type": day_type, "calendar": calendar, "legal_days": legal_days,
            "legal_deadline": legal_deadline, "current": current, "ceiling": ceiling, "max_days": max_days,
            "proposed_days": min(int(item["days"]), max_days)}


def _check_extension(package: dict[str, Any], right: str, decided_at: date, terms: dict[str, Any]) -> dict[str, Any]:
    _require_open(package)
    extension = package["policy"].get("extension") or {}
    if not extension.get("allowed"):
        raise CaseInputError(f"El perfil {package['policy']['policy_id']} no admite prorroga.")
    if right in extension.get("excluded_rights", []):
        raise CaseInputError(f"La prorroga no aplica al derecho {right}.")
    if terms["item"].get("extended"):
        raise CaseInputError(f"El plazo de {right} ya fue prorrogado una vez.")
    if decided_at > terms["legal_deadline"]:
        raise CaseInputError(
            f"La prorroga debe comunicarse dentro del plazo que se amplia (art. 71.2): hasta {terms['legal_deadline']}.")
    return extension


def upgrade_legacy_extensions(package: dict[str, Any], profiles: dict[str, Any]) -> dict[str, Any]:
    """Completa las prórrogas registradas antes de aplicar el art. 71.1 con el tope legal.

    Esas prórrogas movieron el plazo legal los mismos días concedidos (23/11 + 15 = 16/12) en vez de fijar el tope legal
    (23/11 + 20 = 23/12). Se recalcula el plazo legal original desde la recepción y se rellenan `max_days`,
    `original_legal_deadline_at` y `legal_ceiling_at`. El plazo vigente y la decisión no cambian. Devuelve una copia.
    """
    # Con suspensiones el plazo legal original ya no sale de la recepción: no se recalcula (se muestra sin tope, no uno falso).
    pending = [name for name, item in package.get("deadlines", {}).items()
               if item.get("extended") and not (item.get("extension") or {}).get("legal_ceiling_at")
               and not item.get("suspended_days") and not package.get("suspensions") and not package.get("suspension")]
    if not pending:
        return package
    upgraded = copy.deepcopy(package)
    profile = _profile_for(package, profiles)
    calendar, received = holidays(profile), parse_date(package["received_at"])
    for name in pending:
        item = upgraded["deadlines"][name]
        legal_days = int(item.get("legal_days", item["days"]))
        original_legal = add_days(received, legal_days, item["day_type"], calendar)
        ceiling = add_days(original_legal, legal_days, item["day_type"], calendar)
        item["extension"].update(max_days=legal_days, original_legal_deadline_at=original_legal.isoformat(),
                                 legal_ceiling_at=ceiling.isoformat())
        if "legal_deadline_at" in item:
            item["legal_deadline_at"] = ceiling.isoformat()
    return upgraded


def extension_preview(package: dict[str, Any], profiles: dict[str, Any], right: str, decided_at: date,
                      days: int | None = None) -> dict[str, Any]:
    """Lo que aceptaría `extend_deadline`, sin modificar nada: límites, nueva fecha y, si no se puede, el motivo."""
    try:
        terms = extension_terms(package, profiles, right)
    except CaseInputError as exc:
        # Sin calendario para contar el tope (p. ej. cae en un año sin feriados definidos): se explica, no se rompe.
        item = package["deadlines"].get(right) or {}
        return {"right": right, "day_type": item.get("day_type", "business"), "current_days": item.get("days", 0),
                "current_deadline_at": item.get("deadline_at", ""), "legal_days": item.get("legal_days", item.get("days", 0)),
                "communicate_before": item.get("legal_deadline_at", item.get("deadline_at")), "legal_ceiling_at": None,
                "max_days": 0, "proposed_days": 0, "days": None, "new_deadline_at": None, "allowed": False,
                "reason": str(exc)}
    chosen = terms["proposed_days"] if days is None else days
    result: dict[str, Any] = {
        "right": right, "day_type": terms["day_type"], "current_days": terms["item"]["days"],
        "current_deadline_at": terms["current"].isoformat(), "legal_days": terms["legal_days"],
        "communicate_before": terms["legal_deadline"].isoformat(), "legal_ceiling_at": terms["ceiling"].isoformat(),
        "max_days": terms["max_days"], "proposed_days": terms["proposed_days"], "days": chosen,
        "new_deadline_at": None, "allowed": True, "reason": None,
    }
    try:
        _check_extension(package, right, decided_at, terms)
        if not isinstance(chosen, int) or chosen <= 0 or chosen > terms["max_days"]:
            raise CaseInputError(f"La prorroga debe ser de 1 a {terms['max_days']} dias (plazo igual al legal, art. 71.1).")
        result["new_deadline_at"] = add_days(terms["current"], chosen, terms["day_type"], terms["calendar"]).isoformat()
    except CaseInputError as exc:
        result.update(allowed=False, reason=str(exc))
    return result


def extend_deadline(
    package: dict[str, Any],
    profiles: dict[str, Any],
    right: str,
    reason: str,
    decided_by: str,
    decided_at: date,
    days: int | None = None,
) -> dict[str, Any]:
    """Prórroga del art. 71: una vez, por un plazo igual al legal como máximo, comunicada dentro del plazo que se amplía."""
    decided_by = _require(decided_by, "Indica quien decide la prorroga.")
    reason = _require(reason, "Indica el motivo de la prorroga.")
    terms = extension_terms(package, profiles, right)
    basis = _check_extension(package, right, decided_at, terms).get("basis")
    days = terms["proposed_days"] if days is None else days
    if not isinstance(days, int) or days <= 0 or days > terms["max_days"]:
        raise CaseInputError(f"La prorroga debe ser de 1 a {terms['max_days']} dias (plazo igual al legal, art. 71.1).")

    extended = copy.deepcopy(package)
    target = extended["deadlines"][right]
    original = target["deadline_at"]
    target["deadline_at"] = add_days(terms["current"], days, terms["day_type"], terms["calendar"]).isoformat()
    # Con política aplicada el plazo legal vigente pasa a ser el tope legal; la política solo lo acorta.
    if "legal_deadline_at" in target:
        target["legal_deadline_at"] = terms["ceiling"].isoformat()
    extended["deadline_at"] = nearest_deadline(extended["deadlines"])
    target["extended"] = True
    target["extension"] = {
        "days": days,
        "max_days": terms["max_days"],
        "original_deadline_at": original,
        "original_legal_deadline_at": terms["legal_deadline"].isoformat(),
        "legal_ceiling_at": terms["ceiling"].isoformat(),
        "reason": reason,
        "decided_by": decided_by,
        "decided_at": decided_at.isoformat(),
        "basis": basis,
    }
    append_event(extended, extended["status"],
                 f"Prorroga de {right} por {days} dias decidida por {decided_by}; vence {target['deadline_at']}.")
    return extended


def _suspend(
    package: dict[str, Any], kind: str, started_at: date, due_at: date,
    basis: str | None, reason: str, decided_by: str,
) -> dict[str, Any]:
    if any(item["type"] == kind for item in package.get("suspensions", [])):
        raise CaseInputError("Este tramite ya se uso una vez en el expediente.")
    check_transition(package["status"], "ON_HOLD")
    held = copy.deepcopy(package)
    held["suspension"] = {
        "type": kind,
        "basis": basis,
        "started_at": started_at.isoformat(),
        "suspended_from": started_at.isoformat(),
        "due_at": due_at.isoformat(),
        "previous_status": package["status"],
        "reason": reason,
        "decided_by": decided_by,
        "cancellation_proposed": False,
    }
    held["status"] = "ON_HOLD"
    return held


def request_additional_information(
    package: dict[str, Any],
    profiles: dict[str, Any],
    requested_at: date,
    reason: str,
    decided_by: str,
) -> dict[str, Any]:
    """Requerimiento del art. 70: dentro de 7 días; el titular tiene 10; el plazo se suspende."""
    decided_by = _require(decided_by, "Indica quien decide el requerimiento.")
    reason = _require(reason, "Indica la informacion requerida.")
    _require_open(package)
    profile = _profile_for(package, profiles)
    rule = profile.get("additional_information")
    if not rule:
        raise CaseInputError(f"El perfil {package['policy']['policy_id']} no admite este requerimiento.")
    received = parse_date(package["received_at"])
    day_type, calendar = profile.get("day_type", "calendar"), holidays(profile)
    limit = add_days(received, rule["request_within_days"], day_type, calendar)
    if not received <= requested_at <= limit:
        raise CaseInputError(f"El requerimiento debe hacerse entre {received} y {limit}.")
    due = add_days(requested_at, rule["principal_response_days"], day_type, calendar)
    held = _suspend(package, "additional_information", requested_at, due, rule.get("basis"), reason, decided_by)
    append_event(held, "ON_HOLD",
                 f"Requerimiento de informacion adicional decidido por {decided_by}; "
                 f"plazo suspendido, el titular responde hasta {due}.")
    return held


def observe_request(
    package: dict[str, Any],
    profiles: dict[str, Any],
    observed_at: date,
    missing: str,
    decided_by: str,
) -> dict[str, Any]:
    """Observación del art. 66.2: dentro de 5 días; el titular tiene 5 para subsanar."""
    decided_by = _require(decided_by, "Indica quien observa la solicitud.")
    missing = _require(missing, "Indica que debe subsanarse.")
    _require_open(package)
    profile = _profile_for(package, profiles)
    rule = profile.get("request_correction")
    if not rule:
        raise CaseInputError(f"El perfil {package['policy']['policy_id']} no admite subsanacion.")
    received = parse_date(package["received_at"])
    day_type, calendar = profile.get("day_type", "calendar"), holidays(profile)
    limit = add_days(received, rule["observe_within_days"], day_type, calendar)
    if not received <= observed_at <= limit:
        raise CaseInputError(f"La observacion debe hacerse entre {received} y {limit}.")
    due = add_days(observed_at, rule["cure_days"], day_type, calendar)
    held = _suspend(package, "request_correction", observed_at, due, rule.get("basis"), missing, decided_by)
    append_event(held, "ON_HOLD",
                 f"Solicitud observada por {decided_by}; el titular puede subsanar hasta {due}.")
    return held


def _active_suspension(package: dict[str, Any]) -> dict[str, Any]:
    suspension = package.get("suspension")
    if package["status"] != "ON_HOLD" or not suspension:
        raise TransitionError("El expediente no esta suspendido.")
    return suspension


def resume_case(
    package: dict[str, Any],
    profiles: dict[str, Any],
    resumed_at: date,
    decided_by: str,
    note: str,
) -> dict[str, Any]:
    """Reanuda el trámite y desplaza los plazos los días que estuvo suspendido."""
    decided_by = _require(decided_by, "Indica quien reanuda el tramite.")
    note = _require(note, "Indica el motivo de la reanudacion.")
    suspension = _active_suspension(package)
    start, due = parse_date(suspension["suspended_from"]), parse_date(suspension["due_at"])
    if resumed_at < start:
        raise CaseInputError("La reanudacion no puede ser anterior a la suspension.")
    if suspension["type"] == "request_correction" and resumed_at > due:
        raise CaseInputError("El plazo de subsanacion vencio; corresponde proponer la cancelacion.")
    if suspension["cancellation_proposed"]:
        raise TransitionError("Hay una cancelacion propuesta pendiente de decision humana.")
    check_transition("ON_HOLD", suspension["previous_status"])
    # Si el titular no responde, la suspensión termina al vencer su plazo.
    until = min(resumed_at, due)
    profile = _profile_for(package, profiles)
    days = count_days(start, until, profile.get("day_type", "calendar"), holidays(profile))
    resumed = copy.deepcopy(package)
    _shift_deadlines(resumed, days, profile)
    for item in resumed["deadlines"].values():
        item["suspended_days"] = item.get("suspended_days", 0) + days
    closed = resumed.pop("suspension")
    closed.update({"suspended_until": until.isoformat(), "days_suspended": days,
                   "resumed_by": decided_by, "resume_note": note})
    resumed.setdefault("suspensions", []).append(closed)
    resumed["status"] = suspension["previous_status"]
    append_event(resumed, resumed["status"],
                 f"Tramite reanudado por {decided_by}; plazos desplazados {days} dias.")
    return resumed


def propose_cancellation(package: dict[str, Any], as_of: date) -> dict[str, Any]:
    """Si venció la subsanación sin respuesta, propone CANCELLED; decide una persona."""
    suspension = _active_suspension(package)
    if suspension["type"] != "request_correction":
        raise CaseInputError("Solo una solicitud observada puede proponerse como no presentada.")
    if as_of <= parse_date(suspension["due_at"]):
        raise CaseInputError(f"El plazo de subsanacion vence el {suspension['due_at']}.")
    if suspension["cancellation_proposed"]:
        raise CaseInputError("La cancelacion ya fue propuesta.")
    proposed = copy.deepcopy(package)
    proposed["suspension"]["cancellation_proposed"] = True
    hitl = proposed["hitl"]
    hitl["required"] = True
    if CANCELLATION_REASON not in hitl["reasons"]:
        hitl["reasons"].append(CANCELLATION_REASON)
    append_event(proposed, "ON_HOLD", "Se propone CANCELLED por falta de subsanacion; requiere decision humana.")
    return proposed


def _check_decidable(package: dict[str, Any], decision: str) -> None:
    if decision == "CANCELLED":
        suspension = package.get("suspension") or {}
        if package["status"] != "ON_HOLD" or not suspension.get("cancellation_proposed"):
            raise TransitionError("Solo se puede cancelar una solicitud con cancelacion propuesta.")
        return
    if package["status"] not in DECIDABLE_STATES:
        raise TransitionError(f"No se puede decidir un caso en estado {package['status']}.")


def apply_human_decision(
    package: dict[str, Any],
    reviewer: str,
    decision: str,
    note: str,
    decided_at: datetime,
) -> dict[str, Any]:
    """Única vía a APPROVED, REJECTED o CANCELLED. Nunca ejecuta el derecho."""
    reviewer = _require(reviewer, "Indica quien decide y la justificacion.")
    note = _require(note, "Indica quien decide y la justificacion.")
    if decision not in HUMAN_DECISIONS:
        raise CaseInputError("La decision debe ser APPROVED, REJECTED o CANCELLED.")
    _check_decidable(package, decision)
    check_transition(package["status"], decision)
    decided = copy.deepcopy(package)
    decided["status"] = decision
    if decision == "CANCELLED":
        closed = decided.pop("suspension")
        closed["closed_by_decision"] = decision
        decided.setdefault("suspensions", []).append(closed)
    decided["human_decision"] = {
        "reviewer": reviewer, "decision": decision, "note": note,
        "at": format_instant(decided_at), "approver_required": package["hitl"].get("approver"),
    }
    append_event(decided, decision,
                 f"Propuesta {DECISION_LABELS[decision]} por {reviewer}. No se ejecutaron cambios ni envios.")
    return decided
