"""Hechos minimizados del expediente: lo único del caso que recibe un modelo de lenguaje."""

from __future__ import annotations

from typing import Any

CASE_FIELDS = ("case_id", "request_type", "status", "received_at", "deadline_at", "policy", "hitl", "proposed_action")


def case_facts(package: dict[str, Any] | None) -> dict[str, Any]:
    """Sin registros, valores de datos, `request_text` ni identificadores del titular."""
    if not package:
        return {"case_loaded": False}
    records = package["discovered_records"]
    return {key: package[key] for key in CASE_FIELDS} | {
        "request_types": package.get("request_types", [package["request_type"]]),
        "deadlines": package.get("deadlines", {}),
        "identity_status": package["identity_verification"]["status"],
        "record_count": len(records),
        "redacted_fields": sorted({field for record in records for field in record["redacted_fields"]}),
        "coverage": package.get("coverage"),
        "organization_policy_applied": bool((package.get("organization") or {}).get("applied")),
    }
