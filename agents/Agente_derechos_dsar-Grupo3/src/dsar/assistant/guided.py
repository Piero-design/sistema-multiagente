"""Modo guiado: respuestas sin LLM construidas con el expediente, el motor y el RAG."""

from __future__ import annotations

from typing import Any

from dsar.assistant.case_intents import guided_text
from dsar.assistant.facts import case_facts
from dsar.assistant.query import RIGHT_LABELS, mentioned_rights  # noqa: F401  (RIGHT_LABELS se reexporta)
from dsar.core.render import render_response
from dsar.rag.lexical import normalize

# Preguntas rápidas de la interfaz (también forman parte del conjunto «del dominio» de las mediciones).
QUICK_QUESTIONS = (
    "¿Qué es una solicitud DSAR?",
    "¿Qué derechos puede atender este agente?",
    "¿Por qué hay que verificar la identidad?",
    "¿Por qué este caso requiere revisión humana?",
    "¿Cuál es el plazo de este expediente?",
    "¿Qué fuentes usaste para responder?",
    "¿Qué debo hacer ahora con este caso?",
    "Redacta un borrador de respuesta para este caso.",
)


def deadline_lines(deadlines: dict[str, Any]) -> list[str]:
    lines = []
    for right, item in deadlines.items():
        unit = "días hábiles" if item["day_type"] == "business" else "días naturales"
        basis = f" ({item['legal_basis']})" if item.get("legal_basis") else ""
        label, legal = RIGHT_LABELS.get(right, right), item.get("legal_deadline_at")
        if legal and legal != item["deadline_at"]:
            lines.append(f"- {label}: plazo interno {item['days']} {unit}, vence {item['deadline_at']}; "
                         f"plazo legal {item['legal_days']} {unit}, vence {legal}{basis}")
        else:
            lines.append(f"- {label}: {item['days']} {unit}, vence {item['deadline_at']}{basis}")
    return lines


def _computed(computed: dict[str, Any]) -> str:
    if computed.get("error"):
        return f"El motor no pudo calcular los plazos con el perfil {computed['policy_id']}: {computed['error']}"
    return "\n".join(
        [f"Plazos calculados por el motor para una solicitud recibida el **{computed['received_at']}** con el "
         f"perfil **{computed['policy_id']}** (se cuenta desde el día siguiente):"]
        + deadline_lines(computed["deadlines"])
        + [f"Plazo más cercano: **{computed['deadline_at']}**. {computed['disclaimer']}"])


def _right_deadlines(package: dict[str, Any], rights: list[str]) -> str:
    deadlines = {right: package["deadlines"][right] for right in rights}
    names = " y ".join(RIGHT_LABELS.get(right, right).lower() for right in rights)
    return (f"Plazo de {names} en este expediente (se cuenta desde el día siguiente a la recepción, {package['received_at']}):\n\n"
            + "\n".join(deadline_lines(deadlines)))


def _case_deadlines(package: dict[str, Any]) -> str:
    policy = package["policy"]
    lines = [f"La fecha límite más cercana del expediente es **{package['deadline_at']}**, calculada desde "
             f"{package['received_at']} con la política **{policy['policy_id']}** "
             f"({policy.get('label', policy['policy_id'])})."]
    lines += deadline_lines(package.get("deadlines", {}))
    lines.append("ISO/IEC 27701 no fija un plazo universal: exige definir uno (B.1.3.10). " + policy.get("disclaimer", ""))
    return "\n".join(lines)


def _case_summary(package: dict[str, Any]) -> str:
    facts = case_facts(package)
    reasons = package["hitl"]["reasons"] or ["El borrador queda pendiente de revisión ordinaria."]
    if facts["identity_status"] == "verified":
        step = "El siguiente paso es revisar el expediente y el borrador antes de la decisión humana."
    else:
        step = "El siguiente paso es completar la identidad por el canal autorizado antes de buscar datos."
    return (f"El caso está en **{facts['status']}** y tiene **{facts['record_count']} registros** preparados.\n\n"
            + "\n".join("- " + reason for reason in reasons)
            + f"\n\n{step} No se han enviado comunicaciones ni ejecutado cambios.")


def asks_for_sources(question: str) -> bool:
    """«¿Qué fuentes usaste?»: pregunta sobre la respuesta anterior, no sobre el tema."""
    text = normalize(question)
    return "fuente" in text and any(verb in text for verb in ("usaste", "usaron", "consultaste", "citaste",
                                                              "utilizaste", "basaste", "base de tu"))


def sources_reply(previous: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    """Las fuentes de la respuesta anterior; si esa respuesta salió del expediente y del motor, lo dice."""
    if not previous:
        return ("La respuesta anterior no usó fragmentos documentales: salió del expediente y de los cálculos del "
                "motor. Si no hay una respuesta previa, haz primero una pregunta."), []
    lines = [f"- [{item['chunk_id']}] {item['source']} · {item['section']}" for item in previous]
    return "La respuesta anterior se apoyó en estos fragmentos:\n\n" + "\n".join(lines), previous


def guided_reply(question: str, package: dict[str, Any] | None, context: dict[str, Any],
                 computed: dict[str, Any] | None = None, intent: str | None = None,
                 intent_facts: dict[str, Any] | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Respuesta y fuentes realmente usadas: lo que sale del expediente o del motor no lleva fuentes."""
    text = normalize(question)
    if "borrador" in text or "redacta" in text:
        return (render_response(package) if package else "Carga un caso antes de redactar su respuesta."), []
    if package and intent and intent_facts is not None:
        return guided_text(intent, intent_facts), []
    if computed:
        return _computed(computed), []
    if any(word in text for word in ("plazo", "fecha", "dias")) and package:
        rights = mentioned_rights(question, list(package.get("deadlines", {})))
        return (_right_deadlines(package, rights) if rights else _case_deadlines(package)), []
    if any(word in text for word in ("este caso", "expediente", "ahora")) and package:
        return _case_summary(package), []
    chunks = context["retrieved_chunks"]
    if not chunks:
        return ("No encontré un fundamento suficiente en las referencias locales. "
                "Reformula la pregunta o consulta al responsable."), []
    used = chunks[:2]
    return "Contexto recuperado para tu consulta:\n\n" + "\n\n".join(
        f"[{item['chunk_id']}] **{item['section']}**\n\n{item['excerpt']}" for item in used), used


def guided_answer(question: str, package: dict[str, Any] | None, context: dict[str, Any],
                  computed: dict[str, Any] | None = None) -> str:
    return guided_reply(question, package, context, computed)[0]
