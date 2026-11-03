"""Errores de los casos de uso (la API los traduce a códigos HTTP)."""

from __future__ import annotations

import re

from dsar.assistant.llm import LLMError
from dsar.core.errors import CaseInputError, TransitionError

__all__ = ["CASE_ID_PATTERN", "CaseInputError", "LLMError", "MailboxError", "NotFoundError", "TransitionError",
           "check_case_id"]

# Identificadores que genera el sistema: origen + 12 hexadecimales.
CASE_ID_PATTERN = r"^DSAR-(API|MCP|EMAIL)-[0-9A-F]{12}$"
_CASE_ID = re.compile(CASE_ID_PATTERN)


class NotFoundError(LookupError):
    """El recurso pedido no existe."""


class MailboxError(RuntimeError):
    """El buzón o el servidor de correo no respondió."""


def check_case_id(case_id: str) -> str:
    if not isinstance(case_id, str) or not _CASE_ID.fullmatch(case_id):
        raise CaseInputError("Identificador de caso invalido.")
    return case_id
