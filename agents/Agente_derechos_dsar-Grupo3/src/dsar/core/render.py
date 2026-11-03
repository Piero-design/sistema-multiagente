"""Borrador de respuesta con la estructura fija de knowledge/assets/response-template.md."""

from __future__ import annotations

import json
from typing import Any

STRICTER_SOURCE = "política interna (más estricta que la ley)"
SUSPENSION_LABELS = {
    "additional_information": "Requerimiento de informacion adicional",
    "request_correction": "Observacion de solicitud incompleta",
}


def _unit(item: dict[str, Any]) -> str:
    return "dias habiles" if item["day_type"] == "business" else "dias naturales"


def _deadline_line(right: str, item: dict[str, Any]) -> str:
    basis = f" — {item['legal_basis']}" if item.get("legal_basis") else ""
    origin = f" [{item['source']}; legal {item['legal_days']}]" if item.get("source") == STRICTER_SOURCE else ""
    line = f"- {right}: {item['days']} {_unit(item)}, vence {item['deadline_at']}{basis}{origin}"
    if item.get("suspended_days"):
        line += f" [suspendido {item['suspended_days']} {_unit(item)}]"
    if item.get("extended"):
        extension = item["extension"]
        line += f" [prorrogado {extension['days']} {_unit(item)}; vencia {extension['original_deadline_at']}]"
    return line


def _header(package: dict[str, Any]) -> list[str]:
    rights = package.get("request_types") or [package["request_type"]]
    policy = package["policy"]
    lines = [
        "# Borrador de respuesta DSAR",
        "",
        f"**Caso:** {package['case_id']}  ",
        f"**Derecho(s) solicitado(s):** {', '.join(rights)}  ",
        f"**Estado:** {package['status']}  ",
        f"**Politica aplicada:** {policy['policy_id']} ({policy.get('jurisdiction', 'LAB')})  ",
        f"**Fecha limite mas cercana:** {package['deadline_at']}  ",
    ]
    organization = package.get("organization")
    if organization:
        state = "aplicada" if organization["applied"] else "no aplicada"
        lines.append(
            f"**Organizacion:** {organization['name']} — politica v{organization['version']} ({state})  "
        )
    lines.extend([f"**Aprobador designado:** {package['hitl'].get('approver', 'DPO')}", ""])
    return lines


def _deadlines(package: dict[str, Any]) -> list[str]:
    deadlines = package.get("deadlines") or {}
    if len(deadlines) <= 1 and not any(
        item.get("legal_basis") or item.get("source") or item.get("extended") or item.get("suspended_days")
        for item in deadlines.values()
    ):
        return []
    return ["## Plazos por derecho", "", *(_deadline_line(r, i) for r, i in deadlines.items()), ""]


def _suspension(package: dict[str, Any]) -> list[str]:
    suspension = package.get("suspension")
    if not suspension:
        return []
    lines = [
        "## Tramite suspendido",
        "",
        f"- {SUSPENSION_LABELS.get(suspension['type'], suspension['type'])} desde {suspension['suspended_from']}"
        f"; el titular puede responder hasta {suspension['due_at']}.",
    ]
    if suspension.get("basis"):
        lines.append(f"- Base: {suspension['basis']}.")
    if suspension.get("cancellation_proposed"):
        lines.append("- Se propone tener la solicitud por no presentada (CANCELLED); decide una persona.")
    return [*lines, ""]


def _records(package: dict[str, Any]) -> list[str]:
    lines = ["## Resultado preliminar", ""]
    if package["identity_verification"].get("status") != "verified":
        lines.append("La busqueda de datos no se inicio porque la verificacion de identidad esta pendiente.")
        return lines
    records, systems = len(package["discovered_records"]), len(package["source_systems"])
    lines.append(
        ("Se preparo 1 registro sintetico procedente" if records == 1
         else f"Se prepararon {records} registros sinteticos procedentes")
        + f" de {systems} {'sistema' if systems == 1 else 'sistemas'}."
    )
    lines.extend(["", "## Informacion preparada", ""])
    if not package["discovered_records"]:
        lines.append("No se localizaron registros para el identificador proporcionado.")
    for record in package["discovered_records"]:
        lines.append(f"- `{record['source_system']}/{record['record_id']}` ({record['category']})")
        for field, value in record["data"].items():
            shown = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            lines.append(f"  - {field}: `{shown}`")
        confidential = set(record.get("confidential_fields", []))
        third = [field for field in record["redacted_fields"] if field not in confidential]
        if third:
            lines.append("  - Campos de terceros retirados del borrador: " + ", ".join(third))
        if confidential:
            lines.append("  - Campos confidenciales por política interna retirados: " + ", ".join(sorted(confidential)))
    return lines


def _pending(package: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    decision = package.get("human_decision")
    if decision:
        lines.extend(["", "## Decision humana", "",
                      f"- {decision['decision']} por {decision['reviewer']} ({decision['at']}): {decision['note']}",
                      "- La decision autoriza preparar la respuesta; el agente no ejecuta cambios ni envios."])
    lines.extend(["", "## Acciones o revisiones pendientes", ""])
    for action in package.get("proposed_actions") or [package["proposed_action"]]:
        lines.append(f"- Propuesta ({action['type']}, no ejecutada): {action['description']}")
    for reason in package["hitl"]["reasons"]:
        lines.append(f"- Revision humana: {reason}")
    return lines


def _rag_sources(package: dict[str, Any]) -> list[str]:
    retrieved = package.get("rag", {}).get("retrieved_chunks", [])
    if not retrieved:
        return []
    return ["", "## Fundamento recuperado por el RAG", "", *(
        f"- [{item['chunk_id']}] `{item['source']}` — {item['section']} "
        f"(relevancia {item.get('relevance') or item['score']})."
        for item in retrieved
    )]


LETTER_RIGHTS = {
    "access": "acceso", "rectification": "rectificación", "erasure": "supresión o cancelación",
    "portability": "portabilidad", "objection": "oposición", "information": "información",
}
MUTATING_RIGHTS = ("rectification", "erasure", "objection")


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} y {items[-1]}"


def _letter_deadlines(package: dict[str, Any], rights: list[str]) -> str:
    deadlines = package.get("deadlines") or {}
    dates = {right: deadlines[right]["deadline_at"] for right in rights if right in deadlines}
    if len(set(dates.values())) <= 1:
        return f"Le daremos respuesta a más tardar el {package['deadline_at']}, según el plazo aplicable."
    detail = "; ".join(f"{LETTER_RIGHTS.get(right, right)}, a más tardar el {date}" for right, date in dates.items())
    return f"Cada derecho tiene su propio plazo de respuesta: {detail}."


def _letter_findings(package: dict[str, Any]) -> str:
    if package["identity_verification"].get("status") != "verified":
        return ("Antes de consultar sus datos necesitamos confirmar su identidad por el canal autorizado. "
                "Mientras no se complete esa verificación no buscaremos información en nuestros sistemas.")
    count = len(package["discovered_records"])
    if count == 0:
        return ("En los sistemas consultados no localizamos datos asociados a su identificador. "
                "Una persona responsable revisará este resultado antes de responderle.")
    found = "un registro asociado" if count == 1 else f"{count} registros asociados"
    return (f"Localizamos {found} a su identificador. Una persona responsable revisará la información "
            "antes de responderle y retirará cualquier dato de terceros.")


def _letter_status(package: dict[str, Any], rights: list[str]) -> list[str]:
    decision = package.get("human_decision")
    if decision:
        verdict = "aprobó" if decision["decision"] == "APPROVED" else "no aprobó"
        return [f"La persona responsable {verdict} la propuesta de respuesta; le comunicaremos el detalle "
                "en la respuesta definitiva."]
    approver = package["hitl"].get("approver")
    lines = [f"Su solicitud está pendiente de revisión por la persona designada: {approver}." if approver
             else "Su solicitud está pendiente de revisión por la persona responsable."]
    mutating = [LETTER_RIGHTS[right] for right in rights if right in MUTATING_RIGHTS]
    if mutating:
        lines.append(f"Las modificaciones que solicita ({_join(mutating)}) son una propuesta: no se aplicarán "
                     "sin la aprobación de esa persona.")
    return lines


def guided_letter(package: dict[str, Any]) -> str:
    """Carta al titular redactada por el motor, sin LLM: solo hechos del expediente y nunca acciones ejecutadas."""
    rights = package.get("request_types") or [package["request_type"]]
    names = _join([LETTER_RIGHTS.get(right, right) for right in rights])
    organization = (package.get("organization") or {}).get("name") or "El responsable del tratamiento"
    paragraphs = [
        "Estimado/a titular:",
        f"Hemos recibido su solicitud de {names}, registrada el {package['received_at']} "
        f"con la referencia {package['case_id']}.",
        _letter_findings(package),
        _letter_deadlines(package, rights),
        " ".join(_letter_status(package, rights)),
        f"Atentamente,  \n{organization}",
    ]
    return "\n\n".join(paragraphs)


def render_response(package: dict[str, Any], letter: str | None = None) -> str:
    lines = [*_header(package), *_deadlines(package), *_suspension(package)]
    if letter and letter.strip():
        # Prosa redactada por el modelo; la estructura y los hechos los fija el motor.
        lines.extend(["## Carta al titular (borrador, no enviada)", "", letter.strip(), ""])
    lines.extend([*_records(package), *_pending(package), *_rag_sources(package)])
    lines.extend(["", "---", "", package["disclaimer"]])
    return "\n".join(lines) + "\n"
