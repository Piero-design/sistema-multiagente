"""Gemini (nube). Solo recibe hechos minimizados y fragmentos normativos."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request

from dsar.assistant.llm.base import LLMError, LlmResult, Message, Timer, failure, prompt_hash

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3.8-flash"
GENERATION = {"temperature": 0.1, "maxOutputTokens": 800, "thinkingConfig": {"thinkingBudget": 0}}
# Las respuestas en la nube suelen tardar segundos; 120 s cubre colas lentas.
TIMEOUT = 120


def parse_response(data: dict[str, Any]) -> str:
    candidate = (data.get("candidates") or [{}])[0]
    if candidate.get("finishReason") == "MAX_TOKENS":
        raise LLMError("Gemini cortó la respuesta por el límite de tokens (MAX_TOKENS); no se muestra un texto incompleto.")
    text = "".join(part.get("text", "") for part in candidate.get("content", {}).get("parts", [])).strip()
    if not text:
        raise LLMError("Gemini devolvió una respuesta vacía.")
    return text


def post(model: str, system: str, user: str) -> dict[str, Any]:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise LLMError("Falta GEMINI_API_KEY. Defínela en el entorno o en el archivo .env.")
    body = {"system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": GENERATION}
    req = request.Request(URL.format(model=model), data=json.dumps(body).encode("utf-8"),
                          headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with request.urlopen(req, timeout=TIMEOUT) as response:
            return json.load(response)
    except (error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise LLMError(f"Gemini no respondió: {exc}") from exc


class GeminiProvider:
    name = "gemini"
    label = "Gemini (nube)"
    cloud = True

    @property
    def default_model(self) -> str:
        return os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    def complete(self, system: str, user: str, model: str | None = None,
                 history: list[Message] | None = None) -> LlmResult:
        # Sin historial: un turno previo podría contener valores de registros.
        model = model or self.default_model
        timer = Timer()
        try:
            text = parse_response(post(model, system, user))
        except LLMError as exc:
            raise failure(self.name, model, system, user, timer, exc) from exc
        return LlmResult(text=text, provider=self.name, model=model, prompt_sha256=prompt_hash(system, user),
                         at=timer.at, latency_s=timer.elapsed())
