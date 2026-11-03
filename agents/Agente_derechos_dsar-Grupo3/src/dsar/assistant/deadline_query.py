"""Plazos sin expediente: extrae fecha, derechos y perfil de la pregunta y los calcula con el motor."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from dsar.core.engine import standalone_deadlines
from dsar.core.errors import CaseInputError
from dsar.rag.lexical import normalize

MONTHS = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
          "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
ISO_DATE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
NUMERIC_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
WRITTEN_DATE = re.compile(r"\b(\d{1,2})[°o]?\s+de\s+(" + "|".join(MONTHS) + r")(?:\s+(?:de|del)\s+(\d{4}))?\b")
DATE_PATTERN = re.compile("|".join(pattern.pattern for pattern in (ISO_DATE, NUMERIC_DATE, WRITTEN_DATE)))
RIGHT_PATTERNS = (
    ("information", re.compile(r"\bderecho (de|a la) informacion\b")),
    ("access", re.compile(r"\bacces\w*|\bcopia de (mis|sus) datos\b")),
    ("portability", re.compile(r"\bportab\w*")),
    ("rectification", re.compile(r"\b(rectific|correg|correccion)\w*")),
    ("objection", re.compile(r"\b(oposicion|oponer|me opongo)\w*")),
    ("erasure", re.compile(r"\b(supresion|suprim|cancelacion|borr|elimin)\w*")),
)
POLICY_PATTERNS = (
    ("LAB-15-REVIEW", re.compile(r"\blab-15\b")),
    ("LAB-30", re.compile(r"\blab-30\b")),
    ("PE-LEY29733", re.compile(r"\b(peru|peruan[oa]s?|pe-ley29733|29733|016-2024-jus)\b")),
)


@dataclass(frozen=True)
class DeadlineQuery:
    received: date
    rights: tuple[str, ...]
    policy_id: str | None


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def received_date(text: str, today: date | None = None) -> date | None:
    normalized = normalize(text)
    if match := ISO_DATE.search(normalized):
        return _safe_date(int(match[1]), int(match[2]), int(match[3]))
    if match := NUMERIC_DATE.search(normalized):
        return _safe_date(int(match[3]), int(match[2]), int(match[1]))
    if match := WRITTEN_DATE.search(normalized):
        year = int(match[3]) if match[3] else (today or date.today()).year
        return _safe_date(year, MONTHS[match[2]], int(match[1]))
    return None


def requested_rights(text: str) -> tuple[str, ...]:
    normalized = normalize(text)
    return tuple(right for right, pattern in RIGHT_PATTERNS if pattern.search(normalized))


def profile_id(text: str) -> str | None:
    normalized = normalize(text)
    return next((policy for policy, pattern in POLICY_PATTERNS if pattern.search(normalized)), None)


def parse(text: str, today: date | None = None) -> DeadlineQuery | None:
    received, rights = received_date(text, today), requested_rights(text)
    if received is None or not rights:
        return None
    return DeadlineQuery(received, rights, profile_id(text))


def deadline_facts(
    question: str,
    package: dict[str, Any] | None,
    profiles: dict[str, Any],
    organization: dict[str, Any] | None = None,
    today: date | None = None,
) -> dict[str, Any] | None:
    """Plazos calculados por el motor para la pregunta, o None si no trae fecha y derecho.

    Perfil: el que nombra la pregunta; si no, el del expediente; si no, el de la organización.
    """
    query = parse(question, today)
    if query is None:
        return None
    policy_id = (query.policy_id or (package or {}).get("policy", {}).get("policy_id")
                 or (organization or {}).get("legal_profile"))
    if not policy_id:
        return None
    try:
        return standalone_deadlines(query.rights, policy_id, profiles, query.received, organization)
    except CaseInputError as exc:
        return {"policy_id": policy_id, "received_at": query.received.isoformat(),
                "request_types": list(query.rights), "error": str(exc)}
