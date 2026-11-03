"""Perfiles de jurisdicción: derechos admitidos, plazos legales y calendario."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .calendar import DAY_TYPES
from .errors import CaseInputError

# Derechos que el motor sabe tramitar. Cada perfil decide cuáles admite.
RIGHTS = frozenset({"information", "access", "rectification", "erasure", "portability", "objection"})
# Derechos admitidos cuando el perfil no declara `supported_rights` (perfiles LAB).
DEFAULT_RIGHTS = frozenset({"access", "rectification", "erasure", "portability", "objection"})
MUTATING_RIGHTS = frozenset({"rectification", "erasure", "objection"})
# Orden de atención en solicitudes combinadas: primero se informa y se entrega copia,
# después se modifica.
RIGHT_ORDER = ("information", "access", "portability", "rectification", "objection", "erasure")


def supported_rights(profile: dict[str, Any]) -> frozenset[str]:
    return frozenset(profile.get("supported_rights") or DEFAULT_RIGHTS)


def legal_days(profile: dict[str, Any], right: str) -> int | None:
    by_right = profile.get("response_days_by_right") or {}
    return by_right.get(right, profile.get("response_days"))


def holidays(profile: dict[str, Any]) -> dict[str, list[str]]:
    return profile.get("holidays") or {}


def is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _holiday_errors(profile_id: str, value: Any) -> list[str]:
    if not isinstance(value, dict):
        return [f"{profile_id}: holidays debe ser un objeto con las fechas por anio"]
    errors = []
    for year, days in value.items():
        if not isinstance(days, list):
            errors.append(f"{profile_id}: los feriados de {year} deben ser una lista")
            continue
        for item in days:
            try:
                valid = date.fromisoformat(item).year == int(year)
            except (TypeError, ValueError):
                valid = False
            if not valid:
                errors.append(f"{profile_id}: feriado invalido en {year}: {item}")
    return errors


def _block_errors(profile_id: str, profile: dict[str, Any], name: str, fields: tuple[str, ...]) -> list[str]:
    block = profile.get(name)
    if block is None:
        return []
    if not isinstance(block, dict):
        return [f"{profile_id}: {name} debe ser un objeto"]
    return [f"{profile_id}: {name}.{field} debe ser un entero positivo"
            for field in fields if not is_positive_int(block.get(field))]


def _extension_errors(profile_id: str, extension: Any) -> list[str]:
    if extension is None:
        return []
    if not isinstance(extension, dict) or not isinstance(extension.get("allowed"), bool):
        return [f"{profile_id}: extension.allowed debe ser booleano"]
    if extension["allowed"] and not is_positive_int(extension.get("max_times")):
        return [f"{profile_id}: extension.max_times debe ser un entero positivo"]
    return []


def _profile_errors(profile_id: str, profile: Any) -> list[str]:
    if not isinstance(profile, dict):
        return [f"{profile_id}: el perfil debe ser un objeto"]
    errors = []
    day_type = profile.get("day_type", "calendar")
    if day_type not in DAY_TYPES:
        errors.append(f"{profile_id}: day_type no admitido: {day_type}")
    unknown = sorted(set(profile.get("supported_rights") or []) - RIGHTS)
    if unknown:
        errors.append(f"{profile_id}: derechos desconocidos: {', '.join(unknown)}")
    for right in sorted(supported_rights(profile) & RIGHTS):
        if not is_positive_int(legal_days(profile, right)):
            errors.append(f"{profile_id}: sin plazo valido para {right}")
    errors.extend(_holiday_errors(profile_id, profile.get("holidays", {})))
    if day_type == "business" and not profile.get("holidays"):
        errors.append(f"{profile_id}: un perfil en dias habiles necesita feriados")
    errors.extend(_extension_errors(profile_id, profile.get("extension")))
    errors.extend(_block_errors(profile_id, profile, "additional_information",
                                ("request_within_days", "principal_response_days")))
    errors.extend(_block_errors(profile_id, profile, "request_correction",
                                ("observe_within_days", "cure_days")))
    return errors


def validate_profiles(profiles: Any) -> list[str]:
    if not isinstance(profiles, dict) or not profiles:
        return ["Los perfiles deben ser un objeto no vacio"]
    errors: list[str] = []
    for profile_id in sorted(profiles):
        errors.extend(_profile_errors(profile_id, profiles[profile_id]))
    return errors


def load_profiles(path: Path) -> dict[str, Any]:
    profiles = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_profiles(profiles)
    if errors:
        raise CaseInputError("Perfiles de jurisdiccion invalidos: " + "; ".join(errors))
    return profiles


def resolve_profile(profiles: dict[str, Any], profile_id: str, rights: list[str]) -> dict[str, Any]:
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        raise CaseInputError(f"Politica desconocida: {profile_id}")
    unsupported = [right for right in rights if right not in supported_rights(profile)]
    if unsupported:
        raise CaseInputError(f"La politica {profile_id} no admite: {', '.join(unsupported)}")
    return profile
