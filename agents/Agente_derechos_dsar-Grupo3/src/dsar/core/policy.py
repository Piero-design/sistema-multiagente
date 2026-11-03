"""Política de la organización: puede acortar plazos legales, nunca alargarlos."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .calendar import add_days
from .errors import CaseInputError
from .hashing import sha256_json
from .profiles import RIGHTS, holidays, is_positive_int, legal_days, supported_rights

ORG_REQUIRED = frozenset({"org_id", "name", "version", "legal_profile"})


def org_policy_hash(org: dict[str, Any]) -> str:
    return sha256_json(org)


def _legal_limit_errors(org: dict[str, Any], profiles: dict[str, Any]) -> list[str]:
    profile = profiles.get(org["legal_profile"])
    if not isinstance(profile, dict):
        return [f"Perfil legal desconocido: {org['legal_profile']}"]
    errors = []
    for right, value in sorted(org.get("internal_response_days_by_right", {}).items()):
        if right not in supported_rights(profile):
            errors.append(f"El perfil {org['legal_profile']} no admite el derecho {right}")
            continue
        legal = legal_days(profile, right)
        if value > legal:
            errors.append(
                f"El plazo interno de {right} ({value}) supera el legal ({legal}); "
                "la politica no puede alargar un plazo legal"
            )
    return errors


def validate_org_policy(org: Any, profiles: dict[str, Any] | None = None) -> list[str]:
    """Comprueba la forma de la política y, con los perfiles, que no alargue plazos legales."""
    if not isinstance(org, dict):
        return ["La politica de la organizacion debe ser un objeto JSON"]
    errors = [f"Falta el campo {field}" for field in sorted(ORG_REQUIRED - org.keys())]
    days = org.get("internal_response_days_by_right", {})
    if not isinstance(days, dict):
        errors.append("internal_response_days_by_right debe ser un objeto")
    else:
        for right, value in days.items():
            if right not in RIGHTS:
                errors.append(f"Derecho desconocido en plazos internos: {right}")
            if not is_positive_int(value):
                errors.append(f"Plazo interno invalido para {right}")
    for field in ("always_confidential_fields", "systems_to_query"):
        value = org.get(field, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"{field} debe ser una lista de textos")
    approvers = org.get("approvers", {})
    if not isinstance(approvers, dict) or (approvers and "default" not in approvers):
        errors.append("approvers debe ser un objeto con la clave default")
    if profiles is not None and not errors:
        errors.extend(_legal_limit_errors(org, profiles))
    return errors


def ensure_valid_org_policy(org: Any, profiles: dict[str, Any]) -> None:
    errors = validate_org_policy(org, profiles)
    if errors:
        raise CaseInputError("Politica de la organizacion invalida: " + "; ".join(errors))


def load_org_policy(path: Path, profiles: dict[str, Any]) -> dict[str, Any]:
    org = json.loads(path.read_text(encoding="utf-8"))
    ensure_valid_org_policy(org, profiles)
    return org


def apply_org_deadlines(
    deadlines: dict[str, dict[str, Any]],
    org: dict[str, Any],
    profile: dict[str, Any],
    received: date,
) -> None:
    """Aplica los plazos internos más estrictos y conserva el legal en `legal_*`."""
    internal = org.get("internal_response_days_by_right", {})
    for right, item in deadlines.items():
        item["legal_days"] = item["days"]
        item["legal_deadline_at"] = item["deadline_at"]
        item["source"] = "perfil legal"
        days = internal.get(right)
        if days is None or days == item["legal_days"]:
            continue
        if days > item["legal_days"]:
            # Ya lo impide ensure_valid_org_policy; se repite por defensa.
            raise CaseInputError(f"El plazo interno de {right} supera el legal")
        item["days"] = days
        item["deadline_at"] = add_days(received, days, item["day_type"], holidays(profile)).isoformat()
        item["source"] = "política interna (más estricta que la ley)"
