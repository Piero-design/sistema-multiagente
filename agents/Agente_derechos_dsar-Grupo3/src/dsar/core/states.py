"""Estados del expediente y transiciones admitidas."""

from __future__ import annotations

from .errors import TransitionError

ALLOWED_STATES = frozenset({
    "RECEIVED", "TRIAGED", "IDENTITY_PENDING", "VERIFIED", "DISCOVERY", "REVIEW",
    "APPROVAL_REQUIRED", "APPROVED", "FULFILLED", "CLOSED", "ON_HOLD", "REJECTED",
    "PARTIALLY_FULFILLED", "ESCALATED", "CANCELLED",
})
# Estados en los que el motor deja el expediente al construirlo.
ENGINE_FINAL_STATES = frozenset({"IDENTITY_PENDING", "REVIEW", "APPROVAL_REQUIRED"})
# Solo una decisión humana registrada lleva a estos estados.
HUMAN_ONLY_STATES = frozenset({"APPROVED", "REJECTED", "CANCELLED"})
DECIDABLE_STATES = frozenset({"REVIEW", "APPROVAL_REQUIRED"})
# Estados en los que el expediente ya no espera nada: no tiene sentido contar los días que le quedan.
TERMINAL_STATES = HUMAN_ONLY_STATES | frozenset({"FULFILLED", "CLOSED", "PARTIALLY_FULFILLED"})
# Estados abiertos en los que se admite prórroga, suspensión u observación.
OPEN_STATES = ENGINE_FINAL_STATES

TRANSITIONS: dict[str, frozenset[str]] = {
    "RECEIVED": frozenset({"TRIAGED"}),
    "TRIAGED": frozenset({"IDENTITY_PENDING", "VERIFIED"}),
    "VERIFIED": frozenset({"DISCOVERY"}),
    "DISCOVERY": frozenset({"REVIEW", "APPROVAL_REQUIRED"}),
    "IDENTITY_PENDING": frozenset({"ON_HOLD", "VERIFIED"}),
    "REVIEW": frozenset({"APPROVED", "REJECTED", "ON_HOLD"}),
    "APPROVAL_REQUIRED": frozenset({"APPROVED", "REJECTED", "ON_HOLD"}),
    "ON_HOLD": frozenset({"IDENTITY_PENDING", "REVIEW", "APPROVAL_REQUIRED", "CANCELLED"}),
}


def can_transition(current: str, target: str) -> bool:
    return target in TRANSITIONS.get(current, frozenset())


def check_transition(current: str, target: str) -> None:
    if not can_transition(current, target):
        raise TransitionError(f"No se puede pasar de {current} a {target}.")
