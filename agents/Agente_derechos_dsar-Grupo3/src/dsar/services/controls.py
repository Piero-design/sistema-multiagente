"""Controles y cláusulas ISO/IEC 27701:2025 que cubre un expediente (knowledge/references/iso-control-map.md).

Es una descripción del expediente para la persona revisora: no decide nada ni cambia el caso.
"""

from __future__ import annotations

from typing import Any

from dsar.services import cases
from dsar.services.context import ServiceContext

MUTATING = frozenset({"rectification", "erasure", "objection"})


def _control(control: str, title: str, reason: str) -> dict[str, str]:
    return {"control": control, "title": title, "reason": reason}


def applied_controls(package: dict[str, Any]) -> list[dict[str, str]]:
    rights = set(package.get("request_types") or [package["request_type"]])
    records = package["discovered_records"]
    result = [_control("A.1.3.7", "Acceso, corrección o supresión",
                       "Flujo con estados; toda modificación queda como propuesta para aprobación humana.")]
    if rights & {"access", "portability"}:
        result.append(_control("A.1.3.9", "Copia de la PII tratada",
                               "Búsqueda por titular y retiro de datos de terceros antes de entregar la copia."))
    result.append(_control("A.1.3.10", "Gestión de solicitudes",
                           f"Plazo por derecho desde el perfil {package['policy']['policy_id']}; expediente validado."))
    if "information" in rights:
        result.append(_control("A.1.3.3 / A.1.3.4", "Información al titular",
                               "Derecho de información y lenguaje claro en el borrador."))
    if "objection" in rights:
        result.append(_control("A.1.3.6", "Oposición al tratamiento", "Oposición tramitada con aprobación humana."))
    if rights & MUTATING:
        result.append(_control("A.1.3.8", "Informar a terceros",
                               "Al aprobar, handoff al Agente de Terceros para notificar a los destinatarios."))
    if (package.get("coverage") or {}).get("missing_systems"):
        result.append(_control("A.1.2.9", "Registros del tratamiento",
                               "Sistemas declarados sin registros del titular: handoff al Agente de Inventario."))
    if "rectification" in rights:
        result.append(_control("A.1.4.4", "Exactitud y calidad",
                               "La corrección queda como propuesta con el valor nuevo para aprobación humana."))
    if any(record["restrictions"] for record in records):
        result.append(_control("A.1.4.8 / A.1.4.9", "Conservación y eliminación",
                               "Restricciones de conservación: aprobación humana antes de proponer supresión."))
    result += [
        _control("A.3.9", "Derechos de acceso", "El modelo solo recibe hechos minimizados; el MCP no decide."),
        _control("A.3.14", "Protección de registros", "Hashes SHA-256 de las entradas y validación del expediente."),
        _control("A.3.25", "Registro de eventos", f"Rastro de auditoría con {len(package['audit_trail'])} eventos."),
        _control("A.3.31", "Información de prueba", "Solo datos sintéticos (example.test)."),
    ]
    return result + applied_clauses(package)


def applied_clauses(package: dict[str, Any]) -> list[dict[str, str]]:
    """Cláusulas del sistema de gestión que el expediente evidencia (docs/iso-27701-trazabilidad.md)."""
    result = []
    if package["status"] == "IDENTITY_PENDING":
        result.append(_control("Cláusula 8.3", "Tratamiento de riesgos",
                               "Identidad sin verificar: la búsqueda se bloquea hasta que una persona la verifique."))
    result += [
        _control("Cláusula 8.1", "Planificación y control operacional",
                 f"El motor determinista fija el estado {package['status']}; el modelo no decide."),
        _control("Cláusula 5.3", "Roles y autoridades",
                 f"Aprobación humana requerida ({len(package['hitl']['reasons'])} motivos); solo una persona decide."
                 if package["hitl"]["required"] else "Solo una persona aprueba o rechaza el expediente."),
        _control("Cláusula 7.4", "Comunicación",
                 "El borrador sigue una plantilla; el envío lo decide una persona desde la bandeja de salida."),
        _control("Cláusula 9.1", "Seguimiento y medición",
                 f"Vencimiento por derecho registrado para su seguimiento ({len(package['deadlines'])} plazos)."),
        _control("Cláusula 9.2", "Auditoría interna",
                 "El rastro de auditoría y los hashes permiten auditar cada paso del expediente."),
    ]
    return result


def for_case(ctx: ServiceContext, case_id: str) -> list[dict[str, str]]:
    return applied_controls(cases.get(ctx, case_id))
