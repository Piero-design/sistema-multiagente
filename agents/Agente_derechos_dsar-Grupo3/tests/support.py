"""Constantes y utilidades compartidas por las pruebas."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dsar.assistant.llm import LLMError, LlmResult

BACKEND_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = BACKEND_ROOT / "tests" / "fixtures"
GOLDEN = BACKEND_ROOT / "tests" / "golden"
CONFIG = BACKEND_ROOT / "config"
GENERATED_AT = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
HASHES = {"request": "0" * 64, "data": "1" * 64, "policies": "2" * 64}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class FakeProvider:
    def __init__(self, name: str = "ollama", cloud: bool = False, reply: str = "Respuesta del modelo.",
                 error: LLMError | None = None) -> None:
        self.name, self.cloud, self.reply, self.error = name, cloud, reply, error
        self.label = f"Simulado {name}"
        self.default_model = "modelo-simulado"
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, system, user, schema, model=None):
        return self.complete(system, user, model)

    def complete(self, system, user, model=None, history=None):
        self.calls.append({"system": system, "user": user, "model": model, "history": history})
        if self.error:
            raise self.error
        return LlmResult(text=self.reply, provider=self.name, model=model or self.default_model,
                         prompt_sha256="0" * 64, at="2026-10-21T00:00:00+00:00", latency_s=0.1)


SENT_AT = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)


def model_says(ctx, **changes) -> FakeProvider:
    """Respuesta JSON del modelo simulado al leer un correo."""
    provider = ctx.providers["ollama"]
    provider.reply = json.dumps({"is_dsar": True, "rights": ["access"], "subject_email": None, "missing_info": [],
                                 "confidence": "alta"} | changes)
    return provider


def receive(ctx, body: str = "Solicito acceso a mis datos personales.", sender: str = "persona@example.test",
            subject: str = "Solicitud de acceso", sent_at: datetime = SENT_AT) -> str:
    from dsar.services import intake

    return intake.enqueue(ctx, intake.build_message(sender, subject, body, sent_at))
