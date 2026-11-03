"""Control de alcance: decide, antes de cualquier modelo, si una pregunta es del dominio DSAR.

La pregunta solo se compara con reglas y ejemplos y se convierte en un vector; nunca se interpreta
como instrucción. Portado de v4 (app/service.py::scope_details) sin cambiar reglas ni umbrales.
"""

from __future__ import annotations

import re
from typing import Any

from dsar.assistant import guard
from dsar.rag.dense import DenseUnavailable
from dsar.rag.guide import asks_safe_how_to
from dsar.rag.lexical import normalize
from dsar.rag.retrieve import dense_relevance

GREETINGS = frozenset({"hola", "buenos dias", "buenas", "ayuda"})
BYPASS_TERMS = ("ignora", "omite", "omitir", "sin verificar", "sin aprobacion", "elimina todos", "borra todos")
# Palabras que identifican el dominio por sí solas.
DOMAIN_TERMS = ("dsar", "derecho", "dato", "privacidad", "titular", "identidad", "verific", "iso", "27701",
                "pims", "solicitud", "acceso", "supres", "rectific", "portab", "oposic", "caso", "expediente",
                "plazo", "tercero", "revision", "aprob", "fuente", "rag", "skill", "borrador", "retencion",
                "conservacion", "sensible", "humana", "prorroga")
# Palabras del dominio que también se usan fuera de él («qué derechos violó…», «datos del clima», «el caso Odebrecht»).
# Si son lo único que hay, la palabra clave no basta: hace falta similitud semántica con el corpus (antes pasaban solas).
# Se mantiene el umbral de v4 (0,46): con 0,52 se rechazaban 8 preguntas legítimas de la medición existente (90 -> 82 de 93).
# Lo que queda entre 0,46 y 0,52 (preguntas ajenas cercanas al vocabulario del dominio) lo resuelve el modelo con el skill.
WEAK_TERMS = ("derecho", "dato", "caso", "identidad", "revision", "humana", "privacidad", "fuente")
# Palabras genéricas («explica...») que solo cuentan con un expediente cargado.
GENERIC_TERMS = ("correo", "informacion", "ahora", "explica", "resume")
# Medida en v4 con 93 preguntas del dominio (98 % por encima de 0,46) y 24 ajenas (máximo 0,455).
SCOPE_MIN_SIMILARITY = 0.46
# Temas que SKILL.md declara ajenos a este agente y el agente del PIMS que los atiende.
REDIRECTS = (
    ("Agente de Incidentes y Brechas", re.compile(
        r"\b(fuga|brecha|incidente de seguridad|filtracion|hackeo|hackearon|ransomware|"
        r"robo de (datos|informacion)|acceso indebido|datos expuestos|vulneracion|usb|exfiltr\w*|malware|phishing|"
        r"ciberataque|ataque informatico|(perdida|extravio|robo) de(l)? (un |el )?(laptop|portatil|dispositivo|equipo|celular))\b")),
    ("Agente de Evaluación de Riesgos", re.compile(
        r"\b(dpia|evaluacion de impacto|analisis de riesgos?|matriz de riesgos?)\b")),
    ("Agente de Terceros (DPAs)", re.compile(
        r"\b(encargados? de(l)? tratamiento|contrato con (un |el )?(encargado|proveedor)|dpa|"
        r"acuerdo de encargo|subencargado)\b")),
    ("Agente de Inventario de Datos", re.compile(
        r"\b(inventario de (datos|tratamientos)|registro de actividades de tratamiento|mapa de datos)\b")),
    ("Agente de Formación y Conciencia", re.compile(
        r"\b(capacitacion|concienciacion|curso de privacidad|formacion del personal)\b")),
)

REDIRECT_MESSAGE = (
    "Eso corresponde al {agent}; no lo gestiono yo. Yo atiendo solicitudes de derechos de titulares "
    "(información, acceso, rectificación, supresión, portabilidad y oposición). Si tu consulta nace de "
    "una solicitud de un titular, cuéntame el caso y te ayudo con esa parte."
)
OUT_OF_SCOPE_MESSAGE = (
    "Eso está fuera de mi alcance. Solo atiendo solicitudes de derechos sobre datos personales "
    "(información, acceso, rectificación, supresión, portabilidad y oposición): el expediente, sus plazos, "
    "la normativa aplicable y el borrador de respuesta. Para incidentes de seguridad o brechas, "
    "consulta al agente de Incidentes."
)
GREETING_MESSAGE = ("Hola. Soy el asistente de Derechos DSAR. Puedes preguntarme sobre acceso, rectificación, "
                    "supresión, portabilidad, oposición o el expediente cargado.")


def _result(scope: str, basis: str, category: str | None = None, redirect: str | None = None) -> dict[str, Any]:
    return {"scope": scope, "basis": basis, "category": category, "redirect": redirect}


def _weak_keyword_check(question: str, semantic: bool) -> dict[str, Any] | None:
    """Con solo palabras débiles, decide por similitud; sin modelo semántico se conserva la palabra clave (None)."""
    try:
        if not semantic:
            raise DenseUnavailable("control semántico desactivado")
        similarity = dense_relevance(question)
    except DenseUnavailable:
        return None
    if similarity >= SCOPE_MIN_SIMILARITY:
        return _result("dsar", f"palabra clave y similitud semántica {similarity:.3f}")
    return _result("out_of_scope", f"solo palabras débiles y similitud semántica {similarity:.3f} bajo {SCOPE_MIN_SIMILARITY}")


def scope_details(question: str, has_case: bool = False, semantic: bool = True,
                  case_terms: frozenset[str] | set[str] | None = None) -> dict[str, Any]:
    """`scope` (blocked, greeting, dsar, out_of_scope), `basis` y, si aplica, `category` o `redirect`."""
    text = normalize(question)
    if text.strip(" ¿?¡!.,") in GREETINGS:
        return _result("greeting", "saludo")
    category = guard.detect_evasion(question, semantic)
    if category and semantic and asks_safe_how_to(question) and not guard.detect_evasion(question, False):
        category = None  # «¿cómo exporto el expediente?» se parece por similitud a «entrégame los datos», pero es de procedimiento
    if category:
        return _result("blocked", f"evasión ({category}): intenta {guard.CATEGORIES[category][0]}", category)
    if any(word in text for word in BYPASS_TERMS):
        return _result("blocked", "palabra de evasión")
    for agent, pattern in REDIRECTS:
        if pattern.search(text):
            return _result("out_of_scope", f"tema de otro agente: {agent}", redirect=agent)
    matched = [term for term in DOMAIN_TERMS if term in text]
    if matched:
        if all(term in WEAK_TERMS for term in matched) and not (case_terms and any(t in text for t in case_terms)):
            weak = _weak_keyword_check(question, semantic)
            if weak is not None:
                return weak
        return _result("dsar", "palabra clave")
    # Con un expediente cargado, sus sistemas y campos retirados («¿qué hago con hris-demo?») son del dominio.
    if case_terms and any(term in text for term in case_terms):
        return _result("dsar", "dato del expediente cargado")
    generic = any(term in text for term in GENERIC_TERMS)
    if generic and has_case:
        return _result("dsar", "palabra clave sobre el expediente cargado")
    try:
        if not semantic:
            raise DenseUnavailable("control semántico desactivado")
        similarity = dense_relevance(question)
    except DenseUnavailable:
        # Sin modelo semántico se conserva el comportamiento por palabras clave.
        if generic:
            return _result("dsar", "palabra clave (sin modelo semántico)")
        return _result("out_of_scope", "sin coincidencia de palabras clave (sin modelo semántico)")
    if similarity >= SCOPE_MIN_SIMILARITY:
        return _result("dsar", f"similitud semántica {similarity:.3f}")
    return _result("out_of_scope", f"similitud semántica {similarity:.3f} bajo el umbral {SCOPE_MIN_SIMILARITY}")


def reply_for(details: dict[str, Any]) -> str:
    """Respuesta fija para lo que no llega al modelo."""
    if details["scope"] == "greeting":
        return GREETING_MESSAGE
    if details["scope"] == "blocked":
        return guard.CATEGORIES[details["category"]][1] if details["category"] else guard.DEFAULT_MESSAGE
    if details.get("redirect"):
        return REDIRECT_MESSAGE.format(agent=details["redirect"])
    return OUT_OF_SCOPE_MESSAGE
