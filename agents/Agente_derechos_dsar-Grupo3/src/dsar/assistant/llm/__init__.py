"""Proveedores de modelo de lenguaje intercambiables: Ollama local, Gemini y Claude Code.

Reglas:
- Los proveedores en la nube solo reciben hechos minimizados y fragmentos normativos.
- `assert_cloud_safe` bloquea el envío si detecta un valor de un registro del titular.
- Si un proveedor falla, se propaga `LLMError`; nunca se sustituye por otro modo.
"""

from __future__ import annotations

from typing import Any

from dsar.assistant.llm.base import LLMError, LlmResult, Provider, prompt_hash
from dsar.assistant.llm.claude_code import ClaudeCodeProvider
from dsar.assistant.llm.gemini import GeminiProvider
from dsar.assistant.llm.ollama import OllamaProvider

# Valores de menos de 3 caracteres (p. ej. "si") darían falsos positivos.
MIN_LEAK_LENGTH = 3


def default_providers() -> dict[str, Provider]:
    return {provider.name: provider for provider in (OllamaProvider(), GeminiProvider(), ClaudeCodeProvider())}


def record_values(package: dict[str, Any] | None) -> set[str]:
    values: set[str] = set()
    for record in (package or {}).get("discovered_records", []):
        for value in record.get("data", {}).values():
            text = str(value).strip()
            if len(text) >= MIN_LEAK_LENGTH:
                values.add(text)
    return values


def assert_cloud_safe(text: str, package: dict[str, Any] | None) -> None:
    """Impide que un valor de los registros del titular salga hacia un proveedor en la nube."""
    leaked = sorted(value for value in record_values(package) if value in text)
    if leaked:
        raise LLMError(
            f"Envío bloqueado: el mensaje contiene {len(leaked)} valor(es) de registros del titular. "
            "Los modelos en la nube solo reciben hechos minimizados."
        )


__all__ = ["LLMError", "LlmResult", "Provider", "assert_cloud_safe", "default_providers", "prompt_hash",
           "record_values"]
