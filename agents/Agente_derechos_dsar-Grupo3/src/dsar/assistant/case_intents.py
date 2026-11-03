"""Preguntas puntuales sobre un expediente: quién aprueba, controles, prórroga, campos retirados y cobertura.

Cada una se responde con datos que ya calculó el motor (nada lo decide el modelo). El modo guiado los convierte en una
respuesta corta; con un modelo, los mismos datos viajan como `datos_calculados_por_motor` para que conteste la pregunta
concreta sin tener que resumir todo el expediente. También rechaza, antes de cualquier modelo, los pedidos de datos
personales del titular.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from dsar.assistant.query import RIGHT_LABELS, named_rights
from dsar.core.procedures import extension_preview
from dsar.core.states import DECIDABLE_STATES
from dsar.rag.lexical import normalize

DECIDE = re.compile(r"\b(como|donde)\b.*\b(apruebo|aprobar|aprueba|rechazo|rechazar|decido|decidir|registro la decision|"
                    r"se aprueba|se rechaza|dar el visto bueno)\b")
# (intención, expresión con límites de palabra). El orden fija la prioridad.
INTENT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("extension", re.compile(r"\b(prorroga|prorrogar|ampliar (el )?plazo|ampliacion del plazo|extender el plazo|mas tiempo)\b")),
    ("approver", re.compile(r"\b(quien aprueba|quien decide|quien autoriza|quien resuelve|aprobador|quien debe aprobar|"
                            r"quien lo aprueba|quien lo decide)\b")),
    ("coverage", re.compile(r"\b(hris|crm|benefits|cobertura|sin registros|sistemas? (del|de este) (caso|expediente)|"
                            r"sistemas? (se )?consult\w*|sistemas? declarad\w*)\b")),
    ("redacted", re.compile(r"\b(se retiraron|retirados?|campos?\b.{0,12}\b(retirad\w*|confidenciales?)|confidenciales?|"
                            r"(datos|campos?) de terceros|terceros)\b")),
)
# Preguntas sobre lo que dice la norma: aunque nombren «terceros» o «prórroga», las responde el RAG, no los datos del caso.
NORMATIVE = re.compile(r"\b(ley|articulo|art|norma|normativa|reglamento|iso|27701|que dice|que exige|que establece|"
                       r"segun la)\b")
CONTROL_CONTEXT = re.compile(r"\b(iso|27701|aplican|aplica|cubre|cubren)\b")
# Pedidos de VALORES de datos personales del titular: el chat no los muestra (ni el modelo los recibe). Se exige un pedido
# directo y que el dato sea «del titular»/«de la persona»/«de los registros»: «¿qué pasa con los datos personales tras la
# supresión?» o «¿cuáles son los valores de los plazos?» no lo son.
REQUEST = r"(dame|dime|muestrame|muestra|ensename|pasame|enviame|copiame|listame|cual es|cuales son|quiero (ver|saber))"
OWNER = r"(del titular|de la persona|del solicitante|de este caso|del caso|del expediente|de la solicitud)"
PERSONAL_DATA = re.compile(
    r"\b" + REQUEST + r"\b.{0,40}\b(correo|email|mail|telefono|celular|direccion|dni|documento de identidad|apellidos?|nombre|"
    r"datos personales|datos|informacion personal)\b.{0,25}\b" + OWNER + r"\b"
    r"|\b" + REQUEST + r"\b.{0,25}\b(datos de (la tabla|los registros|el registro)|tabla de registros|"
    r"contenido de los registros|valores de los registros)\b")
PERSONAL_DATA_MESSAGE = (
    "No muestro datos personales del titular en el chat (correos, nombres, teléfonos ni los valores de los registros): "
    "los ve, con autorización, quien revisa el expediente en «Registros localizados».{counts} "
    "Sí puedo decirte cuántos registros hay, de qué sistemas y qué campos se retiraron.")
# «¿Qué datos tiene el titular?»: el sustantivo ya va en la propia pregunta.
WHAT_DATA = re.compile(r"\bque (datos|informacion)( personales)? (tiene|hay|constan)\b.{0,20}\b(titular|persona|registros?)\b")


def asks_for_personal_data(question: str) -> bool:
    text = normalize(question)
    return bool(PERSONAL_DATA.search(text) or WHAT_DATA.search(text))


def personal_data_reply(package: dict[str, Any] | None) -> str:
    counts = ""
    if package:
        records = package.get("discovered_records", [])
        counts = f" En este caso hay {len(records)} registro(s)."
    return PERSONAL_DATA_MESSAGE.format(counts=counts)


def detect_intent(question: str) -> str | None:
    text = normalize(question)
    if DECIDE.search(text):
        return "decide"  # «¿cómo apruebo?»: procedimiento, no un pedido de que el asistente apruebe
    if re.search(r"\bcontroles?\b", text) and CONTROL_CONTEXT.search(text):
        return "controls"
    if NORMATIVE.search(text) or re.search(r"\bagentes?\b", text):
        return None  # la norma o «el Agente de Terceros» no son datos de este caso
    for intent, pattern in INTENT_PATTERNS:
        if pattern.search(text):
            return intent
    return None


def case_vocabulary(package: dict[str, Any] | None) -> set[str]:
    """Nombres propios del expediente (sistemas y campos retirados): una pregunta que los usa es del dominio."""
    if not package:
        return set()
    coverage = package.get("coverage") or {}
    names = [*package.get("source_systems", []), *coverage.get("expected_systems", []),
             *coverage.get("found_systems", []), *coverage.get("missing_systems", [])]
    names += [field for record in package.get("discovered_records", []) for field in record.get("redacted_fields", [])]
    return {normalize(name) for name in names if name}


def _redacted(package: dict[str, Any]) -> dict[str, list[str]]:
    records = package.get("discovered_records", [])
    redacted = {field for record in records for field in record.get("redacted_fields", [])}
    confidential = {field for record in records for field in record.get("confidential_fields", [])}
    return {"campos_de_terceros": sorted(redacted - confidential), "campos_confidenciales_por_politica": sorted(confidential)}


def _extension(package: dict[str, Any], profiles: dict[str, Any], today: date, rights: list[str]) -> dict[str, Any]:
    result = {}
    for right in rights:
        preview = extension_preview(package, profiles, right, today)
        name = RIGHT_LABELS.get(right, right)
        if not preview["allowed"]:
            result[right] = {"derecho": name, "se_puede_prorrogar": False, "motivo": preview["reason"]}
            continue
        longest = extension_preview(package, profiles, right, today, days=preview["max_days"])
        result[right] = {
            "derecho": name, "se_puede_prorrogar": True, "tipo_de_dia": preview["day_type"], "dias_maximos": preview["max_days"],
            "vence_hoy": preview["current_deadline_at"], "vence_con_la_prorroga_maxima": longest["new_deadline_at"],
            "tope_legal": preview["legal_ceiling_at"], "comunicar_al_titular_antes_del": preview["communicate_before"],
            "norma": "D.S. 016-2024-JUS, art. 71: una sola vez y por un plazo igual al legal como máximo",
        }
    return result


def intent_data(intent: str, package: dict[str, Any], profiles: dict[str, Any], today: date | None,
                controls: list[dict[str, str]] | None, question: str = "") -> dict[str, Any]:
    """Datos del motor que responden la pregunta (también los recibe el modelo)."""
    if intent == "decide":
        status = package["status"]
        reason = None
        if status == "IDENTITY_PENDING":
            reason = "la identidad no está verificada: hay que completarla por el canal autorizado antes de decidir"
        elif status not in DECIDABLE_STATES:
            decision = package.get("human_decision") or {}
            reason = (f"ya tiene una decisión registrada ({decision.get('decision')})" if decision
                      else f"el expediente está en {status}, un estado que no admite decisión")
        return {"aprobador_designado": package["hitl"].get("approver"), "estado": status,
                "se_puede_decidir_ahora": reason is None, "motivo_si_no_se_puede": reason,
                "opciones_del_panel": ["Aprobar", "Rechazar"],
                "pasos": ["Abrir «Revisión y decisión» desde el expediente", "En «Decisión humana», escribir quién decide",
                          "Elegir Aprobar o Rechazar", "Escribir la justificación",
                          "Marcar la confirmación de que revisó el expediente, los motivos y el borrador",
                          "Pulsar «Registrar decisión»"]}
    if intent == "approver":
        organization = package.get("organization") or {}
        return {"aprobador": package["hitl"].get("approver"),
                "politica_de_la_organizacion_aplicada": bool(organization.get("applied")),
                "version_de_la_politica": organization.get("version")}
    if intent == "controls":
        return {"controles_iso_27701_del_expediente": controls or []}
    if intent == "extension":
        rights = package.get("request_types") or [package["request_type"]]
        asked = named_rights(question, list(package.get("deadlines", {})))  # si nombra un derecho, solo ese (menos ruido)
        return {"derechos_del_expediente": [RIGHT_LABELS.get(right, right) for right in rights],
                "prorroga_por_derecho": _extension(package, profiles, today or date.today(), asked)}
    if intent == "redacted":
        return _redacted(package)
    coverage = package.get("coverage") or {}
    return {"sistemas_esperados": coverage.get("expected_systems", []),
            "sistemas_con_registros": coverage.get("found_systems", []),
            "sistemas_sin_registros": coverage.get("missing_systems", [])}


def _unit(kind: str) -> str:
    return "días hábiles" if kind == "business" else "días naturales"


def guided_text(intent: str, data: dict[str, Any], rights: dict[str, str] | None = None) -> str:
    """Respuesta corta del modo guiado."""
    if intent == "decide":
        if not data["se_puede_decidir_ahora"]:
            return f"Todavía no se puede decidir este expediente: {data['motivo_si_no_se_puede']}."
        steps = "\n".join(f"{number}. {step}." for number, step in enumerate(data["pasos"], 1))
        return (f"Para decidir este expediente (aprobar o rechazar):\n\n{steps}\n\n"
                f"La persona designada es **{data['aprobador_designado']}**. El asistente no puede registrar la decisión por ti, "
                "aunque seas el DPO: solo se registra desde ese panel. Al aprobar se generan los handoffs a otros agentes; "
                "ninguna acción se ejecuta.")
    if intent == "approver":
        base = f"Lo decide **{data['aprobador']}**."
        if data["politica_de_la_organizacion_aplicada"]:
            base += f" Es el aprobador que fija la política de la organización (v{data['version_de_la_politica']})."
        else:
            base += " Es el aprobador por defecto: la política de la organización no se aplicó a este perfil."
        return base + " La decisión solo se registra en «Revisión y decisión»; el asistente no aprueba ni rechaza."
    if intent == "controls":
        lines = [f"- **{item['control']}** {item['title']}: {item['reason']}" for item in data["controles_iso_27701_del_expediente"]]
        return "Este expediente aplica estos controles de ISO/IEC 27701:2025:\n\n" + "\n".join(lines)
    if intent == "extension":
        lines = []
        for right, item in data["prorroga_por_derecho"].items():
            name = item["derecho"]
            if not item["se_puede_prorrogar"]:
                lines.append(f"- {name}: no se puede prorrogar. {item['motivo']}")
                continue
            lines.append(
                f"- {name}: hasta **{item['dias_maximos']} {_unit(item['tipo_de_dia'])}** más (una sola vez, por un plazo igual al "
                f"legal). Vence **{item['vence_hoy']}** y, con la prórroga máxima, pasaría al **{item['vence_con_la_prorroga_maxima']}**; "
                f"el tope legal es {item['tope_legal']}. Debe comunicarse al titular antes del {item['comunicar_al_titular_antes_del']}.")
        return ("Se puede prorrogar **una sola vez** y por un plazo igual al legal como máximo (D.S. 016-2024-JUS, art. 71):\n\n"
                + "\n".join(lines) + "\n\nEs una decisión humana: se registra en «Revisión y decisión» > «Solicitar prórroga».")
    if intent == "redacted":
        third, confidential = data["campos_de_terceros"], data["campos_confidenciales_por_politica"]
        if not third and not confidential:
            return "No se retiró ningún campo de los registros de este expediente."
        parts = []
        if third:
            parts.append("campos de terceros (" + ", ".join(f"`{field}`" for field in third) + ")")
        if confidential:
            parts.append("campos confidenciales por la política de la organización ("
                         + ", ".join(f"`{field}`" for field in confidential) + ")")
        return ("Se retiraron de los registros " + " y ".join(parts) + ". Se quitan antes de cualquier borrador y el modelo "
                "solo conoce sus nombres, nunca sus valores.")
    expected, found, missing = data["sistemas_esperados"], data["sistemas_con_registros"], data["sistemas_sin_registros"]
    lines = []
    if expected:
        lines.append("La política declara estos sistemas: " + ", ".join(f"`{name}`" for name in expected) + ".")
    lines.append("Con registros del titular: " + (", ".join(f"`{name}`" for name in found) or "ninguno") + ".")
    if missing:
        lines.append("Sin registros: " + ", ".join(f"`{name}`" for name in missing)
                     + ". Hay que confirmar la cobertura con el Agente de Inventario (control A.1.2.9); el handoff se genera al aprobar.")
    return "\n\n".join(lines)
