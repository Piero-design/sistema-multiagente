"""Enrutador determinista de tareas T1–T5 por señales ponderadas (portado de v4 sin cambios)."""

from __future__ import annotations

import re

from dsar.assistant.deadline_query import DATE_PATTERN
from dsar.rag.lexical import normalize

TASKS = ("T1", "T2", "T3", "T4", "T5")
DEFAULT_TASK = "T2"
PRIORITY = ("T3", "T4", "T2", "T5", "T1")
SIGNALS: dict[str, tuple[tuple[str, int], ...]] = {
    "T1": (
        (r"\btramit", 2), (r"\bprocesa", 2), (r"\bnueva solicitud\b", 2),
        (r"\bregistr\w* (una|la|esta) (nueva )?solicitud\b", 2), (r"\babr\w* (un|el) expediente\b", 2),
        (r"\ben que orden\b", 2), (r"\bcomo (la|lo) (atiendo|gestiono|tramito)\b", 2), (r"\bque pasos\b", 2),
        (r"\b(la|lo) atiendo\b", 1), (r"\b(gestiono|atenderlo|atenderla)\b", 1),
        (r"\b(llego|llegaron) (un|una)\b", 1), (r"\brecib\w* (un|una) (solicitud|correo|pedido)\b", 1),
        (r"\b(titular|cliente|usuario|persona)\b.{0,12}\b(pide|solicita|quiere)\b", 1),
        (r"\bperson-\d+\b", 1), (r"^\W*(\w+\s+){0,6}?(borra|elimina|suprime|corrige|rectifica)\b", 1),
    ),
    "T2": (
        (r"\biso\b|\b27701\b", 2), (r"\b(articulo|art\.)", 2), (r"\b[ab]\.\d+(\.\d+)+", 2),
        (r"\bque (dice|exige|establece|regula|significa)\b", 1),
        (r"\b(dice|exige|establece|regula|fija|define|significa|obliga|obligatorio)\b", 1),
        (r"\b(norma|normativa)\b", 1), (r"\b(ley|29733)\b", 1), (r"\breglamento\b", 1), (r"\bcontrol\b", 1),
        (r"\bformato\b", 1), (r"\b(gratis|gratuit\w*)\b", 1),
    ),
    "T3": (
        (r"\bredact", 3), (r"\bborrador\b", 3), (r"\bcarta\b", 3), (r"\bescrib", 2),
        (r"\b(correo|mensaje|comunicacion|respuesta) (al|para el) titular\b", 2),
        (r"\b(genera|prepara)\w* (el|la|un|una) (texto|respuesta|carta|comunicacion)\b", 2), (r"\btexto que\b", 1),
    ),
    "T4": (
        (r"\bplazos?\b", 2), (r"\bvence\w*\b", 2), (r"\bvencimiento\b", 2), (r"\bfecha limite\b", 2),
        (r"\bdias habiles\b", 2), (r"\bcuant[oa]s? (dias|tiempo)\b", 2), (r"\bmas tiempo\b", 2),
        (r"\bprorrog\w*\b", 2), (r"\bempieza a contar\b", 2), (r"\bdias\b", 1), (r"\bampliar\b", 1),
        (r"\bferiados?\b", 1), (DATE_PATTERN.pattern, 1),
    ),
    "T5": (
        (r"\bque sigue\b", 2), (r"\bcaso cargado\b", 2), (r"\bresum", 2), (r"\b(que falta|falta para)\b", 2),
        (r"\b(identity_pending|approval_required|review|approved|rejected)\b", 2),
        (r"\ba quien(es)?\b.{0,25}\b(avisar|notificar|informar|comunicar)\b", 2),
        (r"\bquien (tiene que aprobar|aprueba|decide)\b", 2), (r"\bpor que\b", 1), (r"\bestado\b", 1),
        (r"\bexplica", 1), (r"\b(este|el|del) (caso|expediente)\b", 1), (r"\bmotivos?\b", 1),
        (r"\bagentes?\b", 1), (r"\bavisar\b", 1), (r"\bregistros encontrados\b", 1), (r"\bsituacion\b", 1),
        (r"\bque (debo|tengo que) hacer\b", 1),
    ),
}
_COMPILED = {task: [(re.compile(pattern), weight) for pattern, weight in signals]
             for task, signals in SIGNALS.items()}


def task_scores(question: str) -> dict[str, int]:
    text = normalize(question)
    return {task: sum(weight for pattern, weight in signals if pattern.search(text))
            for task, signals in _COMPILED.items()}


def classify_task(question: str) -> str:
    scores = task_scores(question)
    best = max(scores.values())
    if best == 0:
        return DEFAULT_TASK
    return next(task for task in PRIORITY if scores[task] == best)
