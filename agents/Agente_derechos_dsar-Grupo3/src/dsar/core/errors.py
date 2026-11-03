"""Errores del núcleo."""

from __future__ import annotations


class CaseInputError(ValueError):
    """Una entrada no permite construir o modificar el expediente con seguridad."""


class TransitionError(Exception):
    """El cambio de estado pedido no está permitido desde el estado actual."""
