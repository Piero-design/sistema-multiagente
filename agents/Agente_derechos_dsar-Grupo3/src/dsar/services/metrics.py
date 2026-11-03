"""Indicadores del agente: cuentan lo que ya decidieron el motor y las personas. Sin datos personales."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from statistics import mean
from typing import Any

from dsar.core.states import TERMINAL_STATES
from dsar.services.cases import origin_of
from dsar.services.context import ServiceContext

DUE_SOON_DAYS = 3
WEEKS = 8
TOP = 5
DECIDED = frozenset({"APPROVED", "REJECTED"})
IDENTITY_REASON = "La identidad no ha sido verificada"
DISCARD_GROUPS = (("lista blanca", "Remitente fuera de la lista blanca"), ("Respuesta automática", "Envío automático"),
                  ("Cuarentena", "Cuarentena"), ("Descartado por", "Descartado por una persona"))


def _items(counter: Counter[str], limit: int | None = None) -> list[dict[str, Any]]:
    return [{"key": key, "count": count} for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def _ratio(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def _average(values: list[float]) -> float | None:
    return round(mean(values), 1) if values else None


def _local_date(ctx: ServiceContext, instant: str) -> date:
    return (datetime.fromisoformat(instant) + timedelta(hours=ctx.settings.utc_offset_hours)).date()


def _week(day: date) -> str:
    year, week, _ = day.isocalendar()
    return f"{year}-S{week:02d}"


def _weeks(packages: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    """Las últimas semanas hasta hoy, también las que no tuvieron solicitudes (un hueco en el eje engaña)."""
    counts = Counter(_week(date.fromisoformat(item["received_at"])) for item in packages)
    labels = [_week(today - timedelta(weeks=offset)) for offset in range(WEEKS - 1, -1, -1)]
    return [{"key": label, "count": counts[label]} for label in labels]


def _deadlines(ctx: ServiceContext, packages: list[dict[str, Any]], today: date) -> dict[str, Any]:
    open_cases = [item for item in packages if item["status"] not in TERMINAL_STATES]
    remaining = [(date.fromisoformat(item["deadline_at"]) - today).days for item in open_cases]
    decided = [item for item in packages if item["status"] in DECIDED and item.get("human_decision")]
    days = [(_local_date(ctx, item["human_decision"]["at"]) - date.fromisoformat(item["received_at"])).days
            for item in decided]
    within = sum(_local_date(ctx, item["human_decision"]["at"]) <= date.fromisoformat(item["deadline_at"]) for item in decided)
    return {
        "open": len(open_cases),
        "on_time": sum(value > DUE_SOON_DAYS for value in remaining),
        "due_soon": sum(0 <= value <= DUE_SOON_DAYS for value in remaining),
        "overdue": sum(value < 0 for value in remaining),
        "decided": len(decided),
        "decided_within": within,
        "within_pct": _ratio(within, len(decided)),
        "avg_resolution_days": _average(days),
        "extensions": sum(bool(item.get("extended")) for package in packages for item in package["deadlines"].values()),
        "suspensions": sum(bool(package.get("suspension") or package.get("suspensions")) for package in packages),
    }


def _hitl(packages: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [item for item in packages if item["identity_verification"].get("status") == "verified"]
    required = [item for item in verified if item["hitl"].get("required")]
    reasons = Counter(reason for item in required for reason in item["hitl"]["reasons"] if IDENTITY_REASON not in reason)
    decisions = Counter(item["human_decision"]["decision"] for item in packages if item.get("human_decision"))
    return {"verified": len(verified), "required": len(required), "required_pct": _ratio(len(required), len(verified)),
            "top_reasons": _items(reasons, TOP), "decisions": _items(decisions)}


def _identity(packages: list[dict[str, Any]], today: date) -> dict[str, Any]:
    pending = [item for item in packages if item["status"] == "IDENTITY_PENDING"]
    ages = [(today - date.fromisoformat(item["received_at"])).days for item in pending]
    return {"pending": len(pending), "avg_age_days": _average(ages)}


def _discard_group(reason: str | None) -> str:
    return next((label for marker, label in DISCARD_GROUPS if marker in (reason or "")), "No es una solicitud")


def _mail(ctx: ServiceContext, cases_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    inbound = ctx.repository.list_inbound(limit=100_000)
    registered = [item for item in inbound if item["status"] == "registrado"]
    confirmed = [item for item in registered if item["decided_by"] and ((item["proposal"] or {}).get("model"))]
    corrected = sum(set(cases_by_id.get(item["case_id"], {}).get("request_types", []))
                    != set(item["proposal"]["model"]["rights"]) for item in confirmed)
    times = [item["analysis_s"] for item in inbound if item["analysis_s"] is not None]
    return {
        "by_status": _items(Counter(item["status"] for item in inbound)),
        "auto_registered": sum(not item["decided_by"] for item in registered),
        "triage_registered": sum(bool(item["decided_by"]) for item in registered),
        "model_confirmed": len(confirmed) - corrected,
        "model_corrected": corrected,
        "discard_reasons": _items(Counter(_discard_group(item["reason"]) for item in inbound if item["status"] == "descartado")),
        "avg_analysis_s": round(mean(times), 2) if times else None,
    }


def _llm(ctx: ServiceContext) -> dict[str, Any]:
    calls = ctx.repository.list_llm_calls(limit=100_000)
    latencies = [item["latency_s"] for item in calls if item["latency_s"] is not None]
    return {"calls": len(calls), "errors": sum(not item["ok"] for item in calls),
            "avg_latency_s": round(mean(latencies), 2) if latencies else None,
            "by_task": _items(Counter(item["task"] or "chat" for item in calls))}


def indicators(ctx: ServiceContext) -> dict[str, Any]:
    today = ctx.today()
    packages = ctx.repository.all_cases()
    outbox = Counter(item["status"] for item in ctx.repository.list_outbox())
    return {
        "as_of": today.isoformat(),
        "cases_total": len(packages),
        "by_status": _items(Counter(item["status"] for item in packages)),
        "by_right": _items(Counter(right for item in packages for right in item["request_types"])),
        "by_origin": _items(Counter(origin_of(item["case_id"]) for item in packages)),
        "by_week": _weeks(packages, today) if packages else [],
        "deadlines": _deadlines(ctx, packages, today),
        "hitl": _hitl(packages),
        "identity": _identity(packages, today),
        "mail": _mail(ctx, {item["case_id"]: item for item in packages}),
        "outbox": {"drafts": outbox["borrador"], "sent": outbox["enviado"], "discarded": outbox["descartado"]},
        "llm": _llm(ctx),
    }
