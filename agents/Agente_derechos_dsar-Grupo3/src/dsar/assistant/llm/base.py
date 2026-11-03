"""Interfaz común de los proveedores de modelo de lenguaje."""

from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

Message = dict[str, str]


class LLMError(RuntimeError):
    """Fallo de un proveedor. `entry` es la línea de bitácora del intento fallido."""

    def __init__(self, message: str, entry: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.entry = entry


@dataclass
class LlmResult:
    text: str
    provider: str
    model: str
    prompt_sha256: str
    at: str
    latency_s: float
    model_requested: str | None = None
    cost_usd: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def log_entry(self) -> dict[str, Any]:
        """Entrada de bitácora: metadatos sin el texto del prompt ni de la respuesta."""
        entry = {key: value for key, value in asdict(self).items() if key not in {"text", "extra"} and value is not None}
        return entry | {"ok": True} | self.extra


class Provider(Protocol):
    name: str
    label: str
    cloud: bool
    default_model: str

    def complete(self, system: str, user: str, model: str | None = None,
                 history: list[Message] | None = None) -> LlmResult: ...


def prompt_hash(system: str, user: str) -> str:
    return hashlib.sha256((system + "\n\n" + user).encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Timer:
    def __init__(self) -> None:
        self.started = time.monotonic()
        self.at = now_iso()

    def elapsed(self) -> float:
        return round(time.monotonic() - self.started, 2)


def failure(provider: str, model: str, system: str, user: str, timer: Timer, exc: Exception) -> LLMError:
    """Error con su entrada de bitácora; el error se propaga, nunca se sustituye por otro modo."""
    entry = {"provider": provider, "model": model, "prompt_sha256": prompt_hash(system, user), "at": timer.at,
             "ok": False, "error": str(exc), "latency_s": timer.elapsed()}
    return LLMError(str(exc), entry)
