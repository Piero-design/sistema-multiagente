"""Cómputo de plazos en días naturales o hábiles."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, timedelta

from .errors import CaseInputError

DAY_TYPES = ("calendar", "business")
# Feriados por año: {"2026": ["2026-01-01", ...]}.
Holidays = Mapping[str, Iterable[str]]


class CalendarError(CaseInputError):
    """No hay datos de calendario suficientes para contar el plazo."""


def _holidays_for(year: int, holidays: Holidays | None) -> set[str]:
    key = str(year)
    if not holidays or key not in holidays:
        raise CalendarError(
            f"El perfil no define feriados para {year}; no se pueden contar dias habiles."
        )
    return set(holidays[key])


def _check_day_type(day_type: str) -> None:
    if day_type not in DAY_TYPES:
        raise CaseInputError(f"day_type no admitido: {day_type}")


def is_counted_day(day: date, day_type: str, holidays: Holidays | None = None) -> bool:
    _check_day_type(day_type)
    if day_type == "calendar":
        return True
    return day.weekday() < 5 and day.isoformat() not in _holidays_for(day.year, holidays)


def add_days(start: date, days: int, day_type: str, holidays: Holidays | None = None) -> date:
    """Suma el plazo contando desde el día siguiente a `start` (D.S. 016-2024-JUS, art. 69)."""
    _check_day_type(day_type)
    if days < 0:
        raise CaseInputError("El numero de dias no puede ser negativo")
    if day_type == "calendar":
        return start + timedelta(days=days)
    current, counted = start, 0
    while counted < days:
        current += timedelta(days=1)
        if is_counted_day(current, day_type, holidays):
            counted += 1
    return current


def count_days(start: date, end: date, day_type: str, holidays: Holidays | None = None) -> int:
    """Días contables en el intervalo (start, end]."""
    _check_day_type(day_type)
    if end <= start:
        return 0
    if day_type == "calendar":
        return (end - start).days
    current, counted = start, 0
    while current < end:
        current += timedelta(days=1)
        if is_counted_day(current, day_type, holidays):
            counted += 1
    return counted
