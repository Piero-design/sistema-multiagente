"""Handoffs: lo que el Agente DSAR entrega a otros agentes del PIMS.

Cada handoff es un sobre JSON con un formato común. Nunca lleva valores de datos personales:
solo referencias, sistemas, nombres de campos y hashes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MUTATING_RIGHTS = frozenset({"rectification", "erasure", "objection"})
DECIDED_STATES = frozenset({"APPROVED", "REJECTED", "CANCELLED"})
EVIDENCE_CONTROLS = ["A.1.3.7", "A.1.3.9", "A.1.3.10", "A.3.14", "A.3.25"]


def package_hash(package: dict[str, Any]) -> str:
    canonical = json.dumps(package, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def envelope(package: dict[str, Any], to_agent: str, control_ref: str, action: str,
             payload: dict[str, Any], requires_hitl: bool, created_at: str) -> dict[str, Any]:
    body = {
        "from_agent": "dsar",
        "to_agent": to_agent,
        "case_ref": package["case_id"],
        "control_ref": control_ref,
        "action": action,
        "payload": payload,
        "requires_hitl": requires_hitl,
        "created_at": created_at,
    }
    body["sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return body


def build_handoffs(package: dict[str, Any], created_at: str) -> list[dict[str, Any]]:
    """Handoffs de un expediente con decisión humana: Evidencia siempre; Terceros e Inventario si aplican."""
    if package["status"] not in DECIDED_STATES:
        return []
    rights = package.get("request_types") or [package["request_type"]]
    records = package["discovered_records"]
    systems = sorted({item["source_system"] for item in records})
    result = [envelope(package, "evidencia", "A.3.14", "archivar_expediente", {
        "status": package["status"],
        "request_types": rights,
        "policy_id": package["policy"]["policy_id"],
        "package_sha256": package_hash(package),
        "audit_events": len(package["audit_trail"]),
        "decided_by": package["human_decision"]["reviewer"],
        "controls": EVIDENCE_CONTROLS,
    }, requires_hitl=False, created_at=created_at)]
    mutating = [right for right in rights if right in MUTATING_RIGHTS]
    if package["status"] == "APPROVED" and mutating and systems:
        result.append(envelope(package, "terceros", "A.1.3.8", "notificar_destinatarios", {
            "rights": mutating,
            "source_systems": systems,
            "fields": sorted({field for item in records for field in item["data"]}),
            "note": "Identificar destinatarios con los registros de transferencias (A.1.5.4) y monitorear acuse.",
        }, requires_hitl=True, created_at=created_at))
    missing = (package.get("coverage") or {}).get("missing_systems") or []
    if missing:
        result.append(envelope(package, "inventario", "A.1.2.9", "confirmar_cobertura",
                               {"missing_systems": missing, "found_systems": systems},
                               requires_hitl=False, created_at=created_at))
    return result


def summary(handoff: dict[str, Any]) -> dict[str, Any]:
    return {key: handoff[key] for key in ("to_agent", "control_ref", "action", "sha256")}


def write_handoffs(handoffs: list[dict[str, Any]], base: Path) -> list[Path]:
    """Un archivo por agente en `<base>/<case_id>/<agente>.json`."""
    paths = []
    for item in handoffs:
        folder = base / item["case_ref"].lower()
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / f"{item['to_agent']}.json"
        target.write_text(json.dumps(item, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        paths.append(target)
    return paths
